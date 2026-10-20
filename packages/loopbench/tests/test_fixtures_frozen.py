"""Fixture bytes are pinned by packages/loopbench/fixtures/FROZEN.sha256."""

from __future__ import annotations

import hashlib
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
MANIFEST = FIXTURES / "FROZEN.sha256"


def _excluded(path: Path) -> bool:
    rel = path.relative_to(FIXTURES)
    if rel.as_posix() == "FROZEN.sha256":
        return True
    if "__pycache__" in rel.parts or path.suffix == ".pyc":
        return True
    return False


def _discovered() -> list[str]:
    rels = [
        path.relative_to(FIXTURES).as_posix()
        for path in FIXTURES.rglob("*")
        if path.is_file() and not _excluded(path)
    ]
    return sorted(rels)


def _parse(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        rows.append((digest, rel))
    return rows


def test_fixture_hashes_match_manifest_exactly() -> None:
    text = MANIFEST.read_text(encoding="utf-8")
    rows = _parse(text)
    assert [rel for _digest, rel in rows] == _discovered()
    for digest, rel in rows:
        data = (FIXTURES / rel).read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest
    assert text == "".join(f"{digest}  {rel}\n" for digest, rel in rows)


def test_no_unlisted_fixture_file() -> None:
    listed = {rel for _digest, rel in _parse(MANIFEST.read_text(encoding="utf-8"))}
    unlisted = [rel for rel in _discovered() if rel not in listed]
    assert unlisted == []
