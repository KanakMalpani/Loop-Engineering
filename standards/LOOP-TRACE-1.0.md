# Loop Trace Standard 1.0

**Status:** v1.0 (discipline repo)  
**Schema:** [loop-trace-1.0.schema.json](./schema/loop-trace-1.0.schema.json)

Loop Trace 1.0 is the standard JSON format for **observable loop runs** — one file per episode or run, emitted by LoopGym and consumable by LoopBench for observed LES dimensions.

## Required fields

| Field | Purpose |
|-------|---------|
| `trace_version` | Always `"1.0"` |
| `loop_id` | Stable run identifier (UUID or env episode id) |
| `loop_name` | From LSS `loop_name` |
| `started_at` | ISO-8601 UTC timestamp |
| `iterations` | Array of per-iteration records |

## Iteration record

Each element in `iterations` should include:

- `iteration` — 0-based index
- `timestamp` — ISO-8601 UTC
- `worker_id` — worker that acted (optional for composite steps)
- `evaluator_scores` — map of evaluator id → score
- `cost_usd` — incremental spend for the iteration

## Validate

```bash
python -m loopctl trace validate standards/examples/minimal-trace.json
```

## LoopGym contract

On `env.step()` completion or episode end, LoopGym SHOULD write a trace file matching this schema. See [research/LOOPGYM.md](../research/LOOPGYM.md#loop-trace-10).

## Example

See [examples/minimal-trace.json](./examples/minimal-trace.json).
