# Beat LB-MA-1 — Multi-Agent Debate baseline

One-command path for [LoopBench](https://github.com/KanakMalpani/LoopBench) task **LB-MA-1**.

**Target:** LES_obs ≥ **86.5** ([lb-ma-1-baseline.json](../benchmarks/results/lb-ma-1-baseline.json)).

---

## 60-second attempt

```bash
git clone https://github.com/KanakMalpani/Loop-Engineering.git
cd Loop-Engineering
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" "loopbench>=0.1.1" "loopgym>=0.1.2" pyyaml jsonschema

loopbench run \
  --task LB-MA-1 \
  --spec loop-library/coding-agent.yaml \
  --seeds 0,1,2,3,4 \
  -o results.json

loopbench validate results.json
```

No API keys (SimEnv). Fork the spec for your multi-agent harness mapping, re-run.

---

## Submit

1. Post summary on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)
2. Open PR on [LoopBench](https://github.com/KanakMalpani/LoopBench) → `leaderboard/entries.json`
3. Reference [good-first issue #6](https://github.com/KanakMalpani/Loop-Engineering/issues/6)

See also [BEAT_LB-CR-1.md](BEAT_LB-CR-1.md) · [EXTERNAL_SUBMISSIONS.md](EXTERNAL_SUBMISSIONS.md).
