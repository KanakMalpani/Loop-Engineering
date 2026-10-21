# Work log

## Timeline

Times are IST, from the commit log.

| Commit | When (IST) | Subject |
| --- | --- | --- |
| `49809bc` | Tue 20 Oct 21:03 | test(loopbench-validity): commit 10-loop set and fixed pass criterion before any run (B) |
| `95dc6ca` | Tue 20 Oct 21:16 | test(loopbench-validity): add cursor-agent LLMClient shim (B, after criterion) |
| `de143ce` | Tue 20 Oct 21:37 | fix(loopgym): live backend uses injected LLM instead of building MockLLM (wiring only, no scoring change) |
| `3b9afbe` | Tue 20 Oct 21:37 | test(loopbench-validity): short-run harness, MockLLM made to raise |
| `05669ee` | Tue 20 Oct 21:38 | test(loopbench-validity): harness calls LiveEnv's inner SimEnv (LiveEnv lacks run_episode) |
| `e5463cc` | Tue 20 Oct 21:40 | test(loopbench-validity): short measured run results and FAIL write-up (B) |
| `1045714` | Tue 20 Oct 21:40 | test(loopbench-validity): deterministic stub run on all 10 loops (B) |
| `bf47354` | Tue 20 Oct 21:53 | wip(loopbench): real code-repair fixtures cr-001..003 with hidden tests and stub-only reference fixes (not yet frozen) |
| `0700f19` | Tue 20 Oct 23:13 | feat(loopgym): sandboxed test_pass_rate evaluator runs hidden pytest suite on model output (no mock rate) |
| `7822c26` | Tue 20 Oct 23:16 | feat(loopgym): code-repair runtime scores from hidden-test pass rate only; honours inputs, feedback, evaluators, termination, cost caps |
| `bf107eb` | Tue 20 Oct 23:16 | feat(loopgym): LiveEnv.run_episode with injected LLM; LiveEnv refuses to run without one (never MockLLM) |
| `1be0a8c` | Tue 20 Oct 23:16 | test(loopgym): real-outcome evaluator, leak checks, spec-field and cost-cap tests; update tests that asserted old scoring |
| `980f880` | Tue 20 Oct 23:17 | test(loopbench-validity): fixed-benchmark stub checks (ref=1.0, empty=0 on cr-001..003) and 10-loop stub scores |
| `dc39ec3` | Tue 20 Oct 23:25 | test(loopbench-validity): parallel 10x3 runner run_full.py + concurrency probes on gpt-5.3-codex-low-fast (1:13.6s/16.0s, 2:19.8s, 5:15.7s, 10: all timed out at 180s); written by hand before switch to Cursor CLI |
| `32b7846` | Tue 20 Oct 23:33 | chore(loopbench-validity): shim default model gpt-5.3-codex (non-fast), process-group kill on timeout, --timeout flag. Code by Cursor CLI (cursor-agent, model gpt-5.3-codex) |
| `669bc0f` | Tue 20 Oct 23:37 | test(loopbench-validity): concurrency probes on gpt-5.3-codex: 1 call 16.0s, 5 concurrent 20.7s, 10 concurrent all timed out at 180s (193.7s wall) |
| `0a26c86` | Tue 20 Oct 23:38 | style(loopgym): ruff fixes in sandbox evaluator and real-outcome tests. Code by Cursor CLI (cursor-agent, model gpt-5.3-codex) + ruff --fix for import sort |
| `ac61d96` | Tue 20 Oct 23:55 | feat: bwrap-isolated cursor-agent shim, names-only test feedback (+no-expected-literal test), --max-concurrency 5, leak_probe.py. Code by Cursor CLI (cursor-agent; gpt-5.3-codex for main change, grok-4.7-high for test/ruff fixes) |
| `3b999c8` | Tue 20 Oct 23:57 | test(loopbench-validity): leak probe - isolated cursor-agent (gpt-5.3-codex) asked to read hidden test + reference fix: 'No such file or directory', 0 lines leaked |
| `807e74e` | Wed 21 Oct 00:04 | test(loopbench-validity): stub checks re-run on LB-CR-1 seeds 0-4 (ref=1.0, empty=0; 10-loop scores identical across seeds). Code by Cursor CLI (cursor-agent, grok-4.7-high) |
| `5259646` | Wed 21 Oct 00:04 | freeze(loopbench): fixtures and hidden tests frozen for acceptance |
| `9dd5523` | Wed 21 Oct 00:14 | style: ruff clean for run_full.py, run_stub_fixed.py, live.py (RUF100); loopbench now pip install -e in venv so tests run without PYTHONPATH. Code by Cursor CLI (cursor-agent, grok-4.7-high) |

## Decisions

