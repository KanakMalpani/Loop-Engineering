# LoopBench — community platform sync pack

Push these files to [KanakMalpani/LoopBench](https://github.com/KanakMalpani/LoopBench) after review.

| Local path | Remote path |
|------------|-------------|
| `scripts/render_leaderboard.py` | `scripts/render_leaderboard.py` |
| `scripts/leaderboard_common.py` | `scripts/leaderboard_common.py` |
| `docs/index.html` | `docs/index.html` (GitHub Pages — [live site](https://kanakmalpani.github.io/LoopBench/)) |
| `leaderboard/ROW_SCHEMA.md` | `leaderboard/ROW_SCHEMA.md` |
| `.github/workflows/leaderboard-render.yml` | `.github/workflows/leaderboard-render.yml` |
| `.github/workflows/leaderboard-pr-hint.yml` | `.github/workflows/leaderboard-pr-hint.yml` |

Also merge [LoopBench-README.md](../LoopBench-README.md) (includes `<!-- LEADERBOARD:START -->` markers).

```bash
# Example (from Loop-Engineering root)
python scripts/push_github_file.py --repo LoopBench --path scripts/render_leaderboard.py \
  --file docs/ecosystem-sync/LoopBench/scripts/render_leaderboard.py --message "feat: live leaderboard render"
```

After push, run `leaderboard-render` workflow once to generate `leaderboard/LIVE.md`.

Tracker: [COMMUNITY_PLATFORM_STATUS.md](../../maintainer/COMMUNITY_PLATFORM_STATUS.md)
