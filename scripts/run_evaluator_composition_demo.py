#!/usr/bin/env python3
"""LE-OP-04 v0.2: evaluator merge policies + double-counting detection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks" / "evaluator-composition" / "results-v0.2.json"

CASES = [
    {"id": "good", "syntax": 0.95, "tests": 0.92, "rubric": 0.88},
    {"id": "syntax_fail", "syntax": 0.40, "tests": 0.90, "rubric": 0.85},
    {"id": "test_fail", "syntax": 0.95, "tests": 0.55, "rubric": 0.82},
    {"id": "rubric_only_pass", "syntax": 0.95, "tests": 0.72, "rubric": 0.91},
    {"id": "double_count_trap", "syntax": 0.88, "tests": 0.78, "rubric": 0.86},
    {"id": "all_marginal", "syntax": 0.81, "tests": 0.79, "rubric": 0.80},
    {"id": "double_count_severe", "syntax": 0.85, "tests": 0.70, "rubric": 0.92},
    {"id": "syntax_marginal_behavior_fail", "syntax": 0.76, "tests": 0.88, "rubric": 0.87},
]

THRESHOLD = 0.80


def naive_and(scores: dict[str, float]) -> tuple[float, bool]:
    composite = min(scores.values())
    return composite, composite >= THRESHOLD


def double_count_avg(scores: dict[str, float]) -> tuple[float, bool]:
    w_syntax, w_tests, w_rubric = 0.2, 0.45, 0.45
    composite = w_syntax * scores["syntax"] + w_tests * scores["tests"] + w_rubric * scores["rubric"]
    return composite, composite >= THRESHOLD


def rubric_product(scores: dict[str, float]) -> tuple[float, bool]:
    behavioral = scores["tests"]
    synthesis = scores["rubric"]
    composite = (scores["syntax"] ** 0.5) * (behavioral ** 0.25) * (synthesis ** 0.25)
    return composite, composite >= THRESHOLD


def partition_merge(scores: dict[str, float]) -> tuple[float, bool]:
    if scores["syntax"] < 0.75:
        return scores["syntax"], False
    behavioral = scores["tests"]
    synthesis = scores["rubric"] * 0.5 + scores["tests"] * 0.5
    composite = 0.5 * behavioral + 0.5 * synthesis
    return composite, composite >= THRESHOLD


def library_composed_gate(scores: dict[str, float]) -> tuple[float, bool]:
    """Mirrors composite_gate in loop-library/compositions — syntax gate then AND branches."""
    if scores["syntax"] < 0.75:
        return scores["syntax"], False
    branch_min = min(scores["tests"], scores["rubric"])
    composite = 0.6 * branch_min + 0.4 * scores["syntax"]
    return composite, composite >= THRESHOLD


POLICIES = {
    "naive_and": naive_and,
    "double_count_avg": double_count_avg,
    "rubric_product": rubric_product,
    "partition_merge": partition_merge,
    "library_composed_gate": library_composed_gate,
}


def run_demo() -> dict:
    gold_should_pass = {"good", "rubric_only_pass"}
    results = {}
    for name, fn in POLICIES.items():
        false_pass = 0
        false_continue = 0
        rows = []
        for case in CASES:
            scores = {k: case[k] for k in ("syntax", "tests", "rubric")}
            composite, passed = fn(scores)
            should_pass = case["id"] in gold_should_pass
            if passed and not should_pass:
                false_pass += 1
            if not passed and should_pass:
                false_continue += 1
            rows.append(
                {
                    "case_id": case["id"],
                    "composite": round(composite, 4),
                    "passed": passed,
                    "should_pass": should_pass,
                }
            )
        results[name] = {
            "false_pass_count": false_pass,
            "false_continue_count": false_continue,
            "cases": rows,
        }
    baseline_fp = results["double_count_avg"]["false_pass_count"]
    partition_fp = results["partition_merge"]["false_pass_count"]
    library_fp = results["library_composed_gate"]["false_pass_count"]
    return {
        "benchmark_id": "evaluator-composition-v0.2",
        "threshold": THRESHOLD,
        "n_cases": len(CASES),
        "policies": results,
        "summary": {
            "false_pass_reduction_vs_double_count": baseline_fp - partition_fp,
            "partition_merge_beats_double_count": partition_fp < baseline_fp,
            "library_composed_beats_double_count": library_fp < baseline_fp,
            "double_count_false_pass_baseline": baseline_fp,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="LE-OP-04 evaluator composition demo")
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = run_demo()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Wrote {args.output}")
        for name, data in report["policies"].items():
            print(f"  {name}: false_pass={data['false_pass_count']} false_continue={data['false_continue_count']}")
        print(f"  partition vs double_count FP delta: {report['summary']['false_pass_reduction_vs_double_count']}")

    ok = report["summary"]["partition_merge_beats_double_count"] and report["summary"]["library_composed_beats_double_count"]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
