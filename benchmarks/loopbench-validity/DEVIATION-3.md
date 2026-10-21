# Deviation 3 from CRITERION.md (acceptance attempt 5)

`CRITERION.md`, `DEVIATION.md`, `DEVIATION-2.md`, `FROZEN.sha256` and `FROZEN-2.sha256` are unchanged.
This file adds to `DEVIATION-2.md`; everything there still applies unless changed below.
**Status: DRAFT for QA bot review. Not frozen. Nothing may run under it yet.**

## Decision

Kanak's standing rule, relayed by Engineering Lead on Wed 21 Oct 2026: all engineering work uses only Grok or Composer models (never `*-fast`). Attempt 5 therefore moves off `gpt-5.3-codex`.

## Model and runtime pin

- **Model:** `grok-4.7-high`, exactly. It is passed explicitly as `--model grok-4.7-high` on every call. `cursor_llm.DEFAULT_MODEL` is hard-pinned to `grok-4.7-high` with no environment override; there is no fallback to any default model (the `cursor-agent` default or otherwise). A call record whose `model` is not exactly `grok-4.7-high` invalidates the run.
- **cursor-agent version:** `2026.10.19-6bbf2c4` (output of `cursor-agent --version` on the box, 21 Oct 2026). The version is recorded again at launch; if it differs, the run does not start until a deviation entry covers it.
- **Why grok-4.7-high and not Composer:** it matches AE's already-pinned LLM baseline (one model across both projects) and it is the model the concurrency-recipe probe trials already run on, so the recipe is verified on the same model the run uses.

## Comparability

Scores from attempt 5 are **NOT comparable** with attempts 1-4 (all `gpt-5.3-codex`). They are reported on their own and are never pooled, differenced or trended against earlier attempts.

## Unchanged from FROZEN-2

The pass criterion (PASS only if, in every one of the 3 runs, min(GOOD) > max(BAD); any tie or overlap is FAIL), the 10 loops, fixtures cr-001..cr-007, task `LB-CR-1`, seeds 0-4, 3 runs, the per-fixture/episode/loop scoring, the 150 s timeout and the retry cap (at most 2 retries, infrastructure no-result only, per `results/acceptance-2/RETRY-POLICY.md`) are all **unchanged from `FROZEN-2`**. The result remains PROVISIONAL.

## Per-call stderr

- Every `cursor-agent` call saves its own stderr to its own per-call file, including each retry and each probe call.
- A failed call (process_error, timeout, INFRA-FAIL) with no saved stderr file, or an empty one, counts as an **unexplained failure**. The run report lists every unexplained failure; the run cannot be signed off with one unexplained.

## Concurrency

Any concurrency recipe used (cap above 4, reaper, or other worker-server handling) must first be verified by QA bot from the docs, and is named here by commit before the re-freeze. Without a verified recipe, the cap stays at 4.

## Before launch (in order)

1. QA bot accepts this file.
2. Re-freeze: a new freeze commit that adds this file and a new hash file (covering this file, the runner, `cursor_llm.py`, loops and fixtures). The freeze commit and hash file must precede launch.
3. After the re-freeze, rerun the read-only leak probe and the role rules-file pickup probe on `grok-4.7-high`, with stderr saved. Both must pass.
4. Record `cursor-agent --version`, HEAD, and the freeze hashes at launch.
