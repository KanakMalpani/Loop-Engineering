#!/bin/bash
# Counted trial through the FROZEN path. usage: run_trial5b.sh NAME N
# Same behaviour as run_trial5.sh, plus pull-finished preflight, sustained-memory
# gate, dry-run, and SIGINT unwind on guard breach.
set -u
CI=/workspace/concurrency-investigation
cd "$CI"
. ./guard.sh

MEMINFO=${MEMINFO:-/proc/meminfo}
PULL_LOG=${PULL_LOG:-/workspace/oa/pull/pull.log}
PULL_DIR=${PULL_DIR:-/workspace/oa/pull}
WATCHER_NAME=${WATCHER_NAME:-mem_watch.sh}
SUSTAIN_S=${SUSTAIN_S:-60}
SAMPLE_S=${SAMPLE_S:-5}
MIN_MB=${MIN_MB:-6144}
WAIT_MAX_S=${WAIT_MAX_S:-1200}
DRY_RUN=${DRY_RUN:-0}
OUT_BASE=${OUT_BASE:-/workspace/concurrency-investigation/frozen-trial}
PULL_CURL_MATCH=${PULL_CURL_MATCH:-openalex}
SKIP_GUARD_START=${SKIP_GUARD_START:-0}

NAME=$1
N=$2
D=$OUT_BASE/$NAME
mkdir -p "$D"
L=$D/orchestrator.log
P=/workspace/le-venv/bin/python
DECOY=""
M=""
PULL_PID=""

ts() { TZ=Asia/Kolkata date --iso-8601=seconds; }
log() { echo "$(ts) $*" >> "$L"; }

avail_mb() {
  awk '/^MemAvailable:/{print int($2/1024); exit}' "$MEMINFO" 2>/dev/null || true
}

cleanup() {
  if [ -n "${DECOY:-}" ]; then
    local alive=no
    if kill -0 "$DECOY" 2>/dev/null; then
      alive=yes
    fi
    log "decoy pid=$DECOY alive=$alive"
    kill "$DECOY" 2>/dev/null || true
    wait "$DECOY" 2>/dev/null || true
    DECOY=""
  fi
  if [ -n "${M:-}" ]; then
    kill "$M" 2>/dev/null || true
    wait "$M" 2>/dev/null || true
    M=""
  fi
}
trap cleanup EXIT

counts() {
  ./snap.sh "$1"
  echo "tagged=$(awk '$2!="-"' "$1" | wc -l) worker_servers=$(pgrep -fc 'index.js worker-server' || true)"
}

pull_pid_alive() {
  local pid
  PULL_PID=""
  [ -r "$CI/raw/pull-pid" ] || return 1
  pid=$(awk 'NR==1{print $1; exit}' "$CI/raw/pull-pid" 2>/dev/null || true)
  case "$pid" in
    ''|*[!0-9]*) return 1 ;;
  esac
  [ -r "/proc/$pid/comm" ] || return 1
  PULL_PID=$pid
  return 0
}

pull_worker_count() {
  local xpid n
  xpid=$(pgrep -P "$PULL_PID" xargs 2>/dev/null | head -n1 || true)
  if [ -z "$xpid" ]; then
    echo 0
    return 0
  fi
  n=$(pgrep -P "$xpid" -c 2>/dev/null || true)
  [ -n "$n" ] || n=0
  echo "$n"
}

pull_sha() {
  sha256sum "$PULL_DIR/pull.sh" 2>/dev/null | awk 'NR==1{print substr($1,1,64); exit}' || true
}

log_pull_intro() {
  if pull_pid_alive; then
    log "pull pid=$PULL_PID workers=$(pull_worker_count) pull.sh sha=$(pull_sha)"
  else
    log "pull: finished, no process"
  fi
}

log_pull_after() {
  if pull_pid_alive; then
    log "pull workers at after-snapshot=$(pull_worker_count) pull.sh sha=$(pull_sha)"
  else
    log "pull: finished, no process"
  fi
}

fcall_driver_pids() {
  local pid args
  while read -r pid args; do
    [ -n "${pid:-}" ] || continue
    case "$args" in
      *"fcall5.py $D/call-"*)
        case "$args" in
          pgrep*|grep\ *|awk\ *|ps\ *) continue ;;
        esac
        printf '%s\n' "$pid"
        ;;
    esac
  done < <(ps -eo pid=,args=)
}

on_breach() {
  local pids left i
  log "GUARD BREACH during trial - killing our trial calls"
  pids=$(fcall_driver_pids | tr '\n' ' ')
  log "sending SIGINT to fcall5 drivers: ${pids:-none}"
  if [ -n "$pids" ]; then
    # shell word-split is the pid list we just collected
    kill -INT $pids 2>/dev/null || true
  fi
  left="pending"
  for i in $(seq 1 20); do
    left=$(fcall_driver_pids | tr '\n' ' ')
    if [ -z "$left" ]; then
      log "fcall5 drivers exited within ${i}s after SIGINT"
      break
    fi
    sleep 1
  done
  left=$(fcall_driver_pids | tr '\n' ' ')
  if [ -n "$left" ]; then
    log "SIGTERM remaining fcall5 drivers after 20s: $left"
    kill -TERM $left 2>/dev/null || true
  fi
  log "after-breach snapshot: $(counts "$D/after-breach.snap")"
  exit 3
}

check_pull_finished() {
  local finished
  finished=$(grep -E ' PULL_FINISHED$' "$PULL_LOG" 2>/dev/null | tail -n 1 || true)
  if [ -z "$finished" ]; then
    log "ABORT PULL_FINISHED missing"
    exit 5
  fi
  log "PULL_FINISHED at ${finished% PULL_FINISHED}"
}

