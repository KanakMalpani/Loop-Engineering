#!/bin/bash
# Self-contained mem_watch test. Never touches /workspace/oa/pull.
set -u

WATCH=$(cd "$(dirname "$0")" && pwd)/mem_watch.sh
TMP=$(mktemp -d)
tmp_real=$(readlink -f "$TMP")
case "$tmp_real" in
  /tmp/*|/var/tmp/*) ;;
  *)
    printf '%s\n' "FAIL tmp dir is not under /tmp: ${tmp_real}"
    exit 1
    ;;
esac

PULL_DIR=${TMP}/pull
MEMINFO=${TMP}/meminfo
PID_FILE=${TMP}/pull-pid
ID1=2099-01-01_part_0001.gz
ID2=2099-01-01_part_0002.gz
URL1=s3://openalex/data/jsonl/works/updated_date=2099-01-01/part_0001.gz
URL2=s3://openalex/data/jsonl/works/updated_date=2099-01-01/part_0002.gz

recorded=()
watch_pid=
failures=0
REAL_LOG=/workspace/oa/pull/pull.log
REAL_PID=/workspace/concurrency-investigation/raw/pull-pid

write_mem_mb() {
  local mb=$1
  printf 'MemAvailable:       %s kB\n' "$((mb * 1024))" > "${MEMINFO}.new"
  mv "${MEMINFO}.new" "$MEMINFO"
}

assert_safe() {
  local pull_real mem_real pid_real
  pull_real=$(readlink -f "$PULL_DIR")
  mem_real=$(readlink -f "$MEMINFO")
  pid_real=$(readlink -f "$PID_FILE")
  case "$pull_real" in
    "$tmp_real"/*) ;;
    *)
      printf '%s\n' "FAIL PULL_DIR is not under tmp: ${pull_real}"
      exit 1
      ;;
  esac
  case "$mem_real" in
    "$tmp_real"/*) ;;
    *)
      printf '%s\n' "FAIL MEMINFO is not under tmp: ${mem_real}"
      exit 1
      ;;
  esac
  case "$pid_real" in
    "$tmp_real"/*) ;;
    *)
      printf '%s\n' "FAIL PID_FILE is not under tmp: ${pid_real}"
      exit 1
      ;;
  esac
  if [ "$pull_real" = "/workspace/oa/pull" ]; then
    printf '%s\n' "FAIL refusing /workspace/oa/pull"
    exit 1
  fi
}

safe_kill_group() {
  local pgid=$1 pid cwd pids bad=0 any=0
  case "$pgid" in
    ''|*[!0-9]*) return 0 ;;
  esac
  pids=$(COLUMNS=4096 ps -o pid= -g "$pgid" 2>/dev/null || true)
  if [ -z "${pids//[[:space:]]/}" ]; then
    return 0
  fi
  while IFS= read -r pid; do
    pid=${pid//[[:space:]]/}
    [ -n "$pid" ] || continue
    any=1
    cwd=$(readlink -f "/proc/${pid}/cwd" 2>/dev/null || true)
    if [ -z "$cwd" ]; then
      continue
    fi
    case "$cwd" in
      "$tmp_real"/*|"$tmp_real") ;;
      *) bad=1 ;;
    esac
  done <<< "$pids"
  if [ "$any" = "1" ] && [ "$bad" = "0" ]; then
    kill -KILL -- "-${pgid}" 2>/dev/null || true
  fi
}

cleanup() {
  local pg pid_from_file pg2
  if [ -n "${MEMINFO:-}" ]; then
    write_mem_mb 3500 || true
  fi
  if [ -n "${watch_pid}" ] && [ -d "/proc/${watch_pid}" ]; then
    wait "$watch_pid" 2>/dev/null || true
  fi
  for pg in "${recorded[@]}"; do
    safe_kill_group "$pg"
  done
  if [ -n "${PID_FILE:-}" ] && [ -f "$PID_FILE" ]; then
    pid_from_file=$(tr -d '[:space:]' < "$PID_FILE" || true)
    case "$pid_from_file" in
      ''|*[!0-9]*) ;;
      *)
        pg2=$(ps -o pgid= -p "$pid_from_file" 2>/dev/null | tr -d '[:space:]' || true)
        if [ -n "$pg2" ]; then
          safe_kill_group "$pg2"
        fi
        ;;
    esac
  fi
  if [ -n "${TMP:-}" ]; then
    rm -rf "$TMP"
  fi
}
trap cleanup EXIT

mkdir -p "${PULL_DIR}/raw" "${PULL_DIR}/out" "${PULL_DIR}/hist" "${PULL_DIR}/done"
cat > "${PULL_DIR}/pull.sh" << EOF
#!/bin/bash
cd $(printf '%q' "$PULL_DIR")
bash -c 'exec -a "curl -sf -o raw/${ID1} ${URL1}" sleep 300' &
bash -c 'exec -a "curl -sf -o raw/${ID2} ${URL2}" sleep 300' &
sleep 300
EOF
write_mem_mb 1000
printf '%s\n' sentinel > "$PID_FILE"
assert_safe

if [ -f "$REAL_LOG" ]; then
  real_notes_before=$(grep -c 'mem-watch' "$REAL_LOG" || true)
else
  real_notes_before=0
fi
if [ -f "$REAL_PID" ]; then
  real_pid_before=$(sha256sum "$REAL_PID" | awk '{print $1}')
else
  real_pid_before=
fi

start_dummy() {
  local pid pgid sid cwd args raw
  pid=$(
    cd "$PULL_DIR" || exit 1
    bash -c 'setsid nohup bash pull.sh >> pull.out 2>&1 </dev/null & echo $!'
  )
  pid=${pid//[[:space:]]/}
  case "$pid" in
    ''|*[!0-9]*)
      printf '%s\n' "start_dummy: bad pid [${pid}]" >&2
      return 1
      ;;
  esac
  local i n
  n=0
  i=0
  while [ "$i" -lt 30 ]; do
    n=$(COLUMNS=4096 ps -o args= -g "$pid" 2>/dev/null | grep -c 's3://openalex/' || true)
    if [ "$n" -ge 2 ]; then
      break
    fi
    i=$((i + 1))
    sleep 0.1
  done
  if [ "$n" -lt 2 ]; then
    printf '%s\n' "start_dummy: in-flight curls not visible" >&2
    return 1
  fi
  pgid=$(ps -o pgid= -p "$pid" | tr -d '[:space:]')
  sid=$(ps -o sid= -p "$pid" | tr -d '[:space:]')
  cwd=$(readlink -f "/proc/${pid}/cwd")
  raw=$(tr '\0' ' ' < "/proc/${pid}/cmdline")
  args=${raw%" "}
  if [ "$pgid" != "$pid" ] || [ "$sid" != "$pid" ] || [ "$args" != "bash pull.sh" ] || [ "$cwd" != "$(readlink -f "$PULL_DIR")" ]; then
    printf '%s\n' "start_dummy: pgid=${pgid} sid=${sid} args=${args} cwd=${cwd}" >&2
    safe_kill_group "$pgid"
    return 1
  fi
  recorded+=("$pgid")
  printf '%s\n' "$pgid"
}

make_partials() {
  printf '%s\n' partial > "${PULL_DIR}/raw/${ID1}"
  printf '%s\n' partial > "${PULL_DIR}/out/${ID1}.jsonl.gz"
  printf '%s\n' partial > "${PULL_DIR}/hist/${ID1}.json"
  printf '%s\n' partial > "${PULL_DIR}/raw/${ID2}"
  printf '%s\n' partial > "${PULL_DIR}/out/${ID2}.jsonl.gz"
  printf '%s\n' partial > "${PULL_DIR}/hist/${ID2}.json"
}

partials_exist() {
  [ -f "${PULL_DIR}/raw/${ID1}" ] && [ -f "${PULL_DIR}/out/${ID1}.jsonl.gz" ] && [ -f "${PULL_DIR}/hist/${ID1}.json" ] \
    && [ -f "${PULL_DIR}/raw/${ID2}" ] && [ -f "${PULL_DIR}/out/${ID2}.jsonl.gz" ] && [ -f "${PULL_DIR}/hist/${ID2}.json" ]
}

partials_gone() {
  [ ! -e "${PULL_DIR}/raw/${ID1}" ] && [ ! -e "${PULL_DIR}/out/${ID1}.jsonl.gz" ] && [ ! -e "${PULL_DIR}/hist/${ID1}.json" ] \
    && [ ! -e "${PULL_DIR}/raw/${ID2}" ] && [ ! -e "${PULL_DIR}/out/${ID2}.jsonl.gz" ] && [ ! -e "${PULL_DIR}/hist/${ID2}.json" ]
}

group_all_stopped() {
  local pgid=$1 pid stat saw=0
  while IFS= read -r pid; do
    pid=${pid//[[:space:]]/}
    [ -n "$pid" ] || continue
    saw=1
    stat=$(ps -o stat= -p "$pid" | tr -d '[:space:]')
    case "$stat" in
      *T*) ;;
      *) return 1 ;;
    esac
  done < <(COLUMNS=4096 ps -o pid= -g "$pgid")
  [ "$saw" = "1" ]
}

group_alive_not_stopped() {
  local pgid=$1 pid stat saw=0
  while IFS= read -r pid; do
    pid=${pid//[[:space:]]/}
    [ -n "$pid" ] || continue
    saw=1
    stat=$(ps -o stat= -p "$pid" | tr -d '[:space:]')
    case "$stat" in
      *T*) return 1 ;;
    esac
  done < <(COLUMNS=4096 ps -o pid= -g "$pgid")
  [ "$saw" = "1" ]
}

group_gone() {
  local pgid=$1
  if COLUMNS=4096 ps -o pid= -g "$pgid" >/dev/null 2>&1; then
    return 1
  fi
  return 0
}

cmdline_of() {
  local pid=$1 raw
  raw=$(tr '\0' ' ' < "/proc/${pid}/cmdline" 2>/dev/null || true)
  printf '%s\n' "${raw%" "}"
}

dump_case() {
  local label=$1
  printf '%s\n' "--- ${label} pull.log ---" >&2
  cat "${PULL_DIR}/pull.log" >&2 2>/dev/null || true
  printf '%s\n' "--- ${label} stdout ---" >&2
  cat "$2" >&2 2>/dev/null || true
  printf '%s\n' "--- ${label} stderr ---" >&2
  cat "$3" >&2 2>/dev/null || true
}

# --- case 1: DRY_RUN low memory ---
case1_ok=1
rm -f "${PULL_DIR}/pull.log"
make_partials
pg1=$(start_dummy) || case1_ok=0
if [ "$case1_ok" -eq 1 ]; then
  assert_safe
  PULL_DIR="$PULL_DIR" MEMINFO="$MEMINFO" PID_FILE="$PID_FILE" \
    POLL_S=1 MAX_POLLS=1 DRY_RUN=1 PAUSE_BELOW_MB=3072 RESUME_ABOVE_MB=4096 \
    bash "$WATCH" > "${TMP}/case1.out" 2> "${TMP}/case1.err"
  if [ "$?" -ne 0 ]; then
    case1_ok=0
  fi
  if ! grep -Eq '^DRY-RUN [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} IST PAUSE mem-watch available_mb=1000 pgid='"${pg1}"' in_flight=2$' "${PULL_DIR}/pull.log"; then
    case1_ok=0
  fi
  if ! grep -Eq '^DRY-RUN .* PAUSE mem-watch ' "${TMP}/case1.out"; then
    case1_ok=0
  fi
  if ! grep -q "DRY-RUN would: kill -STOP -- -${pg1}" "${TMP}/case1.out"; then
    case1_ok=0
  fi
  if grep -E '^[0-9]{4}-' "${PULL_DIR}/pull.log" | grep -q 'PAUSE mem-watch'; then
    case1_ok=0
  fi
  if ! partials_exist; then
    case1_ok=0
  fi
  if ! group_alive_not_stopped "$pg1"; then
    case1_ok=0
  fi
  if [ "$(tr -d '[:space:]' < "$PID_FILE")" != "sentinel" ]; then
    case1_ok=0
  fi
fi
if [ "$case1_ok" -eq 1 ]; then
  printf '%s\n' "PASS case1 dry-run low mem logs PAUSE and leaves the group running"
else
  printf '%s\n' "FAIL case1 dry-run low mem logs PAUSE and leaves the group running"
  dump_case case1 "${TMP}/case1.out" "${TMP}/case1.err"
  failures=1
fi
if [ -n "${pg1:-}" ]; then
  safe_kill_group "$pg1"
fi

# --- case 2: real pause then resume ---
case2_ok=1
rm -f "${PULL_DIR}/pull.log" "${PULL_DIR}/pull.out"
make_partials
write_mem_mb 1000
printf '%s\n' sentinel > "$PID_FILE"
pg2=$(start_dummy) || case2_ok=0
if [ "$case2_ok" -eq 1 ]; then
  assert_safe
  PULL_DIR="$PULL_DIR" MEMINFO="$MEMINFO" PID_FILE="$PID_FILE" \
    POLL_S=1 MAX_POLLS=10 DRY_RUN=0 PAUSE_BELOW_MB=3072 RESUME_ABOVE_MB=4096 \
    bash "$WATCH" > "${TMP}/case2.out" 2> "${TMP}/case2.err" &
  watch_pid=$!
  i=0
  pause_seen=0
  while [ "$i" -lt 75 ]; do
    if [ -f "${PULL_DIR}/pull.log" ] \
      && grep -Eq "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} IST PAUSE mem-watch available_mb=1000 pgid=${pg2} in_flight=2$" "${PULL_DIR}/pull.log" \
      && grep -Fq "${ID1} re-pulled after mem-watch PAUSE (in flight at pause; raw, partial output, hist deleted)" "${PULL_DIR}/pull.log" \
      && grep -Fq "${ID2} re-pulled after mem-watch PAUSE (in flight at pause; raw, partial output, hist deleted)" "${PULL_DIR}/pull.log"; then
      pause_seen=1
      break
    fi
    i=$((i + 1))
    sleep 0.2
  done
  if [ "$pause_seen" -ne 1 ]; then
    case2_ok=0
  fi
  if ! group_all_stopped "$pg2"; then
    case2_ok=0
  fi
  if ! partials_gone; then
    case2_ok=0
  fi
  sleep 1
  write_mem_mb 5000
  i=0
  resume_seen=0
  while [ "$i" -lt 75 ]; do
    if [ -f "${PULL_DIR}/pull.log" ] \
      && grep -Eq "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} IST RESUME mem-watch available_mb=5000 old_pgid=${pg2} new_pid=[0-9]+ paused_s=[0-9]+$" "${PULL_DIR}/pull.log"; then
      resume_seen=1
      break
    fi
    i=$((i + 1))
    sleep 0.2
  done
  if [ "$resume_seen" -ne 1 ]; then
    case2_ok=0
  fi
  if ! grep -Fq "${ID1} re-pulled after mem-watch RESUME (killed while paused; raw, partial output, hist deleted)" "${PULL_DIR}/pull.log"; then
    case2_ok=0
  fi
  if ! grep -Fq "${ID2} re-pulled after mem-watch RESUME (killed while paused; raw, partial output, hist deleted)" "${PULL_DIR}/pull.log"; then
    case2_ok=0
  fi
  if ! group_gone "$pg2"; then
    case2_ok=0
  fi
  new_pid=$(tr -d '[:space:]' < "$PID_FILE" || true)
  case "$new_pid" in
    ''|*[!0-9]*|sentinel)
      case2_ok=0
      ;;
    *)
      new_pgid=$(ps -o pgid= -p "$new_pid" 2>/dev/null | tr -d '[:space:]' || true)
      if [ -n "$new_pgid" ]; then
        recorded+=("$new_pgid")
      fi
      if ! grep -Eq "new_pid=${new_pid} paused_s=[0-9]+$" "${PULL_DIR}/pull.log"; then
        case2_ok=0
      fi
      if [ "$(cmdline_of "$new_pid")" != "bash pull.sh" ]; then
        case2_ok=0
      fi
      if [ "$(readlink -f "/proc/${new_pid}/cwd" 2>/dev/null || true)" != "$(readlink -f "$PULL_DIR")" ]; then
        case2_ok=0
      fi
      stat_new=$(ps -o stat= -p "$new_pid" 2>/dev/null | tr -d '[:space:]' || true)
      case "$stat_new" in
        ''|*T*|*Z*) case2_ok=0 ;;
      esac
      ;;
  esac
  if ! grep -q "PAUSE mem-watch available_mb=1000 pgid=${pg2} in_flight=2" "${TMP}/case2.out"; then
    case2_ok=0
  fi
  if [ -d "/proc/${watch_pid}" ]; then
    wait "$watch_pid" 2>/dev/null || case2_ok=0
  fi
  watch_pid=
  if [ -n "${new_pid:-}" ] && [ -d "/proc/${new_pid}" ]; then
    if [ "$(cmdline_of "$new_pid")" != "bash pull.sh" ]; then
      case2_ok=0
    fi
    if [ "$(readlink -f "/proc/${new_pid}/cwd" 2>/dev/null || true)" != "$(readlink -f "$PULL_DIR")" ]; then
      case2_ok=0
    fi
  else
    case2_ok=0
  fi
fi
if [ "$case2_ok" -eq 1 ]; then
  printf '%s\n' "PASS case2 pause then resume restarts pull from the fake dir"
else
  printf '%s\n' "FAIL case2 pause then resume restarts pull from the fake dir"
  dump_case case2 "${TMP}/case2.out" "${TMP}/case2.err"
  failures=1
fi

if [ -f "$REAL_LOG" ]; then
  real_notes_after=$(grep -c 'mem-watch' "$REAL_LOG" || true)
else
  real_notes_after=0
fi
if [ "${real_notes_before}" != "${real_notes_after}" ]; then
  printf '%s\n' "FAIL real pull.log gained mem-watch lines"
  failures=1
fi
if [ -n "$real_pid_before" ] && [ -f "$REAL_PID" ]; then
  real_pid_after=$(sha256sum "$REAL_PID" | awk '{print $1}')
  if [ "$real_pid_before" != "$real_pid_after" ]; then
    printf '%s\n' "FAIL real pull pid file changed"
    failures=1
  fi
fi

if [ "$failures" -ne 0 ]; then
  exit 1
fi
exit 0
