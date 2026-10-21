# DEVIATION-5 (DRAFT, NOT FROZEN): attempt return codes, leak-probe records, model-report limit

Status: draft for QA bot. Nothing frozen; FROZEN-4 (f3755e3) stays the attempt-5 baseline until a FROZEN-5 is gated.

## 1. Return code recorded on every attempt (`cursor_llm.py`)
- Every attempt record gains `returncode` (int; `None` on timeout), `rc_nonzero` (returncode not in {0, None}) and `clean` (outcome ok AND returncode 0). The `calls.jsonl`/log line gains ` rc=<value>`.
- Every call record gains `returncode` (final attempt) and `rc_nonzero` (any attempt).
- Behaviour unchanged: a parsed reply with is_error false and a non-zero exit is still final (outcome `ok`, no retry). It is now flagged `rc_nonzero: true, clean: false` and must not be counted as a clean call in trials or runs.
- Trial criterion addition proposed: a counted trial requires every attempt `clean: true`; any `rc_nonzero` attempt fails the trial unless its stderr explains it.
- Closes the gap found in c8-pull-1/c8-2/c8-3 (no exit-code field).

## 2. Leak probe records (`leak_probe.py`)
- Built with `log_path=results/leak-probe.log`, `run_id="leak-probe"` (same mechanism as `role_probe.py`): per-call stderr file in `results/stderr/`, reaper lines in `results/reap.log` under the per-attempt tag.
- Output JSON gains `calls` and, from the last attempt, `stderr_path`, `stderr_bytes`, `returncode`, `reap_tag`, `reap_kills`, `leftover_worker_servers`, `leftover_tagged`, plus `reap_log`. New `--out` option (default unchanged path). Existing keys and exit codes unchanged.
- Closes the gap found in the FROZEN-4 probe rerun (no stderr/reap record for leak_probe).

## 3. Known limit: model_reported unavailable (for QA bot to decide)
- cursor-agent 2026.10.19-6bbf2c4 with `--output-format json` does not emit any model field (see `notes-model-report.md` and `evidence/model-report-2026.10.19-6bbf2c4/`). `model_reported` is therefore always `null`.
- Proposed wording: "The model is verified by pin, not by report: `model_requested` is hard-pinned to `grok-4.7-high` (no env override), the CLI version is pinned and checked at launch, and the CLI rejects unknown slugs before any request. `model_reported` is unavailable from this CLI version and is recorded as null. `model_check` checks `model_requested` only (as it already does) and does not use `model_reported`." Open question for QA bot: should a future non-null `model_reported` that differs from the pin invalidate a run? Not implemented.
- Alternative (not implemented): switch to stream-json and record `system/init.model` as `model_announced` (client-side display name, e.g. "Grok 4.7 256K High"; not server proof).

## Tests
- `packages/loopgym/tests/test_returncode_records.py`: rc 0 ok -> clean; rc 3 with valid JSON -> reply returned, no retry, outcome ok, rc_nonzero true, clean false, call rc_nonzero true; earlier non-zero attempt marks call; timeout -> returncode null.
- `packages/loopgym/tests/test_leak_probe_records.py`: stubbed leak_probe main writes the new fields, LLM built with results-dir log_path and run_id "leak-probe".

## Before FROZEN-5
QA review of this draft and the code; FROZEN-5 manifest (FROZEN-4 set with new cursor_llm.py + leak_probe.py, + DEVIATION-5.md, + FROZEN-4.sha256); clean-worktree gate; probe rerun. Whether the 3 counted trials (run on FROZEN-4) carry over is QA bot's call.

Code changes written by cursor-agent `--model grok-4.7-high` (/workspace/f5-agent/prompt1.txt, agent1.out) and reviewed by SWE.
