#!/usr/bin/env python3
"""LE-OP-11 v0.1: task→taxonomy level recommender trained on LoopNet v0.2."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.loopnet_fields import iter_bucket, iteration_count, oracle_level, primary_pattern  # noqa: E402

DEFAULT_REPORT = ROOT / "benchmarks" / "results" / "le-op-11-recommender-v0.1.json"


@dataclass
class Record:
    pattern: str
    iter_len: int
    workers: int
    level: str


def load_records() -> list[Record]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit("Install: pip install datasets") from exc

    ds = load_dataset("KanakMalpani/loopnet-v0.2", split="train")
    records: list[Record] = []
    for row in ds:
        row = dict(row)
        workers = int(row.get("metadata.worker_count") or 1)
        records.append(
            Record(
                pattern=primary_pattern(row),
                iter_len=iteration_count(row),
                workers=workers,
                level=oracle_level(row),
            )
        )
    return records


def majority(counter: Counter[str]) -> str:
    if not counter:
        return "2"
    return counter.most_common(1)[0][0]


class LevelRecommender:
    """Pattern + iteration bucket + worker count → taxonomy level."""

    def __init__(self) -> None:
        self.by_pattern_bucket_workers: dict[tuple[str, str, str], Counter[str]] = {}
        self.by_pattern_bucket: dict[tuple[str, str], Counter[str]] = {}
        self.by_pattern: dict[str, Counter[str]] = {}
        self.global_levels: Counter[str] = Counter()

    def fit(self, train: list[Record]) -> None:
        for rec in train:
            bucket = iter_bucket(rec.iter_len)
            worker_tag = "multi" if rec.workers >= 2 else "solo"
            keys = [
                (rec.pattern, bucket, worker_tag),
                (rec.pattern, bucket),
            ]
            for key in keys:
                if len(key) == 3:
                    self.by_pattern_bucket_workers.setdefault(key, Counter())[rec.level] += 1
                else:
                    self.by_pattern_bucket.setdefault(key, Counter())[rec.level] += 1
            self.by_pattern.setdefault(rec.pattern, Counter())[rec.level] += 1
            self.global_levels[rec.level] += 1

    def predict(self, pattern: str, iter_len: int, workers: int = 1) -> str:
        bucket = iter_bucket(iter_len)
        worker_tag = "multi" if workers >= 2 else "solo"
        for key in (
            (pattern, bucket, worker_tag),
            (pattern, bucket),
        ):
            if len(key) == 3 and key in self.by_pattern_bucket_workers:
                return majority(self.by_pattern_bucket_workers[key])
            if len(key) == 2 and key in self.by_pattern_bucket:
                return majority(self.by_pattern_bucket[key])
        if pattern in self.by_pattern:
            return majority(self.by_pattern[pattern])
        return majority(self.global_levels)

    def evaluate(self, test: list[Record]) -> dict:
        wrong = 0
        per_level: dict[str, dict[str, int]] = {}
        for rec in test:
            pred = self.predict(rec.pattern, rec.iter_len, rec.workers)
            if pred != rec.level:
                wrong += 1
            bucket = per_level.setdefault(rec.level, {"correct": 0, "total": 0})
            bucket["total"] += 1
            if pred == rec.level:
                bucket["correct"] += 1
        total = len(test)
        rate = (wrong / total) if total else 0.0
        return {
            "n_test": total,
            "misassignments": wrong,
            "misassignment_rate": round(rate, 4),
            "meets_le_op_11_target": rate <= 0.15,
            "per_level_accuracy": {
                lvl: round(v["correct"] / v["total"], 4) if v["total"] else 0.0
                for lvl, v in sorted(per_level.items())
            },
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="LE-OP-11 level recommender v0.1")
    parser.add_argument("--seed", type=int, default=42, help="Train/test split seed")
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--pattern", help="Predict level for one pattern (demo)")
    parser.add_argument("--iter-len", type=int, default=3, help="With --pattern")
    parser.add_argument("--workers", type=int, default=1, help="With --pattern")
    args = parser.parse_args()

    records = load_records()
    if not records:
        print("No LoopNet records loaded.", file=sys.stderr)
        return 1

    rng = __import__("random").Random(args.seed)
    shuffled = records[:]
    rng.shuffle(shuffled)
    split = int(len(shuffled) * args.train_ratio)
    train, test = shuffled[:split], shuffled[split:]

    model = LevelRecommender()
    model.fit(train)

    if args.pattern:
        level = model.predict(args.pattern, args.iter_len, args.workers)
        print(f"pattern={args.pattern!r} iter_len={args.iter_len} workers={args.workers} -> level {level}")
        return 0

    metrics = model.evaluate(test)
    payload = {
        "version": "0.1",
        "problem": "LE-OP-11",
        "dataset": "KanakMalpani/loopnet-v0.2",
        "train_n": len(train),
        "test_n": len(test),
        "features": ["primary_pattern", "iteration_length_bucket", "worker_count"],
        "oracle": "pattern→level map in tools/loopnet_fields.py",
        "metrics": metrics,
        "command": "python tools/level_recommender.py",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("LE-OP-11 v0.1 recommender")
    print(f"  train: {len(train)}  test: {len(test)}")
    print(f"  misassignment_rate: {metrics['misassignment_rate']:.1%}")
    print(f"  target <=15%: {'PASS' if metrics['meets_le_op_11_target'] else 'PENDING'}")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
