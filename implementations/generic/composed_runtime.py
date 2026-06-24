"""Execute LSS specs with composition blocks (sequential, nested, and parallel)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loop_runtime import LoopResult, LoopRuntime, load_lss_spec


@dataclass
class StageResult:
    child_id: str
    loop_name: str
    result: LoopResult
    role: str = "stage"


@dataclass
class ComposedResult:
    success: bool
    output: str
    stages: list[StageResult] = field(default_factory=list)
    composition_type: str = ""
    termination_reason: str = ""


def _resolve_ref(spec_path: Path, ref: str) -> Path:
    if ref.strip().startswith("loop-library/"):
        return spec_path.resolve().parents[2] / ref.strip()
    return (spec_path.parent / ref.strip()).resolve()


class ComposedLoopRuntime:
    """Run child loops in sequence or with nested inner invocation."""

    def __init__(self, spec_path: str | Path) -> None:
        self.spec_path = Path(spec_path)
        self.spec = load_lss_spec(self.spec_path)
        self.composition = self.spec.get("composition") or {}
        if not self.composition:
            raise ValueError(f"No composition block: {self.spec_path}")

    def _run_child(self, ref: str, task: str, child_id: str, role: str) -> StageResult:
        child_path = _resolve_ref(self.spec_path, ref)
        child_spec = load_lss_spec(child_path)
        runtime = LoopRuntime(child_spec)
        result = runtime.run(task)
        return StageResult(
            child_id=child_id,
            loop_name=str(child_spec.get("loop_name", child_path.stem)),
            result=result,
            role=role,
        )

    def _adapter_task(self, prior: StageResult, adapter: dict[str, Any]) -> str:
        snippet = prior.result.output[:500]
        return f"Prior stage ({prior.child_id}) output:\n{snippet}"

    def run_sequential(self, user_input: str) -> ComposedResult:
        children = self.composition.get("children") or []
        adapters = self.composition.get("adapters") or []
        stages: list[StageResult] = []
        task = user_input

        for i, child in enumerate(children):
            stage = self._run_child(
                child["ref"], task, child["id"], child.get("role", "stage")
            )
            stages.append(stage)
            if not stage.result.success:
                return ComposedResult(
                    success=False,
                    output=stage.result.output,
                    stages=stages,
                    composition_type="sequential",
                    termination_reason=f"stage {child['id']} failed",
                )
            if i < len(adapters):
                task = self._adapter_task(stage, adapters[i])

        last = stages[-1].result
        return ComposedResult(
            success=last.success,
            output=last.output,
            stages=stages,
            composition_type="sequential",
            termination_reason=last.termination_reason,
        )

    def run_nested(self, user_input: str) -> ComposedResult:
        children = self.composition.get("children") or []
        outer = next(c for c in children if c.get("role") == "outer")
        inners = [c for c in children if c.get("role") == "inner"]
        adapters = self.composition.get("adapters") or []

        outer_stage = self._run_child(
            outer["ref"], user_input, outer["id"], "outer"
        )
        stages = [outer_stage]

        if outer_stage.result.success:
            return ComposedResult(
                success=True,
                output=outer_stage.result.output,
                stages=stages,
                composition_type="nested",
                termination_reason="outer succeeded without inner",
            )

        task = (
            self._adapter_task(outer_stage, adapters[0])
            if adapters
            else outer_stage.result.output
        )
        for inner in inners:
            inner_stage = self._run_child(
                inner["ref"], task, inner["id"], "inner"
            )
            stages.append(inner_stage)
            if inner_stage.result.success:
                return ComposedResult(
                    success=True,
                    output=inner_stage.result.output,
                    stages=stages,
                    composition_type="nested",
                    termination_reason=f"inner {inner['id']} repaired pipeline",
                )
            task = inner_stage.result.output

        last = stages[-1].result
        return ComposedResult(
            success=False,
            output=last.output,
            stages=stages,
            composition_type="nested",
            termination_reason="inner loops exhausted",
        )

    def run_parallel(self, user_input: str) -> ComposedResult:
        children = self.composition.get("children") or []
        merge = self.composition.get("merge") or {}
        min_pass = int(merge.get("min_branches_pass", max(2, len(children) // 2)))

        def run_branch(child: dict[str, Any]) -> StageResult:
            lens = child.get("lens", "")
            task = f"{lens}\n\nScenario:\n{user_input}" if lens else user_input
            return self._run_child(
                child["ref"], task, child["id"], child.get("role", "branch")
            )

        stages: list[StageResult] = []
        with ThreadPoolExecutor(max_workers=min(len(children), 4)) as pool:
            futures = {pool.submit(run_branch, c): c["id"] for c in children}
            for future in as_completed(futures):
                stages.append(future.result())

        stages.sort(key=lambda s: s.child_id)
        passed = sum(1 for s in stages if s.result.success)
        merged = "\n\n---\n\n".join(
            f"## Branch: {s.child_id} ({s.loop_name})\n"
            f"Quality: {s.result.quality_score:.2f} | Success: {s.result.success}\n"
            f"{s.result.output[:400]}"
            for s in stages
        )
        success = passed >= min_pass
        reason = (
            f"parallel merge: {passed}/{len(stages)} branches passed (need {min_pass})"
            if success
            else f"parallel merge failed: {passed}/{len(stages)} branches passed"
        )
        return ComposedResult(
            success=success,
            output=merged,
            stages=stages,
            composition_type="parallel",
            termination_reason=reason,
        )

    def run(self, user_input: str = "") -> ComposedResult:
        if not user_input:
            examples = (self.spec.get("inputs") or {}).get("examples") or []
            if examples and isinstance(examples[0], dict):
                user_input = str(examples[0].get("task", "composed task"))
            else:
                user_input = "composed task"

        ctype = self.composition.get("type")
        if ctype == "sequential":
            return self.run_sequential(user_input)
        if ctype == "nested":
            return self.run_nested(user_input)
        if ctype == "parallel":
            return self.run_parallel(user_input)
        raise ValueError(f"Unsupported composition type: {ctype}")
