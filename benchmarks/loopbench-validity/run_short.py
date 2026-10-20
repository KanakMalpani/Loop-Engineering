"""Short measured run for B: one task, one seed, via the cursor-agent shim. MockLLM is made to raise."""
import json, sys, time
from pathlib import Path
import loopgym as lg
import loopgym.runtime.loop_runtime as rt
import loopgym.envs.sim as sim
sys.path.insert(0, str(Path(__file__).parent))
from cursor_llm import CursorAgentLLM

class _NoMock:
    def __init__(self, *a, **k): raise RuntimeError("MockLLM was constructed - run void")
rt.MockLLM = sim.MockLLM = _NoMock

loop, model, task, seed = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
here = Path(__file__).parent
llm = CursorAgentLLM(model=model)
env = lg.make("loopbench/code-repair-v1", spec_path=str(here / "loops" / f"{loop}.yaml"), backend="live", llm=llm)
t0 = time.monotonic()
res = env._sim.run_episode(  # LiveEnv has no run_episode (finding); its SimEnv carries the injected LLM
    task_id=task, seed=seed)
out = {"loop": loop, "model": model, "task": task, "seed": seed, "seconds": round(time.monotonic() - t0, 1),
       "mock_constructed": False, "llm_class": type(env._sim._runtime.llm).__name__,
       "result": res if isinstance(res, dict) else getattr(res, "__dict__", str(res)), "calls": llm.calls}
(here / "results").mkdir(exist_ok=True)
(here / "results" / f"short-{loop}-s{seed}.json").write_text(json.dumps(out, indent=2, default=str))
print(json.dumps({k: out[k] for k in ("loop", "model", "seconds", "llm_class")}))
