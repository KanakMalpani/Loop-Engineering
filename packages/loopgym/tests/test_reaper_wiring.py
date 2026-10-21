"""Tag reaper wiring. No real cursor-agent."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
BENCH = ROOT / "benchmarks" / "loopbench-validity"
if str(BENCH) not in sys.path:
    sys.path.insert(0, str(BENCH))

import cursor_llm


def _env(*entries: bytes) -> bytes:
    return b"\0".join(entries) + b"\0"


def _write_proc(root: Path, pid: int, environ: bytes | None, cmdline: bytes) -> None:
    proc_dir = root / str(pid)
    proc_dir.mkdir()
    if environ is not None:
        (proc_dir / "environ").write_bytes(environ)
    (proc_dir / "cmdline").write_bytes(cmdline)


def _empty_reap(tag: str) -> dict:
    return {
        "tag": tag,
        "killed": [],
        "leftover": 0,
        "leftover_tagged": 0,
        "leftover_worker_servers": 0,
    }


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(cursor_llm, "SANDBOX", tmp_path)
    monkeypatch.setattr(cursor_llm, "REAP_SETTLE_S", 0)
    return tmp_path


def test_reap_tag_kills_only_exact_tag(tmp_path, monkeypatch):
    monkeypatch.setattr(cursor_llm, "REAP_SETTLE_S", 0)
    tag = "abc123"
    needle = f"{cursor_llm.REAP_TAG_VAR}={tag}".encode()
    root = tmp_path / "proc"
    root.mkdir()
    _write_proc(
        root, 101, _env(b"HOME=/tmp", needle, b"A=b"), b"cursor-agent\0-p\0",
    )
    _write_proc(root, 102, _env(needle), b"node\0worker-server\0--port\0")
    decoy = _env(
        f"{cursor_llm.REAP_TAG_VAR}={tag}-other".encode(),
        f"WRAP={cursor_llm.REAP_TAG_VAR}={tag}".encode(),
        b"PATH=/bin",
    )
    _write_proc(root, 103, decoy, b"worker-server\0decoy\0")
    unreadable = root / "104"
    unreadable.mkdir()
    (unreadable / "cmdline").write_bytes(b"mystery\0")
    (root / "not-a-pid").mkdir()

    killed: list[tuple[int, int]] = []

    def fake_kill(pid: int, sig: int) -> None:
        killed.append((pid, sig))

    log_path = tmp_path / "logs" / "run.log"
    call_id = "norun-call0-attempt1"
    result = cursor_llm.reap_tag(
        tag, call_id, log_path, proc_root=root, kill=fake_kill,
    )
    assert sorted(pid for pid, _sig in killed) == [101, 102]
    assert {sig for _pid, sig in killed} == {signal.SIGKILL}
    assert sorted(result["killed"]) == [101, 102]
    assert result["tag"] == tag
    assert result["leftover_tagged"] == 2
    assert result["leftover_worker_servers"] == 1
    assert result["leftover"] == 1
    text = (log_path.parent / "reap.log").read_text(encoding="utf-8")
    kills = [line for line in text.splitlines() if " KILL " in line]
    assert len(kills) == 2
    for pid in (101, 102):
        assert any(
            f"pid={pid}" in line and f"tag={tag}" in line and f"call={call_id}" in line
            for line in kills
        )
    assert any("worker-server" in line and "pid=102" in line for line in kills)
    assert "pid=103" not in text
    assert "pid=104" not in text
    done = [line for line in text.splitlines() if " DONE " in line]
    assert len(done) == 1
    assert f"tag={tag}" in done[0]
    assert f"call={call_id}" in done[0]
    assert "reaped=2" in done[0]


def test_kill_errors_are_not_counted(tmp_path, monkeypatch):
    monkeypatch.setattr(cursor_llm, "REAP_SETTLE_S", 0)
    tag = "errtag"
    needle = f"{cursor_llm.REAP_TAG_VAR}={tag}".encode()
    root = tmp_path / "proc"
    root.mkdir()
    _write_proc(root, 201, _env(needle), b"one\0")
    _write_proc(root, 202, _env(needle), b"two\0")

    def fake_kill(pid: int, sig: int) -> None:
        assert sig == signal.SIGKILL
        if pid == 201:
            raise PermissionError(pid)
        raise ProcessLookupError(pid)

    log_path = tmp_path / "run.log"
    result = cursor_llm.reap_tag(tag, "call-x", log_path, proc_root=root, kill=fake_kill)
    assert result["killed"] == []
    text = (tmp_path / "reap.log").read_text(encoding="utf-8")
    assert " KILL " not in text
    assert "reaped=0" in text
    assert result["leftover_tagged"] == 2


def test_reap_uses_module_kill_when_argument_omitted(tmp_path, monkeypatch):
    monkeypatch.setattr(cursor_llm, "REAP_SETTLE_S", 0)
    seen: list[int] = []

    def fake_kill(pid: int, sig: int) -> None:
        assert sig == signal.SIGKILL
        seen.append(pid)

    monkeypatch.setattr(cursor_llm, "_kill", fake_kill)
    tag = "modkill"
    root = tmp_path / "proc"
    root.mkdir()
    needle = f"{cursor_llm.REAP_TAG_VAR}={tag}".encode()
    _write_proc(root, 301, _env(needle), b"cursor-agent\0")
    result = cursor_llm.reap_tag(tag, "c", tmp_path / "run.log", proc_root=root)
    assert seen == [301]
    assert result["killed"] == [301]


def test_timeout_reaps_and_records(sandbox, monkeypatch):
    seen: list[dict] = []
    groups: list[tuple[int, int]] = []

    def fake_reap(tag, call_id, log_path, proc_root=Path("/proc"), kill=None):
        seen.append({"tag": tag, "call_id": call_id, "log_path": log_path})
        return {
            "tag": tag,
            "killed": [5],
            "leftover": 2,
            "leftover_tagged": 4,
            "leftover_worker_servers": 2,
        }

    class Proc:
        def __init__(self, args, kwargs):
            self.args = args
            self.pid = 424242
            self.returncode = None
            err = kwargs.get("stderr")
            if err is not None:
                err.write(b"timed-err")

        def wait(self, timeout=None):
            if timeout is not None:
                raise subprocess.TimeoutExpired(self.args, timeout)
            self.returncode = -9
            return -9

    monkeypatch.setattr(cursor_llm, "reap_tag", fake_reap)
    monkeypatch.setattr(cursor_llm.subprocess, "Popen", lambda args, **kwargs: Proc(args, kwargs))
    monkeypatch.setattr(
        cursor_llm.os, "killpg", lambda pid, sig: groups.append((pid, sig)),
    )
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=sandbox / "run.log", run_id="rid")
    with pytest.raises(cursor_llm.InfraError):
        llm.complete("prompt", role="role")
    assert [item["call_id"] for item in seen] == [
        "rid-call0-attempt1",
        "rid-call0-attempt2",
        "rid-call0-attempt3",
    ]
    assert groups == [(424242, signal.SIGKILL)] * 3
    call = llm.calls[0]
    assert call["reap_kills"] == 3
    assert call["leftover_worker_servers"] == 6
    assert call["reap_log"] == str(sandbox / "reap.log")
    assert len(call["attempts"]) == cursor_llm.INFRA_RETRIES + 1
    for attempt, item in zip(call["attempts"], seen, strict=True):
        assert attempt["outcome"] == "timeout"
        assert attempt["reap_tag"] == item["tag"]
        assert attempt["reap_tag"].startswith("lbreap-")
        assert attempt["reap_kills"] == 1
        assert attempt["leftover_worker_servers"] == 2
        assert attempt["leftover_tagged"] == 4
        path = Path(attempt["stderr_path"])
        assert path.read_text(encoding="utf-8") == "timed-err"
    start = (sandbox / "reap.log").read_text(encoding="utf-8")
    assert start.count(" START ") == 3


def test_ok_path_records_reap_fields(sandbox, monkeypatch):
    body = json.dumps({"result": "hello", "usage": {"inputTokens": 3, "outputTokens": 4}})
    seen: list[dict] = []

    def fake_reap(tag, call_id, log_path, proc_root=Path("/proc"), kill=None):
        seen.append({"tag": tag, "call_id": call_id})
        return {
            "tag": tag,
            "killed": [11, 12],
            "leftover": 0,
            "leftover_tagged": 0,
            "leftover_worker_servers": 0,
        }

    class Proc:
        def __init__(self, args, kwargs):
            self.pid = 50
            self.returncode = 0
            kwargs["stdout"].write(body.encode())

        def wait(self, timeout=None):
            self.returncode = 0
            return 0

    monkeypatch.setattr(cursor_llm, "reap_tag", fake_reap)
    monkeypatch.setattr(cursor_llm.subprocess, "Popen", lambda args, **kwargs: Proc(args, kwargs))
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=sandbox / "run.log", run_id="run")
    assert llm.complete("prompt", role="role") == "hello"
    assert seen[0]["call_id"] == "run-call0-attempt1"
    call = llm.calls[0]
    attempt = call["attempts"][0]
    assert attempt["outcome"] == "ok"
    assert attempt["reap_tag"] == seen[0]["tag"]
    assert attempt["reap_kills"] == 2
    assert attempt["leftover_worker_servers"] == 0
    assert attempt["leftover_tagged"] == 0
    assert call["reap_kills"] == 2
    assert call["leftover_worker_servers"] == 0
    assert call["reap_log"] == str(sandbox / "reap.log")
    assert " START " in (sandbox / "reap.log").read_text(encoding="utf-8")


def test_run_once_uses_files_not_pipes(sandbox, monkeypatch):
    captured: dict = {}
    before = os.environ.get(cursor_llm.REAP_TAG_VAR)

    def fake_reap(tag, call_id, log_path, proc_root=Path("/proc"), kill=None):
        captured["reap_tag"] = tag
        captured["call_id"] = call_id
        return _empty_reap(tag)

    class Proc:
        def __init__(self):
            self.pid = 7
            self.returncode = 0

        def wait(self, timeout=None):
            self.returncode = 0
            return 0

    def fake_popen(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        kwargs["stdout"].write(b"{}\n")
        return Proc()

    monkeypatch.setattr(cursor_llm, "reap_tag", fake_reap)
    monkeypatch.setattr(cursor_llm.subprocess, "Popen", fake_popen)
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=sandbox / "run.log", run_id="pipe")
    stderr_path = sandbox / "stderr" / "pipe.stderr"
    call_id = "pipe-call0-attempt1"
    llm._run_once(
        [cursor_llm.CURSOR_BIN, "-p"], sandbox, stderr_path=stderr_path, call_id=call_id,
    )
    kwargs = captured["kwargs"]
    args = captured["args"]
    assert kwargs["stdout"] != subprocess.PIPE
    assert kwargs["stderr"] != subprocess.PIPE
    assert hasattr(kwargs["stdout"], "fileno")
    assert hasattr(kwargs["stderr"], "fileno")
    assert kwargs["stdin"] == subprocess.DEVNULL
    assert kwargs["start_new_session"] is True
    assert kwargs["env"] is not os.environ
    tag = kwargs["env"][cursor_llm.REAP_TAG_VAR]
    assert tag.startswith("lbreap-")
    assert len(tag) == len("lbreap-") + 32
    assert captured["reap_tag"] == tag
    assert captured["call_id"] == call_id
    assert os.environ.get(cursor_llm.REAP_TAG_VAR) == before
    assert cursor_llm.ISOLATE is True
    assert args[0] == "bwrap"
    seq = ["--setenv", cursor_llm.REAP_TAG_VAR, tag]
    assert any(args[i:i + 3] == seq for i in range(len(args) - 2))
    assert Path(kwargs["stderr"].name) == stderr_path
    assert Path(kwargs["stdout"].name).parent == sandbox


def test_reap_on_launch_exception(sandbox, monkeypatch):
    seen: list[str] = []

    def fake_reap(tag, call_id, log_path, proc_root=Path("/proc"), kill=None):
        seen.append(call_id)
        return _empty_reap(tag)

    def boom(*args, **kwargs):
        raise OSError("launch failed")

    monkeypatch.setattr(cursor_llm, "reap_tag", fake_reap)
    monkeypatch.setattr(cursor_llm.subprocess, "Popen", boom)
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=sandbox / "run.log", run_id="ex")
    with pytest.raises(OSError, match="launch failed"):
        llm.complete("prompt", role="role")
    assert seen == ["ex-call0-attempt1"]


def test_source_does_not_read_reaper_env():
    text = Path(cursor_llm.__file__).read_text(encoding="utf-8")
    assert 'environ.get("CURSOR_REAP' not in text
    assert "environ.get('CURSOR_REAP" not in text
