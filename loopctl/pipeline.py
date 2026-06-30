"""Unified intent → validate → score → trace → observed LES pipeline."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import yaml

from loopforge.compact import compact_pipeline_report, compact_spec, dumps_compact_json
from loopforge.intent import compile_intent
from loopforge.validate import load_schema, validate_spec

from loopctl.scoring.observed import score_trace
from loopctl.scoring.structural import score_spec_file


def repo_root() -> Path | None:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "tools" / "les_calculator.py").is_file():
            return parent
    return None


def _save_spec(spec: dict, out_spec: Path, *, compact: bool) -> None:
    out_spec.parent.mkdir(parents=True, exist_ok=True)
    dump_payload = compact_spec(spec) if compact else spec
    with out_spec.open("w", encoding="utf-8") as fh:
        if compact:
            fh.write(yaml.safe_dump(dump_payload, sort_keys=False, default_flow_style=True, width=120))
        else:
            yaml.safe_dump(dump_payload, fh, sort_keys=False, default_flow_style=False, allow_unicode=True)


def run_pipeline(args: argparse.Namespace) -> int:
    out_spec = Path(args.output) if args.output else Path(tempfile.gettempdir()) / "loopctl-pipeline.yaml"
    preset = None

    if args.recipe:
        from loopforge.mix import load_recipe, mix_spec, save_mixed_spec

        loop_name = args.name or args.recipe
        spec, meta = mix_spec(
            loop_name=loop_name,
            objective=args.intent,
            recipe_id=args.recipe,
        )
        meta["method"] = "mix"
        meta["recipe"] = args.recipe
        if args.suite:
            meta["bench_suite"] = args.suite
        elif not meta.get("default_suite"):
            try:
                meta["bench_suite"] = load_recipe(args.recipe).get("default_suite")
            except KeyError:
                pass
        save_mixed_spec(spec, out_spec, validate=True, compact=args.compact)
    elif args.agent:
        from loopctl.agent_cmds import _compile_for_agent

        spec, meta, preset = _compile_for_agent(args.intent, args.agent, loop_name=args.name)
        meta["agent"] = preset.key
        meta["bench_task"] = args.task or preset.bench_task
        meta["bench_suite"] = args.suite or preset.bench_suite
        meta["default_recipe"] = preset.default_recipe
        _save_spec(spec, out_spec, compact=args.compact)
    else:
        spec, meta = compile_intent(args.intent, loop_name=args.name)
        _save_spec(spec, out_spec, compact=args.compact)

    lss_version = "1.1" if spec.get("composition") else "1.0"
    errors = validate_spec(spec, lss_version=lss_version)
    if errors:
        print("Validation failed:", file=sys.stderr)
        for e in errors[:5]:
            print(f"  - {e}", file=sys.stderr)
        return 1

    report: dict = {
        "intent": args.intent,
        "spec_path": str(out_spec),
        "pattern": meta.get("pattern"),
        "method": meta.get("method"),
        "lss_version": lss_version,
        "valid": True,
    }
    if meta.get("agent"):
        report["agent"] = meta["agent"]
    if meta.get("recipe"):
        report["recipe"] = meta["recipe"]
    bench_suite = args.suite or meta.get("bench_suite")
    bench_task = args.task or meta.get("bench_task")
    if bench_suite:
        report["suite"] = bench_suite
        report["bench_cmd"] = (
            f"loopctl bench suite {bench_suite} --spec {out_spec} --seeds 0,1,2,3,4 -o results.json"
        )
    elif bench_task:
        report["bench_task"] = bench_task
        report["bench_cmd"] = (
            f"loopctl bench run --task {bench_task} --spec {out_spec} --seeds 0,1,2,3,4 -o results.json"
        )

    if not args.skip_score:
        try:
            report["structural_les"] = score_spec_file(out_spec)
        except Exception as exc:
            print(f"Structural score failed: {exc}", file=sys.stderr)
            return 1

    if args.export:
        from loopforge.export import export_stub

        export_dir = Path(args.export_dir or out_spec.parent / f"export-{args.export}")
        export_stub(out_spec, export_dir, args.export)
        report["export"] = {"target": args.export, "dir": str(export_dir)}

    trace_path = Path(args.trace) if args.trace else None
    if args.run_loopgym:
        try:
            import loopgym as lg
        except ImportError:
            print("loopgym required for --run-loopgym", file=sys.stderr)
            return 1
        trace_path = trace_path or Path(tempfile.gettempdir()) / "loopctl-pipeline-trace.json"
        env = lg.make("loopbench/code-repair-v1")
        try:
            episode = env.run_episode(task_id="cr-001", seed=42, trace_path=str(trace_path))
        except TypeError:
            episode = env.run_episode(task_id="cr-001", seed=42)
        report["loopgym"] = {"success": episode.get("success"), "trace": str(trace_path)}

    if trace_path and trace_path.exists():
        schema_path = Path(__file__).resolve().parent / "schemas" / "loop-trace-1.0.schema.json"
        if not schema_path.exists():
            root = repo_root()
            if root:
                schema_path = root / "standards" / "schema" / "loop-trace-1.0.schema.json"
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        schema = load_schema(schema_path)
        terrors = validate_spec(trace, schema)
        report["trace_valid"] = len(terrors) == 0
        if terrors:
            report["trace_errors"] = terrors[:3]
        if report.get("trace_valid", False):
            spec_data = yaml.safe_load(out_spec.read_text(encoding="utf-8"))
            report["observed_les"] = score_trace(trace, spec_data)

    if args.json:
        payload = compact_pipeline_report(report) if args.compact else report
        print(dumps_compact_json(payload) if args.compact else json.dumps(payload, indent=2))
    else:
        print(f"Wrote {out_spec} pattern={meta.get('pattern')} method={meta.get('method')}")
        if report.get("structural_les"):
            les = report["structural_les"].get("les") or report["structural_les"].get("composite")
            print(f"Structural LES: {les}")
        if report.get("observed_les"):
            print(f"Observed LES: {report['observed_les'].get('observed_les')}")

    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    return 0


def add_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("pipeline", help="Intent → validate → score → optional trace pipeline")
    p.add_argument("--intent", required=True, help="Natural language loop objective")
    p.add_argument("--agent", help="Agent preset (langgraph, crewai, react, aider, …)")
    p.add_argument("--recipe", help="Mix recipe (dev-agent, swarm-review, …)")
    p.add_argument("--suite", help="LoopBench suite (suite-repair, suite-agent, …)")
    p.add_argument("--task", help="LoopBench task id override (optional)")
    p.add_argument("--name", help="loop_name override")
    p.add_argument("-o", "--output", help="Write compiled spec YAML here")
    p.add_argument(
        "--export",
        choices=["generic", "langgraph", "crewai", "openai_agents"],
        help="Export runnable stub",
    )
    p.add_argument("--export-dir", help="Export output directory")
    p.add_argument("--run-loopgym", action="store_true", help="Run LoopGym episode and emit trace")
    p.add_argument("--trace", type=Path, help="Trace JSON path (with --run-loopgym or validate existing)")
    p.add_argument("--skip-score", action="store_true", help="Skip structural LES")
    p.add_argument("--compact", action="store_true", help="Compact YAML + minimal JSON (token-efficient)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--report", help="Write full JSON report to file")
    p.set_defaults(func=run_pipeline)
