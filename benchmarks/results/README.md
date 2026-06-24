# Benchmark Results

Published maintainer baselines for LoopBench 0.1.0 (SimEnv, seeds 0–4).

**Submit new results:** [LoopBench](https://github.com/KanakMalpani/LoopBench) or the benchmark submission issue template.

---

## Published baselines

| Task ID | Name | LSS spec | LES observed | Artifact |
|---------|------|----------|--------------|----------|
| LB-CR-1 | Code Repair | autonomous-debugger | 86.7 | [lb-cr-1-baseline.json](./lb-cr-1-baseline.json) |
| LB-RS-1 | Research Synthesis | research-agent | 81.9 | [lb-rs-1-baseline.json](./lb-rs-1-baseline.json) |
| LB-MA-1 | Multi-Agent Debate | coding-agent | 86.5 | [lb-ma-1-baseline.json](./lb-ma-1-baseline.json) |
| LB-COMP-1 | Composed Swarm Rehearsal | scenario-swarm-rehearsal | 77.4 | [lb-comp-1-baseline.json](./lb-comp-1-baseline.json) |

Full submissions: `lb-*-run.json` in this directory.

---

## Reproduce

```bash
pip install loopbench
loopbench run --task LB-CR-1 --spec loop-library/autonomous-debugger.yaml --seeds 0,1,2,3,4 -o results.json
loopbench run --task LB-RS-1 --spec loop-library/research-agent.yaml --seeds 0,1,2,3,4 -o results.json
loopbench run --task LB-MA-1 --spec loop-library/coding-agent.yaml --seeds 0,1,2,3,4 -o results.json
loopbench run --task LB-COMP-1 --spec loop-library/compositions/scenario-swarm-rehearsal.yaml --seeds 0,1,2,3,4 -o results.json
```

See [contributions/REPRODUCE.md](../../contributions/REPRODUCE.md). Beat maintainer LES: [BEAT_LB-CR-1.md](../../contributions/BEAT_LB-CR-1.md) · [BEAT_LB-RS-1.md](../../contributions/BEAT_LB-RS-1.md) · [BEAT_LB-MA-1.md](../../contributions/BEAT_LB-MA-1.md) · [BEAT_LB-COMP-1.md](../../contributions/BEAT_LB-COMP-1.md)

---

## LES fields

| Field | Location | Meaning |
|-------|----------|---------|
| `les_observed` | `results.aggregate` | From LoopBench SimEnv runs (0–1) |
| `les_structural` | `results.les_structural` | From `tools/les_calculator.py` on LSS spec (0–100 display scale) |

CI audit: `python scripts/validate_baselines.py`

---

## Leaderboard

[LoopBench on GitHub](https://github.com/KanakMalpani/LoopBench)

---

## Next

- External submissions on leaderboard ([good-first #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4))
- Dedicated LoopGym env for LB-COMP-1 — **shipped** (`loopbench/composed-swarm-v1`)

See [All about loops/NEXT_STEPS.md](../../All%20about%20loops/NEXT_STEPS.md).
