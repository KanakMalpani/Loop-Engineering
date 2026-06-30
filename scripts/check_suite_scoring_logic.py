#!/usr/bin/env python3
"""Suite scoring logic smoke — no LoopBench sibling checkout or loopgym required."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _task_result(task_id: str, les: float) -> dict:
    return {
        "task_id": task_id,
        "aggregate": {"les_observed": les},
    }


def _test_recipes() -> None:
    from loopforge.mix import list_recipes, load_recipe

    recipes = list_recipes()
    assert len(recipes) >= 4, f"expected >=4 recipes, got {len(recipes)}"
    dev = load_recipe("dev-agent")
    assert dev.get("default_suite") == "suite-repair"
    swarm = load_recipe("swarm-review")
    assert swarm.get("default_suite") == "suite-agent"


def _test_sibling_loopbench() -> None:
    bench_root = ROOT.parent / "07-loopbench"
    if not bench_root.is_dir():
        return
    sys.path.insert(0, str(bench_root))
    from loopbench.suites import list_suites, load_suite, suite_task_ids
    from loopbench.runner import _suite_scores_from_results, build_submission

    suites = list_suites()
    assert len(suites) == 4, suites
    assert "suite-repair" in suites
    repair_ids = suite_task_ids("suite-repair")
    assert "LB-CR-1" in repair_ids
    assert len(repair_ids) == 5

    results = [_task_result(tid, 0.8 + i * 0.01) for i, tid in enumerate(repair_ids)]
    scores = _suite_scores_from_results(results)
    assert "suite-repair" in scores
    assert scores["suite-repair"]["les_observed"] > 0

    suite = load_suite("suite-repair")
    assert suite.get("label")


def main() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        _test_recipes()
        print("OK: suite recipes")
        _test_sibling_loopbench()
        print("OK: suite_scoring_logic")
        return 0
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
