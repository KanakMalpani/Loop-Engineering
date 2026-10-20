# Captured trajectories (v0.2+)

Real loop runs exported from [LoopGym](https://github.com/KanakMalpani/LoopGym) via:

```bash
pip install loopgym

loopgym capture loopbench/code-repair-v1 \
  --task-ids cr-001,cr-002 \
  --seeds 0,1,2,3,4 \
  -o data/captured/code-repair-v1.jsonl
```

Validate a capture file:

```bash
python scripts/validate_record.py data/captured/code-repair-v1.jsonl --skip-corpus-policy
```

Merge with seed corpus:

```bash
python scripts/merge_corpus.py --validate
```

Output: `data/v0.2/records.jsonl`

Do not commit secrets, API keys, or unredacted PII. See [guides/LABELING-GUIDE.md](../guides/LABELING-GUIDE.md).
