# Adoption automation

**Live status:** [COMMUNITY_PLATFORM_STATUS.md](./COMMUNITY_PLATFORM_STATUS.md) · Pinned ops issue [#13](https://github.com/KanakMalpani/Loop-Engineering/issues/13)

**Purpose:** Notify on adoption changes only — never fabricate external signals.

Related: [track_adoption_signals.py](../../scripts/track_adoption_signals.py) · [ecosystem_digest.py](../../scripts/ecosystem_digest.py) · [ADOPTION.md](../../contributions/ADOPTION.md)

---

## What is automated (shipped)

| Component | File | Role |
|-----------|------|------|
| Daily tracker | `track_adoption_signals.py` + `adoption-tracker.yml` | Snapshot JSON/MD under `docs/adoption-tracker/` |
| Ecosystem digest | `ecosystem_digest.py` + `ecosystem-digest.yml` | Leaderboard delta, LoopBench PRs, outreach replies → ops #13 |
| PR hints (LE) | `external-submission-hint.yml` | Case study / repro checklist on relevant PRs |
| Leaderboard validate | LoopBench sync pack | PR validation on `entries.json` |
| HF LoopNet upload | loopnet sync workflow | Tag-triggered dataset upload (needs `HF_TOKEN`) |

---

## What stays manual

- Approving LoopBench leaderboard merges
- First contact in external communities (use `adoption_wave11.py` / `adoption_wave12.py`)
- Answering contributor questions on #4 / #7 / #10

Automation **surfaces** work; it cannot **fabricate** adoption.

---

## Ops hub options

Pick one primary surface — repos stay thin (workflows only POST on change):

| Option | Setup | Best for |
|--------|-------|----------|
| **Pinned dashboard issue #13** | Shipped via `ecosystem_digest.py` | GitHub-only |
| **Slack / Discord webhook** | Secret `ADOPTION_WEBHOOK_URL` on digest workflow | Mobile pings |
| **GitHub watch filters** | Zero code — watch LoopBench PRs + LE #4/#7/#10 | Quick win |

**Do not:** bot fake external rows, daily spam on #4/#11, `pull_request_target` secrets on fork PRs, auto-merge external LoopBench PRs.

---

## Outreach cadence

```bash
python scripts/adoption_wave11.py   # initial partner outreach
python scripts/adoption_wave12.py   # +7d follow-up + PARTNER_LOOPBENCH_SUBMIT.md
python scripts/adoption_wave10.py   # platform gravity copy
```

Index: [docs/outreach/README.md](../outreach/README.md)

---

## Remaining (optional)

| Item | Notes |
|------|-------|
| `ADOPTION_WEBHOOK_URL` | Wire Slack/Discord to digest workflow |
| LoopBench `leaderboard-pr-hint.yml` | Checklist comment on external PRs (sync pack) |
| Monthly outreach cron | Re-run wave 10/11 copy; human posts externally |

---

## Success metrics

| Metric | Target |
|--------|--------|
| Manual tracker checks | 0/week unless digest pings |
| Bot comments per external PR | ≤ 1 checklist |
| External #4 green | Requires 1 real non-maintainer contributor |
