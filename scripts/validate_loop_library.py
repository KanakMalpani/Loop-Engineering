#!/usr/bin/env python3
"""Validate loop-library atomic and composed specs. Exit 1 on any failure."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "loop-library"
COMP = LIB / "compositions"
VALIDATOR = ROOT / "tools" / "loop_validator.py"
COMP_VALIDATOR = ROOT / "tools" / "composition_validator.py"

sys.path.insert(0, str(ROOT))
from tools.level_recommender import LevelRecommender, load_records  # noqa: E402


def run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = (result.stdout or "") + (result.stderr or "")
    return result.returncode, out


NAME_TO_PATTERN: dict[str, str] = {
    "research-agent": "research-loop",
    "coding-agent": "reflection-loop",
    "autonomous-debugger": "verification-loop",
    "interview-coach": "human-in-the-loop",
    "writing-assistant": "reflection-loop",
    "business-strategy-agent": "multi-agent-coordination",
    "startup-validator": "planning-loop",
    "learning-coach": "reflection-loop",
    "scientific-discovery-agent": "exploration-loop",
}


def spec_pattern(spec: dict, path: Path) -> str:
    meta = spec.get("metadata") or {}
    ext = spec.get("extensions") or {}
    patterns = meta.get("patterns") or ext.get("patterns") or spec.get("patterns")
    if patterns:
        return str(patterns[0] if isinstance(patterns, list) else patterns)
    name = spec.get("loop_name") or path.stem
    return NAME_TO_PATTERN.get(name, "reflection-loop")


def warn_taxonomy_levels(warn: bool) -> list[str]:
    if not warn:
        return []
    warnings: list[str] = []
    try:
        records = load_records()
    except SystemExit:
        return ["level recommender: install datasets (`pip install datasets`)"]
    if not records:
        return ["level recommender: no LoopNet records loaded"]
    model = LevelRecommender()
    split = int(len(records) * 0.8)
    model.fit(records[:split])

    for path in sorted(LIB.glob("*.yaml")):
        spec = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        meta = spec.get("metadata") or {}
        declared = str(meta.get("taxonomy_level", ""))
        if not declared:
            continue
        pattern = spec_pattern(spec, path)
        workers = len(spec.get("workers") or [])
        pred = model.predict(pattern, iter_len=3, workers=max(workers, 1))
        if declared != pred:
            warnings.append(f"{path.name}: metadata.taxonomy_level={declared} vs recommender={pred} (pattern={pattern})")
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-level", action="store_true", help="Warn on taxonomy_level vs LE-OP-11 recommender")
    args = parser.parse_args()

    if not VALIDATOR.exists():
        print(f"Error: validator not found: {VALIDATOR}", file=sys.stderr)
        return 2

    yaml_files = sorted(LIB.glob("*.yaml"))
    comp_files = sorted(COMP.glob("*.yaml")) if COMP.is_dir() else []
    all_files = yaml_files + comp_files

    if not all_files:
        print(f"Error: no YAML files in {LIB}", file=sys.stderr)
        return 2

    failed: list[str] = []
    for path in all_files:
        code, out = run([sys.executable, str(VALIDATOR), str(path)])
        if code != 0:
            failed.append(path.name)
            print(out)

    if COMP_VALIDATOR.exists() and comp_files:
        code, out = run([sys.executable, str(COMP_VALIDATOR), "--library", "--strict"])
        if code != 0:
            failed.append("composition-graph")
            print(out)

    for w in warn_taxonomy_levels(args.warn_level):
        print(f"WARN: {w}")

    if failed:
        print(f"\nFAILED: {len(failed)}/{len(all_files)} specs invalid", file=sys.stderr)
        for name in failed:
            print(f"  - {name}", file=sys.stderr)
        return 1

    n_comp = len(comp_files)
    print(f"OK: {len(yaml_files)} atomic + {n_comp} composed specs valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
