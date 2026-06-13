"""LangGraph implementation of the reflection loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypedDict

try:
    from langgraph.graph import END, StateGraph

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


class ReflectionState(TypedDict, total=False):
    task: str
    objective: str
    draft: str
    critique: str
    quality_score: float
    iteration: int
    max_iterations: int
    quality_threshold: float
    history: list[dict[str, Any]]
    done: bool
    termination_reason: str


@dataclass
class ReflectionGraphResult:
    success: bool
    output: str
    iterations: int
    quality_score: float
    termination_reason: str
    history: list[dict[str, Any]] = field(default_factory=list)


def _mock_llm(prompt: str, role: str = "default") -> str:
    if role == "critic":
        return f"Critique: tighten structure. Score: 0.72. PASS"
    if "revise" in prompt.lower():
        return f"Revised draft addressing feedback for: {prompt[:60]}"
    return f"Initial draft for: {prompt[:80]}"


def _parse_score(text: str, iteration: int) -> float:
    for token in text.split():
        try:
            val = float(token.rstrip("."))
            if 0.0 <= val <= 1.0:
                return min(0.99, val + 0.1 * iteration)
        except ValueError:
            continue
    return min(0.99, 0.55 + 0.12 * iteration)


def _act_node(state: ReflectionState) -> ReflectionState:
    iteration = state.get("iteration", 0) + 1
    if iteration == 1:
        draft = _mock_llm(f"Objective: {state['objective']}\nTask: {state['task']}", "implementer")
    else:
        draft = _mock_llm(
            f"Revise based on: {state.get('critique', '')}\nPrior: {state.get('draft', '')}",
            "implementer",
        )
    history = list(state.get("history", []))
    history.append({"iteration": iteration, "phase": "act", "draft": draft})
    return {**state, "iteration": iteration, "draft": draft, "history": history}


def _reflect_node(state: ReflectionState) -> ReflectionState:
    critique = _mock_llm(f"Evaluate: {state.get('draft', '')}", "critic")
    score = _parse_score(critique, state.get("iteration", 1))
    history = list(state.get("history", []))
    history.append({"iteration": state.get("iteration", 0), "phase": "reflect", "critique": critique, "score": score})
    return {**state, "critique": critique, "quality_score": score, "history": history}


def _should_continue(state: ReflectionState) -> str:
    if state.get("quality_score", 0) >= state.get("quality_threshold", 0.8):
        return "end"
    if state.get("iteration", 0) >= state.get("max_iterations", 5):
        return "end"
    return "act"


def _fallback_run(
    objective: str,
    task: str,
    quality_threshold: float,
    max_iterations: int,
) -> ReflectionGraphResult:
    state: ReflectionState = {
        "objective": objective,
        "task": task,
        "quality_threshold": quality_threshold,
        "max_iterations": max_iterations,
        "iteration": 0,
        "history": [],
    }
    while True:
        state = _act_node(state)
        state = _reflect_node(state)
        if state.get("quality_score", 0) >= quality_threshold:
            reason = "quality_threshold_met"
            break
        if state.get("iteration", 0) >= max_iterations:
            reason = "max_iterations"
            break
    else:
        reason = "unknown"

    score = state.get("quality_score", 0.0)
    return ReflectionGraphResult(
        success=score >= quality_threshold,
        output=state.get("draft", ""),
        iterations=state.get("iteration", 0),
        quality_score=score,
        termination_reason=reason,
        history=state.get("history", []),
    )


def build_reflection_graph() -> Any:
    """Build and compile the LangGraph reflection workflow."""
    if not LANGGRAPH_AVAILABLE:
        return None

    graph = StateGraph(ReflectionState)
    graph.add_node("act", _act_node)
    graph.add_node("reflect", _reflect_node)
    graph.set_entry_point("act")
    graph.add_edge("act", "reflect")
    graph.add_conditional_edges("reflect", _should_continue, {"act": "act", "end": END})
    return graph.compile()


def run_reflection_graph(
    graph: Any,
    objective: str,
    task: str,
    quality_threshold: float = 0.8,
    max_iterations: int = 5,
) -> ReflectionGraphResult:
    """Execute the reflection graph (or fallback runner)."""
    if graph is None:
        return _fallback_run(objective, task, quality_threshold, max_iterations)

    initial: ReflectionState = {
        "objective": objective,
        "task": task,
        "quality_threshold": quality_threshold,
        "max_iterations": max_iterations,
        "iteration": 0,
        "history": [],
        "done": False,
    }
    final = graph.invoke(initial)
    score = final.get("quality_score", 0.0)
    reason = (
        "quality_threshold_met"
        if score >= quality_threshold
        else "max_iterations"
    )
    return ReflectionGraphResult(
        success=score >= quality_threshold,
        output=final.get("draft", ""),
        iterations=final.get("iteration", 0),
        quality_score=score,
        termination_reason=reason,
        history=final.get("history", []),
    )


if __name__ == "__main__":
    g = build_reflection_graph()
    result = run_reflection_graph(
        g,
        objective="Explain loop engineering",
        task="Three bullet summary",
    )
    print(f"Success: {result.success}, iterations: {result.iterations}, score: {result.quality_score:.2f}")
    print(result.output)
