# Beat suite-knowledge — research comparison suite

One-command path for LoopBench **suite-knowledge** (4 micro-tasks: RS, RAG, Bootstrap, Auto).

**Target:** `suite_scores.suite-knowledge.rank_score` ≥ maintainer baseline.  
**Micro-tasks:** [SUITE-OVERVIEW.md](../docs/ecosystem-sync/LoopBench/docs/SUITE-OVERVIEW.md)

---

## Harness → recipe → run

```bash
pip install "le-loop-stack>=0.3.0"

# 1. Map research / RAG harness (DSPy, native, …)
loopctl agent map --harness dspy --intent "Synthesize sources into cited report" -o research.yaml --json

# 2. Mix the research-pipeline recipe
loop mix research-pipeline --intent "Literature review with citations" --spec research.yaml -o mixed.yaml --json

loopctl validate mixed.yaml

# 3. Run the comparison suite
loopbench run --suite suite-knowledge --spec mixed.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
```

No API keys (SimEnv). Tune synthesis workers, re-run.

---

## PR checklist

1. `results.json` includes `suite_scores.suite-knowledge` + `grand_composite`
2. Fork [LoopBench](https://github.com/KanakMalpani/LoopBench) → add row to `leaderboard/entries.json`
3. Set `primary_suite: "suite-knowledge"`, `repro_command` to your exact `--suite` run
4. Post summary on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)
5. Reference [good-first #5](https://github.com/KanakMalpani/Loop-Engineering/issues/5) or suite PR on LoopBench

See [BEAT_suite-repair.md](BEAT_suite-repair.md) · [LOOP_PLAYGROUND.md](LOOP_PLAYGROUND.md).
