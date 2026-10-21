"""Write fixtures/FROZEN-2.sha256 for every current fixture file."""

from __future__ import annotations

import hashlib
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
OUT = FIXTURES / "FROZEN-2.sha256"


def _excluded(path: Path) -> bool:
    rel = path.relative_to(FIXTURES)
    frozen = path.name.startswith("FROZEN") and path.suffix == ".sha256"
    cache = "__pycache__" in rel.parts or path.suffix == ".pyc"
    return frozen or cache


def main() -> None:
    rels = sorted(
        path.relative_to(FIXTURES).as_posix()
        for path in FIXTURES.rglob("*")
        if path.is_file() and not _excluded(path)
    )
    lines = []
    for rel in rels:
        digest = hashlib.sha256((FIXTURES / rel).read_bytes()).hexdigest()
        lines.append(f"{digest}  {rel}\n")
    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"wrote {len(lines)} entries to {OUT}")


if __name__ == "__main__":
    main()
