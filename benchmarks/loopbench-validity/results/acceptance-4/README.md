# Acceptance attempt 4: ABANDONED (infrastructure), NOT GRADED

- **Started:** 2026-10-21T14:14:08+05:30, runner PID 47998. See `preflight/` for the freeze checks, the leak probe (0 lines leaked) and the role-pickup probe (picked up).
- **Stopped:** 2026-10-21T17:07:35+05:30. By Engineering Lead's decision, the runner's process group (47998) and the pusher (49226) were stopped.
- **Status:** abandoned as an infrastructure failure. No criterion verdict and no grade. All files are kept as they were.
- **State at stop:** 16 of 30 run files written.

## Why: process_error surge

The first `process_error` in `run.log` is at 16:34:40 IST (`good-2-thorough/r0 call=65`). From then on, the runner's cursor-agent calls failed with process errors at a growing rate.

`run.log` outcome counts:

| snapshot | ok | process_error | timeout |
|---|---|---|---|
| final, at stop | 435 | 161 | 10 |
| `add524f` (14/30 push) | 435 | 118 | 8 |

The figures relayed to me were 435 / 136 / 10. They match neither snapshot exactly, probably because they were taken between the two.

## INFRA-FAIL seeds

These are seeds that still had no result after the 2 committed retries.

At `add524f`, QA bot found INFRA-FAIL seeds in 8 of the 14 run files. In the final 16 files, 10 have INFRA-FAIL seeds:

| run file | INFRA-FAIL seeds |
|---|---|
| bad-1-no-feedback-r1 | 0–4 |
| bad-2-no-tests-r1 | 0–4 |
| bad-3-wrong-role-r1 | 0–4 |
| bad-4-no-bug-input-r0 | 3, 4 |
| bad-4-no-bug-input-r1 | 0–4 |
| bad-5-starved-budget-r1 | 0–4 (written after `add524f`) |
| good-1-fast-r1 | 0–4 (written after `add524f`) |
| good-2-thorough-r0 | 3, 4 |
| good-4-thorough-t0-r0 | 1–4 |
| good-5-fast-strict-r0 | 0–4 |

The process_error cause is under investigation, read-only. Evidence is in `/workspace/concurrency-investigation/` on the box.
