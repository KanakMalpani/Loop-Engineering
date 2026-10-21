# mem_watch

Watches `MemAvailable` and pauses the OpenAlex AE pull when free memory is low. On recovery it kills the paused pull and starts it again. In-flight parts are deleted and pulled from scratch. A stopped `curl` is not resumed mid-download.

This watcher is not started automatically.

## Usage

```bash
PULL_DIR=/workspace/oa/pull \
PID_FILE=/workspace/concurrency-investigation/raw/pull-pid \
bash benchmarks/loopbench-validity/tools/pull-watch/mem_watch.sh
```

`DRY_RUN=1` writes the same `pull.log` lines prefixed with `DRY-RUN `, prints the kill, delete, and restart it would perform, and does not signal, delete, or restart.

```bash
bash benchmarks/loopbench-validity/tools/pull-watch/test_mem_watch.sh
```

The test uses a temporary directory only. It does not touch `/workspace/oa/pull`.

## Environment

| Variable | Default | Meaning |
| --- | --- | --- |
| `PULL_DIR` | `/workspace/oa/pull` | Pull working directory (`pull.sh`, `pull.log`, `raw/`, `out/`, `hist/`, `done/`) |
| `MEMINFO` | `/proc/meminfo` | File to read; `MemAvailable` kB is integer-divided by 1024 |
| `PID_FILE` | `/workspace/concurrency-investigation/raw/pull-pid` | Where the restarted pull pid is written |
| `POLL_S` | `10` | Seconds between polls |
| `PAUSE_BELOW_MB` | `3072` | Pause when available MB is below this |
| `RESUME_ABOVE_MB` | `4096` | Resume when available MB is above this |
| `DRY_RUN` | `0` | `1` logs and prints actions without performing them |
| `MAX_POLLS` | `0` | Stop after this many polls; `0` means run until killed |

## Rules

- The pull is the process whose arguments are exactly `bash pull.sh` and whose cwd is `PULL_DIR`. Its process group id comes from `ps`. If that process is absent, the watcher keeps polling and logs nothing. While already paused, a missing group logs one `NOTE`.
- Below `PAUSE_BELOW_MB` the group is stopped with `kill -STOP -- -$PGID`. Part ids are taken from `ps -o args= -g $PGID` the same way as `switch_v7.sh` (the `s3://openalex/...` URL). For each in-flight id that is not done (`done/<id>` and `out/<id>.jsonl.gz`), `raw/<id>`, `out/<id>.jsonl.gz`, and `hist/<id>.json` are removed.
- Above `RESUME_ABOVE_MB` the stopped group is `kill -KILL`ed (a stopped process cannot handle `TERM`), partials are removed again, and the pull is restarted with `setsid nohup bash pull.sh >> pull.out 2>&1 </dev/null &`. The new pid is written to `PID_FILE`. `pull.sh` skips parts that are already done.
- Between the two thresholds the current state is left as it is.
- Every line appended to `pull.log` is also printed on stdout. Times use `TZ=Asia/Kolkata date '+%F %T IST'`.
