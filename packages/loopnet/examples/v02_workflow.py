#!/usr/bin/env python3
"""End-to-end workflow: LoopNet v0.2 → LoopGym replay → LoopBench score.

Requires: pip install loopgym loopbench
Optional: pip install datasets  (load from Hugging Face Hub)

Run from a clone with sibling repos, or set LOOPNET_RECORDS_PATH and LOOPBENCH_SPEC.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def resolve_corpus_path() -> Path:
    env_path = os.environ.get("LOOPNET_RECORDS_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
        raise FileNotFoundError(f"LOOPNET_RECORDS_PATH not found: {path}")

    local = ROOT / "data" / "v0.2" / "records.jsonl"
    if local.exists():
        return local

    raise FileNotFoundError(
        "No LoopNet corpus found. Clone loopnet or set LOOPNET_RECORDS_PATH."
    )


def load_records_from_hf() -> list[dict] | None:
    try:
        from datasets import load_dataset
    except ImportError:
        return None

    ds = load_dataset("KanakMalpani/loopnet-v0.2", split="train")
    return [dict(row) for row in ds]


def load_records_local(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def pick_captured_record(records: list[dict]) -> dict:
    for record in records:
        tags = (record.get("metadata") or {}).get("tags") or []
        if "captured" in tags or record.get("source") == "case_study":
            return record
    raise ValueError("No captured records in corpus (expected v0.2 mix).")


def resolve_loopbench_spec() -> Path:
    env_path = os.environ.get("LOOPBENCH_SPEC")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
        raise FileNotFoundError(f"LOOPBENCH_SPEC not found: {path}")

    sibling = ROOT.parent / "06-loopbench" / "submissions" / "examples" / "spec-fast-loop.yaml"
    if sibling.exists():
        return sibling

    raise FileNotFoundError(
        "LoopBench spec not found. Clone LoopBench sibling or set LOOPBENCH_SPEC."
    )


def main() -> int:
    print("LoopNet v0.2 end-to-end tutorial\n")

    # --- 1. Load corpus ---
    print("1) Load LoopNet v0.2 corpus")
    hf_records = load_records_from_hf()
    if hf_records is not None:
        records = hf_records
        corpus_label = "Hugging Face: KanakMalpani/loopnet-v0.2"
    else:
        corpus_path = resolve_corpus_path()
        records = load_records_local(corpus_path)
        corpus_label = str(corpus_path)

    print(f"   source: {corpus_label}")
    print(f"   records: {len(records)}")

    record = pick_captured_record(records)
    record_id = record["record_id"]
    les_stored = (record.get("les_observed") or {}).get("les_normalized")
    env_id = (record.get("loop_spec") or {}).get("extensions", {}).get("env_id", "?")
    task_id = (record.get("loop_spec") or {}).get("extensions", {}).get("task_id", "?")
    print(f"   picked captured record: {record_id}")
    print(f"   env={env_id} task={task_id} outcome={record.get('outcome')} les={les_stored}")

    # --- 2. Replay in LoopGym (zero API cost) ---
    print("\n2) Replay trajectory in LoopGym (ReplayEnv)")
    import loopgym as lg

    if hf_records is None:
        env = lg.make("replay/loopnet-v1", records_path=resolve_corpus_path())
    else:
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as tmp:
            for row in records:
                tmp.write(json.dumps(row) + "\n")
            tmp_path = Path(tmp.name)
        env = lg.make("replay/loopnet-v1", records_path=tmp_path)

    replay = env.run_episode(record_id=record_id)
    print(f"   replay steps: {replay['steps']}")
    print(f"   final quality: {replay['quality_score']:.3f}")
    print(f"   success: {replay['success']}")
    print(f"   stored les_observed: {replay.get('les_observed')}")

    # --- 3. Score fresh SimEnv run with LoopBench ---
    print("\n3) Run LoopBench on the same task (SimEnv, mock LLM)")
    try:
        from loopbench.runner import run_task

        spec_path = resolve_loopbench_spec()
        bench = run_task("LB-CR-1", spec_path, seeds=[0], instances=[task_id], backend="sim")
        agg = bench["aggregate"]
        print(f"   spec: {spec_path.name}")
        print(f"   les_observed: {agg['les_observed']:.4f} (display {agg['les_display']})")
        print(f"   success_at_k: {agg['success_at_k']}")
    except FileNotFoundError as exc:
        print(f"   skipped: {exc}")
        print("   (install loopbench and clone LoopBench, or set LOOPBENCH_SPEC)")

    print("\nDone. Captured trajectories replay without API spend; LoopBench scores live runs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
