# Deviation 4 (NOT FROZEN): tag-based reaper wired into the attempt-5 shim

**NOT FROZEN. DRAFT for QA bot review.** This file is not covered by `FROZEN-3.sha256`. Nothing may run under it until `FROZEN-4.sha256` is committed.
Everything in `DEVIATION.md`, `DEVIATION-2.md` and `DEVIATION-3.md` still applies unless changed below. The pass criterion, loops, fixtures, task, seeds, runs, timeout, retry cap, model pin (`grok-4.7-high`), cursor-agent version pin (`2026.10.19-6bbf2c4`), fixed binary path, abort-on-set env vars and per-attempt stderr files are unchanged.

## Why

QA bot signs off concurrency trials only if they run through the exact code path attempt 5 uses. Before this change, the reaper prototype was a wrapper reached through `CURSOR_AGENT_BIN`, which DEVIATION-3 now forbids. The reaper therefore moves into `cursor_llm.py` itself. This replaces DEVIATION-3's statement that "no reaper is part of attempt 5": the in-shim reaper defined here is part of attempt 5 once FROZEN-4 is committed and the trials are signed off.

## Reaper (ported from `tools/reaper/`, commits `3d7bca4` and `060b0c7`; design notes in `/workspace/concurrency-investigation/03-reaper.md`)

- **Always on.** There is no environment variable or flag to turn it off or change it.
- **Tag.** Every attempt gets a unique tag `CURSOR_REAP_TAG=lbreap-<uuid4 hex>`. It is set in the child environment and passed to bwrap with `--setenv`, so cursor-agent and every descendant inherit it, including the worker-server.
- **Reap.** After every attempt ends (ok, error, timeout or exception), and after the process group is SIGKILLed on a timeout, the shim waits `REAP_SETTLE_S` (1 s). It then SIGKILLs only processes whose `/proc/<pid>/environ` contains that exact tag entry, re-checking the tag immediately before each kill. Untagged processes are never touched. So are unreadable or vanished ones, and the shim's own process.
- **Logging.** The per-run reap log (`<outdir>/reap.log`, next to `run.log`) gets one `START` line per attempt, one `KILL pid=<pid> tag=<tag> call=<run>-call<i>-attempt<n> cmd=…` line per kill, and a `DONE … reaped=<n>` line.
- **Records.**
  - Each attempt record holds `reap_tag`, `reap_kills`, `leftover_tagged` and `leftover_worker_servers`.
  - Each call record holds `reap_kills` and `leftover_worker_servers` (both summed over attempts) and `reap_log`.
- **Pipe-hang fix** (`trial/aborted-tee`: a lingering worker-server kept the stderr pipe open, so callers hung until timeout). stdout and stderr now go to real files, not pipes: stderr straight to the per-attempt stderr file, stdout to a temp file in the call's workspace. stdin is `/dev/null`, the process gets a new session, and the shim uses `wait(timeout)`, not `communicate()`.
- **Gaps.**
  - *Stdout exposure: fixed.* The stdout file and the fallback stderr file now live in a host-only directory (`<outdir>/stdio`, or a host `mkdtemp`), outside the call workspace, `SANDBOX`, and every bwrap bind. The shim refuses to start a call if either path is under one of them.
  - *Host-only logs.* Without a run log path, per-attempt stderr and `reap.log` go to the per-instance host `cursor-llm-stdio-*` directory, never under `SANDBOX`.
  - *Kill logging.* The timeout `killpg` is logged to `reap.log` as `KILLPG pid=… pgid=… tag=… call=… reason=timeout`. Reaper kills are logged as `KILL … reason=reap`.
  - *SIGKILL of the shim itself: accepted, on one condition.* If the shim process is SIGKILLed, the in-process reap never runs. This gap is accepted only because every counted trial takes an outside snapshot of processes carrying an `lbreap-` tag, and of worker-servers, before and after the trial. Both counts must be zero, before and after, or the trial does not count.
- The files under `tools/reaper/` remain an unverified prototype and are not used by the runner.

## Code changed

- `cursor_llm.py`: `reap_tag()`, per-attempt tag, file-based stdout/stderr, reap in `finally`, new record fields.
- Tests: new `packages/loopgym/tests/test_reaper_wiring.py`. `test_deviation3_pins.py`, `test_role_probe.py` and `test_role_rules.py` were adapted so their stubs accept the new keyword arguments.
- The commit that adds this file is named in the WORKLOG.

## Before the counted trials and attempt 5 (in order)

1. QA bot reviews and accepts this file and the code.
2. Re-freeze: commit `FROZEN-4.sha256`. It covers everything in FROZEN-3, plus this file, the updated `cursor_llm.py` and the new and changed tests.
3. Run the gate from a clean `git worktree` at the FROZEN-4 commit: `sha256sum -c`, per-package tests from each package's own folder with `/workspace/le-venv/bin/python -m pytest -q -p no:cacheprovider`, and ruff. Do not use `/workspace/le-venv/bin/pytest`: it imports the installed `loopgym` 0.1.4 and fails collection. This corrects DEVIATION-3's note. Keep the log under `logs/`.
4. Rerun the leak probe (`leak_probe.py`) and the role probe (`role_probe.py`) on `grok-4.7-high` through the new shim. Both must pass, with stderr and the reap log saved.
5. Only then run the counted concurrency trials (QA bot's recipe criteria, each with the outside before/after snapshot of tagged processes and worker-servers, which must be zero) and, after QA bot signs them off, attempt 5.
