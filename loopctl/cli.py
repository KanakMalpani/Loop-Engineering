"""Portable loopctl CLI — works from PyPI install or repo clone."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from loopforge.validate import load_schema, validate_spec, validate_yaml_file

from loopctl.pipeline import add_parser as add_pipeline_parser


def repo_root() -> Path | None:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "tools" / "les_calculator.py").is_file():
            return parent
    return None


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.spec)
    if not path.exists():
        print(f"Error: not found: {path}", file=sys.stderr)
        return 2
    errors = validate_yaml_file(path, lss_version=args.lss)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print(f"Valid LSS spec: {path}")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    root = repo_root()
    if root:
        cmd = [sys.executable, str(root / "tools" / "les_calculator.py"), "--spec", str(args.spec)]
        if args.json:
            cmd.append("--json")
        return subprocess.call(cmd, cwd=root)
    print("Structural score requires discipline repo clone (tools/les_calculator.py)", file=sys.stderr)
    return 1


def cmd_trace_validate(args: argparse.Namespace) -> int:
    path = Path(args.file)
    trace = json.loads(path.read_text(encoding="utf-8"))
    schema_path = Path(__file__).resolve().parent / "schemas" / "loop-trace-1.0.schema.json"
    if not schema_path.exists():
        root = repo_root()
        if root:
            schema_path = root / "standards" / "schema" / "loop-trace-1.0.schema.json"
    schema = load_schema(schema_path)
    errors = validate_spec(trace, schema)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print(f"Valid loop trace: {path}")
    return 0


def cmd_observed(args: argparse.Namespace) -> int:
    root = repo_root()
    if not root:
        print("Observed LES requires discipline repo (tools/observed_les.py)", file=sys.stderr)
        return 1
    cmd = [sys.executable, str(root / "tools" / "observed_les.py"), str(args.trace)]
    if args.spec:
        cmd.extend(["--spec", str(args.spec)])
    if args.json:
        cmd.append("--json")
    return subprocess.call(cmd, cwd=root)


def cmd_forge(args: argparse.Namespace) -> int:
    return subprocess.call([sys.executable, "-m", "loopforge", *args.forge_args])


def cmd_repo_passthrough(script: str, argv: list[str]) -> int:
    root = repo_root()
    if not root:
        print(f"{script} requires discipline repo clone", file=sys.stderr)
        return 1
    return subprocess.call([sys.executable, str(root / "tools" / script), *argv], cwd=root)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="loopctl", description="Loop Engineering unified CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    forge = sub.add_parser("forge", help="Passthrough to loopforge")
    forge.add_argument("forge_args", nargs=argparse.REMAINDER)
    forge.set_defaults(func=cmd_forge)

    val = sub.add_parser("validate", help="Validate LSS YAML")
    val.add_argument("spec")
    val.add_argument("--lss", choices=["1.0", "1.1"], default="1.0")
    val.set_defaults(func=cmd_validate)

    score = sub.add_parser("score", help="Structural LES from spec")
    score.add_argument("--spec", required=True)
    score.add_argument("--json", action="store_true")
    score.set_defaults(func=cmd_score)

    trace = sub.add_parser("trace", help="Loop trace tools")
    trace_sub = trace.add_subparsers(dest="trace_cmd", required=True)
    tv = trace_sub.add_parser("validate", help="Validate trace JSON")
    tv.add_argument("file")
    tv.set_defaults(func=cmd_trace_validate)

    obs = sub.add_parser("observed", help="Observed LES from trace JSON")
    obs.add_argument("trace")
    obs.add_argument("--spec")
    obs.add_argument("--json", action="store_true")
    obs.set_defaults(func=cmd_observed)

    def diagram(args: argparse.Namespace) -> int:
        cmd = [args.spec]
        if args.output:
            cmd.extend(["--output", args.output])
        return cmd_repo_passthrough("loop_diagram_generator.py", cmd)

    diag = sub.add_parser("diagram", help="Mermaid diagram (repo clone)")
    diag.add_argument("spec")
    diag.add_argument("--output", "-o")
    diag.set_defaults(func=diagram)

    def level(args: argparse.Namespace) -> int:
        cmd = []
        if args.pattern:
            cmd.extend(["--pattern", args.pattern, "--iter-len", str(args.iter_len), "--workers", str(args.workers)])
        return cmd_repo_passthrough("level_recommender.py", cmd)

    lvl = sub.add_parser("level", help="LE-OP-11 level (repo clone)")
    lvl.add_argument("--pattern")
    lvl.add_argument("--iter-len", type=int, default=3)
    lvl.add_argument("--workers", type=int, default=1)
    lvl.set_defaults(func=level)

    add_pipeline_parser(sub)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
