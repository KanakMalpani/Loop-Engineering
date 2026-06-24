# Bridge: Agent Harnesses → LSS

You already run a feedback loop. Loop Engineering gives it a **name, spec, and score** — no new runtime required.

**Adoption path:** Map your harness → post on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) using [REPRODUCE.md](REPRODUCE.md) (≤60 min).

---

## Quick mapping

| Harness | Typical S | Typical A | Typical O | LSS example in repo |
|---------|-----------|-----------|-----------|---------------------|
| **Cursor Agent** | Chat + repo context | Edit/test tools loop | User accept + tests | [cursor-agent-loop](../case-studies/cursor-agent-loop.md) · [coding-agent](../loop-library/coding-agent.yaml) |
| **LangGraph** | Graph state | Node workers | Conditional edges / critic node | [langgraph-composition-bridge](../case-studies/langgraph-composition-bridge.md) · [langgraph/](../implementations/langgraph/) |
| **CrewAI** | Crew memory | Role agents | Task output review | [crewai/](../implementations/crewai/) |
| **OpenAI Agents SDK** | Session | Tool-calling agent | Eval hook | [openai_agents/](../implementations/openai_agents/) |
| **Devin / SWE-agent** | Repo + issue | Plan/code/test | Test suite | [autonomous-debugger](../loop-library/autonomous-debugger.yaml) |

Full tuple: **L = (S, A, O, T, E, M, τ)** — see [case-studies/TEMPLATE.md](../case-studies/TEMPLATE.md).

---

## Good-first entry points

| Issue | For |
|-------|-----|
| [#8 Map Cursor loop to LSS](https://github.com/KanakMalpani/Loop-Engineering/issues/8) | Cursor users |
| [#4 Reproduce LB-CR-1](https://github.com/KanakMalpani/Loop-Engineering/issues/4) | `loopbench` users |
| [#7 External case study](https://github.com/KanakMalpani/Loop-Engineering/issues/7) | Any harness not in catalog |

---

## Composed loops (multi-agent)

If you run **parallel branches** (e.g. MiroFish-style rehearsal) or **nested repair**, see [loop-library/compositions/](../loop-library/compositions/) — especially [scenario-swarm-rehearsal](../loop-library/compositions/scenario-swarm-rehearsal.md).

```bash
python examples/compose-loop/run.py loop-library/compositions/scenario-swarm-rehearsal.yaml
```

---

## Cite

[contributions/CITATION.md](CITATION.md) · [ECOSYSTEM_VERSIONS.md](../ECOSYSTEM_VERSIONS.md)
