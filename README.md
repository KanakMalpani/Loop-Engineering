# Loop Engineering

This repository is the Loop Engineering monorepo. LoopBench is the benchmark for closed feedback loops (LSS YAML loop specs, scored with LES), run through LoopGym environments.

## Install

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e packages/loopgym -e packages/loopbench -e packages/loop-observability -e packages/loopnet
```

Python >= 3.12.

> **WARNING:** do NOT `pip install loopgym` from PyPI: PyPI has a different loopgym 0.1.4 (same version number as `packages/loopgym`) without `LiveEnv.run_episode`; it broke a benchmark launch. Check with: `python -c "import loopgym; print(loopgym.__file__)"` which must point into `packages/loopgym/`.

## Quickstart

Sim backend, no model calls:

```bash
loopgym list
loopbench list
loopgym run sim/mock-llm-v1 --seed 0
loopbench run --task LB-CR-1 --spec packages/loopgym/examples/minimal-loop.yaml --backend sim --seeds 0,1 -o /tmp/lb-cr-1.json
python packages/loopgym/examples/quickstart.py
```

## Package map

| Directory | Import / dist name | CLI | Role |
| --- | --- | --- | --- |
| `packages/loopgym` | loopgym 0.1.4 | `loopgym` (list, run, capture) | Environments: sim, live, replay backends; registry of env ids e.g. `loopbench/code-repair-v1` |
| `packages/loopbench` | loopbench 0.2.0 | `loopbench` (list, suite, run, validate, rank) | Tasks (LB-CR-1 ...), fixtures, submissions, leaderboard |
| `packages/loop-observability` | loopotel 0.1.0 | `loopotel-validate` | Trace/observability schema validation |
| `packages/loopnet` | loopnet 0.1.0 | none | Dataset/records of loop runs (LoopNet) |
| `packages/loop-core` | loop-engineering-core 1.0.0 | none | LSS/LES specs, schemas, tools |

## Frozen manifest and DEVIATION process

Acceptance runs use only frozen code in `benchmarks/loopbench-validity/`. `FROZEN-N.sha256` lists the sha256 of every file that affects a counted run. From the repo root:

```bash
sha256sum -c benchmarks/loopbench-validity/FROZEN-6.sha256
```

Current freeze: FROZEN-6, commit `f1f5ef9`, 56 entries.

Any change to frozen behaviour is written up first as `DEVIATION-N.md` (draft, QA review, accepted), then frozen into the next manifest. Nothing launches on an unaccepted draft. Drafts live in `benchmarks/loopbench-validity/drafts/`. Counted launches run from a clean worktree at the freeze commit, with a pinned launcher under `benchmarks/loopbench-validity/results/acceptance-N/launcher/`. [`CRITERION.md`](benchmarks/loopbench-validity/CRITERION.md) defines the pass criterion. [`WORKLOG.md`](benchmarks/loopbench-validity/WORKLOG.md) is the running log. Do not edit frozen files.

## Where results live

| Path | Contents |
| --- | --- |
| [`benchmarks/results/`](benchmarks/results/) | Published sim baselines, `lb-*-baseline.json` and `lb-*-run.json` |
| [`benchmarks/loopbench-validity/results/`](benchmarks/loopbench-validity/results/) | Validity study: acceptance-N attempts, probes, trials |
| [`packages/loopbench/submissions/`](packages/loopbench/submissions/) and [`leaderboard/`](packages/loopbench/leaderboard/) | Community submissions |

## Other material

- [Manifesto](manifesto/MANIFESTO.md)
- [Patterns](patterns/)
- [Loop library](loop-library/)
- [Docs](docs/)
- [Demo](demo/README.md)
- [Status](STATUS.md)

License: MIT ([LICENSE](LICENSE)).
