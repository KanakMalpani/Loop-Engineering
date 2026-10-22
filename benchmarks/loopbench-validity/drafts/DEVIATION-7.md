# DEVIATION-7 (DRAFT): per-attempt model-call timeout 150 s -> 900 s, plus three wrapper-only run guards

Status: DRAFT - pending Kanak's approval and QA review. Not frozen, not pinned, nothing launched under it. FROZEN-6 (`f1f5ef9`, manifest `81b977bd…1661`) and `launch5b.sh` (`84121cd`, sha `661d7479…`) are unchanged. FROZEN-7 does not exist yet.

## 0. Grading rules (decided up front)

- Wall-clock cap hit (exit 13, `RUN_INCOMPLETE: wall-clock cap 36h`), memory abort (exit 15, `RUN_ABORTED: mem <2048`) or 3-INFRA-FAIL abort (exit 14, `RUN_ABORTED: 3 INFRA-FAIL runs`) means **INCOMPLETE**: never graded, no partial grade. All outputs are kept and `$O/INCOMPLETE` is written.
- The 3-INFRA-FAIL threshold is a stop rule only. Any single INFRA-FAIL seed anywhere still means `RUN_HAS_ERRORS` (exit 11) and a **FAIL**.
- 900 s is the **final** timeout increase. A timeout at 900 s in the counted run is a FAIL, or a new DEVIATION decided **before** any rerun. There will be no further silent bump.
- Order: the FROZEN-7 freeze, then the wrapper pin, then a **smoke at 900 s on the FROZEN-7 pin that must reach SMOKE_PASS**, then the full run. The full run refuses without `SMOKE_PASS` (exit 7, unchanged).

Everything in `DEVIATION.md` through `DEVIATION-6.md` still applies unless changed below.

## 1. Scope

- `--timeout` on the attempt-5 launch command changes from 150 to 900 (seconds). That is the only benchmark-facing change. The three run guards in section 8 are wrapper-only and don't change how any model call is made or scored.
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
- DEVIATION-6 line 30 ("the 150 s timeout ... unchanged") is **superseded by this document**. DEVIATION-6.md itself is not edited, because it's hashed in FROZEN-6 and an edit would change that hash. If QA prefers an in-file "SUPERSEDED by DEVIATION-7" note, it goes into the FROZEN-7 copy with a new hash.
- Process: section 9.

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

- The 6144 MB floor (`run_full.check_launch_memory`, `MIN_AVAILABLE_MB = 6144`) and the wrapper's 60 s hold plus recheck still apply, once, before launch. They are unchanged.
- **Correction to the request premise:** `run_full.py` and `cursor_llm.py` have **no** running memory guard. `git grep 1229` finds the 1229 MB figure only in DEVIATION-6 prose ("the harness running guard"), meaning the c8 trial harness, not run_full. So the 2048 MB sampler (section 8.3) is a wrapper rule. It is the only running memory guard for the full run, and it sits above the old harness trip of 1229 MB.
- With 900 s calls, each of the 5 slots holds cursor-agent, its node worker-server and a typescript-language-server for up to 15 min instead of 2.5 min. DEVIATION-6 estimates about 2200 MB for 5 calls.

## 8. Wrapper-only run guards (candidate `drafts/launch5c.sh`, full mode)

All constants are hardcoded. Each guard is checked every 30 s while run_full runs. run_full is started with `setsid`, so its PID is its process-group ID. When a guard fires, the wrapper sends SIGTERM to that group only, waits up to 30 s, then SIGKILLs the group. Every run exports `LB5C_RUN_TAG=lb5c-<uuid>`, which bwrap and cursor-agent inherit. After the run, whether normal or aborted, any process still carrying that exact tag is SIGKILLed. Nothing else is ever signalled. The post-run sha check and results line are logged as usual, then the guard's exit code wins.

| guard | constant | fires when | log line | exit |
|---|---|---|---|---|
| wall-clock cap | `CAP_S=129600` (36 h) | 36 h since run_full start | `RUN_INCOMPLETE: wall-clock cap 36h` | 13 |
| infra-fail stop | `INFRA_RUNS_ABORT=3` | 3 run files are INFRA-FAIL runs (definition below) | `RUN_ABORTED: 3 INFRA-FAIL runs` | 14 |
| memory | `MEM_ABORT_MB=2048`, every 30 s to `$O/memsample.log` | MemAvailable < 2048 MB | `RUN_ABORTED: mem <2048` | 15 |

### 8.1 Wall-clock cap rationale

36 h = 1.5 x 24 h, the upper end of the realistic planning range in section 6 (8-24 h). It is far below the worst-case bound (~474 h), which is the point: a run that slow is systemically broken and must not be graded.

### 8.2 INFRA-FAIL run definition (chosen) and the alternative

- Frozen semantics: `run_full.one_run` writes `<loop>-r<k>.json` once the run finishes, with `seeds` (5), `n_ok`, `n_error`, `n_infra_fail`. A seed is INFRA-FAIL when a call still has no result after 3 attempts.
- **Chosen ("systemic"):** a run is an INFRA-FAIL run when `n_infra_fail == len(seeds)`, i.e. every one of its 5 seeds is INFRA-FAIL. That matches acceptance-4's failure mode (several run files with seeds 0-4 all INFRA-FAIL) and Engineering Lead's "systemic" intent. One slow fixture doesn't stop the whole run.
- **Alternative for QA:** a run is an INFRA-FAIL run when `n_infra_fail > 0`. That stops much sooner, after 3 runs with even one bad seed. The grade is the same either way (any INFRA-FAIL is a FAIL, section 0). The choice only changes how soon a doomed run stops.
- Limits: run files appear only when a run finishes, so the guard can't fire mid-run. At concurrency 5, up to 5 runs can be in flight when the third INFRA-FAIL file lands.

