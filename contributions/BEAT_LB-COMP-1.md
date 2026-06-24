# Beat LB-COMP-1 — Composed Swarm Rehearsal baseline

One-command path for [LoopBench](https://github.com/KanakMalpani/LoopBench) task **LB-COMP-1** (LSS 1.1 parallel composition).

**Target:** LES_obs ≥ **77.4** ([lb-comp-1-baseline.json](../benchmarks/results/lb-comp-1-baseline.json)).

---

## 60-second attempt

```bash
git clone https://github.com/KanakMalpani/Loop-Engineering.git
cd Loop-Engineering
pip install "loopbench>=0.1.1" loopgym pyyaml jsonschema

loopbench run \
  --task LB-COMP-1 \
  --spec loop-library/compositions/scenario-swarm-rehearsal.yaml \
  --seeds 0,1,2,3,4 \
  -o results.json

loopbench validate results.json
```

Local composed smoke (no LoopBench):

```bash
python examples/compose-loop/run.py loop-library/compositions/scenario-swarm-rehearsal.yaml
pip install "git+https://github.com/KanakMalpani/LoopGym.git"  # until loopgym>0.1.0 on PyPI
python -c "import loopgym as lg; print(lg.make('loopbench/composed-swarm-v1').reset(task_id='comp-001'))"
```

---

## Submit

1. Post summary on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)
2. Open PR on [LoopBench](https://github.com/KanakMalpani/LoopBench) → `leaderboard/entries.json`
3. Reference composed spec in PR description

See [BEAT_LB-CR-1.md](BEAT_LB-CR-1.md) · [EXTERNAL_SUBMISSIONS.md](EXTERNAL_SUBMISSIONS.md) · [langgraph-composition-bridge.md](../case-studies/langgraph-composition-bridge.md).
