#!/bin/bash
# snap.sh OUT : every pid with its CURSOR_REAP_TAG (or -) and comm
for e in /proc/[0-9]*/environ; do p=${e#/proc/}; p=${p%/environ}
  t=$(tr '\0' '\n' < $e 2>/dev/null | grep -m1 '^CURSOR_REAP_TAG=' | cut -d= -f2); echo "$p ${t:--} $(cat /proc/$p/comm 2>/dev/null)"; done | sort -n > "$1"
