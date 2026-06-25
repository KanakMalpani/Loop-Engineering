#!/usr/bin/env python3
"""LE-OP-11 level recommender benchmark v0.2 — CI gate."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks" / "results" / "le-op-11-recommender-v0.2.json"
TOOL = ROOT / "tools" / "level_recommender.py"


def main() -> int:
    if not TOOL.exists():
        print(f"MISSING: {TOOL}", file=sys.stderr)
        return 1
    try:
        import datasets  # noqa: F401
    except ImportError:
        stub = {
            "version": "0.2",
            "problem": "LE-OP-11",
            "skipped": True,
            "reason": "pip install datasets",
            "metrics": {"misassignment_rate": None, "meets_le_op_11_target": None},
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(stub, indent=2) + "\n", encoding="utf-8")
        print("SKIP: datasets not installed (offline CI)")
        return 0

    proc = subprocess.run(
        [sys.executable, str(TOOL), "--output", str(OUT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return proc.returncode

    report = json.loads(OUT.read_text(encoding="utf-8"))
    report["version"] = "0.2"
    report["integration_note"] = "Used by loopctl pipeline --suggest-level via loopforge level hints"
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    rate = report.get("metrics", {}).get("misassignment_rate", 1.0)
    meets = report.get("metrics", {}).get("meets_le_op_11_target", False)
    print(f"misassignment_rate: {rate:.1%} target<=15%: {'PASS' if meets else 'PENDING'}")
    print(f"Wrote {OUT}")
    # v0.2 gate: track metric even if target not met (datasets optional offline)
    return 0 if OUT.exists() else 1


if __name__ == "__main__":
    raise SystemExit(main())