| Who | Decision | Why |
| --- | --- | --- |
| Kanak | Fix the benchmark rather than drop it | After B FAILED |
| Kanak | Tests must take minutes, not hours | |
| Kanak | All code via Cursor CLI | |
| Kanak | Never use `*-fast` models | |
| Kanak | Coding with Grok/Composer (`grok-4.7-high`) | |
| Kanak | Option (a): provisional deviation in `DEVIATION.md` | Decided by Kanak, relayed by Engineering Lead, about 12:06 AM IST on Wed 21 Oct 2026 |
| Engineering Lead | PASS needs all 30 real-model runs | |
| Engineering Lead | Concurrency cap 5 | |
| Engineering Lead | Hidden tests and the reference fix are never visible to the model; they are copied only after the model turn | Leak rule |
| Engineering Lead | Runner should match the criterion | |
| Engineering Lead | Push at least every 30-45 min | |
| Engineering Lead | No acceptance run until approved | |
| QA bot | Fixtures frozen (hashed) before acceptance | |
| QA bot | Stub checks ref=1.0 / empty=0 must pass first | |
| QA bot | No leak, with committed refusal evidence | |
| QA bot | Feedback without expected values | |
| QA bot | Seeds per the criterion | |
| QA bot | `DEVIATION.md` committed before the first result | |
| QA bot | Every episode logs the pinned model, and MockLLM is never constructed | |
| QA bot | All runs complete; errors are recorded, not dropped; no silent retries | |
| QA bot | Highlight bad-3 against each good loop | |

## Original FAIL (B)

The old runtime scored from the model's self-reported number, plus 0.12 per iteration, plus 0.05. Spec evaluators, feedback, inputs, and cost limits were ignored. `test_pass_rate` read an unset mock rate.

On a short real-model run, `bad-2-no-tests` at 0.99 beat `good-1-fast` at 0.92. On a fixed-reply stub, bad loops 2-5 tied `good-1` / `good-3` at 0.79.

## The fix

`test_pass_rate` is sandboxed: it copies only `src/` to a work dir, copies hidden tests to a separate dir after the model call, runs pytest, and sets score = passed/total (0 on unparseable output).

`CodeRepairRuntime` scores test pass rate only. It honours worker inputs, role, and temperature, feedback channels, and evaluators (no test evaluator means 0). Termination covers max_iterations, consecutive, and stall. Cost limits halt as fail.

`LiveEnv.run_episode` takes an injected LLM and never builds MockLLM. Fixtures `cr-001`..`003` were built and frozen (`FROZEN.sha256`, commit `5259646`).

## Stub results

Task `LB-CR-1`, seeds 0-4.

- Reference patch scores 1.0 and empty output scores 0.0 on all fixtures.
- Feedback stub: `good-1`..`good-5` = 1.00, `bad-1` = 0.17, `bad-2` = 0, `bad-3` = 1.00 (the stub ignores role and temperature; only a real model can separate it), `bad-4` = 0, `bad-5` = 0.
- Fixed-reply stub scores 0.00 everywhere.

## Leak lockdown

`cursor-agent` runs under bubblewrap. `/workspace`, `/tmp`, and `$HOME` are masked. Only its install, login config, a per-call config copy, and the empty sandbox dir are mounted.

Proof: `results/leak-probe.json` (commit `3b999c8`). Asked to print the hidden test and the reference fix, it returned "No such file or directory" / "File not found", and 0 lines leaked. Feedback is failing test names and counts only, and was tested to contain no expected literals.

## Concurrency

`gpt-5.3-codex`: 1 call 16.0s, 5 concurrent 20.7s, 10 concurrent all hung to the 180s timeout (also on the earlier fast model). Cap set to 5.

Cursor CLI coding sessions count toward that limit, so the acceptance run uses `--max-concurrency 4` while coding on the demo continues.

## Models

Coding was hand-written early (through `dc39ec3`), then Cursor CLI `gpt-5.3-codex` (`32b7846`, `0a26c86`, and the main part of `ac61d96`), then `grok-4.7-high` (the rest of `ac61d96`, plus `807e74e`, `5259646`, `9dd5523`, and later).

The model under test is `gpt-5.3-codex`, pinned via `--model`, through the sandboxed shim. An early smoke run (`e5463cc`) used `gpt-5.3-codex-low-fast` before the no-fast rule.

## Open follow-ups

- Full `suite-repair` still needs `evaluators.tool_pass_rate` and real `LB-SAFE` fixtures.
- `cursor-agent` is an agent wrapper, not a raw model. Its token counts include its own tool use (18-21k input tokens inside the sandbox versus about 500 before), which affects cost limits.
- The 10-concurrency hang is unexplained.
- `bad-3` role and temperature are only testable with a real model. Temperature cannot be passed to `cursor-agent`; it is only stated in the prompt.

## Acceptance run progress

- Attempt 1 started Wed 21 Oct 00:23 IST: `run_full.py --confirm-acceptance`, `LB-CR-1`, seeds 0-4, 10 loops × 3 runs, model `gpt-5.3-codex` pinned, sandboxed shim, `--max-concurrency 4` (a Cursor CLI coding session for the demo was running alongside). Fixtures verified against `FROZEN.sha256` before start.
- Aborted 00:35 IST by SWE: 0/30 runs complete. 8 `cursor-agent` calls hit the 180s timeout; Cursor backend logged "Connection lost" at the same time.
- Logs kept in `results/acceptance/` (commit `bbfb3df`); nothing dropped.
- Diagnosis afterwards: a non-sandboxed single call still worked (35s), but sandboxed (bwrap) single calls hung with no output even at concurrency 1, also with the identity socket bound back in. Earlier, 23:45–23:57 IST, sandboxed calls worked (23s; leak probe 144s).
- Root cause unknown. Acceptance is BLOCKED until the sandboxed shim works again. Not restarted without isolation; that would break the leak rule.

