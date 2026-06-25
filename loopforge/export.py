"""Export LSS specs to runnable implementation stubs (PyPI-native templates)."""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Any

import yaml

EXPORT_TARGETS = ("generic", "langgraph", "crewai")


def _read_template(*parts: str) -> str:
    try:
        ref = resources.files("loopforge.templates.export")
        for part in parts:
            ref = ref.joinpath(part)
        with resources.as_file(ref) as path:
            return path.read_text(encoding="utf-8")
    except (ModuleNotFoundError, FileNotFoundError, TypeError):
        local = Path(__file__).resolve().parent / "templates" / "export"
        for part in parts:
            local = local / part
        if not local.exists():
            raise FileNotFoundError(f"Export template missing: {'/'.join(parts)}")
        return local.read_text(encoding="utf-8")


def load_spec(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid spec: {path}")
    return data


def export_stub(spec_path: Path, out_dir: Path, target: str) -> Path:
    if target not in EXPORT_TARGETS:
        raise ValueError(f"Unknown export target: {target} (choose {EXPORT_TARGETS})")

    spec = load_spec(spec_path)
    loop_name = spec.get("loop_name", spec_path.stem)
    objective = str(spec.get("objective", "")).split("\n")[0][:120].replace('"', "'")
    workers = ", ".join(w.get("id", "?") for w in (spec.get("workers") or []))

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "spec.yaml").write_text(spec_path.read_text(encoding="utf-8"), encoding="utf-8")

    run_tpl = _read_template(target, "run.py")
    run_src = run_tpl.replace("{loop_name}", loop_name).replace("{objective_short}", objective)
    (out_dir / "run.py").write_text(run_src, encoding="utf-8")

    readme_tpl = _read_template("README.md")
    readme_src = (
        readme_tpl.replace("{loop_name}", loop_name)
        .replace("{target}", target)
        .replace("{workers}", workers or "none")
    )
    (out_dir / "README.md").write_text(readme_src, encoding="utf-8")
    return out_dir
