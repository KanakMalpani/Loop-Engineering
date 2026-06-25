#!/usr/bin/env python3
"""LangGraph integration: intent -> export -> run (Phase 10)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV = {**os.environ, "PYTHONPATH": str(ROOT)}


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="integrate-lg-"))
    spec = tmp / "loop.yaml"
    export_dir = tmp / "langgraph-export"

    steps = [
        [
            sys.executable,
            "-m",
            "loopforge",
            "intent",
            "Parallel research and coding branches then synthesize",
            "-o",
            str(spec),
            "--suggest-level",
        ],
        [sys.executable, "-m", "loopctl", "validate", str(spec), "--lss", "1.1"],
        [
            sys.executable,
            "-m",
            "loopforge",
            "export",
            "--spec",
            str(spec),
            "--target",
            "langgraph",
            "--out",
            str(export_dir),
        ],
    ]
    for cmd in steps:
        print("+", " ".join(cmd))
        subprocess.run(cmd, cwd=ROOT, check=True, env=ENV)

    run_py = export_dir / "run.py"
    if not run_py.exists():
        print("FAIL: export missing run.py", file=sys.stderr)
        return 1

    # LoopGym fallback path (no langgraph required in CI)
    proc = subprocess.run([sys.executable, str(run_py), "--json"], cwd=export_dir, capture_output=True, text=True)
    print(proc.stdout or proc.stderr)
    if proc.returncode != 0:
        return proc.returncode
    print("OK: integrate-langgraph path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
