# CrewAI Implementation

Multi-agent research and review loops using [CrewAI](https://github.com/joaomdmoura/crewAI).

---

## Install

```bash
pip install crewai crewai-tools  # optional for live runs
```

---

## Files

| File | Description |
|------|-------------|
| `research_crew.py` | Research synthesis crew (researcher + critic) |

---

## Usage

```python
from research_crew import run_research_crew

result = run_research_crew(
    topic="Loop engineering feedback systems",
    use_mock=True,
)
print(result)
```

---

## LSS Mapping

| LSS | CrewAI |
|-----|--------|
| workers | Agent roles in Crew |
| evaluators | Task output validation / reviewer agent |
| orchestrator | Crew process (sequential/hierarchical) |
| memory | Crew memory / external store |

Example spec: [standards/examples/multi-agent-loop.yaml](../../standards/examples/multi-agent-loop.yaml)

---

## Mock Mode

`use_mock=True` runs deterministic stub tasks aligned with `EXAMPLES/research-loop/run.py` behavior.

---

## When to Use CrewAI

Prefer CrewAI when roles, backstory, and task delegation are first-class. Prefer LangGraph when graph topology and checkpoints dominate. Prefer generic runtime for tests and minimal deps.
