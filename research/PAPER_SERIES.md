# Loop Engineering Paper Series

Five-paper research program (S1 survey + P1–P4 companions) that formalizes Loop Engineering as an academic discipline. PDFs are maintained locally under `C:\00 Research Papers\`; this page maps each paper to repository content.

**Status:** Writing complete (June 2026). arXiv and venue submission handled separately.

---

## Series map

| ID | Title (short) | Role | Repository links |
|----|---------------|------|------------------|
| **S1** | Loop Engineering Survey | Discipline map, ten principles, P1–P4 synthesis, benchmark gap | [fundamentals/](../fundamentals/), [patterns/](../patterns/), [research/open-problems.md](open-problems.md) |
| **P1** | Loop Algebra + LSS | Typed composition, safety certificates, Loop Specification Standard | [standards/LSS-1.0.md](../standards/LSS-1.0.md), [loop-library/](../loop-library/) |
| **P2** | Loop Complexity | Loop-P/EXP/CONST classes, iteration prediction, LoopBench calibration | [benchmarks/](../benchmarks/), [tools/loop_complexity_analyzer.py](../tools/loop_complexity_analyzer.py) |
| **P3** | Convergence & Stability | Lyapunov monotonicity, accuracy-correction ceiling, plateau stats | [fundamentals/07-convergence.md](../fundamentals/07-convergence.md) |
| **P4** | LoopNet Empirical | Corpus characterization, cost-coupling, Fano factor, FEI | [LOOPNET.md](LOOPNET.md), [HF v0.2](https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2) |

---

## Reading order

1. **S1** — start here for the full discipline overview
2. **P1** — formal foundation (algebra, LSS)
3. **P4** — empirical grounding on LoopNet v0.2 (545 Tier-1 trajectories)
4. **P2** — complexity bounds and prediction intervals
5. **P3** — convergence and stability theory

---

## Open problems resolved in papers

| Problem ID | Topic | Paper |
|------------|-------|-------|
| LE-OP-10 | Loop composition associativity | P1 (Proposition on algebra) |
| LE-OP-01 | Termination certificates | P3 (Lyapunov + budget caps) |
| LE-OP-02 | Non-monotonic evaluators | P3 (plateau/regression propositions) |
| LE-OP-21 | Cross-harness comparability | P4 (LoopNet process stats) |

See [open-problems.md](open-problems.md) for the full catalog.

---

## Ecosystem alignment

| Paper | Dataset / tool |
|-------|----------------|
| P2 | LoopBench `estimate_iterations()` calibration |
| P4 | [LoopNet v0.2](https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2) |
| All | LSS 1.0 / LES 1.0 in [Loop Core Engineering](https://github.com/KanakMalpani/Loop-Core-Engineering) |

Version registry: [ECOSYSTEM_VERSIONS.md](../ECOSYSTEM_VERSIONS.md)

---

## Citation

BibTeX for the paper series: [contributions/CITATION.md](../contributions/CITATION.md#paper-series-forthcoming).

---

## Local submission packages

Full LaTeX venue tracks live at:

```
C:\00 Research Papers\
├── Loop Engineering Survey\          (S1)
├── Loop Algebra for Autonomous Agent Loops\   (P1)
├── Loop Complexity and Convergence for Agent Loops\  (P2)
├── Loop Convergence and Stability for Agent Loops\  (P3)
└── LoopNet Empirical Characterization\        (P4)
```

See `LOOP_ENGINEERING_SERIES_README.md` in that folder for compile and submission order.
