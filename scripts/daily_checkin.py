#!/usr/bin/env python3
"""Daily Loop Engineering health check — run locally or in CI."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_step(name: str, cmd: list[str]) -> tuple[bool, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    combined = "\n".join(x for x in (out, err) if x)
    ok = result.returncode == 0
    return ok, combined or ("OK" if ok else f"exit {result.returncode}")


def count_specs() -> tuple[int, int]:
    lib = ROOT / "loop-library"
    atomic = len(list(lib.glob("*.yaml")))
    composed = len(list((lib / "compositions").glob("*.yaml"))) if (lib / "compositions").is_dir() else 0
    return atomic, composed


def build_report(results: list[tuple[str, bool, str]], when: datetime) -> str:
    atomic, composed = count_specs()
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    all_ok = passed == total
    status = "GREEN" if all_ok else "RED"

    lines = [
        f"# Daily check-in — {when.strftime('%Y-%m-%d')} UTC",
        "",
        f"**Status:** {status} ({passed}/{total} checks passed)",
        f"**Loop library:** {atomic} atomic + {composed} composed specs",
        "",
        "## Checks",
        "",
        "| Check | Result | Detail |",
        "|-------|--------|--------|",
    ]
    for name, ok, detail in results:
        mark = "pass" if ok else "**FAIL**"
        snippet = detail.replace("|", "\\|").replace("\n", " ")[:120]
        lines.append(f"| {name} | {mark} | `{snippet}` |")

    lines.extend(
        [
            "",
            "## Reproduce locally",
            "",
            "```bash",
            "python scripts/daily_checkin.py",
            "```",
            "",
            f"_Generated at {when.isoformat()}_",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Loop Engineering daily health check")
    parser.add_argument(
        "--output",
        type=Path,
        help="Write markdown report to this path (e.g. docs/checkins/latest.md)",
    )
    parser.add_argument(
        "--archive",
        type=Path,
        help="Also write dated copy (e.g. docs/checkins/archive)",
    )
    args = parser.parse_args()

    py = sys.executable
    checks: list[tuple[str, list[str]]] = [
        ("validate_loop_library", [py, "scripts/validate_loop_library.py"]),
        ("reflection_loop_smoke", [py, "examples/reflection-loop/run.py"]),
        (
            "composed_nested_smoke",
            [py, "examples/compose-loop/run.py", "loop-library/compositions/code-debug-repair.yaml"],
        ),
        ("composition_validator", [py, "tools/composition_validator.py", "--library"]),
    ]

    results: list[tuple[str, bool, str]] = []
    for name, cmd in checks:
        ok, detail = run_step(name, cmd)
        results.append((name, ok, detail))
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {name}")
        if not ok:
            print(detail[:500])

    when = datetime.now(timezone.utc)
    report = build_report(results, when)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Wrote {args.output}")

    if args.archive:
        args.archive.mkdir(parents=True, exist_ok=True)
        dated = args.archive / f"{when.strftime('%Y-%m-%d')}.md"
        dated.write_text(report, encoding="utf-8")
        print(f"Wrote {dated}")

    if not args.output and not args.archive:
        print()
        print(report)

    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
