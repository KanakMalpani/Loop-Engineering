#!/usr/bin/env python3
"""Shared helper for integrate-* smoke demos (Phase 11)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run_map_score_demo(
    label: str,
    intent: str,
    *,
    lss: str = "1.0",
    export_target: str | None = None,
) -> int:
    root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONPATH": str(root)}
    tmp = Path(tempfile.mkdtemp(prefix=f"integrate-{label}-"))
    spec = tmp / "loop.yaml"
    export_dir = tmp / f"export-{export_target}" if export_target else None

    steps: list[list[str]] = [
        [
            sys.executable,
            "-m",
            "loopforge",
            "intent",
            intent,
            "-o",
            str(spec),
            "--suggest-level",
        ],
        [sys.executable, "-m", "loopctl", "validate", str(spec), "--lss", lss],
        [sys.executable, "-m", "loopctl", "score", "--spec", str(spec), "--json"],
    ]

    if export_target and export_dir is not None:
        steps.append(
            [
                sys.executable,
                "-m",
                "loopforge",
                "export",
                "--spec",
                str(spec),
                "--target",
                export_target,
                "--out",
                str(export_dir),
            ]
        )

    for cmd in steps:
        print("+", " ".join(cmd))
        proc = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            print(proc.stderr or proc.stdout, file=sys.stderr)
            return proc.returncode
        if cmd[-1] == "--json" and "score" in cmd:
            data = json.loads(proc.stdout)
            if data.get("les", 0) <= 0:
                print(f"FAIL: invalid LES {data}", file=sys.stderr)
                return 1

    if export_dir is not None:
        run_py = export_dir / "run.py"
        if not run_py.exists():
            print("FAIL: export missing run.py", file=sys.stderr)
            return 1
        proc = subprocess.run(
            [sys.executable, str(run_py), "--json"],
            cwd=export_dir,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            print(proc.stderr or proc.stdout, file=sys.stderr)
            return proc.returncode

    print(f"OK: integrate-{label}")
    return 0
