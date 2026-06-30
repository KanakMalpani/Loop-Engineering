# Beat suite-rigor — composition & safety comparison suite

One-command path for LoopBench **suite-rigor** (5 micro-tasks: COMP, Nest, Sim, HITL, Mem).

**Target:** `suite_scores.suite-rigor.rank_score` ≥ maintainer baseline.  
**Micro-tasks:** [SUITE-OVERVIEW.md](../docs/ecosystem-sync/LoopBench/docs/SUITE-OVERVIEW.md)

---

## Harness → recipe → run

```bash
pip install "le-loop-stack>=0.3.0"

# 1. Map composed / safety-aware harness
loopctl agent map --harness native --intent "Nested loops with human gate and memory" -o rigor.yaml --json

# 2. Mix the safe-repair recipe (composition + guardrails)
loop mix safe-repair --intent "Verify before merge with rollback" --spec rigor.yaml -o mixed.yaml --json

loopctl validate mixed.yaml

# 3. Run the comparison suite
loopbench run --suite suite-rigor --spec mixed.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
```

No API keys (SimEnv). Tune nested composition and evaluators, re-run.

---

## PR checklist

1. `results.json` includes `suite_scores.suite-rigor` + `grand_composite`
2. Fork [LoopBench](https://github.com/KanakMalpani/LoopBench) → add row to `leaderboard/entries.json`
3. Set `primary_suite: "suite-rigor"`, `repro_command` to your exact `--suite` run
4. Post summary on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)
5. Reference composed spec + LoopBench PR (LB-COMP-1 lineage)

See [BEAT_suite-repair.md](BEAT_suite-repair.md) · [BEAT_LB-COMP-1.md](BEAT_LB-COMP-1.md).
