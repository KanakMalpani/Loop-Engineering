# RFC: LSS 1.1 — Composition Blocks

**Status:** Draft (June 2026)  
**Target:** 2027 standards release per [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md)  
**Author:** Loop Engineering maintainers

---

## Summary

Extend LSS 1.0 with first-class **composition blocks** so loops can declare sequential, parallel, and nested composition without ad hoc orchestration YAML.

---

## Motivation

- P1 establishes loop algebra; LSS 1.0 lacks syntax to express composed loops.
- LE-OP-10 (associativity) needs machine-readable composition for validators and `loop_complexity_analyzer.py`.
- 2027 roadmap exit criterion: "composition LSS 1.1" before intent compiler work.

---

## Proposed additions

```yaml
composition:
  type: sequential | parallel | nested
  children:
    - ref: loop-library/research-agent.yaml
    - ref: loop-library/coding-agent.yaml
  adapters:
    - from: children[0].outputs.Result
      to: children[1].inputs.task
```

### New fields

| Field | Purpose |
|-------|---------|
| `composition.type` | Operator from loop algebra |
| `composition.children` | Ordered list of LSS refs or inline specs |
| `composition.adapters` | Typed glue between child outputs/inputs |
| `evaluators.product_type` | AND / OR / correlated ensemble (LE-OP-06) |

---

## Non-goals (LSS 1.1)

- Intent→LSS compiler (LE-OP-15) — deferred to 2027 research branch
- Breaking changes to existing loop-library specs
- Level 5+ self-modification syntax

---

## Migration

- LSS 1.0 specs remain valid; `composition` is optional.
- Validators warn (not fail) on adapter gaps until LSS 1.1 stable.

---

## Next steps

1. Discussion on GitHub — [Discussion #11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11) (label `rfc`, `lss-1.1`)
2. **Framework maintainers:** LangGraph / CrewAI / Cursor users — does `composition.children` + `adapters` match your graph topology? Comment on #11 or open a PR mapping your harness via [BRIDGE_AGENT_HARNESSES.md](BRIDGE_AGENT_HARNESSES.md).
3. Prototype in Loop Core Engineering `specs/lss-1.1-draft.md`
4. Benchmark composed loop on LB-COMP-1 before merge

---

## References

- [loop-composition-algebra.md](../research/loop-composition-algebra.md)
- [PAPER_SERIES.md](../research/PAPER_SERIES.md) (P1)
- LE-OP-10 in [open-problems.md](../research/open-problems.md)
