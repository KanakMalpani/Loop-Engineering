---
license: mit
task_categories:
- other
language:
- en
tags:
- loop-engineering
- agent-loops
- lss
- les
- benchmarks
size_categories:
- 500<n<1K
---

# LoopNet v0.2 (Tier 1)

**545** public loop trajectories for Loop Engineering research — LSS-aligned records with iteration logs, termination reasons, and observed LES vectors.

| Field | Value |
|-------|-------|
| Records | **545** (Tier 1 public) |
| Schema | LSS 1.0 trajectory records |
| Primary repo | [Loop-Engineering](https://github.com/KanakMalpani/Loop-Engineering) |
| Reproduce | [REPRODUCE.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/REPRODUCE.md) |
| Paper | P4 — see [LOOPNET.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/research/LOOPNET.md) |

## Deprecated

**Do not cite** `KanakMalpani/loopnet-seed-v0.1` in new work. Use this dataset (`loopnet-v0.2`) as the primary public corpus.

## Quick load

```python
from datasets import load_dataset
ds = load_dataset("KanakMalpani/loopnet-v0.2", split="train")
print(len(ds))  # 545
```

Or from the discipline repo:

```bash
git clone https://github.com/KanakMalpani/Loop-Engineering.git
pip install datasets
python examples/loopnet-explore/explore.py
```

## LoopGym replay

```bash
pip install loopgym
```

```python
import loopgym as lg
env = lg.make("replay/loopnet-v1")
obs = env.reset(record_id="<record_id from dataset>")
```

## Citation

See [Loop-Engineering CITATION.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/CITATION.md).
