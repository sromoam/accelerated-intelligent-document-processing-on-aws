#!/usr/bin/env python3
"""Render the ablation tables of the "Benchmarks by Problem Set" pages.

Reads the ablation registry (benchmarks/matrices/guidance_ablations.yaml) and writes each
ablation into its page under docs/benchmark-guidance/, between the markers

    <!-- BEGIN GENERATED ABLATIONS -->
    <!-- END GENERATED ABLATIONS -->

Text outside the markers is hand-written and left alone. When a results file exists at
benchmarks/results/guidance/<ID>.json, its values fill the table; otherwise every cell is
"—" and the verdict reads "Not yet measured". A results file looks like:

    {
      "release": "0.6.15",
      "measured": "December 2026",
      "region": "us-west-2",
      "source": "benchmarks/results/v0.6.15/<suite>/summary.json",
      "verdict": "Use iterative extraction above about 400 rows.",
      "cells": {"<dataset key>|<value>|<metric key>": "0.812"}
    }

Usage:
    python3 benchmarks/harness/render_guidance.py           # rewrite the pages
    python3 benchmarks/harness/render_guidance.py --check   # exit 1 if a page is stale
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "benchmarks" / "matrices" / "guidance_ablations.yaml"
RESULTS = REPO / "benchmarks" / "results" / "guidance"
PAGES = REPO / "docs" / "benchmark-guidance"
BEGIN = "<!-- BEGIN GENERATED ABLATIONS -->"
END = "<!-- END GENERATED ABLATIONS -->"
BASELINE = "index.md#the-baseline-every-ablation-starts-from"
EMPTY = "—"


def load_registry() -> dict[str, Any]:
    with REGISTRY.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_results(ablation_id: str) -> dict[str, Any] | None:
    path = RESULTS / f"{ablation_id}.json"
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def dataset_label(key: str, datasets: dict[str, Any]) -> str:
    ds = datasets[key]
    link = ds.get("link")
    return f"[{ds['name']}]({link})" if link else ds["name"]


def render_ablation(ab: dict[str, Any], reg: dict[str, Any]) -> str:
    datasets: dict[str, Any] = reg["datasets"]
    metrics: dict[str, Any] = reg["metrics"]
    page = ab["page"]
    baseline = (
        BASELINE if page != "index" else "#the-baseline-every-ablation-starts-from"
    )
    results = load_results(ab["id"])
    cells: dict[str, str] = (results or {}).get("cells", {})

    lines = [f"### {ab['id']}: {ab['question']}", ""]
    if results:
        lines.append(f"**Verdict:** {results['verdict']}")
        lines.append("")
        lines.append(
            f"*Measured on release {results['release']}, {results['measured']}, "
            f"{results['region']}. Source: `{results['source']}`.*"
        )
    else:
        lines.append("**Verdict:** Not yet measured.")
    new_sets = [datasets[k]["name"] for k in ab["datasets"] if datasets[k].get("new")]
    if new_sets:
        lines.append("")
        lines.append(
            "Needs a dataset that does not exist yet: " + "; ".join(new_sets) + "."
        )
    lines.append("")

    held = ab.get("holds")
    held_text = (
        f"{held}; everything else at the [baseline]({baseline})"
        if held
        else f"Everything else at the [baseline]({baseline})"
    )
    if ab.get("derives"):
        runs_text = f"No new runs: computed from the {ab['derives']} runs"
    else:
        runs_text = f"{ab['runs']} per document per value"
    lines += [
        "| | |",
        "|---|---|",
        f"| **Changes** | {ab['changes']} |",
        f"| **Held fixed** | {held_text} |",
        "| **Datasets** | "
        + "; ".join(dataset_label(k, datasets) for k in ab["datasets"])
        + " |",
        f"| **Runs** | {runs_text} |",
        "",
    ]

    kinds: list[str] = []
    for ds_key in ab["datasets"]:
        if datasets[ds_key]["kind"] not in kinds:
            kinds.append(datasets[ds_key]["kind"])
    for kind in kinds:
        cols = [m for m in ab["metrics"] if kind in metrics[m]["kinds"]]
        if not cols:
            continue
        header = ["Dataset", ab["changes"]] + [metrics[m]["name"] for m in cols]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "---|" * len(header))
        for ds_key in [k for k in ab["datasets"] if datasets[k]["kind"] == kind]:
            for value in ab["values"]:
                row = [datasets[ds_key].get("short", datasets[ds_key]["name"]), value]
                row += [cells.get(f"{ds_key}|{value}|{m}", EMPTY) for m in cols]
                lines.append("| " + " | ".join(row) + " |")
        lines.append("")
    lines.append("")
    return "\n".join(lines)


def render_page(page: str, reg: dict[str, Any]) -> str:
    blocks = [render_ablation(ab, reg) for ab in reg["ablations"] if ab["page"] == page]
    return "\n".join(blocks).rstrip() + "\n"


def splice(text: str, generated: str, path: Path) -> str:
    if BEGIN not in text or END not in text:
        raise SystemExit(f"{path}: missing {BEGIN} / {END} markers")
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{BEGIN}\n\n{generated}\n{END}{tail}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--check", action="store_true", help="fail if a page is out of date"
    )
    args = parser.parse_args()

    reg = load_registry()
    ids = [ab["id"] for ab in reg["ablations"]]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise SystemExit(f"duplicate ablation IDs: {', '.join(duplicates)}")

    stale: list[str] = []
    for page in sorted({ab["page"] for ab in reg["ablations"]}):
        path = PAGES / f"{page}.md"
        text = path.read_text(encoding="utf-8")
        updated = splice(text, render_page(page, reg), path)
        if updated != text:
            if args.check:
                stale.append(str(path.relative_to(REPO)))
            else:
                path.write_text(updated, encoding="utf-8")
                print(f"rendered {path.relative_to(REPO)}")
    if stale:
        print(
            "out of date, run render_guidance.py: " + ", ".join(stale), file=sys.stderr
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
