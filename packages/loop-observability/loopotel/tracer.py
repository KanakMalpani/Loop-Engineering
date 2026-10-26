"""LoopTracer — emit LTF spans for loop runs."""

from __future__ import annotations

import functools
import time
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Callable

from loopotel import les as les_metrics
from loopotel.models import isoformat, new_span_id, new_trace_id, otel_attributes, spec_pins, utc_now

# Canonical failure slugs → F-codes (packages/loop-core/specs/loop-ids.md §2).
FAILURE_F_CODES: dict[str, str] = {
    "fail.open_loop": "F1",
    "fail.self_grade": "F2",
    "fail.evaluator_drift": "F3",
    "fail.tau_omission": "F4",
    "fail.false_pass": "F5",
    "fail.false_fail": "F6",
    "fail.oscillation": "F7",
    "fail.resource_bleed": "F8",
    "fail.state_corruption": "F9",
    "fail.orchestration_deadlock": "F10",
    "fail.meta_instability": "F11",
    "fail.safety_bypass": "F12",
}

_current_tracer: ContextVar[LoopTracer | None] = ContextVar("loopotel_current_tracer", default=None)


def current_tracer() -> LoopTracer | None:
    return _current_tracer.get()


def emit_iteration(
    *,
    iteration: int,
    goal_score: float,
    goal_target: float | None = None,
    tokens_delta: int = 0,
    cost_usd: float | None = None,
    latency_ms: float | None = None,
    worker_id: str | None = None,
    evaluator_id: str | None = None,
) -> str | None:
    """Emit an iteration span on the active tracer (no-op if tracing disabled)."""
    tracer = current_tracer()
    if tracer is None or not tracer.enabled:
        return None
    return tracer.emit_iteration(
        iteration=iteration,
        goal_score=goal_score,
        goal_target=goal_target,
        tokens_delta=tokens_delta,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        worker_id=worker_id,
        evaluator_id=evaluator_id,
    )


