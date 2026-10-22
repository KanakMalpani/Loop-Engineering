# Loop Engineering

Loop Engineering is the engineering discipline of systems that self-improve through feedback. Closed feedback loops (observe, act, evaluate, update, repeat) are made structured, mathematical and benchmarkable. It is for practitioners who build systems that learn from their own output.

- LSS: Loop Specification Standard, the YAML format for loop specs.
- LES: Loop Engineering Score, the score benchmarks report.
- LoopBench: the public scoreboard for loop engineering: fixed tasks, fixed seeds, observed LES.
- LoopGym: compiles LSS YAML into executable environments (simulate, call live models, or replay LoopNet trajectories).

## Prerequisites

Python 3.12 or newer.

## Install

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e packages/loopgym -e packages/loopbench -e packages/loop-observability -e packages/loopnet
```

> [!WARNING]
> **Don't install loopgym from PyPI; it's a different package with the same version number.**
> Check which copy you import:
> ```bash
> python -c "import loopgym; print(loopgym.__file__)"
> ```
> Expected: a path ending in `packages/loopgym/loopgym/__init__.py`.

## Quickstart

```bash
loopgym list # 9 environment ids
loopbench list # 19 tasks, LB-CR-1 first
loopgym run sim/mock-llm-v1 --seed 0 # episode JSON, seed 0
loopbench run --task LB-CR-1 --spec packages/loopgym/examples/minimal-loop.yaml --backend sim --seeds 0,1 -o /tmp/lb-cr-1.json # writes /tmp/lb-cr-1.json
python packages/loopgym/examples/quickstart.py # one episode, then a 3-seed check
```

Success looks like:

- Every command exits 0.
- `loopgym list` prints 9 environment ids such as `loopbench/code-repair-v1`.
- `loopbench list` prints 19 task ids, LB-CR-1 through LB-NEST-1.
- `loopgym run` prints episode JSON ending with `"task_id": "default"` and `"seed": 0`.
- `loopbench run` prints `Wrote /tmp/lb-cr-1.json`.
- That file is a submission JSON with `submission_id`, `loopbench_version` 0.2.0, `lss_version` 1.0.0, `les_version` 1.0.0, `backend` `"sim"`, results for LB-CR-1 (env `loopbench/code-repair-v1`, 6 runs = 3 task instances cr-001..cr-003 x 2 seeds) and a composite score (`les_observed` 0.346 for this minimal spec).
- `quickstart.py` runs one cr-001 episode (6 steps, `Success=False` with the mock LLM), then prints one reproducibility line per seed 0-2 like `seed=0: steps=6 quality=0.000 traj_hash=...`, with the same hash for every seed.

## Package map

| Directory | Import name | Dist name | CLI | Role |
| --- | --- | --- | --- | --- |
| `packages/loopgym` | `loopgym` | `loopgym` | `loopgym` | Loop environments (sim, live, replay) |
| `packages/loopbench` | `loopbench` | `loopbench` | `loopbench` | Tasks, fixtures, submissions, leaderboard |
| `packages/loop-observability` | `loopotel` | `loopotel` | `loopotel-validate` | Trace schema validation |
| `packages/loopnet` | `loopnet` | `loopnet` | none | Loop-run dataset records |
| `packages/loop-core` | none (no Python package) | `loop-engineering-core` | none | LSS/LES specs, schemas, tools |

## Running counted benchmarks (frozen code)

Applies only to acceptance (counted) runs in `benchmarks/loopbench-validity/`. A counted result can be traced to exactly the code and settings that produced it, and nothing changes silently mid-study.

1. Draft a `DEVIATION-N.md` in `benchmarks/loopbench-validity/drafts/`.
2. QA review.
3. Accepted.
4. Freeze: `FROZEN-N.sha256` lists sha256 of every file affecting a counted run. Check it from the repo root:

   ```bash
   sha256sum -c benchmarks/loopbench-validity/FROZEN-6.sha256
   ```

5. Launch from a clean worktree at the freeze commit with a pinned launcher under `benchmarks/loopbench-validity/results/acceptance-N/launcher/`.

Rules:

- Do not edit frozen files.
- Nothing launches on an unaccepted draft.
- [CRITERION.md](benchmarks/loopbench-validity/CRITERION.md) defines the pass criterion.
- [WORKLOG.md](benchmarks/loopbench-validity/WORKLOG.md) is the running log.

## Where results live

| Path | Contents |
| --- | --- |
| [`benchmarks/results/`](benchmarks/results/) | Published sim baselines, `lb-*-baseline.json` and `lb-*-run.json` |
| [`benchmarks/loopbench-validity/results/`](benchmarks/loopbench-validity/results/) | Validity study: acceptance-N attempts, probes, trials |
| [`packages/loopbench/submissions/`](packages/loopbench/submissions/) and [`leaderboard/`](packages/loopbench/leaderboard/) | Community submissions |

## Other material

- [Docs](docs/) (audits, community and project notes)
- [Manifesto](manifesto/MANIFESTO.md) (why the discipline exists)
- [Patterns](patterns/) (reusable loop patterns)
- [Loop library](loop-library/) (example LSS specs)
- [Demo](demo/README.md) (5-minute demo)
- [Status](STATUS.md) (project status)

License: MIT ([LICENSE](LICENSE)).
