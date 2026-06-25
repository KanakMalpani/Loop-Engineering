#!/usr/bin/env python3
"""Smoke test loopctl pipeline with structural score (Phase 11)."""

from __future__ import annotations

import json
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
        "--export",
        "generic",
        "--json",
    ]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return proc.returncode
    data = json.loads(proc.stdout)
    if not data.get("valid"):
        print("FAIL: pipeline not valid", file=sys.stderr)
        return 1
    if "structural_les" not in data:
        print("FAIL: pipeline missing structural_les", file=sys.stderr)
        return 1
    print("OK: loopctl pipeline with score")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
