#!/usr/bin/env python3
"""Generate Mermaid flowchart diagrams from LSS YAML specifications."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


def load_spec(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def _slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", str(text))[:40]


def _worker_label(worker: dict[str, Any]) -> str:
    wid = worker.get("id") or worker.get("role", "worker")
    model = worker.get("model")
    if isinstance(model, dict):
        model_name = model.get("name", "")
    else:
        model_name = str(model) if model else ""
    return f"{wid}" + (f"\\n({model_name})" if model_name else "")


def _slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", str(text))[:40]


def _resolve_ref(spec_path: Path, ref: str) -> Path:
    p = Path(ref)
    return p if p.is_absolute() else (spec_path.parent / p).resolve()


def _composition_mermaid(spec: dict[str, Any], spec_path: Path | None) -> list[str] | None:
    comp = spec.get("composition")
    if not comp or not spec_path:
        return None
    children = comp.get("children") or []
    if not children:
        return None

    comp_type = comp.get("type", "sequential")
    merge = comp.get("merge") or {}
    lines: list[str] = []
    branch_ids: list[str] = []

    if comp_type == "parallel":
        lines.append("    subgraph ParallelBranches[Parallel branches]")
        for child in children:
            cid = child.get("id", "branch")
            ref = child.get("ref", "")
            child_path = _resolve_ref(spec_path, ref) if ref else None
            child_name = child_path.stem if child_path and child_path.exists() else ref
            node = f"B_{_slug(cid)}"
            branch_ids.append(node)
            lens = (child.get("lens") or child.get("role") or cid)[:40].replace('"', "'")
            lines.append(f"        {node}[{cid}\\n{child_name}]")
        lines.append("    end")
    else:
        prev = None
        for child in children:
            cid = child.get("id", "stage")
            node = f"B_{_slug(cid)}"
            branch_ids.append(node)
            lines.append(f"    {node}[{cid}]")
            if prev:
                lines.append(f"    {prev} --> {node}")
            prev = node

    synth = merge.get("synthesizer") or "workers.orchestrator"
    synth_id = "ORCH"
    lines.append(f"    {synth_id}[Merge: {merge.get('strategy', 'synthesizer')}\\n{synth}]")
    for bid in branch_ids:
        lines.append(f"    {bid} --> {synth_id}")

    if merge.get("preserve_dissent"):
        lines.append(f"    {synth_id} -.->|dissent preserved| ParallelBranches")

    return lines


def generate_mermaid(spec: dict[str, Any], spec_path: Path | None = None) -> str:
    loop_name = spec.get("loop_name", "loop")
    level = spec.get("taxonomy_level", 2)
    workers = spec.get("workers") or []
    evaluators = spec.get("evaluators") or []
    feedback = spec.get("feedback_channels") or []
    termination = spec.get("termination_conditions")

    objective = str(spec.get("objective", "objective")).replace("\n", " ")[:50]
    lines = [
        "---",
        f"title: {loop_name} (L{level})",
        "---",
        "flowchart TB",
        f"    START([Start: {objective}])",
    ]

    comp_lines = _composition_mermaid(spec, spec_path)
    if comp_lines:
        comp_type = (spec.get("composition") or {}).get("type", "sequential")
        if comp_type == "parallel":
            lines.append("    START --> ParallelBranches")
        else:
            children = (spec.get("composition") or {}).get("children") or []
            if children:
                first = f"B_{_slug(children[0].get('id', 'stage'))}"
                lines.append(f"    START --> {first}")
        lines.extend(comp_lines)
        prev = "ORCH"
    else:
        prev = "START"
        for i, worker in enumerate(workers):
            wid = worker.get("id") or f"worker_{i}"
            node_id = f"W_{_slug(wid)}"
            lines.append(f"    {node_id}[{_worker_label(worker)}]")
            lines.append(f"    {prev} --> {node_id}")
            prev = node_id

    for i, ev in enumerate(evaluators):
        eid = ev.get("id") or ev.get("type") or f"eval_{i}"
        node_id = f"E_{_slug(eid)}"
        ev_type = ev.get("type", "evaluator")
        rubric = ev.get("rubric") or {}
        threshold = rubric.get("pass_threshold") or ev.get("threshold")
        label = str(eid) + (f"\\n>={threshold}" if threshold is not None else f"\\n({ev_type})")
        lines.append(f"    {node_id}{{{label}}}")
        lines.append(f"    {prev} --> {node_id}")
        prev = node_id

    if feedback:
        lines.append("    subgraph Feedback")
        for i, ch in enumerate(feedback):
            src = ch.get("source") or ch.get("from", "src")
            dst = ch.get("destination") or ch.get("to", "dst")
            fmt = ch.get("format") or ch.get("signal", "feedback")
            lines.append(f"        FB{i}[{src} -> {dst}: {fmt}]")
        lines.append("    end")
        lines.append(f"    {prev} --> FB0")
        prev = "FB0"

    opt = spec.get("optimization_strategy") or {}
    if opt.get("type"):
        opt_id = "OPT"
        lines.append(f"    {opt_id}[Optimize: {opt['type']}]")
        lines.append(f"    {prev} --> {opt_id}")
        prev = opt_id

    term_labels: list[str] = []
    if isinstance(termination, dict):
        for success in termination.get("success") or []:
            term_labels.append(
                f"{success.get('metric')} {success.get('operator')} {success.get('value')}"
            )
        for failure in termination.get("failure") or []:
            val = failure.get("value")
            term_labels.append(
                f"{failure.get('type')}" + (f"={val}" if val is not None else "")
            )
    elif isinstance(termination, list):
        for cond in termination:
            ctype = cond.get("type", "condition")
            val = cond.get("value") or cond.get("threshold")
            term_labels.append(f"{ctype}" + (f"={val}" if val is not None else ""))

    term_text = " | ".join(term_labels) if term_labels else "done"
    lines.append(f"    TERM([Terminate: {term_text}])")
    lines.append(f"    {prev} --> TERM")

    if level >= 2 and workers:
        first_id = workers[0].get("id") or "worker_0"
        first_worker = f"W_{_slug(first_id)}"
        lines.append(f"    {prev} -.->|not done| {first_worker}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a Mermaid flowchart from an LSS YAML specification",
    )
    parser.add_argument("spec", type=Path, help="Path to LSS YAML file")
    parser.add_argument(
        "-o", "--output", type=Path, help="Write Mermaid to file (default: stdout)"
    )
    args = parser.parse_args()

    if not args.spec.exists():
        print(f"Error: file not found: {args.spec}", file=sys.stderr)
        return 2

    try:
        spec = load_spec(args.spec)
        diagram = generate_mermaid(spec, args.spec.resolve())
    except (yaml.YAMLError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.output:
        args.output.write_text(diagram + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(diagram)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
