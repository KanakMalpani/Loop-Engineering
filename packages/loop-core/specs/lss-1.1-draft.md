# LSS 1.1 Draft — Composition Blocks

**Status:** Draft (June 2026, synced from Loop-Engineering)  
**Supersedes:** nothing (extends LSS 1.0)  
**JSON Schema:** [lss-1.1-composition.schema.json](./lss-1.1-composition.schema.json)  
**Discipline RFC:** [RFC-LSS-1.1-composition](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/RFC-LSS-1.1-composition.md)

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
  adapters:
    - from: children.stage_a.outputs.synthesizer
      to: children.stage_b.inputs.task
  merge:                    # required when type: parallel
    strategy: synthesize
    min_branches_pass: 2
    preserve_dissent: true
```

---

## Validation rules

| Type | Rule |
|------|------|
| sequential | >= len(children)-1 adapters (warn until stable) |
| nested | exactly one outer, >=1 inner, >=1 adapter |
| parallel | merge block required, >=2 branch children |

Reference validator: [composition_validator.py](https://github.com/KanakMalpani/Loop-Engineering/blob/main/tools/composition_validator.py) (`--strict` for hard fail).

---

## Cost guidance

| Type | Bound (informal) |
|------|------------------|
| sequential | C <= C_o + C_1 + C_2 + ... |
| parallel | C <= C_o + sum(C_i) |
| nested | C <= C_out + R * C_in per outer iteration |

See [Lemma 1](https://github.com/KanakMalpani/Loop-Engineering/blob/main/mathematics/composition-cost-bound.md) and [Lemma 2](https://github.com/KanakMalpani/Loop-Engineering/blob/main/mathematics/composition-cost-parallel-nested.md).

---

## Reference specs

| Spec | Type |
|------|------|
| research-to-writing | sequential |
| code-debug-repair | nested |
| scenario-swarm-rehearsal | parallel |

Repository: [loop-library/compositions/](https://github.com/KanakMalpani/Loop-Engineering/tree/main/loop-library/compositions)

---

## Benchmark

LB-COMP-1 (composed swarm rehearsal) on [LoopBench](https://github.com/KanakMalpani/LoopBench) — maintainer LES 77.4.

---

## Migration

- LSS 1.0 validators: pass specs with optional `composition`.
- LSS 1.1 validators: warn on adapter gaps; fail on missing merge for parallel (when `--strict`).

---

## Non-goals

- Intent to LSS compiler (LE-OP-15)
- Level 5+ self-modification syntax
- Breaking renames of LSS 1.0 required fields

---

## Target stable release

Q1 2027 after framework feedback on [Discussion #11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11).
