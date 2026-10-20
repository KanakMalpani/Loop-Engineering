# Failure taxonomy (LSS 1.0)

**Canonical codes:** [`loop-ids.md` §2](loop-ids.md#2-failure-taxonomy-codes) (F1–F12 slugs).

**Narrative guide:** `Loop Engineering/standards/failure-taxonomy.md` (discipline mirror — qualitative descriptions, detection signals, remediation).

## Usage in LSS

Emit failure slugs on structured feedback channels:

```yaml
feedback_channels:
  - id: eval_to_worker
    source: evaluators.quality_rubric
    destination: workers.summarizer
    format: structured
    fields: [failure_codes, dimension_scores, remediation_hints]
```

## Code quick reference

| Code | Slug | Severity |
|------|------|----------|
| F4 | `fail.tau_omission` | Critical — missing termination/budget |
| F8 | `fail.resource_bleed` | Critical — exceeds `cost_limits` |
| F12 | `fail.safety_bypass` | Critical — safety constraint ignored |
| F2 | `fail.self_grade` | High — actor grades own output |
| F7 | `fail.oscillation` | Medium — non-converging iterations |

Do not invent ad-hoc failure strings in production telemetry; extend via RFC (new F13+).
