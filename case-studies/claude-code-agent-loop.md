# Case Study: Claude Code Agent Loop

**Domain:** AI agent systems  
**Loop Type:** Terminal-native coding agent with tool loop  
**LES:** 0.76 (medium confidence, structural inference)  
**Primary Sources:** Anthropic Claude Code documentation, practitioner IDE/CLI agent patterns

---

## Tuple mapping

| Component | Instantiation |
|-----------|---------------|
| **S** | CLAUDE.md project rules, open files, shell cwd, MCP server state |
| **A** | File edit, bash, grep/glob, optional MCP tools |
| **O** | Command stdout/stderr, diffs, test results |
| **T** | Tests pass or user `/stop`; else budget halt |
| **E** | Failing tests → next edit strategy; rubric for quality |
| **M** | Session + `.claude/` settings and skills |
| **τ** | Turn budget, API spend, user interrupt |

---

## Integration path

```bash
pip install "le-loop-stack>=0.1.0"
loopforge intent "Fix failing tests from CI with minimal diff" -o claude-mapped.yaml --suggest-level
loopctl score --spec claude-mapped.yaml --json
```

Full guide: [contributions/integrate/CLAUDE_CODE.md](../contributions/integrate/CLAUDE_CODE.md)

Compare with Cursor mapping: [cursor-agent-loop.md](cursor-agent-loop.md)

---

## Related harnesses

| Harness | Case study / bridge |
|---------|---------------------|
| Cursor | [cursor-agent-loop.md](cursor-agent-loop.md) |
| Codex | [integrate/CODEX.md](../contributions/integrate/CODEX.md) |
| Autonomous SWE | [autonomous-coding-agents.md](autonomous-coding-agents.md) |

Contribute external mapping: [Issue #13](https://github.com/KanakMalpani/Loop-Engineering/issues/13)
