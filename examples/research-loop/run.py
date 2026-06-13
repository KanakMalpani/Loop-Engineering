#!/usr/bin/env python3
"""Research loop example using generic loop_runtime."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementations" / "generic"))

from loop_runtime import LoopRuntime, MockLLM, load_lss_spec  # noqa: E402


def default_spec() -> Path:
    for candidate in (
        ROOT / "STANDARDS" / "examples" / "research-loop.yaml",
        ROOT / "standards" / "examples" / "research-loop.yaml",
        Path(__file__).resolve().parents[1] / "specs" / "runtime-minimal.yaml",
    ):
        if candidate.exists():
            return candidate
    raise FileNotFoundError("No research LSS spec found")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run research loop via loop_runtime")
    parser.add_argument("--spec", type=Path, default=None, help="LSS YAML path")
    parser.add_argument("--topic", default="loop engineering feedback systems", help="Research topic")
    parser.add_argument("--json", action="store_true", help="Print result as JSON")
    args = parser.parse_args()

    try:
        spec = load_lss_spec(args.spec or default_spec())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    runtime = LoopRuntime(spec, llm=MockLLM(seed=f"research:{args.topic[:40]}"))
    result = runtime.run(args.topic)

    payload = {
        "topic": args.topic,
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
        print(f"Research: {args.topic}")
        print(f"Success: {result.success} | Iterations: {result.iterations}")
        print(f"Quality: {result.quality_score:.2f} | Reason: {result.termination_reason}")
        print(f"\nOutput:\n{result.output[:500]}...")

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
