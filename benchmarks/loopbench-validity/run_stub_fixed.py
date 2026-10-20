"""Stub checks for the FIXED benchmark (real-outcome scoring). No model; deterministic.

1. Reference-patch stub must score 1.0 on each fixture; empty-output stub must score 0.
2. Across all 10 loops (unchanged since 49809bc), LB-CR-1 seed 0, record scores for:
   - fixed_reply: same non-code reply every call (old run_stub.py reply)
   - feedback_stub: returns the buggy source unchanged, and the reference fix only after it
     receives test-runner feedback in its prompt. Needs bug input + feedback channel + test evaluator.
Stub-only: the reference fixes are read here by the STUB, never by the runtime or a prompt.
"""
import json, re, sys, time
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
        r = env.run_episode(task_id="LB-CR-1", seed=0)
        row[name] = {"score": r["quality_score"], "success": r["success"], "llm_class": r["llm_class"],
                     "per_fixture": {i["fixture"]: [i["quality_score"], i["termination_reason"]] for i in r["instances"]},
                     "cost_usd": r["cost_usd"]}
    rows.append(row)
out = {"fixture_checks": checks, "fixture_checks_pass": ok, "loops": rows,
       "mock_constructed": False, "seconds": round(time.monotonic() - t0, 2),
       "note": "stub run: evidence of runtime behaviour, not a model run; does not count toward check 5"}
(here / "results").mkdir(exist_ok=True)
(here / "results" / "stub-fixed-all-10.json").write_text(json.dumps(out, indent=2))
for c in checks: print(c)
for x in rows:
    print(f"{x['loop']:24} fixed_reply={x['fixed_reply']['score']:.2f} feedback_stub={x['feedback_stub']['score']:.2f} "
          f"{x['feedback_stub']['per_fixture']}")
print("fixture checks pass:", ok, "seconds:", out["seconds"])
sys.exit(0 if ok else 1)
