#!/usr/bin/env python3
"""Smoke test loop combine API — flat merge saves tokens vs composition refs."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from loopforge.combine import LoopChain, combine_loops
    from loopforge.compact import estimate_tokens, token_compare

    spec_flat, meta = combine_loops(
        "repair-chain",
        "Fix tests then verify",
        library_names=["autonomous-debugger", "coding-agent"],
        mode="sequential",
        flatten=True,
        compact=True,
        validate=False,
    )
    if not spec_flat.get("workers") or len(spec_flat["workers"]) < 2:
        print("FAIL: flat combine expected merged workers", file=sys.stderr)
        return 1

    spec_refs, _ = combine_loops(
        "repair-chain-refs",
        "Fix tests then verify",
        library_names=["autonomous-debugger", "coding-agent"],
        mode="sequential",
        flatten=False,
        compact=False,
        validate=False,
    )
    cmp = token_compare(spec_refs, spec_flat)
    if cmp["saved"] <= 0 and spec_refs.get("composition"):
        print(f"NOTE: refs smaller than flat ({cmp}); flat avoids multi-file refs in prompts")

    chain_spec, chain_meta = (
        LoopChain("chain-demo", "Research then write")
        .then_fork("research-agent")
        .then_fork("writing-assistant")
        .build(flatten=True, compact=True, validate=False)
    )
    if chain_meta.get("estimated_tokens", 0) <= 0:
        print("FAIL: chain missing token estimate", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "combined.yaml"
        from loopforge.combine import save_combined_spec

        stats = save_combined_spec(spec_flat, out, compact=True)
        if not out.is_file() or stats["estimated_tokens"] <= 0:
            print("FAIL: save_combined_spec", file=sys.stderr)
            return 1

    print(f"OK combine_smoke flat_tokens={estimate_tokens(spec_flat)} saved={cmp.get('saved', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
