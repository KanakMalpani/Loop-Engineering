#!/bin/bash
# LoopBench acceptance attempt 5c launcher CANDIDATE (DEVIATION-7 draft; FROZEN-7 placeholders).
# Usage: launch5c.sh smoke <B> | launch5c.sh full <B>
# vs launch5b.sh @84121cd: --timeout 900; FROZEN-7 identity pins (placeholders until the freeze);
# full mode only: 36 h wall-clock cap (exit 13), abort at 3 INFRA-FAIL runs (exit 14),
# 30 s MemAvailable sampler with abort below 2048 MB (exit 15). Aborted/capped runs are INCOMPLETE, never graded.
# Differences vs launch5.sh: PYTHONPATH = $B/wt/packages/*, first-party package guard,
# pip freeze, smoke gate, post-run error / zero-call checks. Frozen code untouched.
set -u
MODE="${1:-}"; B="${2:-}"
case "$MODE" in smoke|full) ;; *) echo "usage: $0 smoke|full <B>" >&2; exit 2;; esac
for v in PKG_ROOT GUARD_ONLY HOLD_ONLY MEMINFO; do
  [ -n "${!v+x}" ] && { echo "REFUSED: test-hook env var $v is set; the pinned wrapper has no test hooks" >&2; exit 12; }
done
[ -d "$B/wt" ] || { echo "no $B/wt" >&2; exit 2; }
B=$(realpath "$B"); W=$B/wt/benchmarks/loopbench-validity; PY=/workspace/le-venv/bin/python
SELF=$(readlink -f "$0"); ist() { TZ=Asia/Kolkata date '+%Y-%m-%d %H:%M:%S IST'; }
COMMON="--confirm-acceptance --model grok-4.7-high --task LB-CR-1"
if [ "$MODE" = smoke ]; then O=$B/smoke-out; ARGS="$COMMON --loops good-1-fast --seeds 0 --runs 1 --max-concurrency 5 --timeout 900 --outdir $O"
else O=$B/full-out; ARGS="$COMMON --seeds 0,1,2,3,4 --runs 3 --max-concurrency 5 --timeout 900 --outdir $O"; fi
if [ "$MODE" = full ] && [ ! -f "$B/smoke-out/SMOKE_PASS" ]; then echo "FULL_REFUSED: no $B/smoke-out/SMOKE_PASS" >&2; exit 7; fi
[ -e "$O" ] && { echo "refusing: $O exists (never overwrite)" >&2; exit 2; }
mkdir -p "$O"; L=$O/launch.log
log() { echo "$*" >> "$L"; }
fail() { log "PRECHECK_FAIL: $2"; echo "PRECHECK_FAIL: $2" >&2; exit "$1"; }

