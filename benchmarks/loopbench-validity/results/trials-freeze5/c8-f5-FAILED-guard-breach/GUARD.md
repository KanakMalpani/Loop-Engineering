# Harness guard in c8-f5 (why the trial was killed and the reaper did not run)

**Where:** `/workspace/concurrency-investigation/guard.sh`, sourced by the trial driver `results/trials-freeze5/run_trial5.sh`. Harness only; not part of FROZEN-5.

**Start gate (`guard_start`):** before a trial, waits up to 45 min (30 s samples) until MemAvailable > 2048 MB and 1-min load < 14. run_trial5.sh then also waited (30 s samples, max 20 min) for MemAvailable >= 4096 MB on a single sample. c8-f5 passed it at 23:58:53 IST; the before-snapshot read 4094 MB a second later.

**Running guard (`guard_ok`):** polled every 10 s while any fcall5.py driver is alive. Breach if 1-min load > 14 **or MemAvailable < 1229 MB** (the AE-pull priority floor). Each breach is appended to `guard.log` (UTC timestamp).

**What it kills on breach:** only the trial's own driver processes: `pkill -f "fcall5.py <trial dir>/call-"` (SIGTERM), then the mon.sh sampler, then `exit 3`. It never touches the pull, Chrome or untagged processes. The decoy was not killed by the guard and was not reported by the script, because the exit path skips the decoy check.

**What happened:** samples at 23:58:54 / 23:59:04 / 23:59:14 IST read 4073 / 2361 / 994 MB (resources.log; pull at 3 workers, Chrome+Xvfb about 7 GB RSS). Breach at 23:59:14 IST (guard.log: `2026-10-21T18:29:14+00:00 GUARD BREACH load=8.44 availMB=982`).

**Why the reaper did not run:** the always-on tag reaper lives in frozen `cursor_llm.py` (`_run_once` finally block -> `reap_tag`), inside each fcall5.py Python process. SIGTERM's default action ends Python immediately: no exception, no `finally`, so no reaper pass and no KILL/DONE lines (each reap.log has only START). cursor-agent runs in its own session (`start_new_session=True`), so killing the driver doesn't take its children with it. The result was 32 tagged processes and 8 worker-servers left behind (post-breach.snap). 10 still-tagged processes were then SIGKILLed by hand by tag (manual-cleanup.log, annotated in manual-cleanup.annotated.log); post-cleanup.snap: tagged 0, worker-servers 0.

**Follow-up (harness only, run_trial5b.sh):** on a breach it sends SIGINT so Python unwinds and the frozen reaper runs, then takes an after-breach snapshot. It also requires memory to stay >= 4096 MB for 60 s, re-checks just before launch, requires PULL_FINISHED and no pull process, and reports the decoy on every exit path.
