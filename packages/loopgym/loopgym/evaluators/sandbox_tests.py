"""Sandboxed real-outcome evaluator for code-repair fixtures.

Layout of a fixture dir (packages/loopbench/fixtures/<id>/):
  src/<module>.py   buggy module (the ONLY file the model's working copy ever contains)
  hidden_tests/     pytest suite, copied to a separate temp dir the model never sees
  BUG.md            bug description
Reference fixes live in fixtures/_reference/ and are never read by this module.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FIXTURES_ROOT = Path(
    os.environ.get(
        "LOOPBENCH_FIXTURES",
        str(Path(__file__).resolve().parents[3] / "loopbench" / "fixtures"),
    )
)
TASK_FAMILIES = {"LB-CR-1": ["cr-001", "cr-002", "cr-003", "cr-004", "cr-005", "cr-006", "cr-007"]}

_CODE_BLOCK = re.compile(r"```(?:python|py)[ \t]*\n(.*?)```", re.DOTALL | re.IGNORECASE)


@dataclass(frozen=True)
class Fixture:
    fixture_id: str
    root: Path

    @property
    def module_path(self) -> Path:
        mods = sorted((self.root / "src").glob("*.py"))
        if len(mods) != 1:
            raise ValueError(f"fixture {self.fixture_id} must have exactly one module in src/")
        return mods[0]

    @property
    def module_name(self) -> str:
        return self.module_path.name

    @property
    def source(self) -> str:
        return self.module_path.read_text(encoding="utf-8")

    @property
    def bug_description(self) -> str:
        return (self.root / "BUG.md").read_text(encoding="utf-8").strip()

    @property
    def hidden_tests_dir(self) -> Path:
        return self.root / "hidden_tests"

    def hidden_texts(self) -> list[str]:
        """Contents that must never reach the model (hidden tests + reference fix)."""
        texts = [p.read_text(encoding="utf-8") for p in sorted(self.hidden_tests_dir.glob("*.py"))]
        ref = self.root.parent / "_reference" / f"{self.fixture_id}.py"
        if ref.exists():
            texts.append(ref.read_text(encoding="utf-8"))
        return texts


def get_fixture(fixture_id: str) -> Fixture | None:
    root = FIXTURES_ROOT / fixture_id
    if fixture_id.startswith("_") or not (root / "src").is_dir():
        return None
    return Fixture(fixture_id, root)


def resolve_fixtures(task_id: str) -> list[Fixture]:
    """Map a task id (cr-001) or family (LB-CR-1) to fixtures."""
    ids = TASK_FAMILIES.get(task_id, [task_id])
    return [f for f in (get_fixture(i) for i in ids) if f is not None]


def extract_code(output: str) -> str | None:
    blocks = _CODE_BLOCK.findall(output or "")
    if not blocks:
        return None
    code = blocks[-1].strip("\n") + "\n"
    try:
        compile(code, "<patch>", "exec")
    except SyntaxError:
        return None
    return code


def _count_tests(test_dir: Path) -> int:
    return sum(
        len(re.findall(r"^def test_\w+", p.read_text(encoding="utf-8"), re.MULTILINE))
        for p in test_dir.glob("test_*.py")
    )


def test_pass_rate(fixture: Fixture, output: str, timeout: int = 30) -> dict[str, Any]:
    """Apply model output as a full-file replacement of the fixture module and run hidden tests."""
    total = _count_tests(fixture.hidden_tests_dir)
    base = {"test_pass_rate": 0.0, "score": 0.0, "passed": False, "tests_total": total,
            "tests_passed": 0, "failures": [], "failure_codes": []}
    code = extract_code(output)
    if code is None:
        return {**base, "failure_codes": ["fail.unparseable_output"],
                "remediation_hints": ["Return the full corrected module in one ```python code block."]}
    tmp_dir = os.environ.get("LOOPBENCH_EVAL_TMP")
    with tempfile.TemporaryDirectory(prefix="lb-work-", dir=tmp_dir) as work, \
            tempfile.TemporaryDirectory(prefix="lb-hidden-", dir=tmp_dir) as hidden:
        os.chmod(work, 0o700)
        os.chmod(hidden, 0o700)
        work_p, hidden_p = Path(work), Path(hidden)
        shutil.copytree(fixture.root / "src", work_p, dirs_exist_ok=True)
        (work_p / fixture.module_name).write_text(code, encoding="utf-8")
        # Hidden tests are copied only here, after the model call has already returned.
        shutil.copytree(fixture.hidden_tests_dir, hidden_p / "tests")
        junit = hidden_p / "junit.xml"
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(work_p),
               "PYTHONDONTWRITEBYTECODE": "1", "HOME": str(hidden_p)}
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=no", "-rfE",
               f"--junitxml={junit}", "--rootdir", str(hidden_p / "tests"), str(hidden_p / "tests")]
        try:
            subprocess.run(cmd, cwd=hidden_p, env=env, capture_output=True, text=True,
                           timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            return {**base, "failure_codes": ["fail.test_timeout"],
                    "remediation_hints": ["Tests timed out; avoid infinite loops."]}
        passed = 0
        failures: list[str] = []
        if junit.exists():
            for case in ET.parse(junit).getroot().iter("testcase"):
                bad = [c for c in case if c.tag in ("failure", "error", "skipped")]
                if bad:
                    failures.append(case.get("name") or "collection_error")
                else:
                    passed += 1
        if not failures and passed == 0:
            failures = ["collection_error"]
    total = max(total, 1)
    rate = min(1.0, passed / total)
    failing = ", ".join(failures) if failures else "none"
    return {**base, "test_pass_rate": rate, "score": rate, "passed": rate >= 1.0,
            "tests_passed": passed, "failures": failures,
            "failure_codes": [] if rate >= 1.0 else ["fail.tests_failing"],
            "remediation_hints": [f"{passed}/{total} hidden tests passed", f"Failing tests: {failing}"]}
