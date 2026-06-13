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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare two LSS loop specifications side by side",
    )
    parser.add_argument("spec_a", type=Path, help="First LSS YAML file")
    parser.add_argument("spec_b", type=Path, help="Second LSS YAML file")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

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
