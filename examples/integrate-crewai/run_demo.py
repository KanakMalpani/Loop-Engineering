#!/usr/bin/env python3
"""CrewAI integration: intent -> export -> run (Phase 10)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV = {**os.environ, "PYTHONPATH": str(ROOT)}


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="integrate-crew-"))
    spec = tmp / "loop.yaml"
    export_dir = tmp / "crewai-export"

    steps = [
        [
            sys.executable,
            "-m",
            "loopforge",
            "intent",
            "Sequential pipeline of stages from research to writing",
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
            "crewai",
            "--out",
            str(export_dir),
        ],
    ]
    for cmd in steps:
        print("+", " ".join(cmd))
        subprocess.run(cmd, cwd=ROOT, check=True, env=ENV)

    proc = subprocess.run(
        [sys.executable, str(export_dir / "run.py"), "--json"],
        cwd=export_dir,
        capture_output=True,
        text=True,
    )
    print(proc.stdout or proc.stderr)
    if proc.returncode != 0:
        return proc.returncode
    print("OK: integrate-crewai path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
