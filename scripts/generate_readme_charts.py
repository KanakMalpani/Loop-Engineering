#!/usr/bin/env python3
"""Generate PNG README charts for the Loop Engineering ecosystem."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
REPOS = Path(__file__).resolve().parents[2]

BG = "#111113"
PANEL = "#1c1c1e"
GRID = "#27272a"
TEXT = "#f4f4f5"
MUTED = "#a1a1aa"
COLORS = {
    "baseline": "#71717a",
    "orange": "#f97316",
    "green": "#22c55e",
    "purple": "#a855f7",
    "blue": "#38bdf8",
    "red": "#ef4444",
}


def _style_ax(ax: plt.Axes) -> None:
    ax.set_facecolor(BG)
    ax.figure.patch.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(TEXT)


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160, facecolor=BG, bbox_inches="tight", pad_inches=0.35)
    plt.close(fig)
    print(f"Wrote {path}")


def chart_token_efficiency(out: Path) -> None:
    labels = [
        "separate YAML files",
        "loop combine (flat)",
        "loopctl spec minify",
        "loop quick --max-tokens 1200",
    ]
    values = [100, 84, 43, 34]
    tokens = ["3,255 tok", "2,750 tok", "1,414 tok", "1,101 tok"]
    colors = [COLORS["baseline"], COLORS["orange"], COLORS["green"], COLORS["purple"]]

    fig, ax = plt.subplots(figsize=(10, 4.2))
    _style_ax(ax)
    y = range(len(labels))
    bars = ax.barh(list(y), values, color=colors, height=0.62, edgecolor="none")
    ax.set_yticks(list(y), labels, fontsize=10, color=MUTED)
    ax.set_xlim(0, 110)
    ax.set_xlabel("% of baseline (lower is leaner)", fontsize=10)
    ax.set_title(
        "Token use vs 3 separate library specs (baseline = 100%)",
        fontsize=13,
        fontweight="bold",
        pad=12,
        color=TEXT,
    )
    ax.axvline(100, color=GRID, linestyle="--", linewidth=1, alpha=0.8)
    for bar, val, tok in zip(bars, values, tokens):
        ax.text(
            bar.get_width() + 1.5,
            bar.get_y() + bar.get_height() / 2,
            f"{tok} · {val}%",
            va="center",
            ha="left",
            fontsize=9,
            color=TEXT,
        )
    legend = [
        mpatches.Patch(color=COLORS["baseline"], label="baseline"),
        mpatches.Patch(color=COLORS["orange"], label="flat combine"),
        mpatches.Patch(color=COLORS["green"], label="LSS-min JSON"),
        mpatches.Patch(color=COLORS["purple"], label="combine + budget"),
    ]
    ax.legend(handles=legend, loc="upper right", frameon=False, labelcolor=MUTED, fontsize=8)
    fig.text(0.02, 0.02, "research-agent + coding-agent + autonomous-debugger · le-loopforge 0.5.0", color=MUTED, fontsize=8)
    _save(fig, out)


def chart_spec_layer(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 3.8))
    _style_ax(ax)
    ax.axis("off")
    ax.set_title("One spec layer · zero schema drift", fontsize=13, fontweight="bold", color=TEXT, pad=10)
    blocks = [
        ("LSS 1.1", COLORS["orange"], "workers · evaluators · composition"),
        ("LES 1.0", COLORS["green"], "8 scoring dimensions"),
        ("Taxonomy", COLORS["purple"], "fail.* codes · loop IDs"),
        ("Tools", COLORS["blue"], "validate_lss · les_calculator"),
    ]
    xs = [0.06, 0.28, 0.50, 0.72]
    for x, (title, color, sub) in zip(xs, blocks):
        rect = mpatches.FancyBboxPatch(
            (x, 0.25), 0.2, 0.45, boxstyle="round,pad=0.02,rounding_size=0.02",
            facecolor=PANEL, edgecolor=GRID, linewidth=1.2, transform=ax.transAxes,
        )
        ax.add_patch(rect)
        ax.text(x + 0.1, 0.58, title, ha="center", va="center", fontsize=11, fontweight="bold", color=color, transform=ax.transAxes)
        ax.text(x + 0.1, 0.42, sub, ha="center", va="center", fontsize=8, color=MUTED, transform=ax.transAxes)
        bar = mpatches.Rectangle((x + 0.04, 0.30), 0.12, 0.04, facecolor=color, alpha=0.85, transform=ax.transAxes)
        ax.add_patch(bar)
    fig.text(0.5, 0.08, "Pin once · LoopGym, LoopBench, and LoopNet import the same contracts", ha="center", color=MUTED, fontsize=9)
    _save(fig, out)


def chart_corpus_overview(out: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), gridspec_kw={"width_ratios": [1.2, 1]})
    for ax in axes:
        _style_ax(ax)

    # outcome pie-like bar
    ax = axes[0]
    ax.set_title("LoopNet v0.2 outcomes", fontsize=11, fontweight="bold", color=TEXT)
    ax.barh([0], [60], color=COLORS["green"], height=0.5, label="success 327")
    ax.barh([0], [40], left=[60], color=COLORS["red"], height=0.5, label="failure 218")
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel("% of 545 records", fontsize=9)
    ax.legend(frameon=False, labelcolor=MUTED, fontsize=8, loc="upper right")

    # provenance
    ax = axes[1]
    ax.set_title("Provenance", fontsize=11, fontweight="bold", color=TEXT)
    prov_labels = ["seed (500)", "SimEnv captured (45)"]
    prov_vals = [500, 45]
    ax.barh(prov_labels, prov_vals, color=[COLORS["baseline"], COLORS["blue"]], height=0.55)
    ax.set_xlabel("records", fontsize=9)
    for i, v in enumerate(prov_vals):
        ax.text(v + 8, i, str(v), va="center", color=TEXT, fontsize=9)
    fig.suptitle("545 structured trajectories · 40% labeled failures", fontsize=12, fontweight="bold", color=TEXT, y=1.02)
    _save(fig, out)


def chart_runtime_backends(out: Path) -> None:
    labels = ["SimEnv", "ReplayEnv", "PerturbedSim", "LiveEnv"]
    costs = [0, 0, 0, 100]  # relative
    notes = ["$0 · CI-safe", "$0 · LoopNet replay", "RAG/HITL/safety", "real LLM spend"]
    colors = [COLORS["green"], COLORS["blue"], COLORS["purple"], COLORS["orange"]]

    fig, ax = plt.subplots(figsize=(10, 3.8))
    _style_ax(ax)
    display = [8, 5, 8, 100]
    y = range(len(labels))
    ax.barh(list(y), display, color=colors, height=0.58)
    ax.set_yticks(list(y), labels, fontsize=10, color=MUTED)
    ax.set_xlim(0, 115)
    ax.set_xlabel("relative run cost (lower is cheaper)", fontsize=10)
    ax.set_title("LoopGym backends · one API", fontsize=13, fontweight="bold", color=TEXT, pad=10)
    for i, (d, note) in enumerate(zip(display, notes)):
        ax.text(d + 2, i, note, va="center", color=TEXT, fontsize=9)
    _save(fig, out)


def chart_suite_coverage(out: Path) -> None:
    suites = ["suite-repair", "suite-agent", "suite-knowledge", "suite-rigor"]
    tasks = [5, 5, 4, 5]
    colors = [COLORS["orange"], COLORS["green"], COLORS["blue"], COLORS["purple"]]

    fig, ax = plt.subplots(figsize=(10, 3.8))
    _style_ax(ax)
    y = range(len(suites))
    ax.barh(list(y), tasks, color=colors, height=0.58)
    ax.set_yticks(list(y), suites, fontsize=10, color=MUTED)
    ax.set_xlim(0, 6.5)
    ax.set_xlabel("micro-tasks per suite", fontsize=10)
    ax.set_title("19 micro-tasks · 4 suites · 1 generalist rank", fontsize=13, fontweight="bold", color=TEXT, pad=10)
    for i, n in enumerate(tasks):
        ax.text(n + 0.08, i, f"{n} tasks", va="center", color=TEXT, fontsize=9)
    _save(fig, out)


def chart_trace_footprint(out: Path) -> None:
    labels = ["full chat transcript", "LTF loop trace (loopotel)", "OTel loop.* export"]
    sizes = [100, 30, 28]
    colors = [COLORS["baseline"], COLORS["green"], COLORS["blue"]]

    fig, ax = plt.subplots(figsize=(10, 3.6))
    _style_ax(ax)
    y = range(len(labels))
    ax.barh(list(y), sizes, color=colors, height=0.58)
    ax.set_yticks(list(y), labels, fontsize=10, color=MUTED)
    ax.set_xlim(0, 115)
    ax.set_xlabel("relative storage (lower is leaner)", fontsize=10)
    ax.set_title("Structured traces vs raw chat logs", fontsize=13, fontweight="bold", color=TEXT, pad=10)
    notes = ["100%", "~30%", "Grafana-ready"]
    for i, (s, note) in enumerate(zip(sizes, notes)):
        ax.text(s + 2, i, note, va="center", color=TEXT, fontsize=9)
    _save(fig, out)


CHARTS = {
    REPOS / "01-loop-engineering" / "assets" / "token-efficiency.png": chart_token_efficiency,
    REPOS / "02-loop-core-engineering" / "assets" / "spec-layer.png": chart_spec_layer,
    REPOS / "05-loopnet" / "assets" / "corpus-overview.png": chart_corpus_overview,
    REPOS / "06-loopgym" / "assets" / "runtime-backends.png": chart_runtime_backends,
    REPOS / "07-loopbench" / "assets" / "suite-coverage.png": chart_suite_coverage,
    REPOS / "08-loop-observability" / "assets" / "trace-footprint.png": chart_trace_footprint,
}


def main() -> int:
    try:
        import matplotlib  # noqa: F401
    except ImportError:
        raise SystemExit("pip install matplotlib")

    for path, fn in CHARTS.items():
        fn(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
