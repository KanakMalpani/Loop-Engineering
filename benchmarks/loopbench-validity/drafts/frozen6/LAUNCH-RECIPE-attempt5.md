# Attempt 5 launch recipe

Status: PENDING QA REVIEW - not frozen, no FROZEN-6.sha256 yet. Do not launch until QA accepts `DEVIATION-6.md`.

The command below is the counted acceptance launch. It runs `benchmarks/loopbench-validity/run_full.py` (the runner whose startup floor is `MIN_AVAILABLE_MB = 6144` once this deviation is applied). Do not point it at `drafts/frozen6/run_full.py`: that copy's `here` is the draft directory, which has no `loops/`.

## Preconditions

All of these must hold before the command. If any fails, do not launch.

- No pull process and no curl process. No `bash pull.sh` whose cwd is `/workspace/oa/pull`, and no `curl` whose arguments belong to that pull. The harness check for this is `check_no_pull_process` in `results/trials-freeze5/harness-5b/run_trial5b.sh` (exit 6 on a hit). `PULL_FINISHED` must already be in the pull log.
- MemAvailable >= 6144 MB. The runner enforces this once at startup (`check_launch_memory`, abort below 6144). The trial harness uses the same floor: `MIN_MB` defaults to 6144 (override by setting `MIN_MB`), the 60 s sustained hold requires MemAvailable >= `MIN_MB` for `SUSTAIN_S` seconds, and the pre-launch recheck aborts when MemAvailable is below `MIN_MB`.
- Model is `grok-4.7-high`. None of `CURSOR_LLM_MODEL`, `CURSOR_LLM_INFRA_RETRIES`, `CURSOR_LLM_ISOLATE`, `CURSOR_AGENT_BIN`, `CURSOR_TRIAL_BIN` is set.

## Launch command

`--max-concurrency 5` is explicit. It equals the argparse default (`default=5` on `--max-concurrency` in `run_full.py`).

```bash
cd /workspace/Loop-Engineering/benchmarks/loopbench-validity && /workspace/le-venv/bin/python run_full.py --confirm-acceptance --model grok-4.7-high --task LB-CR-1 --seeds 0,1,2,3,4 --runs 3 --max-concurrency 5 --timeout 150 --outdir results/acceptance-5
```
