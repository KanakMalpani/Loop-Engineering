"""LLMClient shim: routes LoopGym prompts to cursor-agent in an isolated bwrap sandbox.

Validity caveat: cursor-agent is an agent wrapper, not a raw model. Each call runs in ask mode
with tmpfs mounts for /workspace and /tmp plus an ephemeral ~/.cursor, so the agent cannot read
the repo, hidden tests, reference fixes, evaluator temp dirs, or other local agent state.
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

# Pinned (DEVIATION-3): no CURSOR_AGENT_BIN override. A set variable aborts via assert_no_unpinned_env.
CURSOR_BIN = str(Path.home() / ".local/bin/cursor-agent")
SANDBOX = Path(os.environ.get("CURSOR_LLM_SANDBOX", "/workspace/cursor-llm-sandbox"))
# Pinned (DEVIATION-3): no env override, no fallback to the cursor-agent default model.
DEFAULT_MODEL = "grok-4.7-high"
PINNED_CURSOR_AGENT_VERSION = "2026.10.19-6bbf2c4"
ISOLATE = True
# Extra attempts after the first. Infra failures only; model content is never retried.
INFRA_RETRIES = 2
_LOG_LOCK = threading.Lock()
# Always-on tag reaper. The tag is generated per attempt; nothing reads an override.
REAP_TAG_VAR = "CURSOR_REAP_TAG"
REAP_SETTLE_S = 1.0
_kill = os.kill
_PINNED_ENV = (
    "CURSOR_LLM_INFRA_RETRIES",
    "CURSOR_LLM_ISOLATE",
    "CURSOR_LLM_MODEL",
    "CURSOR_AGENT_BIN",
)


class InfraError(RuntimeError):
    """No model result after the infra retries are exhausted."""


def assert_no_unpinned_env() -> None:
    """Pinned (DEVIATION-3): a stale override must not be silently ignored."""
    found = [name for name in _PINNED_ENV if name in os.environ]
    if found:
        listed = ", ".join(found)
        raise RuntimeError(f"pinned cursor_llm settings reject env overrides: {listed}")


def require_pinned_model(model: object) -> None:
    """Probes refuse any model other than the pinned default, before any model call."""
    if model != DEFAULT_MODEL:
        raise SystemExit(f"probe requires pinned model {DEFAULT_MODEL}")


def calls_model_check(calls: list | None) -> dict:
    """Flag call records whose model_requested is not the pinned model."""
    violations = []
    for index, call in enumerate(calls or []):
        requested = call.get("model_requested") if isinstance(call, dict) else None
        if requested != DEFAULT_MODEL:
            violations.append({"call": index, "model_requested": requested})
    return {"pinned": DEFAULT_MODEL, "valid": not violations, "violations": violations}


def launch_identity() -> dict:
    """Resolved cursor-agent binary and the stripped stdout of ``--version``."""
    result = subprocess.run(
        [CURSOR_BIN, "--version"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    stdout = result.stdout if isinstance(result.stdout, str) else ""
    return {
        "cursor_agent_bin": CURSOR_BIN,
        "cursor_agent_resolved": os.path.realpath(CURSOR_BIN),
        "cursor_agent_version": stdout.strip(),
    }


def assert_launch_identity() -> dict:
    """Return launch_identity(), or abort when the installed version is not pinned."""
    identity = launch_identity()
    version = identity["cursor_agent_version"]
    if version != PINNED_CURSOR_AGENT_VERSION:
        raise RuntimeError(
            f"cursor-agent version {version!r} != pinned {PINNED_CURSOR_AGENT_VERSION}"
        )
    return identity


def _iso_utc() -> str:
    return datetime.now(UTC).isoformat()


def _reap_log_file(log_path: Path | str | None) -> Path:
    """Sibling ``reap.log`` of a run log.

    Callers with no run log pass the already-resolved host file
    (``<host-stdio>/reap.log``). ``None`` is rejected so the log cannot land
    under SANDBOX, which bwrap binds into the agent.
    """
    if log_path is None:
        raise ValueError("reap log path must be resolved by the caller")
    return Path(log_path).parent / "reap.log"


def _append_reap_line(path: Path, line: str) -> None:
    text = line if line.endswith("\n") else f"{line}\n"
    with _LOG_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(text)


def _read_text(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8", errors="replace")
    except OSError:
        return ""


_BIND_FLAGS = ("--bind", "--ro-bind", "--dev-bind")


def _bind_paths(run_cmd: list[str]) -> list[Path]:
    """Src and dest of bwrap bind flags. The root dev-bind ("/") is excluded."""
    paths: list[Path] = []
    index = 0
    while index < len(run_cmd):
        if run_cmd[index] in _BIND_FLAGS and index + 2 < len(run_cmd):
            for raw in (run_cmd[index + 1], run_cmd[index + 2]):
                if raw != "/":
                    paths.append(Path(raw))
            index += 3
            continue
        index += 1
    return paths


def _path_is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _assert_stdio_unbound(
    stdout_path: Path,
    stderr_path: Path,
    work: Path,
    run_cmd: list[str],
) -> None:
    """Refuse a call whose stdout or stderr is visible inside the sandbox."""
    banned = [work, SANDBOX, *_bind_paths(run_cmd)]
    for label, path in (("stdout", stdout_path), ("stderr", stderr_path)):
        for root in banned:
            if _path_is_under(path, root):
                raise RuntimeError(f"{label} path {path} is under {root}")


def _environ_has_tag(proc_dir: Path, needle: bytes) -> bool:
    """True only for an exact env entry. Unreadable or vanished processes are not a match."""
    try:
        data = (proc_dir / "environ").read_bytes()
    except OSError:
        return False
    return needle in data.split(b"\0")


def _read_cmdline(proc_dir: Path) -> str:
    try:
        raw = (proc_dir / "cmdline").read_bytes()
    except OSError:
        return ""
    text = raw.replace(b"\0", b" ").decode("utf-8", errors="replace")
    return text.replace("\n", " ").replace("\r", " ")


def reap_tag(
    tag: str,
    call_id: str,
    log_path: Path | str | None,
    proc_root: Path = Path("/proc"),
    kill=None,
) -> dict:
    """SIGKILL processes whose environ has this exact tag. Untagged pids are never touched."""
    killer = _kill if kill is None else kill
    time.sleep(REAP_SETTLE_S)
    needle = f"{REAP_TAG_VAR}={tag}".encode()
    log_file = _reap_log_file(log_path)
    killed: list[int] = []
    try:
        proc_dirs = list(proc_root.iterdir())
    except OSError:
        proc_dirs = []
    for proc_dir in proc_dirs:
        if not proc_dir.name.isdigit():
            continue
        pid = int(proc_dir.name)
        if pid == os.getpid():
            continue
        if not _environ_has_tag(proc_dir, needle):
            continue
        cmdline = _read_cmdline(proc_dir)
        # Re-read immediately before the kill so a recycled pid is not signalled.
        if not _environ_has_tag(proc_dir, needle):
            continue
        try:
            killer(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            continue
        killed.append(pid)
        _append_reap_line(
            log_file,
            (
                f"{_iso_utc()} KILL pid={pid} tag={tag} call={call_id} "
                f"cmd={cmdline[:120]} reason=reap"
            ),
        )
    _append_reap_line(
        log_file,
        f"{_iso_utc()} DONE tag={tag} call={call_id} reaped={len(killed)}",
    )
    leftover_tagged = 0
    leftover_worker_servers = 0
    try:
        proc_dirs = list(proc_root.iterdir())
    except OSError:
        proc_dirs = []
    for proc_dir in proc_dirs:
        if not proc_dir.name.isdigit():
            continue
        pid = int(proc_dir.name)
        if pid == os.getpid():
            continue
        if not _environ_has_tag(proc_dir, needle):
            continue
        leftover_tagged += 1
        if "worker-server" in _read_cmdline(proc_dir):
            leftover_worker_servers += 1
    return {
        "tag": tag,
        "killed": killed,
        "leftover": leftover_worker_servers,
        "leftover_tagged": leftover_tagged,
        "leftover_worker_servers": leftover_worker_servers,
    }


def _coerce_stderr(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, str):
        return value
    return str(value)


def _unpack_run(result: tuple) -> tuple[str, int, str | None]:
    """2-tuple (stdout, code) leaves stderr missing; a 3-tuple carries it."""
    if not isinstance(result, tuple) or len(result) < 2:
        raise TypeError("cursor-agent result must be a 2- or 3-tuple")
    raw_out = result[0]
    stdout = raw_out if isinstance(raw_out, str) else ("" if raw_out is None else str(raw_out))
    if len(result) < 3:
        return stdout, int(result[1]), None
    return stdout, int(result[1]), _coerce_stderr(result[2])


def _model_reported(data: dict | None) -> str | None:
    if not isinstance(data, dict):
        return None
    direct = data.get("model")
    if isinstance(direct, str) and direct.strip():
        return direct
    info = data.get("modelInfo")
    if isinstance(info, dict):
        for key in ("model", "modelName"):
            value = info.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return None


def _classify_attempt(
    stdout: str, returncode: int,
) -> tuple[str, dict | None, BaseException | None]:
    """Classify one cursor-agent process. 'ok' is a model reply and is never retried."""
    text = (stdout or "").strip()
    data: dict | None = None
    parse_error: json.JSONDecodeError | None = None
    if text:
        try:
            parsed = json.loads(text.splitlines()[-1])
        except json.JSONDecodeError as exc:
            parse_error = exc
        else:
            if isinstance(parsed, dict):
                data = parsed
    if data is not None and data.get("is_error"):
        return "process_error", None, RuntimeError(f"cursor-agent error: {data}")
    if data is not None:
        return "ok", data, None
    if returncode != 0:
        if parse_error is not None:
            err: BaseException = parse_error
        elif not text:
            err = RuntimeError(f"cursor-agent exited {returncode} with no output")
        else:
            err = RuntimeError(f"cursor-agent exited {returncode} with no JSON")
        return "process_error", None, err
    if not text:
        return "no_output", None, RuntimeError("cursor-agent returned no output")
    if parse_error is not None:
        return "bad_json", None, parse_error
    return "bad_json", None, RuntimeError("cursor-agent returned no JSON object")


class CursorAgentLLM:
    def __init__(
        self,
        model: str | None = None,
        timeout: int = 180,
        *,
        log_path: Path | str | None = None,
        run_id: str | None = None,
    ) -> None:
        assert_no_unpinned_env()
        self.model = model if model is not None else DEFAULT_MODEL
        if not isinstance(self.model, str) or not self.model.strip():
            raise ValueError("model must be a non-empty string")
        self.timeout = timeout
        self.tokens_used = 0
        self.calls: list[dict] = []
        self.infra_failures = 0
        self.log_path = Path(log_path) if log_path is not None else None
        self.run_id = run_id
        self._last_reap: dict | None = None
        self._host_stdio_tmp: Path | None = None
        SANDBOX.mkdir(parents=True, exist_ok=True)

    def _prepare_workspace(self, role: str) -> Path:
        """Per-call workspace. The role is the instruction layer, not the user prompt."""
        SANDBOX.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="call-", dir=SANDBOX))
        text = f"{role.rstrip()}\n"
        (work / "AGENTS.md").write_text(text, encoding="utf-8")
        rules = work / ".cursor" / "rules"
        rules.mkdir(parents=True)
        (rules / "role.mdc").write_text(
            f"---\nalwaysApply: true\n---\n\n{text}",
            encoding="utf-8",
        )
        return work

    def _host_stdio_dir(self) -> Path:
        """Directory for stdout/stderr files that bwrap must not see.

        With a log path this is ``<outdir>/stdio``. Otherwise it is a per-instance
        directory in the default host temp dir (never ``work`` or ``SANDBOX``).
        """
        if self.log_path is not None:
            directory = self.log_path.parent / "stdio"
            directory.mkdir(parents=True, exist_ok=True)
            return directory
        if self._host_stdio_tmp is None:
            self._host_stdio_tmp = Path(tempfile.mkdtemp(prefix="cursor-llm-stdio-"))
        return self._host_stdio_tmp

    def _reap_log_path(self) -> Path:
        """``<outdir>/reap.log`` when logging, else a host-only file in the stdio dir."""
        if self.log_path is None:
            return self._host_stdio_dir() / "reap.log"
        return _reap_log_file(self.log_path)

    def _run_once(
        self,
        cmd: list[str],
        cwd: Path | None = None,
        stderr_path: Path | str | None = None,
        call_id: str | None = None,
    ) -> tuple[str, int, str]:
        """One sandboxed cursor-agent process. Fresh temp home. Raises TimeoutExpired on timeout."""
        work = Path(cwd) if cwd is not None else SANDBOX
        tag = f"lbreap-{uuid4().hex}"
        if call_id is None:
            call_id = f"{self.run_id or 'norun'}-call{len(self.calls)}-attempt1"
        env = os.environ.copy()
        env[REAP_TAG_VAR] = tag
        run_cmd = list(cmd)
        tmp_home: Path | None = None
        stdout_path: Path | None = None
        stderr_target = Path(stderr_path) if stderr_path is not None else None
        stdout_handle = None
        stderr_handle = None
        proc: subprocess.Popen | None = None
        timed_out: subprocess.TimeoutExpired | None = None
        stdout_text = ""
        stderr_text = ""
        reap_log = self._reap_log_path()
        try:
            _append_reap_line(
                reap_log,
                f"{_iso_utc()} START tag={tag} call={call_id}",
            )
            if ISOLATE:
                home = str(Path.home())
                tmp_home = Path(tempfile.mkdtemp(prefix=".home-", dir=SANDBOX))
                cursor_dir = tmp_home / ".cursor"
                cursor_dir.mkdir(parents=True, exist_ok=True)
                cfg = Path(home) / ".cursor" / "cli-config.json"
                if cfg.exists():
                    shutil.copy2(cfg, cursor_dir / "cli-config.json")
                bind = ["--bind", str(SANDBOX), str(SANDBOX)]
                if work.resolve() != SANDBOX.resolve():
                    bind += ["--bind", str(work), str(work)]
                run_cmd = [
                    "bwrap", "--dev-bind", "/", "/", "--tmpfs", "/workspace", "--tmpfs", "/tmp",
                    "--tmpfs", home, "--ro-bind", f"{home}/.local/bin", f"{home}/.local/bin",
                    "--ro-bind", f"{home}/.local/share/cursor-agent",
                    f"{home}/.local/share/cursor-agent",
                    "--bind", f"{home}/.config/cursor", f"{home}/.config/cursor",
                    "--bind", str(cursor_dir), f"{home}/.cursor",
                    # Host public-plugin cache only; without it cursor-agent downloads plugins and hangs.
                    *(
                        ["--ro-bind", f"{home}/.cursor/plugins", f"{home}/.cursor/plugins"]
                        if (Path(home) / ".cursor" / "plugins").is_dir()
                        else []
                    ),
                    *bind, "--chdir", str(work),
                    "--setenv", "HOME", home,
                    "--setenv", REAP_TAG_VAR, tag,
                    "--die-with-parent",
                ] + list(cmd)
            stdio_dir = self._host_stdio_dir()
            fd, stdout_name = tempfile.mkstemp(prefix="stdout-", dir=stdio_dir)
            os.close(fd)
            stdout_path = Path(stdout_name)
            if stderr_target is None:
                fd, stderr_name = tempfile.mkstemp(prefix="stderr-", dir=stdio_dir)
                os.close(fd)
                stderr_target = Path(stderr_name)
            else:
                stderr_target.parent.mkdir(parents=True, exist_ok=True)
            _assert_stdio_unbound(stdout_path, stderr_target, work, run_cmd)
            # Files, not pipes: a lingering worker-server kept the stderr pipe open and hung callers.
            stdout_handle = stdout_path.open("wb", buffering=0)
            stderr_handle = stderr_target.open("wb", buffering=0)
            proc = subprocess.Popen(
                run_cmd,
                cwd=work,
                stdout=stdout_handle,
                stderr=stderr_handle,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
                env=env,
            )
            try:
                proc.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired as exc:
                try:
                    pgid = os.getpgid(proc.pid)
                except OSError:
                    pgid = proc.pid
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                _append_reap_line(
                    reap_log,
                    (
                        f"{_iso_utc()} KILLPG pid={proc.pid} pgid={pgid} "
                        f"tag={tag} call={call_id} reason=timeout"
                    ),
                )
                proc.wait()
                timed_out = exc
        finally:
            if stdout_handle is not None:
                stdout_handle.close()
            if stderr_handle is not None:
                stderr_handle.close()
            if stdout_path is not None:
                stdout_text = _read_text(stdout_path)
                try:
                    stdout_path.unlink()
                except OSError:
                    pass
            if stderr_target is not None:
                stderr_text = _read_text(stderr_target)
            self._last_reap = reap_tag(tag, call_id, reap_log)
            if tmp_home is not None:
                shutil.rmtree(tmp_home, ignore_errors=True)
        if timed_out is not None:
            timed_out.stderr = stderr_text
            raise timed_out
        code = None if proc is None else proc.returncode
        return stdout_text or "", 1 if code is None else code, stderr_text or ""

    def _log_attempt(
        self,
        call_index: int,
        n: int,
        outcome: str,
        seconds: float,
        returncode: int | None,
    ) -> None:
        if self.log_path is None:
            return
        ident = self.run_id if self.run_id else "-"
        line = (
            f"{datetime.now(UTC).isoformat()} {ident} call={call_index} "
            f"attempt={n} outcome={outcome} seconds={seconds} rc={returncode}\n"
        )
        with _LOG_LOCK:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(line)

    def _stderr_file(self, call_index: int, n: int) -> Path:
        safe_run_id = self.run_id.replace("/", "_") if self.run_id else "norun"
        name = f"{safe_run_id}-call{call_index}-attempt{n}.stderr"
        # log_path set: <outdir>/stderr. No log: inside the per-instance host stdio dir.
        if self.log_path is None:
            directory = self._host_stdio_dir() / "stderr"
        else:
            directory = self.log_path.parent / "stderr"
        return directory / name

    def _store_stderr(self, call_index: int, n: int, stderr: str | None) -> dict:
        path = self._stderr_file(call_index, n)
        path.parent.mkdir(parents=True, exist_ok=True)
        text = "" if stderr is None else stderr
        path.write_text(text, encoding="utf-8")
        record = {"stderr_path": str(path), "stderr_bytes": len(text.encode("utf-8"))}
        if stderr is None:
            record["stderr_missing"] = True
        return record

    def _note_attempt(
        self,
        call_index: int,
        n: int,
        seconds: float,
        outcome: str,
        stderr: str | None,
        returncode: int | None,
        attempts: list[dict],
    ) -> None:
        rc_nonzero = returncode not in (0, None)
        attempts.append({
            "n": n,
            "seconds": seconds,
            "outcome": outcome,
            "returncode": returncode,
            "rc_nonzero": rc_nonzero,
            "clean": outcome == "ok" and returncode == 0,
            **self._store_stderr(call_index, n, stderr),
            **self._reap_fields(),
        })
        self._log_attempt(call_index, n, outcome, seconds, returncode)

    def _reap_fields(self) -> dict:
        info = self._last_reap if isinstance(self._last_reap, dict) else {}
        killed = info.get("killed") or []
        if not isinstance(killed, list):
            killed = []
        return {
            "reap_tag": info.get("tag"),
            "reap_kills": len(killed),
            "leftover_worker_servers": int(info.get("leftover_worker_servers") or 0),
            "leftover_tagged": int(info.get("leftover_tagged") or 0),
        }

    def _append_call(
        self,
        role: str,
        attempts: list[dict],
        usage: dict | None,
        reply: str,
        temperature: float | None,
        model_reported: str | None,
    ) -> None:
        final = attempts[-1] if attempts else {}
        self.calls.append({
            "role": role,
            "reply": reply,
            "seconds": round(sum(a["seconds"] for a in attempts), 1),
            "usage": usage,
            "isolated": ISOLATE,
            "attempts": attempts,
            "returncode": final.get("returncode"),
            "rc_nonzero": any(bool(a.get("rc_nonzero")) for a in attempts),
            "temperature_requested": temperature,
            "temperature_applied": False,
            "model_requested": self.model,
            "model_reported": model_reported,
            "reap_kills": sum(int(a.get("reap_kills") or 0) for a in attempts),
            "leftover_worker_servers": sum(
                int(a.get("leftover_worker_servers") or 0) for a in attempts
            ),
            "reap_log": str(self._reap_log_path()),
        })

    def complete(
        self,
        prompt: str,
        role: str = "default",
        temperature: float | None = None,
    ) -> str:
        call_index = len(self.calls)
        work = self._prepare_workspace(role)
        cmd = [CURSOR_BIN, "-p", "--trust", "--mode", "ask", "--output-format", "json"]
        cmd += ["--model", self.model]
        cmd.append(prompt)
        # No result: timeout, no output, unparsable output, or process error. Retry those.
        # A parsed model reply with content is final, including a non-zero exit that still
        # returned JSON without is_error. Temperature cannot be passed to cursor-agent.
        attempts: list[dict] = []
        last_error: BaseException | None = None
        try:
            for n in range(1, INFRA_RETRIES + 2):
                t0 = time.monotonic()
                stderr_path = self._stderr_file(call_index, n)
                call_id = f"{self.run_id or 'norun'}-call{call_index}-attempt{n}"
                self._last_reap = None
                try:
                    raw = self._run_once(
                        cmd, work, stderr_path=stderr_path, call_id=call_id,
                    )
                except subprocess.TimeoutExpired as exc:
                    seconds = round(time.monotonic() - t0, 1)
                    stderr = _coerce_stderr(getattr(exc, "stderr", None))
                    self._note_attempt(
                        call_index, n, seconds, "timeout", stderr, None, attempts,
                    )
                    self.infra_failures += 1
                    last_error = exc
                    continue
                seconds = round(time.monotonic() - t0, 1)
                stdout, returncode, stderr = _unpack_run(raw)
                outcome, data, err = _classify_attempt(stdout, returncode)
                if outcome != "ok" or data is None:
                    self._note_attempt(
                        call_index, n, seconds, outcome, stderr, returncode, attempts,
                    )
                    self.infra_failures += 1
                    last_error = err or RuntimeError(f"cursor-agent infra failure ({outcome})")
                    continue
                u = data.get("usage") or {}
                self.tokens_used += int(u.get("inputTokens", 0)) + int(u.get("outputTokens", 0))
                reply = data.get("result", "")
                if reply is None:
                    reply = ""
                elif not isinstance(reply, str):
                    reply = str(reply)
                self._note_attempt(
                    call_index, n, seconds, "ok", stderr, returncode, attempts,
                )
                self._append_call(
                    role, attempts, u, reply, temperature, _model_reported(data),
                )
                return reply
            if last_error is None:
                last_error = RuntimeError("cursor-agent infra retry produced no result")
            self._append_call(role, attempts, None, "", temperature, None)
            raise InfraError(str(last_error)) from last_error
        finally:
            shutil.rmtree(work, ignore_errors=True)
