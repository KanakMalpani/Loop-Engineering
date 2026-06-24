# Loop Engineering Ecosystem

**One discipline. Four repos. Zero schema drift.**

This is the official install map for the published stack. Start here if you are building, benchmarking, or researching self-improving AI systems.

**Version registry (canonical):** [Loop-Engineering/ECOSYSTEM_VERSIONS.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/ECOSYSTEM_VERSIONS.md)

---

## The four layers

| # | Repository | Analogy | One line |
|---|------------|---------|----------|
| 1 | [**Loop Core Engineering**](https://github.com/KanakMalpani/Loop-Core-Engineering) | The HTTP spec | LSS, LES, validators, IDs |
| 2 | [**LoopNet**](https://github.com/KanakMalpani/loopnet) | ImageNet | 545 loop trajectories + failures (v0.2) |
| 3 | [**LoopGym**](https://github.com/KanakMalpani/LoopGym) | OpenAI Gym | Run loops (sim / live / replay) |
| 4 | [**LoopBench**](https://github.com/KanakMalpani/LoopBench) | MLPerf | Score loops on public tasks |

**Narrative home** (manifesto, patterns, case studies, reproduction path): [Loop Engineering](https://github.com/KanakMalpani/Loop-Engineering)

---

## Version pins

| Pin | Location |
|-----|----------|
| `lss@1.0.0` | [`specs/lss-1.0.schema.json`](specs/lss-1.0.schema.json) |
| `les@1.0.0` | [`specs/les-1.0.md`](specs/les-1.0.md) |
| `loopnet@0.2.0` | [HF loopnet-v0.2](https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2) · [loopnet repo](https://github.com/KanakMalpani/loopnet) |
| `loopgym@0.1.x` | [LoopGym](https://github.com/KanakMalpani/LoopGym) · `pip install loopgym` |
| `loopbench@0.1.x` | [LoopBench](https://github.com/KanakMalpani/LoopBench) · `pip install loopbench` |

**Deprecated for new work:** `loopnet-seed-v0.1` (500 seed-only records). Use **v0.2** (545 records).

---

## 5-minute full stack

```bash
# Specs & validators
git clone https://github.com/KanakMalpani/Loop-Core-Engineering.git

# Runtime + benchmarks
pip install loopgym loopbench

# First benchmark run
loopbench run \
  --task LB-CR-1 \
  --spec submissions/examples/spec-fast-loop.yaml \
  --seeds 0,1 \
  -o results.json

loopbench validate results.json
```

Clone [loopnet](https://github.com/KanakMalpani/loopnet) when you need ReplayEnv or dataset R&D.

**Reproduce the discipline stack (≤60 min):** [Loop-Engineering/REPRODUCE.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/REPRODUCE.md)

---

## Load LoopNet v0.2 (recommended)

```python
from datasets import load_dataset

ds = load_dataset("KanakMalpani/loopnet-v0.2", split="train")
print(len(ds), ds[0]["pattern_slug"])
```

**Seed-only v0.1 (legacy):**

```python
ds = load_dataset("KanakMalpani/loopnet-seed-v0.1", split="train")
```

**Stream from GitHub (v0.2 JSONL):**

```python
ds = load_dataset(
    "json",
    data_files="https://raw.githubusercontent.com/KanakMalpani/loopnet/main/data/v0.2/records.jsonl",
    split="train",
)
```

---

## Dependency graph

```
Loop Core Engineering
        │
        ├──► LoopNet (dataset v0.2)
        │
        └──► LoopGym (runtime) ──► LoopBench (measurement)
```

CI in downstream repos checks out **Loop Core Engineering** from GitHub — never a forked schema.

---

## Where to go next

| I want to… | Go to |
|------------|-------|
| Write a valid loop spec | [LSS 1.0 overview](specs/lss-1.0.md) |
| Understand scoring | [LES 1.0](specs/les-1.0.md) |
| Run a loop locally | [LoopGym README](https://github.com/KanakMalpani/LoopGym) |
| Get a public score | [LoopBench README](https://github.com/KanakMalpani/LoopBench) |
| Train on loop trajectories | [LoopNet v0.2](https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2) |
| Read the philosophy | [Loop Engineering manifesto](https://github.com/KanakMalpani/Loop-Engineering) |
| Reproduce end-to-end | [REPRODUCE.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/REPRODUCE.md) |
