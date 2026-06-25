# Adoption automation — execution plan

**Purpose:** Stop manually checking adoption daily. Get **notified only when something changes**, auto-route real contributors, stay safe on **public** repos.

**Status:** Phase 13 Community Platform in progress · See [COMMUNITY_PLATFORM_STATUS.md](./COMMUNITY_PLATFORM_STATUS.md)

Related: [track_adoption_signals.py](../../scripts/track_adoption_signals.py) · [adoption-tracker/latest.json](../../docs/adoption-tracker/latest.json) · [LOOP_PLAYGROUND.md](../../contributions/LOOP_PLAYGROUND.md) · Issue [#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) · [PYPI_PUBLISH.md](./PYPI_PUBLISH.md)

---

## Executive summary

| Question | Answer |
|----------|--------|
| Can we automate everything? | **No** — external LoopBench / case study / repro need real humans |
| Can we automate *checking*? | **Yes** — diff + webhook + LoopBench poll + PR digest |
| Private repo needed? | **No** for core stack; use **GitHub Secrets** on public repos |
| Best first step | **Ops hub** (Slack/Discord or pinned issue) + adoption diff |
| Leaderboard + PRs without checking? | **Yes** — unified digest platform (see below) |

---

## Selected automations (best ROI)

### Included (implement in order)

| Phase | Automation | Replaces |
|-------|------------|----------|
| **1** | Adoption diff + notify | Opening `latest.md` daily |
| **2** | LoopBench leaderboard poll | Manually watching #4 / entries.json |
| **2b** | **Ecosystem digest hub** (leaderboard + cross-repo PRs) | Checking LoopBench PRs and leaderboard by hand |
| **3** | Pinned dashboard issue (bot-updated) | Checking 5 doc locations |
| **4** | PR checklist bot (LE + LoopBench) | Repasting EXTERNAL_SUBMISSIONS checklists |
| **5** | Monthly outreach refresh | Rewriting wave 10 copy |
| **6** | HF LoopNet upload on tag (optional) | Manual HF upload |

### Excluded (and why)

| Idea | Why not |
|------|---------|
| Bot fake external comments or LoopBench rows | Tracker excludes maintainer/bots; harms credibility |
| Daily auto-comments on #4 / #11 | Spam; community ignores |
| `pull_request_target` + secrets on fork PRs | **Security anti-pattern** on public repos |
| Auto-merge external LoopBench PRs | Scoreboard integrity needs human review |
| Fully automated Reddit/HN posting | Spam risk; keep human click |
| New private “ops” repo | Unnecessary — external channel or one pinned issue is enough |
| Daily bot comments on every LoopBench PR | Repo noise; batch into digest instead |

---

## Unified platform — no more checking leaderboard & PRs

**Problem:** Adoption work spans **Loop-Engineering** (issues #4/#7/#10) and **LoopBench** (leaderboard PRs). Checking GitHub repeatedly does not scale.

**Goal:** One place you look **only when something needs you** — without cluttering public repos.

### Design principle: keep repos clean

| Do | Don't |
|----|-------|
| 1–3 small workflow files per repo | Dozens of bots, logs, or markdown spam |
| One **pinned dashboard issue** OR external **#loop-ops** channel | Auto-comment on every PR in every repo |
| Snapshot JSON under `docs/adoption-tracker/` (already used) | Commit webhook payloads or raw API dumps |
| Notify on **change** only | Hourly “all clear” messages |
| Read-only polling of public leaderboard JSON | Store LoopBench credentials in repo |

---

### Option comparison (pick one primary hub)

| Option | Repo footprint | You check | Best for |
|--------|----------------|-----------|----------|
| **A. Slack / Discord ops channel** (recommended) | 1 workflow + 1 secret | Phone/desktop app when pinged | Hands-off; cross-repo |
| **B. Pinned GitHub dashboard issue** | 1 workflow, updates 1 issue | One bookmarked issue weekly | GitHub-only, no Slack |
| **C. GitHub Slack/Mobile app filters** | **Zero code** | Notification settings | Quick win today |
| **D. GitHub Project board** | Zero code; optional Action | One project URL | Visual PR queue |
| **E. Email digest via Actions** | 1 workflow | Inbox when diff | No third-party app |

**Recommended stack:** **C today** (5 min setup) + **A or B** when Phase 2b ships.

---

### Option A — External ops channel (cleanest repos)

Use **Slack** or **Discord** as the platform. Repos stay thin: workflows only POST JSON digests.

```
Loop-Engineering workflow ──┐
LoopBench workflow ─────────┼──► ADOPTION_WEBHOOK_URL ──► #loop-ops
Public leaderboard poll ────┘
```

**You receive messages only when:**

- LoopBench `entries.json` gains a new row or external submitter
- Open PR on LoopBench touches `leaderboard/entries.json`
- Open PR on Loop-Engineering touches `case-studies/` or mentions `loopbench`
- Adoption tracker signal flips green/yellow/red

**Setup (once):**

1. Create channel `#loop-ops` (private Slack workspace is fine — **not** a private GitHub repo)
2. Incoming webhook → secret `ADOPTION_WEBHOOK_URL` on **Loop-Engineering** (and optionally LoopBench)
3. Mute channel except @mentions; read only when mobile pings

**Security:** Webhook URL only in GitHub Secrets; never in git. Rotate if leaked.

---

### Option B — Pinned dashboard issue (GitHub-native platform)

Single issue acts as your **in-repo dashboard** without polluting history:

- Title: `🔭 Loop Engineering ops dashboard (auto-updated — do not comment)`
- Updated **only** on change (not daily noise)
- Sections: Leaderboard delta · Open adoption PRs · Tracker summary · Links

**Keep clean:**

- Bot **edits one issue body** instead of commenting on #4, #7, every PR
- Optional: one short comment on #4 **only** when external row appears (celebration)

Bookmark + pin this issue. You never visit LoopBench unless the dashboard says so.

---

### Option C — Zero-code GitHub notifications (do today)

No repo changes. Configure GitHub account notifications:

1. **Watch** [LoopBench](https://github.com/KanakMalpani/LoopBench) → Custom → **Pull requests** only
2. **Watch** Loop-Engineering → Custom → Issues + Discussions on #4, #7, #10
3. Install **GitHub Mobile** or **GitHub for Slack** → filter to `KanakMalpani/LoopBench` PRs

**Limitation:** Still noisy on busy days; no leaderboard JSON change detection (PR-only).

---

### Option D — GitHub Project “Adoption inbox”

Create a **Project** on your user/org:

| Column | Auto-rule |
|--------|-----------|
| Needs review | LoopBench PRs with label `leaderboard` or path filter |
| Community | LE issues #4, #7, #12 open |
| Done | Closed / merged |

Repos stay clean (Project lives on GitHub, not in file tree). You open **one board URL** instead of each repo.

---

### Option E — Cross-repo digest workflow (Phase 2b implementation)

**Single workflow in Loop-Engineering** (or thin mirror in LoopBench) — recommended build:

| File | Role |
|------|------|
| `scripts/ecosystem_digest.py` | Fetch leaderboard JSON + GitHub API open PRs (LE + LoopBench) |
| `.github/workflows/ecosystem-digest.yml` | Cron every 6h; on diff → webhook + update dashboard issue |

**GitHub API scope (secret `GH_PAT_READ` optional):**

- Fine-grained PAT: **Read** on `Loop-Engineering`, `LoopBench` only
- Used only in scheduled workflow on `main` — never in fork PRs

**Digest contents (one message):**

```text
Loop Ops Digest — 2026-06-25
• Leaderboard: +1 row (submitter: acme-labs) ← would flip #4
• LoopBench PR #12: leaderboard/entries.json (external fork)
• LE PR #45: case-studies/acme-codex-bridge.md
• Tracker: 8 green · 7 yellow (was 7 · 8)
→ Dashboard: https://github.com/.../issues/NNN
```

If nothing changed: **no webhook, no commit, no issue edit.**

---

### LoopBench repo — minimal mirror (keep both repos clean)

LoopBench should **not** duplicate Loop-Engineering logic. Add at most:

| File | Purpose |
|------|---------|
| `.github/workflows/leaderboard-pr-hint.yml` | On PR to `leaderboard/entries.json` → checklist comment (Phase 4) |
| Optional: forward webhook to same `ADOPTION_WEBHOOK_URL` | “PR opened on LoopBench” ping |

Leaderboard **content** changes are detected by **poll from Loop-Engineering** (public JSON) — no LoopBench secret required for reads.

---

### What you stop doing

| Before | After |
|--------|-------|
| Open LoopBench → leaderboard → entries.json | Digest tells you “+1 row” |
| Refresh LoopBench PR list | Digest lists adoption-related PRs only |
| Open adoption-tracker/latest.md daily | Ping only on status change |
| Check PyPI versions manually | Included in weekly dashboard issue |

---

### Private repo for the “platform”?

| Approach | Private GitHub repo? |
|----------|-------------------|
| Slack / Discord ops channel | **No** — workspace can be private; repos stay public |
| Pinned dashboard issue | **No** |
| GitHub Project | **No** |
| Self-hosted dashboard (Grafana, etc.) | Optional private VPS — **overkill** |
| Private repo mirroring webhooks/logs | **Avoid** — duplicates secrets surface |

**Verdict:** The “platform” is **outside the git tree** (Slack/Discord/notifications) or **one pinned issue** — not a new private repository.

---

## Private repository — do you need one?

### No — keep the ecosystem public

| Repository | Public? | Reason |
|------------|---------|--------|
| Loop-Engineering | Yes | Discipline home, PyPI source, onboarding |
| LoopBench | Yes | Public scoreboard must be auditable |
| loopnet | Yes | Open dataset |
| LoopGym / Loop-Core | Yes | Runtime + constitution |

### Where secrets live (public repo is OK)

Store only in **GitHub → Settings → Secrets and variables → Actions**:

| Secret | Used for | Scope |
|--------|----------|-------|
| `PYPI_API_TOKEN` | Publish workflows | PyPI upload (already in use) |
| `ADOPTION_WEBHOOK_URL` | Phase 1 notify | Slack/Discord incoming webhook |
| `HF_TOKEN` | Phase 6 (optional) | Hugging Face dataset write |

Secrets are **encrypted**, not visible in forks, and masked in logs.

### When a private repo might make sense (later, optional)

- Internal runbooks with credentials you refuse to use GitHub Secrets for
- Pre-release embargo (not applicable today)
- Commercial fork with proprietary integrations

**Recommendation:** **Zero private repos** for adoption automation.

---

## Security model (public repos)

```
Public read (no secrets)          GitHub Secrets (encrypted)
────────────────────────          ──────────────────────────
LoopBench entries.json     →      ADOPTION_WEBHOOK_URL
PyPI JSON API              →      PYPI_API_TOKEN (publish only)
track_adoption_signals.py  →      HF_TOKEN (optional)
```

### Rules

1. **Never** commit tokens, webhook URLs, or `.env` files.
2. **Notify workflows:** `contents: read` only; webhook via secret.
3. **Publish workflows:** API token auth only ([PYPI_PUBLISH.md](./PYPI_PUBLISH.md)); no `id-token: write` unless PyPI trusted publishing is configured.
4. **Fork PRs:** use `pull_request` event; run validation **without secrets**. Gate secret steps with:
   ```yaml
   if: github.event.pull_request.head.repo.full_name == github.repository
   ```
5. **Never use `pull_request_target`** to run untrusted code with secrets.
6. **Webhook URLs** are passwords — rotate if leaked.
7. **GITHUB_TOKEN** for same-repo issue comments is fine; use minimal permissions (`issues: write`).

### What attackers can do on public repos

| Risk | Mitigation |
|------|------------|
| Fork PR runs malicious CI | No secrets in fork PR workflows |
| Exfiltrate `PYPI_API_TOKEN` | Never pass secrets to fork PRs; publish only on `main` / release |
| Spam issues via workflow | Workflows only on `schedule` + `workflow_dispatch` + same-repo PRs |
| Fake leaderboard entry | Human review on LoopBench merge |

---

## Phase 1 — Notify on change (Week 1)

**Goal:** Email/Slack only when adoption signals **change**.

### Deliverables

| Artifact | Description |
|----------|-------------|
| `scripts/adoption_diff.py` | Diff new `latest.json` vs committed `docs/adoption-tracker/previous.json` |
| `.github/workflows/adoption-notify.yml` | Daily, after tracker runs |
| `docs/adoption-tracker/previous.json` | Baseline; bot updates when diff is clean |

### Behavior

1. Run `track_adoption_signals.py`
2. Compare to `previous.json`
3. If **any status changed** or **external LoopBench submitter appeared** → notify
4. If unchanged → exit 0 silently

### Notification options (pick one)

| Option | Setup | Effort |
|--------|-------|--------|
| **A. GitHub failure email** | Workflow `exit 1` on diff | Zero — uses GitHub default notifications |
| **B. Slack/Discord webhook** | Secret `ADOPTION_WEBHOOK_URL` | 5 min — create incoming webhook |
| **C. Both** | Fail job + webhook | Recommended |

### Your one-time setup

1. (Optional) Create Slack/Discord incoming webhook
2. Add repository secret `ADOPTION_WEBHOOK_URL`
3. Enable Actions on `main`

---

## Phase 2 — LoopBench watcher (Week 1–2)

**Goal:** Know within hours when Issue #4 should close.

### Deliverables

| Artifact | Description |
|----------|-------------|
| `scripts/check_loopbench_external.py` | Reuse `INTERNAL_SUBMITTER_MARKERS` from tracker |
| `.github/workflows/loopbench-watch.yml` | Cron every 6 hours |
| `docs/adoption-tracker/loopbench-snapshot.json` | Last known leaderboard hash |

### Behavior

- Fetch public `leaderboard/entries.json` (read-only)
- On new external submitter → comment on [#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) with name + link
- Optional: label `adoption-unlocked` when tracker would go green

**No LoopBench write token needed.**

---

## Phase 2b — Ecosystem digest hub (Week 1–2)

**Goal:** Never manually poll LoopBench leaderboard **or** PR lists.

### Deliverables

| Artifact | Repo | Description |
|----------|------|-------------|
| `scripts/ecosystem_digest.py` | Loop-Engineering | Leaderboard diff + open PRs (LE + LoopBench) via public API |
| `.github/workflows/ecosystem-digest.yml` | Loop-Engineering | Cron 6h; notify on change only |
| `docs/adoption-tracker/ecosystem-snapshot.json` | Loop-Engineering | Last digest hash (small, intentional) |
| `leaderboard-pr-hint.yml` | LoopBench (optional) | PR checklist only — no digest duplicate |

### Optional secret

| Secret | Scope | When |
|--------|-------|------|
| `GH_PAT_READ` | Fine-grained read: LE + LoopBench | Private PRs on free tier rare; public repos work with `GITHUB_TOKEN` for same repo only — PAT needed for **cross-repo** PR list |

For **public** repos, unauthenticated GitHub API works for open PRs (rate-limited). PAT recommended for reliability.

### Output routing (choose one)

1. `ADOPTION_WEBHOOK_URL` → Slack/Discord (**recommended**)
2. Update pinned dashboard issue body
3. Both

**No output if digest unchanged.**

---

## Phase 3 — Pinned dashboard issue (Week 2)

**Goal:** One URL to bookmark.

### Deliverables

| Artifact | Description |
|----------|-------------|
| `scripts/update_adoption_dashboard.py` | Create/update issue body via GitHub API |
| `.github/workflows/adoption-dashboard.yml` | Weekly cron |

### Issue template content

- Tracker summary (green/yellow/red)
- Links: #4, #7, #10, #11, #12
- PyPI versions (`le-loop-stack`, `le-loopctl`)
- “Changed this week” from adoption_diff
- Latest wave 10 CTA one-liner

**Manual once:** Pin the dashboard issue in GitHub UI.

---

## Phase 4 — PR checklist bot (Week 2–3)

### Loop-Engineering

| PR touches | Auto-comment |
|------------|--------------|
| `case-studies/` | [EXTERNAL_SUBMISSIONS.md](../../contributions/EXTERNAL_SUBMISSIONS.md) §3 checklist |
| Body contains `LB-CR-1` / `loopbench` | Link #4 + [BEAT_LB-CR-1.md](../../contributions/BEAT_LB-CR-1.md) |

### LoopBench (separate repo)

| PR touches | Auto-comment |
|------------|--------------|
| `leaderboard/entries.json` | Row schema checklist + `loopbench validate` hint |
| Always | “Maintainer review required” |

**Security:** `pull_request` only; no secrets; validation uses public SimEnv.

---

## Phase 5 — Outreach refresh (Week 3)

**Goal:** Never rewrite wave copy from scratch.

### Deliverables

- `.github/workflows/outreach-refresh.yml` — cron: 1st of month
- Append `adoption_wave10.py` output to dashboard issue or `docs/outreach/latest-wave.md`

**Not automated:** posting to Claude/Codex/Aider communities (human click avoids spam).

### Outside repo (15 min/month)

- Google Alert: `"agent loop benchmark"`, `"LangGraph evaluation loop"`
- On alert → paste pre-generated block from dashboard issue

---

## Phase 6 — HF LoopNet upload (optional, Week 4)

- Trigger: `workflow_dispatch` or tag `loopnet-v0.3-*`
- Secret: `HF_TOKEN` (write, scoped to your HF user)
- Steps: [HF-v0.3-preview.md](../loopnet/HF-v0.3-preview.md)

Dataset stays **public** on Hugging Face.

---

## Outside-the-repo ideas (no code, high leverage)

| Channel | Automation level | Notes |
|---------|------------------|-------|
| **Algora / bounties** on #4 | Semi | Attracts real external LoopBench PRs |
| **Google Alerts** | Full alert | You paste, not bot |
| **Discord/Slack `#loop-ops` channel** | Webhook from Phase 1 + 2b | **Primary ops platform** — repos stay clean |
| **PyPI download stats** | Weekly cron | Proxy metric, not #4 green |
| **Dev.to / newsletter** | Manual quarterly | Republish Golden Path when versions bump |

---

## Implementation checklist (Agent mode)

### Quick wins (no code — today)

- [ ] GitHub: Custom watch on LoopBench (PRs only)
- [ ] GitHub Mobile or GitHub for Slack with LoopBench filter
- [ ] Create GitHub Project “Adoption inbox” (optional)

### Build (Loop-Engineering)

- [ ] Phase 1: `adoption_diff.py` + `adoption-notify.yml`
- [ ] Phase 2: `check_loopbench_external.py` + `loopbench-watch.yml`
- [ ] **Phase 2b:** `ecosystem_digest.py` + `ecosystem-digest.yml`
- [ ] Phase 3: `update_adoption_dashboard.py` + weekly workflow
- [ ] Phase 4: `.github/workflows/pr-adoption-hints.yml` (LE)
- [ ] Phase 5: `outreach-refresh.yml`
- [ ] Phase 6: `hf-loopnet-upload.yml` (optional)

### Build (LoopBench — minimal)

- [ ] Phase 4: `leaderboard-pr-hint.yml` only

### Secrets & setup

- [ ] `ADOPTION_WEBHOOK_URL` (Slack/Discord — **ops platform**)
- [ ] `GH_PAT_READ` (optional, cross-repo PR digest)
- [ ] Pin dashboard issue (manual)
- [ ] Create `#loop-ops` channel (manual)

**Estimated build:** 2–3 days · **Your setup:** ~20 minutes (webhook + watches + pin issue)

---

## Success metrics

| Metric | Target |
|--------|--------|
| Manual tracker checks | 0/week unless notified |
| Manual LoopBench PR/leaderboard checks | 0/week unless digest pings |
| Time to learn #4 unlocked | < 1 hour |
| Bot comments per external PR | ≤ 1 checklist (no spam thread) |
| Secrets committed to git | 0 |
| External #4 green | Still requires 1 real contributor |

---

## What stays manual forever

- Approving LoopBench leaderboard merges
- Authentic first contact in external communities
- Answering contributor questions on #4 / #7 / #10

Automation **surfaces** work; it cannot **fabricate** adoption.
