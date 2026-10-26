"""Offline dependency-cache behavior for demo/demo.sh (criterion C3)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DEMO_SH = "demo/demo.sh"


def _tail(blob: str, n: int = 50) -> str:
    lines = blob.splitlines()
    return "\n".join(lines[-n:] if len(lines) > n else lines)


def _report(proc: subprocess.CompletedProcess[str]) -> str:
    return _tail(f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")


if shutil.which("unshare") is None:
    pytest.skip("unshare not available", allow_module_level=True)
_unshare_probe = subprocess.run(["unshare", "-rn", "true"], capture_output=True, check=False)
if _unshare_probe.returncode != 0:
    pytest.skip("unshare -rn failed (need user namespaces)", allow_module_level=True)


def test_warm_run_offline_skips_install(tmp_path: Path) -> None:
    venv = tmp_path / "venv"
    env = {**os.environ, "DEMO_VENV": str(venv)}

    warm = subprocess.run(
        ["bash", DEMO_SH],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    assert warm.returncode == 0, _report(warm)
    assert "deps: installing" in warm.stdout, _report(warm)

    offline = subprocess.run(
        ["unshare", "-rn", "bash", DEMO_SH],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    assert offline.returncode == 0, _report(offline)
    assert "deps: cached" in offline.stdout, _report(offline)
    assert "deps: installing" not in offline.stdout, _report(offline)
    combined = offline.stdout + offline.stderr
    assert "Collecting" not in combined, _report(offline)

    (venv / ".demo-stamp").write_text("stale\n", encoding="utf-8")
    stale = subprocess.run(
        ["unshare", "-rn", "bash", DEMO_SH],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    assert "deps: installing" in stale.stdout, _report(stale)
