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

A metric is written only when the runs report it (confidence metrics need confidence
on; page accuracy needs page-level class ground truth).

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
#: Test Studio cost-breakdown step names, by the registry's metric key.
STEP_METRICS = {
    "ocr_tokens": "OCR",
    "classification_tokens": "Classification",
    "extraction_tokens": "Extraction",
    "scoring_tokens": "Assessment",
}


def mean_se(values: list[float]) -> dict[str, float]:
    m = statistics.fmean(values)
    se = statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else 0.0
    return {"mean": round(m, 6), "se": round(se, 6)}


def step_tokens(result: dict[str, Any], step: str | None) -> int:
    """Bedrock tokens (input, output, cache reads and writes) for one step, or all."""
    total = 0
    for name, items in result.get("costBreakdown", {}).items():
        if step and name != step:
            continue
        for key, item in items.items():
            if key.startswith("bedrock/") and key.endswith("_totalTokens"):
                total += int(item["value"])
    return total


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
    run_ids: list[str] = []
    for ds_key, values in man["runs"].items():
        for value, ids in values.items():
            per_doc: dict[str, list[float]] = {}
            tokens: dict[str, list[float]] = {k: [] for k in [*STEP_METRICS, "total"]}
            medians: list[float] = []
            per_run: dict[str, list[float]] = {}
            for run_id in ids:
                path = args.results_dir / f"{run_id}-result.json"
                result = json.loads(path.read_text(encoding="utf-8"))
                if result.get("status") != "COMPLETE" or result.get("failedFiles"):
                    raise SystemExit(
                        f"{run_id}: not a clean run ({result.get('status')})"
                    )
                run_ids.append(run_id)
                scores = result.get("weightedOverallScores") or {}
                for key, score in scores.items():
                    per_doc.setdefault(key.split("/", 1)[1], []).append(float(score))
                n_pages = pages(result) or 1
                for metric, step in STEP_METRICS.items():
                    tokens[metric].append(step_tokens(result, step) / n_pages)
                tokens["total"].append(step_tokens(result, None) / n_pages)
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

    out = {
        "release": man["release"],
        "measured": man["measured"],
        "region": man["region"],
        "source": "Test Studio runs " + ", ".join(run_ids),
        "verdict": man["verdict"],
        "cells": cells,
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
