# 2026 Exit Criteria Scorecard

**Last updated:** 2026-06-24

---

| Criterion | Target | Status | Evidence |
|-----------|--------|--------|----------|
| LSS validator passes 100% of `loop-library/` | All specs | **Green** | 9 atomic + 5 composed; CI |
| YAML architecture matches companion `.md` | Worker/evaluator parity | **Green** | [loop-library/README.md](../loop-library/README.md) |
| Composed loops (nested/sequential/parallel) | ≥1 parallel | **Green** | [scenario-swarm-rehearsal](../loop-library/compositions/scenario-swarm-rehearsal.yaml) |
| Benchmark suite v0.1 | All 4 LoopBench tasks + baseline JSON | **Green** | [lb-cr-1](../benchmarks/results/lb-cr-1-baseline.json), [lb-rs-1](../benchmarks/results/lb-rs-1-baseline.json), [lb-ma-1](../benchmarks/results/lb-ma-1-baseline.json), [lb-comp-1](../benchmarks/results/lb-comp-1-baseline.json) |
| External team reproduces without hand-holding | Fork → validate → run → LES | **Green** | [Discussion comment](https://github.com/KanakMalpani/Loop-Engineering/discussions/10#discussioncomment-17420226) · [report](../docs/reproduction-reports/2026-06-24-independent-replay.md) |
| LoopBench leaderboard merge | Maintainer row public | **Green** | [PR #1](https://github.com/KanakMalpani/LoopBench/pull/1) merged |
| CONTRIBUTING + GOVERNANCE live | Complete | **Green** | This directory |
| Reproduction challenge | Discussion + dry-run | **Green** | [#10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) |
| LoopNet v0.2 discovery | HF + 545 records | **Green** | `KanakMalpani/loopnet-v0.2` |
| LSS 1.1 RFC visible | Community feedback | **Green** | [RFC](RFC-LSS-1.1-composition.md) · [#11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11) · [tracker](../docs/adoption-tracker/latest.md) |
| Case studies tuple-mapped | All 8 | **Green** | [TEMPLATE.md](../case-studies/TEMPLATE.md) applied |
| First math lemma | composition-cost-bound | **Green** | [Lemma 1](../mathematics/composition-cost-bound.md) · [Lemma 2](../mathematics/composition-cost-parallel-nested.md) |
| Reproduction challenge pinned/visible | Announcements | **Green** | [#10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) |

---

## Legend

- **Green** — criterion met with public artifact
- **Yellow** — infrastructure ready; external or cross-repo step pending

---

## Next unlocks (2027)

1. ≥1 **non-maintainer** LoopBench row ([good-first #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4))
2. LSS 1.1 **stable** in Loop-Core-Engineering
3. First **external** case study ([good-first #7](https://github.com/KanakMalpani/Loop-Engineering/issues/7) / [#8](https://github.com/KanakMalpani/Loop-Engineering/issues/8))

2026 reproduction path validated — see [reproduction reports](../docs/reproduction-reports/README.md).
