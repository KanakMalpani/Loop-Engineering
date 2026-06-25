# LoopNet Schema Changelog

**Scope:** Discipline-side notes for trajectory records consumed by LoopGym replay and LoopNet corpus tooling.

**Canonical schema:** [loopnet/schema/](https://github.com/KanakMalpani/loopnet/tree/main/schema)

---

## v0.3 draft (Phase 6 — June 2026)

| Change | v0.2 | v0.3 (draft) |
|--------|------|--------------|
| Trace import | Manual | `scripts/loopnet_export_trace.py` from Loop Trace 1.0 |
| Source field | — | `metadata.source: loop-trace-1.0` |
| Success flag | Inferred | `metadata.success` from trace |
| Contributor path | HF PR | Trace JSON → row JSON → loopnet PR |

Export locally:

```bash
python scripts/generate_trace_demo.py
python scripts/loopnet_export_trace.py docs/submission-dry-run/trace.json -o row.json
```

Contributor guide: [docs/loopnet/CONTRIBUTING-v0.3.md](../docs/loopnet/CONTRIBUTING-v0.3.md).

**Phase 9 (June 2026):** Schema promoted to sibling repo — [loopnet/schema/record-v0.3.json](https://github.com/KanakMalpani/loopnet/blob/main/schema/record-v0.3.json), `scripts/validate_trace_export.py`, preview row in `data/v0.3-preview/`.

See [LOOP-TRACE-1.0.md](../standards/LOOP-TRACE-1.0.md).

---

| Change | v0.1 | v0.2 |
|--------|------|------|
| Record ID format | `ln-seed-*` | `ln/record-v1` UUID-style |
| Trajectory steps | Flat `steps[]` | `iterations[]` with evaluator vectors |
| LES fields | Optional scalar | `les_vector` eight-category when available |
| Pattern taxonomy | Free string | LSS-aligned `pattern` + `taxonomy_level` |
| Corpus split | Single seed file | Tier 1 public HF + Tier 2 DUA |
| Deprecation | — | `loopnet-seed-v0.1` **do not cite** |

### Migration for contributors

1. Export trajectories with `record_id`, `loop_id`, `pattern`, `taxonomy_level`.
2. Each iteration: `state`, `action`, `evaluator_scores`, `cost_usd` (if known).
3. Terminal: `termination_reason`, `total_cost`, optional `les_vector`.
4. Validate against loopnet repo JSON Schema before PR.

### Discipline repo alignment

| Artifact | Path |
|----------|------|
| Explore script | [examples/loopnet-explore/explore.py](../examples/loopnet-explore/explore.py) |
| Histograms | [docs/loopnet/histograms/](../docs/loopnet/histograms/) |
| Replay env | LoopGym `replay/loopnet-v1` |
| Field helpers | [tools/loopnet_fields.py](../tools/loopnet_fields.py) |

---

## Contributor checklist (discipline side)

Before opening a PR on [loopnet](https://github.com/KanakMalpani/loopnet):

- [ ] Run LoopGym replay smoke on your record subset
- [ ] Confirm `taxonomy_level` matches LSS spec used
- [ ] Include harness + model tier in `metadata`
- [ ] No PHI / secrets in trajectory text
- [ ] Follow [COMMUNITY-SUBMISSION.md](https://github.com/KanakMalpani/loopnet/blob/main/guides/COMMUNITY-SUBMISSION.md)

Post reproduction notes on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10).

---

## Planned v0.3 extensions (beyond flat trace export)

- Composition-aware trajectory linking (`parent_loop_id`, `branch_id`)
- LTF trace cross-reference ([loop-observability](https://github.com/KanakMalpani/loop-observability))
- Tier 2 DUA workflow automation

Flat trace export schema (`record-v0.3.json`) is in preview — see v0.3 draft section above.

See [LOOPNET.md](LOOPNET.md) · [MASTER_CHECKLIST.md](../All%20about%20loops/MASTER_CHECKLIST.md) §3.
