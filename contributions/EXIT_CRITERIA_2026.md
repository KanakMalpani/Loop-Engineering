# 2026 Exit Criteria Scorecard

**Last updated:** 2026-06-24

---

| Criterion | Target | Status | Evidence |
|-----------|--------|--------|----------|
| LSS validator passes 100% of `loop-library/` | All specs | **Green** | 9 atomic + 5 composed; CI |
| YAML architecture matches companion `.md` | Worker/evaluator parity | **Green** | [loop-library/README.md](../loop-library/README.md) |
| Composed loops (nested/sequential/parallel) | ≥1 parallel | **Green** | [scenario-swarm-rehearsal](../loop-library/compositions/scenario-swarm-rehearsal.yaml) |
| Benchmark suite v0.1 | All 3 LoopBench tasks + baseline JSON | **Green** | [lb-cr-1](../benchmarks/results/lb-cr-1-baseline.json), [lb-rs-1](../benchmarks/results/lb-rs-1-baseline.json), [lb-ma-1](../benchmarks/results/lb-ma-1-baseline.json) |
| External team reproduces without hand-holding | Fork → validate → run → LES | **Yellow** | [REPRODUCE.md](REPRODUCE.md); awaiting external report |
| LoopBench leaderboard merge | Maintainer row public | **Green** | [PR #1](https://github.com/KanakMalpani/LoopBench/pull/1) merged |
| CONTRIBUTING + GOVERNANCE live | Complete | **Green** | This directory |
| Reproduction challenge | Discussion + dry-run | **Green** | [#10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) |
| LoopNet v0.2 discovery | HF + 545 records | **Green** | `KanakMalpani/loopnet-v0.2` |
| LSS 1.1 RFC visible | Community feedback | **Green** | [RFC](RFC-LSS-1.1-composition.md) · [#11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11) |
| Mathematics foundation seed | `mathematics/` directory | **Green** | [mathematics/README.md](../mathematics/README.md) |

---

## Legend

- **Green** — criterion met with public artifact
- **Yellow** — infrastructure ready; external or cross-repo step pending

---

## Next unlocks (2027)

1. First **external** reproduction report
2. LoopBench PR #1 merged + RS/MA rows on leaderboard
3. LSS 1.1 draft in Loop-Core-Engineering

See [All about loops/NEXT_STEPS.md](../All%20about%20loops/NEXT_STEPS.md).
