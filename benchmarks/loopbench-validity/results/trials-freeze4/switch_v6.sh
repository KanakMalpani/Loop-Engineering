#!/bin/bash
# AE pull v5 -> v6 (2 workers), same procedure as v3->v4 (18:46:21 IST) and v4->v5 (19:10:25 IST).
set -u; cd /workspace/oa/pull; PG=370638
ts(){ TZ=Asia/Kolkata date '+%F %T IST'; }
ids=$(ps -o args= -g $PG | grep -o 's3://openalex/[^ ]*' | sed 's#.*/works/##; s#/#_#; s#updated_date=##' | sort -u)
echo "in-flight: $ids"
kill -TERM -- -$PG; sleep 3
sed -e 's/xargs -P3 /xargs -P2 /' -e '2s/.*/# usage: pull.sh  (reads parts.tsv: url size records). 2 parallel, 15MB\/s each (~30MB\/s total); v6./' pull.sh > pull.sh.v6
cp pull.sh.v6 pull.sh
sha=$(sha256sum pull.sh.v6 | cut -d' ' -f1)
echo "$(ts) SWITCH pull.sh v5 -> v6 (2 workers): drop to 2 workers before the during-pull counted concurrency trial (QA bot rule: worker count frozen until the after-snapshot); ordered by Engineering Lead. checks unchanged. sha256: $sha" >> pull.log
for id in $ids; do
  if ! { [ -f done/$id ] && [ -f out/$id.jsonl.gz ]; }; then
    rm -f raw/$id out/$id.jsonl.gz hist/$id.json
    echo "$(ts) $id re-pulled after switch (killed in flight; raw, partial output, hist deleted)" >> pull.log
  fi
done
setsid nohup bash pull.sh >> pull.out 2>&1 </dev/null &
echo $! > /workspace/concurrency-investigation/raw/pull-pid; echo "new pid $!"
