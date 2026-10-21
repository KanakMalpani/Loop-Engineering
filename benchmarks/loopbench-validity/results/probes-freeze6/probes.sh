#!/bin/bash
# FROZEN-6 probe rerun, same procedure as probes-freeze5 (clean worktree, memwait to run_full floor, launch memcheck, leak then role probe)
W=/workspace/le-gate-f1f5ef9/benchmarks/loopbench-validity
O=$W/results/probes-freeze6; mkdir -p $O; cd $W
PY=/workspace/le-venv/bin/python
END=$(( $(date +%s) + 1800 ))
while :; do m=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  [ $m -ge 6144 ] && break
  echo "$(TZ=Asia/Kolkata date +%T) IST waiting availMB=$m" >> $O/memwait.log
  [ $(date +%s) -ge $END ] && { echo "$(TZ=Asia/Kolkata date +%T) IST TIMEOUT 30min, floor 6144 not reached; probes NOT run" >> $O/memwait.log; exit 4; }
  sleep 30; done
echo "$(TZ=Asia/Kolkata date +%T) IST reached availMB=$m" >> $O/memwait.log
$PY -c "import sys; sys.path.insert(0,'.'); import run_full,shutil; r=run_full.check_launch_memory('.'); sys.exit(0 if r['ok'] else 5)" || { cp results/launch-memcheck.log $O/; exit 5; }
cp results/launch-memcheck.log $O/launch-memcheck.log
$PY leak_probe.py --out $O/leak-probe.json > $O/leak-probe.stdout 2> $O/leak-probe.stderr; echo "leak exit=$?" >> $O/exit.log
$PY role_probe.py --out $O/role-probe.json > $O/role-probe.stdout 2> $O/role-probe.stderr; echo "role exit=$?" >> $O/exit.log
for f in leak-probe.log reap.log; do [ -f results/$f ] && [ ! -f $O/$f ] && cp results/$f $O/; done
[ -d results/stderr ] && cp -rn results/stderr $O/ 2>/dev/null
echo DONE >> $O/exit.log
