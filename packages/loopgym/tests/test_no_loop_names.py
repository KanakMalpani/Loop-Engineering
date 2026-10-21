"""Generic runner code must not name a validity loop."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOOPS = ROOT / "benchmarks" / "loopbench-validity" / "loops"
FRAGMENTS = ("wrong-role", "no-feedback", "bad-", "good-")


def _scanned_files() -> list[Path]:
    files = sorted((ROOT / "packages" / "loopgym" / "loopgym").rglob("*.py"))
    bench = ROOT / "benchmarks" / "loopbench-validity"
    files.append(bench / "cursor_llm.py")
    files.append(bench / "run_full.py")
    return files


def test_no_loop_names_in_generic_code():
    stems = sorted(path.stem for path in LOOPS.glob("*.yaml"))
    assert stems, "validity loop specs are missing"
    needles = stems + list(FRAGMENTS)
    offenders: list[str] = []
    for path in _scanned_files():
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle in text:
                offenders.append(f"{path.relative_to(ROOT)}: {needle}")
    assert not offenders, "loop names leaked into generic code:\n" + "\n".join(offenders)
