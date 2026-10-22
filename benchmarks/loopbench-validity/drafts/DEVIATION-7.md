# DEVIATION-7 (DRAFT): per-attempt model-call timeout 150 s -> 900 s

Status: DRAFT - pending Kanak's approval and QA review. Not frozen, not pinned, nothing launched under it. FROZEN-6 (`f1f5ef9`, manifest `81b977bd…1661`) and `launch5b.sh` (`84121cd`, sha `661d7479…`) are unchanged.

Everything in `DEVIATION.md` through `DEVIATION-6.md` still applies unless changed below.

## 1. Scope

- `--timeout` on the attempt-5 launch command changes from 150 to 900 (seconds). That is the only change.
- Unchanged: the retry cap (`INFRA_RETRIES = 2`, so at most 3 attempts per call, infrastructure no-result only), `--max-concurrency 5`, prompts, roles, loops, fixtures (cr-001..cr-007), task `LB-CR-1`, seeds 0-4, 3 runs, model `grok-4.7-high`, the cursor-agent pin `2026.10.19-6bbf2c4`, the `--output-format json` call shape, the 6144 MB startup floor, and the pass criterion.
- `run_full.py` and `cursor_llm.py` code is unchanged. The timeout is already a command-line value.

## 2. How the timeout is used (frozen code, read-only check)

- `run_full.py` `--timeout` (argparse `default=180`, line 431) goes to `one_run(..., timeout)` and then `CursorAgentLLM(timeout=timeout)` (line 165).
- `cursor_llm.py` `_run_once` applies it **per attempt**: `proc.wait(timeout=self.timeout)` (line 469). On expiry it SIGKILLs the process group, logs `KILLPG ... reason=timeout` to `reap.log`, and the attempt counts as a timeout.
- `complete()` retries a no-result attempt (timeout, no output, unparsable, process error) `INFRA_RETRIES + 1 = 3` times (line 632). A call that times out 3 times raises `InfraError` and its seed becomes INFRA-FAIL (`run_full.one_run`); the run moves on to the next seed. Seeds run sequentially within a run; runs run in parallel up to `--max-concurrency`.
- So the worst case per call is 3 x timeout, plus about 1 s per attempt of reap overhead.
- `launch_identity()`'s `timeout=30` (line 77) is the `cursor-agent --version` check and is unrelated.

## 3. Evidence

### 3.1 Smoke failures (launcher `launch5b.sh` `84121cd`, FROZEN-6 worktree)

| smoke | dir | call 4 attempts (IST) | result |
|---|---|---|---|
| 1 | `/home/box/le-runs/attempt5b-20261022-124833-IST` | 12:51:59-12:54:30, -12:57:01, -12:59:32 | 3 x timeout at 151.0 s |
| 2 | `/home/box/le-runs/attempt5b-20261022-130050-IST` | 13:04:12-13:06:43, -13:09:14, -13:11:45 | 3 x timeout at 151.0 s |

- Both: `good-1-fast`, seed 0, `SMOKE_FAIL: n_infra_fail=1` (wrapper rc 10 recorded for smoke 2), run rc 0, sha check MATCH, 0 leftover worker-servers.
- Calls 0-3 were ok in 26.5-42.9 s. Call 4 is the first revision prompt (cr-004 `durations.py`, iteration 2, with test_runner feedback "3/12 hidden tests passed"). That's 6 out of 6 timeouts on the same step, with stderr 0 bytes and no connection, auth or rate-limit errors (`call4-investigation.md` in the smoke-1 dir).

### 3.2 Diagnostic (`/home/box/le-runs/diag-call4-20261022-131308-IST`, DIAGNOSTIC, not acceptance evidence)

Same sandbox, binary, flags and model as frozen `cursor_llm.py`, except `--output-format stream-json --stream-partial-output` and a 900 s cap.

| run | prompt | first answer text | total | output tokens | tool calls | finished |
|---|---|---|---|---|---|---|
| call4-run1 | call 4 | 17.8 s | 548.4 s | 10304 | 14 | yes (one 2 s reconnect at 409 s) |
| call4-run2 | call 4 | 19.1 s | 234.5 s | 13842 | 7 | yes |
| call4-run3 | call 4 | 18.8 s | 305.6 s | 17804 | 7 | yes |
| call3-control | call 3 | 16.5 s | 25.3 s | 857 | 2 | yes |

Read: slow, not hung. On the revision prompt the model streams from about 18 s, then reasons for minutes and makes read-only tool calls before returning a fenced module. All 3 runs exceed 150 s.

Prompt shas (`prompts.sha256` in the diag dir):
- call 4, smoke 2: `3179520ea928cfcbfba643ccf074ad626d224a95bf5b0727609a9622dfc87247` (1425 bytes, byte-exact, parsed from the INFRA-FAIL command repr)
- call 4, smoke 1: `f471d6475f8546d559373468977b1bc1f1c58cf31d63c541d82a77ca8e64cf03` (1291 bytes, byte-exact, same method)
- call 3, control: `24f815d6bfdf173064a3a984e31a9e12df0b5e65fbfd0b675dc9f07ccb059e91` (546 bytes)

Control caveat: call 3's prompt was never recorded. It was rebuilt as the call-4 prompt cut before `\n\nYour previous reply:\n`, following `outcome_runtime.build_prompt` for iteration 1. Supporting evidence: the call-4 "previous reply" equals the recorded call-3 reply, and input tokens agree (12626 smoke vs 12623 diag). It is not independently verified as byte-exact.

### 3.3 acceptance-4 (read-only, `results/acceptance-4`)

