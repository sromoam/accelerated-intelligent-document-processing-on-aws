#!/usr/bin/env python3
"""Render the ablation tables of the "Benchmarks by Problem Set" pages.

Reads the ablation registry (benchmarks/matrices/guidance_ablations.yaml) and writes three
regions of each page under docs/benchmark-guidance/, each between a pair of markers:

    <!-- BEGIN GENERATED FAQ -->       each question, its answer and its headline plot
    <!-- BEGIN GENERATED ABLATIONS --> each ablation's details and results tables

(each closed by the matching END marker), and the dataset list of datasets.md between
DATASETS markers. Text outside the
markers is hand-written and left alone. When a results file exists at
benchmarks/results/guidance/<ID>.json, its values fill the table; otherwise every cell is
"—" and the answer reads "Not yet measured". A results file looks like:

    {
      "release": "0.6.15",
      "measured": "December 2026",
      "region": "us-west-2",
      "source": "benchmarks/results/v0.6.15/<suite>/summary.json",
      "verdict": "Use iterative extraction above about 400 rows.",
      "cells": {"<dataset key>|<value>|<metric key>": {"mean": 0.812, "se": 0.006}}
    }

A cell is either a string, printed as is, or a mean and standard error over the runs,
printed as "0.81 ± 0.01" (two standard errors). For each dataset kind, the ablation's
`plot` metric (or its first metric) is drawn as a dot-and-whisker SVG under
images/benchmark-guidance/ whenever at least one of its cells has a mean.

Usage:
    python3 benchmarks/harness/render_guidance.py           # rewrite the pages
    python3 benchmarks/harness/render_guidance.py --check   # exit 1 if a page is stale
    python3 benchmarks/harness/render_guidance.py --preview EX-02 \
        --results sample.json --out /tmp/plots              # draw one ablation's plots
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from guidance_plots import MAX_LABELLED, draw_plot, draw_scatter, fmt

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "benchmarks" / "matrices" / "guidance_ablations.yaml"
RESULTS = REPO / "benchmarks" / "results" / "guidance"
PAGES = REPO / "docs" / "benchmark-guidance"
#: Generated regions of a page. ABLATIONS is required; the others are optional.
REGIONS = ("FAQ", "ABLATIONS")
PRESETS = "index.md#how-we-run-a-benchmark"
DATASETS_PAGE = "datasets.md"
PLOTS = REPO / "images" / "benchmark-guidance"
PLOTS_FROM_PAGES = "../../images/benchmark-guidance"
EMPTY = "—"
CAPTION = "Dots are the mean of the runs; lines span two standard errors either side."
SCATTER_CAPTION = (
    "Each point is one value of the setting; lines span two standard errors either "
    "side. Up and to the left is better."
)

sys.path.insert(0, str(REPO / "scripts"))
from check_markdown_links import slugify  # noqa: E402  (github-slugger rules)

Cell = str | dict[str, float]


def markers(region: str) -> tuple[str, str]:
    return (
        f"<!-- BEGIN GENERATED {region} -->",
        f"<!-- END GENERATED {region} -->",
    )


def load_registry() -> dict[str, Any]:
    with REGISTRY.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_results(ablation_id: str) -> dict[str, Any] | None:
    path = RESULTS / f"{ablation_id}.json"
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def cell_text(cell: Cell | None) -> str:
    if cell is None:
        return EMPTY
    if isinstance(cell, str):
        return cell
    return f"{fmt(cell['mean'])} ± {fmt(2 * cell.get('se', 0))}"


def dataset_anchor(key: str, datasets: dict[str, Any]) -> str:
    return f"{DATASETS_PAGE}#{slugify(datasets[key]['name'])}"


def dataset_label(key: str, datasets: dict[str, Any], short: bool = False) -> str:
    ds = datasets[key]
    text = ds.get("short", ds["name"]) if short else ds["name"]
    return f"[{text}]({dataset_anchor(key, datasets)})"


def details_heading(ab: dict[str, Any]) -> str:
    return f"{ab['id']}: {ab['question']}"


class Rendered:
    """One ablation's FAQ entry, details section and plots."""

    def __init__(self) -> None:
        self.faq: list[str] = []
        self.details: list[str] = []
        self.plots: dict[str, str] = {}


