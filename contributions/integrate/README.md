# Integration hub — agent harnesses

Map your existing agent loop to LSS, score it, and optionally export — **without rewriting your runtime**.

**Install (one line):**

```bash
pip install "le-loop-stack>=0.3.0"
```

**Golden Path:** [GOLDEN_PATH.md](../GOLDEN_PATH.md) · **North star:** [NORTH_STAR.md](../NORTH_STAR.md)

---

## Harness packs

| Harness | Type | Guide | Demo |
|---------|------|-------|------|
| **Claude Code** | Map + score | [CLAUDE_CODE.md](./CLAUDE_CODE.md) | [integrate-claude-code](../../examples/integrate-claude-code/) |
| **OpenAI Codex** | Map + score | [CODEX.md](./CODEX.md) | [integrate-codex](../../examples/integrate-codex/) |
| **OpenAI Agents SDK** | Export stub | [OPENAI_AGENTS.md](./OPENAI_AGENTS.md) | [integrate-openai-agents](../../examples/integrate-openai-agents/) |
| **LangGraph** | Export stub | [langgraph-composition-bridge](../case-studies/langgraph-composition-bridge.md) | [integrate-langgraph](../../examples/integrate-langgraph/) |
| **CrewAI** | Export stub | [crewai-composition-bridge](../case-studies/crewai-composition-bridge.md) | [integrate-crewai](../../examples/integrate-crewai/) |
| **Cursor** | Map in IDE | [CURSOR.md](./CURSOR.md) | [cursor-agent-loop](../case-studies/cursor-agent-loop.md) |
| **Aider** | Map + score | [AIDER.md](./AIDER.md) | [integrate-aider](../../examples/integrate-aider/) |
| **Gemini CLI** | Map + score | [GEMINI_CLI.md](./GEMINI_CLI.md) | [integrate-gemini](../../examples/integrate-gemini/) |
| **GitHub Copilot** | Bridge | [COPILOT.md](./COPILOT.md) | — |
| **Devin / OpenHands** | Bridge | [DEVIN.md](./DEVIN.md) | [autonomous-coding-agents](../case-studies/autonomous-coding-agents.md) |

Full mapping table: [BRIDGE_AGENT_HARNESSES.md](../BRIDGE_AGENT_HARNESSES.md)

---

## Export targets

```bash
loopforge export --spec my-loop.yaml --target generic|langgraph|crewai|openai_agents --out ./export/
```

---

## Community

| Goal | Link |
|------|------|
| Reproduction report | [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) |
| External case study | [Issue #7](https://github.com/KanakMalpani/Loop-Engineering/issues/7) |
| Claude Code mapping | [Issue #13](https://github.com/KanakMalpani/Loop-Engineering/issues/13) |
| LoopBench row | [Issue #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) |
