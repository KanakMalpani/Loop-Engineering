"""Original cr-001..cr-003 bytes stay pinned by fixtures/FROZEN.sha256."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
MANIFEST = FIXTURES / "FROZEN.sha256"
_PINNED = re.compile(r"^(?:cr-00[1-3]/.+|_reference/cr-00[1-3]\.py)$")


def _excluded(path: Path) -> bool:
    rel = path.relative_to(FIXTURES)
    return "__pycache__" in rel.parts or path.suffix == ".pyc"


def _pinned_files() -> list[str]:
    rels = []
    for path in FIXTURES.rglob("*"):
        if not path.is_file() or _excluded(path):
            continue
        rel = path.relative_to(FIXTURES).as_posix()
        if _PINNED.match(rel):
            rels.append(rel)
    return sorted(rels)


def _parse(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        rows.append((digest, rel))
    return rows


def test_frozen_entries_match_original_fixtures() -> None:
    text = MANIFEST.read_text(encoding="utf-8")
    rows = _parse(text)
    assert [rel for _digest, rel in rows] == _pinned_files()
    for digest, rel in rows:
        data = (FIXTURES / rel).read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest
    assert text == "".join(f"{digest}  {rel}\n" for digest, rel in rows)


def test_original_fixture_files_are_listed() -> None:
    listed = {rel for _digest, rel in _parse(MANIFEST.read_text(encoding="utf-8"))}
    assert listed == set(_pinned_files())