## Deliverable A

- `demo/` committed at `b8e3459` (offline, stub only, spec → trace → benchmark).
- 3 cold runs (fresh clone of the branch + fresh venv, pip cache warm) took 13s each end to end. Demo itself: 8.18s / 8.00s / 8.04s.
- `gen_ai.*` spans, `loop.cost_usd` on the trace path, and `fail.*` trace events are marked PLANNED.
- Benchmark scores labelled "pending fixed benchmark acceptance".

## Sandbox hang: cause and fix

The per-call sandbox `~/.cursor` had no plugins cache, so cursor-agent tried to download Cursor's public plugins and blocked after "Cursor plugin load did not finish within the rules wait budget" (seen in its session log). It worked 23:45–23:57 IST because the download succeeded then.

Fix: read-only bind of `~/.cursor/plugins` (public plugin cache only) into the sandbox.

After the fix:

- Leak probe re-run: not leaked (`results/sandbox-fix/leak-probe-after-fix.json`).
- 1 call: 18.2 s.
- 4 concurrent: 46.2 s, and again 23.4 s, with 0 errors.
- 5 concurrent: all 5 timed out at 150 s (box load average ~108; other agents share it).

Attempt 2 runs at `--max-concurrency 4` with no coding sessions. Infra-only retry policy added (see `results/acceptance-2/RETRY-POLICY.md`).

## Acceptance attempt 2

- Started Wed 21 Oct 01:28:44 IST, finished 03:34 IST (about 126 min by timestamps). `summary.json` `wall_seconds` 4652 disagrees: monotonic clock, likely host suspension during box connection drops.
- 30/30 runs complete, committed at `ef3c5c8`. Model `gpt-5.3-codex` pinned for all runs, `CursorAgentLLM`, sandboxed, MockLLM never constructed. Concurrency 4, timeout 150 s.
- 0 INFRA-FAIL, 0 errors. 627 call attempts, 621 ok, 6 timeouts, all recovered by the infra-only retry.
- Per-loop scores (3 runs): bad-1 1.0/1.0/1.0, bad-2 0/0/0, bad-3 1.0/1.0/1.0, bad-4 0.333/0.200/0.333, bad-5 0/0/0, good-1 1.0/0.983/1.0, good-2..good-5 1.0 in all runs.
- Verdict FAIL as written (provisional per `DEVIATION.md`): runs 0 and 2 tie at 1.0; run 1 min good 0.983 < max bad 1.0. bad-3 ties every good loop in every run and beats good-1 in run 1.
- `DEVIATION.md` and `FROZEN.sha256` byte-identical to `5d02f63` after the run. No Cursor CLI sessions during the run, so this log was not edited until after it.
- Diagnosis: bad-1, bad-3, good-1, good-3, and good-5 used exactly 15 model calls per run (15 episodes × 1 iteration), so the model fixed each bug in one shot and feedback channels never came into play. good-2 and good-4 used 30 (2 iterations only because their success rule needs 2 consecutive passes).
- bad-3's role (rewrite in another language) was ignored; the model still returned Python that passed. Temperature 1.8 is only stated in the prompt; cursor-agent cannot set it. good-1 run 1 seed 4 stopped at 0.75 on cr-001 because 0.75 meets its success threshold.
- The fixtures are too easy for this model to separate feedback/role defects. Model replies are not stored in the run files, so bad-3's actual code cannot be inspected from logs.

## 2026-10-21 03:50 IST: QA follow-ups on attempt 2 (results untouched)

- **Retries:** all 6 are logged in each run file's `calls[i].attempts` lists, not in `run.log`. Every one is a first-attempt timeout at 150 s followed by an ok second attempt:
  - `bad-1-no-feedback-r0` call 0
  - `bad-2-no-tests-r0` call 0
  - `bad-3-wrong-role-r0` call 0
  - `bad-4-no-bug-input-r0` call 0
  - `bad-4-no-bug-input-r2` call 15
  - `good-4-thorough-t0-r0` call 8
  - The first four were the first calls at startup.
  - `run.log` doesn't print retries; this is a gap to fix in the next attempt.
- **Wall time:** the two figures disagree.
  - `summary.json` gives `wall_seconds` = 4652 s, about 77.5 min.
  - The START and finish timestamps, 01:28:44 to 03:34:44 IST, span about 126 min.
  - `wall_seconds` is likely measured with a monotonic clock that doesn't advance while the box is suspended or paused, while the timestamps use wall-clock time. That cause hasn't been verified, and the criterion doesn't depend on time.
- **Next attempt:** store every model reply in the run files, so bad-3's code can be inspected, and log each retry attempt in `run.log`.

## Acceptance attempt 3 started (Wed 21 Oct 2026)

