"""Stub checks for the FIXED benchmark (real-outcome scoring). No model; deterministic.

1. Reference-patch stub must score 1.0 on each fixture; empty-output stub must score 0.
2. Across all 10 loops (unchanged since 49809bc), run --task (default LB-CR-1) for every
   --seeds value (default 0,1,2,3,4). Record scores for:
   - fixed_reply: same non-code reply every call (old run_stub.py reply)
   - feedback_stub: returns the buggy source unchanged, and the reference fix only after it
     receives test-runner feedback in its prompt. Needs bug input + feedback channel + test evaluator.
   Per stub, score is the minimum across seeds.
Stub-only: the reference fixes are read here by the STUB, never by the runtime or a prompt.
"""
import argparse, json, re, sys, time
from pathlib import Path
import loopgym as lg
import loopgym.envs.sim as sim
import loopgym.runtime.loop_runtime as rt
from loopgym.evaluators.sandbox_tests import FIXTURES_ROOT, get_fixture, test_pass_rate

class _NoMock:
    def __init__(self, *a, **k): raise RuntimeError("MockLLM was constructed - run void")
rt.MockLLM = sim.MockLLM = _NoMock

here = Path(__file__).parent
REF = FIXTURES_ROOT / "_reference"
MOD2ID = {"calc": "cr-001", "stats": "cr-002", "text": "cr-003"}
blk = lambda c: f"```python\n{c}```"

class FixedReply:
    tokens_used = 0
    def complete(self, prompt, role="default"): return "Draft patch. score: 0.50"

class FeedbackStub:
    tokens_used = 0
    def complete(self, prompt, role="default"):
        m = re.search(r"Module under repair \((\w+)\.py\)", prompt)
        if not m: return "I need the bug and the code."
        fid = MOD2ID[m.group(1)]
        if "Feedback from test_runner" in prompt: return blk((REF / f"{fid}.py").read_text())
        return blk(get_fixture(fid).source)

parser = argparse.ArgumentParser(description="Stub checks for the FIXED benchmark")
parser.add_argument("--seeds", default="0,1,2,3,4", help="comma-separated seeds")
parser.add_argument("--task", default="LB-CR-1")
args = parser.parse_args()
seeds = [int(part.strip()) for part in args.seeds.split(",") if part.strip() != ""]
if not seeds:
    parser.error("at least one seed is required")
task = args.task

checks = []
for fid in ("cr-001", "cr-002", "cr-003"):
    fx = get_fixture(fid)
    checks.append({"fixture": fid,
                   "reference_patch": test_pass_rate(fx, blk((REF / f"{fid}.py").read_text()))["test_pass_rate"],
                   "empty_output": test_pass_rate(fx, "")["test_pass_rate"],
                   "buggy_source_unchanged": test_pass_rate(fx, blk(fx.source))["test_pass_rate"]})
ok = all(c["reference_patch"] == 1.0 and c["empty_output"] == 0.0 for c in checks)

rows = []
t0 = time.monotonic()
for p in sorted((here / "loops").glob("*.yaml")):
    row = {"loop": p.stem}
    for name, cls in (("fixed_reply", FixedReply), ("feedback_stub", FeedbackStub)):
        env = lg.make("loopbench/code-repair-v1", spec_path=str(p), backend="live", llm=cls())
        by_seed = {}
        chosen = None
        for seed in seeds:
            r = env.run_episode(task_id=task, seed=seed)
            by_seed[seed] = r["quality_score"]
            if chosen is None or r["quality_score"] < chosen["quality_score"]:
                chosen = r
        row[name] = {"score": min(by_seed.values()), "by_seed": by_seed,
                     "success": chosen["success"], "llm_class": chosen["llm_class"],
                     "per_fixture": {i["fixture"]: [i["quality_score"], i["termination_reason"]] for i in chosen["instances"]},
                     "cost_usd": chosen["cost_usd"]}
    rows.append(row)
out = {"seeds": seeds, "task": task, "fixture_checks": checks, "fixture_checks_pass": ok, "loops": rows,
       "mock_constructed": False, "seconds": round(time.monotonic() - t0, 2),
       "note": "stub run: evidence of runtime behaviour, not a model run; does not count toward check 5"}
(here / "results").mkdir(exist_ok=True)
(here / "results" / "stub-fixed-all-10.json").write_text(json.dumps(out, indent=2))
for c in checks: print(c)
def _fmt_by_seed(by_seed):
    return ",".join(f"{seed}:{score:.2f}" for seed, score in by_seed.items())

for x in rows:
    fr, fb = x["fixed_reply"], x["feedback_stub"]
    print(f"{x['loop']:24} fixed_reply={fr['score']:.2f} [{_fmt_by_seed(fr['by_seed'])}] "
          f"feedback_stub={fb['score']:.2f} [{_fmt_by_seed(fb['by_seed'])}]")
print("fixture checks pass:", ok, "task:", task, "seeds:", seeds, "seconds:", out["seconds"])
sys.exit(0 if ok else 1)
