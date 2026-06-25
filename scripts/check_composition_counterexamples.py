#!/usr/bin/env python3
"""Assert LE-OP-10 counterexample fixtures emit expected composition warnings."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.composition_validator import load_yaml, validate_composition  # noqa: E402

FIXTURES = ROOT / "standards" / "examples" / "composition-counterexamples"

EXPECTATIONS: dict[str, list[str]] = {
    "parallel-first-wins.yaml": ["first_wins"],
    "sequential-no-adapters.yaml": ["adapter"],
    "nested-no-adapters.yaml": ["nested composition without adapters"],
}


def main() -> int:
    failed = 0
    for name, needles in EXPECTATIONS.items():
        path = FIXTURES / name
        if not path.exists():
            print(f"MISSING: {path}", file=sys.stderr)
            failed += 1
            continue
        spec = load_yaml(path)
        errors, warnings = validate_composition(path, spec)
        if errors:
            print(f"FAIL {name}: unexpected errors: {errors}", file=sys.stderr)
            failed += 1
            continue
        blob = " ".join(warnings).lower()
        for needle in needles:
            if needle.lower() not in blob:
                print(
                    f"FAIL {name}: expected warning containing {needle!r}, got: {warnings}",
                    file=sys.stderr,
                )
                failed += 1
                break
        else:
            print(f"OK: {name} ({len(warnings)} warning(s))")
    if failed:
        print(f"\nFAILED: {failed} fixture(s)", file=sys.stderr)
        return 1
    print(f"OK: {len(EXPECTATIONS)} counterexample fixture(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
