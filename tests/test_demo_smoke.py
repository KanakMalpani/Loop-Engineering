"""Smoke test for the offline demo step functions."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO_STEPS = ROOT / "demo" / "demo_steps.py"


def _load():
    spec = importlib.util.spec_from_file_location("demo_steps", DEMO_STEPS)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_demo_steps_complete(tmp_path, capsys):
    steps = _load()
    steps.spec_step()
    outdir = tmp_path / "out"
    steps.trace_step(outdir)
    steps.bench_step()
    captured = capsys.readouterr().out

    trace_path = outdir / "trace.json"
    assert trace_path.is_file()
    document = json.loads(trace_path.read_text(encoding="utf-8"))
    spans = document["spans"]
    assert spans
    assert any(span.get("name") == "loop.run" for span in spans)
    assert any(span.get("name") == "loop.iteration" for span in spans)
    # Row 4 C2: loopotel emits gen_ai.* worker spans; the file must contain them.
    assert "gen_ai." in trace_path.read_text(encoding="utf-8")
    assert "gen_ai" in captured
    planned = captured.split("PLANNED (not built yet)", 1)[1] if "PLANNED" in captured else ""
    assert "gen_ai.* spans" not in planned
    assert "SHOWN" in captured
    assert "pending fixed benchmark acceptance" in captured
