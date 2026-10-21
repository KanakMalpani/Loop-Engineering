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
