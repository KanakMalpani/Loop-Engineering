# LoopNet Seed Corpus — Data Card (v0.1)

**Dataset name:** LoopNet Seed v0.1  
**Schema version:** `ln/record-v1`  
**Created:** 2026-06-13  
**Records:** 500 (synthetic)  
**License:** CC BY 4.0

---

## Motivation

Loop Engineering needs ground-truth data for loop planning, failure prediction, and LES estimation. LoopNet is the canonical dataset layer — analogous to ImageNet for vision.

This v0.1 seed corpus establishes the record schema, labeling conventions, and baseline splits. It is **synthetic** with known ground truth; production and community records arrive in v1.0.

---

## Composition

| Split | Records | Share |
|-------|---------|-------|
| train | 400 | 80% |
| val | 50 | 10% |
| test | 50 | 10% |

| Outcome | Target share (v0.1 actual) |
|---------|----------------------------|
| failure | ≥40% |
| success | ~48% |
| partial | ~10% |

| Source (v0.1) | Share |
|---------------|-------|
| synthetic | 100% |

**v1.0 target mix:** 40% synthetic, 20% case study, 20% redacted production, 20% community.

---

## Record fields

Each JSONL line is one `ln/record-v1` record:

| Field | Description |
|-------|-------------|
| `record_id` | `ln-{uuid}` stable identifier |
| `patterns` | Pattern slugs from core registry |
| `objective` | Declarative loop goal |
| `loop_spec` | Optional LSS design snapshot |
| `outcome` | `success`, `failure`, or `partial` |
| `termination_reason` | Why the loop stopped |
| `failure_mode` | Primary `fail.*` slug (failures) |
| `failure_modes` | All observed failure slugs |
| `trajectory` | Per-iteration goal, cost, latency telemetry |
| `les_observed` | LES-1.0 composite + 8 categories |
| `metadata` | Aggregates (cost, regressions, budgets) |

Full schema: [`schema/loopnet-record-v1.json`](schema/loopnet-record-v1.json)

---

## Failure taxonomy

Labels align with [`01-loop-engineering-core/specs/loop-ids.md`](../01-loop-engineering-core/specs/loop-ids.md):

| Slug | Name |
|------|------|
| `fail.open_loop` | Open loop |
| `fail.self_grade` | Self-grade |
| `fail.evaluator_drift` | Evaluator drift |
| `fail.tau_omission` | τ omission |
| `fail.false_pass` | False pass |
| `fail.false_fail` | False fail |
| `fail.oscillation` | Oscillation |
| `fail.resource_bleed` | Resource bleed |
| `fail.state_corruption` | State corruption |
| `fail.orchestration_deadlock` | Orchestration deadlock |
| `fail.meta_instability` | Meta instability |
| `fail.safety_bypass` | Safety bypass |

---

## Intended uses

- Train/evaluate failure-mode classifiers from early trajectory windows
- Calibrate LES predictors against observed trajectories
- Bootstrap LoopGym replay environments (`lg/replay/loopnet-v1`)
- Research on loop convergence and cost efficiency

## Out of scope

- Running live loops (see `05-loopgym`)
- Leaderboard scoring (see `06-loopbench`)

---

## Known limitations (v0.1)

- All records are synthetic; trajectories are simulated, not from production runs
- `loop_spec` snapshots are abbreviated, not full LSS documents
- `les_observed` uses heuristic category inference, not full benchmark perturbation suites
- No PII; `redaction.level` is always `none` for synthetic records

---

## Validation

```bash
python scripts/validate_record.py --require-count 500
```

Checks: JSON Schema conformance, unique `record_id`, ≥40% failure rate.

---

## Regeneration

```bash
python scripts/generate_seed.py --count 500 --seed 42
```

Deterministic with `--seed 42`.

---

## Citation

```bibtex
@dataset{loopnet_seed_v01,
  title={LoopNet Seed Corpus v0.1},
  author={Loop Engineering},
  year={2026},
  schema={ln/record-v1}
}
```

---

## Changelog

| Version | Change |
|---------|--------|
| 0.3-preview | Loop Trace 1.0 flat export schema (`record-v0.3.json`), validate_trace_export.py, dry-run preview row |
| 0.1.0 | Initial schema, 500 synthetic records, validation tooling |
