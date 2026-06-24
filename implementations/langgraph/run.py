#!/usr/bin/env python3
"""Smoke test for LangGraph reflection bridge (no API keys)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementations" / "langgraph"))

from reflection_graph import build_reflection_graph, run_reflection_graph  # noqa: E402


def main() -> int:
    graph = build_reflection_graph()
    result = run_reflection_graph(
        graph,
        objective="Map LSS composition to LangGraph nodes",
        task="Explain composition.children vs graph nodes",
        quality_threshold=0.75,
        max_iterations=3,
    )
    print(f"success={result.success} iterations={result.iterations} score={result.quality_score:.2f}")
    print(f"termination={result.termination_reason}")
    print("LSS 1.1 mapping: workers->nodes, evaluators->conditional edges, state->TypedDict")
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
