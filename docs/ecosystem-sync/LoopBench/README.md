# LoopBench — community platform sync pack

**Source of truth:** edit here in Loop-Engineering, then merge to `main`. LoopBench pulls this pack automatically every hour via [`sync-platform-pack.yml`](.github/workflows/sync-platform-pack.yml) — no manual push required.

| Local path | Remote path |
|------------|-------------|
| `scripts/render_leaderboard.py` | `scripts/render_leaderboard.py` |
| `scripts/leaderboard_common.py` | `scripts/leaderboard_common.py` |
| `docs/**` | `docs/**` (GitHub Pages — [live site](https://kanakmalpani.github.io/LoopBench/)) |
| `leaderboard/README.md`, `ROW_SCHEMA.md` | same |
| `.github/workflows/*.yml` | same |

Also merge [LoopBench-README.md](../LoopBench-README.md) (includes `<!-- LEADERBOARD:START -->` markers) when README structure changes.

## Automatic pipeline (LoopBench remote)

| Trigger | Workflow | Result |
|---------|----------|--------|
| PR changes `entries.json` | `leaderboard-validate.yml` | Schema + render dry-run |
| PR changes `entries.json` | `leaderboard-pr-hint.yml` | Bot checklist comment |
| Merge to `main` (`entries.json`) | `leaderboard-render.yml` | Updates `LIVE.md`, README block, `docs/data/leaderboard.json` |
| After render / `docs/**` push | `pages.yml` | Deploys [GitHub Pages](https://kanakmalpani.github.io/LoopBench/) |
| Hourly + manual | `sync-platform-pack.yml` | Pulls this sync pack from Loop-Engineering `main` |
| Mon 08:00 UTC | `leaderboard-render.yml` | Weekly re-render |
| Every 6h (Loop-Engineering) | `ecosystem-digest.yml` | Updates pinned ops issue [#13](https://github.com/KanakMalpani/Loop-Engineering/issues/13) |

**Do not edit** `leaderboard/entries.json`, `LIVE.md`, or generated JSON on LoopBench without a PR — render workflow owns those outputs.

**Custom domain (optional):** Add `CNAME` in `docs/` and configure DNS → GitHub Pages settings on LoopBench repo.

Tracker: [COMMUNITY_PLATFORM_STATUS.md](../../maintainer/COMMUNITY_PLATFORM_STATUS.md)
