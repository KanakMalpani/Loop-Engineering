# RFC-NNNN: [Title]

| Field | Value |
|-------|-------|
| **Status** | Draft / Review / Accepted / Rejected / Superseded |
| **Author(s)** | |
| **Created** | YYYY-MM-DD |
| **Target spec** | `lss` / `les` / `loop-ids` / other |
| **Semver impact** | MAJOR / MINOR / PATCH |

## Summary

One paragraph: what changes and why.

## Motivation

What problem does this solve? Link issues, incidents, or benchmark gaps.

## Specification

Concrete normative changes (schema diff, formula change, new ID table rows).

### Before

```yaml
# or JSON schema excerpt
```

### After

```yaml
# proposed state
```

## Compatibility

- Breaking for consumers? List repos (`04-loopnet`, `05-loopgym`, …).
- Migration steps for existing LSS YAML / LoopNet records.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| A | | |
| B | | |

## Test plan

- [ ] Schema validates existing examples
- [ ] New fixtures added
- [ ] Downstream contract tests updated

## References

- Related RFCs
- Discipline docs in `Loop Engineering`