- QA PASS on the freeze (`8b1bfc1`) and Engineering Lead go. `FROZEN.sha256` and `FROZEN-2.sha256` tests pass before start.
- First launch at 09:52:09 IST was killed about 5 s later, when the shell tool that launched it was interrupted. That was before any episode completed: progress 0/30, no run files, no run.log. Its leftovers were moved out of the repo to `/workspace/acc3-aborted-0922/`. Nothing in the frozen set or the runtime changed.
- Attempt 3 restarted from zero at 09:52:25 IST, detached with setsid/nohup: `run_full.py --confirm-acceptance --model gpt-5.3-codex --task LB-CR-1 --seeds 0,1,2,3,4 --runs 3 --max-concurrency 4 --timeout 150 --outdir results/acceptance-3`.
- **Not directly comparable to attempt 2.** Attempt 3's scored-patch rule differs: untagged ``` fences are now accepted as the patch (DEVIATION-2.md, "What is scored"). Attempt 2 accepted only python/py-tagged fences. Attempt 3 also adds cr-004..cr-007, enforces the role via the rules file, and drops role and temperature text from the prompt. So attempt 2 and attempt 3 scores are not directly comparable.

### Attempt 3 timestamp correction

These times are from git and from `results/acceptance-3/run.log`.
- Freeze commit `8b1bfc1`: 09:49:18 IST (04:19:18Z).
- First launch: 09:52:09 IST. It was killed about 5 s later, with 0 results.
- Clean restart: 09:52:25 IST.
- First `run.log` line: 04:24:55.33Z (09:54:55 IST). It is `bad-1-no-feedback/r0 call=0 attempt=1 outcome=timeout seconds=150.1`, and lines are written when an attempt ends. So the first call of attempt 3 started at about 04:22:25Z (09:52:25 IST). That attempt was retried and returned ok after 23.8 s.
- The "10:00 AM" start time I posted in Eng Pod was wrong. The correct start is 09:52:25 IST.

## Attempt 3 abandoned; acceptance attempt 4 started (Wed 21 Oct 2026, times IST)

- Attempt 3's last call finished at 12:31:09 IST.
- The box restarted at about 13:18 IST. The restart killed the runner and the pusher and changed the box timezone to UTC.
- Attempt 3 is abandoned at 8/30. Its partial state is committed at `4aca065` and the run was not resumed. It has no criterion verdict.
- Also lost in the restart: `/workspace/oa/pull/out` (77 AE parts). This is unrelated to the benchmark.
- After the restart, cursor-agent was still logged in. Engineering Lead approved attempt 4.
- Attempt 4 preflight, logged in `results/acceptance-4/preflight/`:
  - Fresh sandbox `/workspace/cursor-llm-sandbox-acc4-20261021T084236Z` and fresh eval tmp `/workspace/lb-eval-tmp-acc4-20261021T084236Z`, with nothing reused from attempt 3.
  - HEAD at launch was `4aca065`.
  - The FROZEN and FROZEN-2 tests passed both before the probes and at launch.
  - Read-only leak probe on cr-004: 0 leaked lines.
  - Role rules-file pickup probe: picked up ("ROLE-PICKUP-7731 Hello!").
- Attempt 4 launched at 2026-10-21T14:14:08+05:30 (08:44:08Z), runner PID 47998, under setsid/nohup. The command is the same as attempt 3's, with `--outdir results/acceptance-4`.
- The pusher (`/workspace/acc4/pusher.sh`) pushes `results/acceptance-4` every 3 completed runs or every 25 minutes, and once more at the end.

## Attempt 4 abandoned (infrastructure), not graded (Wed 21 Oct 2026, IST)

- Stopped at 17:07:35 IST by Engineering Lead's decision. The runner's process group (PID 47998) and the pusher (49226) were stopped. Nothing else was killed.
- A process_error surge began at 16:34:40 IST.
- `run.log` outcome counts:
  - at stop: 435 ok, 161 process_error, 10 timeout;
  - at `add524f`: 435 ok, 118 process_error, 8 timeout;
  - the relayed figures were 435 / 136 / 10.
- INFRA-FAIL seeds were in 8 of 14 run files at `add524f` (QA bot), and in 10 of 16 at stop.
- 16 of 30 run files were written. All files are kept, and there is no verdict.
- Details are in `results/acceptance-4/README.md`. The cause is under read-only investigation.

## 2026-10-21 18:40 IST: probe model switch (exploration only)
- Concurrency-recipe probe trials now use grok-4.7-high (switched from gpt-5.3-codex), per Engineering Lead.
- Recipe trials on grok-4.7-high count as exploration only for LoopBench until Kanak decides the model; they do not count toward the frozen run's sign-off.
- AE is unaffected: its LLM baseline was already pinned to grok-4.7-high.
- Quota check on attempt 4: 0 matches for "usage limit" or ActionRequiredError in results/acceptance-4 (run files + run.log) or /workspace/acc4 logs. Caveat: stderr was not captured; 43 INFRA-FAIL seeds read "cursor-agent exited 1 with no output", so quota can't be ruled out from these files.

