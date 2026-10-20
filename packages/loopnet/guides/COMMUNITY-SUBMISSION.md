# Community record submissions

Contribute `ln/record-v1` trajectories to LoopNet. Accepted records are merged into the next corpus release and published on Hugging Face under **CC BY 4.0**.

## Quick path

```bash
pip install loopgym loopbench

# Capture with LoopGym (SimEnv — no API keys)
loopgym capture loopbench/code-repair-v1 \
  --task-ids cr-001 \
  --seeds 0,1,2 \
  -o my-records.jsonl

# Set community metadata (see checklist below), then validate
python scripts/validate_community.py my-records.jsonl

# Open a PR: copy file to submissions/community/your-handle.jsonl
```

## PR checklist

1. **File location:** `submissions/community/{your-handle}.jsonl` (one or more records per file)
2. **Schema:** every line validates as `ln/record-v1`
3. **Source:** `"source": "community"` on every record
4. **Contributor:** `"contributor": { "handle": "your-github-or-hf-handle" }`
5. **License:** you agree to **CC BY 4.0** for dataset content (code in PR is MIT)
6. **Privacy:** no API keys, emails, raw prompts with PII, or local file paths
7. **Redaction:** production captures must set `redaction.level` to `basic` or `full` — see [LABELING-GUIDE.md](LABELING-GUIDE.md)

## Required fields (per record)

| Field | Value |
|-------|-------|
| `record_id` | `ln-{uuid}` — must be unique globally |
| `schema_version` | `ln/record-v1` |
| `source` | `community` |
| `split` | `train`, `val`, or `test` |
| `trajectory` | ≥1 iteration with `goal_score` |
| `outcome` | `success`, `failure`, or `partial` |
| `contributor.handle` | your public handle |

## Validate locally

```bash
pip install -r requirements.txt
python scripts/validate_community.py submissions/community/your-handle.jsonl
```

CI runs the same check on PRs that touch `submissions/community/`.

## After merge

Maintainers run `scripts/merge_corpus.py --community-dir submissions/community` before a release. You do **not** need to edit `data/v0.2/records.jsonl` directly.

## Capture alternatives

| Method | When to use |
|--------|-------------|
| `loopgym capture` | LoopBench SimEnv trajectories (recommended) |
| `loopotel` + export | LTF trace → [trajectory mapping](https://github.com/KanakMalpani/loop-observability) |
| Hand-authored JSONL | Only if you fully conform to [schema](../schema/loopnet-record-v1.json) |

## Questions

Open a [GitHub Discussion](https://github.com/KanakMalpani/loopnet/discussions) or issue with the `community-data` label.
