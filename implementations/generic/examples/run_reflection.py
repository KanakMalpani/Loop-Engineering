#!/usr/bin/env python3
"""Run the generic reflection loop against the minimal LSS example."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running as script from examples/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reflection_loop import ReflectionLoop, load_lss_spec  # noqa: E402


def default_spec_path() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "standards" / "examples" / "minimal-loop.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a reflection loop from an LSS spec")
    parser.add_argument("--spec", type=Path, default=default_spec_path(), help="Path to LSS YAML")
    parser.add_argument("--input", default="Explain loop engineering in three bullet points", help="Task input")
    parser.add_argument("--json", action="store_true", help="Print result as JSON")
    args = parser.parse_args()

    spec = load_lss_spec(args.spec)
    loop = ReflectionLoop(spec)
    result = loop.run(args.input)

    if args.json:
        print(
            json.dumps(
                {
                    "success": result.success,
                    "output": result.output,
                    "iterations": result.iterations,
                    "quality_score": result.quality_score,
                    "termination_reason": result.termination_reason,
                    "elapsed_seconds": result.elapsed_seconds,
                    "tokens_used": result.tokens_used,
                },
                indent=2,
            )
        )
    else:
        print(f"Loop: {spec.get('loop_name')} v{spec.get('version')}")
        print(f"Success: {result.success}")
        print(f"Iterations: {result.iterations}")
        print(f"Quality: {result.quality_score:.2f}")
        print(f"Reason: {result.termination_reason}")
        print(f"Tokens: {result.tokens_used}")
        print(f"\nOutput:\n{result.output}")

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
