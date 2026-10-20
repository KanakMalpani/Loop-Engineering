# B result: FAIL (measured short run, NOT the committed 30-run test)

Run 20 Oct 2026 ~9:45 PM IST. Criterion and loop set unchanged since `49809bc`.
Scope cut per Kanak (minutes, not hours): 2 loops, task LB-CR-1, seed 0, 1 run each.
Model: cursor-agent `--model gpt-5.3-codex-low-fast`, via `cursor_llm.py`. MockLLM patched to raise; never constructed (`llm_class: CursorAgentLLM` in each log).

| Loop | quality_score | success | LLM calls | seconds |
|---|---|---|---|---|
| good-1-fast | 0.92 | True | 2 | 31.9 |
| bad-2-no-tests (test evaluator removed) | 0.99 | True | 4 | 68.8 |

The bad loop outscored the good one, so the criterion (every good > every bad) fails.

## Why (code evidence, loopgym `runtime/loop_runtime.py`)
- Score = the number the model writes in its own critique, then `+ 0.12 × iteration + 0.05`, capped at 0.99. More iterations wins regardless of quality.
- Spec evaluators, feedback channels, inputs and cost limits are never read by the runtime.
- `evaluators.test_pass_rate` reads `mock_pass_rate`, which nothing sets; no real tests run.
- `live` backend: never received an injected LLM (fixed in wiring commit), and `LiveEnv` has no `run_episode`, so LoopBench's live path cannot run as shipped.

## Caveats
- cursor-agent is an agent wrapper (Cursor's system prompt and routing), not a raw model.
- n=1 per loop; this shows the failure mode, not a distribution.

## Redesign (proposed, not built)
1. Score from deterministic evaluators running real task tests in a sandbox (test_pass_rate, type_clean, diff_score as the task's goal scalar says); the model critique becomes feedback only. ~1.5 days.
2. Honour spec fields: inputs into prompts, feedback channels routed to workers, cost_limits and max_iterations enforced. ~1 day.
3. Real model in `live`: provider from the spec's `model:` block, `LiveEnv.run_episode`, mock refusal in live mode. ~0.5 day.
4. Re-run the committed 10-loop criterion. Total ~3–4 days.
Fallback: if not funded, drop LoopBench scores from the demo and README and label the leaderboard experimental.
