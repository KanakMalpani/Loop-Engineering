"""LoopBench passthrough — PyPI-native when loopbench is installed."""

from __future__ import annotations

import argparse
import subprocess
import sys


def _require_loopbench() -> bool:
    try:
        import loopbench  # noqa: F401
        return True
    except ImportError:
        print("Install loopbench: pip install le-loop-stack  (includes loopbench)", file=sys.stderr)
        return False


def cmd_bench_run(args: argparse.Namespace) -> int:
    if not _require_loopbench():
        return 1
    extra = list(args.extra or [])
    if extra and extra[0] == "--":
        extra = extra[1:]
    return subprocess.call(["loopbench", "run", *extra])


def cmd_bench_suite(args: argparse.Namespace) -> int:
    if not _require_loopbench():
        return 1
    argv = [
        "loopbench",
        "run",
        "--suite",
        args.suite_id,
        "--spec",
        args.spec,
        "--seeds",
        args.seeds,
        "--submitter",
        args.submitter,
        "--backend",
        args.backend,
    ]
    if args.output:
        argv.extend(["-o", args.output])
    return subprocess.call(argv)


def cmd_bench_passthrough(args: argparse.Namespace) -> int:
    if not _require_loopbench():
        return 1
    extra = list(args.extra or [])
    if extra and extra[0] == "--":
        extra = extra[1:]
    return subprocess.call(["loopbench", *extra])


def add_bench_parser(sub: argparse._SubParsersAction) -> None:
    b = sub.add_parser("bench", help="LoopBench — run tasks or comparison suites")
    bench_sub = b.add_subparsers(dest="bench_cmd", required=True)

    suite_p = bench_sub.add_parser("suite", help="Run a comparison suite")
    suite_p.add_argument("suite_id", help="suite-repair, suite-agent, suite-knowledge, suite-rigor")
    suite_p.add_argument("--spec", required=True, help="LSS YAML path")
    suite_p.add_argument("--seeds", default="0,1,2,3,4")
    suite_p.add_argument("--submitter", default="local-dev")
    suite_p.add_argument("--backend", default="sim", choices=["sim", "live", "replay"])
    suite_p.add_argument("-o", "--output", help="Results JSON path")
    suite_p.set_defaults(func=cmd_bench_suite)

    run_p = bench_sub.add_parser("run", help="Run loopbench (e.g. run --task LB-CR-1 --spec x.yaml)")
    run_p.add_argument("extra", nargs=argparse.REMAINDER, help="Arguments after 'run'")
    run_p.set_defaults(func=cmd_bench_run)

    passthrough = bench_sub.add_parser("passthrough", help="Raw loopbench subcommand passthrough")
    passthrough.add_argument("extra", nargs=argparse.REMAINDER)
    passthrough.set_defaults(func=cmd_bench_passthrough)
