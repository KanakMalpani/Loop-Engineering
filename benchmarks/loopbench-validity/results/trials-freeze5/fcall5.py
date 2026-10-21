"""One call through the FROZEN cursor_llm (clean worktree at 6edebdf (FROZEN-5)). Usage: fcall.py OUTDIR"""
import json, sys, time
from pathlib import Path
WT = Path("/workspace/le-trial-6edebdf")
sys.path.insert(0, str(WT / "benchmarks/loopbench-validity"))
import cursor_llm  # frozen file, no shim, no CURSOR_TRIAL_BIN
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
FX = WT / "packages/loopbench/fixtures/cr-004"
prompt = ("Objective: repair the module so its hidden tests pass.\n"
          f"Bug description:\n{(FX/'BUG.md').read_text()}\n"
          f"Module under repair (durations.py):\n```\n{(FX/'src/durations.py').read_text()}```\n"
          "Return the full corrected module in one fenced code block.")
rec = {"cursor_llm": cursor_llm.__file__, "model": cursor_llm.DEFAULT_MODEL, "timeout": 150,
       "prompt_chars": len(prompt), "start": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
t0 = time.monotonic()
llm = cursor_llm.CursorAgentLLM(timeout=150, log_path=OUT / "calls.jsonl", run_id=OUT.name)
try:
    rec["reply"] = llm.complete(prompt, role="Produce a minimal code patch")[-3000:]
except Exception as e:  # noqa: BLE001
    rec["error"] = repr(e)
rec["calls"] = llm.calls
rec["seconds"] = round(time.monotonic() - t0, 1); rec["end"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
(OUT / "result.json").write_text(json.dumps(rec, indent=2, default=str))
print(json.dumps({"dir": OUT.name, "seconds": rec["seconds"], "error": rec.get("error")}))
