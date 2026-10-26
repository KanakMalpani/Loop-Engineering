"""LoopGym gen_ai wiring integration tests (C2b)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES = REPO_ROOT / "packages/loopbench/fixtures"
SPEC_PATH = REPO_ROOT / "packages/loopgym/loopgym/envs/loopbench/code-repair-v1/spec.yaml"

os.environ["LOOPBENCH_FIXTURES"] = str(FIXTURES)

pytest.importorskip("loopgym")

import loopgym as lg

from loopotel.integrations.loopgym import run_traced_episode
from loopotel.validate import validate_trace


def _episode_trace(enabled: bool = True) -> tuple[dict, dict]:
    env = lg.make("loopbench/code-repair-v1", spec_path=str(SPEC_PATH), seed=0)
    return run_traced_episode(env, task_id="cr-001", seed=0, enabled=enabled)


def _gen_ai_spans(trace: dict) -> list[dict]:
    return [s for s in trace["spans"] if "gen_ai.operation.name" in s.get("attributes", {})]


def test_gen_ai_span_per_iteration():
    _result, trace = _episode_trace(enabled=True)
    iterations = [s for s in trace["spans"] if s["kind"] == "iteration"]
    gen_ai = _gen_ai_spans(trace)
    assert len(iterations) >= 1
    assert len(gen_ai) == len(iterations)

    iter_ids = {s["span_id"] for s in iterations}
    parents: dict[str, int] = {}
    for span in gen_ai:
        assert span["kind"] == "worker"
        assert span["name"] == "chat mock-llm"
        attrs = span["attributes"]
        assert attrs["gen_ai.operation.name"] == "chat"
        assert attrs["gen_ai.system"] == "mock"
        assert attrs["gen_ai.request.model"] == "mock-llm"
        assert isinstance(attrs["gen_ai.usage.input_tokens"], int)
        assert attrs["gen_ai.usage.input_tokens"] > 0
        assert "gen_ai.usage.output_tokens" not in attrs
        pid = span["parent_span_id"]
        assert pid in iter_ids
        parents[pid] = parents.get(pid, 0) + 1
    assert parents == dict.fromkeys(iter_ids, 1)

    valid, errors = validate_trace(trace)
    assert valid, errors


def test_failure_event_on_failed_episode():
    result, trace = _episode_trace(enabled=True)
    assert result["success"] is False
    assert "max_iterations" in result["termination_reason"]

    root = next(s for s in trace["spans"] if s["kind"] == "loop")
    ev = next(e for e in root["events"] if e["name"] == "fail.tau_omission")
    assert ev["attributes"]["loop.failure.code"] == "fail.tau_omission"
    assert ev["attributes"]["loop.failure.f_code"] == "F4"


def test_disabled_no_gen_ai():
    _result, trace = _episode_trace(enabled=False)
    assert _gen_ai_spans(trace) == []
    assert trace["spans"] == []
