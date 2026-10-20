# LoopNet Labeling Guide

**Version:** 1.0.0  
**Schema:** `ln/record-v1`  
**Failure taxonomy owner:** `01-loop-engineering-core/specs/loop-ids.md`

This guide defines how to label LoopNet records for human annotators and community contributors.

---

## 1. When to create a record

Create a LoopNet record when you have:

1. A complete loop run (or bounded partial run) with iteration-level telemetry
2. A known or inferable outcome (`success`, `failure`, `partial`)
3. No secrets, API keys, or unredacted PII in the payload

**Do not submit** raw production logs without consent and redaction.

---

## 2. Required labels

| Label | Rule |
|-------|------|
| `outcome` | `success` if goal met within budget; `failure` if terminated without meeting goal; `partial` if meaningful progress but human/budget stop |
| `termination_reason` | Pick the closest enum value (see schema) |
| `failure_mode` | **Required for `outcome=failure`**. Single primary `fail.*` slug |
| `failure_modes` | All applicable `fail.*` slugs observed in trajectory or postmortem |
| `patterns` | One or more pattern slugs; outermost safety wrapper first |

---

## 3. Choosing `failure_mode`

Use the **root cause**, not the symptom:

| Symptom | Likely `failure_mode` |
|---------|----------------------|
| Loop ran forever / no termination | `fail.tau_omission` or `fail.open_loop` |
| Agent graded its own output as passing | `fail.self_grade` |
| Evaluator scores drift from human judgment | `fail.evaluator_drift` |
| Passed checks but output wrong | `fail.false_pass` |
| Failed checks despite good output | `fail.false_fail` |
| Scores oscillate without convergence | `fail.oscillation` |
| Cost exceeded `cost_limits` | `fail.resource_bleed` |
| Memory/context inconsistent across iterations | `fail.state_corruption` |
| Multi-agent wait cycle | `fail.orchestration_deadlock` |
| Self-modification degraded quality | `fail.meta_instability` |
| Safety constraint bypassed | `fail.safety_bypass` |

If multiple modes apply, pick the earliest causal failure as `failure_mode`; list all in `failure_modes`.

---

## 4. Trajectory labeling

Each iteration must include:

- `iteration` — 1-based index
- `goal_score` — `G_t` in `[0, 1]` per case study goal function
- `cost_usd` — iteration spend
- `latency_seconds` — wall-clock duration

Optional but recommended:

- `primary_quality` — primary evaluator score
- `failure_codes` — `fail.*` slugs detected this iteration
- `safety_events` — count of safety constraint triggers
- `human_intervention` — `true` if human edited or approved

---

## 5. LES fields

- `les_observed` — computed from actual run metrics (see `les@1.0.0`)
- `les_predicted` — optional; design-time or model estimate only

Report `partial: true` when Robustness is excluded (fewer than 3 perturbations).

---

## 6. Redaction checklist

Before submission:

- [ ] Remove API keys, tokens, credentials
- [ ] Remove customer names, emails, account IDs
- [ ] Replace proprietary code with structural summaries if needed
- [ ] Set `redaction.level` to `basic` or `full`
- [ ] List removed fields in `redaction.fields_removed`

---

## 7. Community submission (v1.0)

Submission pipeline (form + validation hook) ships in v1.0. For v0.1, open a PR adding JSONL lines to `data/seed/` and run:

```bash
python scripts/validate_record.py data/seed/your-records.jsonl
```

---

## 8. Quality bar

- Failed loops are **more valuable** — prioritize labeling failed trajectories
- Minimum 3 iterations unless termination was immediate error
- `failure_mode` must be consistent with `trajectory[].failure_codes` when present
