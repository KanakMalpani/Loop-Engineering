"""Role rules-file pickup probe. No real cursor-agent."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
BENCH = ROOT / "benchmarks" / "loopbench-validity"
if str(BENCH) not in sys.path:
    sys.path.insert(0, str(BENCH))

import cursor_llm
import role_probe

PINNED = "grok-4.7-high"
PROMPT = "Say hello in one short sentence."
ROLE = (
    "Every reply you give must begin with the exact token ROLE-PICKUP-7731 followed by a space."
)


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(cursor_llm, "SANDBOX", tmp_path)
    return tmp_path


def _body(result: str, **extra: object) -> str:
    payload = {"result": result, "usage": {"inputTokens": 1, "outputTokens": 1}, **extra}
    return json.dumps(payload)


def _stub_version(monkeypatch, version: str | None = None) -> None:
    reported = cursor_llm.PINNED_CURSOR_AGENT_VERSION if version is None else version

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, stdout=reported + "\n", stderr="")

    monkeypatch.setattr(cursor_llm.subprocess, "run", fake_run)


def _forbid_run_once(monkeypatch) -> dict:
    state = {"n": 0}

    def fake(self, cmd, cwd, **_extra):
        state["n"] += 1
        raise AssertionError("model call is not allowed")

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    return state


def _argv(out: Path, model: str = PINNED) -> list[str]:
    return ["role_probe.py", "--model", model, "--timeout", "5", "--out", str(out)]


def _invoke() -> object:
    try:
        role_probe.main()
    except SystemExit as exc:
        return 0 if exc.code is None else exc.code
    return 0


def test_role_pickup_success(sandbox, monkeypatch, tmp_path):
    assert sandbox == tmp_path
    _stub_version(monkeypatch)
    out_path = tmp_path / "results" / "role-probe.json"
    monkeypatch.setattr(sys, "argv", _argv(out_path))
    seen = {}

    def fake(self, cmd, cwd, **_extra):
        seen["cmd"] = list(cmd)
        seen["role"] = (Path(cwd) / "AGENTS.md").read_text(encoding="utf-8")
        seen["rule"] = (Path(cwd) / ".cursor" / "rules" / "role.mdc").read_text(encoding="utf-8")
        return _body("ROLE-PICKUP-7731 Hello!", model=PINNED), 0, "stub-stderr"

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    assert _invoke() == 0
    assert seen["cmd"][seen["cmd"].index("--model") + 1] == PINNED
    assert seen["cmd"][-1] == PROMPT
    assert seen["role"].strip() == ROLE
    assert ROLE in seen["rule"]
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written["picked_up"] is True
    assert written["reply"] == "ROLE-PICKUP-7731 Hello!"
    assert written["model"] == PINNED
    assert written["model_requested"] == PINNED
    assert written["model_reported"] == PINNED
    assert written["error"] is None
    assert "invalid" not in written
    assert written["model_check"]["valid"] is True
    assert written["model_check"]["pinned"] == PINNED
    assert written["model_check"]["violations"] == []
    identity = written["launch_identity"]
    assert identity["cursor_agent_bin"] == cursor_llm.CURSOR_BIN
    assert identity["cursor_agent_version"] == cursor_llm.PINNED_CURSOR_AGENT_VERSION
    assert identity["cursor_agent_resolved"] == os.path.realpath(cursor_llm.CURSOR_BIN)
    assert written["calls"]
    for call in written["calls"]:
        assert call["model_requested"] == PINNED
        assert call["model_reported"] == PINNED
        assert call["attempts"]
        for attempt in call["attempts"]:
            path = Path(attempt["stderr_path"])
            assert path == out_path.parent / "stderr" / "role-probe-call0-attempt1.stderr"
            assert path.is_file()
            assert path.read_text(encoding="utf-8") == "stub-stderr"


def test_role_not_picked_up_exits(sandbox, monkeypatch, tmp_path):
    _stub_version(monkeypatch)
    out_path = tmp_path / "role-probe.json"
    monkeypatch.setattr(sys, "argv", _argv(out_path))

    def fake(self, cmd, cwd, **_extra):
        return _body("Hello!"), 0, "stderr"

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    assert _invoke() == 1
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written["picked_up"] is False
    assert written["reply"] == "Hello!"
    assert written["error"] is None
    assert written["model_check"]["valid"] is True
    assert "invalid" not in written


def test_unpinned_model_refused_before_call(sandbox, monkeypatch, tmp_path):
    _stub_version(monkeypatch)
    out_path = tmp_path / "role-probe.json"
    monkeypatch.setattr(sys, "argv", _argv(out_path, model="gpt-5.3-codex"))
    state = _forbid_run_once(monkeypatch)
    with pytest.raises(SystemExit) as caught:
        role_probe.main()
    assert state["n"] == 0
    assert not out_path.exists()
    message = caught.value.code
    assert message not in (0, None)
    assert PINNED in (message if isinstance(message, str) else str(message))


@pytest.mark.parametrize(
    "name",
    [
        "CURSOR_LLM_MODEL",
        "CURSOR_LLM_INFRA_RETRIES",
        "CURSOR_LLM_ISOLATE",
        "CURSOR_AGENT_BIN",
    ],
)
def test_env_override_aborts_before_call(sandbox, monkeypatch, tmp_path, name):
    _stub_version(monkeypatch)
    out_path = tmp_path / "role-probe.json"
    monkeypatch.setattr(sys, "argv", _argv(out_path))
    monkeypatch.setenv(name, "1")
    state = _forbid_run_once(monkeypatch)
    with pytest.raises(RuntimeError, match=name):
        role_probe.main()
    assert state["n"] == 0
    assert not out_path.exists()


def test_version_mismatch_aborts_before_call(sandbox, monkeypatch, tmp_path):
    _stub_version(monkeypatch, "2020.01.01-deadbeef")
    out_path = tmp_path / "role-probe.json"
    monkeypatch.setattr(sys, "argv", _argv(out_path))
    state = _forbid_run_once(monkeypatch)
    with pytest.raises(RuntimeError, match="2020.01.01-deadbeef"):
        role_probe.main()
    assert state["n"] == 0
    assert not out_path.exists()


def test_model_check_mismatch_marks_invalid(sandbox, monkeypatch, tmp_path):
    _stub_version(monkeypatch)
    out_path = tmp_path / "role-probe.json"
    monkeypatch.setattr(sys, "argv", _argv(out_path))

    def fake(self, cmd, cwd, **_extra):
        return _body("ROLE-PICKUP-7731 Hello!", model=PINNED), 0, "stderr"

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    real = cursor_llm.calls_model_check

    def bad_check(calls):
        calls[0]["model_requested"] = "gpt-5.3-codex"
        return real(calls)

    monkeypatch.setattr(cursor_llm, "calls_model_check", bad_check)
    assert _invoke() == 1
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written["invalid"] is True
    assert written["model_check"]["valid"] is False
    assert written["model_check"]["violations"] == [
        {"call": 0, "model_requested": "gpt-5.3-codex"},
    ]
    assert written["calls"][0]["model_requested"] == "gpt-5.3-codex"
    assert written["model_requested"] == "gpt-5.3-codex"


def test_infra_error_records_error(sandbox, monkeypatch, tmp_path):
    _stub_version(monkeypatch)
    out_path = tmp_path / "role-probe.json"
    monkeypatch.setattr(sys, "argv", _argv(out_path))
    state = {"n": 0}

    def fake(self, cmd, cwd, **_extra):
        state["n"] += 1
        return "", 1, "boom-stderr"

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    assert _invoke() == 1
    assert state["n"] == cursor_llm.INFRA_RETRIES + 1
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written["picked_up"] is False
    assert written["error"] == "cursor-agent exited 1 with no output"
    assert written["reply"] == ""
    assert written["model_check"]["valid"] is True
    assert "invalid" not in written
    attempts = written["calls"][0]["attempts"]
    assert len(attempts) == cursor_llm.INFRA_RETRIES + 1
    for attempt in attempts:
        path = Path(attempt["stderr_path"])
        assert path.is_file()
        assert path.parent == out_path.parent / "stderr"
        assert path.read_text(encoding="utf-8") == "boom-stderr"
