# Deviation 2 from CRITERION.md (acceptance attempt 3)

`CRITERION.md`, the 10 loops, fixtures cr-001..cr-003, `DEVIATION.md` and `FROZEN.sha256` are unchanged.
This file adds to `DEVIATION.md`; everything there still applies unless changed below.

## Decision

Kanak decided on Wed 21 Oct 2026, relayed by Engineering Lead:
1. Add harder fixtures that need several iterations, then rerun.
2. Enforce the worker role at the runtime level.

## What is scored

- Task `LB-CR-1` only, not `suite-repair` (same as `DEVIATION.md`).
- Seeds 0, 1, 2, 3, 4.
- Fixtures: cr-001 (calc), cr-002 (stats), cr-003 (text), plus the new cr-004 (durations), cr-005 (intervals), cr-006 (slugs) and cr-007 (money).
- **Per fixture:** the score is the raw hidden-test pass rate (tests passed / tests total) of the patch at the end of that fixture's loop episode. The patch is the last fenced code block of the reply, tagged python or py, or untagged. It is a cost-cap fail (0) if the spec's budget is exceeded.
- **Episode** (one loop, one seed): the plain mean of the 7 per-fixture scores.
- **Loop score for a run:** the mean of the episode scores over the 5 seeds. Seeds that end in INFRA-FAIL after the committed retries are reported separately. They are not scored 0 and not dropped silently.
- Each of the 10 loops is run 3 times, on model `gpt-5.3-codex` via sandboxed `cursor-agent`, capped at 4 calls at once, with the retry policy in `results/acceptance-2/RETRY-POLICY.md`. That policy allows at most 2 retries, and only on infrastructure no-result.
- **Criterion, as written:** PASS only if, in every one of the 3 runs, min(GOOD loop scores) > max(BAD loop scores). Any tie or overlap is a FAIL.
- The result is **PROVISIONAL**, because it deviates from the committed suite and score.

## Harder fixtures

Each BUG.md describes the most visible bug honestly but not completely. The hidden tests also check edge cases that BUG.md doesn't mention. The model learns about those only from failing test names, which arrive as feedback. So the obvious one-line fix still scores below 1.0 (stub-verified in `results/stub-attempt3/`):

| fixture | obvious-fix score |
| --- | --- |
| cr-004 | 0.25 |
| cr-005 | 0.64 |
| cr-006 | 0.42 |
| cr-007 | 0.67 |

## Runtime change: role and temperature

- **Role.** The worker's own spec field is used: `system_prompt` if present, otherwise `role`. For every call it is written into a fresh per-call sandbox workspace, as `AGENTS.md` and `.cursor/rules/role.mdc` (`alwaysApply: true`). It is no longer text inside the user prompt. The user prompt carries only the task: objective, bug description, module, test feedback, and "Return the full corrected module in one fenced code block". It no longer names the role or requires Python. The evaluator scores whatever comes back, so a reply in another language scores 0 honestly. The handling is generic and driven only by spec fields, and it is identical for all 10 loops. No code names a loop, and `packages/loopgym/tests/test_no_loop_names.py` enforces this.
- **Temperature: not applied.** `cursor-agent` has no temperature or system-prompt option (evidence: `evidence/cursor-agent-help.txt`). The spec temperature has been removed from the prompt. It is kept only in the call logs, as `temperature_requested` with `temperature_applied: false`.
- Whether `cursor-agent` actually picks up the rules file is checked by one real probe call, after this file and `FROZEN-2.sha256` are committed.

## Known limitation

The bad loop with the wrong role (rewrite in a different language, temperature 1.8) can still tie the good loops. That happens if the model ignores the rules-file role and returns working Python anyway, because temperature cannot be applied.

## Freeze and logging

- `packages/loopbench/fixtures/FROZEN-2.sha256` pins all fixture files, old and new (28 entries). `packages/loopbench/tests/test_fixtures_frozen2.py` checks it.
- Every model reply is stored in full in the run files (`calls[i].reply`). Every attempt and retry is logged in `run.log`.
- This file and FROZEN-2 are committed before any real-model call against the new fixtures or the new runtime.