## 2026-10-21 18:42 IST: model sweep to grok-4.7-high; DEVIATION-3 draft
- Kanak's standing rule (via Engineering Lead): Grok or Composer models only, never `*-fast`.
- Drafted `DEVIATION-3.md` (attempt 5 on pinned `grok-4.7-high`, cursor-agent `2026.10.19-6bbf2c4`; not comparable with attempts 1-4; per-call stderr; QA-verified recipe; re-freeze + probes rerun before launch). Draft only: NOT frozen, nothing run. sha256 f49e70f4a0f55cd3effc4f714055eddcdfc6d52ff40c77cb0f82f5d152a8e900.
- Changed: `benchmarks/loopbench-validity/cursor_llm.py` `DEFAULT_MODEL`: `os.environ.get("CURSOR_LLM_MODEL", "gpt-5.3-codex")` -> `"grok-4.7-high"` (hard pin, env override removed). This also changes the `--model` default of `run_full.py` and `leak_probe.py`, which read it.
- Already grok-4.7-high, no change: `/workspace/concurrency-investigation/{call.py,lb_probes.py,ae_nonet_probe.py}`.
- Left alone (historical / not engineering-model defaults):
  - `/workspace/acc4/launch_acc4.sh` (`--model gpt-5.3-codex`) and `/workspace/acc4/probes.py` (gpt-5.3-codex x2): attempt-4 launch evidence; attempt 5 gets its own launcher.
  - `/workspace/acc4/run.out`, `/workspace/concurrency-investigation/lifecycle/aborted-*/plain-none.json`, `results/acceptance-*`: old logs/results.
  - `benchmarks/loopbench-validity/loops/*.yaml` (`name: gpt-4.1-mini`): frozen loop specs; loops unchanged per DEVIATION-3. The spec model is not used by cursor-agent calls.
  - `loop-library/*.yaml`, `loopctl/schemas/minimal-loop.yaml`, `packages/loopgym/examples/minimal-loop.yaml`, `scripts/composition_templates.py`, `scripts/enrich_loop_library.py` (`gpt-4.1-mini`): product/example loop-spec content for end users, not the model our engineering work runs on.
  - Codex mentions in docs, `examples/integrate-codex/`, `scripts/adoption_wave*.py`, `scripts/daily_checkin.py`: harness names, not model defaults.
  - `evidence/cursor-agent-help.txt`: captured CLI help.
  - Artificial-Emotions repo: not touched (PREREG-pinned).
- Tests (/workspace/le-venv): packages/loopbench 16 passed, 2 skipped; packages/loopgym 56 passed, 1 failed (`test_working_copy_contains_only_src`, fails identically without this change, pre-existing). ruff: cursor_llm.py clean; benchmarks/loopbench-validity has the same pre-existing findings before and after.

## 2026-10-21 19:10 IST: DEVIATION-3 fixes after QA bot rejection at 79b4bfc (not frozen, nothing run)
- Code changed via cursor-agent (`--model grok-4.7-high`, prompt and output in /workspace/dev3-fix/); reviewed and re-tested by SWE.
- `cursor_llm.py`:
  - `INFRA_RETRIES`: `int(os.environ.get("CURSOR_LLM_INFRA_RETRIES", "2"))` -> `2` (pinned constant).
  - `ISOLATE`: `os.environ.get("CURSOR_LLM_ISOLATE", "1") != "0"` -> `True` (pinned constant).
  - New `assert_no_unpinned_env()`: raises if `CURSOR_LLM_MODEL`, `CURSOR_LLM_INFRA_RETRIES` or `CURSOR_LLM_ISOLATE` is set; called in `CursorAgentLLM.__init__`. Chosen option: pin + abort on any stale override (never silently ignored).
  - Empty or whitespace model -> `ValueError`; `--model` is now always passed (was only when non-empty).
  - `_run_once` returns stderr (also after a timeout kill); each attempt's stderr goes to its own file `<log dir>/stderr/<run>-call<i>-attempt<n>.stderr` (or `SANDBOX/stderr/` with no log path); attempt records gain `stderr_path`, `stderr_bytes` (and `stderr_missing` for legacy 2-tuple stubs).
  - Call records gain `model_requested` and `model_reported` (null when cursor-agent reports none).
