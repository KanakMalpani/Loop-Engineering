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
    # Logs stay beside tmp_path; the sandbox directory is what bwrap binds.
    box = tmp_path / "sandbox"
    box.mkdir()
    monkeypatch.setattr(cursor_llm, "SANDBOX", box)
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
    assert all("reason=reap" in line for line in kills)
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
    work = cursor_llm.SANDBOX / "work"
    work.mkdir()
    llm._run_once(
        [cursor_llm.CURSOR_BIN, "-p"], work, stderr_path=stderr_path, call_id=call_id,
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
    assert Path(kwargs["stdout"].name).parent == sandbox / "stdio"


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


def test_unlogged_instances_get_distinct_host_stderr_dirs(sandbox):
    first = cursor_llm.CursorAgentLLM(timeout=5, log_path=None, run_id="same")
    second = cursor_llm.CursorAgentLLM(timeout=5, log_path=None, run_id="same")
    path_a = first._stderr_file(0, 1)
    path_b = second._stderr_file(0, 1)
    assert path_a.name == path_b.name == "same-call0-attempt1.stderr"
    assert path_a.parent != path_b.parent
    assert path_a.parent == first._host_stdio_dir() / "stderr"
    assert path_b.parent == second._host_stdio_dir() / "stderr"
    for path in (path_a, path_b):
        assert not _is_under(path, cursor_llm.SANDBOX)


def test_reap_log_without_log_path_is_host_only(sandbox, monkeypatch):
    seen: list[object] = []
    works: list[Path] = []
    prepare = cursor_llm.CursorAgentLLM._prepare_workspace

    def fake_reap(tag, call_id, log_path, proc_root=Path("/proc"), kill=None):
        seen.append(log_path)
        return _empty_reap(tag)

    def tracking_prepare(self, role):
        work = prepare(self, role)
        works.append(work)
        return work

    class Proc:
        def __init__(self, args, kwargs):
            self.pid = 9
            self.returncode = 0
            body = '{"result":"ok","usage":{"inputTokens":1,"outputTokens":1}}\n'
            kwargs["stdout"].write(body.encode())

        def wait(self, timeout=None):
            self.returncode = 0
            return 0

    monkeypatch.setattr(cursor_llm, "reap_tag", fake_reap)
    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_prepare_workspace", tracking_prepare)
    monkeypatch.setattr(cursor_llm.subprocess, "Popen", lambda args, **kwargs: Proc(args, kwargs))
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=None, run_id="host")
    assert llm.complete("prompt", role="role") == "ok"
    reap_log = Path(llm.calls[0]["reap_log"])
    assert reap_log == llm._host_stdio_dir() / "reap.log"
    assert seen == [reap_log]
    assert " START " in reap_log.read_text(encoding="utf-8")
    assert not _is_under(reap_log, cursor_llm.SANDBOX)
    assert works
    for work in works:
        assert not _is_under(reap_log, work)
    assert not (cursor_llm.SANDBOX / "reap.log").exists()


def test_source_does_not_read_reaper_env():
    text = Path(cursor_llm.__file__).read_text(encoding="utf-8")
    assert 'environ.get("CURSOR_REAP' not in text
    assert "environ.get('CURSOR_REAP" not in text


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _bwrap_bind_paths(args: list[str]) -> list[Path]:
    flags = {"--bind", "--ro-bind", "--dev-bind"}
    found: list[Path] = []
    index = 0
    while index < len(args):
        if args[index] in flags and index + 2 < len(args):
            for raw in (args[index + 1], args[index + 2]):
                if raw != "/":
                    found.append(Path(raw))
            index += 3
            continue
        index += 1
    return found


class _HandleProc:
    def __init__(self, args, kwargs):
        self.args = args
        self.pid = 5150
        self.returncode = None
        self.kwargs = kwargs

    def wait(self, timeout=None):
        self.returncode = 0
        return 0


@pytest.mark.parametrize("logged", [True, False])
def test_stdio_handles_avoid_bound_paths(tmp_path, monkeypatch, logged):
    box = tmp_path / "sandbox"
    box.mkdir()
    monkeypatch.setattr(cursor_llm, "SANDBOX", box)
    monkeypatch.setattr(cursor_llm, "REAP_SETTLE_S", 0)
    captured: dict = {}

    def fake_reap(tag, call_id, log_path, proc_root=Path("/proc"), kill=None):
        return _empty_reap(tag)

    def fake_popen(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        kwargs["stdout"].write(b"{}\n")
        return _HandleProc(args, kwargs)

    monkeypatch.setattr(cursor_llm, "reap_tag", fake_reap)
    monkeypatch.setattr(cursor_llm.subprocess, "Popen", fake_popen)
    log_path = tmp_path / "out" / "run.log" if logged else None
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=log_path, run_id="stdio")
    assert cursor_llm.ISOLATE is True
    work = llm._prepare_workspace("role")
    stderr_path = llm._stderr_file(0, 1)
    llm._run_once(
        [cursor_llm.CURSOR_BIN, "-p"],
        work,
        stderr_path=stderr_path,
        call_id="stdio-call0-attempt1",
    )
    kwargs = captured["kwargs"]
    args = captured["args"]
    assert args[0] == "bwrap"
    stdout_path = Path(kwargs["stdout"].name)
    stderr_file = Path(kwargs["stderr"].name)
    banned = [work, box, *_bwrap_bind_paths(args)]
    for path in (stdout_path, stderr_file):
        for root in banned:
            assert not _is_under(path, root), f"{path} is under {root}"


def test_timeout_killpg_logged(tmp_path, monkeypatch):
    box = tmp_path / "sandbox"
    box.mkdir()
    monkeypatch.setattr(cursor_llm, "SANDBOX", box)
    monkeypatch.setattr(cursor_llm, "REAP_SETTLE_S", 0)
    captured: dict = {}

    class Proc:
        def __init__(self, args, kwargs):
            self.args = args
            self.pid = 5150
            self.returncode = None
            captured["env"] = kwargs.get("env")

        def wait(self, timeout=None):
            if timeout is not None:
                raise subprocess.TimeoutExpired(self.args, timeout)
            self.returncode = -9
            return -9

    monkeypatch.setattr(cursor_llm, "reap_tag", lambda *args, **kwargs: _empty_reap(args[0]))
    monkeypatch.setattr(cursor_llm.subprocess, "Popen", lambda args, **kwargs: Proc(args, kwargs))
    monkeypatch.setattr(cursor_llm.os, "killpg", lambda pid, sig: None)
    monkeypatch.setattr(cursor_llm.os, "getpgid", lambda pid: 9090)
    log_path = tmp_path / "out" / "run.log"
    llm = cursor_llm.CursorAgentLLM(timeout=5, log_path=log_path, run_id="rid")
    work = box / "work"
    work.mkdir()
    with pytest.raises(subprocess.TimeoutExpired):
        llm._run_once(
            [cursor_llm.CURSOR_BIN, "-p"], work, call_id="rid-call0-attempt1",
        )
    text = (log_path.parent / "reap.log").read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if " KILLPG " in line]
    assert len(lines) == 1
    line = lines[0]
    tag = captured["env"][cursor_llm.REAP_TAG_VAR]
    assert "pid=5150" in line
    assert "pgid=9090" in line
    assert f"tag={tag}" in line
    assert "call=rid-call0-attempt1" in line
    assert "reason=timeout" in line
