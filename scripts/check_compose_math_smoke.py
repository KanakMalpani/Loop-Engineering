#!/usr/bin/env python3
"""Smoke optional loopmath compose certificates when installed."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from loopforge.compose_math import math_available, compose_certificate
    from loopforge.combine import combine_loops

    if not math_available():
        print("SKIP compose_math_smoke (loopmath not installed; pip install -e ../../03-loop-math/loopmath)")
        return 0

    a, _ = combine_loops("a", "A", library_names=["research-agent"], flatten=True, validate=False)
    b, _ = combine_loops("b", "B", library_names=["coding-agent"], flatten=True, validate=False)
    cert = compose_certificate(a, b, mode="sequential")
    if not cert or cert.get("source") != "loopmath":
        print("FAIL: expected loopmath certificate", file=sys.stderr)
        return 1

    spec, meta = combine_loops(
        "math-chain",
        "Proof-carrying combine",
        library_names=["research-agent", "coding-agent"],
        flatten=True,
        validate=False,
    )
    meta_block = spec.get("metadata") or {}
    if not meta_block.get("compose_certificates"):
        print("WARN: combine metadata missing compose_certificates (optional)")

    print(f"OK compose_math_smoke valid={cert.get('valid')} theory={len(cert.get('theory_ref') or [])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
