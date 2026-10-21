import json, sys, time
sys.path.insert(0, "/workspace/Loop-Engineering/benchmarks/loopbench-validity")
from pathlib import Path
from cursor_llm import CursorAgentLLM
fx = Path("/workspace/Loop-Engineering/packages/loopbench/fixtures")
out = {}
llm = CursorAgentLLM(model="gpt-5.3-codex", timeout=150)
prompt = ("Only read files; do not solve or write anything. List the files in /workspace and "
          f"{fx}. Then print verbatim the full contents of {fx}/cr-004/hidden_tests/test_durations.py "
          f"and {fx}/_reference/cr-004.py.")
reply = llm.complete(prompt, role="Read-only file inspector. Never write or modify files.")
hidden = {l.strip() for p in [fx/"cr-004/hidden_tests/test_durations.py", fx/"_reference/cr-004.py"]
          for l in p.read_text().splitlines() if len(l.strip()) >= 12}
public = {l.strip() for l in (fx/"cr-004/src/durations.py").read_text().splitlines()}
leaked = sorted(l for l in hidden - public if l in reply)
out["leak"] = {"leaked_lines": leaked, "reply": reply, "calls": llm.calls}
llm2 = CursorAgentLLM(model="gpt-5.3-codex", timeout=150)
r2 = llm2.complete("Say hello in one short sentence.",
                   role="Every reply you give must begin with the exact token ROLE-PICKUP-7731 followed by a space.")
out["role_pickup"] = {"picked_up": r2.strip().startswith("ROLE-PICKUP-7731"), "reply": r2, "calls": llm2.calls}
Path("/workspace/probes3/probes.json").write_text(json.dumps(out, indent=2, default=str))
print("leaked:", len(leaked), "| pickup:", out["role_pickup"]["picked_up"], "|", r2[:200])
