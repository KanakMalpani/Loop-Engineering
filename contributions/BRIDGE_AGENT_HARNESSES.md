# Bridge: Agent Harnesses → LSS

You already run a feedback loop. Loop Engineering gives it a **name, spec, and score** — no new runtime required.

**Adoption path:** Map your harness → post on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) using [REPRODUCE.md](REPRODUCE.md) (≤60 min).

**Integration hub:** [integrate/README.md](integrate/README.md) · **One-line install:** `pip install "le-loop-stack>=0.1.0"`

---

## Quick mapping

| Harness | Typical S | Typical A | Typical O | LSS example in repo |
|---------|-----------|-----------|-----------|---------------------|
| **Claude Code** | CLAUDE.md + repo | Edit/bash/MCP | Test/diff output | [integrate/CLAUDE_CODE.md](integrate/CLAUDE_CODE.md) · [claude-code-agent-loop](../case-studies/claude-code-agent-loop.md) |
| **OpenAI Codex** | Repo + tests | Edit/run | CI pass/fail | [integrate/CODEX.md](integrate/CODEX.md) |
| **Cursor Agent** | Chat + repo context | Edit/test tools loop | User accept + tests | [integrate/CURSOR.md](integrate/CURSOR.md) · [cursor-agent-loop](../case-studies/cursor-agent-loop.md) |
| **LangGraph** | Graph state | Node workers | Conditional edges / critic node | [langgraph-composition-bridge](../case-studies/langgraph-composition-bridge.md) |
| **CrewAI** | Crew memory | Role agents | Task output review | [crewai-composition-bridge](../case-studies/crewai-composition-bridge.md) |
| **OpenAI Agents SDK** | Session | Tool-calling agent | Eval hook | [integrate/OPENAI_AGENTS.md](integrate/OPENAI_AGENTS.md) |
| **Aider** | Git + chat | LLM edits | Test output | [integrate/AIDER.md](integrate/AIDER.md) |
| **Gemini CLI** | Project context | Tool use | Command output | [integrate/GEMINI_CLI.md](integrate/GEMINI_CLI.md) |
| **GitHub Copilot** | IDE context | Suggested edits | Build/test | [integrate/COPILOT.md](integrate/COPILOT.md) |
| **Windsurf** | IDE + cascade | Edit/run | Linter/tests | Map via [Issue #7](https://github.com/KanakMalpani/Loop-Engineering/issues/7) |
| **Devin / SWE-agent** | Repo + issue | Plan/code/test | Test suite | [integrate/DEVIN.md](integrate/DEVIN.md) · [autonomous-debugger](../loop-library/autonomous-debugger.yaml) |

Full tuple: **L = (S, A, O, T, E, M, τ)** — see [case-studies/TEMPLATE.md](../case-studies/TEMPLATE.md).

---

## Tracing and observability

| Path | When to use |
|------|-------------|
| **Loop Trace 1.0** (default) | `loopgym>=0.1.2` emits trace JSON; `loopctl observed` |
| **loopotel / LTF** (optional) | [loop-observability](https://github.com/KanakMalpani/loop-observability) spans for OTel pipelines |

No repo merge required — Loop Trace from LoopGym is the default Golden Path.

---

## Good-first entry points

| Issue | For |
|-------|-----|
| [#13 Map Claude Code loop to LSS](https://github.com/KanakMalpani/Loop-Engineering/issues/13) | Claude Code users |
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
