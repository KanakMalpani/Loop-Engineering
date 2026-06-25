#!/usr/bin/env python3
"""Generate Loop Trace via LoopGym when installed; else generic runtime."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "submission-dry-run" / "trace-loopgym.json"


def via_loopgym() -> bool:
    try:
        import loopgym as lg  # noqa: F401
    except ImportError:
        return False

    import loopgym as lg

    env = lg.make("loopbench/code-repair-v1")
    try:
        result = env.run_episode(task_id="cr-001", seed=42, trace_path=OUT)
    except TypeError:
        print("loopgym>=0.1.2 required for trace_path — falling back")
        return False
    print(f"LoopGym episode success={result['success']} quality={result['quality_score']}")
    if "loop_trace" in result and not OUT.exists():
        OUT.write_text(json.dumps(result["loop_trace"], indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    return OUT.exists()


def main() -> int:
    if via_loopgym():
        return 0
    print("loopgym not installed — falling back to generic trace demo")
    subprocess.run([sys.executable, "scripts/generate_trace_demo.py"], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
