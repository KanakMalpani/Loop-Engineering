# Integrate Claude Code agent loops

Map [Claude Code](https://docs.anthropic.com/en/docs/claude-code) sessions to LSS without replacing your terminal workflow.

## Tuple mapping

| LSS | Claude Code |
|-----|-------------|
| **S** | CLAUDE.md project context + open files + shell state |
| **A** | Edit, bash, search, MCP tool calls |
| **O** | Command output, diffs, test results |
| **E** | User approval, CI, rubric you define |
| **M** | Session + `.claude/` settings + skills |
| **τ** | Max turns, budget, `/stop` |

Case study: [claude-code-agent-loop.md](../case-studies/claude-code-agent-loop.md)

## CLAUDE.md snippet

Add to your repo root:

```markdown
## Loop Engineering

When changing agent loops, map to LSS and score before large refactors:

\`\`\`bash
pip install "le-loop-stack>=0.1.0"
loopforge intent "YOUR LOOP IN ENGLISH" -o mapped.yaml --suggest-level
loopctl validate mapped.yaml && loopctl score --spec mapped.yaml --json
\`\`\`

Guide: https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/integrate/CLAUDE_CODE.md
```

## 15-minute path

```bash
pip install "le-loop-stack>=0.1.0"

loopforge intent "Fix failing tests from CI with minimal diff" -o claude-mapped.yaml --suggest-level
loopctl validate claude-mapped.yaml
loopctl score --spec claude-mapped.yaml --json
loopctl pipeline --intent "Fix failing tests from CI" -o claude-mapped.yaml --run-loopgym --json
```

## Good-first issue

Contribute your mapping: [#13 Map Claude Code loop to LSS](https://github.com/KanakMalpani/Loop-Engineering/issues/13)

North star: [NORTH_STAR.md](../NORTH_STAR.md)
