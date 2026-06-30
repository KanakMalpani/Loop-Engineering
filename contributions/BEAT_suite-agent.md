# Beat suite-agent — multi-agent comparison suite

One-command path for LoopBench **suite-agent** (5 micro-tasks: MA, Crew, Graph, ToT, Vote).

**Target:** `suite_scores.suite-agent.rank_score` ≥ maintainer baseline.  
**Micro-tasks:** [SUITE-OVERVIEW.md](../docs/ecosystem-sync/LoopBench/docs/SUITE-OVERVIEW.md)

---

## Harness → recipe → run

```bash
pip install "le-loop-stack>=0.3.0"

# 1. Map LangGraph / CrewAI / native multi-agent harness
loopctl agent map --harness langgraph --intent "Parallel branches with merge gate" -o agent.yaml --json

# 2. Mix the swarm-review recipe
loop mix swarm-review --intent "Parallel research and debate" --spec agent.yaml -o mixed.yaml --json

loopctl validate mixed.yaml

# 3. Run the comparison suite
loopbench run --suite suite-agent --spec mixed.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
```

No API keys (SimEnv). Tune composition workers, re-run.

---

## PR checklist

1. `results.json` includes `suite_scores.suite-agent` + `grand_composite`
2. Fork [LoopBench](https://github.com/KanakMalpani/LoopBench) → add row to `leaderboard/entries.json`
3. Set `primary_suite: "suite-agent"`, `repro_command` to your exact `--suite` run
4. Post summary on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)
5. Reference [good-first #6](https://github.com/KanakMalpani/Loop-Engineering/issues/6) or suite PR on LoopBench

See [BEAT_suite-repair.md](BEAT_suite-repair.md) · [LOOP_PLAYGROUND.md](LOOP_PLAYGROUND.md).
