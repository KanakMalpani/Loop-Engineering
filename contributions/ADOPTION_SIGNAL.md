# Loop Engineering v0.2 — Reproduction Challenge

**Launch:** June 2026  
**Goal:** First external reproduction of the Loop Engineering stack without maintainer assistance.

---

## What to reproduce

Complete [REPRODUCE.md](REPRODUCE.md) (≤60 minutes):

1. Validate an LSS spec from `loop-library/`
2. Run `examples/reflection-loop/run.py`
3. Emit LES JSON via `les_calculator.py`
4. (Optional) Match or beat the ALS-T2 maintainer baseline

---

## How to participate

**Option A — GitHub Discussion**  
Open a discussion titled `Reproduction report — [your handle]` on [Loop-Engineering](https://github.com/KanakMalpani/Loop-Engineering/discussions) with:

- Python version
- Validator output
- Reflection-loop output snippet
- LES JSON (attach or paste)
- Time to complete

**Option B — Benchmark issue**  
File an issue using the **Benchmark submission** template if you ran ALS tasks.

**Option C — External case study**  
File a **Case study** issue for a real system mapped to L = (S, A, O, T, E, M, τ).

---

## Maintainer baseline (LB-CR-1 / ALS-T2)

| Metric | Value |
|--------|-------|
| Task | LB-CR-1 Code Repair (LoopBench) |
| Spec | `loop-library/autonomous-debugger.yaml` |
| Structural LES | ~74.5 (post-enrichment) |
| Harness | LoopBench SimEnv (no API keys) |

Artifact: [benchmarks/results/als-t2-code-repair-baseline.json](../benchmarks/results/als-t2-code-repair-baseline.json)

---

## Success signal

This challenge succeeds when **at least one external contributor** publishes a reproduction report or benchmark submission.

That unlocks the 2027 roadmap (LSS 1.1 composition RFC, contributor funnel expansion).

---

## Links

- [REPRODUCE.md](REPRODUCE.md)
- [ECOSYSTEM_VERSIONS.md](../ECOSYSTEM_VERSIONS.md)
- [EXIT_CRITERIA_2026.md](EXIT_CRITERIA_2026.md)
