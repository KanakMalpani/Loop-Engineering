# Hugging Face token setup — LoopNet v0.3 preview

## 1. Create token

1. Log in at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. **New token** → role **Write** (dataset upload)
3. Copy token (starts with `hf_`)

## 2. GitHub secret

1. [loopnet → Settings → Secrets → Actions](https://github.com/KanakMalpani/loopnet/settings/secrets/actions)
2. **New repository secret**
3. Name: `HF_TOKEN`
4. Value: paste `hf_...`

## 3. Create dataset repo (first time)

```bash
huggingface-cli repo create loopnet-v0.3-preview --type dataset --organization KanakMalpani
```

Or create via the Hugging Face UI under `KanakMalpani/loopnet-v0.3-preview`.

## 4. Export preview rows (local)

From `01-loop-engineering`:

```bash
pip install "le-loop-stack>=0.1.0"
python scripts/run_submission_dryrun.py
python scripts/loopnet_export_trace.py --trace docs/submission-dry-run/trace.json --out /tmp/loopnet-v03-preview/
```

Copy exported JSONL into `05-loopnet/data/` if committing rows to the loopnet repo.

## 5. Upload via CI

Workflow: [05-loopnet/.github/workflows/hf-dataset-upload.yml](https://github.com/KanakMalpani/loopnet/blob/main/.github/workflows/hf-dataset-upload.yml)

**Option A — tag push:**

```bash
git tag loopnet-v0.3-preview
git push origin loopnet-v0.3-preview
```

**Option B — manual dispatch:**

Actions → **Upload LoopNet dataset to Hugging Face** → Run workflow → `dataset_slug`: `loopnet-v0.3-preview`

If `HF_TOKEN` is missing, the workflow logs a skip (non-failing).

## 6. Verify

- Dataset card loads: `https://huggingface.co/datasets/KanakMalpani/loopnet-v0.3-preview`
- Update [ECOSYSTEM_VERSIONS.md](../../ECOSYSTEM_VERSIONS.md) and [HF-v0.3-preview.md](../loopnet/HF-v0.3-preview.md)
