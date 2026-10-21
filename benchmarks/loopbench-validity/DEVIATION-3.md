# Deviation 3 from CRITERION.md (acceptance attempt 5)

`CRITERION.md`, `DEVIATION.md`, `DEVIATION-2.md`, `FROZEN.sha256` and `FROZEN-2.sha256` are unchanged.
This file adds to `DEVIATION-2.md`; everything there still applies unless changed below.
**Status: DRAFT for QA bot review. Not frozen. Nothing may run under it yet.**

## Decision

Kanak's standing rule, relayed by Engineering Lead on Wed 21 Oct 2026: all engineering work uses only Grok or Composer models (never `*-fast`). Attempt 5 therefore moves off `gpt-5.3-codex`.

## Model and runtime pin

- **Model:** `grok-4.7-high`, exactly. It is passed explicitly as `--model grok-4.7-high` on every call. `cursor_llm.DEFAULT_MODEL` is hard-pinned to `grok-4.7-high` with no environment override; there is no fallback to any default model (the `cursor-agent` default or otherwise). Every call record carries `model_requested` and `model_reported` (the model cursor-agent reports, or null if it reports none). `run_full.py` refuses to launch an acceptance run with `--model` other than `grok-4.7-high`, and its summary `model_check` invalidates the run (criterion pass forced false) if any call's `model_requested` is not exactly `grok-4.7-high`. An empty model name raises an error instead of falling back to the cursor-agent default.
- **cursor-agent ignores the frozen loop specs' `model` field** (e.g. `gpt-4.1-mini` in `loops/*.yaml`); the requested model is always `grok-4.7-high`, enforced by a test. The loop specs are left untouched.
- **cursor-agent binary:** pinned to `~/.local/bin/cursor-agent`. At launch the runner and both probes record the resolved path and `cursor-agent --version` (`launch_identity`) and abort if the version is not `2026.10.19-6bbf2c4`.
- **Probes:** the leak probe (`leak_probe.py`) and `run_full.py --probe` refuse any model other than `grok-4.7-high`, record `model_requested`/`model_reported` per call, and fail if any call mismatches. The role rules-file pickup probe (`role_probe.py`) applies the same checks and saves per-call stderr.
- **Other runtime pins:** `CURSOR_LLM_INFRA_RETRIES` (2) and `CURSOR_LLM_ISOLATE` (on) are pinned in `cursor_llm.py` like the model. Any of `CURSOR_LLM_MODEL`, `CURSOR_LLM_INFRA_RETRIES`, `CURSOR_LLM_ISOLATE` or `CURSOR_AGENT_BIN` set in the environment makes the shim and the runner abort, so a stale override can never take effect or be silently ignored.
- **cursor-agent version:** `2026.10.19-6bbf2c4` (output of `cursor-agent --version` on the box, 21 Oct 2026). The version is recorded again at launch; if it differs, the run does not start until a deviation entry covers it.
- **Why grok-4.7-high and not Composer:** it matches AE's already-pinned LLM baseline (one model across both projects) and it is the model the concurrency-recipe probe trials already run on, so the recipe is verified on the same model the run uses.

## Comparability

Scores from attempt 5 are **NOT comparable** with attempts 1-4 (all `gpt-5.3-codex`). They are reported on their own and are never pooled, differenced or trended against earlier attempts.

## Unchanged from FROZEN-2

The pass criterion (PASS only if, in every one of the 3 runs, min(GOOD) > max(BAD); any tie or overlap is FAIL), the 10 loops, fixtures cr-001..cr-007, task `LB-CR-1`, seeds 0-4, 3 runs, the per-fixture/episode/loop scoring, the 150 s timeout and the retry cap (at most 2 retries, infrastructure no-result only, per `results/acceptance-2/RETRY-POLICY.md`) are all **unchanged from `FROZEN-2`**. The result remains PROVISIONAL.

## Per-call stderr

- Every `cursor-agent` call saves its own stderr to its own per-attempt file (`<outdir>/stderr/<run>-call<i>-attempt<n>.stderr`), including each retry and each probe call; the path is stored in the call record as `stderr_path`.
- A failed call (process_error, timeout, INFRA-FAIL) with no saved stderr file, or an empty one, counts as an **unexplained failure**. The run report lists every unexplained failure; the run cannot be signed off with one unexplained.

## Concurrency

**No launch without a QA-verified concurrency recipe.** The recipe (concurrency cap and worker-server handling) must be verified by QA bot from the docs and is named here by commit before the re-freeze. There is no fallback configuration: without a verified recipe, attempt 5 does not launch.
- **No reaper is part of attempt 5** until QA bot signs off the trial results. The files under `tools/reaper/` (committed in `3d7bca4` as a prototype, not wired into the runner) are unverified and are not named by the freeze.

## Before launch (in order)

1. QA bot accepts this file.
2. Re-freeze: a new freeze commit that adds this file and a new hash file (covering this file, the runner, `cursor_llm.py`, loops and fixtures). The freeze commit and hash file must precede launch.
3. After the re-freeze, rerun the read-only leak probe (`leak_probe.py`) and the role rules-file pickup probe (`role_probe.py`) on `grok-4.7-high`, with stderr saved. Both must pass.
4. Freeze-gate tests run from a clean `git worktree` at the freeze commit (not the working checkout, whose ignored `__pycache__/` dirs under fixtures break `test_working_copy_contains_only_src`; nothing is deleted). QA bot can use `/workspace/le-venv/bin/pytest`.
5. Record `cursor-agent --version`, the resolved binary path, HEAD, and the freeze hashes at launch.
