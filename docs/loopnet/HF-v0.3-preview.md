# LoopNet v0.3 — Hugging Face preview card

Schema merged in [loopnet PR #1](https://github.com/KanakMalpani/loopnet/pull/1).

## Preview upload (maintainer)

1. Clone [loopnet](https://github.com/KanakMalpani/loopnet) at `main` (v0.3 schema).
2. Export trace-native rows from discipline repo:

```bash
pip install "le-loop-stack>=0.1.0"
python scripts/run_submission_dryrun.py
python scripts/loopnet_export_trace.py --trace docs/submission-dry-run/trace.json --out /tmp/loopnet-v03-preview/
```

3. Upload dataset card to Hugging Face as **`loopnet-v0.3-preview`** (private preview until community DUA review).
4. Link card from [loopnet README](https://github.com/KanakMalpani/loopnet) and [ECOSYSTEM_VERSIONS.md](../../ECOSYSTEM_VERSIONS.md).

**CI:** Push workflow from [05-loopnet/.github/workflows/hf-dataset-upload.yml](https://github.com/KanakMalpani/loopnet/blob/main/.github/workflows/hf-dataset-upload.yml); set `HF_TOKEN` secret per [HF_TOKEN_SETUP.md](../maintainer/HF_TOKEN_SETUP.md); tag `loopnet-v0.3-preview` or run workflow_dispatch.

## Contributor path

[CONTRIBUTING-v0.3.md](./CONTRIBUTING-v0.3.md)

## Histograms

[histograms/](./histograms/)
