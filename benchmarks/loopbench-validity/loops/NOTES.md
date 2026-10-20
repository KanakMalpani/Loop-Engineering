# Loop set

- `good-1-fast`: GOOD: upstream reference spec-fast-loop, unchanged
- `good-2-thorough`: GOOD: upstream reference spec-thorough-loop, unchanged
- `good-3-fast-5iter`: GOOD: fast loop with 5 iterations instead of 3
- `good-4-thorough-t0`: GOOD: thorough loop with implementer at temperature 0
- `good-5-fast-strict`: GOOD: fast loop with stricter 0.85 quality bar
- `bad-1-no-feedback`: BAD: no feedback channel and 1 iteration, so the loop cannot repair
- `bad-2-no-tests`: BAD: deterministic test evaluator removed; only the rubric judges
- `bad-3-wrong-role`: BAD: implementer told to rewrite the file in another language at temperature 1.8
- `bad-4-no-bug-input`: BAD: implementer never receives the bug description
- `bad-5-starved-budget`: BAD: cost cap of $0.001 halts before a patch can finish
