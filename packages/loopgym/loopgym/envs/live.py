"""LiveEnv — real LLM APIs (optional, user-provided keys)."""

from __future__ import annotations

import os
from typing import Any

from loopgym.envs.base import LoopEnv, Observation
from loopgym.envs.sim import SimEnv
from loopgym.runtime.loop_runtime import LLMClient


class _OpenAILiveLLM:
    """Thin wrapper for OpenAI-compatible APIs (optional dependency)."""

    def __init__(self, model: str = "gpt-4.1-mini", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.tokens_used = 0
        if not self.api_key:
            raise ValueError(
                "LiveEnv requires OPENAI_API_KEY or api_key= parameter. "
                "Use SimEnv for keyless testing."
            )
        try:
            import openai
        except ImportError as exc:
            raise ImportError("Install openai: pip install openai") from exc
        self._client = openai.OpenAI(api_key=self.api_key)

    def complete(self, prompt: str, role: str = "default") -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are a {role} agent in a loop."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        text = response.choices[0].message.content or ""
        if response.usage:
            self.tokens_used += response.usage.total_tokens
        return text


class LiveEnv(LoopEnv):
    """Live environment using real LLM APIs. Falls back to documenting key requirement."""

    def __init__(
        self,
        env_id: str,
        spec: dict[str, Any],
        llm: LLMClient | None = None,
        **sim_kwargs: Any,
    ) -> None:
        super().__init__(env_id)
        if llm is None:
            raise ValueError(
                "LiveEnv requires an injected LLM (llm=...); it never falls back to MockLLM. "
                "Use SimEnv for keyless testing, or LiveEnv.with_openai(...)."
            )
        self._sim = SimEnv(env_id, spec, **sim_kwargs)
        self._llm = llm
        self._sim._runtime = None
        self._sim.llm_override = llm  # reset() uses it instead of building MockLLM

    def reset(self, task_id: str = "", seed: int | None = None, **kwargs: Any) -> Observation:
        obs = self._sim.reset(task_id=task_id, seed=seed, **kwargs)
        if self._llm and self._sim._runtime:
            self._sim._runtime.llm = self._llm
        return obs

    def step(self, action: Any = None) -> tuple[Observation, float, bool, dict[str, Any]]:
        return self._sim.step(action)

    @property
    def done(self) -> bool:
        return self._sim.done

    @property
    def llm(self) -> LLMClient:
        return self._llm

    def run_episode(self, task_id: str = "", seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
        """Full episode with the injected LLM. Asserts the runtime really uses it."""
        result = self._sim.run_episode(task_id=task_id, seed=seed, **kwargs)
        rt = self._sim._runtime
        if rt is None or rt.llm is not self._llm:
            raise RuntimeError("LiveEnv runtime is not using the injected LLM")
        result["backend"] = "live"
        result["llm_class"] = type(self._llm).__name__
        return result

    @classmethod
    def with_openai(
        cls,
        env_id: str,
        spec: dict[str, Any],
        model: str = "gpt-4.1-mini",
        api_key: str | None = None,
        **sim_kwargs: Any,
    ) -> LiveEnv:
        return cls(env_id, spec, llm=_OpenAILiveLLM(model=model, api_key=api_key), **sim_kwargs)
