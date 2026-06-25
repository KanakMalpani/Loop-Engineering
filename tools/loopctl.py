#!/usr/bin/env python3
"""Unified Loop Engineering toolchain CLI."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SCRIPTS = ROOT / "scripts"


def run(cmd: list[str]) -> int:
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


def cmd_forge(args: argparse.Namespace) -> int:
    return run([sys.executable, "-m", "loopforge", *args.forge_args])


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.spec)
    if not path.exists():
        print(f"Error: spec not found: {path}", file=sys.stderr)
        return 2
    cmd = [sys.executable, str(TOOLS / "loop_validator.py"), str(path)]
    if args.lss == "1.1":
        cmd.extend(["--schema", str(ROOT / "standards" / "schema" / "lss-1.1-composition.schema.json")])
    code = run(cmd)
    if code == 0 and (path.parent.name == "compositions" or _has_composition(path)):
        comp_cmd = [sys.executable, str(TOOLS / "composition_validator.py"), str(path)]
        if args.strict:
            comp_cmd.append("--strict")
        code = run(comp_cmd)
    return code


def _has_composition(path: Path) -> bool:
    import yaml

    try:
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        return bool(isinstance(spec, dict) and spec.get("composition"))
    except Exception:
        return False


def cmd_score(args: argparse.Namespace) -> int:
    cmd = [sys.executable, str(TOOLS / "les_calculator.py"), "--spec", args.spec]
    if args.json:
        cmd.append("--json")
    return run(cmd)


def cmd_diagram(args: argparse.Namespace) -> int:
    cmd = [sys.executable, str(TOOLS / "loop_diagram_generator.py"), args.spec]
    if args.output:
        cmd.extend(["--output", args.output])
    return run(cmd)


def cmd_level(args: argparse.Namespace) -> int:
    cmd = [sys.executable, str(TOOLS / "level_recommender.py")]
    if args.pattern:
        cmd.extend(["--pattern", args.pattern, "--iter-len", str(args.iter_len), "--workers", str(args.workers)])
    elif args.spec:
        import yaml

        spec_path = Path(args.spec)
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
        name = spec.get("loop_name") or spec_path.stem
        from loopforge.level_hint import infer_pattern

        pattern = infer_pattern(spec, name)
        workers = len(spec.get("workers") or [])
        cmd.extend(["--pattern", pattern, "--iter-len", str(args.iter_len), "--workers", str(max(workers, 1))])
    else:
        print("Provide --pattern or --spec", file=sys.stderr)
        return 2
    return run(cmd)


def cmd_bench(args: argparse.Namespace) -> int:
    try:
        cmd = ["loopbench", *args.bench_args]
        return subprocess.call(cmd)
    except FileNotFoundError:
        print("loopbench not installed. Run: pip install loopbench", file=sys.stderr)
        return 1


def cmd_trace(args: argparse.Namespace) -> int:
    if args.trace_command == "validate":
        from loopforge.validate import load_schema, validate_spec
        import json

        path = Path(args.file)
        with path.open(encoding="utf-8") as fh:
            trace = json.load(fh)
        schema = load_schema(ROOT / "standards" / "schema" / "loop-trace-1.0.schema.json")
        errors = validate_spec(trace, schema)
        if errors:
            for e in errors:
                print(e, file=sys.stderr)
            return 1
        print(f"Valid loop trace: {path}")
        return 0
    print(f"Unknown trace command: {args.trace_command}", file=sys.stderr)
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="loopctl", description="Loop Engineering unified toolchain")
    sub = parser.add_subparsers(dest="command", required=True)

    forge_p = sub.add_parser("forge", help="Pass-through to loopforge CLI")
    forge_p.add_argument("forge_args", nargs=argparse.REMAINDER, help="loopforge arguments")
    forge_p.set_defaults(func=cmd_forge)

    val_p = sub.add_parser("validate", help="Validate LSS YAML (+ composition if present)")
    val_p.add_argument("spec", help="Path to spec")
    val_p.add_argument("--lss", choices=["1.0", "1.1"], default="1.0")
    val_p.add_argument("--strict", action="store_true")
    val_p.set_defaults(func=cmd_validate)

    score_p = sub.add_parser("score", help="Structural LES from spec")
    score_p.add_argument("--spec", required=True)
    score_p.add_argument("--json", action="store_true")
    score_p.set_defaults(func=cmd_score)

    diag_p = sub.add_parser("diagram", help="Generate Mermaid diagram from spec")
    diag_p.add_argument("spec")
    diag_p.add_argument("--output", "-o")
    diag_p.set_defaults(func=cmd_diagram)

    level_p = sub.add_parser("level", help="LE-OP-11 taxonomy level recommender")
    level_p.add_argument("--pattern")
    level_p.add_argument("--spec")
    level_p.add_argument("--iter-len", type=int, default=3)
    level_p.add_argument("--workers", type=int, default=1)
    level_p.set_defaults(func=cmd_level)

    bench_p = sub.add_parser("bench", help="Passthrough to loopbench CLI")
    bench_p.add_argument("bench_args", nargs=argparse.REMAINDER)
    bench_p.set_defaults(func=cmd_bench)

    trace_p = sub.add_parser("trace", help="Loop trace schema tools")
    trace_sub = trace_p.add_subparsers(dest="trace_command", required=True)
    trace_val = trace_sub.add_parser("validate", help="Validate loop trace JSON")
    trace_val.add_argument("file")
    trace_val.set_defaults(func=cmd_trace)

    return parser


def main(argv: list[str] | None = None) -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