- `run_full.py`: `PINNED_MODEL`; `assert_no_unpinned_env()` at startup; `--confirm-acceptance` with `--model` != grok-4.7-high exits before launch; `model_check(rows)` in summary, any violation sets `invalid: true` and criterion `pass: false`; summary `deviation` "see DEVIATION.md" -> "see DEVIATION.md, DEVIATION-2.md, DEVIATION-3.md".
- New `packages/loopgym/tests/test_deviation3_pins.py` (stubbed, no real calls): per-attempt stderr files incl. timeout-then-ok retry; empty-model guard; each env override raises; model_requested/model_reported; model_check; `one_run` on `loops/good-1-fast.yaml` (spec model gpt-4.1-mini) always requests grok-4.7-high.
- `DEVIATION-3.md`: "cap stays at 4" fallback replaced by "no launch without a QA-verified concurrency recipe, named by commit"; added model_requested/model_reported/model_check, empty-model guard, env pins, per-attempt stderr path, and "cursor-agent ignores the frozen loop specs' model field" (specs untouched). sha256 fcdad40b13893934e01bf25136d65485b195aca5f034e08e39f5ba118d7e203d.
- Correction to the 18:42 entry, `test_working_copy_contains_only_src`: it does NOT fail at the code level. In clean worktrees it passes at base `41f77ac` (22/22) and at `79b4bfc` (22/22). It fails only in this checkout, which has ignored `__pycache__/` dirs under `packages/loopbench/fixtures/cr-*/hidden_tests/`, likely created by SWE's earlier root-level pytest run. The test then sees 2 hidden dirs instead of 1. It is a known environment-only failure that predates this change. The cache dirs were left in place; removing them is untracked cleanup awaiting approval.
- Tests (/workspace/le-venv, `-p no:cacheprovider`, run serially): packages/loopgym 67 passed, 1 failed (the environment-only failure above); packages/loopbench 16 passed, 2 skipped. ruff on cursor_llm.py, run_full.py and test_deviation3_pins.py: all checks passed.

## Attempt 4 surge cause: STRONG INFERENCE, NOT PROVEN
- Attempt 4's process_error surge from 16:34 IST was most likely the gpt-5.3-codex Cursor usage limit.
- Evidence: a bare gpt-5.3-codex call now exits 1 after about 12 s with "You've hit your usage limit… resets 11/5/2026". The last ok call was at 16:34:50 IST. 106 of the 161 process_errors took 10-15 s. The shim discarded stderr, so nothing was logged (fixed above).
- The leftover worker-servers were likely a side effect: each outlives its call by about 5 min and stays in the call's process group (see /workspace/concurrency-investigation/02-lifecycle.md).
- Low box memory: avoid heavy parallel test runs.

## 2026-10-21 19:22 IST: DEVIATION-3 round 3 (QA bot on cd2ae98); not frozen, nothing run
- Code via cursor-agent `--model grok-4.7-high` (/workspace/dev3-fix/prompt3.txt, agent3.out); reviewed by SWE.
- `cursor_llm.py`: `CURSOR_BIN` `os.environ.get("CURSOR_AGENT_BIN", ~/.local/bin/cursor-agent)` -> `~/.local/bin/cursor-agent` (pinned); `CURSOR_AGENT_BIN` added to the abort-on-set list; new `PINNED_CURSOR_AGENT_VERSION = "2026.10.19-6bbf2c4"`, `launch_identity()` (bin, resolved path, `--version`), `assert_launch_identity()` (aborts on version mismatch), `require_pinned_model()`, `calls_model_check()`. Live check on the box: resolved `/home/box/.local/share/cursor-agent/versions/2026.10.19-6bbf2c4/cursor-agent`, version `2026.10.19-6bbf2c4`.
- `run_full.py`: `assert_launch_identity()` at startup, recorded as `launch_identity` in summary and probe output; `--probe` refuses non-pinned models, records model_requested/model_reported per call and `model_check`, writes `invalid: true` and exits 1 on mismatch; `model_check(rows)` now uses `calls_model_check`.
- `leak_probe.py`: same launch-identity and pinned-model refusal; output has per-call model_requested/model_reported, `model_check`, `launch_identity`; exits 1 on mismatch.
- The role rules-file pickup probe is not in this repo (it lived in /workspace/acc4/probes.py for attempt 4); attempt 5's role probe must use the same helpers.
- Tests: new cases in `packages/loopgym/tests/test_deviation3_pins.py` (CURSOR_AGENT_BIN abort, version mismatch, identity dict, probes refuse gpt-5.3-codex before any call, calls_model_check, leak-probe output fields).
- Reaper: `tools/reaper/{README.md,cursor-agent-errlog,cursor-agent-reap,snap.sh,verify.py}` came in via `3d7bca4` (18:52 IST, the concurrency-investigation prototype, "not wired into runner"), which landed on this branch between `79b4bfc` and `cd2ae98`. DEVIATION-3 now says no reaper is part of attempt 5 until QA bot signs off the trial results, and these files are unverified and not named by the freeze.
- Freeze-gate tests run from a clean `git worktree` at the freeze commit (avoids the ignored fixture `__pycache__/` dirs in this checkout; nothing deleted). QA bot can use `/workspace/le-venv/bin/pytest`.

## 2026-10-21 19:35 IST: attempt-5 role probe committed (QA bot's last pre-freeze condition); not frozen, nothing run
- New `role_probe.py`, ported from the role-pickup half of /workspace/acc4/probes.py: the same prompt ("Say hello in one short sentence."), the same `ROLE-PICKUP-7731` role and the same pickup test. It uses the same guards as `leak_probe.py`:
  - abort if `CURSOR_LLM_*` or `CURSOR_AGENT_BIN` is set;
  - `assert_launch_identity()` (fixed binary path, version 2026.10.19-6bbf2c4);
  - `require_pinned_model` (grok-4.7-high);
  - per-call stderr files under `<out dir>/stderr/`;
  - output with model_requested/model_reported, model_check and launch_identity;
  - `invalid: true` and exit 1 on a model mismatch; exit 1 on no pickup or InfraError.
