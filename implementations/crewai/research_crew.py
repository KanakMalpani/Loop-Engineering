"""CrewAI-style research crew with mock fallback."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CrewResult:
    query: str
    findings: list[str]
    synthesis: str
    verification: str
    quality_score: float
    agents_used: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "findings": self.findings,
            "synthesis": self.synthesis,
            "verification": self.verification,
            "quality_score": self.quality_score,
            "agents_used": self.agents_used,
        }


class MockResearchAgent:
    def __init__(self, role: str) -> None:
        self.role = role

    def execute(self, task: str) -> str:
        if self.role == "researcher":
            return f"[{self.role}] Found 3 sources on: {task[:80]}"
        if self.role == "analyst":
            return f"[{self.role}] Synthesized themes from research on: {task[:60]}"
        if self.role == "verifier":
            return f"[{self.role}] Verification PASS — coverage adequate for: {task[:60]}"
        return f"[{self.role}] Output for: {task[:60]}"


def _build_crewai_crew(query: str):
    try:
        from crewai import Agent, Crew, Process, Task  # type: ignore

        researcher = Agent(role="Researcher", goal="Find sources", backstory="Expert researcher", verbose=False)
        analyst = Agent(role="Analyst", goal="Synthesize", backstory="Expert analyst", verbose=False)
        verifier = Agent(role="Verifier", goal="Verify", backstory="Fact checker", verbose=False)

        t1 = Task(description=f"Research: {query}", expected_output="Bullet findings", agent=researcher)
        t2 = Task(description="Synthesize findings", expected_output="Summary", agent=analyst)
        t3 = Task(description="Verify synthesis", expected_output="Pass/fail", agent=verifier)

        crew = Crew(agents=[researcher, analyst, verifier], tasks=[t1, t2, t3], process=Process.sequential)
        return crew
    except ImportError:
        return None


def run_research_crew(query: str, use_mock: bool = True) -> dict[str, Any]:
    """Run a sequential research → analyze → verify crew."""
    if not use_mock:
        crew = _build_crewai_crew(query)
        if crew is not None:
            output = crew.kickoff(inputs={"query": query})
            return {
                "query": query,
                "synthesis": str(output),
                "quality_score": 0.85,
                "agents_used": ["Researcher", "Analyst", "Verifier"],
            }

    researcher = MockResearchAgent("researcher")
    analyst = MockResearchAgent("analyst")
    verifier = MockResearchAgent("verifier")

    findings = [
        researcher.execute(query),
        researcher.execute(f"secondary search: {query}"),
    ]
    synthesis = analyst.execute("\n".join(findings))
    verification = verifier.execute(synthesis)
    score = 0.78 if "PASS" in verification else 0.55

    result = CrewResult(
        query=query,
        findings=findings,
        synthesis=synthesis,
        verification=verification,
        quality_score=score,
        agents_used=["researcher", "analyst", "verifier"],
    )
    return result.to_dict()


if __name__ == "__main__":
    out = run_research_crew("Loop engineering taxonomy levels")
    print(f"Score: {out['quality_score']:.2f}")
    print(out["synthesis"])
