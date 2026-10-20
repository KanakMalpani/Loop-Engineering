# 04 — loopnet

## One-line purpose

**LoopNet** — large-scale dataset of loop designs, trajectories, successes, and failures (the ImageNet of Loop Engineering).

## Why this repo exists

No field without ground truth. LoopNet enables ML on loop planning, failure prediction, and LES estimation.

## Scope (in scope)

- LoopNet Record schema v1 (see Phase 2 design)
- Seed corpus: 500 records (synthetic + curated from case studies)
- Import/export: JSONL, Parquet, HuggingFace dataset script
- Labeling guide + failure taxonomy alignment
- Train/val/test splits + data card
- Submission pipeline for community contributions

## Scope (out of scope)

- Running loops → `05-loopgym`
- Leaderboards → `06-loopbench`

## Deliverables v0.1

- [x] `schema/loopnet-record-v1.json`
- [x] `data/seed/` — 500 records (mostly synthetic v0.1)
- [x] `scripts/validate_record.py`
- [x] `scripts/upload_hf.py` (optional)
- [x] `DATACARD.md`

## Dependencies

- **01-loop-engineering-core** — LSS, failure codes, LES dimensions

## Data mix (target v1.0)

| Source | % | Notes |
|--------|---|-------|
| Synthetic | 40% | Known ground truth |
| Case study derived | 20% | From core repo |
| Redacted production | 20% | Requires consent |
| Community | 20% | Submit form |

**Critical:** Failed loops ≥ 40% of corpus (rarer, more valuable).

## Success criteria

`validate_record.py` passes on full seed; HuggingFace dataset loads in ≤3 lines; one baseline model notebook predicts failure_mode from first 3 iterations.

## Agent instructions

Prioritize **failed loop trajectories** with labeled failure taxonomy. Never commit secrets or PII.

## Status

✅ v0.1 shipped (2026-06-13)
