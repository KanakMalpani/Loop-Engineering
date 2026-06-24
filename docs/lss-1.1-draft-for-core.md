# LSS 1.1 Draft — Composition Blocks

**Status:** Draft (June 2026)  
**Canonical home:** Loop Core Engineering  
**Discipline RFC:** [Loop-Engineering RFC-LSS-1.1-composition](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/RFC-LSS-1.1-composition.md)

---

## Summary

Optional extension to LSS 1.0. All LSS 1.0 documents remain valid without a `composition` block.

---

## New top-level field

```yaml
composition:
  type: sequential | parallel | nested
  children:
    - id: stage_a
      ref: loop-library/research-agent.yaml
      role: stage | branch | outer | inner
      lens: "Optional prompt prefix for parallel branches"
      trigger: "Optional inner invocation condition (nested)"
  adapters:
    - from: children.stage_a.outputs.synthesizer
      to: children.stage_b.inputs.task
  merge:                    # required when type: parallel
    strategy: consensus_rubric
    min_branches_pass: 2
    preserve_dissent: true
    synthesizer: workers.orchestrator
```

---

## Validation rules (draft)

| Type | Rule |
|------|------|
| sequential | ≥ `len(children)-1` adapters |
| nested | exactly one `outer`, ≥1 `inner`, ≥1 adapter |
| parallel | `merge` block required, ≥2 `branch` children |

Reference implementation: [composition_validator.py](https://github.com/KanakMalpani/Loop-Engineering/blob/main/tools/composition_validator.py)

---

## Reference specs (Loop-Engineering)

| Spec | Type |
|------|------|
| research-to-writing | sequential |
| startup-to-strategy | sequential |
| code-debug-repair | nested |
| research-code-nest | nested |
| scenario-swarm-rehearsal | parallel |

---

## Migration

- LSS 1.0 validators: **pass** specs with unknown top-level keys (`additionalProperties: true`).
- LSS 1.1 validators: **warn** on adapter gaps; **fail** on missing merge for parallel.

---

## Non-goals

- Intent→LSS compiler (LE-OP-15)
- Level 5+ self-modification syntax
- Breaking renames of LSS 1.0 required fields

---

## Next

1. JSON Schema fragment for `composition` in `schema/lss-1.1.schema.json`
2. Normative merge after LoopBench composed-task baseline
