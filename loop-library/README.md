# Loop Library

Production-ready **LSS 1.0** atomic loops plus **LSS 1.1 draft** composed loops (loops inside loops).

## Atomic loops (9)

| Loop | Level | Domain | LES Est. |
|------|-------|--------|----------|
| [Research Agent](./research-agent.yaml) | 2 | Literature synthesis | 78 |
| [Coding Agent](./coding-agent.yaml) | 3 | Feature implementation | 82 |
| [Autonomous Debugger](./autonomous-debugger.yaml) | 3 | Test-driven repair | 85 |
| [Scientific Discovery Agent](./scientific-discovery-agent.yaml) | 4 | Hypothesis testing | 71 |
| [Business Strategy Agent](./business-strategy-agent.yaml) | 3 | Strategic planning | 76 |
| [Startup Validator](./startup-validator.yaml) | 2 | PMF experiments | 74 |
| [Learning Coach](./learning-coach.yaml) | 2 | Adaptive tutoring | 80 |
| [Interview Coach](./interview-coach.yaml) | 2 | Interview prep | 77 |
| [Writing Assistant](./writing-assistant.yaml) | 2 | Long-form composition | 79 |

## Composed loops (5)

Nested, sequential, and **parallel** pipelines in [`compositions/`](compositions/README.md):

| Composition | Type | Power |
|-------------|------|-------|
| [scenario-swarm-rehearsal](./compositions/scenario-swarm-rehearsal.yaml) | **parallel** | MiroFish-style worldview rehearsal → merged forecast |
| [code-debug-repair](./compositions/code-debug-repair.yaml) | **nested** | Code → auto-debug on failure |
| [research-code-nest](./compositions/research-code-nest.yaml) | **nested** | Research → prototype code |
| [research-to-writing](./compositions/research-to-writing.yaml) | sequential | Brief → polished doc |
| [startup-to-strategy](./compositions/startup-to-strategy.yaml) | sequential | PMF → strategy memo |

```bash
python scripts/validate_loop_library.py
python examples/compose-loop/run.py loop-library/compositions/code-debug-repair.yaml
```

## Validate and score

```bash
python scripts/validate_loop_library.py          # 9 atomic + 5 composed
python tools/les_calculator.py --spec loop-library/coding-agent.yaml
python tools/composition_validator.py --library
```

**Note:** `research-agent` models Citation Verifier as an evaluator, not a worker.

See [standards/LSS-1.0.md](../standards/LSS-1.0.md) and [RFC-LSS-1.1-composition.md](../contributions/RFC-LSS-1.1-composition.md).

## Composition rules

1. Each child loop keeps its own evaluators — no merged oracles.
2. Adapters declare explicit `from`/`to` paths between children.
3. Nested loops invoke inner children only on outer failure (e.g. test suite fail).

## Contributing

New atomic loops need YAML + companion `.md`. New compositions need a clear adapter graph and entry in `compositions/README.md`.

See [contributions/CONTRIBUTING.md](../contributions/CONTRIBUTING.md).
