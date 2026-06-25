# LoopNet v0.3 contributor path

**Status:** Draft (Phase 7) · **Schema:** Loop Trace 1.0 → LoopNet row  
**Canonical schema repo:** [KanakMalpani/loopnet](https://github.com/KanakMalpani/loopnet)

---

## Overview

LoopNet v0.3 accepts trajectories exported from **Loop Trace 1.0** documents. Contributors no longer hand-author iteration rows from scratch.

```mermaid
flowchart LR
  A[Run loop] --> B[Loop Trace JSON]
  B --> C[loopctl trace validate]
  C --> D[loopnet_export_trace.py]
  D --> E[LoopNet row JSON]
  E --> F[HF / loopnet PR]
```

---

## Prerequisites

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" "loopgym>=0.1.2"
```

---

## Step 1 — Produce a Loop Trace

**Option A — LoopGym (recommended):**

```python
import loopgym as lg

env = lg.make("loopbench/code-repair-v1")
result = env.run_episode(task_id="cr-001", seed=42, trace_path="trace.json")
```

**Option B — Generic runtime smoke:**

```bash
python scripts/generate_trace_demo.py
# → docs/submission-dry-run/trace.json
```

---

## Step 2 — Validate trace

```bash
loopctl trace validate trace.json
loopctl observed trace.json --spec path/to/your-spec.yaml --json
```

---

## Step 3 — Export LoopNet row

```bash
python scripts/loopnet_export_trace.py trace.json \
  --pattern verification-loop \
  -o loopnet-row.json
```

Required metadata fields (v0.3 draft):

| Field | Source |
|-------|--------|
| `metadata.source` | `loop-trace-1.0` |
| `metadata.schema_version` | `0.3-draft` |
| `metadata.success` | trace `success` |
| `metadata.iteration_count` | len(`iterations`) |

See [LOOPNET-SCHEMA-CHANGELOG.md](../research/LOOPNET-SCHEMA-CHANGELOG.md).

---

## Step 4 — Submit to LoopNet

1. Fork [loopnet](https://github.com/KanakMalpani/loopnet)
2. Add row JSON under contributor path (see loopnet repo `CONTRIBUTING.md`)
3. Open PR referencing your Loop Trace + LSS spec

**Reference dry-run:** [docs/submission-dry-run/](../submission-dry-run/) (maintainer-generated, not external adoption)

---

## Maintainer dry-run

Regenerate the full path:

```bash
python scripts/run_submission_dryrun.py
```

Produces: spec YAML, trace, observed LES, LoopNet row, `summary.json`.

---

## Related

- [LOOP-TRACE-1.0.md](../standards/LOOP-TRACE-1.0.md)
- [BEAT_TEMPLATE.md](../contributions/BEAT_TEMPLATE.md)
- [GOLDEN_PATH.md](../contributions/GOLDEN_PATH.md)
