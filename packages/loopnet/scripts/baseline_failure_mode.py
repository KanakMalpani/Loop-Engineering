#!/usr/bin/env python3
"""Baseline: predict failure_mode from first 3 trajectory iterations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSONL = ROOT / "data" / "seed" / "records.jsonl"


def load_records(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def extract_features(record: dict, window: int = 3) -> list[float]:
    trajectory = record["trajectory"][:window]
    if len(trajectory) < window:
        trajectory = trajectory + [trajectory[-1]] * (window - len(trajectory))

    features: list[float] = []
    for step in trajectory:
        features.extend(
            [
                step["goal_score"],
                step.get("primary_quality", step["goal_score"]),
                step["cost_usd"],
                step["latency_seconds"],
                float(step.get("safety_events", 0)),
                float(step.get("human_intervention", False)),
            ]
        )

    features.append(record["metadata"]["goal_target"])
    features.append(float(record["metadata"]["worker_count"]))
    features.append(float(record["metadata"]["evaluator_count"]))
    return features


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL)
    parser.add_argument("--window", type=int, default=3)
    args = parser.parse_args(argv)

    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import classification_report
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise SystemExit("scikit-learn required: pip install -e '.[notebook]'") from exc

    records = load_records(args.jsonl)
    labeled = [r for r in records if r.get("failure_mode")]

    train = [r for r in labeled if r["split"] == "train"]
    test = [r for r in labeled if r["split"] == "test"]

    if not train or not test:
        print("Need labeled train and test splits with failure_mode.")
        return 1

    x_train = [extract_features(r, args.window) for r in train]
    y_train = [r["failure_mode"] for r in train]
    x_test = [extract_features(r, args.window) for r in test]
    y_test = [r["failure_mode"] for r in test]

    model = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=200, random_state=42)),
        ]
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    print(classification_report(y_test, predictions, zero_division=0))
    accuracy = (predictions == y_test).mean()
    print(f"Accuracy on test split: {accuracy:.1%} ({len(test)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
