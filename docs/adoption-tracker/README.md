# Adoption tracker

Automated status for **2027 adoption signals** (community-owned items).

| File | Purpose |
|------|---------|
| [latest.md](./latest.md) | Human-readable dashboard (updated daily) |
| [latest.json](./latest.json) | Machine-readable snapshot |

## Signals tracked

| Signal | Green when |
|--------|------------|
| Non-maintainer LoopBench row | External submitter on [LoopBench leaderboard](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json) |
| Discussion #10 external comment | Non-maintainer reproduction report |
| Discussion #11 external comment | Framework maintainer RFC feedback |
| PyPI loopbench >= 0.1.1 | Published on [PyPI](https://pypi.org/project/loopbench/) |
| LSS 1.1 stable | `lss-1.1.md` in Loop-Core (not draft only) |
| Good-first issues #4, #7–#9 | Closed when contributed |

## Run locally

```bash
python scripts/track_adoption_signals.py
python scripts/track_adoption_signals.py --output docs/adoption-tracker/latest.md --json docs/adoption-tracker/latest.json
```

Included in `scripts/daily_checkin.py` and [.github/workflows/daily-checkin.yml](../.github/workflows/daily-checkin.yml).

See [All about loops/NEXT_STEPS.md](../../All%20about%20loops/NEXT_STEPS.md).
