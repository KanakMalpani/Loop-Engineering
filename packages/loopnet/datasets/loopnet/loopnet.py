"""HuggingFace datasets loader script for LoopNet seed corpus."""

import json
from pathlib import Path

import datasets


_DESCRIPTION = "LoopNet seed corpus — loop designs, trajectories, and labeled outcomes."
_HOMEPAGE = "https://github.com/loop-engineering/loopnet"
_LICENSE = "cc-by-4.0"
_SCHEMA_VERSION = "ln/record-v1"


class LoopNetConfig(datasets.BuilderConfig):
    def __init__(self, *, records_file: str | None = None, **kwargs):
        super().__init__(version=datasets.Version("0.1.0"), **kwargs)
        self.records_file = records_file or "data/seed/records.jsonl"


class LoopNet(datasets.GeneratorBasedBuilder):
    BUILDER_CONFIGS = [
        LoopNetConfig(name="seed_v0.1", description="500-record synthetic seed corpus"),
    ]
    DEFAULT_CONFIG_NAME = "seed_v0.1"

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "record_id": datasets.Value("string"),
                    "schema_version": datasets.Value("string"),
                    "source": datasets.Value("string"),
                    "split": datasets.Value("string"),
                    "loop_name": datasets.Value("string"),
                    "objective": datasets.Value("string"),
                    "outcome": datasets.Value("string"),
                    "termination_reason": datasets.Value("string"),
                    "failure_mode": datasets.Value("string"),
                    "patterns": datasets.Sequence(datasets.Value("string")),
                    "failure_modes": datasets.Sequence(datasets.Value("string")),
                    "trajectory": datasets.Value("string"),
                    "les_observed": datasets.Value("string"),
                    "metadata": datasets.Value("string"),
                    "record_json": datasets.Value("string"),
                }
            ),
            homepage=_HOMEPAGE,
            license=_LICENSE,
        )

    def _split_generators(self, dl_manager):
        records_path = Path(__file__).resolve().parents[2] / self.config.records_file
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={"records_path": str(records_path), "split_name": "train"},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={"records_path": str(records_path), "split_name": "val"},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={"records_path": str(records_path), "split_name": "test"},
            ),
        ]

    def _generate_examples(self, records_path: str, split_name: str):
        with open(records_path, encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                record = json.loads(line)
                if record.get("split") != split_name:
                    continue
                yield index, {
                    "record_id": record["record_id"],
                    "schema_version": record["schema_version"],
                    "source": record["source"],
                    "split": record["split"],
                    "loop_name": record["loop_name"],
                    "objective": record["objective"],
                    "outcome": record["outcome"],
                    "termination_reason": record["termination_reason"],
                    "failure_mode": record.get("failure_mode", ""),
                    "patterns": record["patterns"],
                    "failure_modes": record.get("failure_modes", []),
                    "trajectory": json.dumps(record["trajectory"]),
                    "les_observed": json.dumps(record["les_observed"]),
                    "metadata": json.dumps(record["metadata"]),
                    "record_json": json.dumps(record),
                }