- `run.log` has 10 timeout attempts in about 600 attempts (~1.6%); 9 of them are in the 16 run files.
- By role: Produce a minimal code patch 6 / 321 calls; Analyze failing tests 2 / 103; Rewrite the whole file 1 / 54.
- By attempt number: 7 on attempt 1, 2 on attempt 2, and 1 on attempt 3 (good-3-fast-5iter/r1 call=0, in `run.log` only).
- Initial vs revision is not recorded. Only call=0 is certainly initial (2 of 10).
- No prompt timed out 3 times in a row in acceptance-4. The repeatable failure on this revision step is new evidence from 2026-10-22.

## 4. Rule for 900 s

- Slowest observed revision run: 548.4 s. 1.5 x 548.4 = 822.6 s, rounded up to 900 s. 900 s is also the diag cap, so every diag run finished within the proposed value.
- Limits: n = 3 runs on one prompt (one fixture, one loop). Run 1 included a 2 s reconnect (409-411 s). Other fixtures' revision prompts were not measured and may be slower.

## 5. Exactly what changes (if approved)

| file | status | line | from | to |
|---|---|---|---|---|
| `drafts/frozen6/LAUNCH-RECIPE-attempt5.md` | recipe doc (DEVIATION-6 record) | 20 | `--timeout 150` | `--timeout 900`, or supersede with an attempt-5 recipe under DEVIATION-7 |
| `results/acceptance-5/launcher/launch5b.sh` | pinned `84121cd` | 16 (smoke `ARGS`) | `--timeout 150` | `--timeout 900` |
| same | pinned | 17 (full `ARGS`) | `--timeout 150` | `--timeout 900` |
| `DEVIATION-6.md` | frozen in FROZEN-6 | 30 ("the 150 s timeout ... unchanged") | not edited; superseded by DEVIATION-7 | |

- Not changed: `run_full.py` default 180 (line 431, overridden by the explicit flag), `cursor_llm.py` `INFRA_RETRIES = 2` (line 29), and per-attempt use (line 469). `leak_probe.py` (default 180) and `role_probe.py` (default 150) are probes and stay out of scope.
- Process: re-pin `launch5b.sh` (new sha), add DEVIATION-7.md to a FROZEN-7 manifest (FROZEN-6 set + DEVIATION-7.md + the recipe), QA review, then smoke, then full.

## 6. Runtime for the full recipe (30 runs, concurrency 5)

Structure (from frozen code and loops):
- One run = 5 seeds, run sequentially. One seed = LB-CR-1, 7 instances (cr-001..cr-007, `_run_family`), run sequentially. One instance = up to `max_iterations` iterations, 1 model call per iteration as observed for good-1-fast; thorough loops were not checked call-for-call. Iteration 1 is the initial prompt and iterations 2+ are revisions.
- `max_iterations` per loop: bad-1 1; bad-2, bad-3, bad-4, bad-5, good-1, good-5 3; good-3 5; good-2, good-4 8. Sum over the 10 loops = 40.
- Max calls = 3 runs x 35 (seed x instance) x 40 = **4200**. Of these, initial = 30 runs x 35 = **1050**, revision <= **3150**.

**Worst case** (every revision call times out on all 3 attempts at 900 s; initial calls ~35 s):
- Per revision call: 3 x 900 = 2700 s.
- Serial: 3150 x 2700 + 1050 x 35 = 8,505,000 + 36,750 = 8,541,750 s.
- Across 5 slots: 8,541,750 / 5 = 1,708,350 s ≈ **474.5 h ≈ 19.8 days**.
- The longest single run (good-2 or good-4: 35 x 8 = 280 calls, 245 revisions) is 245 x 2700 + 35 x 35 = 662,725 s ≈ 184 h, so wall time is at least about 7.7 days even with perfect packing.
- In practice, early stop (success threshold, stall, bad-5's budget) cuts this a lot. This is an upper bound, not a forecast.

**Realistic estimate** (observed times):
- Call count from acceptance-4 r0 run files (10 runs, 448 calls), x3 runs ≈ 1344 calls: 1050 initial + ~294 revisions. acceptance-4 r0 includes INFRA-FAIL seeds, so this undercounts.
- Initial ~35 s (smokes: 26.5-42.9 s). Revision ~363 s (diag mean of 548.4, 234.5 and 305.6).
- Serial: 1050 x 35 + 294 x 363 = 36,750 + 106,722 = 143,472 s; / 5 = 28,694 s ≈ **8.0 h**.
- If revisions are as frequent as the worst-case structure allows at the realistic time (3150 x 363 + 36,750 = 1,180,200 s / 5) ≈ 65.6 h.
- Reasonable planning range: **8 to 24 h**, with progress checks every 30 min.

## 7. Memory floor during long-held slots

- The 6144 MB floor (`check_launch_memory`) and the wrapper's 60 s hold plus recheck run **once, before launch only**. `run_full.py` has no running memory guard; only the trial harness had one (1229 MB trip).
- With 900 s calls, each of the 5 slots holds cursor-agent, its node worker-server and a typescript-language-server for up to 15 min, instead of up to 2.5 min. DEVIATION-6 estimates about 2200 MB for 5 calls. The calls overlap far more, so the plateau lasts longer, and other agents, Chrome or Xvfb growing in that window can push MemAvailable toward OOM. Nothing would stop the run, and failures would show only as process_error or timeouts.
- Proposed (wrapper-only, no frozen change, needs QA): run a read-only MemAvailable sampler next to the full run (e.g. every 30 s to `$O/memwatch.log`, like `memfloor-watch`), and report it with progress. Any abort rule (e.g. alert below 1229 MB) is for QA to decide.
