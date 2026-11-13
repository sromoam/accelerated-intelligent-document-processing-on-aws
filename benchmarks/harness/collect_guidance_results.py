#!/usr/bin/env python3
"""Summarize Test Studio runs into a results file for the benchmark guidance pages.

Each value of an ablation is run as one or more Test Studio test runs. This script reads
those runs' results (the JSON `idp-cli test-result --output-dir` writes) and the
stack's tracking table, and writes benchmarks/results/guidance/<ID>.json, which
render_guidance.py turns into the page's tables and plots. The full per-document results
stay in Test Studio on the stack; the file keeps only the summary and the run IDs.

A run manifest names the runs:

    {
      "ablation": "EX-01",
      "stack": "sr-testing",
      "region": "us-east-1",
      "release": "0.6.15.dev1",
      "measured": "November 2026",
      "verdict": "...",
      "runs": {
        "realkie": {
          "Single pass, Simple (default)": ["RealKIE-FCC-Verified-20261113-173220", ...],
          "Iterative, Advanced": ["RealKIE-FCC-Verified-20261113-173219", ...]
        }
      }
    }

Metrics (cell keys `dataset|value|metric`, each a mean and standard error):

    weighted_accuracy   per document, averaged over its runs; SE across documents
    <step>_tokens       tokens per page for one step, per run; SE across runs
    total_tokens        tokens per page for every Bedrock step, per run; SE across runs
    median_seconds      median workflow time per document, per run; SE across runs
    all_fields_right    share of documents scoring 1.0, per run; SE across runs
    auroc               field-confidence AUROC, per run; SE across runs
    calibration_error   field-confidence ECE, per run; SE across runs
    page_accuracy       share of pages with the right class, per run; SE across runs
    section_accuracy    share of sections with the right pages and class, per run
    grouping_score      DocSplit packet score for grouping pages into documents

A metric is written only when the runs report it (confidence metrics need confidence
on; page accuracy needs page-level class ground truth).

The file also keeps each run's billed usage per document scored, so the renderer can
price it with config_library/pricing.yaml:

    "usage": {"<dataset key>|<value>": [
        {"bedrock/us.anthropic.claude-sonnet-5|inputTokens": 41250.5,
         "textract/analyze_document-Tables|pages": 2.1, ...},
        ...one entry per run
    ]}

Usage:
    AWS_PROFILE=... python3 benchmarks/harness/collect_guidance_results.py \\
        manifest.json --results-dir /tmp/ex01/results
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import boto3

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "benchmarks" / "results" / "guidance"
#: Test Studio cost-breakdown step names, by the registry's metric key. Detecting
#: sections first meters its two calls as Splitting and SectionClassification.
STEP_METRICS = {
    "ocr_tokens": ("OCR",),
    "classification_tokens": ("Classification", "Splitting", "SectionClassification"),
    "extraction_tokens": ("Extraction",),
    "scoring_tokens": ("Assessment",),
}
#: Cost-breakdown services kept as usage, and units that carry no price of their own.
PRICED_SERVICES = ("bedrock/", "textract/")
UNPRICED_UNITS = ("requests", "totalTokens")


def mean_se(values: list[float]) -> dict[str, float]:
    m = statistics.fmean(values)
    se = statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else 0.0
    return {"mean": round(m, 6), "se": round(se, 6)}


def step_tokens(result: dict[str, Any], steps: tuple[str, ...] | None) -> int:
    """Bedrock tokens (input, output, cache reads and writes) for some steps, or all."""
    total = 0
    for name, items in result.get("costBreakdown", {}).items():
        if steps and name not in steps:
            continue
        for key, item in items.items():
            if key.startswith("bedrock/") and key.endswith("_totalTokens"):
                total += int(item["value"])
    return total


def run_usage(result: dict[str, Any]) -> dict[str, float]:
    """Bedrock and Textract usage per document scored, summed over every step.

    Cost-breakdown keys look like `bedrock/<model id>_<unit>`; the result's keys look
    like `bedrock/<model id>|<unit>`.
    """
    docs = int(result.get("completedFiles") or 0) or (
        int(result.get("filesCount") or 0) - int(result.get("failedFiles") or 0)
    )
    if docs <= 0:
        return {}
    totals: dict[str, float] = {}
    for items in (result.get("costBreakdown") or {}).values():
        for key, item in items.items():
            if not key.startswith(PRICED_SERVICES):
                continue
            service_id, _, unit = key.rpartition("_")
            if not service_id or unit in UNPRICED_UNITS:
                continue
            name = f"{service_id}|{unit}"
            totals[name] = totals.get(name, 0.0) + float(item.get("value") or 0)
    return {k: round(v / docs, 4) for k, v in sorted(totals.items())}


def run_metrics(result: dict[str, Any]) -> dict[str, float]:
    """Per-run metrics that Test Studio reports directly, when present."""
    out: dict[str, float] = {}
    scores = [float(v) for v in result.get("weightedOverallScores", {}).values()]
    if scores:
        out["all_fields_right"] = sum(v >= 0.9999 for v in scores) / len(scores)
    overall = (result.get("confidenceMetrics") or {}).get("overall") or {}
    if (overall.get("auroc") or {}).get("value") is not None:
        out["auroc"] = float(overall["auroc"]["value"])
    if (overall.get("ece") or {}).get("value") is not None:
        out["calibration_error"] = float(overall["ece"]["value"])
    split = result.get("splitClassificationMetrics") or {}
    if split.get("page_level_accuracy") is not None:
        out["page_accuracy"] = float(split["page_level_accuracy"])
    if split.get("split_accuracy_without_order") is not None:
        out["section_accuracy"] = float(split["split_accuracy_without_order"])
    graded = ((result.get("gradedPacketMetrics") or {}).get("mean")) or {}
    if graded.get("final_score") is not None:
        out["grouping_score"] = float(graded["final_score"])
    return out


def pages(result: dict[str, Any]) -> int:
    return int(result.get("splitClassificationMetrics", {}).get("total_pages") or 0)


def workflow_seconds(table: Any, run_id: str, doc_keys: list[str]) -> list[float]:
    out = []
    for key in doc_keys:
        item = table.get_item(Key={"PK": f"doc#{key}", "SK": "none"}).get("Item")
        if (
            not item
            or not item.get("CompletionTime")
            or not item.get("WorkflowStartTime")
        ):
            continue
        start = datetime.fromisoformat(item["WorkflowStartTime"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(item["CompletionTime"].replace("Z", "+00:00"))
        out.append((end - start).total_seconds())
    return out


def tracking_table(stack: str, region: str) -> Any:
    cfn = boto3.client("cloudformation", region_name=region)
    for page in cfn.get_paginator("list_stack_resources").paginate(StackName=stack):
        for r in page["StackResourceSummaries"]:
            if r["LogicalResourceId"] == "TrackingTable":
                return boto3.resource("dynamodb", region_name=region).Table(
                    r["PhysicalResourceId"]
                )
    raise SystemExit(f"{stack}: no TrackingTable resource")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()

    man = json.loads(args.manifest.read_text(encoding="utf-8"))
    table = tracking_table(man["stack"], man["region"])
    cells: dict[str, dict[str, float]] = {}
    usage: dict[str, list[dict[str, float]]] = {}
    run_ids: list[str] = []
    failed_total = 0
    for ds_key, values in man["runs"].items():
        for value, ids in values.items():
            per_doc: dict[str, list[float]] = {}
            tokens: dict[str, list[float]] = {k: [] for k in [*STEP_METRICS, "total"]}
            medians: list[float] = []
            per_run: dict[str, list[float]] = {}
            runs_usage: list[dict[str, float]] = []
            for run_id in ids:
                path = args.results_dir / f"{run_id}-result.json"
                result = json.loads(path.read_text(encoding="utf-8"))
                failed = int(result.get("failedFiles") or 0)
                allowed = int(man.get("max_failed", {}).get(ds_key, 0))
                if failed > allowed or result.get("status") not in (
                    "COMPLETE",
                    "PARTIAL_COMPLETE",
                ):
                    raise SystemExit(
                        f"{run_id}: not a clean run ({result.get('status')})"
                    )
                failed_total += failed
                run_ids.append(run_id)
                scores = result.get("weightedOverallScores") or {}
                for key, score in scores.items():
                    per_doc.setdefault(key.split("/", 1)[1], []).append(float(score))
                n_pages = pages(result) or 1
                for metric, step in STEP_METRICS.items():
                    tokens[metric].append(step_tokens(result, step) / n_pages)
                tokens["total"].append(step_tokens(result, None) / n_pages)
                runs_usage.append(run_usage(result))
                for metric, v in run_metrics(result).items():
                    per_run.setdefault(metric, []).append(v)
                secs = workflow_seconds(table, run_id, list(scores))
                if secs:
                    medians.append(statistics.median(secs))
            cell = f"{ds_key}|{value}|"
            if per_doc:
                cells[cell + "weighted_accuracy"] = mean_se(
                    [statistics.fmean(v) for v in per_doc.values()]
                )
            for metric in STEP_METRICS:
                if any(tokens[metric]):
                    cells[cell + metric] = mean_se(tokens[metric])
            cells[cell + "total_tokens"] = mean_se(tokens["total"])
            if medians:
                cells[cell + "median_seconds"] = mean_se(medians)
            for metric, vals in per_run.items():
                if len(vals) == len(ids):
                    cells[cell + metric] = mean_se(vals)
            if runs_usage and all(runs_usage):
                usage[f"{ds_key}|{value}"] = runs_usage

    out = {
        "release": man["release"],
        "measured": man["measured"],
        "region": man["region"],
        "source": "Test Studio runs "
        + ", ".join(run_ids)
        + (
            f" ({failed_total} failed documents left out of the scores)"
            if failed_total
            else ""
        ),
        "verdict": man["verdict"],
        "cells": cells,
        "usage": usage,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{man['ablation']}.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(REPO)}")
    for k, v in cells.items():
        print(f"  {k}: {v['mean']:.4g} ± {2 * v['se']:.2g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
