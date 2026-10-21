#!/bin/bash
# Sandbox tests for run_trial5b.sh. DRY_RUN only. Never uses /workspace/oa/pull.
set -u

HERE=$(cd "$(dirname "$0")" && pwd)
SCRIPT=$HERE/run_trial5b.sh
fail=0

SANDBOX=$(mktemp -d)
PULL_DIR=$SANDBOX/pulldir
OUT_BASE=$SANDBOX/out
MEMINFO=$SANDBOX/meminfo
PULL_LOG=$SANDBOX/pull.log
CURL_TOKEN=nocurl-$SANDBOX
WATCHER_NAME=nowatcher-$$-$RANDOM
fake_pid=""

mkdir -p "$PULL_DIR" "$OUT_BASE"

case "$PULL_DIR" in
  /workspace/oa/pull|/workspace/oa/pull/*)
    echo "FAIL: PULL_DIR points at the real pull"
    exit 1
    ;;
esac

list_decoys() {
  ps -eo pid=,args= | awk '$2=="sleep" && $3=="100000" {print $1}'
}

stop_fake_pull() {
  [ -n "${fake_pid:-}" ] || return 0
  if [ -d "/proc/$fake_pid" ]; then
    local args cwd pgid mypg target
    args=$(ps -o args= -p "$fake_pid" 2>/dev/null | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    cwd=$(readlink -f "/proc/$fake_pid/cwd" 2>/dev/null || true)
    target=$(readlink -f "$PULL_DIR")
    if [ "$args" = "bash pull.sh" ] && [ "$cwd" = "$target" ]; then
      pgid=$(ps -o pgid= -p "$fake_pid" | tr -d ' ')
      mypg=$(ps -o pgid= -p $$ | tr -d ' ')
      if [ -n "$pgid" ] && [ "$pgid" = "$fake_pid" ] && [ "$pgid" != "$mypg" ]; then
        kill -TERM -- "-$pgid" 2>/dev/null || true
      fi
    fi
  fi
  fake_pid=""
}

reap_leaked_decoys() {
  local pid
  for pid in $(list_decoys); do
    case " $decoys_before " in
      *" $pid "*) ;;
      *)
        kill -TERM "$pid" 2>/dev/null || true
        echo "FAIL: leaked decoy sleep pid=$pid"
        fail=1
        ;;
    esac
  done
}

cleanup() {
  stop_fake_pull
  reap_leaked_decoys
  rm -rf "$SANDBOX"
}
decoys_before=" $(list_decoys | tr '\n' ' ') "
trap cleanup EXIT

write_mem() {
  cat > "$MEMINFO" << EOF
MemTotal:       16000000 kB
MemAvailable:   $1 kB
EOF
}

write_finished() {
  echo "2026-10-21T12:00:00+05:30 PULL_FINISHED" > "$PULL_LOG"
}

write_unfinished() {
  echo "2026-10-21T12:00:00+05:30 still pulling" > "$PULL_LOG"
}

run_trial() {
  # Export only. Do not put WATCHER_NAME on argv: pgrep -f would match timeout/env.
  export SKIP_GUARD_START=1
  export DRY_RUN=1
  export SUSTAIN_S=2
  export SAMPLE_S=1
  export WAIT_MAX_S=5
  export MEMINFO="$MEMINFO"
  export PULL_LOG="$PULL_LOG"
  export PULL_DIR="$PULL_DIR"
  export OUT_BASE="$OUT_BASE"
  export PULL_CURL_MATCH="$CURL_TOKEN"
  export WATCHER_NAME
  # Drop MIN_MB so these cases see the script default, not a caller override.
  env -u MIN_MB timeout 40 bash "$SCRIPT" "$1" "$2"
}

find_fake_pull() {
  local pid args cwd target
  target=$(readlink -f "$PULL_DIR")
  while read -r pid args; do
    [ -n "${pid:-}" ] || continue
    if [ "$args" = "bash pull.sh" ]; then
      cwd=$(readlink -f "/proc/$pid/cwd" 2>/dev/null || true)
      if [ "$cwd" = "$target" ]; then
        echo "$pid"
        return 0
      fi
    fi
  done < <(ps -eo pid=,args=)
  return 1
}

# --- case: no PULL_FINISHED ---
write_unfinished
write_mem 8388608
set +e
run_trial case_nofin 1
ec=$?
set -e
if [ "$ec" -eq 5 ]; then
  echo "PASS: no PULL_FINISHED -> exit 5"
else
  echo "FAIL: no PULL_FINISHED -> exit 5 (got $ec)"
  fail=1
fi
reap_leaked_decoys

# --- case: fake bash pull.sh in tmp PULL_DIR ---
write_finished
write_mem 8388608
cat > "$PULL_DIR/pull.sh" << 'EOF'
#!/bin/bash
sleep 30
EOF
chmod +x "$PULL_DIR/pull.sh"
(cd "$PULL_DIR" && setsid bash -c 'exec -a "bash" bash pull.sh') &
fake_pid=""
for _ in $(seq 1 25); do
  fake_pid=$(find_fake_pull || true)
  [ -n "$fake_pid" ] && break
  sleep 0.1
done
if [ -z "$fake_pid" ]; then
  echo "FAIL: fake bash pull.sh -> exit 6 (fixture did not start)"
  fail=1
else
  set +e
  run_trial case_pull 1
  ec=$?
  set -e
  if [ "$ec" -eq 6 ]; then
    echo "PASS: fake bash pull.sh -> exit 6"
  else
    echo "FAIL: fake bash pull.sh -> exit 6 (got $ec)"
    fail=1
    cat "$OUT_BASE/case_pull/orchestrator.log" 2>/dev/null || true
  fi
  stop_fake_pull
fi
reap_leaked_decoys

# --- case: low memory ---
write_finished
write_mem 102400
set +e
run_trial case_low 1
ec=$?
set -e
if [ "$ec" -eq 4 ]; then
  echo "PASS: low memory -> exit 4"
else
  echo "FAIL: low memory -> exit 4 (got $ec)"
  fail=1
  cat "$OUT_BASE/case_low/orchestrator.log" 2>/dev/null || true
fi
reap_leaked_decoys

# --- case: all preflight good, dry run ---
write_finished
write_mem 8388608
set +e
run_trial case_ok 3
ec=$?
set -e
logf=$OUT_BASE/case_ok/orchestrator.log
ok=1
missing=""
if [ "$ec" -ne 0 ]; then
  ok=0
  missing="exit=$ec"
fi
for s in \
  "PULL_FINISHED" \
  "no-pull-process check: PASS" \
  "watcher-not-started: PASS" \
  "memory sustained" \
  "DRY-RUN would launch"
do
  if ! grep -q -F "$s" "$logf" 2>/dev/null; then
    ok=0
    missing="$missing missing[$s]"
  fi
done
if [ -e "$OUT_BASE/case_ok/before.snap" ] || [ -e "$OUT_BASE/case_ok/after.snap" ]; then
  ok=0
  missing="$missing unexpected-snapshot"
fi
if [ "$ok" -eq 1 ]; then
  echo "PASS: all good -> exit 0 and required log lines"
else
  echo "FAIL: all good -> exit 0 and required log lines ($missing)"
  fail=1
  cat "$logf" 2>/dev/null || true
fi
reap_leaked_decoys

# --- case: 5000 MB is below the default 6144 floor ---
write_finished
write_mem 5120000
set +e
run_trial case_5000 1
ec=$?
set -e
logf=$OUT_BASE/case_5000/orchestrator.log
if [ "$ec" -eq 4 ] && grep -q -F "STOP memory not sustained" "$logf" \
  && ! grep -q -F "memory sustained >=6144" "$logf" \
  && ! grep -q -F "DRY-RUN would launch" "$logf"; then
  echo "PASS: 5000 MB < default 6144 -> exit 4"
else
  echo "FAIL: 5000 MB < default 6144 -> exit 4 (got $ec)"
  fail=1
  cat "$logf" 2>/dev/null || true
fi
reap_leaked_decoys

# --- case: 7000 MB clears the default 6144 floor ---
write_finished
write_mem 7168000
set +e
run_trial case_7000 1
ec=$?
set -e
logf=$OUT_BASE/case_7000/orchestrator.log
ok=1
missing=""
if [ "$ec" -ne 0 ]; then
  ok=0
  missing="exit=$ec"
fi
for s in \
  "memory sustained >=6144 for 2 s" \
  "pre-launch recheck availMB=7000 PASS" \
  "DRY-RUN would launch"
do
  if ! grep -q -F "$s" "$logf" 2>/dev/null; then
    ok=0
    missing="$missing missing[$s]"
  fi
done
if [ "$ok" -eq 1 ]; then
  echo "PASS: 7000 MB >= default 6144 -> exit 0"
else
  echo "FAIL: 7000 MB >= default 6144 -> exit 0 ($missing)"
  fail=1
  cat "$logf" 2>/dev/null || true
fi
reap_leaked_decoys

if [ "$fail" -ne 0 ]; then
  exit 1
fi
echo "ALL PASS"
exit 0
