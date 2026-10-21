"""Isolate benchmark run_full launch-memory side effects during pytest."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REAL_LAUNCH_MEMORY_MODULE = "test_launch_memory_check"


def _benchmark_run_full_path() -> Path:
    return (
        Path(__file__).resolve().parents[3]
        / "benchmarks"
        / "loopbench-validity"
        / "run_full.py"
    )


def _imported_run_full(request):
    """Benchmark run_full already imported by the test module, if any.

    Importing run_full here would replace MockLLM. Callers restore the real
    classes around their own import; this fixture only patches that object.
    """
    path = _benchmark_run_full_path()
    if not path.is_file():
        return None
    module = request.module
    loaded = getattr(module, "run_full", None) if module is not None else None
    if loaded is None:
        loaded = sys.modules.get("run_full")
    origin = getattr(loaded, "__file__", None)
    if not origin:
        return None
    try:
        if Path(origin).resolve() != path.resolve():
            return None
    except OSError:
        return None
    return loaded


@pytest.fixture(autouse=True)
def isolate_launch_memory(request):
    """Return 8192 MB and write launch-memcheck.log under the test tmp dir.

    Skips test_launch_memory_check, which calls the real parser and the real
    check with its own monkeypatches.
    """
    module = request.module
    name = "" if module is None else module.__name__.rsplit(".", 1)[-1]
    run_full = None if name == _REAL_LAUNCH_MEMORY_MODULE else _imported_run_full(request)
    if run_full is None:
        yield
        return

    monkeypatch = request.getfixturevalue("monkeypatch")
    tmp_path = request.getfixturevalue("tmp_path")

    def _mem_available_mb(meminfo_path: str = "/proc/meminfo") -> int:
        return 8192

    monkeypatch.setattr(run_full, "mem_available_mb", _mem_available_mb)
    original = run_full.check_launch_memory

    def _check_launch_memory(outdir_or_logdir):
        return original(tmp_path)

    monkeypatch.setattr(run_full, "check_launch_memory", _check_launch_memory)
    yield
