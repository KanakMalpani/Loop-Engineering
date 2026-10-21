"""Pinned model, retries, and per-call stderr. No real cursor-agent."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import loopgym.runtime.loop_runtime as loop_rt
from loopgym.envs import sim

ROOT = Path(__file__).resolve().parents[3]
BENCH = ROOT / "benchmarks" / "loopbench-validity"
LOOP = "good-1-fast"
if str(BENCH) not in sys.path:
    sys.path.insert(0, str(BENCH))

import cursor_llm

# run_full replaces MockLLM at import. Put the real classes back so other tests still run.
_SAVED_MOCK = (loop_rt.MockLLM, sim.MockLLM)
import run_full

loop_rt.MockLLM, sim.MockLLM = _SAVED_MOCK

PINNED = "grok-4.7-high"


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(cursor_llm, "SANDBOX", tmp_path)
    return tmp_path


def _body(result: str, **extra: object) -> str:
    payload = {"result": result, "usage": {"inputTokens": 1, "outputTokens": 1}, **extra}
    return json.dumps(payload)


def test_stderr_file_per_attempt_including_retry(sandbox, monkeypatch):
    state = {"n": 0}

    def fake(self, cmd, cwd):
        state["n"] += 1
        if state["n"] == 1:
            exc = subprocess.TimeoutExpired(cmd, 1)
            exc.stderr = "timed out noise"
            raise exc
        return _body("ok-reply"), 0, "second stderr"

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    llm = cursor_llm.CursorAgentLLM(
        timeout=5, log_path=sandbox / "run.log", run_id="sample/r0",
    )
    assert llm.complete("prompt", role="role") == "ok-reply"
    attempts = llm.calls[0]["attempts"]
    assert [item["outcome"] for item in attempts] == ["timeout", "ok"]
    expected = ["timed out noise", "second stderr"]
    for attempt, content, n in zip(attempts, expected, (1, 2), strict=True):
        path = Path(attempt["stderr_path"])
        assert path == sandbox / "stderr" / f"sample_r0-call0-attempt{n}.stderr"
        assert path.read_text(encoding="utf-8") == content
        assert attempt["stderr_bytes"] == len(content.encode("utf-8"))
        assert "stderr_missing" not in attempt


def test_missing_stderr_writes_empty_file(sandbox, monkeypatch):
    def fake(self, cmd, cwd):
        return _body("plain"), 0

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    llm = cursor_llm.CursorAgentLLM(timeout=5, run_id="norun-case")
    assert llm.complete("prompt", role="role") == "plain"
    attempt = llm.calls[0]["attempts"][0]
    path = Path(attempt["stderr_path"])
    assert path == sandbox / "stderr" / "norun-case-call0-attempt1.stderr"
    assert path.read_text(encoding="utf-8") == ""
    assert attempt["stderr_bytes"] == 0
    assert attempt["stderr_missing"] is True


def test_empty_stderr_is_stored(sandbox, monkeypatch):
    def fake(self, cmd, cwd):
        return _body("plain"), 0, ""

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=sandbox / "run.log")
    llm.complete("prompt", role="role")
    attempt = llm.calls[0]["attempts"][0]
    path = Path(attempt["stderr_path"])
    assert path == sandbox / "stderr" / "norun-call0-attempt1.stderr"
    assert path.read_bytes() == b""
    assert attempt["stderr_bytes"] == 0
    assert "stderr_missing" not in attempt


@pytest.mark.parametrize("model", ["", "  "])
def test_empty_model_raises(sandbox, model):
    with pytest.raises(ValueError):
        cursor_llm.CursorAgentLLM(model=model)


@pytest.mark.parametrize(
    "name",
    ["CURSOR_LLM_INFRA_RETRIES", "CURSOR_LLM_ISOLATE", "CURSOR_LLM_MODEL"],
)
def test_env_override_raises(sandbox, monkeypatch, name):
    monkeypatch.setenv(name, "1")
    with pytest.raises(RuntimeError):
        cursor_llm.assert_no_unpinned_env()
    with pytest.raises(RuntimeError):
        cursor_llm.CursorAgentLLM()


def test_model_requested_and_reported(sandbox, monkeypatch):
    replies = [
        {"result": "plain", "usage": {"inputTokens": 0, "outputTokens": 0}},
        {
            "result": "named",
            "usage": {"inputTokens": 0, "outputTokens": 0},
            "model": "grok-4.7-high",
        },
        {
            "result": "info-model",
            "usage": {"inputTokens": 0, "outputTokens": 0},
            "modelInfo": {"model": "from-info"},
        },
        {
            "result": "info-name",
            "usage": {"inputTokens": 0, "outputTokens": 0},
            "modelInfo": {"modelName": "from-name"},
        },
    ]
    state = {"n": 0}

    def fake(self, cmd, cwd):
        body = replies[state["n"]]
        state["n"] += 1
        return json.dumps(body), 0, ""

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=sandbox / "run.log", run_id="m")
    for body in replies:
        assert llm.complete("prompt", role="role") == body["result"]
    assert [call["model_requested"] for call in llm.calls] == [PINNED] * 4
    assert [call["model_reported"] for call in llm.calls] == [
        None, PINNED, "from-info", "from-name",
    ]


def test_model_check_flags_unpinned_and_accepts_pinned():
    bad = {"loop": LOOP, "run": 0, "calls": [{"model_requested": "gpt-5.3-codex"}]}
    good = {"loop": LOOP, "run": 1, "calls": [{"model_requested": PINNED}]}
    flagged = run_full.model_check([bad])
    assert flagged["pinned"] == run_full.PINNED_MODEL == PINNED
    assert flagged["valid"] is False
    assert flagged["violations"] == [{"loop": LOOP, "run": 0, "call": 0}]
    passed = run_full.model_check([good])
    assert passed["valid"] is True
    assert passed["violations"] == []


def test_one_run_requests_pinned_model_not_spec_model(sandbox, monkeypatch, tmp_path):
    spec = (BENCH / "loops" / f"{LOOP}.yaml").read_text(encoding="utf-8")
    assert "gpt-4.1-mini" in spec
    cmds: list[list[str]] = []

    def fake(self, cmd, cwd):
        cmds.append(list(cmd))
        return _body("no code", model=PINNED), 0, ""

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    outdir = tmp_path / "out"
    outdir.mkdir()
    row = run_full.one_run(LOOP, 0, run_full.PINNED_MODEL, "cr-001", outdir, 5, [0])
    assert cmds
    for cmd in cmds:
        index = cmd.index("--model")
        assert cmd[index + 1] == PINNED
        assert all("gpt-4.1-mini" not in part for part in cmd)
    assert row["calls"]
    assert all(call["model_requested"] == PINNED for call in row["calls"])
