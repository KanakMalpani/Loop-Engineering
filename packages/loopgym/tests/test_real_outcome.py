"""Real-outcome code-repair scoring: sandboxed evaluator, spec honouring, leak checks."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

import loopgym as lg
import loopgym.envs.sim as sim_mod
import loopgym.runtime.loop_runtime as rt_mod
from loopgym.evaluators.deterministic import run_deterministic
from loopgym.evaluators.sandbox_tests import FIXTURES_ROOT, extract_code, get_fixture
from loopgym.evaluators.sandbox_tests import test_pass_rate as tpr

LOOPS = Path(__file__).resolve().parents[3] / "benchmarks" / "loopbench-validity" / "loops"
REF = FIXTURES_ROOT / "_reference"
IDS = ["cr-001", "cr-002", "cr-003", "cr-004", "cr-005", "cr-006", "cr-007"]
MOD2ID = {
    "calc": "cr-001",
    "stats": "cr-002",
    "text": "cr-003",
    "durations": "cr-004",
    "intervals": "cr-005",
    "slugs": "cr-006",
    "money": "cr-007",
}


def _block(code: str) -> str:
    return f"```python\n{code}```"


class RecordingStub:
    """Deterministic stub: buggy source first; reference fix only once test feedback arrives."""

    tokens_used = 0

    def __init__(self, always_fix: bool = False):
        self.prompts: list[str] = []
        self.always_fix = always_fix

    def complete(self, prompt, role="default"):
        self.prompts.append(prompt)
        m = re.search(r"Module under repair \((\w+)\.py\)", prompt)
        if not m:
            return "I need more context."
        fid = MOD2ID[m.group(1)]
        if self.always_fix or "Feedback from test_runner" in prompt:
            return _block((REF / f"{fid}.py").read_text())
        return _block(get_fixture(fid).source)


@pytest.mark.parametrize("fid", IDS)
def test_reference_scores_one_empty_scores_zero(fid):
    fx = get_fixture(fid)
    assert tpr(fx, _block((REF / f"{fid}.py").read_text()))["test_pass_rate"] == 1.0
    assert tpr(fx, "")["test_pass_rate"] == 0.0
    assert tpr(fx, "no code here")["test_pass_rate"] == 0.0
    assert tpr(fx, _block(fx.source))["test_pass_rate"] < 1.0


def test_unparseable_and_syntax_error_score_zero():
    fx = get_fixture("cr-001")
    assert extract_code("```python\ndef broken(:\n```") is None
    assert tpr(fx, "```python\ndef broken(:\n```")["score"] == 0.0


def test_deterministic_dispatch_no_mock_rate():
    out = run_deterministic("evaluators.test_pass_rate", "x", {"mock_pass_rate": 1.0})
    assert out["score"] == 0.0  # mock rate is ignored; no fixture -> no real outcome


def test_reference_dir_is_not_a_fixture():
    assert get_fixture("_reference") is None


def _run(loop, llm, task="LB-CR-1"):
    env = lg.make("loopbench/code-repair-v1", spec_path=str(LOOPS / f"{loop}.yaml"),
                  backend="live", llm=llm)
    return env.run_episode(task_id=task, seed=0), env


def test_live_never_builds_mock(monkeypatch):
    class Boom:
        def __init__(self, *a, **k):
            raise RuntimeError("MockLLM constructed")

    monkeypatch.setattr(sim_mod, "MockLLM", Boom)
    monkeypatch.setattr(rt_mod, "MockLLM", Boom)
    stub = RecordingStub(always_fix=True)
    res, _env = _run("good-1-fast", stub)
    assert res["llm_class"] == "RecordingStub"
    assert res["quality_score"] == 1.0
    with pytest.raises(ValueError):
        lg.make("loopbench/code-repair-v1", backend="live")


def test_no_hidden_content_in_prompts():
    for loop in sorted(p.stem for p in LOOPS.glob("*.yaml")):
        stub = RecordingStub()
        _run(loop, stub)
        for fid in IDS:
            public = get_fixture(fid).source + get_fixture(fid).bug_description
            for text in get_fixture(fid).hidden_texts():
                for line in text.splitlines():
                    line = line.strip()
                    if len(line) >= 12 and line not in public:
                        for p in stub.prompts:
                            # the reference fix only appears as the stub's OWN previous reply
                            visible = p.split("Your previous reply:")[0]
                            assert line not in visible, (loop, fid, line)
        assert all("pytest" not in p and "hidden_tests" not in p and "_reference" not in p
                   for p in stub.prompts), loop


def test_working_copy_contains_only_src(monkeypatch):
    import shutil as _sh

    import loopgym.evaluators.sandbox_tests as sb

    seen = {}
    real = _sh.copytree

    def spy(src, dst, *a, **k):
        seen.setdefault(str(dst), str(src))
        return real(src, dst, *a, **k)

    monkeypatch.setattr(sb.shutil, "copytree", spy)
    fx = get_fixture("cr-001")
    tpr(fx, _block(fx.source))
    work = [d for d in seen if "lb-work-" in d]
    hidden = [d for d in seen if "lb-hidden-" in d]
    assert len(work) == 1 and seen[work[0]].endswith("/src")
    assert len(hidden) == 1 and seen[hidden[0]].endswith("hidden_tests")
    assert not Path(hidden[0]).is_relative_to(Path(work[0]))


def test_spec_fields_change_outcomes():
    scores = {}
    for loop in ["good-1-fast", "bad-1-no-feedback", "bad-2-no-tests", "bad-4-no-bug-input"]:
        res, _ = _run(loop, RecordingStub())
        scores[loop] = res["quality_score"]
    assert scores["good-1-fast"] == 1.0  # fixed after test feedback
    assert scores["bad-1-no-feedback"] < 1.0  # no feedback channel, 1 iteration
    assert scores["bad-2-no-tests"] == 0.0  # no deterministic evaluator -> no real outcome
    assert scores["bad-4-no-bug-input"] == 0.0  # no inputs -> no source, no bug


def test_cost_cap_halts_as_fail():
    class Pricey(RecordingStub):
        def complete(self, prompt, role="default"):
            self.tokens_used += 5000
            return super().complete(prompt, role)

    res, _ = _run("bad-5-starved-budget", Pricey(always_fix=True), task="cr-001")
    assert res["success"] is False and res["quality_score"] == 0.0
    assert "cost_limit" in res["termination_reason"]
    res, _ = _run("good-1-fast", Pricey(always_fix=True), task="cr-001")
    assert res["success"] is True


@pytest.mark.parametrize("fid", IDS)
def test_feedback_has_no_expected_literals(fid):
    fx = get_fixture(fid)
    result = tpr(fx, _block(fx.source))
    hints = list(result.get("remediation_hints") or [])
    count_idx = next(
        i for i, hint in enumerate(hints) if isinstance(hint, str) and hint.endswith(" hidden tests passed")
    )
    count_hint = hints[count_idx]
    other_hints = [hint for i, hint in enumerate(hints) if i != count_idx]
    payload = json.dumps(
        {"failures": result.get("failures", []), "remediation_hints": other_hints}
    )
    strings: set[str] = set()
    numbers: set[str] = set()
    for test_file in sorted(fx.hidden_tests_dir.glob("*.py")):
        tree = ast.parse(test_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if len(node.value) >= 2:
                    strings.add(node.value)
            elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float, complex)) and not isinstance(node.value, bool):
                numbers.add(str(node.value))
    for value in strings:
        assert value not in payload
    for value in numbers:
        assert not re.search(rf"(?<!\w){re.escape(value)}(?!\w)", payload)
    assert "assert" not in payload
    assert "Error" not in payload
    assert count_hint == f"{result['tests_passed']}/{result['tests_total']} hidden tests passed"