def render_ablation(
    ab: dict[str, Any], reg: dict[str, Any], results: dict[str, Any] | None
) -> Rendered:
    datasets: dict[str, Any] = reg["datasets"]
    metrics: dict[str, Any] = reg["metrics"]
    presets = PRESETS if ab["page"] != "index" else "#how-we-run-a-benchmark"
    cells: dict[str, Cell] = (results or {}).get("cells", {})
    out = Rendered()
    answer = results["verdict"] if results else "Not yet measured."
    details_link = f"[Details: {ab['id']}](#{slugify(details_heading(ab))})"

    # Details: heading, answer, what was run.
    d = out.details
    d += [f"#### {details_heading(ab)}", "", f"**Answer:** {answer}"]
    if results:
        d += [
            "",
            f"*Measured on release {results['release']}, {results['measured']}, "
            f"{results['region']}. Source: `{results['source']}`.*",
        ]
    new_sets = [datasets[k]["name"] for k in ab["datasets"] if datasets[k].get("new")]
    if new_sets:
        d += ["", "Needs a dataset we haven't built yet: " + "; ".join(new_sets) + "."]
    held = ab.get("holds")
    fixed_text = (
        f"{held}; the rest as each dataset's [preset]({presets}) sets it"
        if held
        else f"As each dataset's [preset]({presets}) sets it"
    )
    if ab.get("derives"):
        runs_text = f"None: computed from the {ab['derives']} runs"
    else:
        runs_text = f"{ab['runs']} per document, per value"
    d += [
        "",
        "| | |",
        "|---|---|",
        f"| **Changes** | {ab['changes']} |",
        f"| **Everything else** | {fixed_text} |",
        "| **Datasets** | "
        + "; ".join(dataset_label(k, datasets) for k in ab["datasets"])
        + " |",
        f"| **Runs** | {runs_text} |",
        "",
    ]

    # One plot and one table per dataset kind. The first plot drawn is the
    # headline and goes in the FAQ entry; any others stay with their tables.
    kinds: list[str] = []
    for ds_key in ab["datasets"]:
        if datasets[ds_key]["kind"] not in kinds:
            kinds.append(datasets[ds_key]["kind"])
    headline: list[str] = []
    for kind in kinds:
        cols = [m for m in ab["metrics"] if kind in metrics[m]["kinds"]]
        if not cols:
            continue
        kind_sets = [k for k in ab["datasets"] if datasets[k]["kind"] == kind]
        plot_metric = ab.get("plot") if ab.get("plot") in cols else cols[0]
        panels = []
        for ds_key in kind_sets:
            rows = []
            for value in ab["values"]:
                cell = cells.get(f"{ds_key}|{value}|{plot_metric}")
                rows.append((value, cell if isinstance(cell, dict) else None))
            panels.append(
                (datasets[ds_key].get("short", datasets[ds_key]["name"]), rows)
            )
        panels = [(name, rows) for name, rows in panels if any(p for _, p in rows)]
        x_metric = ab.get("plot_x") or (
            "total_tokens"
            if "total_tokens" in cols
            else next(
                (m for m in cols if m.endswith("_tokens") and m != plot_metric), None
            )
        )
        scatter = []
        if x_metric and not plot_metric.endswith("_tokens"):
            for ds_key in kind_sets:
                pts = []
                for value in ab["values"]:
                    x = cells.get(f"{ds_key}|{value}|{x_metric}")
                    y = cells.get(f"{ds_key}|{value}|{plot_metric}")
                    if isinstance(x, dict) and isinstance(y, dict):
                        pts.append((value, x, y))
                if pts:
                    scatter.append(
                        (datasets[ds_key].get("short", datasets[ds_key]["name"]), pts)
                    )
        if panels:
            name = f"{ab['id']}-{kind}.svg"
            metric_name = metrics[plot_metric]["name"]
            if scatter and x_metric:
                x_name = metrics[x_metric]["name"]
                out.plots[name] = draw_scatter(
                    x_name, metric_name, scatter, ab.get("runs", 0)
                )
                alt = f"{metric_name} against {x_name.lower()} for each {ab['changes']}"
                caption = f"*{metric_name} against {x_name.lower()}. {SCATTER_CAPTION}"
                if max(len(pts) for _, pts in scatter) > MAX_LABELLED:
                    caption += (
                        " Labels mark the default and the values no other value "
                        "beats on both axes; hover a point for the rest."
                    )
                caption += "*"
            else:
                out.plots[name] = draw_plot(metric_name, panels, ab.get("runs", 0))
                alt = f"{metric_name} for each value of {ab['changes']}"
                caption = f"*{metric_name}. {CAPTION}*"
            plotted = [
                k
                for k in kind_sets
                if datasets[k].get("short", datasets[k]["name"])
                in {p for p, _ in panels}
            ]
            caption += (
                " Datasets: "
                + ", ".join(dataset_label(k, datasets, short=True) for k in plotted)
                + "."
            )
            plot_md = [f"![{alt}]({PLOTS_FROM_PAGES}/{name})", "", caption, ""]
            if headline:
                d += plot_md
            else:
                headline = plot_md
        header = ["Dataset", ab["changes"]] + [metrics[m]["name"] for m in cols]
        d.append("| " + " | ".join(header) + " |")
        d.append("|" + "---|" * len(header))
        for ds_key in kind_sets:
            for value in ab["values"]:
                row = [datasets[ds_key].get("short", datasets[ds_key]["name"]), value]
                row += [cell_text(cells.get(f"{ds_key}|{value}|{m}")) for m in cols]
                d.append("| " + " | ".join(row) + " |")
        d.append("")
    d.append("")

    # FAQ entry: the question, the answer, the headline plot, a link to details.
    out.faq += [f"### {ab['question']}", "", f"**Answer:** {answer} {details_link}", ""]
    out.faq += headline
    return out