check_no_pull_process() {
  local target pid args cwd base
  local pull_hits="" curl_hits="" np=0 nc=0
  target=$(readlink -f "$PULL_DIR")
  while read -r pid args; do
    [ -n "${pid:-}" ] || continue
    if [ "$args" = "bash pull.sh" ]; then
      cwd=$(readlink -f "/proc/$pid/cwd" 2>/dev/null || true)
      if [ "$cwd" = "$target" ]; then
        pull_hits="$pull_hits $pid"
        np=$((np + 1))
      fi
    fi
    base=${args%% *}
    base=${base##*/}
    if [ "$base" = "curl" ] && [ -n "$PULL_CURL_MATCH" ] && [[ "$args" == *"$PULL_CURL_MATCH"* ]]; then
      curl_hits="$curl_hits $pid"
      nc=$((nc + 1))
    fi
  done < <(ps -eo pid=,args=)
  if [ "$np" -eq 0 ] && [ "$nc" -eq 0 ]; then
    log "no-pull-process check: PASS (0 pull.sh, 0 curl)"
    return 0
  fi
  log "no-pull-process check: FAIL offending pids pull.sh=${pull_hits# } curl=${curl_hits# }"
  exit 6
}

check_watcher() {
  local pid comm wp=""
  while read -r pid; do
    [ -n "${pid:-}" ] || continue
    [ "$pid" = "$$" ] && continue
    comm=$(cat "/proc/$pid/comm" 2>/dev/null || true)
    [ "$comm" = "pgrep" ] && continue
    wp="$wp $pid"
  done < <(pgrep -f "$WATCHER_NAME" || true)
  if [ -n "$wp" ]; then
    log "watcher-not-started: FAIL pids=${wp# }"
    exit 7
  fi
  log "watcher-not-started: PASS"
}

sustain_memory() {
  local start now m good_since=""
  start=$(date +%s)
  : > "$D/memwait.log"
  while :; do
    now=$(date +%s)
    if [ $((now - start)) -ge "$WAIT_MAX_S" ]; then
      log "STOP memory not sustained"
      exit 4
    fi
    m=$(avail_mb)
    case "$m" in
      ''|*[!0-9]*) m=0 ;;
    esac
    echo "$(ts) availMB=$m" >> "$D/memwait.log"
    if [ "$m" -ge "$MIN_MB" ]; then
      if [ -z "$good_since" ]; then
        good_since=$now
      fi
      if [ $((now - good_since)) -ge "$SUSTAIN_S" ]; then
        log "memory sustained >=${MIN_MB} for ${SUSTAIN_S} s"
        return 0
      fi
    else
      good_since=""
    fi
    sleep "$SAMPLE_S"
  done
}

check_env_and_guard() {
  local v
  for v in CURSOR_LLM_MODEL CURSOR_LLM_INFRA_RETRIES CURSOR_LLM_ISOLATE CURSOR_AGENT_BIN CURSOR_TRIAL_BIN; do
    [ -n "${!v+x}" ] && { log "ABORT $v set"; exit 2; }
  done
  if [ "$SKIP_GUARD_START" = "1" ]; then
    log "guard_start skipped"
  else
    guard_start || { log "STOP start-gate"; exit 3; }
  fi
}

prelaunch_recheck() {
  local m
  m=$(avail_mb)
  case "$m" in
    ''|*[!0-9]*) m=0 ;;
  esac
  if [ "$m" -lt "$MIN_MB" ]; then
    log "ABORT pre-launch recheck availMB=$m"
    exit 8
  fi
  log "pre-launch recheck availMB=$m PASS"
}

sleep 100000 &
DECOY=$!
log "decoy untagged sleep pid=$DECOY"

check_pull_finished
check_no_pull_process
check_watcher
sustain_memory
check_env_and_guard
log_pull_intro

if [ "$DRY_RUN" != "1" ]; then
  log "before snapshot: $(counts "$D/before.snap") $(free -m | awk '/Mem/{print "availMB="$7}') load=$(cut -d' ' -f1-3 /proc/loadavg)"
fi
prelaunch_recheck

if [ "$DRY_RUN" = "1" ]; then
  log "DRY-RUN would launch $N calls"
  exit 0
fi

./mon.sh "$D/tree" 10 &
M=$!
log "start N=$N"
for i in $(seq 1 "$N"); do
  "$P" "$CI/frozen-trial/fcall5.py" "$D/call-$i" >> "$L" 2>&1 &
done
while [ -n "$(fcall_driver_pids | head -n 1)" ]; do
  m=$(avail_mb)
  case "$m" in
    ''|*[!0-9]*) m=0 ;;
  esac
  if pull_pid_alive; then
    pbit="pullworkers=$(pull_worker_count)"
  else
    pbit="pull: finished, no process"
  fi
  echo "$(ts) availMB=$m load=$(cut -d' ' -f1 /proc/loadavg) ws=$(pgrep -fc 'index.js worker-server' || true) $pbit" >> "$D/resources.log"
  guard_ok || on_breach
  sleep 10
done
log "all calls returned"
sleep 5
if [ -n "${M:-}" ]; then
  kill "$M" 2>/dev/null || true
  wait "$M" 2>/dev/null || true
  M=""
fi
log "after snapshot: $(counts "$D/after.snap") $(free -m | awk '/Mem/{print "availMB="$7}') load=$(cut -d' ' -f1-3 /proc/loadavg)"
log_pull_after
cleanup
log "DONE"
