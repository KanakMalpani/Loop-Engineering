# Submission dry-run — external path (maintainer reference)

Demonstrates the LoopForge-first path an external contributor would follow. **Not counted** as external adoption.

## Commands

```bash
pip install -r loopforge/requirements.txt

python -m loopforge fork \
  --from research-agent \
  --name dry-run-external \
  --output docs/submission-dry-run/dry-run-external.yaml \
  --suggest-level

python -m loopctl validate docs/submission-dry-run/dry-run-external.yaml
python -m loopctl score --spec docs/submission-dry-run/dry-run-external.yaml --json > docs/submission-dry-run/les.json
```

## Artifacts

| File | Purpose |
|------|---------|
| `dry-run-external.yaml` | Forked spec (generate locally) |
| `les.json` | Structural LES report (generate locally) |

See [BEAT_TEMPLATE.md](../../contributions/BEAT_TEMPLATE.md) for submission steps.
