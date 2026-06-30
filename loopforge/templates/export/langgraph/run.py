#!/usr/bin/env python3
"""Generated LangGraph-oriented stub for {loop_name}."""

from __future__ import annotations

import argparse
import json
import sys


def run_stub_fallback(trace: str, json_out: bool) -> int:
    payload = {
        "mode": "stub",
        "success": True,
        "score": 0.85,
        "iterations": 1,
        "trace": trace,
    }
    if json_out:
        print(json.dumps(payload, indent=2))
    else:
        print(f"No LangGraph/LoopGym — stub success score={payload['score']:.2f}")
    return 0


def run_loopgym_fallback(trace: str, json_out: bool) -> int:
    try:
        import loopgym as lg
    except ImportError:
        return run_stub_fallback(trace, json_out)

    env = lg.make("loopbench/code-repair-v1")
    try:
        result = env.run_episode(task_id="cr-001", seed=42, trace_path=trace)
    except TypeError:
        result = env.run_episode(task_id="cr-001", seed=42)
    payload = {"mode": "loopgym_fallback", "success": result.get("success"), "trace": trace}
    if json_out:
        print(json.dumps(payload, indent=2))
    else:
        print(f"LangGraph not installed — ran LoopGym fallback success={payload['success']}")
    return 0 if payload["success"] else 1


def run_langgraph() -> dict:
    """Minimal reflection-shaped graph mapping LSS workers → nodes."""
    from langgraph.graph import END, StateGraph
    from typing import TypedDict

    class State(TypedDict):
        draft: str
        score: float
        iteration: int

    def generate(state: State) -> State:
        return {{"draft": "draft for {objective_short}", "score": 0.72, "iteration": state.get("iteration", 0) + 1}}

    def evaluate(state: State) -> State:
        return {{"draft": state["draft"], "score": min(0.95, state["score"] + 0.12), "iteration": state["iteration"]}}

    def route(state: State) -> str:
        return "done" if state["score"] >= 0.8 or state["iteration"] >= 3 else "generate"

    g = StateGraph(State)
    g.add_node("generate", generate)
    g.add_node("evaluate", evaluate)
    g.add_conditional_edges("generate", route, {{"generate": "evaluate", "done": END}})
    g.add_edge("evaluate", "generate")
    g.set_entry_point("generate")
    graph = g.compile()
    final = graph.invoke({{"draft": "", "score": 0.0, "iteration": 0}})
    return {{"success": final["score"] >= 0.8, "score": final["score"], "iterations": final["iteration"]}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", default="trace.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        payload = run_langgraph()
        payload["mode"] = "langgraph"
    except ImportError:
        return run_loopgym_fallback(args.trace, args.json)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"success={{payload['success']}} score={{payload['score']:.2f}} iterations={{payload['iterations']}}")
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
