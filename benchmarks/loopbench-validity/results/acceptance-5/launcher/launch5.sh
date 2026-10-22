#!/bin/bash
# LoopBench acceptance attempt 5 wrapper (FROZEN-6 f1f5ef9). Usage: launch5.sh <base dir>
B="$1"; W=$B/wt/benchmarks/loopbench-validity; O=$B/out; L=$O/launch.log
PY=/workspace/le-venv/bin/python; SELF=$(readlink -f "$0")
FILES="$W/run_full.py $W/cursor_llm.py $SELF"
cd "$W" || exit 2
unset CURSOR_LLM_MODEL CURSOR_LLM_INFRA_RETRIES CURSOR_LLM_ISOLATE CURSOR_AGENT_BIN CURSOR_TRIAL_BIN MIN_MB
{
echo "launch IST: $(TZ=Asia/Kolkata date '+%Y-%m-%d %H:%M:%S %Z')"
echo "repo head (chore/monorepo-dryrun): $(git -C /workspace/Loop-Engineering rev-parse HEAD)"
echo "worktree head: $(git rev-parse HEAD) (FROZEN-6 commit f1f5ef9)"
echo "manifest sha256: $(sha256sum FROZEN-6.sha256 | cut -c1-64)"
echo "manifest check: $(cd ../.. && sha256sum -c benchmarks/loopbench-validity/FROZEN-6.sha256 2>/dev/null | grep -c ': OK$')/$(grep -c . FROZEN-6.sha256) OK"
echo "pre-run sha256:"; sha256sum $FILES | sed 's/^/  /'
echo "MemAvailable: $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) MB (MIN_MB unset; run_full MIN_AVAILABLE_MB=$(grep -oP '^MIN_AVAILABLE_MB = \K\d+' run_full.py))"
echo "cursor-agent: $(command -v cursor-agent) $(cursor-agent --version 2>&1)"
echo "pull.log: $(grep -c . /workspace/oa/pull/pull.log) lines; $(grep PULL_FINISHED /workspace/oa/pull/pull.log)"
echo "pull procs: $(pgrep -fa 'pull.sh' | grep -v pgrep | wc -l)"
echo "command: cd $W && $PY run_full.py --confirm-acceptance --model grok-4.7-high --task LB-CR-1 --seeds 0,1,2,3,4 --runs 3 --max-concurrency 5 --timeout 150 --outdir $O"
} > "$L"
PRE=$(sha256sum $FILES)
$PY run_full.py --confirm-acceptance --model grok-4.7-high --task LB-CR-1 --seeds 0,1,2,3,4 --runs 3 --max-concurrency 5 --timeout 150 --outdir "$O"
rc=$?
echo "run rc: $rc" >> "$L"
echo "end IST: $(TZ=Asia/Kolkata date '+%Y-%m-%d %H:%M:%S %Z')" >> "$L"
POST=$(sha256sum $FILES)
echo "post-run sha256:" >> "$L"; echo "$POST" | sed 's/^/  /' >> "$L"
if [ "$PRE" = "$POST" ]; then echo "post-run sha check: MATCH" >> "$L"; else echo "post-run sha check: CHANGED (run VOID)" >> "$L"; fi
cp -n results/launch-memcheck.log "$O/" 2>/dev/null
exit $rc
