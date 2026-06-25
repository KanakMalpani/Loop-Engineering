# LE-OP-10 composition counterexamples

Intentionally **invalid associativity** fixtures. Daily CI runs [scripts/check_composition_counterexamples.py](../../scripts/check_composition_counterexamples.py) to assert expected validator warnings (non-strict).

| Fixture | Expected warning theme |
|---------|-------------------------|
| `parallel-first-wins.yaml` | `first_wins` order-sensitive merge |
| `sequential-no-adapters.yaml` | sequential adapter gap |
| `nested-no-adapters.yaml` | nested without adapters |

Do **not** copy these into production specs. See [research/le-op-10-associativity.md](../../research/le-op-10-associativity.md).
