# Contributing to LoopNet

## What belongs here

- LoopNet record schema (`ln/record-v1`)
- Seed and future corpus data with documented splits
- Validation scripts and dataset card
- HuggingFace builder and export tooling

## What does not belong here

- LSS schema — [Loop Core Engineering](https://github.com/KanakMalpani/Loop-Core-Engineering)
- Loop execution — [LoopGym](https://github.com/KanakMalpani/LoopGym)
- Benchmark tasks — [LoopBench](https://github.com/KanakMalpani/LoopBench)

## Before opening a PR

```bash
pip install -r requirements.txt
python scripts/generate_seed.py --count 500 --seed 42
python scripts/validate_record.py --require-count 500
```

## v0.2 captured data (LoopGym → LoopNet)

See [V0.2-PLAN.md](V0.2-PLAN.md). Capture real trajectories:

```bash
pip install loopgym

loopgym capture loopbench/code-repair-v1 \
  --task-ids cr-001,cr-002,cr-003 \
  --seeds 0,1,2,3,4 \
  --failure-seeds 2,3,4 \
  -o data/captured/code-repair-v1.jsonl

python scripts/validate_record.py data/captured/code-repair-v1.jsonl --skip-corpus-policy
python scripts/merge_corpus.py --validate
```

## Community submissions

See **[guides/COMMUNITY-SUBMISSION.md](guides/COMMUNITY-SUBMISSION.md)**. Summary:

1. Add `submissions/community/{your-handle}.jsonl`
2. `python scripts/validate_community.py submissions/community/your-handle.jsonl`
3. Use the **community_records** PR template
4. Every record: `source: community`, `contributor.handle`, CC BY 4.0, no secrets/PII

## License

Code contributions: MIT. Dataset contributions: CC BY 4.0 (see [DATACARD.md](DATACARD.md)).
