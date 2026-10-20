# Deviation from CRITERION.md

`CRITERION.md` (frozen at `49809bc`, untouched) names suite `suite-repair`, seeds 0-4, scored by the suite's primary LoopBench score in `results.json` (a composite LES score).

The acceptance run instead uses task `LB-CR-1` only (instances `cr-001`, `cr-002`, `cr-003`), seeds 0-4, 10 loops × 3 runs, scored on the raw hidden-test pass rate (mean over instances and seeds), not the composite LoopBench score.

## Why

`suite-repair` = `LB-CR-1`, `LB-REACT-1`, `LB-REFLEX-1`, `LB-OPT-1`, `LB-SAFE-1`.

- `LB-REACT-1` grades with `evaluators.tool_pass_rate`, which does not exist.
- `LB-SAFE-1` uses `safety-constrained-v1` with instances `LB-SAFE-1` / `LB-SAFE-2`, which have no real fixtures and still use the old self-scored runtime.
- `LB-REFLEX-1` and `LB-OPT-1` reuse the same `cr-001`..`003` fixtures.
- The composite score mixes in speed, cost, and robustness and is not a real-outcome score.

## PASS/FAIL

The PASS/FAIL rule is kept as written: in each of the 3 runs, min(GOOD) > max(BAD). Any tie or overlap is a FAIL.

## Status

The result is **PROVISIONAL**.

Decided by Kanak (option a), relayed by Engineering Lead, about 12:06 AM IST on Wed 21 Oct 2026.

Committed before any acceptance result file exists.
