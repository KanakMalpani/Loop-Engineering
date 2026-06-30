#!/usr/bin/env python3
"""Smoke test Wave 15 mix + suite CLI paths."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _has_loopbench_suite_cli() -> bool:
    if importlib.util.find_spec("loopbench") is None:
        return False
    return importlib.util.find_spec("loopbench.__main__") is not None


def main() -> int:
    py = sys.executable
    tmp = Path(tempfile.gettempdir()) / "le-mix-smoke.yaml"
    checks: list[tuple[str, list[str]]] = [
        ("loopforge_mix_list", [py, "-m", "loopforge", "mix", "--list"]),
        (
            "loopforge_mix_dev_agent",
            [py, "-m", "loopforge", "mix", "dev-agent", "-o", str(tmp), "--compact"],
        ),
    ]
    if _has_loopbench_suite_cli():
        checks.append(("loopbench_suite_list", [py, "-m", "loopbench", "suite", "list"]))

    for name, cmd in checks:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"FAIL {name}:\n{proc.stderr or proc.stdout}", file=sys.stderr)
            return 1
        print(f"OK {name}")

    proc = subprocess.run(
        [
            py,
            "-m",
            "loopctl",
            "pipeline",
            "--recipe",
            "dev-agent",
            "--intent",
            "Smoke test repair pipeline",
            "--suite",
            "suite-repair",
            "--compact",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return 1
    data = json.loads(proc.stdout)
    if not (data.get("valid") or data.get("ok")):
        print("FAIL: pipeline recipe not valid", file=sys.stderr)
        return 1
    if "bench_cmd" not in data or "suite-repair" not in data.get("bench_cmd", ""):
        print("FAIL: missing suite bench_cmd", file=sys.stderr)
        return 1
    print("OK loopctl_pipeline_recipe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
