"""loop combine — merge library loops with flat compact output (token-efficient)."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from loopforge.compact import dumps_compact_json, estimate_tokens
from loopforge.combine import combine_loops, save_combined_spec


def cmd_combine(args: argparse.Namespace) -> int:
    library = [x.strip() for x in args.library.split(",")] if args.library else None
    paths = [x.strip() for x in args.specs.split(",")] if args.specs else None
    patterns = [p.strip() for p in args.patterns.split(",")] if args.patterns else None
    forks = [f.strip() for f in args.forks.split(",")] if args.forks else None

    if not any([args.recipe, library, paths, patterns, forks]):
        print(
            dumps_compact_json(
                {
                    "ok": False,
                    "error": "provide recipe, --library, --specs, --patterns, or --forks",
                    "hint": "loop combine --library research-agent,autonomous-debugger -o out.yaml",
                }
            ),
            file=sys.stderr,
        )
        return 2

    loop_name = args.name or (args.recipe or "combined-loop")
    objective = args.intent or f"Run the {loop_name} combined pipeline."
    out = Path(args.output) if args.output else Path(tempfile.gettempdir()) / f"{loop_name}.yaml"

    try:
        spec, meta = combine_loops(
            loop_name,
            objective,
            recipe_id=args.recipe,
            patterns=patterns,
            forks=forks,
            library_names=library,
            spec_paths=paths,
            mode=args.mode,
            flatten=not args.no_flatten,
            compact=not args.no_compact,
            validate=not args.no_validate,
            max_tokens=args.max_tokens,
        )
        stats = save_combined_spec(spec, out, compact=not args.no_compact, validate=not args.no_validate)
    except (KeyError, ValueError, FileNotFoundError) as exc:
        print(dumps_compact_json({"ok": False, "error": str(exc)}))
        return 1

    report = {
        "ok": True,
        "spec": str(out),
        "mode": meta.get("mode"),
        "method": meta.get("method"),
        "flatten": meta.get("flatten", not args.no_flatten),
        "tokens": stats.get("estimated_tokens"),
        "suite": meta.get("default_suite"),
    }
    if meta.get("token_budget"):
        report["token_budget"] = meta["token_budget"]
    if args.json or args.compact:
        print(dumps_compact_json(report))
    else:
        print(f"Combined -> {out} (~{report['tokens']} tokens, flatten={report['flatten']})")
    return 0


def add_combine_parser(sub: argparse._SubParsersAction) -> None:
    c = sub.add_parser("combine", help="Combine loops from library, specs, or recipes (flat + compact)")
    c.add_argument("recipe", nargs="?", help="Optional recipe id")
    c.add_argument("--library", help="Comma-separated loop-library templates")
    c.add_argument("--specs", help="Comma-separated LSS YAML paths")
    c.add_argument("--patterns", help="Comma-separated patterns")
    c.add_argument("--forks", help="Comma-separated fork names")
    c.add_argument("--mode", choices=["sequential", "parallel", "nested"], default="sequential")
    c.add_argument("--intent", help="Combined objective")
    c.add_argument("--name", "-n", help="loop_name")
    c.add_argument("-o", "--output", help="Output YAML path")
    c.add_argument("--no-flatten", action="store_true", help="Use LSS 1.1 child refs (more tokens)")
    c.add_argument("--no-compact", action="store_true")
    c.add_argument("--no-validate", action="store_true")
    c.add_argument("--max-tokens", type=int, help="Cap estimated spec tokens via progressive compact")
    c.add_argument("--compact", action="store_true", default=True, help="Compact JSON output")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_combine)
