"""Row 4 (packages_step) tests for demo/demo_steps.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import jsonschema
import loopnet

ROOT = Path(__file__).resolve().parents[1]
DEMO_STEPS = ROOT / "demo" / "demo_steps.py"
RECORD_SCHEMA = ROOT / "packages/loopnet/schema/loopnet-record-v1.json"
VALIDATE_LSS_SUFFIX = "loop-core/tools/validate_lss.py"
PENDING = "pending fixed benchmark acceptance"


def _load():
    spec = importlib.util.spec_from_file_location("demo_steps", DEMO_STEPS)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _validate_lss_loaded() -> bool:
    for mod in sys.modules.values():
        path = getattr(mod, "__file__", None)
        if path and Path(path).resolve().as_posix().endswith(VALIDATE_LSS_SUFFIX):
            return True
    return False


def _line_needs_pending(line: str) -> bool:
    return "les_observed" in line or ("LES" in line and any(ch.isdigit() for ch in line))


def test_packages_step_calls_all_five(tmp_path, capsys):
    steps = _load()
    steps.spec_step()
    trace = steps.trace_step(tmp_path)
    out = steps.packages_step(trace, tmp_path)
    captured = capsys.readouterr().out

    assert "loopnet" in sys.modules
    assert "loopnet.les" in sys.modules
    assert "loopbench.les_compute" in sys.modules
    assert "loopgym" in sys.modules
    assert "loopotel.tracer" in sys.modules
    assert _validate_lss_loaded()

    assert out["loop_core_errors"] == []

    schema = json.loads(RECORD_SCHEMA.read_text(encoding="utf-8"))
    record_path = tmp_path / "record.json"
    assert record_path.is_file()
    jsonschema.Draft202012Validator(schema).validate(
        json.loads(record_path.read_text(encoding="utf-8"))
    )
    assert out["record"]["failure_mode"] in loopnet.FAILURE_MODES

    assert "=== 4. PACKAGES ===" in captured
    for prefix in ("loop-core: ", "loopnet: ", "loopbench: ", "loopgym: ", "loopotel: "):
        assert any(line.startswith(prefix) for line in captured.splitlines())

    bench_lines = [ln for ln in captured.splitlines() if ln.startswith("loopbench: ")]
    assert len(bench_lines) == 1
    assert "compute_task_les" in bench_lines[0]
    assert bench_lines[0].rstrip().endswith(PENDING)

    for line in captured.splitlines():
        if _line_needs_pending(line):
            assert PENDING in line


def test_main_all_includes_packages(capsys, tmp_path, monkeypatch):
    steps = _load()
    assert steps.main(["packages", "--outdir", str(tmp_path)]) == 0
    assert "=== 4. PACKAGES ===" in capsys.readouterr().out
