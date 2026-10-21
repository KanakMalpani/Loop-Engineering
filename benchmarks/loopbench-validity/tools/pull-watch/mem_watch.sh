#!/bin/bash
# Pause the AE pull while MemAvailable is low, then kill in-flight parts and restart.
# In-flight downloads are not resumed; pull.sh fetches them again from scratch.
# This watcher is not started automatically. See README.md.
set -u

PULL_DIR=${PULL_DIR:-/workspace/oa/pull}
MEMINFO=${MEMINFO:-/proc/meminfo}
PID_FILE=${PID_FILE:-/workspace/concurrency-investigation/raw/pull-pid}
POLL_S=${POLL_S:-10}
PAUSE_BELOW_MB=${PAUSE_BELOW_MB:-3072}
RESUME_ABOVE_MB=${RESUME_ABOVE_MB:-4096}
DRY_RUN=${DRY_RUN:-0}
MAX_POLLS=${MAX_POLLS:-0}

state=running
paused_at=0
missing_note=0
polls=0
RESTARTED_PID=
SELF_PGID=$(ps -o pgid= -p "$$" | tr -d '[:space:]')

ts() {
  TZ=Asia/Kolkata date '+%F %T IST'
}

emit() {
  local line=$1
  if [ "$DRY_RUN" = "1" ]; then
    line="DRY-RUN ${line}"
  fi
  printf '%s\n' "$line" >> "${PULL_DIR}/pull.log"
  printf '%s\n' "$line"
}

mem_available_mb() {
  local kb
  kb=$(awk '/^MemAvailable:/ { print $2; exit }' "$MEMINFO")
  case "$kb" in
    ''|*[!0-9]*)
      printf '%s\n' "mem_watch: MemAvailable not numeric in ${MEMINFO}" >&2
      return 1
      ;;
  esac
  echo $((kb / 1024))
}

# Args exactly "bash pull.sh" (NUL-separated cmdline) and cwd == PULL_DIR.
# pgid comes from ps. Candidates are filtered with ps so unrelated long
# command lines are not read.
find_pull_pgid() {
  local pid raw args cwd pgid want
  want=$(readlink -f "$PULL_DIR")
  while IFS= read -r pid; do
    [ -n "$pid" ] || continue
    [ -r "/proc/${pid}/cmdline" ] || continue
    raw=$(tr '\0' ' ' < "/proc/${pid}/cmdline" 2>/dev/null || true)
    args=${raw%" "}
    [ "$args" = "bash pull.sh" ] || continue
    cwd=$(readlink -f "/proc/${pid}/cwd" 2>/dev/null || true)
    [ "$cwd" = "$want" ] || continue
    pgid=$(ps -o pgid= -p "$pid" 2>/dev/null | tr -d '[:space:]' || true)
    [ -n "$pgid" ] || continue
    printf '%s\n' "$pgid"
    return 0
  done < <(COLUMNS=4096 ps -ww -eo pid=,args= | sed -n 's/^ *\([0-9][0-9]*\) bash pull\.sh *$/\1/p')
  return 1
}

# Same extraction as switch_v7.sh: s3 urls in the process group, then the part id.
in_flight_ids() {
  local pgid=$1
  COLUMNS=4096 ps -o args= -g "$pgid" 2>/dev/null \
    | grep -o 's3://openalex/[^ ]*' \
    | sed 's#.*/works/##; s#/#_#; s#updated_date=##' \
    | sort -u \
    || true
}

count_ids() {
  local ids=$1 id n=0
  if [ -z "$ids" ]; then
    echo 0
    return 0
  fi
  while IFS= read -r id; do
    [ -n "$id" ] || continue
    n=$((n + 1))
  done <<< "$ids"
  echo "$n"
}

part_done() {
  local id=$1
  [ -f "${PULL_DIR}/done/${id}" ] && [ -f "${PULL_DIR}/out/${id}.jsonl.gz" ]
}

pgid_is_our_pull() {
  local pgid=$1 pid raw args cwd want
  want=$(readlink -f "$PULL_DIR")
  while IFS= read -r pid; do
    pid=${pid//[[:space:]]/}
    [ -n "$pid" ] || continue
    [ -r "/proc/${pid}/cmdline" ] || continue
    raw=$(tr '\0' ' ' < "/proc/${pid}/cmdline" 2>/dev/null || true)
    args=${raw%" "}
    [ "$args" = "bash pull.sh" ] || continue
    cwd=$(readlink -f "/proc/${pid}/cwd" 2>/dev/null || true)
    [ "$cwd" = "$want" ] || return 1
    return 0
  done < <(COLUMNS=4096 ps -o pid= -g "$pgid" 2>/dev/null || true)
  return 1
}

may_signal_group() {
  local pgid=$1
  case "$pgid" in
    ''|*[!0-9]*) return 1 ;;
  esac
  [ "$pgid" -gt 1 ] || return 1
  [ "$pgid" != "$SELF_PGID" ] || return 1
  pgid_is_our_pull "$pgid"
}

