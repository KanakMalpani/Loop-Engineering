# Sync policy — LoopNet

**Dataset layer for Loop Engineering.**

| Artifact | Canonical source | This repo |
|----------|------------------|-----------|
| Record schema | **This repo** `schema/loopnet-record-v1.json` | `ln/record-v1` |
| Seed corpus | **This repo** `data/seed/` | CC BY 4.0 |
| Failure codes | [Loop Core Engineering](https://github.com/KanakMalpani/Loop-Core-Engineering) `specs/loop-ids.md` | cite `fail.*` only |
| LES categories | [Loop Core Engineering](https://github.com/KanakMalpani/Loop-Core-Engineering) `specs/les-1.0.md` | store observed values in records |

**Repository:** https://github.com/KanakMalpani/loopnet

## Downstream consumers

- [LoopGym](https://github.com/KanakMalpani/LoopGym) ReplayEnv — reads `data/seed/records.jsonl` (sibling clone or `LOOPNET_SEED_PATH`)
- [LoopBench](https://github.com/KanakMalpani/LoopBench) — holdout eval split (v0.2)

## Validation before release

```bash
python scripts/validate_record.py --require-count 500
```

## Do not duplicate

- LSS schema — validate against Loop Core Engineering
- Loop runtime — belongs in LoopGym
