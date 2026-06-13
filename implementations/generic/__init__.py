"""Generic Loop Engineering runtime — framework-independent LSS executor."""

try:
    from .loop_runtime import (
        LoopResult,
        LoopRuntime,
        LoopState,
        MockLLM,
        load_lss_spec,
    )
    from .reflection_loop import ReflectionLoop
    from .research_loop import ResearchLoop
    from .verification_loop import VerificationLoop
    from .multi_agent_loop import MultiAgentLoop
except ImportError:
    from loop_runtime import (
        LoopResult,
        LoopRuntime,
        LoopState,
        MockLLM,
        load_lss_spec,
    )
    from reflection_loop import ReflectionLoop
    from research_loop import ResearchLoop
    from verification_loop import VerificationLoop
    from multi_agent_loop import MultiAgentLoop

__all__ = [
    "LoopResult",
    "LoopRuntime",
    "LoopState",
    "MockLLM",
    "load_lss_spec",
    "ReflectionLoop",
    "ResearchLoop",
    "VerificationLoop",
    "MultiAgentLoop",
]
