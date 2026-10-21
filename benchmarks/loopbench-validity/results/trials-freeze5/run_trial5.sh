#!/bin/bash
# Counted during-pull trial through the FROZEN path. usage: run_trial.sh NAME N
set -u; CI=/workspace/concurrency-investigation; cd $CI; . ./guard.sh
NAME=$1; N=$2; D=$CI/frozen-trial/$NAME; mkdir -p $D; L=$D/orchestrator.log; P=/workspace/le-venv/bin/python
ts(){ TZ=Asia/Kolkata date --iso-8601=seconds; }; log(){ echo "$(ts) $*" >> $L; }
for v in CURSOR_LLM_MODEL CURSOR_LLM_INFRA_RETRIES CURSOR_LLM_ISOLATE CURSOR_AGENT_BIN CURSOR_TRIAL_BIN; do [ -n "${!v+x}" ] && { log "ABORT $v set"; exit 2; }; done
counts(){ ./snap.sh $1; echo "tagged=$(awk '$2!="-"' $1 | wc -l) worker_servers=$(pgrep -fc 'index.js worker-server')"; }
sleep 100000 & DECOY=$!; log "decoy untagged sleep pid=$DECOY"
guard_start || { log "STOP start-gate"; exit 3; }
for i in $(seq 1 40); do m=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); [ $m -ge 4096 ] && break; log "waiting availMB=$m (need >=4096)"; sleep 30; done; [ $m -ge 4096 ] || { log "STOP memory <4096 MB after 20 min"; exit 4; }
PULL=$(cat raw/pull-pid); log "pull pid=$PULL workers=$(pgrep -P $(pgrep -P $PULL xargs) -c) pull.sh sha=$(sha256sum /workspace/oa/pull/pull.sh|cut -c1-64)"
log "before snapshot: $(counts $D/before.snap) $(free -m|awk '/Mem/{print "availMB="$7}') load=$(cut -d' ' -f1-3 /proc/loadavg)"
./mon.sh $D/tree 10 & M=$!
log "start N=$N"
for i in $(seq 1 $N); do $P $CI/frozen-trial/fcall5.py $D/call-$i >> $L 2>&1 & done
while pgrep -f "fcall5.py $D/call-" >/dev/null; do
  echo "$(ts) availMB=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) load=$(cut -d' ' -f1 /proc/loadavg) ws=$(pgrep -fc 'index.js worker-server') pullworkers=$(pgrep -P $(pgrep -P $PULL xargs) -c)" >> $D/resources.log
  guard_ok || { log "GUARD BREACH during trial - killing our trial calls"; pkill -f "fcall5.py $D/call-"; sleep 5; kill $M; exit 3; }
  sleep 10; done
log "all calls returned"; sleep 5; kill $M
log "after snapshot: $(counts $D/after.snap) $(free -m|awk '/Mem/{print "availMB="$7}') load=$(cut -d' ' -f1-3 /proc/loadavg)"
log "pull workers at after-snapshot=$(pgrep -P $(pgrep -P $PULL xargs) -c) pull.sh sha=$(sha256sum /workspace/oa/pull/pull.sh|cut -c1-64)"
log "decoy pid=$DECOY alive=$(kill -0 $DECOY 2>/dev/null && echo yes || echo no)"; kill $DECOY
log "DONE"
