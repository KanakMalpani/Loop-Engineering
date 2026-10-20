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
import time
from pathlib import Path

CURSOR_BIN = os.environ.get("CURSOR_AGENT_BIN", str(Path.home() / ".local/bin/cursor-agent"))
SANDBOX = Path(os.environ.get("CURSOR_LLM_SANDBOX", "/workspace/cursor-llm-sandbox"))
DEFAULT_MODEL = os.environ.get("CURSOR_LLM_MODEL", "gpt-5.3-codex")
ISOLATE = os.environ.get("CURSOR_LLM_ISOLATE", "1") != "0"
# Extra attempts after the first. Infra failures only; model content is never retried.
INFRA_RETRIES = int(os.environ.get("CURSOR_LLM_INFRA_RETRIES", "2"))


class InfraError(RuntimeError):
    """No model result after the infra retries are exhausted."""


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
    def __init__(self, model: str | None = None, timeout: int = 180) -> None:
        self.model = model if model is not None else DEFAULT_MODEL
        self.timeout = timeout
        self.tokens_used = 0
        self.calls: list[dict] = []
        self.infra_failures = 0
        SANDBOX.mkdir(parents=True, exist_ok=True)

    def _run_once(self, cmd: list[str]) -> tuple[str, int]:
        """One sandboxed cursor-agent process. Fresh temp home. Raises TimeoutExpired on timeout."""
        run_cmd = cmd
        tmp_home: Path | None = None
        if ISOLATE:
            home = str(Path.home())
            tmp_home = Path(tempfile.mkdtemp(prefix=".home-", dir=SANDBOX))
            cursor_dir = tmp_home / ".cursor"
            cursor_dir.mkdir(parents=True, exist_ok=True)
            cfg = Path(home) / ".cursor" / "cli-config.json"
            if cfg.exists():
                shutil.copy2(cfg, cursor_dir / "cli-config.json")
            run_cmd = [
                "bwrap", "--dev-bind", "/", "/", "--tmpfs", "/workspace", "--tmpfs", "/tmp",
                "--tmpfs", home, "--ro-bind", f"{home}/.local/bin", f"{home}/.local/bin",
                "--ro-bind", f"{home}/.local/share/cursor-agent", f"{home}/.local/share/cursor-agent",
                "--bind", f"{home}/.config/cursor", f"{home}/.config/cursor",
                "--bind", str(cursor_dir), f"{home}/.cursor",
                # Host public-plugin cache only; without it cursor-agent downloads plugins and hangs.
                *(
                    ["--ro-bind", f"{home}/.cursor/plugins", f"{home}/.cursor/plugins"]
                    if (Path(home) / ".cursor" / "plugins").is_dir()
                    else []
                ),
                "--bind", str(SANDBOX), str(SANDBOX), "--chdir", str(SANDBOX),
                "--setenv", "HOME", home, "--die-with-parent",
            ] + cmd
        try:
            proc = subprocess.Popen(
                run_cmd,
                cwd=SANDBOX,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            try:
                stdout, _stderr = proc.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.communicate()
                raise
        finally:
            if tmp_home is not None:
                shutil.rmtree(tmp_home, ignore_errors=True)
        code = proc.returncode
        return stdout or "", 1 if code is None else code

    def _append_call(self, role: str, attempts: list[dict], usage: dict | None) -> None:
        self.calls.append({
            "role": role,
            "seconds": round(sum(a["seconds"] for a in attempts), 1),
            "usage": usage,
            "isolated": ISOLATE,
            "attempts": attempts,
        })

    def complete(self, prompt: str, role: str = "default") -> str:
        cmd = [CURSOR_BIN, "-p", "--trust", "--mode", "ask", "--output-format", "json"]
        if self.model:
            cmd += ["--model", self.model]
        cmd.append(f"You are the {role} agent in a loop. Answer in plain text only.\n\n{prompt}")
        # No result: timeout, no output, unparsable output, or process error. Retry those.
        # A parsed model reply with content is final, including a non-zero exit that still
        # returned JSON without is_error.
        attempts: list[dict] = []
        last_error: BaseException | None = None
        for n in range(1, INFRA_RETRIES + 2):
            t0 = time.monotonic()
            try:
                stdout, returncode = self._run_once(cmd)
            except subprocess.TimeoutExpired as exc:
                seconds = round(time.monotonic() - t0, 1)
                attempts.append({"n": n, "seconds": seconds, "outcome": "timeout"})
                self.infra_failures += 1
                last_error = exc
                continue
            seconds = round(time.monotonic() - t0, 1)
            outcome, data, err = _classify_attempt(stdout, returncode)
            if outcome != "ok" or data is None:
                attempts.append({"n": n, "seconds": seconds, "outcome": outcome})
                self.infra_failures += 1
                last_error = err or RuntimeError(f"cursor-agent infra failure ({outcome})")
                continue
            u = data.get("usage") or {}
            self.tokens_used += int(u.get("inputTokens", 0)) + int(u.get("outputTokens", 0))
            attempts.append({"n": n, "seconds": seconds, "outcome": "ok"})
            self._append_call(role, attempts, u)
            return data.get("result", "")
        if last_error is None:
            last_error = RuntimeError("cursor-agent infra retry produced no result")
        self._append_call(role, attempts, None)
        raise InfraError(str(last_error)) from last_error
