# Submission dry-run — trace-native reference path

Maintainer-generated end-to-end path demonstrating what an **external** contributor should follow. **Not counted** as external adoption.

## Quick run

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" "loopgym>=0.1.2"

python scripts/run_submission_dryrun.py
```

## What it does

1. `loopforge intent` → LSS spec YAML  
2. `loopctl validate` + structural LES  
3. Loop Trace 1.0 (LoopGym or generic runtime)  
4. `loopctl trace validate` + observed LES  
5. LoopNet v0.3 draft row export  

## Artifacts

| File | Purpose |
|------|---------|
| `dry-run-external.yaml` | Intent-compiled spec |
| `trace.json` | Loop Trace 1.0 (generic runtime) |
| `trace-loopgym.json` | Loop Trace from LoopGym (when installed) |
| `observed-les.json` | Observed LES from trace |
| `loopnet-row.json` | LoopNet v0.3 draft row |
| `summary.json` | End-to-end manifest |

## Manual steps

```bash
loopforge intent "Fix failing unit tests from CI logs" \
  -o docs/submission-dry-run/dry-run-external.yaml --suggest-level

loopctl validate docs/submission-dry-run/dry-run-external.yaml
python scripts/generate_loopgym_trace_demo.py
loopctl trace validate docs/submission-dry-run/trace-loopgym.json
loopctl observed docs/submission-dry-run/trace-loopgym.json \
  --spec docs/submission-dry-run/dry-run-external.yaml --json
python scripts/loopnet_export_trace.py docs/submission-dry-run/trace-loopgym.json \
  -o docs/submission-dry-run/loopnet-row.json
```

## Related

- [BEAT_TEMPLATE.md](../../contributions/BEAT_TEMPLATE.md) — external LoopBench submission  
- [CONTRIBUTING-v0.3.md](../loopnet/CONTRIBUTING-v0.3.md) — LoopNet contributor path  
- [GOLDEN_PATH.md](../../contributions/GOLDEN_PATH.md) — practitioner onboarding  
