#!/bin/bash
# c8-f5 on FROZEN-6. Harness = run_trial5b.sh from bce9f60, MIN_MB unset (default 6144), WAIT_MAX_S=1800 (30 min).
set -u
unset MIN_MB
R=/workspace/Loop-Engineering/benchmarks/loopbench-validity
H=/workspace/f6/run_trial5b-bce9f60.sh
git -C /workspace/Loop-Engineering show bce9f60:benchmarks/loopbench-validity/results/trials-freeze5/harness-5b/run_trial5b.sh > $H; chmod +x $H
TSIST=$(TZ=Asia/Kolkata date +%Y%m%d-%H%M%S-IST); OUT=/home/box/le-runs/c8-f5-$TSIST; mkdir -p $OUT/c8-f5
LL=$OUT/c8-f5/launch.log
DRV=/workspace/concurrency-investigation/frozen-trial/fcall5.py; DRV_SHA=7a01b40533cb39b206aa3386316c9c7acf9cdc502487b06e4cb8dd90bb34bdbb; LE=/workspace/le-trial-f1f5ef9/benchmarks/loopbench-validity
{
echo "# c8-f5 launch log (FROZEN-6 f1f5ef968715edf141f6995fd0b650fadd7eb216, worktree /workspace/le-trial-f1f5ef9), written $(TZ=Asia/Kolkata date --iso-8601=seconds)"
echo "FROZEN-6 commit: $(git -C /workspace/le-trial-f1f5ef9 rev-parse HEAD)"
echo "harness: git show bce9f60:.../harness-5b/run_trial5b.sh sha256 $(sha256sum $H | cut -c1-64)"
echo "fcall5.py sha256 $(sha256sum /workspace/concurrency-investigation/frozen-trial/fcall5.py | cut -c1-64) WT=$(grep '^WT' /workspace/concurrency-investigation/frozen-trial/fcall5.py)"
(cd /workspace/le-trial-f1f5ef9 && echo "FROZEN-6.sha256 check: $(sha256sum -c benchmarks/loopbench-validity/FROZEN-6.sha256 | grep -c ': OK$') OK of $(wc -l < benchmarks/loopbench-validity/FROZEN-6.sha256), failures: $(sha256sum -c --quiet benchmarks/loopbench-validity/FROZEN-6.sha256 2>&1 | wc -l)")
echo "cursor-agent --version: $(cursor-agent --version 2>&1)"
PL=/workspace/oa/pull/pull.log
echo "pull.log: $( [ -r $PL ] && wc -l < $PL || echo missing ) lines; PULL_FINISHED: $(grep -E ' PULL_FINISHED$' $PL 2>/dev/null | tail -1 || true) (informational; c8-f5 does not need out/)"
echo "--- ps (pull.sh|curl|mem_watch):"; ps -eo pid=,args= | grep -E 'pull\.sh|(^| |/)curl |mem_watch\.sh' | grep -v grep || echo "none"
echo "pgrep -f mem_watch.sh: $(pgrep -f mem_watch.sh | grep -v $$ || echo none)"
echo "MIN_MB: ${MIN_MB-unset} (harness default 6144: $(grep -o 'MIN_MB=${MIN_MB:-[0-9]*}' $H))"
echo "WAIT_MAX_S=1800"
echo "MemAvailable MB: $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; free -m
echo "driver (run by harness): $DRV sha256 $(sha256sum $DRV|cut -c1-64) expected $DRV_SHA (committed 2bd5d6b results/c8-f5/driver/fcall5.py)"
echo "driver diff vs tracked trials-freeze5/fcall5.py (2476c0c1...):"
diff -u $LE/results/trials-freeze5/fcall5.py $DRV || true
echo "frozen cursor_llm import: $LE/cursor_llm.py sha256 $(sha256sum $LE/cursor_llm.py|cut -c1-64)"
echo "c8.sh sha256 $(sha256sum /workspace/f6/c8.sh|cut -c1-64); c8-f5-home.sh sha256 $(sha256sum "$0"|cut -c1-64)"
diff -u /workspace/f6/c8.sh "$0" || true
echo "flag 1 resolved: probe run reap.log was overwritten, so leak-probe.json reap_kills:4 stands as its record; c8-f5 uses per-call append-only reap logs ($OUT/c8-f5/call-N/reap.log, frozen cursor_llm.py opens it in append mode)"
echo "hold/recheck: harness run_trial5b.sh does the 60 s sustained-memory hold (SUSTAIN_S=60, MIN_MB 6144) and pre-launch recheck (ABORT exit 8 below floor); see $OUT/c8-f5/orchestrator.log and memwait.log"
echo "calls: 8 concurrent"
} > $LL 2>&1
if [ "$(sha256sum $DRV|cut -c1-64)" != "$DRV_SHA" ]; then echo "$(TZ=Asia/Kolkata date --iso-8601=seconds) ABORT driver sha mismatch, not launching" >> $LL; exit 9; fi
OUT_BASE=$OUT WAIT_MAX_S=1800 $H c8-f5 8; rc=$?
echo "$(TZ=Asia/Kolkata date --iso-8601=seconds) run_trial5b.sh exit=$rc" >> $LL
P2=$(sha256sum $DRV|cut -c1-64); [ "$P2" = "$DRV_SHA" ] && S=MATCH || S="CHANGED (run VOID)"; echo "driver sha post-run: $P2 $S" >> $LL
