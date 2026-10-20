"""Deterministic stub run for B: same reply every call, all 10 loops. Evidence of runtime structure, not a model run."""
import json
from pathlib import Path
import loopgym as lg

class FixedStub:
    tokens_used = 0
    def complete(self, prompt, role="default"):
        return "Draft patch. score: 0.50"

here = Path(__file__).parent
rows = []
for p in sorted((here / "loops").glob("*.yaml")):
    env = lg.make("loopbench/code-repair-v1", spec_path=str(p), backend="live", llm=FixedStub())
    r = env._sim.run_episode(task_id="LB-CR-1", seed=0)
    r = r if isinstance(r, dict) else r.__dict__
    rows.append({"loop": p.stem, "quality_score": r.get("quality_score"), "success": r.get("success")})
(here / "results").mkdir(exist_ok=True)
(here / "results" / "stub-all-10.json").write_text(json.dumps(rows, indent=2))
for x in rows: print(f"{x['loop']:24} {x['quality_score']:.2f} {x['success']}")
