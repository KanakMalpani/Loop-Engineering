# Community Platform — rollout status

**North star:** Loop-Engineering = learn + try · LoopBench = rank + recognize · Ops = pinned GitHub dashboard (change-only).

**Last updated:** 2026-06-28  
**Current phase:** Phase 13 — Community Platform v1 (shipped)  
**Living tracker:** update this file when milestones ship; CI may append to [Automation log](#automation-log) only.

Related: [LOOP_PLAYGROUND.md](../../contributions/LOOP_PLAYGROUND.md) · [ADOPTION_AUTOMATION.md](./ADOPTION_AUTOMATION.md) · [EXTERNAL_SUBMISSIONS.md](../../contributions/EXTERNAL_SUBMISSIONS.md) · [AGENT_BRIEFS.md](./AGENT_BRIEFS.md)

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
- [x] `.github/workflows/external-submission-hint.yml` (LE case study / repro PRs)
- [x] Partner submission pack — [PARTNER_LOOPBENCH_SUBMIT.md](../../contributions/PARTNER_LOOPBENCH_SUBMIT.md)
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
| 2026-06-25 | PyPI stack + partner pack + wave 12 | `le-loop-stack` + `le-loopctl` 0.2.0 on PyPI · [PARTNER_LOOPBENCH_SUBMIT.md](../../contributions/PARTNER_LOOPBENCH_SUBMIT.md) |
| 2026-06-25 | Full LoopBench automation | Hourly sync pack pull · validate on PR · render → Pages chain |
| 2026-06-25 | Pinned ops dashboard | [Issue #13](https://github.com/KanakMalpani/Loop-Engineering/issues/13) · `OPS_DASHBOARD_ISSUE_NUMBER=13` |
| 2026-06-28 | Wave 13 outreach | Reflexion · DSPy · SmolAgents · #10 beat challenge · #12 exam pilots · #11 RFC |
| 2026-06-28 | Wave 15/16 suite submissions | 4 comparison suites · loop mix recipes · dual-track policy (LB-CR-1 easy vs `--suite` preferred) |
| 2026-06-28 | Loop institute v0.1 | `13-loop-institute/CHARTER.md` · RFC template |
| 2026-06-28 | LoopNet HF CLI fix | `hf upload` workflow · [HF_TOKEN_SETUP.md](./HF_TOKEN_SETUP.md) |

---

## In progress

| Item | Owner | Notes |
|------|-------|-------|
| First external LoopBench row | Community | [#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) · wave 11–15 sent · [partner pack](../../contributions/PARTNER_LOOPBENCH_SUBMIT.md) · suite path [BEAT_suite-repair.md](../../contributions/BEAT_suite-repair.md) |

---

## Wave 15/16 — dual-track submission policy

LoopBench v0.2 introduces **4 comparison suites** over **19 micro-tasks** ([SUITE-OVERVIEW.md](../ecosystem-sync/LoopBench/docs/SUITE-OVERVIEW.md)). Community submissions follow two tracks:

| Track | Command | Leaderboard placement | Outreach |
|-------|---------|----------------------|----------|
| **Easy (1a)** | `loopbench run --task LB-CR-1 …` | Per-task tab only | Wave 11–12 partner pack |
| **Preferred (1b)** | `loopbench run --suite suite-* …` | Generalist (`grand_composite`) + suite tabs | Wave 15 (`adoption_wave15.py`) |

**Rules:**

- Both tracks count toward external adoption when merged from a non-maintainer account.
- Path 1b requires `suite_scores` + `grand_composite` in `entries.json` ([ROW_SCHEMA.md](../ecosystem-sync/LoopBench/leaderboard/ROW_SCHEMA.md)).
- Set `partial: true` when fewer than 4 suite scores — row ranks on suite tabs only, excluded from generalist.
- Wave 16 maintainer follow-up nudges wave 11–14 responders toward Path 1b without deprecating Path 1a.

Docs: [LOOP_PLAYGROUND.md](../../contributions/LOOP_PLAYGROUND.md) · [EXTERNAL_SUBMISSIONS.md](../../contributions/EXTERNAL_SUBMISSIONS.md) · `python scripts/adoption_wave15.py`

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
- 2026-06-25 UTC: Adoption wave 11 — invited [Agentless #86](https://github.com/OpenAutoCoder/Agentless/issues/86), [Aider #5328](https://github.com/Aider-AI/aider/issues/5328), [OpenHands #14984](https://github.com/OpenHands/OpenHands/issues/14984) for first external LoopBench row.
- 2026-06-25 UTC: Wave 12 follow-up + partner pack + PyPI stack published (`le-loop-stack`, `le-loopctl` 0.2.0).
- 2026-06-25 20:05 UTC: digest changed; external=none
- 2026-06-26 04:01 UTC: digest changed; external=none
- 2026-06-26 09:33 UTC: digest changed; external=none
- 2026-06-26 14:31 UTC: digest changed; external=none
- 2026-06-26 19:53 UTC: digest changed; external=none
- 2026-06-27 03:45 UTC: digest changed; external=none
- 2026-06-27 08:40 UTC: digest changed; external=none
- 2026-06-27 13:49 UTC: digest changed; external=none
- 2026-06-27 19:25 UTC: digest changed; external=none
- 2026-06-28 04:09 UTC: digest changed; external=none
- 2026-06-28 08:57 UTC: digest changed; external=none
- 2026-06-28 13:54 UTC: digest changed; external=none
- 2026-06-28 19:25 UTC: digest changed; external=none
- 2026-06-29 04:15 UTC: digest changed; external=none
- 2026-06-29 11:06 UTC: digest changed; external=none
- 2026-06-29 15:53 UTC: digest changed; external=none
- 2026-06-29 20:03 UTC: digest changed; external=none
- 2026-06-30 03:57 UTC: digest changed; external=none
- 2026-06-30 09:43 UTC: digest changed; external=none
- 2026-06-30 14:26 UTC: digest changed; external=none
- 2026-06-30 20:03 UTC: digest changed; external=none
- 2026-07-01 04:12 UTC: digest changed; external=none
- 2026-07-01 09:54 UTC: digest changed; external=none
- 2026-07-01 14:43 UTC: digest changed; external=none
- 2026-07-01 20:00 UTC: digest changed; external=none
- 2026-07-02 03:52 UTC: digest changed; external=none
- 2026-07-02 09:17 UTC: digest changed; external=none
- 2026-07-02 14:09 UTC: digest changed; external=none
- 2026-07-02 19:35 UTC: digest changed; external=none
- 2026-07-03 03:34 UTC: digest changed; external=none
- 2026-07-03 09:23 UTC: digest changed; external=none
- 2026-07-03 14:13 UTC: digest changed; external=none
- 2026-07-03 19:27 UTC: digest changed; external=none
- 2026-07-04 03:27 UTC: digest changed; external=none
- 2026-07-04 08:41 UTC: digest changed; external=none
- 2026-07-04 13:40 UTC: digest changed; external=none
- 2026-07-04 19:18 UTC: digest changed; external=none
- 2026-07-05 03:44 UTC: digest changed; external=none
- 2026-07-05 08:56 UTC: digest changed; external=none
- 2026-07-05 13:46 UTC: digest changed; external=none
- 2026-07-05 19:22 UTC: digest changed; external=none
- 2026-07-06 03:53 UTC: digest changed; external=none
- 2026-07-06 10:43 UTC: digest changed; external=none
- 2026-07-06 15:39 UTC: digest changed; external=none
- 2026-07-06 20:02 UTC: digest changed; external=none
- 2026-07-07 03:42 UTC: digest changed; external=none
- 2026-07-07 09:48 UTC: digest changed; external=none
- 2026-07-07 14:43 UTC: digest changed; external=none
- 2026-07-07 19:59 UTC: digest changed; external=none
- 2026-07-08 02:56 UTC: digest changed; external=none
- 2026-07-08 08:34 UTC: digest changed; external=none
- 2026-07-08 14:21 UTC: digest changed; external=none
- 2026-07-08 19:37 UTC: digest changed; external=none
- 2026-07-09 03:35 UTC: digest changed; external=none
- 2026-07-09 09:45 UTC: digest changed; external=none
- 2026-07-09 15:16 UTC: digest changed; external=none
- 2026-07-09 19:50 UTC: digest changed; external=none
- 2026-07-10 03:37 UTC: digest changed; external=none
- 2026-07-10 09:40 UTC: digest changed; external=none
- 2026-07-10 14:34 UTC: digest changed; external=none
- 2026-07-10 19:37 UTC: digest changed; external=none
- 2026-07-11 02:52 UTC: digest changed; external=none
- 2026-07-11 08:01 UTC: digest changed; external=none
- 2026-07-11 13:26 UTC: digest changed; external=none
- 2026-07-11 19:09 UTC: digest changed; external=none
- 2026-07-12 03:17 UTC: digest changed; external=none
- 2026-07-12 08:22 UTC: digest changed; external=none
- 2026-07-12 13:26 UTC: digest changed; external=none
- 2026-07-12 19:09 UTC: digest changed; external=none
- 2026-07-13 03:20 UTC: digest changed; external=none
- 2026-07-13 09:33 UTC: digest changed; external=none
- 2026-07-13 14:41 UTC: digest changed; external=none
- 2026-07-13 19:26 UTC: digest changed; external=none
- 2026-07-14 02:44 UTC: digest changed; external=none
- 2026-07-14 08:12 UTC: digest changed; external=none
- 2026-07-14 13:51 UTC: digest changed; external=none
- 2026-07-14 19:23 UTC: digest changed; external=none
- 2026-07-15 02:42 UTC: digest changed; external=none
- 2026-07-15 08:19 UTC: digest changed; external=none
- 2026-07-15 13:49 UTC: digest changed; external=none
- 2026-07-15 19:16 UTC: digest changed; external=none
- 2026-07-16 02:49 UTC: digest changed; external=none
- 2026-07-16 08:19 UTC: digest changed; external=none
- 2026-07-16 14:00 UTC: digest changed; external=none
- 2026-07-16 19:16 UTC: digest changed; external=none
- 2026-07-17 02:52 UTC: digest changed; external=none
- 2026-07-17 08:14 UTC: digest changed; external=none
- 2026-07-17 13:45 UTC: digest changed; external=none
- 2026-07-17 19:15 UTC: digest changed; external=none
- 2026-07-18 02:44 UTC: digest changed; external=none
- 2026-07-18 07:56 UTC: digest changed; external=none
- 2026-07-18 13:22 UTC: digest changed; external=none
- 2026-07-18 19:09 UTC: digest changed; external=none
- 2026-07-19 03:13 UTC: digest changed; external=none
- 2026-07-19 08:23 UTC: digest changed; external=none
- 2026-07-19 13:23 UTC: digest changed; external=none
- 2026-07-19 19:10 UTC: digest changed; external=none
- 2026-07-20 03:28 UTC: digest changed; external=none
- 2026-07-20 09:20 UTC: digest changed; external=none
- 2026-07-20 14:12 UTC: digest changed; external=none
- 2026-07-20 19:46 UTC: digest changed; external=none
- 2026-07-21 02:54 UTC: digest changed; external=none
- 2026-07-21 08:33 UTC: digest changed; external=none
- 2026-07-21 13:59 UTC: digest changed; external=none
- 2026-07-21 19:35 UTC: digest changed; external=none
- 2026-07-22 02:52 UTC: digest changed; external=none
- 2026-07-22 08:33 UTC: digest changed; external=none
- 2026-07-22 14:02 UTC: digest changed; external=none
- 2026-07-22 19:25 UTC: digest changed; external=none
- 2026-07-23 03:13 UTC: digest changed; external=none
- 2026-07-23 08:34 UTC: digest changed; external=none
- 2026-07-23 14:08 UTC: digest changed; external=none
- 2026-07-23 19:22 UTC: digest changed; external=none
- 2026-07-24 02:53 UTC: digest changed; external=none
- 2026-07-24 08:31 UTC: digest changed; external=none
- 2026-07-24 13:50 UTC: digest changed; external=none
- 2026-07-24 19:28 UTC: digest changed; external=none
- 2026-07-25 02:52 UTC: digest changed; external=none
- 2026-07-25 08:10 UTC: digest changed; external=none
- 2026-07-25 13:40 UTC: digest changed; external=none
- 2026-07-25 19:11 UTC: digest changed; external=none
- 2026-07-26 03:18 UTC: digest changed; external=none
- 2026-07-26 08:30 UTC: digest changed; external=none
- 2026-07-26 13:35 UTC: digest changed; external=none
- 2026-07-26 19:15 UTC: digest changed; external=none
<!-- AUTOMATION-LOG:END -->

---

## Explicit non-goals

- Auto-updating top 10 in Loop-Engineering README every 12h
- Auto-merge external LoopBench PRs
- Bot-generated fake external submissions
- Slack/Discord webhook in v1 (GitHub pinned issue only)
