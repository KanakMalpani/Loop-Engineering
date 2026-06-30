"""loopctl mix — recipe / pattern blends with bench suite hints."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from loopforge.compact import dumps_compact_json
from loopforge.mix import list_recipes, mix_spec, save_mixed_spec

from loopctl.scoring.structural import score_spec_file


def _bench_cmd(suite: str | None, spec: Path) -> str:
    if suite:
        return f'loopctl bench suite {suite} --spec "{spec}" --seeds 0,1,2,3,4 -o results.json'
    return f'loopctl bench run --task LB-CR-1 --spec "{spec}" --seeds 0,1,2,3,4 -o results.json'


def cmd_mix(args: argparse.Namespace) -> int:
    if args.list:
        recipes = [{"id": r["id"], "label": r.get("label"), "suite": r.get("default_suite")} for r in list_recipes()]
        print(dumps_compact_json({"recipes": recipes}))
        return 0

    recipe_id = args.recipe
    patterns = [p.strip() for p in args.patterns.split(",")] if args.patterns else None
    forks = [f.strip() for f in args.forks.split(",")] if args.forks else None

    if not recipe_id and not patterns and not forks:
        print("Error: provide recipe name, --list, --patterns, or --forks", file=sys.stderr)
        return 2

    loop_name = args.name or (recipe_id or "mixed-loop")
    objective = args.intent or f"Run the {loop_name} mixed loop pipeline."

    try:
        spec, meta = mix_spec(
            loop_name=loop_name,
            objective=objective,
            recipe_id=recipe_id,
            patterns=patterns,
            forks=forks,
            mode=args.mode,
            flatten=not getattr(args, "no_flatten", False),
        )
    except (KeyError, ValueError, FileNotFoundError) as exc:
        print(dumps_compact_json({"ok": False, "error": str(exc)}))
        return 1

    out = Path(args.output) if args.output else Path(tempfile.gettempdir()) / f"{loop_name}.yaml"
    try:
        save_mixed_spec(spec, out, validate=not args.no_validate, compact=args.compact)
    except ValueError as exc:
        print(dumps_compact_json({"ok": False, "error": str(exc)}))
        return 1

    suite = args.suite or meta.get("default_suite")
    report: dict = {
        "ok": True,
        "recipe": recipe_id,
        "mode": meta.get("mode"),
        "spec": str(out),
        "suite": suite,
        "bench_cmd": _bench_cmd(suite, out),
    }

    if not args.skip_score:
        try:
            scored = score_spec_file(out)
            les = scored.get("les") or scored.get("composite")
            if les is not None:
                report["les"] = round(float(les), 1)
        except Exception as exc:
            report["score_error"] = str(exc)

    if args.json or args.compact:
        print(dumps_compact_json(report))
    else:
        print(f"Mixed → {out} (mode={meta.get('mode')}, recipe={recipe_id})")
        print(f"  bench: {report['bench_cmd']}")
        if report.get("les") is not None:
            print(f"  LES: {report['les']}")
    return 0


def add_mix_parser(sub: argparse._SubParsersAction) -> None:
    mix = sub.add_parser("mix", help="Mix patterns/recipes into one LSS spec")
    mix.add_argument("--list", action="store_true", help="List bundled recipes (JSON)")
    mix.add_argument("recipe", nargs="?", help="Recipe id (dev-agent, swarm-review, …)")
    mix.add_argument("--patterns", help="Comma-separated patterns (react,verification,…)")
    mix.add_argument("--forks", help="Comma-separated library fork names")
    mix.add_argument("--mode", choices=["sequential", "parallel", "nested"], help="Override recipe mode")
    mix.add_argument("--intent", help="Objective string for child loops")
    mix.add_argument("--name", "-n", help="loop_name for output spec")
    mix.add_argument("--suite", help="LoopBench suite for bench_cmd hint")
    mix.add_argument("-o", "--output", help="Output YAML path")
    mix.add_argument("--flatten", action="store_true", default=True, help="Flat single-file spec (default)")
    mix.add_argument("--no-flatten", dest="no_flatten", action="store_true")
    mix.add_argument("--compact", action="store_true", default=True, help="Compact YAML output")
    mix.add_argument("--no-validate", action="store_true")
    mix.add_argument("--skip-score", action="store_true")
    mix.add_argument("--json", action="store_true")
    mix.set_defaults(func=cmd_mix)
