# Failure Taxonomy

Universal failure modes for loop systems across taxonomy levels 1–6.

---

## Classification

| ID | Name | Description | Typical level |
|----|------|-------------|---------------|
| F1 | Open loop | No evaluator closure; human carries all feedback | 1 |
| F2 | Self-grade | Actor evaluates own output | 2–3 |
| F3 | Evaluator drift | Evaluator criteria change without version bump | 2–4 |
| F4 | τ omission | No max_iterations or cost_limit | all |
| F5 | False pass | Evaluator passes incorrect artifact | 2–5 |
| F6 | False fail | Evaluator rejects valid artifact | 2–5 |
| F7 | Oscillation | Quality alternates without convergence | 2–4 |
| F8 | Resource bleed | Run continues past cost_limits | all |
| F9 | State corruption | Memory M inconsistent across iterations | 2–6 |
| F10 | Orchestration deadlock | Multi-agent wait cycle | 3+ |
| F11 | Meta-instability | Self-modification degrades LES | 5–6 |
| F12 | Safety bypass | Constraint ignored by worker or runtime | all |

---

## Detection

| ID | Signal |
|----|--------|
| F1 | termination_reason always manual or external |
| F2 | same model ID on actor and sole evaluator |
| F3 | LES Effectiveness variance without spec change |
| F4 | validator strict mode failure |
| F5 | downstream human/tool rejects "passed" artifacts |
| F6 | retry succeeds with identical artifact |
| F7 | quality_score zigzag in history |
| F8 | metrics.tokens >> cost_limits.max_tokens |
| F9 | memory read/write conflicts in logs |
| F10 | iteration count stuck, no worker progress |
| F11 | LES monotonic decrease over meta iterations |
| F12 | audit log shows forbidden action |

---

## Remediation Hints

- **F2:** Add evaluator_agent or command eval; maker-checker pattern
- **F4:** Add termination_conditions + cost_limits
- **F7:** Reduce optimization aggressiveness; increase min delta threshold
- **F10:** Add orchestrator timeout; partial order on tasks
- **F11:** Freeze spec mutations; require human approval for Level 5+

---

## Usage in DD-MIS

Diagnose phase: classify incidents with F-IDs before Improve. Track F-ID frequency in production dashboards.

See [framework/diagnose.md](../framework/diagnose.md) and [safety-standard.md](safety-standard.md).
