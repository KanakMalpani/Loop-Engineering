# LSS 1.0 — Loop Specification Standard

**Version:** 1.0.0  
**Status:** Stable  
**Schema:** [`lss-1.0.schema.json`](./lss-1.0.schema.json)

LSS 1.0 is the canonical machine- and human-readable format for specifying autonomous agent loops. A conforming document declares workers, evaluators, feedback routing, termination, metrics, safety, and cost envelopes.

LSS documents are YAML or JSON validated against the JSON Schema in this directory.

---

## Design principles

1. **Completeness** — Thirteen required top-level fields; no implicit defaults that hide risk.
2. **Boundedness** — Every loop must terminate via `termination_conditions` or `cost_limits`.
3. **Safety-first** — `safety_constraints` evaluated before trusting outputs.
4. **Observability** — `metrics` tie to evaluators and telemetry, not aspirations.
5. **Version discipline** — Document `version` follows semver; changes are auditable.

---

## Required fields

| Field | Purpose |
|-------|---------|
| `loop_name` | Stable kebab-case identifier |
| `version` | Semver of this spec document |
| `objective` | Declarative outcome statement |
| `inputs` | Per-invocation input schema |
| `memory` | Ephemeral, session, or persistent state |
| `workers` | Agents that produce artifacts (min 1) |
| `evaluators` | Quality judges (min 1) |
| `feedback_channels` | Evaluator → worker/optimizer routing (min 1) |
| `optimization_strategy` | How the loop improves across iterations |
| `termination_conditions` | Success, failure, and stall rules |
| `metrics` | Quantitative health measures (min 1) |
| `safety_constraints` | Hard invariants (required array; may be empty in dev) |
| `cost_limits` | Financial and token budgets |

Full field reference and examples live in the discipline repo: `Loop Engineering/standards/LSS-1.0.md`. **This repo owns the schema**; narrative docs may mirror there until Option A/B (single source of truth) is decided.

---

## Validation

```bash
python tools/validate_lss.py examples/minimal-loop.yaml
python tools/validate_all_examples.py
```

Schema-only validation uses JSON Schema Draft 2020-12. Recommended semantic checks (DAG acyclicity, reference integrity) are documented in LSS-1.0 narrative.

---

## Conformance levels

| Level | Requirements |
|-------|--------------|
| **LSS-Parseable** | Schema valid |
| **LSS-Operational** | + metrics collection + cost_limits enforced at runtime |
| **LSS-Production** | + non-empty safety_constraints + evaluator calibration + runbook |

---

## Version pin

Consumers pin: **`lss@1.0.0`** → `specs/lss-1.0.schema.json`

See [CHANGELOG.md](../CHANGELOG.md) for semver policy.

---

## Examples

| File | Description |
|------|-------------|
| [`examples/minimal-loop.yaml`](../examples/minimal-loop.yaml) | Smallest valid loop |
| [`examples/research-loop.yaml`](../examples/research-loop.yaml) | Research brief pipeline |
| [`examples/multi-agent-loop.yaml`](../examples/multi-agent-loop.yaml) | Multi-agent review DAG |
