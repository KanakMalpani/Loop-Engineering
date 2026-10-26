"""Tests for gen_ai worker spans and loop failure events (C2a)."""

from __future__ import annotations

import pytest

from loopotel.tracer import LoopTracer
from loopotel.validate import validate_trace


def _span(trace: dict, span_id: str) -> dict:
    for span in trace["spans"]:
        if span["span_id"] == span_id:
            return span
    raise AssertionError(f"span {span_id} not found")


def test_gen_ai_span_under_iteration():
    with LoopTracer(loop_name="test-loop") as t:
        it_id = t.emit_iteration(iteration=1, goal_score=0.1)
        assert isinstance(it_id, str)
        sid = t.emit_llm_call(model="mock-llm", system="mock", input_tokens=50)
        t.finish(outcome="success", termination_reason="goal_met")

    trace = t.build_trace()
    valid, errors = validate_trace(trace)
    assert valid, errors

    span = _span(trace, sid)
    assert span["name"] == "chat mock-llm"
    assert span["kind"] == "worker"
    assert span["parent_span_id"] == it_id
    attrs = span["attributes"]
    assert attrs["gen_ai.operation.name"] == "chat"
    assert attrs["gen_ai.system"] == "mock"
    assert attrs["gen_ai.request.model"] == "mock-llm"
    assert attrs["gen_ai.usage.input_tokens"] == 50
    assert "gen_ai.usage.output_tokens" not in attrs


def test_llm_call_explicit_parent_and_defaults_to_root():
    with LoopTracer(loop_name="test-loop") as t:
        solo = t.emit_llm_call(model="solo", system="mock")
        it_id = t.emit_iteration(iteration=1, goal_score=0.2)
        root_id = next(s["span_id"] for s in t._spans if s["kind"] == "loop")
        explicit = t.emit_llm_call(
            model="gpt",
            system="openai",
            parent_span_id=root_id,
            output_tokens=7,
        )
        t.finish()

    trace = t.build_trace()
    assert _span(trace, solo)["parent_span_id"] == root_id
    explicit_span = _span(trace, explicit)
    assert explicit_span["parent_span_id"] == root_id
    assert explicit_span["parent_span_id"] != it_id
    assert explicit_span["attributes"]["gen_ai.usage.output_tokens"] == 7


def test_emit_failure_canonical_on_root():
    with LoopTracer(loop_name="test-loop") as t:
        t.emit_failure("fail.tau_omission")
        t.finish()

    trace = t.build_trace()
    valid, errors = validate_trace(trace)
    assert valid, errors

    root = trace["spans"][0]
    ev = next(e for e in root["events"] if e["name"] == "fail.tau_omission")
    assert ev["attributes"]["loop.failure.code"] == "fail.tau_omission"
    assert ev["attributes"]["loop.failure.f_code"] == "F4"


def test_emit_failure_noncanonical_and_invalid_code():
    with LoopTracer(loop_name="test-loop") as t:
        t.emit_failure("fail.not_canonical")
        with pytest.raises(ValueError):
            t.emit_failure("bogus")
        t.finish()

    root = t.build_trace()["spans"][0]
    ev = next(e for e in root["events"] if e["name"] == "fail.not_canonical")
    assert ev["attributes"]["loop.failure.code"] == "fail.not_canonical"
    assert "loop.failure.f_code" not in ev["attributes"]


def test_emit_failure_targets_iteration_span():
    with LoopTracer(loop_name="test-loop") as t:
        it_id = t.emit_iteration(iteration=1, goal_score=0.5)
        t.emit_failure("fail.tau_omission", span_id=it_id)
        t.finish()

    trace = t.build_trace()
    it_events = [e for e in _span(trace, it_id)["events"] if e["name"] == "fail.tau_omission"]
    root_events = [e for e in trace["spans"][0]["events"] if e["name"] == "fail.tau_omission"]
    assert len(it_events) == 1
    assert root_events == []


def test_disabled_tracer_gen_ai_and_failure_noop():
    with LoopTracer(loop_name="off", enabled=False) as t:
        assert t.emit_iteration(iteration=1, goal_score=0.1) is None
        assert t.emit_llm_call(model="m", system="s") is None
        t.emit_failure("fail.open_loop")

    assert t.build_trace()["spans"] == []
