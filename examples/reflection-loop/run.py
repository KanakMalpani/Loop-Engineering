#!/usr/bin/env python3
"""Reflection loop example using generic loop_runtime."""

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


def inline_spec() -> dict:
    return {
        "loop_name": "reflection-example",
        "version": "1.0",
        "objective": "Refine draft through iterative critique",
        "workers": [{"id": "writer", "role": "actor", "policy": "Draft and improve"}],
        "evaluators": [{"id": "quality", "type": "rubric", "threshold": 0.75}],
        "termination_conditions": [{"type": "max_iterations", "value": 5}],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run reflection loop via loop_runtime")
    parser.add_argument("--spec", type=Path, default=None, help="LSS YAML path")
    parser.add_argument("--input", default="Explain loop engineering in three bullet points", help="Task input")
    parser.add_argument("--json", action="store_true", help="Print result as JSON")
    args = parser.parse_args()

    try:
        if args.spec:
            spec = load_lss_spec(args.spec)
        elif default_spec().exists():
            spec = load_lss_spec(default_spec())
        else:
            spec = inline_spec()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    runtime = LoopRuntime(spec, llm=MockLLM(seed=spec.get("loop_name", "reflection")))
    result = runtime.run(args.input)

    payload = {
        "loop_name": spec.get("loop_name"),
        "success": result.success,
        "iterations": result.iterations,
        "quality_score": result.quality_score,
        "termination_reason": result.termination_reason,
        "output": result.output,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Loop: {spec.get('loop_name')}")
        print(f"Success: {result.success} | Iterations: {result.iterations}")
        print(f"Quality: {result.quality_score:.2f} | Reason: {result.termination_reason}")
        print(f"\nOutput:\n{result.output}")

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
