#!/usr/bin/env python3
"""Smoke test loopctl score from pip-style install (Phase 11)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    spec = ROOT / "loopctl" / "schemas" / "minimal-loop.yaml"
    if not spec.is_file():
        print(f"FAIL: missing {spec}", file=sys.stderr)
        return 1

    cmd = [
        sys.executable,
        "-m",
        "loopctl",
        "score",
        "--spec",
        str(spec),
        "--json",
    ]
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "loopforge") + __import__("os").pathsep + str(ROOT / "loopctl") + __import__("os").pathsep + str(ROOT)}
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return proc.returncode

    data = json.loads(proc.stdout)
    if "les" not in data or data["les"] <= 0:
        print(f"FAIL: invalid score output: {data}", file=sys.stderr)
        return 1
    print(f"OK: pip_only_score_smoke LES={data['les']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
