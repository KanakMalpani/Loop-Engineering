"""Leak probe records calls and the last attempt. No real cursor-agent."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BENCH = ROOT / "benchmarks" / "loopbench-validity"
if str(BENCH) not in sys.path:
    sys.path.insert(0, str(BENCH))

import cursor_llm
import leak_probe

PINNED = "grok-4.7-high"


def _body(result: str) -> str:
    payload = {
        "result": result,
        "is_error": False,
        "usage": {"inputTokens": 1, "outputTokens": 1},
    }
    return json.dumps(payload)


def _stub_version(monkeypatch) -> None:
    reported = cursor_llm.PINNED_CURSOR_AGENT_VERSION

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, stdout=reported + "\n", stderr="")

    monkeypatch.setattr(cursor_llm.subprocess, "run", fake_run)


def test_leak_probe_records_call_and_last_attempt(tmp_path, monkeypatch):
    monkeypatch.setattr(cursor_llm, "SANDBOX", tmp_path / "sandbox")
    _stub_version(monkeypatch)
    results = tmp_path / "results"
    monkeypatch.setattr(leak_probe, "results_dir", results)
    out_path = tmp_path / "custom" / "leak-probe.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["leak_probe.py", "--model", PINNED, "--timeout", "5", "--out", str(out_path)],
    )
    built: dict = {}
    real_cls = leak_probe.CursorAgentLLM

    class Recording(real_cls):
        def __init__(self, *args, **kwargs):
            built["kwargs"] = kwargs
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(leak_probe, "CursorAgentLLM", Recording)

    def fake(self, cmd, cwd, **_extra):
        self._last_reap = {
            "tag": "lbreap-test",
            "killed": [9],
            "leftover": 1,
            "leftover_tagged": 2,
            "leftover_worker_servers": 1,
        }
        return _body("ZZ-NO-LEAK-TOKEN"), 0, "leak-stderr"

    monkeypatch.setattr(cursor_llm.CursorAgentLLM, "_run_once", fake)
    leak_probe.main()
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written["reply"] == "ZZ-NO-LEAK-TOKEN"
    assert written["leaked"] is False
    call = written["calls"][-1]
    attempt = call["attempts"][-1]
    assert written["stderr_path"] == attempt["stderr_path"]
    assert written["stderr_bytes"] == attempt["stderr_bytes"]
    assert written["returncode"] == attempt["returncode"]
    assert written["reap_tag"] == attempt["reap_tag"]
    assert written["reap_kills"] == attempt["reap_kills"]
    assert written["leftover_worker_servers"] == attempt["leftover_worker_servers"]
    assert written["leftover_tagged"] == attempt["leftover_tagged"]
    assert written["reap_log"] == call["reap_log"]
    stderr_path = Path(written["stderr_path"])
    assert stderr_path.parent == results / "stderr"
    assert stderr_path.name == "leak-probe-call0-attempt1.stderr"
    assert stderr_path.read_text(encoding="utf-8") == "leak-stderr"
    assert written["stderr_bytes"] == len(b"leak-stderr")
    assert written["reap_tag"] == "lbreap-test"
    assert written["reap_kills"] == 1
    assert written["leftover_worker_servers"] == 1
    assert written["leftover_tagged"] == 2
    assert written["reap_log"] == str(results / "reap.log")
    log_path = Path(built["kwargs"]["log_path"])
    assert log_path.parent == results
    assert built["kwargs"]["run_id"] == "leak-probe"
