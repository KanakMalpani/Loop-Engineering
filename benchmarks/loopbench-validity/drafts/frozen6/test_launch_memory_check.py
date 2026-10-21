"""Launch MemAvailable preflight for the frozen6 draft runner.

No real cursor-agent and no real /proc read.
Loads drafts/frozen6/run_full.py and expects a 6144 MB floor.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

DRAFT = Path(__file__).resolve().parent
BENCH = DRAFT.parents[1]
REPO = DRAFT.parents[3]
LOOPGYM_SRC = REPO / "packages" / "loopgym"
if BENCH.name != "loopbench-validity":
    raise RuntimeError(f"draft test expected loopbench-validity, found {BENCH}")
# The installed loopgym has no evaluators.sandbox_tests. Probe main imports it
# from the source tree, which is what packages/loopgym's own pytest rootdir does.
if not (LOOPGYM_SRC / "loopgym" / "evaluators" / "sandbox_tests.py").is_file():
    raise RuntimeError(f"loopgym source missing sandbox_tests under {LOOPGYM_SRC}")
sys.path.insert(0, str(LOOPGYM_SRC))

import loopgym.runtime.loop_runtime as loop_rt
from loopgym.envs import sim

# cursor_llm stays the module beside the FROZEN-5 runner. This draft does not copy it.
if str(BENCH) not in sys.path:
    sys.path.insert(0, str(BENCH))

import cursor_llm

# run_full replaces MockLLM at import. Put the real classes back so other tests still run.
_SAVED_MOCK = (loop_rt.MockLLM, sim.MockLLM)
sys.path.insert(0, str(DRAFT))
import run_full

loop_rt.MockLLM, sim.MockLLM = _SAVED_MOCK

if Path(run_full.__file__).resolve() != (DRAFT / "run_full.py").resolve():
    raise RuntimeError(f"loaded {run_full.__file__}, expected draft run_full.py")
if run_full.MIN_AVAILABLE_MB != 6144:
    raise RuntimeError(f"draft floor is {run_full.MIN_AVAILABLE_MB}, expected 6144")

PINNED = "grok-4.7-high"


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


def _meminfo(tmp_path: Path, kb: int) -> Path:
    path = tmp_path / "meminfo"
    path.write_text(
        f"MemTotal:       {kb + 10} kB\nMemAvailable:    {kb} kB\n",
        encoding="utf-8",
    )
    return path


def test_mem_available_mb_parses_meminfo_file(tmp_path):
    path = _meminfo(tmp_path, 6291456)
    assert run_full.mem_available_mb(meminfo_path=str(path)) == 6291456 // 1024
    low = _meminfo(tmp_path, 6291455)
    assert run_full.mem_available_mb(str(low)) == 6143


@pytest.mark.parametrize(
    ("mb", "ok", "status"),
    [(6143, False, "ABORT"), (6144, True, "PASS"), (6145, True, "PASS")],
)
def test_check_launch_memory_threshold(mb, ok, status, monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(run_full, "here", tmp_path)
    seen = {"n": 0}

    def fake(meminfo_path: str = "/proc/meminfo") -> int:
        seen["n"] += 1
        assert meminfo_path == "/proc/meminfo"
        return mb

    monkeypatch.setattr(run_full, "mem_available_mb", fake)
    result = run_full.check_launch_memory(tmp_path)
    assert seen["n"] == 1
    assert result == {
        "available_mb": mb,
        "required_mb": 6144,
        "ok": ok,
        "time_ist": result["time_ist"],
    }
    assert result["time_ist"].endswith("+05:30")
    assert "T" in result["time_ist"]
    assert "." not in result["time_ist"]
    line = (
        f"{result['time_ist']} LAUNCH-MEMCHECK available_mb={mb} "
        f"required_mb=6144 result={status}"
    )
    log_path = tmp_path / "results" / "launch-memcheck.log"
    assert log_path.read_text(encoding="utf-8").splitlines() == [line]
    assert capsys.readouterr().err.splitlines() == [line]


def test_main_aborts_below_6144_before_any_llm(monkeypatch, tmp_path, capsys):
    _stub_version(monkeypatch)
    monkeypatch.setattr(run_full, "here", tmp_path)
    monkeypatch.setattr(sys, "argv", ["run_full.py", "--probe", "1", "--model", PINNED])
    monkeypatch.setattr(run_full, "mem_available_mb", lambda meminfo_path="/proc/meminfo": 6143)
    constructed = {"n": 0}

    def init(self, *args, **kwargs):
        constructed["n"] += 1
        raise AssertionError("LLM constructed")

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "__init__", init)
    calls = _forbid_run_once(monkeypatch)
    with pytest.raises(SystemExit) as caught:
        run_full.main()
    assert caught.value.code not in (0, None)
    message = caught.value.code if isinstance(caught.value.code, str) else str(caught.value.code)
    assert "6143" in message
    assert "6144" in message
    assert constructed["n"] == 0
    assert calls["n"] == 0
    assert not (tmp_path / "results" / "probe-1.json").exists()
    log = (tmp_path / "results" / "launch-memcheck.log").read_text(encoding="utf-8")
    assert "available_mb=6143" in log
    assert "required_mb=6144" in log
    assert "result=ABORT" in log
    assert "+05:30" in log
    assert "available_mb=6143" in capsys.readouterr().err


def test_probe_main_calls_launch_memory_check_once(monkeypatch, tmp_path):
    _stub_version(monkeypatch)
    monkeypatch.setattr(run_full, "here", tmp_path)
    monkeypatch.setattr(sys, "argv", ["run_full.py", "--probe", "1", "--model", PINNED])
    monkeypatch.setattr(run_full, "mem_available_mb", lambda meminfo_path="/proc/meminfo": 6144)
    seen = {"n": 0}
    real = run_full.check_launch_memory

    def wrapped(outdir_or_logdir):
        seen["n"] += 1
        return real(outdir_or_logdir)

    monkeypatch.setattr(run_full, "check_launch_memory", wrapped)

    def fake(self, cmd, cwd, **_extra):
        return _body("probe-ok", model=PINNED), 0, ""

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    monkeypatch.setattr(cursor_llm, "SANDBOX", tmp_path)
    run_full.main()
    assert seen["n"] == 1
    written = json.loads((tmp_path / "results" / "probe-1.json").read_text(encoding="utf-8"))
    assert written["launch_memcheck"]["available_mb"] == 6144
    assert written["launch_memcheck"]["required_mb"] == 6144
    assert written["launch_memcheck"]["ok"] is True
    assert written["launch_memcheck"]["time_ist"].endswith("+05:30")
    log = (tmp_path / "results" / "launch-memcheck.log").read_text(encoding="utf-8")
    assert "available_mb=6144" in log
    assert "result=PASS" in log
    assert "+05:30" in log
