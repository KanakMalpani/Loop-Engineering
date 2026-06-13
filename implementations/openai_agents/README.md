# OpenAI Agents Implementation

Reflection loops using the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) pattern.

---

## Install

```bash
pip install openai openai-agents  # optional for live runs
```

---

## Usage

```python
from reflection_agent import run_reflection_agent

result = run_reflection_agent(
    objective="Fix failing tests",
    task="Debug the login module",
    use_mock=True,
)
print(result.output)
```

Set `use_mock=False` and export `OPENAI_API_KEY` for live runs.

---

## LSS Mapping

| LSS | Agents SDK |
|-----|------------|
| workers | Agent definitions with instructions |
| evaluators | Separate agent or tool-based checks |
| handoffs | Agent transfer for maker-checker |
| cost_limits | max_turns / external budget wrapper |

---

## Mock Mode

Default mock enables CI and EXAMPLES without API keys. Mock responses follow the same iteration structure as `MockLLM` in `generic/loop_runtime.py`.

---

## Safety

Apply [safety-standard.md](../../standards/safety-standard.md): separate evaluator agent from implementer; never self-grade on critical paths.
