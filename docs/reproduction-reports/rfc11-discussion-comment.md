## RFC LSS 1.1 — maintainer synthesis (2026-06-24)

Summary of decisions while awaiting framework-maintainer feedback:

| Topic | Decision |
|-------|----------|
| Backward compatibility | `composition` optional; LSS 1.0 unchanged |
| Parallel | `merge` required; `preserve_dissent` for rehearsal patterns |
| Adapters | Warn by default; strict mode fails |
| Cost limits | Parent cap = sum per Lemma 1/2 |
| Harness mapping | [Cursor case study](https://github.com/KanakMalpani/Loop-Engineering/blob/main/case-studies/cursor-agent-loop.md) |

**Artifacts synced to Loop-Core:**
- [specs/lss-1.1-draft.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.1-draft.md)
- [specs/lss-1.1-composition.schema.json](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.1-composition.schema.json)

**Question for LangGraph / CrewAI / Cursor users:** Does `composition.children` + `adapters` match your graph/crew topology? Reply here with a minimal YAML mapping.

Full RFC: [RFC-LSS-1.1-composition.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/RFC-LSS-1.1-composition.md)
