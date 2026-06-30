"""Optional loopmath integration for proof-carrying compose certificates."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Literal


def _ensure_loopmath_path() -> None:
    env = os.environ.get("LOOP_MATH_PATH")
    if env:
        p = Path(env)
        if p.is_dir() and str(p) not in sys.path:
            sys.path.insert(0, str(p))
        return
    # Dev layout: 03-loop-math/loopmath next to 01-loop-engineering
    here = Path(__file__).resolve().parents[2]
    for candidate in (
        here.parent / "03-loop-math" / "loopmath",
        here / "03-loop-math" / "loopmath",
    ):
        if (candidate / "loopmath" / "algebra.py").is_file() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
            return


def math_available() -> bool:
    _ensure_loopmath_path()
    try:
        from loopmath.algebra import check_compose_valid  # noqa: F401

        return True
    except ImportError:
        return False


def compose_certificate(
    spec_a: dict[str, Any],
    spec_b: dict[str, Any],
    *,
    mode: Literal["sequential", "parallel"] = "sequential",
) -> dict[str, Any] | None:
    """Return PCLS certificate when loopmath is installed; else None."""
    _ensure_loopmath_path()
    try:
        from loopmath.algebra import check_compose_valid
    except ImportError:
        return None

    cert = check_compose_valid(spec_a, spec_b, mode=mode)
    return {
        "valid": cert.get("valid"),
        "issues": cert.get("issues") or [],
        "warnings": cert.get("warnings") or [],
        "theory_ref": cert.get("theory_ref") or [],
        "source": "loopmath",
    }


def attach_compose_metadata(
    composed: dict[str, Any],
    child_specs: list[dict[str, Any]],
    *,
    mode: Literal["sequential", "parallel"],
) -> dict[str, Any]:
    """Fold pairwise certificates into composed spec metadata when loopmath present."""
    if len(child_specs) < 2 or not math_available():
        return composed

    certs: list[dict[str, Any]] = []
    if mode == "sequential":
        acc = child_specs[0]
        for nxt in child_specs[1:]:
            c = compose_certificate(acc, nxt, mode="sequential")
            if c:
                certs.append(c)
            acc = composed
    else:
        for i in range(0, len(child_specs), 2):
            if i + 1 < len(child_specs):
                c = compose_certificate(child_specs[i], child_specs[i + 1], mode="parallel")
                if c:
                    certs.append(c)

    if not certs:
        return composed

    meta = composed.setdefault("metadata", {})
    if isinstance(meta, dict):
        meta["compose_certificates"] = certs
        meta["compose_valid"] = all(c.get("valid") for c in certs)
        meta["proof_source"] = "loopmath"
    return composed
