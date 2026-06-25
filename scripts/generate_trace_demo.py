#!/usr/bin/env python3
"""Generate Loop Trace 1.0 from reflection-loop smoke run."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "implementations" / "generic"))

from loop_runtime import LoopRuntime, MockLLM, load_lss_spec  # noqa: E402
from trace_emitter import build_trace  # noqa: E402

SPEC = ROOT / "examples" / "specs" / "runtime-minimal.yaml"
OUT = ROOT / "docs" / "submission-dry-run" / "trace.json"


def main() -> int:
    spec = load_lss_spec(SPEC)
    runtime = LoopRuntime(spec, llm=MockLLM(seed="dry-run"))
    result = runtime.run("Explain loop engineering in three bullet points")
    cost = result.tokens_used * 0.000002
    trace = build_trace(
        spec,
        success=result.success,
        iterations=result.iterations,
        termination_reason=result.termination_reason,
        history=result.history,
        total_cost_usd=cost,
        spec_path=str(SPEC.relative_to(ROOT)),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
