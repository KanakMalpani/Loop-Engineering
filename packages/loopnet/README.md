<div align="center">

# LoopNet

**Ground truth for self-improving systems.**

Structured loop designs, execution trajectories, outcomes, and failure modes — so you can train, evaluate, and debug loops with data, not anecdotes.

<br>

[![CI](https://github.com/KanakMalpani/loopnet/actions/workflows/validate.yml/badge.svg)](https://github.com/KanakMalpani/loopnet/actions/workflows/validate.yml)
[![Code: MIT](https://img.shields.io/badge/Code-MIT-yellow.svg)](LICENSE)
[![Dataset: CC BY 4.0](https://img.shields.io/badge/Dataset-CC%20BY%204.0-green.svg)](DATACARD.md)
[![Records](https://img.shields.io/badge/records-545-blue.svg)](data/v0.2/records.jsonl)
[![Failure rate](https://img.shields.io/badge/failures-40%25-red.svg)](DATACARD.md)
[![Hugging Face v0.2](https://img.shields.io/badge/HF-loopnet--v0.2-yellow.svg)](https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2)
[![Hugging Face v0.1](https://img.shields.io/badge/HF-seed--v0.1-lightgrey.svg)](https://huggingface.co/datasets/KanakMalpani/loopnet-seed-v0.1)

<br>

[**Load the dataset**](#load-in-one-minute) · [**End-to-end tutorial**](guides/END-TO-END-TUTORIAL.md) · [**Contribute records**](guides/COMMUNITY-SUBMISSION.md) · [**Data card**](DATACARD.md)

</div>

---

## 🚀 Why this exists

Computer vision had ImageNet. RL had MuJoCo. **Loop engineering had no shared corpus.**

LoopNet fills that gap: every record is a complete loop story — spec, trajectory, outcome, LES breakdown, and when things break, a **`fail.*` code** from the [shared taxonomy](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/failure-taxonomy.md).

**Why it matters beyond storage:** train failure predictors, replay trajectories for **$0**, benchmark generalization against LoopBench holdouts, and publish research on *loop structure* — not scraped chat logs.

---

## Corpus overview

545 structured loop trajectories — outcomes, LES breakdowns, and labeled failures for replay and research.

<div align="center">
  <img src="assets/corpus-overview.png" alt="LoopNet v0.2 corpus breakdown" width="92%" />
</div>

| Stat | Value |
| :--- | ---: |
| Total records | **545** |
| Labeled failures | **40%** (218 records) |
| Seed corpus | 500 synthetic |
| Captured SimEnv runs | 45 |
| Load time | one Hugging Face line |

---

## ⚡ What you can do with it

| Use case | How LoopNet helps |
|----------|-------------------|
| **Failure prediction** | 42% labeled failures — models learn what breaking looks like |
| **Benchmark generalization** | Same schema as [LoopBench](https://github.com/KanakMalpani/LoopBench) holdout (v0.2) |
| **Zero-cost replay** | Feed [LoopGym](https://github.com/KanakMalpani/LoopGym) ReplayEnv — no API spend |
| **Research & fine-tuning** | JSONL + Parquet + Hugging Face — train on loop structure, not chat logs |
| **Community contributions** | [`ln/record-v1`](schema/loopnet-record-v1.json) + [submission guide](guides/COMMUNITY-SUBMISSION.md) |

---

## 🧩 Corpus at a glance (v0.2)

| Dimension | Value |
| :--- | :--- |
| **Records** | 545 (500 seed + 45 captured LoopGym runs) |
| **Failure rate** | 40% — meets corpus policy |
| **Schema** | `ln/record-v1` · pins `lss@1.1.0` + `les@1.0.0` |
| **Source** | Synthetic seed + SimEnv captures (3 LoopBench envs) |
| **License** | Code MIT · Dataset [CC BY 4.0](DATACARD.md) |

**Version registry:** [ECOSYSTEM_VERSIONS.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/ECOSYSTEM_VERSIONS.md). Seed-only v0.1 (500 records) remains at [`loopnet-seed-v0.1`](https://huggingface.co/datasets/KanakMalpani/loopnet-seed-v0.1).

---

## 🛠️ Load in one minute

**Hugging Face** (recommended — v0.2):

```python
from datasets import load_dataset

ds = load_dataset("KanakMalpani/loopnet-v0.2", split="train")
print(ds[0]["outcome"], ds[0]["pattern_slug"])
```

**Seed-only v0.1:**

```python
ds = load_dataset("KanakMalpani/loopnet-seed-v0.1", split="train")
```

**Stream from GitHub** (no clone):

```python
ds = load_dataset(
    "json",
    data_files="https://raw.githubusercontent.com/KanakMalpani/loopnet/main/data/seed/records.jsonl",
    split="train",
)
```

**Replay in LoopGym:**

```python
import loopgym as lg

env = lg.make("replay/loopnet-v1")
obs = env.reset(record_id="ln-00042")  # trajectory from corpus
```

---

## 📈 Validate and reproduce

Explored this corpus? Post on the [reproduction challenge](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) after [REPRODUCE.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/REPRODUCE.md).

---

## 🗺️ Where it sits

```mermaid
flowchart LR
  CORE[Loop Core Engineering]
  NET["<b>LoopNet</b><br/>you are here"]
  GYM[LoopGym ReplayEnv]
  BENCH[LoopBench holdout]

  CORE --> NET
  NET --> GYM
  NET -.-> BENCH
```

| Layer | Repo |
|-------|------|
| Specs & failure codes | [Loop Core Engineering](https://github.com/KanakMalpani/Loop-Core-Engineering) |
| **Dataset** | **LoopNet** |
| Execution | [LoopGym](https://github.com/KanakMalpani/LoopGym) |
| Observability | [loop-observability](https://github.com/KanakMalpani/loop-observability) |
| Public scores | [LoopBench](https://github.com/KanakMalpani/LoopBench) |

---

## 📂 Repository map

| Path | Purpose |
|------|---------|
| [`schema/loopnet-record-v1.json`](schema/loopnet-record-v1.json) | Canonical record schema |
| [`data/seed/records.jsonl`](data/seed/records.jsonl) | Seed corpus |
| [`scripts/validate_record.py`](scripts/validate_record.py) | Schema + policy validation |
| [`scripts/generate_seed.py`](scripts/generate_seed.py) | Deterministic regeneration (`--seed 42`) |
| [`guides/COMMUNITY-SUBMISSION.md`](guides/COMMUNITY-SUBMISSION.md) | Contribute records via PR |
| [`submissions/community/`](submissions/community/) | Community JSONL inbox |

---

## 📝 Citation

```bibtex
@dataset{loopnet_v02,
  title={LoopNet v0.2},
  author={Malpani, Kanak},
  year={2026},
  url={https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2}
}
```

<div align="center">

<sub><a href="CONTRIBUTING.md">Contributing</a></sub>

</div>
