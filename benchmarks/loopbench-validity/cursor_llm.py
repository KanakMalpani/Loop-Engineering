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


class CursorAgentLLM:
    def __init__(self, model: str | None = None, timeout: int = 180) -> None:
        self.model = model if model is not None else DEFAULT_MODEL
        self.timeout = timeout
        self.tokens_used = 0
        self.calls: list[dict] = []
        SANDBOX.mkdir(parents=True, exist_ok=True)

    def complete(self, prompt: str, role: str = "default") -> str:
        cmd = [CURSOR_BIN, "-p", "--trust", "--mode", "ask", "--output-format", "json"]
        if self.model:
            cmd += ["--model", self.model]
        cmd.append(f"You are the {role} agent in a loop. Answer in plain text only.\n\n{prompt}")
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
                "--bind", str(SANDBOX), str(SANDBOX), "--chdir", str(SANDBOX),
                "--setenv", "HOME", home, "--die-with-parent",
            ] + cmd
        t0 = time.monotonic()
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
        dt = time.monotonic() - t0
        data = json.loads(stdout.strip().splitlines()[-1])
        if data.get("is_error"):
            raise RuntimeError(f"cursor-agent error: {data}")
        u = data.get("usage") or {}
        self.tokens_used += int(u.get("inputTokens", 0)) + int(u.get("outputTokens", 0))
        self.calls.append({"role": role, "seconds": round(dt, 1), "usage": u, "isolated": ISOLATE})
        return data.get("result", "")
