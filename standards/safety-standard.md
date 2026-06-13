# Loop Safety Standard

Minimum safety requirements for LSS specifications by taxonomy level and deployment context.

---

## Severity Levels

| Severity | Meaning | Example |
|----------|---------|---------|
| critical | Must never violate; halt loop | No production writes without approval |
| high | Violation triggers immediate τ | PII exfiltration blocked |
| medium | Log and retry with backoff | Rate limit exceeded |
| low | Advisory; human review | Style guideline |

---

## Required Constraints by Level

| Level | Minimum safety_constraints |
|-------|---------------------------|
| 1 | 1 constraint (scope boundary) |
| 2 | 2 constraints including output bounds |
| 3 | 3 constraints + evaluator separation |
| 4 | 4 constraints + rollback policy |
| 5 | 5 constraints + human gate on spec mutation |
| 6 | Charter + containment + kill switch |

---

## Mandatory Patterns

### Maker-checker (Level 3+)

Actor worker MUST NOT be sole model evaluator on same artifact.

### Kill switch

Runtime MUST honor external halt signal and set `termination_reason: safety_halt`.

### Cost envelope

`cost_limits` REQUIRED for any loop with Autonomy LES > 50.

### Audit trail

`memory` or external store MUST persist iteration history for Level 4+.

---

## Constraint Schema (LSS)

```yaml
safety_constraints:
  - id: no_prod_writes
    rule: "Workers must not write to production databases"
    severity: critical
    enforcement: runtime_block
```

---

## Review Process

- Level 1–2: one reviewer
- Level 3–4: two reviewers including security
- Level 5–6: RFC + 30-day review + red team exercise

Validator strict mode checks presence of safety_constraints and cost_limits:

```bash
python tools/loop_validator.py spec.yaml --strict
```

---

## Mapping to LES

Safety dimension in LES weights constraint count, severity coverage, and enforcement type. See [scoring/LES-1.0.md](../scoring/LES-1.0.md).

Related failures: [failure-taxonomy.md](failure-taxonomy.md) F12, F11, F8.
