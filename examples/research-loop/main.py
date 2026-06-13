#!/usr/bin/env python3
"""
Research Loop — Level 2 (Reflective)
Retrieve → Synthesize → Verify with triangular evaluators.

LSS mapping:
  loop_name: research-loop-example
  evaluators: [citation_verifier, claim_support, coherence]
"""

from __future__ import annotations

import dataclasses
import re
from typing import Any


CORPUS: dict[str, dict[str, Any]] = {
    "src-1": {
        "title": "Loop Engineering Manifesto",
        "text": "Loop Engineering is the discipline of designing self-improving feedback systems.",
        "url": "https://example.com/manifesto",
    },
    "src-2": {
        "title": "LSS 1.0 Specification",
        "text": "LSS defines loop_name, workers, evaluators, and termination_conditions in YAML.",
        "url": "https://example.com/lss",
    },
    "src-3": {
        "title": "LES Scoring Framework",
        "text": "LES scores loops across eight weighted categories including effectiveness and safety.",
        "url": "https://example.com/les",
    },
}


@dataclasses.dataclass
class ResearchState:
    question: str
    retrieved: list[str] = dataclasses.field(default_factory=list)
    brief: str = ""
    iteration: int = 0


MAX_ITERATIONS = 5


def retriever(state: ResearchState) -> list[str]:
    """Mock search: return sources not yet retrieved, prioritized by keyword overlap."""
    q_words = set(state.question.lower().split())
    candidates = []
    for sid, doc in CORPUS.items():
        if sid in state.retrieved:
            continue
        doc_words = set(doc["text"].lower().split())
        overlap = len(q_words & doc_words)
        candidates.append((overlap, sid))
    candidates.sort(reverse=True)
    new_ids = [sid for _, sid in candidates[:2]]
    state.retrieved.extend(new_ids)
    return new_ids


def synthesizer(state: ResearchState) -> str:
    """Build brief from retrieved sources; quality improves with more sources."""
    if not state.retrieved:
        return "Insufficient sources."

    sections = [f"# Research Brief: {state.question}\n"]
    sections.append("## Summary\n")
    if len(state.retrieved) >= 2:
        refs = " ".join(f"[{sid}]" for sid in state.retrieved[:2])
        sections.append(
            f"Loop Engineering formalizes iterative feedback systems using "
            f"LSS specifications and LES scoring {refs}.\n"
        )
    else:
        sections.append("Loop Engineering is a new discipline [src-1].\n")

    sections.append("\n## Findings\n")
    for sid in state.retrieved:
        doc = CORPUS[sid]
        sections.append(f"- {doc['text']} [{sid}]\n")

    if len(state.retrieved) >= 3:
        sections.append(
            "\nEvaluation uses LES across eight categories [src-3].\n"
        )

    sections.append("\n## Bibliography\n")
    for sid in state.retrieved:
        doc = CORPUS[sid]
        sections.append(f"- [{sid}] {doc['title']} — {doc['url']}\n")

    return "".join(sections)


def eval_citations(brief: str, retrieved: list[str]) -> tuple[bool, str]:
    cited = set(re.findall(r"\[(src-\d+)\]", brief))
    required = set(retrieved)
    missing = required - cited
    if missing:
        return False, f"Missing citations: {missing}"
    uncited_refs = cited - required
    if uncited_refs:
        return False, f"Citations not in retrieved set: {uncited_refs}"
    invalid = cited - set(CORPUS.keys())
    if invalid:
        return False, f"Invalid citation IDs: {invalid}"
    return True, "All citations valid"


def eval_claim_support(brief: str, retrieved: list[str]) -> tuple[bool, str]:
    if len(retrieved) < 2:
        return False, "Need at least 2 sources for claim support"
    if "LSS" in brief and "src-2" not in retrieved:
        return False, "LSS claim without src-2"
    return True, "Claims supported"


def eval_coherence(brief: str) -> tuple[bool, str]:
    required_sections = ["## Summary", "## Findings", "## Bibliography"]
    missing = [s for s in required_sections if s not in brief]
    if missing:
        return False, f"Missing sections: {missing}"
    if len(brief) < 100:
        return False, "Brief too short"
    return True, "Coherent structure"


def run_research_loop(question: str) -> ResearchState:
    state = ResearchState(question=question)

    while state.iteration < MAX_ITERATIONS:
        state.iteration += 1
        new = retriever(state)
        print(f"[iter {state.iteration}] retrieved: {new or 'none new'}")

        state.brief = synthesizer(state)

        checks = [
            ("citation_verifier", eval_citations(state.brief, state.retrieved)),
            ("claim_support", eval_claim_support(state.brief, state.retrieved)),
            ("coherence", eval_coherence(state.brief)),
        ]

        all_pass = True
        for name, (passed, msg) in checks:
            status = "PASS" if passed else "FAIL"
            print(f"  {name}: {status} — {msg}")
            if not passed:
                all_pass = False

        if all_pass:
            print("\n[OK] Terminated: all evaluators pass")
            break
    else:
        print("\n[WARN] Terminated: max_iterations reached")

    return state


def main() -> None:
    state = run_research_loop("Explain Loop Engineering, LSS, and LES")
    print("\n--- Final Brief ---")
    print(state.brief)


if __name__ == "__main__":
    main()
