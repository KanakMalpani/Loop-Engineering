# Beat LB-CR-1 — one-command LoopBench path

For `pip install loopbench` users landing from [LoopBench](https://github.com/KanakMalpani/LoopBench) or [REPRODUCE.md](REPRODUCE.md).

**Target:** Success@k ≥ maintainer, LES_obs ≥ **86.7** ([lb-cr-1-baseline.json](../benchmarks/results/lb-cr-1-baseline.json)).

---

## 60-second attempt

```bash
git clone https://github.com/KanakMalpani/Loop-Engineering.git
cd Loop-Engineering
pip install "loopbench>=0.1.1" loopgym pyyaml jsonschema

loopbench run \
  --task LB-CR-1 \
  --spec loop-library/autonomous-debugger.yaml \
  --seeds 0,1,2,3,4 \
  -o results.json

loopbench validate results.json
```

No API keys (SimEnv). Fork the spec, tune workers/evaluators, re-run.

---

## Submit

1. Post `results.json` summary on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)
2. Open PR on [LoopBench](https://github.com/KanakMalpani/LoopBench) adding your row to `leaderboard/entries.json`
3. Reference [good-first issue #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4)

---

## Cursor / LangGraph / CrewAI

Map your harness first: [BRIDGE_AGENT_HARNESSES.md](BRIDGE_AGENT_HARNESSES.md) · [cursor-agent-loop case study](../case-studies/cursor-agent-loop.md).
