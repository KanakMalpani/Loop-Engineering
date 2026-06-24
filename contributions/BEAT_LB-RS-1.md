# Beat LB-RS-1 — Research Synthesis baseline

One-command path for [LoopBench](https://github.com/KanakMalpani/LoopBench) task **LB-RS-1**.

**Target:** LES_obs ≥ **81.9** ([lb-rs-1-baseline.json](../benchmarks/results/lb-rs-1-baseline.json)).

---

## 60-second attempt

```bash
git clone https://github.com/KanakMalpani/Loop-Engineering.git
cd Loop-Engineering
pip install "loopbench>=0.1.1" loopgym pyyaml jsonschema

loopbench run \
  --task LB-RS-1 \
  --spec loop-library/research-agent.yaml \
  --seeds 0,1,2,3,4 \
  -o results.json

loopbench validate results.json
```

No API keys (SimEnv). Tune synthesis workers/evaluators in the spec, re-run.

---

## Submit

1. Post summary on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)
2. Open PR on [LoopBench](https://github.com/KanakMalpani/LoopBench) → `leaderboard/entries.json`
3. Reference [good-first issue #5](https://github.com/KanakMalpani/Loop-Engineering/issues/5)

See also [BEAT_LB-CR-1.md](BEAT_LB-CR-1.md) · [EXTERNAL_SUBMISSIONS.md](EXTERNAL_SUBMISSIONS.md).
