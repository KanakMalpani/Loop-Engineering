# Beat suite-repair — repair comparison suite

One-command path for LoopBench **suite-repair** (5 micro-tasks: CR, ReAct, Reflexion, OPT, SAFE).

**Target:** `suite_scores.suite-repair.rank_score` ≥ maintainer baseline.  
**Micro-tasks:** [SUITE-OVERVIEW.md](../docs/ecosystem-sync/LoopBench/docs/SUITE-OVERVIEW.md)

---

## Harness → recipe → run

```bash
pip install "le-loop-stack>=0.3.0"

# 1. Map your repair harness (Agentless, Aider, OpenHands, native, …)
loopctl agent map --harness aider --intent "Fix failing tests with minimal diff" -o repair.yaml --json

# 2. Mix the dev-agent recipe into the spec
loop mix dev-agent --intent "Fix CI tests" --spec repair.yaml -o mixed.yaml --json

loopctl validate mixed.yaml

# 3. Run the comparison suite (not flat --task)
loopbench run --suite suite-repair --spec mixed.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
```

No API keys (SimEnv). Tune workers/evaluators, re-run.

---

## PR checklist

1. `results.json` includes `suite_scores.suite-repair` + `grand_composite` (set `partial: true` if only this suite)
2. Fork [LoopBench](https://github.com/KanakMalpani/LoopBench) → add row to `leaderboard/entries.json` ([template](../docs/submission-dry-run/external-template-row.json))
3. Set `primary_suite: "suite-repair"`, `repro_command` to your exact `--suite` run
4. Post summary on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)
5. Reference [good-first #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4)

See [LOOP_PLAYGROUND.md](LOOP_PLAYGROUND.md) · [PARTNER_LOOPBENCH_SUBMIT.md](PARTNER_LOOPBENCH_SUBMIT.md).
