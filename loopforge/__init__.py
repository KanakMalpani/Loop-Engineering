"""LoopForge — scaffold valid LSS loop specifications from common patterns."""

from loopforge.builder import LoopBuilder
from loopforge.combine import LoopChain, combine_loops, compose_specs_many
from loopforge.compact import estimate_tokens, token_compare
from loopforge.patterns import Pattern

__all__ = [
    "LoopBuilder",
    "LoopChain",
    "Pattern",
    "combine_loops",
    "compose_specs_many",
    "estimate_tokens",
    "token_compare",
]
__version__ = "0.5.0"
