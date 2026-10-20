# Publishing LoopNet to Hugging Face

## One-time setup

1. Create a Hugging Face account and [access token](https://huggingface.co/settings/tokens) with **write** scope.
2. Add **`HF_TOKEN`** to this repo: Settings → Secrets → Actions.

## Upload via GitHub Actions

**Actions → Upload to Hugging Face → Run workflow**

Default dataset id: `KanakMalpani/loopnet-seed-v0.1`

## Upload locally

```bash
pip install -e ".[dev]"
python scripts/validate_record.py --require-count 500
export HF_TOKEN=hf_...
python scripts/upload_hf.py --export-parquet --upload --repo-id KanakMalpani/loopnet-seed-v0.1
```

## Load after publish

```python
from datasets import load_dataset

ds = load_dataset("KanakMalpani/loopnet-seed-v0.1", split="train")
```

Or from GitHub JSONL:

```python
ds = load_dataset(
    "json",
    data_files="https://raw.githubusercontent.com/KanakMalpani/loopnet/main/data/seed/records.jsonl",
    split="train",
)
```
