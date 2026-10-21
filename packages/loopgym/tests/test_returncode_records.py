"""Attempt and call records carry returncode. No real cursor-agent."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
BENCH = ROOT / "benchmarks" / "loopbench-validity"
if str(BENCH) not in sys.path:
    sys.path.insert(0, str(BENCH))

import cursor_llm


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(cursor_llm, "SANDBOX", tmp_path)
    return tmp_path


def _body(result: str) -> str:
    payload = {
        "result": result,
        "is_error": False,
        "usage": {"inputTokens": 1, "outputTokens": 1},
    }
    return json.dumps(payload)


def test_ok_returncode_zero_is_clean(sandbox, monkeypatch):
    state = {"n": 0}

    def fake(self, cmd, cwd, **_extra):
        state["n"] += 1
        return _body("hello"), 0, "stderr"

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=sandbox / "run.log", run_id="rc0")
    assert llm.complete("prompt", role="role") == "hello"
    assert state["n"] == 1
    call = llm.calls[0]
    assert len(call["attempts"]) == 1
    attempt = call["attempts"][0]
    assert attempt["outcome"] == "ok"
    assert attempt["returncode"] == 0
    assert attempt["rc_nonzero"] is False
    assert attempt["clean"] is True
    assert call["returncode"] == 0
    assert call["rc_nonzero"] is False
    log = (sandbox / "run.log").read_text(encoding="utf-8")
    assert " rc=0" in log


def test_ok_nonzero_returncode_is_not_retried(sandbox, monkeypatch):
    state = {"n": 0}

    def fake(self, cmd, cwd, **_extra):
        state["n"] += 1
        return _body("still-ok"), 3, "stderr"

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=sandbox / "run.log", run_id="rc3")
    assert llm.complete("prompt", role="role") == "still-ok"
    assert state["n"] == 1
    call = llm.calls[0]
    assert len(call["attempts"]) == 1
    attempt = call["attempts"][0]
    assert attempt["outcome"] == "ok"
    assert attempt["returncode"] == 3
    assert attempt["rc_nonzero"] is True
    assert attempt["clean"] is False
    assert call["returncode"] == 3
    assert call["rc_nonzero"] is True
    log = (sandbox / "run.log").read_text(encoding="utf-8")
    assert " rc=3" in log


def test_prior_nonzero_marks_call_even_when_final_is_clean(sandbox, monkeypatch):
    state = {"n": 0}

    def fake(self, cmd, cwd, **_extra):
        state["n"] += 1
        if state["n"] == 1:
            return "", 5, "boom"
        return _body("recovered"), 0, "stderr"

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=sandbox / "run.log", run_id="mix")
    assert llm.complete("prompt", role="role") == "recovered"
    call = llm.calls[0]
    assert [item["returncode"] for item in call["attempts"]] == [5, 0]
    assert call["attempts"][0]["rc_nonzero"] is True
    assert call["attempts"][0]["clean"] is False
    assert call["attempts"][1]["clean"] is True
    assert call["returncode"] == 0
    assert call["rc_nonzero"] is True


def test_timeout_attempt_returncode_is_none(sandbox, monkeypatch):
    def fake(self, cmd, cwd, **_extra):
        raise subprocess.TimeoutExpired(cmd, 1)

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=sandbox / "run.log", run_id="to")
    with pytest.raises(cursor_llm.InfraError):
        llm.complete("prompt", role="role")
    attempts = llm.calls[0]["attempts"]
    assert len(attempts) == cursor_llm.INFRA_RETRIES + 1
    for attempt in attempts:
        assert attempt["outcome"] == "timeout"
        assert attempt["returncode"] is None
        assert attempt["rc_nonzero"] is False
        assert attempt["clean"] is False
    assert llm.calls[0]["returncode"] is None
    assert llm.calls[0]["rc_nonzero"] is False
    log = (sandbox / "run.log").read_text(encoding="utf-8")
    assert log.count(" rc=None") == cursor_llm.INFRA_RETRIES + 1
