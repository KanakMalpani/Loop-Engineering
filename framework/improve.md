# Improve Phase

The Improve phase closes the DD-MIS lifecycle: turn Diagnose findings into spec changes that measurably raise LES.

---

## When to Improve

Improve when **Measure** shows:

- LES dimension below target (e.g., Effectiveness < 70)
- Recurring failure class from [failure taxonomy](../standards/failure-taxonomy.md)
- Cost per successful run above budget
- Safety near-miss logged in production

Do **not** improve spec reactively from a single failed run unless failure is classified as systematic.

---

## Improve Workflow

```
1. Hypothesis  — "Separating evaluator agent raises Effectiveness"
2. Change LSS   — minimal diff; version bump
3. Validate     — loop_validator.py --strict
4. Shadow run   — parallel to production spec
5. Compare      — loop_comparison.py + LES delta
6. Promote      — merge if ΔLES > threshold and no safety regression
```

---

## Change Categories

| Category | Example | Risk |
|----------|---------|------|
| Evaluator | Add command eval for regression tests | Low |
| Worker policy | Clarify constraints in worker prompt | Low |
| Topology | Add second worker (maker-checker) | Medium |
| Termination | Tighten max_iterations | Low |
| Optimization | Enable search over policies | High |
| Self-modification | Loop edits its own spec | Critical |

Level 5+ changes require [safety standard](../standards/safety-standard.md) review.

---

## Anti-Patterns

- **Prompt thrashing** — changing worker text without evaluator separation
- **Metric gaming** — optimizing one LES dimension while Safety drops
- **Unbounded iteration** — removing τ without adding cost_limits
- **Silent self-grade** — actor and evaluator share one model with no separation

---

## Checklist

- [ ] Hypothesis stated with target LES dimension
- [ ] LSS diff reviewed in PR
- [ ] Validator passes (`--strict` for production)
- [ ] Shadow metrics collected (N ≥ 10 runs)
- [ ] Comparison documented
- [ ] Rollback spec tagged in git

See also: [framework/diagnose.md](diagnose.md), [framework/measure.md](measure.md), [framework/scale.md](scale.md).
