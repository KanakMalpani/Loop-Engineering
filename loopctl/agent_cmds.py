"""Agent harness commands — map any popular agent to LSS in one step."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from loopforge.agents import enrich_intent, list_agents, resolve_agent
from loopforge.compact import compact_spec, dump_compact_yaml, dumps_compact_json
from loopforge.intent import compile_intent
from loopforge.validate import validate_spec

from loopctl.scoring.structural import score_spec_file


def _compile_for_agent(intent: str, agent: str, *, loop_name: str | None = None):
    preset = resolve_agent(agent)
    enriched = enrich_intent(intent, preset)
    if preset.compose and preset.compose not in enriched.lower():
        enriched = f"{preset.compose} composition: {enriched}"
    spec, meta = compile_intent(enriched, loop_name=loop_name)
    meta["agent"] = preset.key
    meta["bench_task"] = preset.bench_task
    if preset.export:
        meta["export_target"] = preset.export
    return spec, meta, preset


def cmd_agent_list(_: argparse.Namespace) -> int:
    print(dumps_compact_json({"agents": list_agents()}))
    return 0


def cmd_agent_map(args: argparse.Namespace) -> int:
    try:
        spec, meta, preset = _compile_for_agent(args.intent, args.harness, loop_name=args.name)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    lss_version = "1.1" if spec.get("composition") else "1.0"
    errors = validate_spec(spec, lss_version=lss_version)
    if errors:
        for e in errors[:5]:
            print(e, file=sys.stderr)
        return 1

    out = Path(args.output) if args.output else Path(f"{preset.key}-mapped.yaml")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = compact_spec(spec) if args.compact else spec
    with out.open("w", encoding="utf-8") as fh:
        if args.compact:
            fh.write(dump_compact_yaml(payload))
        else:
            yaml.safe_dump(payload, fh, sort_keys=False, default_flow_style=False)

    report: dict = {
        "agent": preset.key,
        "pattern": meta.get("pattern"),
        "method": meta.get("method"),
        "spec_path": str(out),
        "bench_task": preset.bench_task,
        "bench_suite": preset.bench_suite,
        "default_recipe": preset.default_recipe,
        "bench_cmd": f'loopctl bench suite {preset.bench_suite} --spec "{out}" --seeds 0,1,2,3,4 -o results.json',
        "export": preset.export,
        "pip_extra": preset.pip_extra,
        "valid": True,
    }

    if not args.skip_score:
        try:
            scored = score_spec_file(out)
            les = scored.get("les") or scored.get("composite")
            report["les"] = round(float(les), 1) if les is not None else None
        except Exception as exc:
            print(f"Score failed: {exc}", file=sys.stderr)
            return 1

    if args.export and preset.export:
        from loopforge.export import export_stub

        export_dir = Path(args.export_dir or out.parent / f"export-{preset.export}")
        export_stub(out, export_dir, preset.export)
        report["export_dir"] = str(export_dir)

    if args.json or args.compact:
        print(dumps_compact_json(report))
    else:
        print(f"Mapped {preset.label} → {out}")
        print(f"  bench: {report['bench_cmd']}")
        if report.get("les") is not None:
            print(f"  LES: {report['les']}")
    return 0


def add_agent_parsers(sub: argparse._SubParsersAction) -> None:
    agent = sub.add_parser("agent", help="Map popular AI agent harnesses to LSS")
    agent_sub = agent.add_subparsers(dest="agent_cmd", required=True)

    lst = agent_sub.add_parser("list", help="List supported agent presets (JSON)")
    lst.set_defaults(func=cmd_agent_list)

    mp = agent_sub.add_parser("map", help="Intent + harness → LSS YAML + bench command")
    mp.add_argument("--harness", required=True, help="Agent key (langgraph, crewai, react, …)")
    mp.add_argument("--intent", required=True, help="What the loop should accomplish")
    mp.add_argument("--name", help="loop_name override")
    mp.add_argument("-o", "--output", help="Output YAML path")
    mp.add_argument("--export", action="store_true", help="Also export runnable stub")
    mp.add_argument("--export-dir", help="Export directory")
    mp.add_argument("--skip-score", action="store_true")
    mp.add_argument("--compact", action="store_true", help="Compact YAML + JSON output")
    mp.add_argument("--json", action="store_true")
    mp.set_defaults(func=cmd_agent_map)
