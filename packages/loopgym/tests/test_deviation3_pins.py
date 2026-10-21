"""Pinned model, retries, and per-call stderr. No real cursor-agent."""

from __future__ import annotations

import json
import os
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
import leak_probe

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

    def fake(self, cmd, cwd, **_extra):
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
    def fake(self, cmd, cwd, **_extra):
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
    def fake(self, cmd, cwd, **_extra):
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
    [
        "CURSOR_LLM_INFRA_RETRIES",
        "CURSOR_LLM_ISOLATE",
        "CURSOR_LLM_MODEL",
        "CURSOR_AGENT_BIN",
    ],
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

    def fake(self, cmd, cwd, **_extra):
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

    def fake(self, cmd, cwd, **_extra):
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


def test_cursor_bin_is_home_pin():
    assert cursor_llm.CURSOR_BIN == str(Path.home() / ".local" / "bin" / "cursor-agent")
    assert cursor_llm.PINNED_CURSOR_AGENT_VERSION == "2026.10.19-6bbf2c4"


def test_version_mismatch_raises(monkeypatch):
    _stub_version(monkeypatch, "2020.01.01-deadbeef")
    with pytest.raises(RuntimeError):
        cursor_llm.assert_launch_identity()


def test_matching_version_returns_resolved_path(monkeypatch):
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = list(cmd)
        seen["timeout"] = kwargs.get("timeout")
        return subprocess.CompletedProcess(cmd, 0, stdout="2026.10.19-6bbf2c4\n", stderr="")

    monkeypatch.setattr(cursor_llm.subprocess, "run", fake_run)
    ident = cursor_llm.assert_launch_identity()
    assert seen["cmd"] == [cursor_llm.CURSOR_BIN, "--version"]
    assert seen["timeout"] == 30
    assert ident["cursor_agent_bin"] == cursor_llm.CURSOR_BIN
    assert ident["cursor_agent_resolved"] == os.path.realpath(cursor_llm.CURSOR_BIN)
    assert ident["cursor_agent_version"] == cursor_llm.PINNED_CURSOR_AGENT_VERSION


def test_calls_model_check_flags_mismatched_model_requested():
    flagged = cursor_llm.calls_model_check([
        {"model_requested": "gpt-5.3-codex", "model_reported": "gpt-5.3-codex"},
    ])
    assert flagged["pinned"] == PINNED
    assert flagged["valid"] is False
    assert flagged["violations"] == [{"call": 0, "model_requested": "gpt-5.3-codex"}]
    passed = cursor_llm.calls_model_check([{"model_requested": PINNED, "model_reported": None}])
    assert passed["valid"] is True
    assert passed["violations"] == []


@pytest.mark.parametrize("entry", ["leak_probe.py", "run_full.py"])
def test_probes_refuse_unpinned_model_before_call(monkeypatch, entry):
    if entry == "leak_probe.py":
        monkeypatch.setattr(sys, "argv", [entry, "--model", "gpt-5.3-codex"])
        target = leak_probe.main
    else:
        monkeypatch.setattr(sys, "argv", [entry, "--probe", "1", "--model", "gpt-5.3-codex"])
        target = run_full.main
    _stub_version(monkeypatch)
    state = _forbid_run_once(monkeypatch)
    with pytest.raises(SystemExit) as caught:
        target()
    assert state["n"] == 0
    message = caught.value.code
    assert message not in (0, None)
    assert PINNED in (message if isinstance(message, str) else str(message))


def test_leak_probe_output_records_models(sandbox, monkeypatch, tmp_path):
    _stub_version(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["leak_probe.py", "--model", PINNED])
    monkeypatch.setattr(leak_probe, "results_dir", tmp_path)

    def fake(self, cmd, cwd, **_extra):
        return _body("probe-stub-reply", model=PINNED), 0, ""

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    leak_probe.main()
    out = json.loads((tmp_path / "leak-probe.json").read_text(encoding="utf-8"))
    assert out["model_requested"] == PINNED
    assert out["model_reported"] == PINNED
    assert out["model_check"]["valid"] is True
    assert out["launch_identity"]["cursor_agent_bin"] == cursor_llm.CURSOR_BIN
    assert out["launch_identity"]["cursor_agent_version"] == cursor_llm.PINNED_CURSOR_AGENT_VERSION


def test_probe_main_invalid_model_check_exits(sandbox, monkeypatch, tmp_path):
    _stub_version(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["run_full.py", "--probe", "1", "--model", PINNED])
    monkeypatch.setattr(run_full, "here", tmp_path)

    def fake(self, cmd, cwd, **_extra):
        return _body("corrected", model="other-model"), 0, ""

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)

    def bad_check(calls):
        return {
            "pinned": PINNED,
            "valid": False,
            "violations": [{"call": 0, "model_requested": calls[0].get("model_requested")}],
        }

    monkeypatch.setattr(cursor_llm, "calls_model_check", bad_check)
    with pytest.raises(SystemExit) as caught:
        run_full.main()
    assert caught.value.code not in (0, None)
    written = json.loads((tmp_path / "results" / "probe-1.json").read_text(encoding="utf-8"))
    assert written["invalid"] is True
    assert written["model_check"]["valid"] is False
    assert written["calls"][0]["model_requested"] == PINNED
    assert "model_reported" in written["calls"][0]
    assert written["launch_identity"]["cursor_agent_resolved"] == os.path.realpath(cursor_llm.CURSOR_BIN)
