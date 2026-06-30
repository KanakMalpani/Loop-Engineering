"""CLI entry point: python -m loopforge"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from loopforge.builder import LoopBuilder
from loopforge.composition import build_composition_spec, parse_child_arg, save_composition
from loopforge.export import export_stub
from loopforge.level_hint import apply_level_hint
from loopforge.library import fork_spec
from loopforge.patterns import Pattern
from loopforge.validate import validate_yaml_file


def _save_spec(spec: dict, path: Path, *, validate: bool, suggest_level: bool, source: str | None = None) -> None:
    import yaml

    if suggest_level:
        hint = apply_level_hint(spec, source)
        print(
            f"Level hint: L{hint['taxonomy_level']} "
            f"(pattern={hint['pattern']}, workers={hint['workers']}, confidence={hint['confidence']})"
        )
    if validate:
        from loopforge.validate import validate_spec

        version = "1.1" if spec.get("composition") else "1.0"
        meta = spec.get("metadata") or {}
        if meta.get("schema_version") == "1.1":
            version = "1.1"
        errors = validate_spec(spec, lss_version=version)
        if errors:
            preview = "\n".join(f"  - {e}" for e in errors[:5])
            raise ValueError(f"Spec failed LSS validation:\n{preview}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(spec, fh, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)


def cmd_new(args: argparse.Namespace) -> int:
    builder = (
        LoopBuilder(args.name, args.objective)
        .from_pattern(args.pattern)
        .with_quality_threshold(args.quality)
        .with_max_iterations(args.max_iterations)
        .with_lss_version(args.lss)
    )
    if args.input:
        builder.with_input(args.input, example=args.input_example or None)

    out = Path(args.output)
    try:
        builder.save(out, validate=not args.no_validate, suggest_level=args.suggest_level)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Wrote {out}")
    if args.print_yaml:
        print(out.read_text(encoding="utf-8"))
    return 0


def cmd_fork(args: argparse.Namespace) -> int:
    try:
        spec = fork_spec(args.source, args.name)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.objective:
        spec["objective"] = f"{args.objective.rstrip()}\nAchieve primary_quality >= 0.80 within cost_limits with zero safety violations."
    out = Path(args.output)
    try:
        _save_spec(spec, out, validate=not args.no_validate, suggest_level=args.suggest_level, source=args.source)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Wrote {out} (forked from {args.source})")
    return 0


def cmd_compose(args: argparse.Namespace) -> int:
    base = Path.cwd()
    child_specs = [parse_child_arg(raw, base) for raw in args.children]
    out = Path(args.output)
    try:
        spec = build_composition_spec(
            args.name,
            args.objective,
            args.mode,
            child_specs,
            output_path=out,
            quality_threshold=args.quality,
        )
        save_composition(spec, out, validate=not args.no_validate, strict_composition=args.strict)
        if args.suggest_level:
            hint = apply_level_hint(spec)
            print(
                f"Level hint: L{hint['taxonomy_level']} "
                f"(pattern={hint['pattern']}, confidence={hint['confidence']})"
            )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Wrote composition {out} ({args.mode}, {len(child_specs)} children)")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"Error: spec not found: {spec_path}", file=sys.stderr)
        return 2
    try:
        if args.format == "minjson":
            out = export_minjson(spec_path, Path(args.out) if args.out else None)
        else:
            if not args.target:
                print("Error: --target required for stub export", file=sys.stderr)
                return 2
            out = export_stub(spec_path, Path(args.out), args.target)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Exported {args.format or args.target} to {out}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.spec)
    if not path.exists():
        print(f"Error: spec not found: {path}", file=sys.stderr)
        return 2
    errors = validate_yaml_file(path, lss_version=args.lss)
    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    elif errors:
        for err in errors:
            print(err, file=sys.stderr)
    else:
        print(f"Valid LSS spec: {path}")
    return 0 if not errors else 1


def cmd_list_patterns(_: argparse.Namespace) -> int:
    descriptions = {
        Pattern.SIMPLE: "Single worker + quality rubric (fastest starting point)",
        Pattern.REFLECTION: "Generator + reflector with feedback before commit",
        Pattern.VERIFICATION: "Implementer + test/scope evaluators",
        Pattern.RESEARCH: "Query planner + synthesizer for sourced briefs",
    }
    for pattern in Pattern:
        print(f"{pattern.value:14}  {descriptions[pattern]}")
    print("compose modes: sequential, parallel, nested (via `loopforge compose`)")
    return 0


def cmd_demo(_: argparse.Namespace) -> int:
    """Build all patterns to a temp dir and validate (used by daily checkin)."""
    import tempfile

    patterns = Pattern.choices()
    with tempfile.TemporaryDirectory(prefix="loopforge-demo-") as tmp:
        tmp_path = Path(tmp)
        for pattern in patterns:
            out = tmp_path / f"{pattern}-demo.yaml"
            (
                LoopBuilder(f"{pattern}-demo", f"Demo objective for {pattern} pattern")
                .from_pattern(pattern)
                .save(out)
            )
        # Fork smoke
        try:
            fork_out = tmp_path / "fork-demo.yaml"
            spec = fork_spec("research-agent", "fork-demo")
            _save_spec(spec, fork_out, validate=True, suggest_level=False, source="research-agent")
        except FileNotFoundError:
            pass
        print(f"Validated {len(patterns)}+ scaffolded specs in {tmp_path}")
    return 0


def cmd_intent(args: argparse.Namespace) -> int:
    from loopforge.intent import compile_intent

    try:
        spec, meta = compile_intent(args.text, loop_name=args.name, use_fork=not args.scaffold_only)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    out = Path(args.output)
    _save_spec(spec, out, validate=not args.no_validate, suggest_level=args.suggest_level)
    print(f"Wrote {out} (pattern={meta['pattern']}, method={meta['method']})")
    if args.print_yaml:
        print(out.read_text(encoding="utf-8"))
    return 0


def cmd_combine(args: argparse.Namespace) -> int:
    from loopforge.combine import combine_loops, save_combined_spec
    from loopforge.compact import dumps_compact_json

    library = [x.strip() for x in args.library.split(",")] if args.library else None
    paths = [x.strip() for x in args.specs.split(",")] if args.specs else None
    patterns = [p.strip() for p in args.patterns.split(",")] if args.patterns else None
    forks = [f.strip() for f in args.forks.split(",")] if args.forks else None

    if not any([args.recipe, library, paths, patterns, forks]):
        print("Error: provide recipe, --library, --specs, --patterns, or --forks", file=sys.stderr)
        return 2
    if not args.output:
        print("Error: -o/--output required", file=sys.stderr)
        return 2

    loop_name = args.name or (args.recipe or "combined-loop")
    objective = args.objective or f"Run the {loop_name} combined pipeline."
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
        out = Path(args.output)
        stats = save_combined_spec(spec, out, compact=not args.no_compact, validate=not args.no_validate)
    except (KeyError, ValueError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(
            dumps_compact_json(
                {
                    "ok": True,
                    "spec": str(out),
                    "mode": meta.get("mode"),
                    "flatten": meta.get("flatten"),
                    "tokens": stats.get("estimated_tokens"),
                    "method": meta.get("method"),
                }
            )
        )
    else:
        print(f"Wrote {out} (mode={meta.get('mode')}, flatten={meta.get('flatten')}, ~{stats.get('estimated_tokens')} tokens)")
    if args.print_yaml:
        print(out.read_text(encoding="utf-8"))
    return 0


def cmd_mix(args: argparse.Namespace) -> int:
    from loopforge.mix import list_recipes, mix_spec, save_mixed_spec

    if args.list:
        for recipe in list_recipes():
            suite = recipe.get("default_suite") or "grand"
            print(f"  {recipe['id']:18}  {recipe.get('label', '')}  suite={suite}")
        return 0

    recipe_id = args.recipe
    patterns = [p.strip() for p in args.patterns.split(",")] if args.patterns else None
    forks = [f.strip() for f in args.forks.split(",")] if args.forks else None
    if not recipe_id and not patterns and not forks:
        print("Error: provide recipe, --patterns, or --forks", file=sys.stderr)
        return 2

    if not args.output:
        print("Error: -o/--output required", file=sys.stderr)
        return 2

    loop_name = args.name or (recipe_id or "mixed-loop")
    objective = args.objective or f"Run the {loop_name} mixed loop pipeline."
    try:
        spec, meta = mix_spec(
            loop_name=loop_name,
            objective=objective,
            recipe_id=recipe_id,
            patterns=patterns,
            forks=forks,
            mode=args.mode,
            flatten=args.flatten,
        )
        out = Path(args.output)
        save_mixed_spec(spec, out, validate=not args.no_validate, compact=args.compact)
    except (KeyError, ValueError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    from loopforge.compact import estimate_tokens

    tokens = estimate_tokens(spec)
    print(f"Wrote {out} (mode={meta.get('mode')}, recipe={recipe_id}, flatten={meta.get('flatten')}, ~{tokens} tokens)")
    if args.print_yaml:
        print(out.read_text(encoding="utf-8"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="loopforge",
        description="Scaffold valid LSS loop YAML from common patterns",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_lss_flags(p: argparse.ArgumentParser) -> None:
        p.add_argument("--lss", choices=["1.0", "1.1"], default="1.0", help="LSS schema version metadata")
        p.add_argument("--suggest-level", action="store_true", help="Print LE-OP-11 taxonomy level hint on save")
        p.add_argument("--no-validate", action="store_true", help="Skip schema validation on save")

    new_p = sub.add_parser("new", help="Create a new loop spec YAML")
    new_p.add_argument("--pattern", "-p", required=True, help="Pattern name (simple, reflection, ...)")
    new_p.add_argument("--name", "-n", required=True, help="loop_name (kebab-case)")
    new_p.add_argument("--objective", required=True, help="One-line loop objective")
    new_p.add_argument("--output", "-o", required=True, help="Output YAML path")
    new_p.add_argument("--input", help="Primary input field name (default: task)")
    new_p.add_argument("--input-example", help="Example value for the primary input")
    new_p.add_argument("--quality", type=float, default=0.80, help="Quality pass threshold")
    new_p.add_argument("--max-iterations", type=int, default=8, help="Max loop iterations")
    new_p.add_argument("--print-yaml", action="store_true", help="Print generated YAML to stdout")
    add_lss_flags(new_p)
    new_p.set_defaults(func=cmd_new)

    fork_p = sub.add_parser("fork", help="Fork an existing loop-library template")
    fork_p.add_argument("--from", dest="source", required=True, help="Source loop name (e.g. research-agent)")
    fork_p.add_argument("--name", "-n", required=True, help="New loop_name")
    fork_p.add_argument("--objective", help="Override objective (optional)")
    fork_p.add_argument("--output", "-o", required=True, help="Output YAML path")
    add_lss_flags(fork_p)
    fork_p.set_defaults(func=cmd_fork)

    compose_p = sub.add_parser("compose", help="Scaffold an LSS 1.1 composition spec")
    compose_p.add_argument("--mode", required=True, choices=["sequential", "parallel", "nested"])
    compose_p.add_argument("--name", "-n", required=True)
    compose_p.add_argument("--objective", required=True)
    compose_p.add_argument("--output", "-o", required=True)
    compose_p.add_argument(
        "--children",
        nargs="+",
        required=True,
        help="Child refs: path or id:path or id:path:lens",
    )
    compose_p.add_argument("--quality", type=float, default=0.80)
    compose_p.add_argument("--strict", action="store_true", help="Run composition_validator after save")
    compose_p.add_argument("--suggest-level", action="store_true")
    compose_p.add_argument("--no-validate", action="store_true")
    compose_p.set_defaults(func=cmd_compose)

    export_p = sub.add_parser("export", help="Export spec to runnable stub or LSS-min JSON")
    export_p.add_argument("--spec", required=True, help="LSS YAML path")
    export_p.add_argument("--format", choices=["stub", "minjson"], default="stub")
    export_p.add_argument("--target", choices=["generic", "langgraph", "crewai", "openai_agents"], help="Stub target")
    export_p.add_argument("--out", required=True, help="Output directory or .min.json path")
    export_p.set_defaults(func=cmd_export)

    intent_p = sub.add_parser("intent", help="Compile natural language intent to LSS YAML (LE-OP-15)")
    intent_p.add_argument("text", help="Natural language loop objective")
    intent_p.add_argument("--name", "-n", help="loop_name override")
    intent_p.add_argument("--output", "-o", required=True, help="Output YAML path")
    intent_p.add_argument("--scaffold-only", action="store_true", help="Skip fork-from-library")
    add_lss_flags(intent_p)
    intent_p.add_argument("--print-yaml", action="store_true")
    intent_p.set_defaults(func=cmd_intent)

    val_p = sub.add_parser("validate", help="Validate an existing LSS YAML file")
    val_p.add_argument("spec", help="Path to LSS YAML")
    val_p.add_argument("--lss", choices=["1.0", "1.1"], default="1.0")
    val_p.add_argument("--json", action="store_true", help="Emit JSON result")
    val_p.set_defaults(func=cmd_validate)

    sub.add_parser("list-patterns", help="List supported patterns").set_defaults(func=cmd_list_patterns)
    sub.add_parser("demo", help="Scaffold and validate all patterns (smoke test)").set_defaults(
        func=cmd_demo
    )

    mix_p = sub.add_parser("mix", help="Mix patterns/recipes into one LSS spec")
    mix_p.add_argument("--list", action="store_true", help="List bundled recipes")
    mix_p.add_argument("recipe", nargs="?", help="Recipe id (dev-agent, swarm-review, …)")
    mix_p.add_argument("--patterns", help="Comma-separated patterns")
    mix_p.add_argument("--forks", help="Comma-separated library fork names")
    mix_p.add_argument("--mode", choices=["sequential", "parallel", "nested"])
    mix_p.add_argument("--objective", help="Pipeline objective")
    mix_p.add_argument("--name", "-n", help="loop_name")
    mix_p.add_argument("-o", "--output", help="Output YAML path")
    mix_p.add_argument("--flatten", action="store_true", default=True, help="Flat single-file spec (default)")
    mix_p.add_argument("--no-flatten", dest="flatten", action="store_false")
    mix_p.add_argument("--compact", action="store_true", default=True, help="Compact YAML (default)")
    mix_p.add_argument("--no-compact", dest="compact", action="store_false")
    mix_p.add_argument("--no-validate", action="store_true")
    mix_p.add_argument("--print-yaml", action="store_true")
    mix_p.set_defaults(func=cmd_mix)

    comb_p = sub.add_parser("combine", help="Combine library loops, specs, or recipes (token-efficient)")
    comb_p.add_argument("recipe", nargs="?", help="Recipe id (optional if using --library/--specs)")
    comb_p.add_argument("--library", help="Comma-separated loop-library names (research-agent,coding-agent)")
    comb_p.add_argument("--specs", help="Comma-separated paths to LSS YAML files")
    comb_p.add_argument("--patterns", help="Comma-separated patterns")
    comb_p.add_argument("--forks", help="Comma-separated library fork names")
    comb_p.add_argument("--mode", choices=["sequential", "parallel", "nested"], default="sequential")
    comb_p.add_argument("--objective", help="Combined pipeline objective")
    comb_p.add_argument("--name", "-n", help="loop_name")
    comb_p.add_argument("-o", "--output", help="Output YAML path")
    comb_p.add_argument("--no-flatten", action="store_true", help="Keep LSS 1.1 child refs instead of flat merge")
    comb_p.add_argument("--no-compact", action="store_true", help="Verbose YAML")
    comb_p.add_argument("--no-validate", action="store_true")
    comb_p.add_argument("--max-tokens", type=int, help="Cap estimated spec tokens")
    comb_p.add_argument("--json", action="store_true")
    comb_p.add_argument("--print-yaml", action="store_true")
    comb_p.set_defaults(func=cmd_combine)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
