# Organizational Intelligence Systems

*Applying Loop Engineering at team and enterprise scale*

Organizations already run feedback loops — standups, retros, OKR cycles, incident reviews. Most are **implicit, unmeasured, and non-composable**. Loop Engineering provides a path to **explicit LSS specs for org processes**, scored with LES, and safe to scale.

---

## Org Loop Tuple

Map organizational learning to L = (S, A, O, T, E, M, τ):

| Symbol | Org mapping |
|--------|-------------|
| S | Shared state: docs, tickets, metrics dashboards |
| A | Teams / roles executing work |
| O | Observations: KPIs, customer feedback, audits |
| T | Decision policies: prioritization, approval gates |
| E | Evaluators: QA, compliance, customer success |
| M | Institutional memory: wikis, postmortems, CRM |
| τ | Cycle end: sprint, quarter, audit period |

---

## Patterns

### Incident response loop (Level 2–3)

- **Workers:** Responder, comms lead
- **Evaluators:** Timeline completeness, customer impact rubric
- **τ:** Severity-based SLA

### Strategy loop (Level 2)

- **Workers:** Strategy team
- **Evaluators:** Market signal checklist, finance guardrails
- **τ:** Quarterly review

### Hiring loop (Level 3)

- **Workers:** Recruiter, interview panel (parallel)
- **Evaluators:** Rubric scores, bar-raiser veto
- **τ:** Offer or reject

---

## Governance

- Org loops need **safety_constraints** (HR, legal, privacy) like AI loops
- **cost_limits** map to headcount and meeting time
- LES **Robustness** captures process survival under turnover

---

## Anti-Patterns

- **Dashboard theater** — metrics without evaluators tied to decisions
- **Retro without τ** — discussion without state update
- **Implicit loops** — "we've always done it this way" with no spec

---

## Implementation Path

1. Document top 3 recurring processes as LSS
2. Measure one LES dimension per quarter
3. Separate evaluator role (e.g., QA, audit) where actors self-grade
4. Compose sub-loops (hiring ⊕ onboarding) per [loop-composition-algebra.md](loop-composition-algebra.md)

See [framework/scale.md](../framework/scale.md) for fleet deployment patterns.