@dataclass
class LoopTracer:
    """Collect LTF spans for one loop run."""

    loop_name: str
    env_id: str | None = None
    task_id: str | None = None
    goal_target: float = les_metrics.DEFAULT_GOAL_TARGET
    enabled: bool = True
    trace_id: str = field(default_factory=new_trace_id)
    started_at: Any = field(default_factory=utc_now)
    ended_at: Any | None = None
    outcome: str = "unknown"
    termination_reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    _root_span_id: str = field(default_factory=new_span_id)
    _goal_scores: list[float] = field(default_factory=list)
    _spans: list[dict[str, Any]] = field(default_factory=list)
    _token_total: int = 0
    _last_iteration_span_id: str | None = None

    def _span_for(self, span_id: str) -> dict[str, Any]:
        for span in self._spans:
            if span["span_id"] == span_id:
                return span
        raise ValueError(f"unknown span_id: {span_id}")

    def __enter__(self) -> LoopTracer:
        if self.enabled:
            _current_tracer.set(self)
            self._spans.append(
                {
                    "span_id": self._root_span_id,
                    "parent_span_id": None,
                    "name": "loop.run",
                    "kind": "loop",
                    "start_time": isoformat(self.started_at),
                    "attributes": otel_attributes(
                        loop_name=self.loop_name,
                        env_id=self.env_id,
                        task_id=self.task_id,
                        goal_target=self.goal_target,
                    ),
                    "events": [],
                }
            )
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.enabled:
            self.finish(
                outcome="failure" if exc else self.outcome,
                termination_reason=self.termination_reason or ("error" if exc else ""),
            )
            _current_tracer.set(None)

    def emit_iteration(
        self,
        *,
        iteration: int,
        goal_score: float,
        goal_target: float | None = None,
        tokens_delta: int = 0,
        cost_usd: float | None = None,
        latency_ms: float | None = None,
        worker_id: str | None = None,
        evaluator_id: str | None = None,
    ) -> str | None:
        if not self.enabled:
            return None
        target = goal_target if goal_target is not None else self.goal_target
        self._goal_scores.append(goal_score)
        self._token_total += tokens_delta
        eff = les_metrics.effectiveness(goal_score, target)
        cumulative = les_metrics.cumulative_les(self._goal_scores, target)
        now = utc_now()
        span_id = new_span_id()
        events: list[dict[str, Any]] = [
            {
                "name": "loop.iteration.start",
                "timestamp": isoformat(now),
                "attributes": {"loop.iteration": iteration},
            }
        ]
        if worker_id:
            events.append(
                {
                    "name": "loop.worker.complete",
                    "timestamp": isoformat(now),
                    "attributes": {"loop.worker.id": worker_id},
                }
            )
        if evaluator_id:
            events.append(
                {
                    "name": "loop.evaluator.complete",
                    "timestamp": isoformat(now),
                    "attributes": {"loop.evaluator.id": evaluator_id, "loop.goal_score": goal_score},
                }
            )
        events.append(
            {
                "name": "loop.iteration.end",
                "timestamp": isoformat(now),
                "attributes": {"loop.iteration": iteration, "loop.goal_score": goal_score},
            }
        )
        self._spans.append(
            {
                "span_id": span_id,
                "parent_span_id": self._root_span_id,
                "name": "loop.iteration",
                "kind": "iteration",
                "start_time": isoformat(now),
                "end_time": isoformat(now),
                "attributes": otel_attributes(
                    loop_name=self.loop_name,
                    env_id=self.env_id,
                    task_id=self.task_id,
                    iteration=iteration,
                    goal_score=round(goal_score, 4),
                    goal_target=target,
                    tokens_delta=tokens_delta,
                    cost_usd=cost_usd,
                    latency_ms=latency_ms,
                    les_cumulative=cumulative,
                    les_effectiveness=round(eff, 4),
                    worker_id=worker_id,
                    evaluator_id=evaluator_id,
                ),
                "events": events,
            }
        )
        self._last_iteration_span_id = span_id
        return span_id

    def emit_llm_call(
        self,
        *,
        model: str,
        system: str,
        operation: str = "chat",
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        latency_ms: float | None = None,
        parent_span_id: str | None = None,
    ) -> str | None:
        if not self.enabled:
            return None
        parent = (
            parent_span_id
            or self._last_iteration_span_id
            or self._root_span_id
        )
        now = utc_now()
        span_id = new_span_id()
        attrs: dict[str, Any] = {
            "gen_ai.operation.name": operation,
            "gen_ai.system": system,
            "gen_ai.request.model": model,
        }
        if input_tokens is not None:
            attrs["gen_ai.usage.input_tokens"] = input_tokens
        if output_tokens is not None:
            attrs["gen_ai.usage.output_tokens"] = output_tokens
        if latency_ms is not None:
            attrs["loop.latency_ms"] = latency_ms
        self._spans.append(
            {
                "span_id": span_id,
                "parent_span_id": parent,
                "name": f"{operation} {model}",
                "kind": "worker",
                "start_time": isoformat(now),
                "end_time": isoformat(now),
                "attributes": attrs,
                "events": [],
            }
        )
        return span_id

    def emit_failure(self, code: str, *, span_id: str | None = None) -> None:
        if not self.enabled:
            return
        if not code.startswith("fail."):
            raise ValueError(f"failure code must start with 'fail.': {code}")
        target_id = span_id if span_id is not None else self._root_span_id
        span = self._span_for(target_id)
        now = utc_now()
        event_attrs: dict[str, Any] = {"loop.failure.code": code}
        f_code = FAILURE_F_CODES.get(code)
        if f_code is not None:
            event_attrs["loop.failure.f_code"] = f_code
        span["events"].append(
            {
                "name": code,
                "timestamp": isoformat(now),
                "attributes": event_attrs,
            }
        )

    def finish(
        self,
        *,
        outcome: str = "unknown",
        termination_reason: str = "",
    ) -> None:
        if not self.enabled:
            return
        self.outcome = outcome
        self.termination_reason = termination_reason
        self.ended_at = utc_now()
        if self._spans:
            root = self._spans[0]
            root["end_time"] = isoformat(self.ended_at)
            root["attributes"].update(
                otel_attributes(
                    loop_name=self.loop_name,
                    env_id=self.env_id,
                    task_id=self.task_id,
                    outcome=outcome,
                    termination_reason=termination_reason,
                )
            )
            root["attributes"]["loop.tokens_total"] = self._token_total

    def build_trace(self) -> dict[str, Any]:
        if self.ended_at is None:
            self.finish()
        doc: dict[str, Any] = {
            "schema_version": "ltf/0.1",
            "trace_id": self.trace_id,
            "loop_name": self.loop_name,
            "started_at": isoformat(self.started_at),
            "ended_at": isoformat(self.ended_at or utc_now()),
            "outcome": self.outcome,
            "termination_reason": self.termination_reason,
            "spec_pins": spec_pins(),
            "spans": self._spans,
            "metadata": dict(self.metadata),
        }
        if self.env_id is not None:
            doc["env_id"] = self.env_id
        if self.task_id is not None:
            doc["task_id"] = self.task_id
        return doc


def trace_loop(
    *,
    loop_name: str,
    env_id: str | None = None,
    enabled: bool = True,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator: wrap a function in a LoopTracer context."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with LoopTracer(loop_name=loop_name, env_id=env_id, enabled=enabled):
                return fn(*args, **kwargs)

        return wrapper

    return decorator
