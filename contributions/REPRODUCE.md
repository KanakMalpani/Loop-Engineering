# Reproduce Loop Engineering in One Hour

This checklist satisfies the 2026 roadmap exit criterion: an external team can fork the repo, validate LSS, run one benchmark, and publish LES **without maintainer hand-holding**.

**Target time:** ≤60 minutes on a clean machine with Python 3.10+.

**When done:** post your report on the [reproduction challenge](https://github.com/KanakMalpani/Loop-Engineering/discussions/10).

---

## Prerequisites

- Python 3.10 or newer
- Git
- Internet access (pip, Hugging Face optional for Step 6)

---

## Step 1 — Clone repositories (5 min)

```bash
git clone https://github.com/KanakMalpani/Loop-Engineering.git
git clone https://github.com/KanakMalpani/Loop-Core-Engineering.git
cd Loop-Engineering
```

---

## Step 2 — Install dependencies (5 min)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix:    source .venv/bin/activate

pip install pyyaml jsonschema
pip install loopgym loopbench   # optional but recommended for Steps 5–6
```

Record installed versions:

```bash
pip show loopgym loopbench pyyaml | findstr /i "Name Version"
# Unix: pip show loopgym loopbench pyyaml | grep -E 'Name|Version'
```

---

## Step 3 — Validate an LSS spec (10 min)

**Option A — local validator (this repo):**

```bash
python tools/loop_validator.py loop-library/autonomous-debugger.yaml
```

Expected: `VALID: loop-library\autonomous-debugger.yaml`

**Option B — canonical validator (Loop Core Engineering):**

```bash
cd ../Loop-Core-Engineering
pip install pyyaml jsonschema
python tools/validate_lss.py ../Loop-Engineering/loop-library/autonomous-debugger.yaml
```

**Validate entire library:**

```bash
cd ../Loop-Engineering
python scripts/validate_loop_library.py
```

Expected: `OK: all 10 loop-library specs valid`

**Pick taxonomy level (LE-OP-11 v0.1) before authoring a new spec:**

```bash
pip install datasets
python tools/level_recommender.py --pattern research-loop --iter-len 4 --workers 1
```

Optional: warn if declared level disagrees with recommender:

```bash
python scripts/validate_loop_library.py --warn-level
```

---

## Step 4 — Run a loop example (10 min)

No API keys required:

```bash
python examples/reflection-loop/run.py
```

Expected output includes `Success: True` and a quality score.

---

## Step 5 — Compute LES from an LSS spec (10 min)

Structural LES estimate from spec design (not a live run):

```bash
python tools/les_calculator.py --spec loop-library/autonomous-debugger.yaml
python tools/les_calculator.py --spec loop-library/autonomous-debugger.yaml --json > my_les_report.json
```

Inspect `my_les_report.json` — eight LES dimensions plus composite score.

---

## Step 6 — LoopBench baseline (optional, 15 min)

If `loopbench` is installed (`pip install "loopbench>=0.1.1"`):

```bash
loopbench list
loopbench run --task LB-CR-1 --spec loop-library/autonomous-debugger.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
```

Guides: [BEAT_LB-CR-1.md](BEAT_LB-CR-1.md) · [BEAT_LB-RS-1.md](BEAT_LB-RS-1.md) · [BEAT_LB-MA-1.md](BEAT_LB-MA-1.md) · [BEAT_LB-COMP-1.md](BEAT_LB-COMP-1.md)

**Composed loop (LoopGym env):**

```bash
python examples/compose-loop/run.py loop-library/compositions/scenario-swarm-rehearsal.yaml
pip install "git+https://github.com/KanakMalpani/LoopGym.git"
python -c "import loopgym as lg; print(lg.make('loopbench/composed-swarm-v1').run_episode(task_id='comp-001', seed=0))"
```

Published maintainer baselines: [benchmarks/results/](../benchmarks/results/)

---

## Step 7 — Explore LoopNet v0.2 (optional, 10 min)

```bash
pip install datasets
python examples/loopnet-explore/explore.py
```

See [research/LOOPNET.md](../research/LOOPNET.md).

---

## Step 8 — Report your reproduction

Open a GitHub issue using the **Benchmark submission** template, or comment on the reproduction challenge (see [contributions/ADOPTION_SIGNAL.md](ADOPTION_SIGNAL.md)).

Include:

- [ ] Python version and `pip show` output
- [ ] Validator pass/fail for one spec
- [ ] Reflection-loop run output
- [ ] LES JSON file
- [ ] (Optional) LoopBench run matching ALS-T2

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `jsonschema` missing | `pip install jsonschema` |
| Validator INVALID | Use specs in `loop-library/` after 2026-06 migration; run `scripts/validate_loop_library.py` |
| LoopNet load fails | Check network; HF dataset `KanakMalpani/loopnet-v0.2` |
| loopbench not found | `pip install loopbench` or skip Step 6 |

---

## Version pins (tested 2026-06-17)

| Package | Version | Notes |
|---------|---------|-------|
| Python | 3.14.3 | Maintainer smoke test |
| pyyaml | 6.0.3 | Required |
| jsonschema | 4.26.0 | Required for validator |
| datasets | 5.0.0 | LoopNet explore (545 records) |
| loopgym | 0.1.0 | Optional replay env |
| loopbench | 0.1.1 | LB-CR-1 / LB-RS-1 / LB-MA-1 / LB-COMP-1 |

Full registry: [ECOSYSTEM_VERSIONS.md](../ECOSYSTEM_VERSIONS.md)

---

## Success criteria

You have reproduced Loop Engineering when you can:

1. Validate at least one LSS YAML file
2. Run `examples/reflection-loop/run.py` successfully
3. Emit an LES JSON report from `les_calculator.py`

That meets the 2026 foundation exit criterion for external reproducibility.
