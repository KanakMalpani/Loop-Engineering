# LE-OP-04 Evaluator Composition Benchmark (v0.1)

Three merge policies on synthetic evaluator scores (0–1 scale). Demonstrates false-pass rate when evaluators double-count overlapping dimensions.

| Scenario | Policy | Expected false-pass |
|----------|--------|---------------------|
| `naive_and` | All evaluators must pass independently | Lower false-pass, higher false-continue |
| `double_count_avg` | Weighted average with overlapping dims (invalid) | Inflated pass rate |
| `partition_merge` | Disjoint dimensions + single merge gate | Baseline per [le-op-04-evaluator-composition.md](../../research/le-op-04-evaluator-composition.md) |

Run:

```bash
python scripts/run_evaluator_composition_demo.py
```

Reference spec: [scenario-swarm-rehearsal.yaml](../../loop-library/compositions/scenario-swarm-rehearsal.yaml)
