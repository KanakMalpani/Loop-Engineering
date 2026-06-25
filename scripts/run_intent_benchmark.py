#!/usr/bin/env python3
"""Run LE-OP-15 intent→LSS benchmark and write report JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loopforge.intent import COMPOSE_MODES, classify_intent, compile_intent  # noqa: E402
from loopforge.validate import validate_spec  # noqa: E402

MANIFEST = ROOT / "benchmarks" / "intent-to-lss" / "manifest.json"
OUTPUT = ROOT / "benchmarks" / "intent-to-lss" / "results-v0.5.json"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    version = manifest.get("version", "0.5")
    intents = manifest["intents"]
    results = []
    pattern_ok = 0
    valid_ok = 0

    for item in intents:
        text = item["text"]
        expected = item["expected_pattern"]
        predicted, _fork = classify_intent(text)
        spec, meta = compile_intent(text, use_fork=True)
        lss_version = "1.1" if spec.get("composition") else "1.0"
        errors = validate_spec(spec, lss_version=lss_version)
        valid = len(errors) == 0
        pattern_match = predicted == expected
        if pattern_match:
            pattern_ok += 1
        if valid:
            valid_ok += 1
        results.append(
            {
                "id": item["id"],
                "expected_pattern": expected,
                "predicted_pattern": predicted,
                "pattern_match": pattern_match,
                "valid_lss": valid,
                "method": meta["method"],
                "fork_source": meta.get("fork_source"),
                "loop_name": spec.get("loop_name"),
                "lss_version": lss_version,
                "errors": errors[:3],
            }
        )

    n = len(intents)
    compose_n = sum(1 for i in intents if i["expected_pattern"] in COMPOSE_MODES)
    report = {
        "version": version,
        "problem": "LE-OP-15",
        "n_intents": n,
        "n_composition_intents": compose_n,
        "pattern_accuracy": round(pattern_ok / n, 4),
        "validation_pass_rate": round(valid_ok / n, 4),
        "meets_v05_pattern_target": pattern_ok / n >= 0.80,
        "meets_v05_valid_target": valid_ok / n >= 0.95,
        "results": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Pattern accuracy: {report['pattern_accuracy']:.1%}")
    print(f"Validation pass:  {report['validation_pass_rate']:.1%}")
    print(f"Composition intents: {compose_n}")
    print(f"Wrote {OUTPUT}")
    return 0 if report["meets_v05_pattern_target"] and report["meets_v05_valid_target"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
