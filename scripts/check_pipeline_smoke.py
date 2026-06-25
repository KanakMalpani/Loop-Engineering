#!/usr/bin/env python3
"""Smoke test loopctl pipeline (Phase 10)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "loopctl",
        "pipeline",
        "--intent",
        "Summarize user feedback into actionable themes",
        "--skip-score",
        "--export",
        "generic",
        "--json",
    ]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return proc.returncode
    if "valid" not in proc.stdout.lower():
        print("FAIL: pipeline JSON missing valid flag", file=sys.stderr)
        return 1
    print("OK: loopctl pipeline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
