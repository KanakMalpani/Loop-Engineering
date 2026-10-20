#!/usr/bin/env python3
"""Offline deterministic demo steps: spec, trace, benchmark.

No model calls. SimEnv uses MockLLM. Benchmark numbers come from the
sandbox evaluator and a read-only stub results file.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "packages/loopgym/loopgym/envs/loopbench/code-repair-v1/spec.yaml"
FIXTURES = ROOT / "packages/loopbench/fixtures"
STUB_RESULTS = ROOT / "benchmarks/loopbench-validity/results/stub-fixed-all-10.json"
TABLE_LOOPS = ("bad-1-no-feedback", "bad-2-no-tests", "good-1-fast")
PENDING = "pending fixed benchmark acceptance"

# Bind fixtures before loopgym imports the evaluator (path is fixed at import).
os.environ["LOOPBENCH_FIXTURES"] = str(FIXTURES)


def spec_step() -> None:
    """Compile the code-repair LSS spec and print a short summary."""
    from loopgym.runtime.compiler import compile_lss
    from loopgym.runtime.loop_runtime import load_lss_spec

    print("=== 1. SPEC ===")
    print(f"spec: {SPEC_PATH.relative_to(ROOT)}")
    spec = load_lss_spec(SPEC_PATH)
    graph = compile_lss(spec)
    objective = " ".join(str(spec.get("objective", "")).split())
    print(f"compile_lss: ok  loop_name={graph.loop_name}  version={graph.version}")
    print(f"objective: {objective}")
    print(f"workers ({len(graph.workers)}):")
    for worker in graph.workers:
        print(f"  - {worker.id}: {worker.role}")
    print(f"evaluators ({len(graph.evaluators)}):")
    for evaluator in graph.evaluators:
        print(f"  - {evaluator.id}: {evaluator.type}")
    channels = spec.get("feedback_channels") or []
    print(f"feedback channels ({len(channels)}):")
    for channel in channels:
        print(
            f"  - {channel.get('id')}: {channel.get('source')} -> {channel.get('destination')}"
            f"  fields={channel.get('fields')}"
        )
    term = spec.get("termination_conditions") or {}
    success = term.get("success") or []
    failure = term.get("failure") or []
    print("termination:")
    print(f"  compiled quality_threshold: {graph.quality_threshold}")
    print(f"  compiled max_iterations: {graph.max_iterations}")
    for rule in success:
        print(f"  success: {rule.get('metric')} {rule.get('operator')} {rule.get('value')}")
    for rule in failure:
        print(f"  failure: {rule.get('type')} value={rule.get('value', '')} action={rule.get('action', '')}")
    limits = spec.get("cost_limits") or {}
    on_exceed = limits.get("on_exceed") or {}
    print("cost limits:")
    print(f"  per_iteration_usd: {limits.get('per_iteration_usd')}")
    print(f"  cumulative_usd: {limits.get('cumulative_usd')}")
    print(f"  on_exceed: {on_exceed.get('action')}")
    print()


def trace_step(outdir: str | Path) -> dict[str, Any]:
    """Run one MockLLM SimEnv episode and write an LTF trace."""
    import loopgym as lg
    from loopotel.integrations.loopgym import run_traced_episode
    from loopotel.validate import validate_trace

    print("=== 2. TRACE ===")
    print("backend: SimEnv + MockLLM (no model call)")
    env = lg.make("loopbench/code-repair-v1", spec_path=str(SPEC_PATH), seed=0)
    result, trace = run_traced_episode(env, task_id="cr-001", seed=0, enabled=True)
    valid, errors = validate_trace(trace)
    if not valid:
        raise RuntimeError("LTF validation failed: " + "; ".join(errors))

    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    trace_path = out / "trace.json"
    trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")

    print(
        f"episode: task=cr-001 seed=0 success={result['success']}"
        f" quality_score={result['quality_score']}"
        f" termination={result['termination_reason']}"
    )
    print(f"wrote: {trace_path}")
    print("OpenTelemetry span tree (loopotel LTF spans):")
    print(_span_tree(trace))
    print(f"spec_pins: {json.dumps(trace.get('spec_pins'), sort_keys=True)}")
    _print_shown_and_planned(trace)
    print()
    return trace


def bench_step() -> None:
    """Score reference vs empty patches, then print a stub LoopBench table."""
    import loopgym.evaluators.sandbox_tests as sandbox

    sandbox.FIXTURES_ROOT = FIXTURES
    print("=== 3. BENCHMARK ===")
    print("evaluator: loopgym.evaluators.sandbox_tests.test_pass_rate")
    print(f"fixtures: {FIXTURES.relative_to(ROOT)}")
    print("reference patches: packages/loopbench/fixtures/_reference")
    for fixture_id in ("cr-001", "cr-002", "cr-003"):
        fixture = sandbox.get_fixture(fixture_id)
        if fixture is None:
            raise RuntimeError(f"missing fixture {fixture_id}")
        reference = (FIXTURES / "_reference" / f"{fixture_id}.py").read_text(encoding="utf-8")
        reference_score = sandbox.test_pass_rate(fixture, f"```python\n{reference}```")["test_pass_rate"]
        empty_score = sandbox.test_pass_rate(fixture, "")["test_pass_rate"]
        if reference_score != 1.0 or empty_score != 0.0:
            raise RuntimeError(
                f"{fixture_id} stub check failed: reference={reference_score} empty={empty_score}"
            )
        print(
            f"  {fixture_id}: reference_patch={reference_score:.1f}"
            f" empty_output={empty_score:.1f}"
            "  (evaluator stub check)"
        )
    print("evaluator stub checks: pass")

    payload = json.loads(STUB_RESULTS.read_text(encoding="utf-8"))
    by_name = {row["loop"]: row for row in payload.get("loops") or []}
    missing = [name for name in TABLE_LOOPS if name not in by_name]
    if missing:
        raise RuntimeError(f"stub results missing loops: {missing}")

    print()
    print(f"LoopBench table (read-only {STUB_RESULTS.relative_to(ROOT)})")
    print(f"task={payload.get('task')} seeds={payload.get('seeds')}")
    header = f"{'loop':<22} {'fixed_reply':>12} {'feedback_stub':>14}  label"
    print(header)
    print("-" * len(header))
    for name in TABLE_LOOPS:
        row = by_name[name]
        fixed = float(row["fixed_reply"]["score"])
        feedback = float(row["feedback_stub"]["score"])
        print(f"{name:<22} {fixed:12.4f} {feedback:14.4f}  {PENDING}")
    print()
    print(
        "Every score in the table above is pending fixed benchmark acceptance."
        " No real-model acceptance has completed."
    )
    print("See benchmarks/loopbench-validity/DEVIATION.md.")
    print()


def _span_tree(trace: dict[str, Any]) -> str:
    spans = trace.get("spans") or []
    children: dict[Any, list[dict[str, Any]]] = {}
    for span in spans:
        children.setdefault(span.get("parent_span_id"), []).append(span)
    lines: list[str] = []

    def walk(parent: Any, indent: str) -> None:
        for span in children.get(parent, []):
            attrs = span.get("attributes") or {}
            bits = []
            for key in (
                "loop.iteration",
                "loop.goal_score",
                "loop.goal_target",
                "loop.cost_usd",
                "loop.les.cumulative_normalized",
                "loop.les.effectiveness",
                "loop.worker.id",
                "loop.evaluator.id",
                "loop.outcome",
                "loop.termination_reason",
            ):
                if key in attrs:
                    bits.append(f"{key}={attrs[key]}")
            suffix = ("  " + " ".join(bits)) if bits else ""
            lines.append(f"{indent}{span.get('name')}{suffix}")
            for event in span.get("events") or []:
                lines.append(f"{indent}  event {event.get('name')}")
            walk(span.get("span_id"), indent + "  ")

    walk(None, "")
    return "\n".join(lines)


def _has_attr(trace: dict[str, Any], key: str) -> bool:
    return any(key in (span.get("attributes") or {}) for span in trace.get("spans") or [])


def _has_fail_event(trace: dict[str, Any]) -> bool:
    for span in trace.get("spans") or []:
        for event in span.get("events") or []:
            name = str(event.get("name") or "")
            attrs = event.get("attributes") or {}
            if name.startswith("fail.") or "fail." in name or name == "loop.safety.violation":
                return True
            if any(str(k).startswith("fail.") or "fail." in str(v) for k, v in attrs.items()):
                return True
            if "loop.failure.code" in attrs:
                return True
    return False


def _has_gen_ai(trace: dict[str, Any]) -> bool:
    for span in trace.get("spans") or []:
        if "gen_ai" in str(span.get("name") or ""):
            return True
        if any(str(key).startswith("gen_ai.") for key in (span.get("attributes") or {})):
            return True
    return False


def _print_shown_and_planned(trace: dict[str, Any]) -> None:
    checks: list[tuple[str, bool, str]] = [
        (
            "iteration span (loop.iteration)",
            any(span.get("name") == "loop.iteration" for span in trace.get("spans") or []),
            "loopotel emits a loop.iteration child span per step.",
        ),
        (
            "goal_target (loop.goal_target)",
            _has_attr(trace, "loop.goal_target"),
            "integrations/loopgym.py passes the spec success threshold into emit_iteration.",
        ),
        (
            "cost_usd (loop.cost_usd)",
            _has_attr(trace, "loop.cost_usd"),
            "LoopTracer.emit_iteration accepts cost_usd, but run_traced_episode does not pass it, so this trace omits loop.cost_usd.",
        ),
        (
            "LES attrs (loop.les.cumulative_normalized, loop.les.effectiveness)",
            _has_attr(trace, "loop.les.cumulative_normalized") and _has_attr(trace, "loop.les.effectiveness"),
            "emit_iteration writes both LES attributes.",
        ),
        (
            "spec_pins",
            bool(trace.get("spec_pins")),
            "build_trace() records spec_pins from loopotel.models.spec_pins.",
        ),
        (
            "F-code/fail.* events",
            _has_fail_event(trace),
            "otel-semconv-loop.md describes loop.safety.violation / loop.failure.code. tracer.py emits loop.iteration.start, loop.iteration.end, loop.worker.complete, and loop.evaluator.complete only.",
        ),
        (
            "gen_ai.* spans",
            _has_gen_ai(trace),
            "loopotel has no gen_ai.* span names or attributes. The span tree uses loop.* (loop.run, loop.iteration).",
        ),
    ]
    print("SHOWN")
    for label, present, _note in checks:
        if present:
            print(f"  - {label}")
    print("PLANNED (not built yet)")
    for label, present, note in checks:
        if not present:
            print(f"  - {label}: {note}")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    command = args[0] if args else "all"
    if command == "spec":
        spec_step()
    elif command == "trace":
        outdir: str | Path = ROOT / "demo" / "out"
        if "--outdir" in args:
            outdir = args[args.index("--outdir") + 1]
        trace_step(outdir)
    elif command == "bench":
        bench_step()
    elif command == "all":
        spec_step()
        trace_step(ROOT / "demo" / "out")
        bench_step()
    else:
        print(f"unknown command: {command}", file=sys.stderr)
        print("usage: python demo/demo_steps.py [all|spec|trace|bench]", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