# 1. pinned env
unset CURSOR_LLM_MODEL CURSOR_LLM_INFRA_RETRIES CURSOR_LLM_ISOLATE CURSOR_AGENT_BIN CURSOR_TRIAL_BIN MIN_MB
# 2. PYTHONPATH from every package dir in the worktree 
PKGS=$(realpath "$B/wt/packages")
export PYTHONPATH=$(ls -d "$PKGS"/*/ | sed 's:/$::' | sort | paste -sd:)
log "mode: $MODE"; log "launch IST: $(ist)"; log "PYTHONPATH: $PYTHONPATH"
# 2b. exact FROZEN-6 identity
# FROZEN-7 pins: filled in by the re-freeze commit, after Kanak's approval and QA review.
FROZEN_HEAD=__FROZEN7_HEAD__
FROZEN_MANIFEST=FROZEN-7.sha256
FROZEN_MANIFEST_SHA=__FROZEN7_MANIFEST_SHA__
FROZEN_MANIFEST_N=__FROZEN7_MANIFEST_N__
case "$FROZEN_HEAD$FROZEN_MANIFEST_SHA$FROZEN_MANIFEST_N" in *__FROZEN7_*) fail 2 "CANDIDATE_NOT_FROZEN: FROZEN-7 pins are placeholders";; esac
h=$(git -C "$B/wt" rev-parse HEAD 2>/dev/null); log "worktree HEAD: $h (required $FROZEN_HEAD)"
[ "$h" = "$FROZEN_HEAD" ] || fail 5 "worktree HEAD $h != $FROZEN_HEAD"
ms=$(sha256sum "$W/$FROZEN_MANIFEST" 2>/dev/null | cut -c1-64); log "$FROZEN_MANIFEST sha256: $ms (required $FROZEN_MANIFEST_SHA)"
[ "$ms" = "$FROZEN_MANIFEST_SHA" ] || fail 6 "$FROZEN_MANIFEST sha256 $ms != $FROZEN_MANIFEST_SHA"
# 3. first-party package guard: must resolve under $B/wt/packages/
cd "$W" || fail 2 "cd $W"
for m in loopgym loopbench loopotel loopnet; do
  f=$("$PY" -c "import os,$m; print(os.path.realpath($m.__file__))" 2>>"$L") || fail 8 "$m import failed"
  log "pkg $m $f $(sha256sum "$f" | cut -c1-64)"
  case "$f" in "$PKGS"/*) ;; *) fail 8 "$m resolves outside $PKGS/ ($f)";; esac
done
# 4. pip freeze
PF=$B/pip-freeze.txt; [ -e "$PF" ] && PF=$B/pip-freeze-$MODE.txt
if "$PY" -m pip freeze > "$PF" 2>>"$L" && [ -s "$PF" ]; then src="pip freeze"
else # venv pip is broken (pip._internal.operations.build missing); list installed dists instead
  "$PY" - > "$PF" 2>>"$L" <<'MDEOF' || fail 9 "importlib.metadata listing incomplete (missing name/version/location)"
import importlib.metadata as m, sys
rows, bad = [], 0
for d in m.distributions():
    n, v, loc = d.metadata["Name"], d.version, d.locate_file("")
    if not n or not v or not str(loc):
        bad += 1; print(f"MISSING name={n!r} version={v!r} location={loc!r}", file=sys.stderr); continue
    rows.append(f"{n}=={v} @ {loc}")
print("\n".join(sorted(rows)))
sys.exit(1 if bad or not rows else 0)
MDEOF
  src="importlib.metadata name==version @ location (pip freeze FAILED)"; fi
[ -s "$PF" ] || fail 9 "could not list installed packages"
log "pip freeze: $PF via $src $(sha256sum "$PF" | cut -c1-64) ($(wc -l < "$PF") lines)"
# 5. manifest
ok=$(cd "$B/wt" && sha256sum -c "benchmarks/loopbench-validity/$FROZEN_MANIFEST" 2>/dev/null | grep -c ': OK$'); n=$(grep -c . "$FROZEN_MANIFEST")
log "manifest sha256: $(sha256sum "$FROZEN_MANIFEST" | cut -c1-64)"; log "manifest check: $ok/$n OK"
[ "$ok" = "$FROZEN_MANIFEST_N" ] && [ "$n" = "$FROZEN_MANIFEST_N" ] || fail 3 "manifest $ok/$n (required $FROZEN_MANIFEST_N)"
# 6. memory floor
avail_mb() { awk '/^MemAvailable:/{print int($2/1024); exit}' /proc/meminfo 2>/dev/null || true; }
mem=$(avail_mb); floor=$(grep -oP '^MIN_AVAILABLE_MB = \K\d+' run_full.py)
log "MemAvailable: $mem MB (MIN_MB unset; run_full MIN_AVAILABLE_MB=$floor)"
[ "$floor" = 6144 ] || fail 4 "MIN_AVAILABLE_MB=$floor"; [ "$mem" -ge 6144 ] || fail 4 "MemAvailable $mem < 6144"
# 6b. smoke and full: 60 s sustained hold + pre-launch recheck, as run_trial5b.sh @ bce9f60
#     (MIN_MB 6144, SUSTAIN_S 60, SAMPLE_S 5, WAIT_MAX_S 1200; samples in $O/memwait.log)
{
  MIN_MB=6144; SUSTAIN_S=60; SAMPLE_S=5; WAIT_MAX_S=1200; start=$(date +%s); good_since=""
  while :; do
    now=$(date +%s); [ $((now - start)) -ge "$WAIT_MAX_S" ] && fail 4 "memory not sustained >=$MIN_MB for $SUSTAIN_S s within $WAIT_MAX_S s"
    m=$(avail_mb); case "$m" in ''|*[!0-9]*) m=0;; esac
    echo "$(ist) availMB=$m" >> "$O/memwait.log"
    if [ "$m" -ge "$MIN_MB" ]; then
      [ -z "$good_since" ] && { good_since=$now; log "hold start availMB=$m $(ist)"; }
      [ $((now - good_since)) -ge "$SUSTAIN_S" ] && { log "memory sustained >=$MIN_MB for $SUSTAIN_S s (last availMB=$m $(ist))"; break; }
    else good_since=""; fi
    sleep "$SAMPLE_S"
  done
  m=$(avail_mb); case "$m" in ''|*[!0-9]*) m=0;; esac
  [ "$m" -ge "$MIN_MB" ] || fail 4 "pre-launch recheck availMB=$m < $MIN_MB"
  log "pre-launch recheck availMB=$m PASS $(ist)"
}
# 7. identity
log "repo head: $(git -C /workspace/Loop-Engineering rev-parse HEAD)"; log "worktree head: $(git rev-parse HEAD) (FROZEN-7 $FROZEN_HEAD)"
log "cursor-agent: $(command -v cursor-agent) $(cursor-agent --version 2>&1)"
log "command: cd $W && PYTHONPATH=$PYTHONPATH $PY run_full.py $ARGS"
# 8. shas
FILES="$W/run_full.py $W/cursor_llm.py $SELF"; PRE=$(sha256sum $FILES); log "pre-run sha256:"; log "$PRE"

RUN_TAG=lb5c-$(cat /proc/sys/kernel/random/uuid); log "run tag: LB5C_RUN_TAG=$RUN_TAG"
reap_tagged() {  # kill only processes carrying this run's tag (inherited env); never anything else
  local p n=0
  for p in /proc/[0-9]*; do
    { tr '\0' '\n' < "$p/environ"; } 2>/dev/null | grep -qx "LB5C_RUN_TAG=$RUN_TAG" || continue
    kill -KILL "${p#/proc/}" 2>/dev/null && n=$((n+1))
  done
  log "reap tagged ($1): killed $n"
}
why=""
if [ "$MODE" = smoke ]; then
  LB5C_RUN_TAG=$RUN_TAG "$PY" run_full.py $ARGS; rc=$?
else
  # full-mode guards, constants hardcoded
  CAP_S=129600          # 36 h = 1.5 x 24 h planning upper end
  POLL_S=30             # sampler / monitor period
  MEM_ABORT_MB=2048     # wrapper abort floor while running (launch floor 6144 still applies above)
  INFRA_RUNS_ABORT=3    # stop rule: runs whose every seed is INFRA-FAIL
  LB5C_RUN_TAG=$RUN_TAG setsid "$PY" run_full.py $ARGS & RP=$!
  log "run_full pid=pgid=$RP start $(ist); cap ${CAP_S}s, mem abort <${MEM_ABORT_MB} MB, infra-run abort at $INFRA_RUNS_ABORT"
  t0=$(date +%s)
  while kill -0 "$RP" 2>/dev/null; do
    m=$(avail_mb); case "$m" in ''|*[!0-9]*) m=0;; esac
    echo "$(ist) availMB=$m" >> "$O/memsample.log"
    if [ "$m" -lt "$MEM_ABORT_MB" ]; then why=mem; break; fi
    nf=$("$PY" - "$O" <<'PYEOF'
import json,sys,glob
n=0
for f in glob.glob(sys.argv[1]+"/*-r*.json"):
    try: d=json.load(open(f))
    except Exception: continue
    seeds=len(d.get("seeds") or []) or len(d.get("by_seed") or {})
    if seeds and d.get("n_infra_fail",0)==seeds: n+=1   # every seed INFRA-FAIL
print(n)
PYEOF
)
    if [ "${nf:-0}" -ge "$INFRA_RUNS_ABORT" ]; then why=infra; break; fi
    if [ $(( $(date +%s) - t0 )) -ge "$CAP_S" ]; then why=cap; break; fi
    for _ in $(seq "$POLL_S"); do kill -0 "$RP" 2>/dev/null || break; sleep 1; done
  done
  if [ -n "$why" ]; then
    log "guard fired: $why at $(ist) (availMB=$m, infra_runs=${nf:-0}); stopping pgid $RP"
    kill -TERM -- -"$RP" 2>/dev/null
    for _ in $(seq 30); do kill -0 "$RP" 2>/dev/null || break; sleep 1; done
    kill -KILL -- -"$RP" 2>/dev/null
  fi
  wait "$RP"; rc=$?
fi
reap_tagged "after run"
log "run rc: $rc"; log "end IST: $(ist)"
POST=$(sha256sum $FILES); log "post-run sha256:"; log "$POST"
bad=""
if [ "$PRE" = "$POST" ]; then log "post-run sha check: MATCH"; else log "post-run sha check: CHANGED (run VOID)"; bad="$bad sha_changed"; fi
[ "$rc" = 0 ] || bad="$bad rc=$rc"
# post-run results (wrapper-only checks)
res=$("$PY" - "$O" <<'PYEOF'
import json,sys,glob
fs=sorted(glob.glob(sys.argv[1]+"/*-r*.json")); e=i=k=c=allerr=0
for f in fs:
    d=json.load(open(f)); e+=d.get("n_error",0); i+=d.get("n_infra_fail",0); k+=d.get("n_ok",0); c+=len(d.get("calls",[]))
    allerr+= (d.get("n_ok",0)==0 and d.get("n_error",0)>0)
r=[]
if not fs: r.append("NO_RUN_FILES")
if e: r.append(f"n_error={e}")
if i: r.append(f"n_infra_fail={i}")
if c==0: r.append("ZERO_MODEL_CALLS")
if fs and allerr==len(fs): r.append("ALL_RUNS_ERROR")
print(f"runs={len(fs)} n_ok={k} n_error={e} n_infra_fail={i} calls={c} runs_all_error={allerr}|{' '.join(r)}")
PYEOF
) || res="|RESULT_CHECK_FAILED"
log "results: ${res%%|*}"; bad="$bad ${res#*|}"; bad=$(echo $bad)
case "$why" in
  cap)   log "RUN_INCOMPLETE: wall-clock cap 36h"; echo "RUN_INCOMPLETE: wall-clock cap 36h" >&2; echo INCOMPLETE > "$O/INCOMPLETE"; exit 13;;
  infra) log "RUN_ABORTED: 3 INFRA-FAIL runs"; echo "RUN_ABORTED: 3 INFRA-FAIL runs" >&2; echo INCOMPLETE > "$O/INCOMPLETE"; exit 14;;
  mem)   log "RUN_ABORTED: mem <2048"; echo "RUN_ABORTED: mem <2048" >&2; echo INCOMPLETE > "$O/INCOMPLETE"; exit 15;;
esac
if [ "$MODE" = smoke ]; then
  if [ -z "$bad" ]; then echo "$(ist) ${res%%|*}" > "$O/SMOKE_PASS"; log "SMOKE_PASS"; exit 0; fi
  log "SMOKE_FAIL: $bad"; echo "SMOKE_FAIL: $bad" >&2; exit 10
fi
[ -z "$bad" ] || { log "RUN_HAS_ERRORS: $bad"; echo "RUN_HAS_ERRORS: $bad" >&2; exit 11; }
log "RUN_CLEAN"; exit "$rc"
