#!/usr/bin/env bash
# 13 samples, every 300 s, IST time, MemAvailable MB, loadavg
LOG="$(dirname "$0")/mem-hourly.log"
for i in $(seq 1 13); do
  m=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  echo "$(TZ=Asia/Kolkata date '+%F %T IST') sample=$i MemAvailable_MB=$m load=$(cut -d' ' -f1-3 /proc/loadavg)" >> "$LOG"
  [ $i -lt 13 ] && sleep 300
done
echo "DONE $(TZ=Asia/Kolkata date '+%F %T IST')" >> "$LOG"
