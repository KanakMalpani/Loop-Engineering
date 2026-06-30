"""Agent harness presets — map popular frameworks to LSS + LoopBench in one call."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentPreset:
    """Token-efficient mapping from a harness name to loop tooling defaults."""

    key: str
    label: str
    pattern: str
    export: str | None
    fork: str | None
    compose: str | None
    bench_task: str
    bench_suite: str
    default_recipe: str | None
    intent_hint: str
    pip_extra: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "pattern": self.pattern,
            "export": self.export,
            "fork": self.fork,
            "compose": self.compose,
            "bench_task": self.bench_task,
            "bench_suite": self.bench_suite,
            "default_recipe": self.default_recipe,
            "intent_hint": self.intent_hint,
            "pip_extra": self.pip_extra,
        }


AGENT_PRESETS: dict[str, AgentPreset] = {
    "react": AgentPreset(
        key="react",
        label="ReAct (reason → act → observe)",
        pattern="react",
        export="generic",
        fork=None,
        compose=None,
        bench_task="LB-REACT-1",
        bench_suite="suite-repair",
        default_recipe="dev-agent",
        intent_hint="Use tools iteratively until the goal is satisfied",
        pip_extra=None,
    ),
    "reflexion": AgentPreset(
        key="reflexion",
        label="Reflexion (verbal RL + memory)",
        pattern="reflection",
        export="generic",
        fork="autonomous-debugger",
        compose=None,
        bench_task="LB-REFLEX-1",
        bench_suite="suite-repair",
        default_recipe="dev-agent",
        intent_hint="Reflect on failures and retry with episodic memory",
        pip_extra=None,
    ),
    "langgraph": AgentPreset(
        key="langgraph",
        label="LangGraph (state graph / routing)",
        pattern="parallel",
        export="langgraph",
        fork=None,
        compose="parallel",
        bench_task="LB-GRAPH-1",
        bench_suite="suite-agent",
        default_recipe="swarm-review",
        intent_hint="Parallel branches with conditional routing and merge",
        pip_extra="langgraph",
    ),
    "crewai": AgentPreset(
        key="crewai",
        label="CrewAI (sequential crew roles)",
        pattern="crew",
        export="crewai",
        fork="coding-agent",
        compose="sequential",
        bench_task="LB-CREW-1",
        bench_suite="suite-agent",
        default_recipe="full-stack",
        intent_hint="Sequential crew: planner then implementer then reviewer",
        pip_extra="crewai",
    ),
    "dspy": AgentPreset(
        key="dspy",
        label="DSPy (compile / optimize programs)",
        pattern="verification",
        export="generic",
        fork="autonomous-debugger",
        compose=None,
        bench_task="LB-OPT-1",
        bench_suite="suite-repair",
        default_recipe="dev-agent",
        intent_hint="Optimize prompts until tests pass",
        pip_extra=None,
    ),
    "openai_agents": AgentPreset(
        key="openai_agents",
        label="OpenAI Agents SDK",
        pattern="react",
        export="openai_agents",
        fork=None,
        compose=None,
        bench_task="LB-REACT-1",
        bench_suite="suite-repair",
        default_recipe="dev-agent",
        intent_hint="Agent with tool calls until task complete",
        pip_extra=None,
    ),
    "aider": AgentPreset(
        key="aider",
        label="Aider (pair-programming edit-test loop)",
        pattern="verification",
        export="generic",
        fork="autonomous-debugger",
        compose=None,
        bench_task="LB-CR-1",
        bench_suite="suite-repair",
        default_recipe="safe-repair",
        intent_hint="Edit code and run tests until passing",
        pip_extra=None,
    ),
    "openhands": AgentPreset(
        key="openhands",
        label="OpenHands / Devin-style dev agent",
        pattern="plan",
        export="generic",
        fork="coding-agent",
        compose=None,
        bench_task="LB-AUTO-1",
        bench_suite="suite-knowledge",
        default_recipe="full-stack",
        intent_hint="Plan, implement, and verify autonomously under budget",
        pip_extra=None,
    ),
    "claude_code": AgentPreset(
        key="claude_code",
        label="Claude Code / IDE agent",
        pattern="verification",
        export="generic",
        fork="coding-agent",
        compose=None,
        bench_task="LB-CR-1",
        bench_suite="suite-repair",
        default_recipe="dev-agent",
        intent_hint="Fix failing tests from CI with minimal diff",
        pip_extra=None,
    ),
    "codex": AgentPreset(
        key="codex",
        label="Codex / test-driven coding agent",
        pattern="verification",
        export="generic",
        fork="autonomous-debugger",
        compose=None,
        bench_task="LB-CR-1",
        bench_suite="suite-repair",
        default_recipe="dev-agent",
        intent_hint="Repair failing unit tests iteratively",
        pip_extra=None,
    ),
    "smolagents": AgentPreset(
        key="smolagents",
        label="Hugging Face SmolAgents",
        pattern="react",
        export="generic",
        fork=None,
        compose=None,
        bench_task="LB-REACT-1",
        bench_suite="suite-repair",
        default_recipe="dev-agent",
        intent_hint="Tool-use agent loop with observation feedback",
        pip_extra=None,
    ),
    "autogpt": AgentPreset(
        key="autogpt",
        label="AutoGPT-style long-horizon agent",
        pattern="plan",
        export="generic",
        fork="coding-agent",
        compose=None,
        bench_task="LB-AUTO-1",
        bench_suite="suite-knowledge",
        default_recipe="research-pipeline",
        intent_hint="Multi-step plan execute loop under strict budget",
        pip_extra=None,
    ),
}

_ALIASES: dict[str, str] = {
    "lang-graph": "langgraph",
    "crew": "crewai",
    "crew-ai": "crewai",
    "openai-agents": "openai_agents",
    "openai": "openai_agents",
    "devin": "openhands",
    "open-hands": "openhands",
    "claude": "claude_code",
    "claude-code": "claude_code",
    "hf": "smolagents",
    "auto-gpt": "autogpt",
}


def resolve_agent(name: str) -> AgentPreset:
    key = name.strip().lower().replace(" ", "_").replace("-", "_")
    key = _ALIASES.get(key, key)
    if key not in AGENT_PRESETS:
        valid = ", ".join(sorted(AGENT_PRESETS))
        raise KeyError(f"Unknown agent {name!r}. Choose: {valid}")
    return AGENT_PRESETS[key]


def list_agents() -> list[dict[str, Any]]:
    return [p.to_dict() for p in AGENT_PRESETS.values()]


def enrich_intent(intent: str, preset: AgentPreset) -> str:
    """Prepend harness hint only when intent is very short (token-efficient)."""
    text = intent.strip()
    if len(text.split()) >= 6:
        return text
    return f"{preset.intent_hint}. {text}"
