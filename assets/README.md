# README chart assets

PNG charts in this folder (and sibling repos) are **generated** — do not edit by hand.

## Regenerate

From the Loop-Engineering repo root:

```bash
pip install matplotlib
python scripts/generate_readme_charts.py
```

This writes:

| Output | Repo |
| :--- | :--- |
| `benefits-overview.png`, `token-efficiency.png` | Loop-Engineering |
| `spec-layer.png` | Loop-Core-Engineering |
| `corpus-overview.png` | loopnet |
| `runtime-backends.png` | LoopGym |
| `suite-coverage.png` | LoopBench |
| `trace-footprint.png` | loop-observability |

Commit PNGs together with any script or README changes so GitHub always renders charts that match reviewed source.
