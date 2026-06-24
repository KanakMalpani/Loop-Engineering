# Daily check-ins

Automated health reports from [`.github/workflows/daily-checkin.yml`](../../.github/workflows/daily-checkin.yml).

| File | Purpose |
|------|---------|
| [latest.md](./latest.md) | Most recent run (updated daily ~14:00 UTC) |
| [archive/](./archive/) | One file per day (`YYYY-MM-DD.md`) |

## What runs

1. `validate_loop_library.py` — all atomic + composed LSS specs
2. `reflection-loop/run.py` — mock runtime smoke test
3. `compose-loop/run.py` — nested composition smoke test
4. `composition_validator.py --library` — composition graph checks

## Run locally

```bash
python scripts/daily_checkin.py --output docs/checkins/latest.md
```

## On failure

CI opens or updates a GitHub issue (title prefix `Daily check-in failed`) when checks fail.