def render_datasets(reg: dict[str, Any]) -> str:
    """The Benchmark Datasets page: one section per dataset in the registry."""
    datasets: dict[str, Any] = reg["datasets"]
    used: dict[str, list[dict[str, Any]]] = {k: [] for k in datasets}
    for ab in reg["ablations"]:
        for k in ab["datasets"]:
            used[k].append(ab)
    built = [k for k in datasets if not datasets[k].get("new")]
    planned = [k for k in datasets if datasets[k].get("new")]
    lines: list[str] = []
    for heading, keys in (
        ("Datasets we run", built),
        ("Datasets we haven't built yet", planned),
    ):
        lines += [f"## {heading}", ""]
        for k in keys:
            ds = datasets[k]
            lines += [f"### {ds['name']}", ""]
            if ds.get("link"):
                lines.append(
                    f"- **About the dataset:** [{ds['name'].split(' (')[0].split(',')[0]}]({ds['link']})"
                )
            if ds.get("preset"):
                lines.append(f"- **Preset:** `{ds['preset']}`")
            if ds.get("testset"):
                lines.append(
                    f"- **Test Studio test set:** `{ds['testset']}`, "
                    f"{ds.get('docs', 20)} documents per run"
                )
            elif not ds.get("new"):
                lines.append(
                    "- **Test Studio test set:** not on the benchmark stack yet"
                )
            if used[k]:
                links = ", ".join(
                    f"[{ab['id']}]({ab['page']}.md#{slugify(details_heading(ab))})"
                    for ab in used[k]
                )
                lines.append(f"- **Used by:** {links}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_page(
    page: str, reg: dict[str, Any]
) -> tuple[dict[str, str], dict[str, str]]:
    """Return the page's generated regions and its plots."""
    faq: list[str] = []
    details: list[str] = []
    plots: dict[str, str] = {}
    for ab in reg["ablations"]:
        if ab["page"] == page:
            r = render_ablation(ab, reg, load_results(ab["id"]))
            faq += r.faq
            details += r.details
            plots.update(r.plots)
    regions = {
        "FAQ": "\n".join(faq).rstrip() + "\n",
        "ABLATIONS": "\n".join(details).rstrip() + "\n",
    }
    return regions, plots


