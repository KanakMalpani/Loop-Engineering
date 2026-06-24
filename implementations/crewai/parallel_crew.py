"""CrewAI-style parallel branch crew with mock fallback (LB-COMP-1 mapping)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BranchResult:
    branch_id: str
    lens: str
    output: str
    quality_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch_id": self.branch_id,
            "lens": self.lens,
            "output": self.output,
            "quality_score": self.quality_score,
        }


@dataclass
class ParallelCrewResult:
    task: str
    branches: list[BranchResult]
    synthesis: str
    quality_score: float
    dissent: list[str] = field(default_factory=list)
    success: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "branches": [b.to_dict() for b in self.branches],
            "synthesis": self.synthesis,
            "quality_score": self.quality_score,
            "dissent": self.dissent,
            "success": self.success,
        }


class MockBranchAgent:
    def __init__(self, branch_id: str, lens: str) -> None:
        self.branch_id = branch_id
        self.lens = lens

    def execute(self, task: str) -> BranchResult:
        score = 0.82 if "operator" in self.branch_id else 0.79
        return BranchResult(
            branch_id=self.branch_id,
            lens=self.lens,
            output=f"[{self.branch_id}] {self.lens[:60]}... on: {task[:80]}",
            quality_score=score,
        )


def run_parallel_crew(task: str, quality_threshold: float = 0.80) -> dict[str, Any]:
    """Run three parallel worldview branches then merge (mirrors scenario-swarm-rehearsal)."""
    branches = [
        MockBranchAgent("falsifier", "Pre-mortem: assume plan FAILS"),
        MockBranchAgent("evidence", "Gather sourced facts and uncertainty bounds"),
        MockBranchAgent("operator", "90-day action memo regardless of optimism"),
    ]

    results = [agent.execute(task) for agent in branches]
    dissent = [b.branch_id for b in results if b.quality_score < 0.80]
    avg = sum(b.quality_score for b in results) / len(results)
    dissent_note = f" Dissent preserved from: {', '.join(dissent)}." if dissent else ""
    synthesis = (
        f"Merged forecast brief for: {task[:100]}. "
        f"Branch consensus avg={avg:.2f}.{dissent_note}"
    )
    composite = min(0.99, avg * 0.6 + 0.35)
    success = composite >= quality_threshold

    out = ParallelCrewResult(
        task=task,
        branches=results,
        synthesis=synthesis,
        quality_score=composite,
        dissent=dissent,
        success=success,
    )
    return out.to_dict()
