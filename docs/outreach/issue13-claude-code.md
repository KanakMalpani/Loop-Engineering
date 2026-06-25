# Good first: Map Claude Code loop to LSS (Issue #13)

Use this template when opening or commenting on GitHub issue **#13**.

## Title

`[Good first] Map Claude Code loop to LSS case study`

## Body

```markdown
## Harness

Claude Code (terminal agent)

## Tuple (S, A, O, T, E, M, τ)

| LSS | Your Claude Code instantiation |
|-----|--------------------------------|
| S | |
| A | |
| O | |
| T | |
| E | |
| M | |
| τ | |

## Reproduction (≤60 min)

\`\`\`bash
pip install "le-loop-stack>=0.1.0"
loopforge intent "YOUR LOOP" -o mapped.yaml --suggest-level
loopctl validate mapped.yaml
loopctl score --spec mapped.yaml --json
\`\`\`

Guide: https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/integrate/CLAUDE_CODE.md

## Deliverable

- PR adding or extending `case-studies/claude-code-agent-loop.md`
- Optional: comment on Discussion #10 with trace-native repro
```

Maintainer: create issue via GitHub UI if #13 does not exist yet.
