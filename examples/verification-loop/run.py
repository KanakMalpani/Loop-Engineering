#!/usr/bin/env python3
"""Verification loop example using generic loop_runtime."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementations" / "generic"))

from loop_runtime import LoopRuntime, MockLLM, load_lss_spec  # noqa: E402


def default_spec() -> Path:
    return Path(__file__).resolve().parents[1] / "specs" / "runtime-minimal.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run verification loop via loop_runtime")
    parser.add_argument("--spec", type=Path, default=default_spec(), help="LSS YAML path")
    parser.add_argument("--input", default="Fix failing login test in auth module", help="Task input")
    parser.add_argument("--json", action="store_true", help="Print result as JSON")
    args = parser.parse_args()

    try:
        spec = load_lss_spec(args.spec)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    spec["objective"] = spec.get("objective", "Repair failing tests with verified fix")
    runtime = LoopRuntime(spec, llm=MockLLM(seed=spec.get("loop_name", "verification")))
    result = runtime.run(args.input)

    payload = {
        "loop_name": spec.get("loop_name"),
        "success": result.success,
        "iterations": result.iterations,
        "quality_score": result.quality_score,
        "termination_reason": result.termination_reason,
        "history": result.history,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Verification loop: {spec.get('loop_name')}")
        print(f"Success: {result.success} | Iterations: {result.iterations}")
        print(f"Quality: {result.quality_score:.2f} | Reason: {result.termination_reason}")
        for record in result.history:
            print(f"  [{record['iteration']}] score={record['quality_score']:.2f}")

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
