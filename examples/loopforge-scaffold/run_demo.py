#!/usr/bin/env python3
"""LoopForge demo — scaffold all patterns and validate against LSS 1.0."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from loopforge import LoopBuilder, Pattern  # noqa: E402


def main() -> int:
    out_dir = ROOT / "examples" / "loopforge-scaffold" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    for pattern in Pattern:
        path = out_dir / f"{pattern.value}-demo.yaml"
        (
            LoopBuilder(
                f"{pattern.value}-demo",
                f"Demonstrate the {pattern.value} loop pattern scaffolded by LoopForge",
            )
            .from_pattern(pattern)
            .with_quality_threshold(0.85)
            .save(path)
        )
        print(f"Wrote and validated {path.relative_to(ROOT)}")

    print(f"OK — {len(Pattern)} patterns scaffolded")

    try:
        from loopforge.library import fork_spec
        from loopforge.level_hint import apply_level_hint
        import yaml

        fork_path = out_dir / "fork-demo.yaml"
        spec = fork_spec("research-agent", "fork-demo")
        apply_level_hint(spec, "research-agent")
        with fork_path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(spec, fh, sort_keys=False, allow_unicode=True, width=100)
        print(f"Wrote fork demo {fork_path.relative_to(ROOT)}")
    except FileNotFoundError as exc:
        print(f"Skip fork demo: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
