# Community Platform — rollout status

**North star:** Loop-Engineering = learn + try · LoopBench = rank + recognize · Ops = pinned GitHub dashboard (change-only).

**Last updated:** 2026-06-25  
**Current phase:** Phase 13 — Community Platform v1 (shipped)  
**Living tracker:** update this file when milestones ship; CI may append to [Automation log](#automation-log) only.

Related: [LOOP_PLAYGROUND.md](../../contributions/LOOP_PLAYGROUND.md) · [ADOPTION_AUTOMATION.md](./ADOPTION_AUTOMATION.md) · [EXTERNAL_SUBMISSIONS.md](../../contributions/EXTERNAL_SUBMISSIONS.md)

---

## Workstream checklist

### Loop-Engineering

- [x] `docs/maintainer/COMMUNITY_PLATFORM_STATUS.md` (this file)
- [x] `contributions/LOOP_PLAYGROUND.md`
- [x] README + EXTERNAL_SUBMISSIONS + GOLDEN_PATH cross-links
- [x] `docs/community/CONTRIBUTOR_BADGE.md`
- [x] `docs/community/spotlight/` index + first edition
- [x] `scripts/leaderboard_common.py` + `scripts/render_leaderboard_preview.py`
- [x] `scripts/ecosystem_digest.py` + `.github/workflows/ecosystem-digest.yml`
- [x] `community_platform_v1` adoption signal in `track_adoption_signals.py`

### LoopBench (sync via [ecosystem-sync](../ecosystem-sync/))

- [x] `docs/ecosystem-sync/LoopBench/scripts/render_leaderboard.py`
- [x] `docs/ecosystem-sync/LoopBench/leaderboard/README.md`
- [x] `docs/ecosystem-sync/LoopBench/.github/workflows/leaderboard-render.yml`
- [x] `docs/ecosystem-sync/LoopBench/.github/workflows/leaderboard-pr-hint.yml`
- [x] `docs/ecosystem-sync/LoopBench/.github/workflows/pages.yml`
- [x] `docs/ecosystem-sync/LoopBench/.github/workflows/sync-platform-pack.yml` (hourly pull from LE)
- [x] `docs/ecosystem-sync/LoopBench/.github/workflows/leaderboard-validate.yml`
- [x] **Push mirrors to LoopBench** — automated via `sync-platform-pack` (LE mirror is source of truth)
- [x] LoopBench README `<!-- LEADERBOARD:START -->` markers live on remote

### Manual setup (maintainer)

- [x] Create pinned issue: `Loop Engineering ops dashboard (auto-updated — do not comment)` → [#13](https://github.com/KanakMalpani/Loop-Engineering/issues/13)
- [x] Set repo variable `OPS_DASHBOARD_ISSUE_NUMBER` = `13` on Loop-Engineering
- [x] Pin the issue on GitHub

---

## Completed log

| Date | Item | Artifact |
|------|------|----------|
| 2026-06-17 | Living status tracker | This file |
| 2026-06-17 | Loop Playground hub | [LOOP_PLAYGROUND.md](../../contributions/LOOP_PLAYGROUND.md) |
| 2026-06-17 | Recognition layer | [CONTRIBUTOR_BADGE.md](../community/CONTRIBUTOR_BADGE.md) · [spotlight/](../community/spotlight/) |
| 2026-06-17 | Leaderboard render (LE preview) | [render_leaderboard_preview.py](../../scripts/render_leaderboard_preview.py) |
| 2026-06-17 | Ecosystem digest | [ecosystem_digest.py](../../scripts/ecosystem_digest.py) |
| 2026-06-17 | LoopBench sync pack | [docs/ecosystem-sync/LoopBench/](../ecosystem-sync/LoopBench/) |
| 2026-06-25 | Full LoopBench automation | Hourly sync pack pull · validate on PR · render → Pages chain |
| 2026-06-25 | Pinned ops dashboard | [Issue #13](https://github.com/KanakMalpani/Loop-Engineering/issues/13) · `OPS_DASHBOARD_ISSUE_NUMBER=13` |

---

## In progress

| Item | Owner | Notes |
|------|-------|-------|
| First external LoopBench row | Community | [#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) |

---

## Blocked / external

| Item | Unblocks when |
|------|----------------|
| First external LoopBench row | Non-maintainer merges [entries.json](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json) PR ([#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4)) |
| First Community Spotlight feature | Verified external submission or standout [#10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) repro |

---

## Success metrics

| Metric | Target | Current |
|--------|--------|---------|
| Single doc: zero → `loopbench validate` | `LOOP_PLAYGROUND.md` | Shipped |
| Live rankings on LoopBench | `leaderboard/LIVE.md` + README block | Live |
| Maintainer manual leaderboard checks | 0 unless dashboard shows delta | [#13](https://github.com/KanakMalpani/Loop-Engineering/issues/13) pinned |
| External LoopBench row | ≥ 1 non-maintainer | Yellow (maintainer-only rows) |

---

## Pinned ops dashboard setup

1. **Create issue** on Loop-Engineering with title exactly:  
   `Loop Engineering ops dashboard (auto-updated — do not comment)`
2. **Repository variable:** Settings → Secrets and variables → Actions → Variables →  
   `OPS_DASHBOARD_ISSUE_NUMBER` = issue number (integer).
3. **Pin** the issue on the Issues page.
4. **Verify:** run workflow `Ecosystem digest` manually; issue body should update when leaderboard or tracker changes.

The [ecosystem-digest.yml](../../.github/workflows/ecosystem-digest.yml) workflow uses Actions cache (`ecosystem-digest-v1`) — no git commit on every poll.

---

## Automation log

_Append-only. CI adds lines when leaderboard or adoption signals change (max 1 per signal type per week)._

<!-- AUTOMATION-LOG:START -->
- 2026-06-25 UTC: Platform shipped — LoopBench LIVE.md live, ops dashboard [#13](https://github.com/KanakMalpani/Loop-Engineering/issues/13) populated.
- 2026-06-25 14:39 UTC: digest changed; external=none
<!-- AUTOMATION-LOG:END -->

---

## Explicit non-goals

- Auto-updating top 10 in Loop-Engineering README every 12h
- Auto-merge external LoopBench PRs
- Bot-generated fake external submissions
- Slack/Discord webhook in v1 (GitHub pinned issue only)
