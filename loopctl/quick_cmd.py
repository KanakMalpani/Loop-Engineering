"""One-liner loopctl quick — minimal tokens in, scored spec out."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import yaml

from loopforge.compact import compact_pipeline_report, compact_spec, dumps_compact_json
from loopforge.intent import compile_intent
from loopforge.validate import validate_spec

from loopctl.agent_cmds import _compile_for_agent
from loopctl.scoring.structural import score_spec_file


def run_quick(args: argparse.Namespace) -> int:
    try:
        if args.library or args.patterns or args.forks:
            from loopforge.combine import combine_loops, save_combined_spec

            library = [x.strip() for x in args.library.split(",")] if args.library else None
            patterns = [p.strip() for p in args.patterns.split(",")] if args.patterns else None
            forks = [f.strip() for f in args.forks.split(",")] if args.forks else None
            loop_name = args.name or "quick-combined"
            spec, meta = combine_loops(
                loop_name,
                args.intent,
                recipe_id=args.recipe,
                patterns=patterns,
                forks=forks,
                library_names=library,
                mode=args.mode,
                flatten=not args.no_flatten,
                compact=True,
                max_tokens=args.max_tokens,
            )
            meta["method"] = meta.get("method") or "combine"
        elif args.recipe:
            from loopforge.mix import mix_spec

            loop_name = args.name or args.recipe
            spec, meta = mix_spec(
                loop_name=loop_name,
                objective=args.intent,
                recipe_id=args.recipe,
                flatten=not args.no_flatten,
            )
            meta["method"] = "mix"
            meta["recipe"] = args.recipe
            preset = None
        elif args.agent:
            spec, meta, preset = _compile_for_agent(args.intent, args.agent, loop_name=args.name)
        else:
            spec, meta = compile_intent(args.intent, loop_name=args.name)
            preset = None
    except (KeyError, FileNotFoundError, ValueError) as exc:
        print(dumps_compact_json({"ok": False, "error": str(exc)}))
        return 1

    lss_version = "1.1" if spec.get("composition") else "1.0"
    errors = validate_spec(spec, lss_version=lss_version)
    if errors:
        print(dumps_compact_json({"ok": False, "errors": errors[:3]}))
        return 1

    out = Path(args.output) if args.output else Path(tempfile.gettempdir()) / "loop-quick.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.recipe or args.library or args.patterns or args.forks:
        from loopforge.mix import save_mixed_spec

        save_mixed_spec(spec, out, validate=False, compact=True)
    else:
        with out.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(compact_spec(spec), fh, sort_keys=False, default_flow_style=True, width=120)

    report: dict = {
        "valid": True,
        "intent": args.intent,
        "spec_path": str(out),
        "pattern": meta.get("pattern"),
        "method": meta.get("method"),
        "lss_version": lss_version,
    }
    if preset:
        report["agent"] = preset.key
        report["bench_suite"] = preset.bench_suite
        report["bench_task"] = preset.bench_task
        report["bench_cmd"] = (
            f"loopctl bench suite {preset.bench_suite} --spec {out} --seeds 0,1,2,3,4 -o results.json"
        )
    elif args.task:
        report["bench_task"] = args.task
        report["bench_cmd"] = f"loopctl bench run --task {args.task} --spec {out} --seeds 0,1,2,3,4 -o results.json"
    elif args.recipe or args.library or args.patterns or args.forks:
        from loopforge.mix import load_recipe

        suite = None
        if args.recipe:
            try:
                suite = load_recipe(args.recipe).get("default_suite")
            except KeyError:
                pass
        suite = suite or meta.get("default_suite")
        if suite:
            report["suite"] = suite
            report["bench_cmd"] = (
                f"loopctl bench suite {suite} --spec {out} --seeds 0,1,2,3,4 -o results.json"
            )

    if not args.skip_score:
        scored = score_spec_file(out)
        report["structural_les"] = scored
        les = scored.get("les") or scored.get("composite")
        if les is not None:
            report["les"] = round(float(les), 1)

    if args.run_loopgym:
        try:
            import loopgym as lg
        except ImportError:
            print(dumps_compact_json({"ok": False, "error": "loopgym not installed"}))
            return 1
        env_id = args.env or "loopbench/code-repair-v1"
        task_id = args.env_task or "cr-001"
        env = lg.make(env_id)
        trace_path = Path(args.trace) if args.trace else out.with_suffix(".trace.json")
        try:
            episode = env.run_episode(task_id=task_id, seed=42, trace_path=str(trace_path))
        except TypeError:
            episode = env.run_episode(task_id=task_id, seed=42)
        report["loopgym"] = {"success": episode.get("success"), "env": env_id}

    from loopforge.compact import estimate_tokens

    report["estimated_tokens"] = estimate_tokens(spec)
    if meta.get("token_budget"):
        report["token_budget"] = meta["token_budget"]

    payload = compact_pipeline_report(report) if args.compact else report
    print(dumps_compact_json(payload))
    return 0


def add_quick_parser(sub: argparse._SubParsersAction) -> None:
    q = sub.add_parser(
        "quick",
        help="One-liner: intent → compact YAML + LES JSON (token-efficient)",
    )
    q.add_argument("intent", help="Natural language loop objective")
    q.add_argument("--agent", help="Agent preset (langgraph, crewai, react, …)")
    q.add_argument("--recipe", help="Mix recipe (dev-agent, swarm-review, …)")
    q.add_argument("--library", help="Comma-separated loop-library names to combine")
    q.add_argument("--patterns", help="Comma-separated patterns to combine")
    q.add_argument("--forks", help="Comma-separated library forks to combine")
    q.add_argument("--mode", choices=["sequential", "parallel", "nested"], default="sequential")
    q.add_argument("--no-flatten", action="store_true", help="Keep LSS 1.1 child refs (more tokens)")
    q.add_argument("--max-tokens", type=int, help="Cap estimated spec tokens via progressive compact")
    q.add_argument("--name", help="loop_name override")
    q.add_argument("-o", "--output", help="Write spec YAML here")
    q.add_argument("--task", help="LoopBench task id for bench_cmd hint")
    q.add_argument("--skip-score", action="store_true")
    q.add_argument("--run-loopgym", action="store_true")
    q.add_argument("--env", help="LoopGym env id when --run-loopgym")
    q.add_argument("--env-task", help="LoopGym task instance id")
    q.add_argument("--trace", type=Path)
    q.add_argument("--compact", action="store_true", default=True)
    q.set_defaults(func=run_quick)
