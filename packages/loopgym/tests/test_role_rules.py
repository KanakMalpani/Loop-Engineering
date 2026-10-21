"""Role is an instruction file. Temperature is logged and not sent. No real cursor-agent."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from loopgym.evaluators.sandbox_tests import extract_code, get_fixture
from loopgym.evaluators.sandbox_tests import test_pass_rate as score_output
from loopgym.runtime.loop_runtime import LoopState, worker_instruction, worker_temperature
from loopgym.runtime.outcome_runtime import CodeRepairRuntime

ROOT = Path(__file__).resolve().parents[3]
BENCH = ROOT / "benchmarks" / "loopbench-validity"
LOOPS = BENCH / "loops"
if str(BENCH) not in sys.path:
    sys.path.insert(0, str(BENCH))

import cursor_llm

ROLE = "Rewrite identifiers into another notation"
TASK = "Repair the module described below."
REPLY = "full reply line 1\nfull reply line 2\n"


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(cursor_llm, "SANDBOX", tmp_path)
    return tmp_path


def _ok_payload(text: str = REPLY) -> tuple[str, int]:
    body = {"result": text, "usage": {"inputTokens": 2, "outputTokens": 3}}
    return json.dumps(body), 0


def test_rules_hold_role_prompt_does_not_and_temperature_is_not_applied(sandbox, monkeypatch):
    seen: dict = {}

    def fake(self, cmd, cwd, **_extra):
        work = Path(cwd)
        seen["cmd"] = cmd
        seen["cwd"] = work
        seen["agents"] = (work / "AGENTS.md").read_text(encoding="utf-8")
        seen["rule"] = (work / ".cursor" / "rules" / "role.mdc").read_text(encoding="utf-8")
        return _ok_payload()

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    llm = cursor_llm.CursorAgentLLM(
        model="stub-model",
        timeout=5,
        log_path=sandbox / "run.log",
        run_id="sample/r0",
    )
    text = llm.complete(TASK, role=ROLE, temperature=1.8)
    prompt = seen["cmd"][-1]
    assert text == REPLY
    assert seen["agents"].strip() == ROLE
    assert "alwaysApply: true" in seen["rule"]
    assert ROLE in seen["rule"]
    assert prompt == TASK
    assert ROLE not in prompt
    assert "You are the" not in prompt
    assert "plain text" not in prompt.lower()
    assert "```python" not in prompt
    assert "temperature" not in " ".join(seen["cmd"]).lower()
    call = llm.calls[0]
    assert call["reply"] == REPLY
    assert call["temperature_requested"] == 1.8
    assert call["temperature_applied"] is False
    log = (sandbox / "run.log").read_text(encoding="utf-8")
    assert "sample/r0" in log
    assert "call=0" in log and "attempt=1" in log and "outcome=ok" in log
    assert "seconds=" in log


def test_each_attempt_is_logged_and_ok_is_not_retried(sandbox, monkeypatch):
    calls = {"n": 0, "cwds": []}

    def fake(self, cmd, cwd, **_extra):
        calls["n"] += 1
        calls["cwds"].append(Path(cwd))
        if calls["n"] == 1:
            raise subprocess.TimeoutExpired(cmd, 1)
        if calls["n"] == 2:
            return "not-json", 0
        return _ok_payload("done")

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    llm = cursor_llm.CursorAgentLLM(model="stub-model", timeout=5, log_path=sandbox / "run.log",
                                    run_id="sample/r1")
    assert llm.complete(TASK, role=ROLE, temperature=0) == "done"
    assert calls["n"] == 3
    assert llm.calls[0]["reply"] == "done"
    assert [item["outcome"] for item in llm.calls[0]["attempts"]] == ["timeout", "bad_json", "ok"]
    assert llm.calls[0]["temperature_requested"] == 0
    assert llm.calls[0]["temperature_applied"] is False
    log = (sandbox / "run.log").read_text(encoding="utf-8")
    assert "outcome=timeout" in log
    assert "outcome=bad_json" in log
    assert "outcome=ok" in log
    assert "attempt=1" in log and "attempt=2" in log and "attempt=3" in log

    def once(self, cmd, cwd, **_extra):
        calls["cwds"].append(Path(cwd))
        calls["n"] += 1
        return _ok_payload("only")

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", once)
    before = calls["n"]
    assert llm.complete("second task", role=ROLE, temperature=0.2) == "only"
    assert calls["n"] == before + 1
    assert calls["cwds"][-1] != calls["cwds"][-2]
    assert "call=1" in (sandbox / "run.log").read_text(encoding="utf-8")
    assert llm.calls[1]["temperature_applied"] is False


@pytest.mark.parametrize(
    ("reply", "expected"),
    [
        ("```\nx = 1\n```", "x = 1\n"),
        ("```python\nx = 1\n```", "x = 1\n"),
        ("```javascript\nx = 1\n```", None),
    ],
)
def test_fence_tag_extraction(reply, expected):
    assert extract_code(reply) == expected


def test_unparseable_hint_does_not_demand_a_language():
    hint = score_output(get_fixture("cr-001"), "no code")["remediation_hints"][0]
    assert "```python" not in hint
    assert "python" not in hint.lower()
    assert "fenced code block" in hint


@pytest.mark.parametrize("spec_path", sorted(LOOPS.glob("*.yaml")), ids=lambda path: path.stem)
def test_spec_role_is_instruction_not_prompt(spec_path, sandbox, monkeypatch):
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    worker = spec["workers"][0]
    role = worker_instruction(worker)
    temperature = worker_temperature(worker)
    prompts: list[str] = []

    def fake(self, cmd, cwd, **_extra):
        work = Path(cwd)
        prompts.append(cmd[-1])
        assert (work / "AGENTS.md").read_text(encoding="utf-8").strip() == role
        rule = (work / ".cursor" / "rules" / "role.mdc").read_text(encoding="utf-8")
        assert "alwaysApply: true" in rule
        assert role in rule
        assert role not in cmd[-1]
        return _ok_payload("no code")

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    llm = cursor_llm.CursorAgentLLM(model="stub-model", timeout=5, log_path=sandbox / "run.log",
                                    run_id="sample/r2")
    runtime = CodeRepairRuntime(spec, llm=llm, fixture=get_fixture("cr-001"))
    state = LoopState()
    for _ in range(2):
        if state.terminated:
            break
        runtime.step_once(state)
    assert prompts
    for prompt in prompts:
        assert role not in prompt
        assert "temperature" not in prompt.lower()
        assert "```python" not in prompt
        assert "You are the" not in prompt
        assert "plain text" not in prompt.lower()
        assert "Your role" not in prompt
    assert llm.calls
    assert all(call["temperature_requested"] == temperature for call in llm.calls)
    assert all(call["temperature_applied"] is False for call in llm.calls)
    assert all(call["role"] == role for call in llm.calls)


def _any_spec() -> dict:
    return yaml.safe_load(min(LOOPS.glob("*.yaml")).read_text(encoding="utf-8"))


def test_system_prompt_field_overrides_role_text(sandbox, monkeypatch):
    spec = _any_spec()
    spec["workers"][0]["system_prompt"] = "UNIQUE_SYSTEM_INSTRUCTION"
    spec["workers"][0]["role"] = "UNIQUE_ROLE_NOT_USED"
    seen: dict = {}

    def fake(self, cmd, cwd, **_extra):
        seen["prompt"] = cmd[-1]
        seen["agents"] = (Path(cwd) / "AGENTS.md").read_text(encoding="utf-8")
        return _ok_payload("no code")

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    llm = cursor_llm.CursorAgentLLM(model="stub-model", timeout=5)
    runtime = CodeRepairRuntime(spec, llm=llm, fixture=get_fixture("cr-001"))
    runtime.step_once(LoopState())
    assert seen["agents"].strip() == "UNIQUE_SYSTEM_INSTRUCTION"
    assert "UNIQUE_SYSTEM_INSTRUCTION" not in seen["prompt"]
    assert "UNIQUE_ROLE_NOT_USED" not in seen["prompt"]
    assert llm.calls[0]["role"] == "UNIQUE_SYSTEM_INSTRUCTION"


def test_legacy_complete_signature_still_runs():
    spec = _any_spec()
    role = worker_instruction(spec["workers"][0])

    class Legacy:
        tokens_used = 0

        def __init__(self):
            self.got = None

        def complete(self, prompt, role="default"):
            self.got = (prompt, role)
            return "no code"

    legacy = Legacy()
    runtime = CodeRepairRuntime(spec, llm=legacy, fixture=get_fixture("cr-001"))
    runtime.step_once(LoopState())
    prompt, got_role = legacy.got
    assert got_role == role
    assert role not in prompt
    assert "temperature" not in prompt.lower()
    assert "```python" not in prompt