def splice(text: str, regions: dict[str, str], path: Path) -> str:
    for region in REGIONS:
        begin, end = markers(region)
        if begin not in text or end not in text:
            if region == "ABLATIONS":
                raise SystemExit(f"{path}: missing {begin} / {end} markers")
            continue
        head, rest = text.split(begin, 1)
        _, tail = rest.split(end, 1)
        text = f"{head}{begin}\n\n{regions[region]}\n{end}{tail}"
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--check", action="store_true", help="fail if a page is out of date"
    )
    parser.add_argument("--preview", metavar="ID", help="draw one ablation's plots")
    parser.add_argument("--results", type=Path, help="results file for --preview")
    parser.add_argument("--out", type=Path, help="output directory for --preview")
    args = parser.parse_args()

    reg = load_registry()
    ids = [ab["id"] for ab in reg["ablations"]]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise SystemExit(f"duplicate ablation IDs: {', '.join(duplicates)}")

    if args.preview:
        if not (args.results and args.out):
            raise SystemExit("--preview needs --results and --out")
        ab = next((a for a in reg["ablations"] if a["id"] == args.preview), None)
        if ab is None:
            raise SystemExit(f"no ablation {args.preview}")
        results = json.loads(args.results.read_text(encoding="utf-8"))
        plots = render_ablation(ab, reg, results).plots
        args.out.mkdir(parents=True, exist_ok=True)
        for name, svg in plots.items():
            (args.out / name).write_text(svg, encoding="utf-8")
            print(f"wrote {args.out / name}")
        return 0

    stale: list[str] = []
    expected: dict[str, str] = {}
    for page in sorted({ab["page"] for ab in reg["ablations"]}):
        path = PAGES / f"{page}.md"
        text = path.read_text(encoding="utf-8")
        regions, plots = render_page(page, reg)
        expected.update(plots)
        updated = splice(text, regions, path)
        if updated != text:
            if args.check:
                stale.append(str(path.relative_to(REPO)))
            else:
                path.write_text(updated, encoding="utf-8")
                print(f"rendered {path.relative_to(REPO)}")
    ds_path = PAGES / f"{DATASETS_PAGE}"
    ds_text = ds_path.read_text(encoding="utf-8")
    begin, end = markers("DATASETS")
    head, rest = ds_text.split(begin, 1)
    _, tail = rest.split(end, 1)
    ds_updated = f"{head}{begin}\n\n{render_datasets(reg)}\n{end}{tail}"
    if ds_updated != ds_text:
        if args.check:
            stale.append(str(ds_path.relative_to(REPO)))
        else:
            ds_path.write_text(ds_updated, encoding="utf-8")
            print(f"rendered {ds_path.relative_to(REPO)}")
    existing = {p.name for p in PLOTS.glob("*.svg")} if PLOTS.exists() else set()
    for name, svg in expected.items():
        plot = PLOTS / name
        if not plot.exists() or plot.read_text(encoding="utf-8") != svg:
            if args.check:
                stale.append(str(plot.relative_to(REPO)))
            else:
                PLOTS.mkdir(parents=True, exist_ok=True)
                plot.write_text(svg, encoding="utf-8")
                print(f"drew {plot.relative_to(REPO)}")
    for name in sorted(existing - expected.keys()):
        if args.check:
            stale.append(f"{(PLOTS / name).relative_to(REPO)} (no longer drawn)")
        else:
            (PLOTS / name).unlink()
            print(f"removed {(PLOTS / name).relative_to(REPO)}")
    if stale:
        print(
            "out of date, run render_guidance.py: " + ", ".join(stale), file=sys.stderr
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
