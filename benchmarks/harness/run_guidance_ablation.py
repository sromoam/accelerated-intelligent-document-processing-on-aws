#!/usr/bin/env python3
"""Run one ablation of the benchmark guidance registry as Test Studio runs.

For each dataset of the ablation that has a test set on the stack, and each value of
the setting, this script:

1. downloads the dataset's preset profile from the stack (the profile named after the
   preset, e.g. `realkie-fcc-verified`),
2. applies the value's overrides from the registry's `set` list (dotted config paths),
3. uploads the result as an unmanaged profile `bench-<id>-<dataset>-<n>`,
4. starts `runs` Test Studio runs of the dataset's test set under that profile, limited
   to the dataset's `docs`, and waits for their evaluation.

It then writes a run manifest under benchmarks/results/guidance/manifests/ and calls
collect_guidance_results.py, which writes benchmarks/results/guidance/<ID>.json.
Re-running an ablation keeps the runs already in its manifest and adds only what is
missing, so an interrupted run can be resumed.

The CLI runs from --checkout, which must be the source of the code the stack runs, so
that the profiles round-trip every setting the stack knows about.

Usage:
    AWS_PROFILE=... python3 benchmarks/harness/run_guidance_ablation.py EX-03 \\
        --stack sr-testing --region us-east-1 --checkout ~/wt/fix-1785 \\
        --release 0.6.15.dev1 --workdir /tmp/guidance-runs [--datasets realkie]
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "benchmarks" / "matrices" / "guidance_ablations.yaml"
MANIFESTS = REPO / "benchmarks" / "results" / "guidance" / "manifests"
COLLECT = REPO / "benchmarks" / "harness" / "collect_guidance_results.py"
LOCK = threading.Lock()


def cli(args: argparse.Namespace, *cmd: str, timeout: int = 7200) -> str:
    root = Path(args.checkout).expanduser()
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        str(p)
        for p in sorted((root / "lib").iterdir())
        if (p / "pyproject.toml").exists()
    )
    proc = subprocess.run(
        [sys.executable, "-m", "idp_cli.cli", *cmd],
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
        check=False,
    )
    return proc.stdout + proc.stderr


def set_path(cfg: dict[str, Any], dotted: str, value: Any) -> None:
    node = cfg
    keys = dotted.split(".")
    for key in keys[:-1]:
        node = node.setdefault(key, {})
    node[keys[-1]] = value


def make_profile(
    args: argparse.Namespace,
    ab: dict[str, Any],
    ds_key: str,
    ds: dict[str, Any],
    idx: int,
) -> tuple[str, int]:
    """Create (or update) the profile for one value; return its name and revision."""
    work = Path(args.workdir) / ab["id"]
    work.mkdir(parents=True, exist_ok=True)
    base = work / f"base-{ds_key}.yaml"
    if not base.exists():
        out = cli(
            args,
            "config-download",
            "--stack-name",
            args.stack,
            "--config-profile",
            ds["preset"],
            "--output",
            str(base),
        )
        if not base.exists():
            raise SystemExit(f"could not download profile {ds['preset']}:\n{out}")
    cfg = yaml.safe_load(base.read_text(encoding="utf-8"))
    cfg["managed"] = False
    for dotted, value in ab["set"][idx].items():
        set_path(cfg, dotted, value)
    name = f"bench-{ab['id'].lower()}-{ds_key.replace('_', '-')}-{idx}"
    path = work / f"{name}.yaml"
    path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    out = cli(
        args,
        "config-upload",
        "--stack-name",
        args.stack,
        "--config-file",
        str(path),
        "--config-profile",
        name,
        "--version-description",
        f"Benchmark {ab['id']}: {ab['values'][idx]}",
    )
    m = re.search(r"Revision: r(\d+)", out)
    if not m:
        raise SystemExit(f"upload of {name} failed:\n{out[-2000:]}")
    return name, int(m.group(1))


def one_run(
    args: argparse.Namespace,
    ab: dict[str, Any],
    ds: dict[str, Any],
    profile: str,
    rev: int,
    label: str,
) -> str | None:
    out = cli(
        args,
        "process",
        "--stack-name",
        args.stack,
        "--test-set",
        ds["testset"],
        "--number-of-files",
        str(ds.get("docs", 20)),
        "--config-profile",
        profile,
        "--config-revision",
        str(rev),
        "--context",
        label,
        timeout=600,
    )
    m = re.search(r"Test run started: (\S+)", out)
    if not m:
        print(f"  ! could not start {label}:\n{out[-1500:]}", flush=True)
        return None
    run_id = m.group(1)
    results = Path(args.workdir) / "results"
    results.mkdir(parents=True, exist_ok=True)
    out = cli(
        args,
        "test-result",
        "--stack-name",
        args.stack,
        "--test-run-id",
        run_id,
        "--wait",
        "--timeout",
        "5400",
        "--output-dir",
        str(results),
    )
    if not (results / f"{run_id}-result.json").exists():
        print(f"  ! no result for {run_id} ({label}):\n{out[-1500:]}", flush=True)
        return None
    data = json.loads((results / f"{run_id}-result.json").read_text(encoding="utf-8"))
    max_failed = int(ds.get("max_failed", 0))
    failed = int(data.get("failedFiles") or 0)
    ok_status = data.get("status") == "COMPLETE" or (
        data.get("status") == "PARTIAL_COMPLETE" and failed <= max_failed
    )
    if not ok_status or failed > max_failed:
        print(
            f"  ! {run_id} ({label}) is {data.get('status')} with "
            f"{data.get('failedFiles')} failed files; not counted",
            flush=True,
        )
        return None
    print(f"  ✓ {label}: {run_id}", flush=True)
    return run_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("ablation")
    parser.add_argument("--stack", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--checkout", required=True)
    parser.add_argument("--release", required=True)
    parser.add_argument("--measured", default="November 2026")
    parser.add_argument("--workdir", default="/tmp/guidance-runs")
    parser.add_argument("--datasets", help="comma-separated dataset keys")
    parser.add_argument("--runs", type=int, help="override the registry's runs")
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args()

    reg = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    ab = next((a for a in reg["ablations"] if a["id"] == args.ablation), None)
    if ab is None or "set" not in ab:
        raise SystemExit(f"{args.ablation}: not in the registry, or has no `set` list")
    keys = args.datasets.split(",") if args.datasets else ab["datasets"]
    keys = [k for k in keys if reg["datasets"][k].get("testset")]
    if not keys:
        raise SystemExit(f"{args.ablation}: no dataset with a test set on the stack")
    runs = args.runs or ab["runs"]

    MANIFESTS.mkdir(parents=True, exist_ok=True)
    mpath = MANIFESTS / f"{ab['id']}.json"
    manifest = (
        json.loads(mpath.read_text(encoding="utf-8"))
        if mpath.exists()
        else {"ablation": ab["id"], "verdict": "Measured; see the table.", "runs": {}}
    )
    manifest["max_failed"] = {
        k: int(reg["datasets"][k].get("max_failed", 0))
        for k in keys
        if reg["datasets"][k].get("max_failed")
    } or manifest.get("max_failed", {})
    manifest.update(
        stack=args.stack,
        region=args.region,
        release=args.release,
        measured=args.measured,
    )

    jobs = []
    for ds_key in keys:
        ds = reg["datasets"][ds_key]
        for idx, value in enumerate(ab["values"]):
            have = manifest["runs"].get(ds_key, {}).get(value, [])
            if len(have) >= runs:
                continue
            profile, rev = make_profile(args, ab, ds_key, ds, idx)
            for n in range(len(have), runs):
                jobs.append((ds_key, ds, value, profile, rev, n + 1))
    print(f"{ab['id']}: {len(jobs)} runs to do", flush=True)

    def save() -> None:
        mpath.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {
            pool.submit(
                one_run,
                args,
                ab,
                ds,
                profile,
                rev,
                f"{ab['id']} {ds_key} {value} run {n}",
            ): (ds_key, value)
            for ds_key, ds, value, profile, rev, n in jobs
        }
        for fut in cf.as_completed(futures):
            run_id = fut.result()
            if run_id:
                ds_key, value = futures[fut]
                with LOCK:
                    manifest["runs"].setdefault(ds_key, {}).setdefault(
                        value, []
                    ).append(run_id)
                    save()
    save()

    proc = subprocess.run(
        [
            sys.executable,
            str(COLLECT),
            str(mpath),
            "--results-dir",
            str(Path(args.workdir) / "results"),
        ],
        check=False,
    )
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