- New stubbed tests in `packages/loopgym/tests/test_role_probe.py`. Code written by cursor-agent `--model grok-4.7-high` (/workspace/dev3-fix/prompt4.txt, agent4.out) and reviewed by SWE.
- `DEVIATION-3.md`: names `role_probe.py` in the probe pin line and in pre-launch step 3. sha256 74af392 113082e8… -> 91ebf752f750cf8c69a94fd0611b95f632dc76359c98fb80e6a32ab4367efe9b.

## 2026-10-21 19:40 IST: re-freeze for attempt 5 (FROZEN-3), approved by QA bot after DEVIATION-3 sign-off at 057a236
- Pre-check: `sha256sum -c packages/loopbench/fixtures/FROZEN-2.sha256` -> 28/28 OK; FROZEN.sha256 12/12 OK. FROZEN-2.sha256 unchanged.
- New `benchmarks/loopbench-validity/FROZEN-3.sha256` (same `<sha256>  <path>` format; paths relative to repo root; check with `sha256sum -c benchmarks/loopbench-validity/FROZEN-3.sha256` from the repo root). 49 entries:
  - all 28 FROZEN-2 fixture files (`packages/loopbench/fixtures/...`) plus `FROZEN.sha256` and `FROZEN-2.sha256` themselves;
  - `CRITERION.md`, `DEVIATION.md`, `DEVIATION-2.md`, `DEVIATION-3.md`, `results/acceptance-2/RETRY-POLICY.md`;
  - `run_full.py`, `cursor_llm.py`, `leak_probe.py`, `role_probe.py`;
  - the 10 `loops/*.yaml`.
- Excluded: everything under `tools/reaper/`, until QA bot signs off the trial results.
- The freeze commit is the one that adds this entry and FROZEN-3.sha256. Gate: run from a clean `git worktree` at the freeze commit: `sha256sum -c`, then the loopgym and loopbench tests each from their own folder with `-p no:cacheprovider` (never from the repo root), then ruff. The output is kept under `benchmarks/loopbench-validity/logs/`.
- Attempt 5 is not launched and no probes have run.

## 2026-10-21 20:13 IST: NOT FROZEN: tag-based reaper wired into cursor_llm.py; DEVIATION-4 draft
- Code by cursor-agent `--model grok-4.7-high` (/workspace/dev3-fix/prompt5.txt, agent5.out), reviewed by SWE. QA bot reviews before FROZEN-4. No re-freeze, no launch, no real calls.
- Port of `tools/reaper/` (`3d7bca4`, `060b0c7`) into the shim, always on, no env override:
  - per-attempt `CURSOR_REAP_TAG=lbreap-<uuid>` (Popen env + bwrap `--setenv`);
  - after every attempt (ok, error, timeout, exception) SIGKILL only exact-tag processes, re-checked before each kill; untagged or unreadable processes are never touched;
  - per-run `reap.log` with START/KILL(pid, tag, call)/DONE lines;
  - record fields `reap_tag`, `reap_kills`, `leftover_tagged`, `leftover_worker_servers` (per attempt) and `reap_kills`, `leftover_worker_servers`, `reap_log` (per call).
- Pipe-hang fix (trial/aborted-tee): stdout/stderr go to files, not pipes; stdin DEVNULL; `wait(timeout)` instead of `communicate()`.
- Files: `benchmarks/loopbench-validity/cursor_llm.py` (changed), `benchmarks/loopbench-validity/DEVIATION-4.md` (new, sha256 969a21a46b7986e2ef318994e63945b27c1af0579358a8584d0f111e354b675a), `packages/loopgym/tests/test_reaper_wiring.py` (new), `packages/loopgym/tests/test_deviation3_pins.py`, `packages/loopgym/tests/test_role_probe.py`, `packages/loopgym/tests/test_role_rules.py` (stubs accept the new kwargs).
- FROZEN-3 no longer matches `cursor_llm.py` from this commit on. FROZEN-4 plus a probe rerun are needed before the counted trials and attempt 5 (DEVIATION-4).
- Known gaps: SIGKILL of the shim process itself skips the in-process reap; the stdout temp file sits in the call workspace (visible to the agent, read-only ask mode).

## 2026-10-21 20:39 IST: NOT FROZEN: reaper fixes after QA bot's review of f62709f
- Code by cursor-agent `--model grok-4.7-high` (/workspace/dev3-fix/prompt6.txt, prompt7.txt; agent6.out, agent7.out), reviewed by SWE.
- `cursor_llm.py`:
  - The stdout temp file and the fallback stderr temp file moved from `work` to the host-only `_host_stdio_dir()`: `<outdir>/stdio`, or a per-instance `cursor-llm-stdio-*` mkdtemp.
  - `_bind_paths` and `_assert_stdio_unbound` raise if either path is under `work`, `SANDBOX` or any bwrap bind.
  - Without a log path, stderr goes to `<stdio>/stderr` (was SANDBOX/stderr, then the shared tmp/stderr) and the reap log to `<stdio>/reap.log` (was SANDBOX/reap.log).
  - The timeout killpg is logged as `KILLPG pid= pgid= tag= call= reason=timeout`. Reaper kills now end with `reason=reap`. These are the only two kill sites.
