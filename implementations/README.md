# Implementations

Reference implementations of [LSS](../standards/LSS-1.0.md) loops across frameworks.

---

## Directory Layout

| Path | Framework | Status |
|------|-----------|--------|
| [generic/](generic/) | Framework-agnostic Python runtime | Stable |
| [langgraph/](langgraph/) | LangGraph state graphs | Reference |
| [openai_agents/](openai_agents/) | OpenAI Agents SDK | Reference |
| [crewai/](crewai/) | CrewAI multi-agent crews | Reference |

---

## Generic Runtime

Start here for understanding loop execution without framework dependencies:

```bash
python implementations/generic/examples/run_reflection.py
python EXAMPLES/reflection-loop/run.py
```

Core module: `generic/loop_runtime.py` — inject `MockLLM` or custom LLM client.

---

## Framework Selection

| Need | Choose |
|------|--------|
| Minimal deps, tests, CI | generic |
| Graph visualization, checkpoints | langgraph |
| OpenAI tool use, handoffs | openai_agents |
| Role-based crews, tasks | crewai |

All implementations SHOULD consume the same LSS YAML; divergences must be documented in framework README.

---

## Adding an Implementation

1. Create `implementations/<framework>/README.md`
2. Map LSS workers/evaluators to framework primitives
3. Provide mock mode for CI
4. Link from this README

Validate spec before run:

```bash
python tools/loop_validator.py standards/examples/minimal-loop.yaml
```
