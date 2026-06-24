#!/usr/bin/env python3
"""Compare two LSS loop specifications side by side."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from les_calculator import compute_les, LES_WEIGHTS, CATEGORY_LABELS  # noqa: E402
from loop_complexity_analyzer import analyze_complexity, _max_iterations  # noqa: E402


def load_spec(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def diff_lists(a: list, b: list, key: str = "id") -> dict[str, list[str]]:
    a_ids = {item.get(key, str(i)): item for i, item in enumerate(a)}
    b_ids = {item.get(key, str(i)): item for i, item in enumerate(b)}
    only_a = sorted(set(a_ids) - set(b_ids))
    only_b = sorted(set(b_ids) - set(a_ids))
    common = sorted(set(a_ids) & set(b_ids))
    changed = [cid for cid in common if a_ids[cid] != b_ids[cid]]
    return {"only_in_a": only_a, "only_in_b": only_b, "changed": changed}


def _summary(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "loop_name": spec.get("loop_name"),
        "version": spec.get("version"),
        "taxonomy_level": spec.get("taxonomy_level"),
        "objective": (spec.get("objective") or "")[:80],
        "workers": len(spec.get("workers") or []),
        "evaluators": len(spec.get("evaluators") or []),
        "safety_constraints": len(spec.get("safety_constraints") or []),
        "max_iterations": _max_iterations(spec),
    }


def compare_specs(spec_a: dict[str, Any], spec_b: dict[str, Any]) -> dict[str, Any]:
    les_a, cat_a = compute_les(spec_a)
    les_b, cat_b = compute_les(spec_b)
    complexity_a = analyze_complexity(spec_a)
    complexity_b = analyze_complexity(spec_b)

    return {
        "a": {
            "summary": _summary(spec_a),
            "les": les_a,
            "categories": cat_a,
            "complexity": complexity_a,
        },
        "b": {
            "summary": _summary(spec_b),
            "les": les_b,
            "categories": cat_b,
            "complexity": complexity_b,
        },
        "delta": {
            "les": round(les_a - les_b, 1),
            "categories": {cat: round(cat_a[cat] - cat_b[cat], 3) for cat in LES_WEIGHTS},
            "expected_tokens": complexity_b["expected_total_tokens"] - complexity_a["expected_total_tokens"],
            "taxonomy_level": (spec_b.get("taxonomy_level") or 0) - (spec_a.get("taxonomy_level") or 0),
        },
        "workers_diff": diff_lists(spec_a.get("workers") or [], spec_b.get("workers") or []),
        "evaluators_diff": diff_lists(spec_a.get("evaluators") or [], spec_b.get("evaluators") or []),
        "objective_changed": spec_a.get("objective") != spec_b.get("objective"),
    }


def format_table(comparison: dict[str, Any], path_a: str, path_b: str) -> str:
    sa = comparison["a"]["summary"]
    sb = comparison["b"]["summary"]
    lines = [
        "Loop Specification Comparison",
        "=" * 60,
        f"{'Field':<28} {'A':<14} {'B':<14} Diff",
        "-" * 60,
        f"{'File':<28} {Path(path_a).name:<14} {Path(path_b).name:<14}",
        f"{'loop_name':<28} {str(sa['loop_name']):<14} {str(sb['loop_name']):<14}",
        f"{'version':<28} {str(sa['version']):<14} {str(sb['version']):<14}",
        f"{'taxonomy_level':<28} {str(sa['taxonomy_level']):<14} {str(sb['taxonomy_level']):<14} {comparison['delta']['taxonomy_level']:+d}",
        f"{'workers':<28} {str(sa['workers']):<14} {str(sb['workers']):<14}",
        f"{'evaluators':<28} {str(sa['evaluators']):<14} {str(sb['evaluators']):<14}",
        f"{'max_iterations':<28} {str(sa['max_iterations']):<14} {str(sb['max_iterations']):<14}",
        "",
        "LES Comparison:",
        f"  A: {comparison['a']['les']:.1f}",
        f"  B: {comparison['b']['les']:.1f}",
        f"  Diff: {comparison['delta']['les']:+.1f}",
        "",
        "Token estimate (expected total):",
        f"  A: {comparison['a']['complexity']['expected_total_tokens']:,}",
        f"  B: {comparison['b']['complexity']['expected_total_tokens']:,}",
        f"  Diff: {comparison['delta']['expected_tokens']:+,}",
        "",
        "Category deltas (A - B):",
    ]
    for cat in LES_WEIGHTS:
        d = comparison["delta"]["categories"][cat]
        sign = "+" if d >= 0 else ""
        lines.append(f"  {CATEGORY_LABELS[cat]:14s}  {sign}{d:.3f}")
    return "\n".join(lines)


def _extract_aggregate(data: dict[str, Any]) -> dict[str, Any]:
    results = data.get("results")
    if isinstance(results, list) and results:
        first = results[0]
        if isinstance(first, dict):
            return first.get("aggregate") or {}
    if isinstance(results, dict):
        return results.get("aggregate") or {}
    return data.get("aggregate") or {}


def pareto_report(baselines: list[tuple[str, dict[str, Any]]], dim_x: str, dim_y: str) -> dict[str, Any]:
    points = []
    for label, data in baselines:
        agg = _extract_aggregate(data)
        cats = agg.get("categories") or {}
        les_struct = data.get("results", {}).get("les_structural") if isinstance(data.get("results"), dict) else {}
        composite = agg.get("les_observed")
        if composite is None and isinstance(les_struct, dict):
            composite = les_struct.get("composite")
        points.append(
            {
                "label": label,
                "x": cats.get(dim_x, 0.0),
                "y": cats.get(dim_y, 0.0),
                "les_observed": composite,
                "les_display": agg.get("les_display"),
            }
        )
    # Non-dominated (maximize both)
    frontier = []
    for i, p in enumerate(points):
        dominated = False
        for j, q in enumerate(points):
            if i != j and q["x"] >= p["x"] and q["y"] >= p["y"] and (q["x"] > p["x"] or q["y"] > p["y"]):
                dominated = True
                break
        if not dominated:
            frontier.append(p["label"])
    return {
        "dimensions": {"x": dim_x, "y": dim_y},
        "points": points,
        "pareto_frontier": frontier,
    }


def load_baseline_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare two LSS loop specifications side by side",
    )
    parser.add_argument("spec_a", type=Path, nargs="?", help="First LSS YAML file")
    parser.add_argument("spec_b", type=Path, nargs="?", help="Second LSS YAML file")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "--pareto",
        action="store_true",
        help="Pareto report from baseline JSON files (provide 2+ --baseline paths)",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        action="append",
        help="Baseline JSON for --pareto mode",
    )
    parser.add_argument("--dim-x", default="speed", help="LES category for X axis (pareto)")
    parser.add_argument("--dim-y", default="effectiveness", help="LES category for Y axis (pareto)")
    parser.add_argument(
        "--pareto-output",
        type=Path,
        default=Path("benchmarks/results/les-pareto-baselines-v0.1.json"),
    )
    args = parser.parse_args()

    if args.pareto:
        if not args.baseline or len(args.baseline) < 2:
            parser.error("--pareto requires at least two --baseline paths")
        baselines = [(p.stem, load_baseline_json(p)) for p in args.baseline]
        report = pareto_report(baselines, args.dim_x, args.dim_y)
        report["generated_from"] = [str(p) for p in args.baseline]
        args.pareto_output.parent.mkdir(parents=True, exist_ok=True)
        args.pareto_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Pareto ({args.dim_x} vs {args.dim_y}): wrote {args.pareto_output}")
            for p in report["points"]:
                mark = "*" if p["label"] in report["pareto_frontier"] else " "
                print(f"  {mark} {p['label']:20s} x={p['x']:.2f} y={p['y']:.2f} LES={p.get('les_display')}")
        return 0

    if not args.spec_a or not args.spec_b:
        parser.error("Provide spec_a and spec_b, or use --pareto")

    for p in (args.spec_a, args.spec_b):
        if not p.exists():
            print(f"Error: file not found: {p}", file=sys.stderr)
            return 2

    try:
        spec_a = load_spec(args.spec_a)
        spec_b = load_spec(args.spec_b)
        comparison = compare_specs(spec_a, spec_b)
    except (yaml.YAMLError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        comparison["paths"] = {"a": str(args.spec_a), "b": str(args.spec_b)}
        print(json.dumps(comparison, indent=2))
    else:
        print(format_table(comparison, str(args.spec_a), str(args.spec_b)))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
