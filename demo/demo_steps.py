#!/usr/bin/env python3
"""Offline deterministic demo steps: spec, trace, packages, benchmark.

No model calls. SimEnv uses MockLLM. Step 4 exercises loop-core (loaded by
path), loopnet, loopbench LES math, loopgym export, and loopotel trace checks.
Benchmark numbers come from the sandbox evaluator and a read-only stub file.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "packages/loopgym/loopgym/envs/loopbench/code-repair-v1/spec.yaml"
FIXTURES = ROOT / "packages/loopbench/fixtures"
STUB_RESULTS = ROOT / "benchmarks/loopbench-validity/results/stub-fixed-all-10.json"
RECORD_SCHEMA = ROOT / "packages/loopnet/schema/loopnet-record-v1.json"
VALIDATE_LSS_PATH = ROOT / "packages/loop-core/tools/validate_lss.py"
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


def _load_validate_lss_module():
    spec = importlib.util.spec_from_file_location("validate_lss", VALIDATE_LSS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validate_lss from {VALIDATE_LSS_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _episode_from_trace(trace: dict[str, Any]) -> dict[str, Any]:
    spans = trace.get("spans") or []
    root_attrs = (spans[0].get("attributes") or {}) if spans else {}
    tokens_total = int(root_attrs.get("loop.tokens_total") or 0)
    iteration_spans = [span for span in spans if span.get("name") == "loop.iteration"]
    iteration_spans.sort(
        key=lambda span: int((span.get("attributes") or {}).get("loop.iteration", 0))
    )
    trajectory: list[dict[str, Any]] = []
    for span in iteration_spans:
        attrs = span.get("attributes") or {}
        trajectory.append(
            {
                "iteration": int(attrs.get("loop.iteration", len(trajectory) + 1)),
                "quality_score": float(attrs.get("loop.goal_score", 0.0)),
            }
        )
    return {
        "trajectory": trajectory,
        "success": trace.get("outcome") == "success",
        "termination_reason": str(trace.get("termination_reason") or ""),
        "tokens_used": tokens_total,
        "task_id": trace.get("task_id"),
    }


def _gen_ai_span_count(trace: dict[str, Any]) -> int:
    count = 0
    for span in trace.get("spans") or []:
        attrs = span.get("attributes") or {}
        if any(str(key).startswith("gen_ai.") for key in attrs):
            count += 1
    return count


def _fail_event_names(trace: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for span in trace.get("spans") or []:
        for event in span.get("events") or []:
            name = str(event.get("name") or "")
            if name.startswith("fail."):
                names.append(name)
    return names


def packages_step(trace: dict[str, Any], outdir: str | Path) -> dict[str, Any]:
    """Exercise monorepo packages against one traced MockLLM episode."""
    import jsonschema
    import loopnet
    from loopbench.les_compute import RunMetrics, compute_task_les
    from loopgym.export.loopnet import episode_to_record
    from loopgym.runtime.compiler import compile_lss
    from loopgym.runtime.loop_runtime import load_lss_spec
    from loopnet.les import trajectory_diagnostics
    from loopotel.validate import validate_trace

    print("=== 4. PACKAGES ===")

    validate_lss = _load_validate_lss_module()
    lss_spec = validate_lss.load_yaml(SPEC_PATH)
    lss_schema = validate_lss.load_schema(validate_lss.DEFAULT_SCHEMA)
    loop_core_errors = validate_lss.validate_spec(lss_spec, lss_schema)
    if loop_core_errors:
        err_text = "; ".join(loop_core_errors)
        print(
            f"loop-core: validate_lss.validate_spec called -> {len(loop_core_errors)} errors: {err_text}"
        )
    else:
        print(f"loop-core: validate_lss.validate_spec called -> {len(loop_core_errors)} errors")

    spec = load_lss_spec(SPEC_PATH)
    graph = compile_lss(spec)
    env_id = str(trace.get("env_id") or "loopbench/code-repair-v1")
    episode = _episode_from_trace(trace)
    record = episode_to_record(episode, spec=spec, env_id=env_id)
    failure_mode = record.get("failure_mode")
    if failure_mode is not None and failure_mode not in loopnet.FAILURE_MODES:
        raise RuntimeError(f"unexpected failure_mode: {failure_mode}")

    record_schema = json.loads(RECORD_SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(record_schema)
    schema_errors = sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path))
    if schema_errors:
        messages = "; ".join(err.message for err in schema_errors)
        raise RuntimeError(f"loopnet record schema validation failed: {messages}")

    traj = record["trajectory"]
    diag = trajectory_diagnostics(traj)
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    record_path = out / "record.json"
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(
        "loopnet: loopgym.export.loopnet.episode_to_record called ->"
        f" record_id={record['record_id']} failure_mode={failure_mode}"
        f" trajectory_diagnostics={diag}"
    )

    goal_trace = [float(step["goal_score"]) for step in traj]
    run = RunMetrics(
        task_instance_id=str(trace.get("task_id") or "cr-001"),
        seed=0,
        g_final=float(traj[-1]["goal_score"]),
        g_0=float(traj[0]["goal_score"]),
        g_target=float(graph.quality_threshold),
        iterations=len(traj),
        t_budget=int(graph.max_iterations),
        cost_usd=round(sum(float(step["cost_usd"]) for step in traj), 4),
        elapsed_s=round(sum(float(step["latency_seconds"]) for step in traj), 4),
        success=bool(episode["success"]),
        termination_reason=str(episode["termination_reason"]),
        goal_trace=goal_trace,
    )
    les_result = compute_task_les([run], backend="sim")
    print(
        "loopbench: les_compute.compute_task_les called ->"
        f" les_observed={les_result.les_observed} {PENDING}"
    )

    print(
        "loopgym: make('loopbench/code-repair-v1') + SimEnv/MockLLM,"
        " loopgym.export.loopnet.episode_to_record called -> ok"
    )

    valid, ltf_errors = validate_trace(trace)
    fail_names = _fail_event_names(trace)
    print(
        "loopotel: validate.validate_trace called ->"
        f" valid={valid} gen_ai_spans={_gen_ai_span_count(trace)}"
        f" fail_events={fail_names}"
    )
    if not valid:
        raise RuntimeError("LTF validation failed: " + "; ".join(ltf_errors))

    print()
    return {"loop_core_errors": loop_core_errors, "record": record, "les": les_result}


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
    elif command == "packages":
        outdir = ROOT / "demo" / "out"
        if "--outdir" in args:
            outdir = args[args.index("--outdir") + 1]
        trace = trace_step(outdir)
        packages_step(trace, outdir)
    elif command == "bench":
        bench_step()
    elif command == "all":
        demo_out = ROOT / "demo" / "out"
        spec_step()
        trace = trace_step(demo_out)
        packages_step(trace, demo_out)
        bench_step()
    else:
        print(f"unknown command: {command}", file=sys.stderr)
        print(
            "usage: python demo/demo_steps.py [all|spec|trace|packages|bench]",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
