"""Unified intent → validate → score → trace → observed LES pipeline."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from loopforge.intent import compile_intent
from loopforge.validate import validate_spec


def repo_root() -> Path | None:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "tools" / "les_calculator.py").is_file():
            return parent
    return None


def run_pipeline(args: argparse.Namespace) -> int:
    out_spec = Path(args.output) if args.output else Path(tempfile.gettempdir()) / "loopctl-pipeline.yaml"
    spec, meta = compile_intent(args.intent, loop_name=args.name)
    lss_version = "1.1" if spec.get("composition") else "1.0"
    errors = validate_spec(spec, lss_version=lss_version)
    if errors:
        print("Validation failed:", file=sys.stderr)
        for e in errors[:5]:
            print(f"  - {e}", file=sys.stderr)
        return 1

    out_spec.parent.mkdir(parents=True, exist_ok=True)
    with out_spec.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(spec, fh, sort_keys=False, default_flow_style=False, allow_unicode=True)

    report: dict = {
        "intent": args.intent,
        "spec_path": str(out_spec),
        "pattern": meta.get("pattern"),
        "method": meta.get("method"),
        "lss_version": lss_version,
        "valid": True,
    }

    root = repo_root()
    if root and not args.skip_score:
        proc = subprocess.run(
            [sys.executable, str(root / "tools" / "les_calculator.py"), "--spec", str(out_spec), "--json"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            report["structural_les"] = json.loads(proc.stdout)

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
        from loopforge.validate import load_schema, validate_spec as validate_trace_dict

        schema_path = Path(__file__).resolve().parent / "schemas" / "loop-trace-1.0.schema.json"
        if not schema_path.exists() and root:
            schema_path = root / "standards" / "schema" / "loop-trace-1.0.schema.json"
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        schema = load_schema(schema_path)
        terrors = validate_trace_dict(trace, schema)
        report["trace_valid"] = len(terrors) == 0
        if terrors:
            report["trace_errors"] = terrors[:3]
        if root and report.get("trace_valid", False):
            proc = subprocess.run(
                [
                    sys.executable,
                    str(root / "tools" / "observed_les.py"),
                    str(trace_path),
                    "--spec",
                    str(out_spec),
                    "--json",
                ],
                cwd=root,
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                report["observed_les"] = json.loads(proc.stdout)

    if args.json:
        print(json.dumps(report, indent=2))
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
    p.add_argument("--name", help="loop_name override")
    p.add_argument("-o", "--output", help="Write compiled spec YAML here")
    p.add_argument("--export", choices=["generic", "langgraph", "crewai"], help="Export runnable stub")
    p.add_argument("--export-dir", help="Export output directory")
    p.add_argument("--run-loopgym", action="store_true", help="Run LoopGym episode and emit trace")
    p.add_argument("--trace", type=Path, help="Trace JSON path (with --run-loopgym or validate existing)")
    p.add_argument("--skip-score", action="store_true", help="Skip structural LES (offline)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--report", help="Write full JSON report to file")
    p.set_defaults(func=run_pipeline)
