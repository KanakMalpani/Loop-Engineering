"""Stub checks for cr-001..cr-007. No model; deterministic.

1. Reference patch scores 1.0 and empty output scores 0 on every fixture.
   cr-004+ also record an obvious-fix score, which must sit strictly between 0 and 1.
2. Across all 10 loops, run --task (default LB-CR-1) for every --seeds value
   (default 0,1,2,3,4). Per stub, score is the minimum across seeds.
   - fixed_reply: same non-code reply every call
   - feedback_stub: buggy source until test-runner feedback, then the reference fix
   - iterative_stub: buggy source, then the obvious fix after the first test feedback
     (reference immediately for cr-001..cr-003), then the reference after the second
Stub-only: reference fixes and obvious fixes are read here, never by the runtime.
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import loopgym as lg
import loopgym.runtime.loop_runtime as rt
from loopgym.envs import sim
from loopgym.evaluators.sandbox_tests import FIXTURES_ROOT, get_fixture, test_pass_rate


class _NoMock:
    def __init__(self, *a, **k):
        raise RuntimeError("MockLLM was constructed - run void")


rt.MockLLM = sim.MockLLM = _NoMock

here = Path(__file__).parent
REF = FIXTURES_ROOT / "_reference"
OBVIOUS = here / "obvious_fixes"
IDS = [f"cr-00{n}" for n in range(1, 8)]
EARLY = {"cr-001", "cr-002", "cr-003"}
MOD2ID = {
    "calc": "cr-001",
    "stats": "cr-002",
    "text": "cr-003",
    "durations": "cr-004",
    "intervals": "cr-005",
    "slugs": "cr-006",
    "money": "cr-007",
}


def blk(code: str) -> str:
    return f"```python\n{code}```"


class FixedReply:
    tokens_used = 0

    def complete(self, prompt, role="default"):
        return "Draft patch. score: 0.50"


class FeedbackStub:
    tokens_used = 0

    def complete(self, prompt, role="default"):
        match = re.search(r"Module under repair \((\w+)\.py\)", prompt)
        if not match:
            return "I need the bug and the code."
        fid = MOD2ID[match.group(1)]
        if "Feedback from test_runner" in prompt:
            return blk((REF / f"{fid}.py").read_text())
        return blk(get_fixture(fid).source)


class IterativeStub:
    """Buggy source, then obvious fix, then reference — per fixture."""

    tokens_used = 0

    def __init__(self):
        self.feedback_rounds = {}

    def complete(self, prompt, role="default"):
        match = re.search(r"Module under repair \((\w+)\.py\)", prompt)
        if not match:
            return "I need the bug and the code."
        fid = MOD2ID[match.group(1)]
        if "Feedback from test_runner" not in prompt:
            self.feedback_rounds[fid] = 0
            return blk(get_fixture(fid).source)
        seen = self.feedback_rounds.get(fid, 0) + 1
        self.feedback_rounds[fid] = seen
        if seen == 1 and fid not in EARLY:
            return blk((OBVIOUS / f"{fid}.py").read_text())
        return blk((REF / f"{fid}.py").read_text())


parser = argparse.ArgumentParser(description="Stub checks including obvious-fix fixtures")
parser.add_argument("--seeds", default="0,1,2,3,4", help="comma-separated seeds")
parser.add_argument("--task", default="LB-CR-1")
args = parser.parse_args()
seeds = [int(part.strip()) for part in args.seeds.split(",") if part.strip() != ""]
if not seeds:
    parser.error("at least one seed is required")
task = args.task

checks = []
for fid in IDS:
    fx = get_fixture(fid)
    row = {
        "fixture": fid,
        "reference_patch": test_pass_rate(fx, blk((REF / f"{fid}.py").read_text()))["test_pass_rate"],
        "empty_output": test_pass_rate(fx, "")["test_pass_rate"],
        "buggy_source_unchanged": test_pass_rate(fx, blk(fx.source))["test_pass_rate"],
    }
    if fid not in EARLY:
        row["obvious_fix"] = test_pass_rate(fx, blk((OBVIOUS / f"{fid}.py").read_text()))["test_pass_rate"]
    checks.append(row)
obvious = [c for c in checks if "obvious_fix" in c]
ok = all(c["reference_patch"] == 1.0 and c["empty_output"] == 0.0 for c in checks) and all(
    0.0 < c["obvious_fix"] < 1.0 for c in obvious
)

rows = []
t0 = time.monotonic()
stubs = (("fixed_reply", FixedReply), ("feedback_stub", FeedbackStub), ("iterative_stub", IterativeStub))
for path in sorted((here / "loops").glob("*.yaml")):
    row = {"loop": path.stem}
    for name, cls in stubs:
        env = lg.make("loopbench/code-repair-v1", spec_path=str(path), backend="live", llm=cls())
        by_seed = {}
        chosen = None
        for seed in seeds:
            result = env.run_episode(task_id=task, seed=seed)
            by_seed[seed] = result["quality_score"]
            if chosen is None or result["quality_score"] < chosen["quality_score"]:
                chosen = result
        row[name] = {
            "score": min(by_seed.values()),
            "by_seed": by_seed,
            "success": chosen["success"],
            "llm_class": chosen["llm_class"],
            "per_fixture": {
                item["fixture"]: [item["quality_score"], item["termination_reason"]]
                for item in chosen["instances"]
            },
            "cost_usd": chosen["cost_usd"],
        }
    rows.append(row)
out = {
    "seeds": seeds,
    "task": task,
    "fixture_checks": checks,
    "fixture_checks_pass": ok,
    "loops": rows,
    "mock_constructed": False,
    "seconds": round(time.monotonic() - t0, 2),
    "note": "stub run: evidence of runtime behaviour, not a model run; does not count toward check 5",
}
out_dir = here / "results" / "stub-attempt3"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "stub-all-10.json").write_text(json.dumps(out, indent=2))
for c in checks:
    print(c)


def _fmt_by_seed(by_seed):
    return ",".join(f"{seed}:{score:.2f}" for seed, score in by_seed.items())


for item in rows:
    parts = [f"{item['loop']:24}"]
    for name, _cls in stubs:
        block = item[name]
        parts.append(f"{name}={block['score']:.2f} [{_fmt_by_seed(block['by_seed'])}]")
    print(" ".join(parts))
print("fixture checks pass:", ok, "task:", task, "seeds:", seeds, "seconds:", out["seconds"])
sys.exit(0 if ok else 1)
