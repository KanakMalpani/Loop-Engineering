#!/usr/bin/env python3
"""Run a composed loop from loop-library/compositions/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementations" / "generic"))

from composed_runtime import ComposedLoopRuntime  # noqa: E402

DEFAULT = ROOT / "loop-library" / "compositions" / "code-debug-repair.yaml"


def main() -> int:
    spec = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not spec.exists():
        print(f"Spec not found: {spec}", file=sys.stderr)
        return 1

    runtime = ComposedLoopRuntime(spec)
    result = runtime.run()

    print(f"Composition: {result.composition_type}")
    print(f"Success: {result.success} | Reason: {result.termination_reason}")
    for stage in result.stages:
        r = stage.result
        print(
            f"  [{stage.role}] {stage.child_id} ({stage.loop_name}): "
            f"success={r.success} quality={r.quality_score:.2f} iters={r.iterations}"
        )
    print(f"\nOutput:\n{result.output[:400]}...")
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
