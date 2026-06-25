# Integrate OpenAI Agents SDK

Map [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) sessions to LSS and export a runnable stub.

## Tuple mapping

| LSS | Agents SDK |
|-----|------------|
| **S** | Session + tool context |
| **A** | Agent with tool-calling |
| **O** | Tool results, handoff payloads |
| **E** | Eval hook / rubric agent |
| **M** | Session store |
| **τ** | Max turns, guardrails |

Reference implementation: [implementations/openai_agents/](../../implementations/openai_agents/)

## 15-minute path

```bash
pip install "le-loop-stack>=0.1.0"

loopforge intent "Research topic then reflect until quality threshold" -o agents-mapped.yaml --suggest-level
loopctl validate agents-mapped.yaml
loopctl score --spec agents-mapped.yaml --json
loopforge export --spec agents-mapped.yaml --target openai_agents --out ./agents-export/
python agents-export/run.py --json
```

Optional live SDK (requires `OPENAI_API_KEY`):

```bash
pip install openai-agents
python implementations/openai_agents/reflection_agent.py
```

North star: [NORTH_STAR.md](../NORTH_STAR.md)
