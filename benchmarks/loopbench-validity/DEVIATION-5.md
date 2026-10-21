# DEVIATION-5 (QA rulings applied; to be frozen as FROZEN-5): attempt return codes, leak-probe records, model-report limit

Status: QA rulings applied; frozen in FROZEN-5.sha256 (FROZEN-4 at f3755e3 is superseded once the FROZEN-5 gate passes).

## 1. Return code recorded on every attempt (`cursor_llm.py`)
- Every attempt record gains `returncode` (int; `None` on timeout), `rc_nonzero` (returncode not in {0, None}) and `clean` (outcome ok AND returncode 0). The `calls.jsonl`/log line gains ` rc=<value>`.
- Every call record gains `returncode` (final attempt) and `rc_nonzero` (any attempt).
- Behaviour unchanged: a parsed reply with is_error false and a non-zero exit is still final (outcome `ok`, no retry). It is now flagged `rc_nonzero: true, clean: false` and must not be counted as a clean call in trials or runs.
- QA ruling (a): the launch preflight (leak and role probes) and every future counted trial require `clean: true` on every attempt; for attempt 5, any call with outcome ok and a non-zero exit (`rc_nonzero: true`) makes its run ungradable, treated the same as INFRA-FAIL.
- Closes the gap found in c8-pull-1/c8-2/c8-3 (no exit-code field).

## 2. Leak probe records (`leak_probe.py`)
- Built with `log_path=results/leak-probe.log`, `run_id="leak-probe"` (same mechanism as `role_probe.py`): per-call stderr file in `results/stderr/`, reaper lines in `results/reap.log` under the per-attempt tag.
- Output JSON gains `calls` and, from the last attempt, `stderr_path`, `stderr_bytes`, `returncode`, `reap_tag`, `reap_kills`, `leftover_worker_servers`, `leftover_tagged`, plus `reap_log`. New `--out` option (default unchanged path). Existing keys and exit codes unchanged.
- Closes the gap found in the FROZEN-4 probe rerun (no stderr/reap record for leak_probe).

## 3. Known limit: model_reported unavailable (accepted, QA ruling (c))
- cursor-agent 2026.10.19-6bbf2c4 with `--output-format json` does not emit any model field (see `notes-model-report.md` and `evidence/model-report-2026.10.19-6bbf2c4/`). `model_reported` is therefore always `null`.
- Accepted wording: "The model is verified by pin, not by report: `model_requested` is hard-pinned to `grok-4.7-high` (no env override), the CLI version is pinned and checked at launch, and the CLI rejects unknown slugs before any request. `model_reported` is unavailable from this CLI version and is recorded as null. `model_check` checks `model_requested` only (as it already does) and does not use `model_reported`." QA ruling (c): any non-null `model_reported` that differs from the pinned model invalidates the run.
- Ruling (c) is a written rule checked by QA bot from the call records; it is not code-enforced (`calls_model_check` checks `model_requested` only). With this CLI version `model_reported` is always null, so the rule cannot trigger in attempt 5; it exists for any future CLI that reports a model.
- `model_announced` (stream-json `system/init.model`) is not built.

## 4. Launch memory check and pull plan for attempt 5 (Engineering Lead; pull plan only)
- Launch check: enforced in `run_full.py` (`check_launch_memory`), checked exactly once at startup before any model call, never mid-run; requires MemAvailable >= 4096 MB; logs available MB and IST time to results/launch-memcheck.log (and the summary/probe JSON) on both PASS and ABORT; aborts below 4096 MB. Tests: `packages/loopgym/tests/test_launch_memory_check.py` (4095 aborts, 4096/4097 pass).
- Pull plan during attempt 5: the AE pull (/workspace/oa/pull) stays at 3 workers (pull.sh v7, sha256 6aaab5ab027ed5372fb69c036ad2fe62c0cbeecb324f8afc127da3495c6150ca); no worker switch during the run.
- Memory watcher: `tools/pull-watch/mem_watch.sh`, sha256 44458a7e4023c92bb47f51dc565db1f86c4d34d13bc9fc02e4625d2b9de5af03 (committed; NOT in the FROZEN-5 manifest; not started until attempt-5 launch is approved). It polls MemAvailable every 10 s and finds the pull's process group (`bash pull.sh` with cwd /workspace/oa/pull).
  - Below 3072 MB: PAUSE. It lists the parts in flight, `kill -STOP -- -<pgid>`, writes `<IST> PAUSE mem-watch available_mb=<MB> pgid=<pgid> in_flight=<n>` to pull.log, and deletes each in-flight part's raw, partial output and hist files, logging `<IST> <id> re-pulled after mem-watch PAUSE ...` per part.
  - Above 4096 MB while paused: RESUME. It `kill -KILL -- -<pgid>` (the stopped group), waits for it to exit, deletes in-flight partials again (logged per part), restarts `setsid nohup bash pull.sh` exactly like switch_v6/v7, writes the new PID to raw/pull-pid, and logs `<IST> RESUME mem-watch available_mb=<MB> old_pgid=<pgid> new_pid=<pid> paused_s=<s>`.
  - In-flight parts are never resumed mid-download: they are deleted and re-pulled from scratch by the restarted pull.sh (done parts are skipped), consistent with the SNAPSHOT rules for worker switches. A PAUSE/RESUME is not a worker switch; pull.sh and its sha are unchanged.
  - `DRY_RUN=1` logs `DRY-RUN` lines and sends no signals, deletes nothing, restarts nothing. Test: `tools/pull-watch/test_mem_watch.sh` (temp fake pull dir and dummy process group only; both cases PASS, log `tools/pull-watch/test-run-*-IST.log`).

## Tests
- `packages/loopgym/tests/test_returncode_records.py`: rc 0 ok -> clean; rc 3 with valid JSON -> reply returned, no retry, outcome ok, rc_nonzero true, clean false, call rc_nonzero true; earlier non-zero attempt marks call; timeout -> returncode null.
- `packages/loopgym/tests/test_leak_probe_records.py`: stubbed leak_probe main writes the new fields, LLM built with results-dir log_path and run_id "leak-probe".
- `packages/loopgym/tests/test_launch_memory_check.py`: MemAvailable parse; 4095 MB aborts `main` before any LLM; 4096 and 4097 MB pass; `results/launch-memcheck.log` records available_mb and IST (+05:30) on PASS and ABORT; probe `main` calls the check once.

## Before FROZEN-5
QA review of this draft and the code; FROZEN-5 manifest (FROZEN-4 set with new cursor_llm.py + leak_probe.py + run_full.py, + DEVIATION-5.md, + FROZEN-4.sha256); clean-worktree gate; probe rerun. FROZEN-5 needs its own probe rerun (both probes clean) and one counted 8-concurrent trial (c8-f5) on the FROZEN-5 worktree.

Code changes written by cursor-agent `--model grok-4.7-high` (/workspace/f5-agent/prompt1.txt, prompt3.txt, prompt4.txt, prompt5.txt; agent1/3/4/5b.out) and reviewed by SWE.