purge_inflight() {
  local id=$1 reason=$2
  if part_done "$id"; then
    return 0
  fi
  if [ "$DRY_RUN" = "1" ]; then
    printf '%s\n' "DRY-RUN would: rm -f ${PULL_DIR}/raw/${id} ${PULL_DIR}/out/${id}.jsonl.gz ${PULL_DIR}/hist/${id}.json"
  else
    rm -f "${PULL_DIR}/raw/${id}" "${PULL_DIR}/out/${id}.jsonl.gz" "${PULL_DIR}/hist/${id}.json"
  fi
  emit "$(ts) ${id} ${reason}"
}

for_each_id() {
  local ids=$1 reason=$2 id
  if [ -z "$ids" ]; then
    return 0
  fi
  while IFS= read -r id; do
    [ -n "$id" ] || continue
    purge_inflight "$id" "$reason"
  done <<< "$ids"
}

wait_group_gone() {
  local pgid=$1 start
  start=$SECONDS
  while [ $((SECONDS - start)) -lt 10 ]; do
    if ! COLUMNS=4096 ps -o pid= -g "$pgid" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.2
  done
  if ! COLUMNS=4096 ps -o pid= -g "$pgid" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

restart_pull() {
  local oldpwd
  if [ "$DRY_RUN" = "1" ]; then
    printf '%s\n' "DRY-RUN would: cd ${PULL_DIR}; setsid nohup bash pull.sh >> pull.out 2>&1 </dev/null &"
    printf '%s\n' "DRY-RUN would: write new pid to ${PID_FILE}"
    RESTARTED_PID="-"
    return 0
  fi
  oldpwd=$(pwd)
  cd "$PULL_DIR" || return 1
  setsid nohup bash pull.sh >> pull.out 2>&1 </dev/null &
  RESTARTED_PID=$!
  printf '%s\n' "$RESTARTED_PID" > "$PID_FILE"
  cd "$oldpwd" || true
}

do_pause() {
  local pgid=$1 mb=$2 ids n
  may_signal_group "$pgid" || return 1
  ids=$(in_flight_ids "$pgid")
  n=$(count_ids "$ids")
  if [ "$DRY_RUN" = "1" ]; then
    printf '%s\n' "DRY-RUN would: kill -STOP -- -${pgid}"
  else
    kill -STOP -- "-${pgid}"
  fi
  state=paused
  paused_at=$(date +%s)
  missing_note=0
  emit "$(ts) PAUSE mem-watch available_mb=${mb} pgid=${pgid} in_flight=${n}"
  for_each_id "$ids" "re-pulled after mem-watch PAUSE (in flight at pause; raw, partial output, hist deleted)"
}

do_resume() {
  local pgid=$1 mb=$2 ids now paused_s
  may_signal_group "$pgid" || return 1
  ids=$(in_flight_ids "$pgid")
  if [ "$DRY_RUN" = "1" ]; then
    printf '%s\n' "DRY-RUN would: kill -KILL -- -${pgid}"
    printf '%s\n' "DRY-RUN would: wait until process group ${pgid} is gone (max 10s)"
  else
    kill -KILL -- "-${pgid}" || true
    if ! wait_group_gone "$pgid"; then
      printf '%s\n' "mem_watch: process group ${pgid} still present after 10s; not restarting" >&2
      return 1
    fi
  fi
  for_each_id "$ids" "re-pulled after mem-watch RESUME (killed while paused; raw, partial output, hist deleted)"
  restart_pull || return 1
  now=$(date +%s)
  paused_s=$((now - paused_at))
  emit "$(ts) RESUME mem-watch available_mb=${mb} old_pgid=${pgid} new_pid=${RESTARTED_PID} paused_s=${paused_s}"
  state=running
  missing_note=0
}

while true; do
  polls=$((polls + 1))
  mb=$(mem_available_mb) || exit 1
  pgid=$(find_pull_pgid || true)
  if [ -z "$pgid" ]; then
    if [ "$state" = "paused" ] && [ "$missing_note" = "0" ]; then
      emit "$(ts) NOTE mem-watch paused but pull pgid not found"
      missing_note=1
    fi
  else
    missing_note=0
    if [ "$state" = "running" ] && [ "$mb" -lt "$PAUSE_BELOW_MB" ]; then
      do_pause "$pgid" "$mb" || true
    elif [ "$state" = "paused" ] && [ "$mb" -gt "$RESUME_ABOVE_MB" ]; then
      do_resume "$pgid" "$mb" || true
    fi
  fi
  if [ "$MAX_POLLS" -gt 0 ] && [ "$polls" -ge "$MAX_POLLS" ]; then
    break
  fi
  sleep "$POLL_S"
done
