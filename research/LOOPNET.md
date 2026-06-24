# LoopNet v0.2 — Dataset Guide

LoopNet is the reference corpus for empirical Loop Engineering research. Tier 1 is **public** on Hugging Face; this guide connects the dataset to repository fundamentals and the P4 paper.

**Dataset:** https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2  
**GitHub:** https://github.com/KanakMalpani/loopnet  
**Paper:** P4 — *LoopNet Empirical Characterization* (see [PAPER_SERIES.md](PAPER_SERIES.md))

---

## Tier 1 snapshot (v0.2)

| Field | Value |
|-------|-------|
| Trajectories | 545 (Tier 1 public) |
| Schema | LSS-aligned trajectory records with iteration logs |
| Use | Calibration, empirical propositions, LoopGym replay |

**Deprecated:** `loopnet-seed-v0.1` — do not cite in new work.

---

## Key empirical findings (P4)

These statistics ground fundamentals and benchmark design:

| Metric | Finding | Repo link |
|--------|---------|-----------|
| Cost coupling | ρ(iterations, cost) ≈ 0.914 | [fundamentals/06-evaluation-systems.md](../fundamentals/06-evaluation-systems.md) |
| Process variability | Fano factor on iteration counts | [benchmarks/suite-overview.md](../benchmarks/suite-overview.md) |
| First-error index (FEI) | Early-iteration failure signal | [patterns/verification-loop.md](../patterns/verification-loop.md) |
| Lyapunov non-increasing | 72.5% (370/510) runs | [fundamentals/07-convergence.md](../fundamentals/07-convergence.md) (P3) |

---

## Schema overview

Each Tier-1 record typically includes:

- `loop_id`, `pattern`, `taxonomy_level`
- `iterations[]` — per-step state, action, evaluator scores
- `termination_reason`, `total_cost`, `les_vector` (when available)
- `metadata` — harness, model tier, timestamp

Full schema: LoopNet repo `schema/` directory.

---

## Quick explore (no API keys)

From repo root:

```bash
pip install datasets pyyaml
python examples/loopnet-explore/explore.py
```

This loads Tier 1 from Hugging Face and prints corpus summary statistics.

**After explore:** post on the [reproduction challenge](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) ([REPRODUCE.md](../contributions/REPRODUCE.md)).

---

## Using LoopNet with LoopGym

```bash
pip install loopgym
loopgym replay --dataset KanakMalpani/loopnet-v0.2 --split train --limit 5
```

See [LOOPGYM.md](LOOPGYM.md) and [LoopGym](https://github.com/KanakMalpani/LoopGym) for replay and simulation modes.

**Contribute trajectories:** LoopGym replay → [loopnet COMMUNITY-SUBMISSION](https://github.com/KanakMalpani/loopnet/blob/main/guides/COMMUNITY-SUBMISSION.md).

---

## Tier 2 (future)

Full records under data-use agreement — not required for public benchmarks. See LoopNet repo `CORPUS-POLICY.md`.

---

## Citation

```bibtex
@misc{loopnet-v02-2026,
  title        = {LoopNet v0.2: Empirical Corpus of Agent Loop Trajectories},
  author       = {Malpani, Kanak Anil},
  year         = {2026},
  howpublished = {\url{https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2}},
  note         = {Tier 1 public release; companion paper P4}
}
```

Full citation pack: [contributions/CITATION.md](../contributions/CITATION.md)