### 8.3 Memory abort rationale

- 2048 MB is below c8-f5's observed dip (3764 MB with 8 concurrent 150 s calls, `56e1cd8`), so normal load shouldn't trip it. It's also about 800 MB above the old harness trip (1229 MB), leaving room for a clean SIGTERM before OOM risk.
- It's a wrapper rule. run_full has no running guard of its own (section 7). The 6144 MB launch floor and the 60 s hold are unchanged.

### 8.4 Candidate

- `drafts/launch5c.sh`, sha256 `74d95efc81ea1e49c37e28eccc7635105934c08336ac389ba0cd9ca435eca677`, written by hand (Engineering Lead accepted hand-writing). It is **not pinned** and must not be used before FROZEN-7. Its FROZEN-7 pins are placeholders (`__FROZEN7_HEAD__`, `__FROZEN7_MANIFEST_SHA__`, `__FROZEN7_MANIFEST_N__`), and any run refuses with `PRECHECK_FAIL: CANDIDATE_NOT_FROZEN` (exit 2). That is tested.
- Diff vs the `84121cd` pin (`launch5b.sh`, `661d7479…`), 86 changed lines:
  - The header comment.
  - `--timeout 150` changes to `--timeout 900` in the smoke and full `ARGS`.
  - The identity pins change from the FROZEN-6 literals to FROZEN-7 placeholders, plus the `CANDIDATE_NOT_FROZEN` check. The manifest file and entry count are now variables (`FROZEN-7.sha256`, N).
  - The run line is replaced by: the run tag and `reap_tagged()`; smoke runs in the foreground with the tag; full runs with `setsid`, plus the 30 s monitor loop (memory sample, INFRA-FAIL run count, cap) and a clean group stop.
  - The exit-code mapping for 13, 14 and 15 is inserted before the SMOKE/RUN_HAS_ERRORS block.
  - Everything else is byte-identical: env refusal (exit 12), package guard, pip list, manifest check, 6144 floor, 60 s hold, shas MATCH/CHANGED, results checks and SMOKE gate.
- Dry tests (no model calls) on an unpinned test copy `launch5b-dev/launch5c-test.sh`, with a fake `stub_run_full.py`, shortened poll (2 s), hold (2 s) and cap (6 s), a fake meminfo, and FROZEN-6 values in place of the placeholders. The test-copy diff vs the candidate touches only those hooks (`launch5b-dev/launch5c-test-vs-candidate.diff`):
  - cap fires: rc 13, `RUN_INCOMPLETE`, INCOMPLETE marker, outputs kept.
  - 3 all-INFRA-FAIL run files: rc 14, `RUN_ABORTED: 3 INFRA-FAIL runs`.
  - 2 all-INFRA-FAIL + 1 partial: no abort, rc 11 `RUN_HAS_ERRORS: n_infra_fail=11`.
  - fake meminfo 1500 MB mid-run: rc 15, `RUN_ABORTED: mem <2048`.
  - normal completion: rc 0 `RUN_CLEAN` (full), rc 0 `SMOKE_PASS` (smoke).
  - Every run: tagged straggler (`setsid sleep 1000` from the stub) `reap tagged ... killed 1`, and 0 strays afterwards.
  - Existing guards: wrong HEAD rc 5, wrong manifest sha rc 6, package outside wt rc 8, full without SMOKE_PASS rc 7, existing outdir rc 2, hook env var on the candidate rc 12, placeholders on the candidate rc 2 `CANDIDATE_NOT_FROZEN`.

## 9. FROZEN-7 re-freeze plan (only after Kanak approves and QA accepts this draft; not done)

1. Move `drafts/DEVIATION-7.md` to `benchmarks/loopbench-validity/DEVIATION-7.md`, with status set to ACCEPTED plus the QA PASS time.
2. Write `drafts/frozen7/LAUNCH-RECIPE-attempt5c.md`: the attempt-5 command with `--timeout 900`, the section 0 grading rules and the section 8 guards. It supersedes `drafts/frozen6/LAUNCH-RECIPE-attempt5.md` for the timeout only.
3. `FROZEN-7.sha256` = the 56 FROZEN-6 entries unchanged, plus `DEVIATION-7.md`, `FROZEN-6.sha256` and `drafts/frozen7/LAUNCH-RECIPE-attempt5c.md`. That's 59 entries if nothing else changes. No `run_full.py` or `cursor_llm.py` change, and DEVIATION-6.md keeps its FROZEN-6 hash (superseded per section 5).
4. Commit as `loopbench-validity: FROZEN-7 manifest ...` with the manifest sha in the message. Gate it in a fresh worktree at that commit: manifest N/N OK, loopgym and loopbench tests, ruff, as for FROZEN-6.
5. Fill the candidate's placeholders with the FROZEN-7 commit, the manifest sha and N. Pin it byte-identical as `results/acceptance-5/launcher/launch5c.sh` plus `.sha256` in a separate commit. The wrapper can't sit inside the manifest whose commit it pins.
6. QA reviews the pinned wrapper. Then smoke on a fresh worktree at the FROZEN-7 commit (900 s) must reach SMOKE_PASS, then full. Pushes only with Kanak's approval.
