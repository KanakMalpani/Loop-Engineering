# Status

| Field | Value |
|-------|-------|
| **Phase** | v0.2 complete — tutorial shipped |
| **Symbol** | ✅ |
| **Notes** | HF `loopnet-v0.2` live; ReplayEnv + [end-to-end tutorial](guides/END-TO-END-TUTORIAL.md) |

## Completion checklist

- [x] `schema/loopnet-record-v1.json`
- [x] `data/seed/` — 500 records (synthetic v0.1)
- [x] `scripts/validate_record.py`
- [x] `scripts/upload_hf.py` (optional)
- [x] `DATACARD.md`
- [x] `guides/LABELING-GUIDE.md`
- [x] `scripts/generate_seed.py`
- [x] `scripts/baseline_failure_mode.py`
- [x] `datasets/loopnet/loopnet.py` (HuggingFace builder)
- [x] CI: validate workflow
- [x] `SYNC.md` — canonical source policy
- [x] `loopgym capture` pipeline + `data/captured/` (45 records)
- [x] `scripts/merge_corpus.py` → `data/v0.2/records.jsonl` (545 records, 40% failures)
- [x] Hugging Face upload `loopnet-v0.2` — [KanakMalpani/loopnet-v0.2](https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2)
- [x] [End-to-end tutorial](guides/END-TO-END-TUTORIAL.md) + `examples/v02_workflow.py`
- [x] [Community submission guide](guides/COMMUNITY-SUBMISSION.md) + PR template + CI validation

## Corpus stats (seed v0.1)

Regenerate with `python scripts/generate_seed.py` then validate.

| Metric | Value |
|--------|-------|
| Records | 500 |
| Failure rate | 42.0% (210 failures) |
| Source | 100% synthetic |

## Links

- Parent workspace: [../README.md](../README.md)
- Core dependency: [../01-loop-engineering-core/](../01-loop-engineering-core/)
- Agent brief: [../AGENT-BRIEF.md](../AGENT-BRIEF.md)
- Plan: [PLAN.md](PLAN.md)
