"""LLMClient shim: routes LoopGym prompts to the Cursor CLI (cursor-agent) instead of MockLLM.

Validity caveat: cursor-agent is an agent wrapper, not a raw model. It runs in read-only
"ask" mode in an empty sandbox dir, so tools cannot edit files, but its system prompt and
model routing are Cursor's, not ours.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

CURSOR_BIN = os.environ.get("CURSOR_AGENT_BIN", str(Path.home() / ".local/bin/cursor-agent"))
SANDBOX = Path(os.environ.get("CURSOR_LLM_SANDBOX", "/workspace/cursor-llm-sandbox"))


class CursorAgentLLM:
    def __init__(self, model: str | None = None, timeout: int = 180) -> None:
        self.model = model
        self.timeout = timeout
        self.tokens_used = 0
        self.calls: list[dict] = []
        SANDBOX.mkdir(parents=True, exist_ok=True)

    def complete(self, prompt: str, role: str = "default") -> str:
        cmd = [CURSOR_BIN, "-p", "--trust", "--mode", "ask", "--output-format", "json"]
        if self.model:
            cmd += ["--model", self.model]
        cmd.append(f"You are the {role} agent in a loop. Answer in plain text only.\n\n{prompt}")
        t0 = time.monotonic()
        out = subprocess.run(cmd, cwd=SANDBOX, capture_output=True, text=True, timeout=self.timeout)
        dt = time.monotonic() - t0
        data = json.loads(out.stdout.strip().splitlines()[-1])
        if data.get("is_error"):
            raise RuntimeError(f"cursor-agent error: {data}")
        u = data.get("usage") or {}
        self.tokens_used += int(u.get("inputTokens", 0)) + int(u.get("outputTokens", 0))
        self.calls.append({"role": role, "seconds": round(dt, 1), "usage": u})
        return data.get("result", "")