- Tests: `test_reaper_wiring.py` (host-only stdio for both log-path cases, KILLPG line, reason=reap, distinct per-instance stderr dirs, host-only reap log); `test_deviation3_pins.py` expectation updated.
- DEVIATION-4 gaps updated:
  - stdout exposure fixed;
  - host-only logs;
  - kill logging;
  - the shim-SIGKILL gap is accepted only with an outside before/after snapshot of tagged processes and worker-servers, which must be zero, for every counted trial.
- Correction: `/workspace/le-venv/bin/pytest` imports the installed loopgym 0.1.4 and fails collection (2 errors). Gate tests must use `/workspace/le-venv/bin/python -m pytest` from each package folder. DEVIATION-3, which is frozen and unchanged, said QA bot could use the pytest script; DEVIATION-4 corrects that.

## 2026-10-21 22:34 IST: during-pull counted trial 1 of 3 (c8-pull-1), frozen path at 99cc307
- AE pull switch: `pull.sh` v5 -> v6 (2 workers) at 22:32:06 IST, sha256 cc65dfc51993520aa5680b164a65b50894a79243dae2398ad1d08b91e17151b1 (SWITCH line in /workspace/oa/pull/pull.log; script `switch_v6.sh`, same procedure as v4/v5). In flight and re-pulled from scratch: 2026-09-27 parts 0010, 0011, 0012. New pull PID 590112 (was 370638). Worker count 2 at before- and after-snapshot, sha unchanged.
- Trial: started 22:33:04 IST, all calls returned 22:33:54, after-snapshot 22:34:00. 8 concurrent calls, each its own process, importing the frozen `cursor_llm.py` from clean worktree /workspace/le-trial-99cc307 (no shim, no CURSOR_TRIAL_BIN, none of the pinned env vars set), grok-4.7-high, timeout 150 s, cr-004 LoopBench prompt (504 chars + role). Driver `results/trials-freeze4/{run_trial.sh,fcall.py}`.
- Result: 8/8 ok on attempt 1, 27.6-47.8 s; 0 timeouts, 0 retries, 0 errors. Each call has its own stderr file, 0 bytes (clean ok). Reaper: 32 KILL (4 per call, all reason=reap, own tag/call), 0 KILLPG, 8 DONE; per-call leftover worker-servers 0, tagged 0.
- Outside snapshots (snap.sh): before tagged=0 worker_servers=0; after tagged=0 worker_servers=0. Untagged decoy sleep pid 598384 survived.
- Resources: availMB min 4318, 1-min load max 5.40; guard never tripped.
- Gap: the frozen record has no per-attempt exit code field (outcome=ok only).
- Logs: `results/trials-freeze4/c8-pull-1/`. Pull left at 2 workers pending report; other 2 counted trials not run.

## 2026-10-21 22:38 IST: counted trials 2 and 3 of 3 (c8-2, c8-3), frozen path at 99cc307
- AE pull switch: `pull.sh` v6 -> v7 (3 workers) at 22:35:55 IST, sha256 6aaab5ab027ed5372fb69c036ad2fe62c0cbeecb324f8afc127da3495c6150ca (`switch_v7.sh`, same procedure). In flight and re-pulled from scratch: 2026-09-27 parts 0016, 0017. New pull PID 608189 (was 590112). 3 workers and same sha at every before/after snapshot; no worker change until c8-3 after-snapshot.
- Setup identical to c8-pull-1 (`results/trials-freeze4/{run_trial.sh,fcall.py}`): frozen cursor_llm.py from /workspace/le-trial-99cc307, no shim/CURSOR_TRIAL_BIN/pinned env vars, grok-4.7-high, 150 s, 8 concurrent, cr-004 prompt.
- c8-2: started 22:36:14 IST, calls returned 22:36:54, after-snapshot 22:37:00. 8/8 ok on attempt 1, 24.5-35.2 s; 0 timeouts, 0 retries, 0 errors; 8 stderr files, 0 bytes each. Reap: 8 START, 32 KILL (reason=reap), 0 KILLPG, 8 DONE; per-call leftovers 0/0. Snapshots before tagged=0 ws=0, after tagged=0 ws=0. Decoy pid 613389 survived. availMB min 3050, load max 6.42.
- c8-3: started 22:37:01 IST, calls returned 22:37:42, after-snapshot 22:37:48. 8/8 ok on attempt 1, 24.7-31.0 s; 0 timeouts, 0 retries, 0 errors; 8 stderr files, 0 bytes each. Reap: 8 START, 32 KILL, 0 KILLPG, 8 DONE; leftovers 0/0. Snapshots before 0/0, after 0/0. Decoy pid 619680 survived. availMB min 2808, load max 6.75.
- Same gap as c8-pull-1: no per-attempt exit-code field in the frozen record (outcome=ok only). Logs: `results/trials-freeze4/c8-2/`, `c8-3/`. Awaiting QA grading; attempt 5 on hold.
