#!/bin/bash
# AE pull v6 -> v7 (3 workers), same procedure as v3->v4 (18:46:21 IST) and v4->v5 (19:10:25 IST) and v5->v6 (22:32:06 IST).
set -u; cd /workspace/oa/pull; PG=$(cat /workspace/concurrency-investigation/raw/pull-pid)
ts(){ TZ=Asia/Kolkata date '+%F %T IST'; }
ids=$(ps -o args= -g $PG | grep -o 's3://openalex/[^ ]*' | sed 's#.*/works/##; s#/#_#; s#updated_date=##' | sort -u)
echo "in-flight: $ids"
kill -TERM -- -$PG; sleep 3
sed -e 's/xargs -P2 /xargs -P3 /' -e '2s/.*/# usage: pull.sh  (reads parts.tsv: url size records). 3 parallel, 15MB\/s each (~45MB\/s total); v7./' pull.sh > pull.sh.v7
cp pull.sh.v7 pull.sh
sha=$(sha256sum pull.sh.v7 | cut -d' ' -f1)
echo "$(ts) SWITCH pull.sh v6 -> v7 (3 workers): back to 3 workers after during-pull trial c8-pull-1 (passed), before counted trials c8-2 and c8-3; worker count frozen until c8-3 after-snapshot; ordered by Engineering Lead. checks unchanged. sha256: $sha" >> pull.log
for id in $ids; do
  if ! { [ -f done/$id ] && [ -f out/$id.jsonl.gz ]; }; then
    rm -f raw/$id out/$id.jsonl.gz hist/$id.json
    echo "$(ts) $id re-pulled after switch (killed in flight; raw, partial output, hist deleted)" >> pull.log
  fi
done
setsid nohup bash pull.sh >> pull.out 2>&1 </dev/null &
echo $! > /workspace/concurrency-investigation/raw/pull-pid; echo "new pid $!"
