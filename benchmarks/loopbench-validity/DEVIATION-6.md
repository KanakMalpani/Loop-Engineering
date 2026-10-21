# DEVIATION-6 (FROZEN-6): attempt-5 startup floor 6144 MB, explicit concurrency 5

Status: ACCEPTED - QA PASS at 04:33 IST 2026-10-22 (reviewed d82cf3a, bce9f60); frozen in FROZEN-6.sha256.

Everything in `DEVIATION.md`, `DEVIATION-2.md`, `DEVIATION-3.md`, `DEVIATION-4.md` and `DEVIATION-5.md` still applies unless changed below. Nothing else changes vs FROZEN-5. `FROZEN-6.sha256` freezes this deviation. The change is now applied to canonical `benchmarks/loopbench-validity/run_full.py` and `packages/loopgym/tests/test_launch_memory_check.py`, with `drafts/frozen6` kept as the review record. `cursor_llm.py` is not edited here.

## 1. Startup memory floor (`run_full.py`)

- `MIN_AVAILABLE_MB` changes from 4096 to 6144. That is the only change in the runner.
- `check_launch_memory` is unchanged in behaviour otherwise: it runs exactly once at startup, before any model call, and never mid-run. It requires MemAvailable >= 6144 MB, logs available MB and IST time to `results/launch-memcheck.log` (and the summary/probe JSON) on both PASS and ABORT, and aborts below 6144 MB.
- Draft under review: `benchmarks/loopbench-validity/drafts/frozen6/run_full.py`, an exact copy of the FROZEN-5 `run_full.py` except `MIN_AVAILABLE_MB = 6144`.
- Tests for this draft: `drafts/frozen6/test_launch_memory_check.py` (loads that file; 6143 MB aborts, 6144 MB passes). The change is now applied to canonical `benchmarks/loopbench-validity/run_full.py` and `packages/loopgym/tests/test_launch_memory_check.py`, with `drafts/frozen6` kept as the review record.

## 2. Attempt 5 launches with explicit `--max-concurrency 5`

- The attempt-5 launch command passes `--max-concurrency 5` on the command line.
- That value equals the argparse default in `run_full.py` (`ap.add_argument("--max-concurrency", type=int, default=5)`). Passing it explicitly does not change the runner relative to omitting the flag. It is passed explicitly so the counted launch does not depend on the default staying 5.
- Model remains `grok-4.7-high`, passed as `--model grok-4.7-high`.
- Exact command and preconditions: `drafts/frozen6/LAUNCH-RECIPE-attempt5.md`.

## Rationale and margin

- Eight concurrent calls need about 3.5 GB.
- The harness running guard trips when MemAvailable is under 1229 MB.
- The c8-f5 rerun (commit `90654d4`) launched from 4692 MB and breached at 1130 MB (`results/trials-freeze5/c8-f5-rerun/`: pre-launch recheck 4692 MB, guard breach availMB=1130). Eight calls from a 4692 MB start do not clear the 1229 MB guard.
- Attempt 5 uses 5 calls, not 8. Five calls need about 2200 MB. Margin at the new floor: 6144 − ~2200 MB = ~3944 MB left, about 2700 MB above the 1229 MB guard.

## Unchanged vs FROZEN-5

Return-code records, leak-probe records, the model-report limit, the pull plan (3 workers, no switch), the memory watcher, the model pin (`grok-4.7-high`), the cursor-agent pin (`2026.10.19-6bbf2c4`), task `LB-CR-1`, seeds 0-4, 3 runs, the 150 s timeout, the retry cap, and the pass criterion are unchanged. `cursor_llm.py` is unchanged.

## Harness floor (not part of FROZEN-5)

`results/trials-freeze5/harness-5b/run_trial5b.sh` default `MIN_MB` changes from 4096 to 6144. `MIN_MB` in the environment still overrides it. The 60 s sustained hold and the pre-launch recheck both compare MemAvailable to `MIN_MB`. This file is harness-only, as in the c8-f5 guard notes, and is not a FROZEN-5 manifest entry.

## Tests

- `benchmarks/loopbench-validity/drafts/frozen6/test_launch_memory_check.py`: loads `drafts/frozen6/run_full.py`; MemAvailable parse at the new floor (6291456 kB -> 6144, 6291455 kB -> 6143); 6143 MB aborts `main` before any LLM; 6144 and 6145 MB pass; `results/launch-memcheck.log` records available_mb, required_mb=6144, and IST (+05:30) on PASS and ABORT; probe `main` calls the check once.
- `results/trials-freeze5/harness-5b/test_run_trial5b.sh`: existing cases kept; with `MIN_MB` unset, fake MemAvailable 5000 MB fails the default floor (exit 4, memory not sustained) and 7000 MB passes (`memory sustained >=6144`, pre-launch recheck PASS).

## Before FROZEN-6

QA review of this draft and of `drafts/frozen6/run_full.py`. Do not write `FROZEN-6.sha256` until that review accepts the deviation. Nothing may launch under this draft until then. After acceptance, the freeze is the FROZEN-5 set with `run_full.py` replaced by the 6144-floor copy, plus this file. Probe rerun and the counted attempt-5 launch stay behind that gate, using `LAUNCH-RECIPE-attempt5.md`.
