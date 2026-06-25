"""Named loop patterns aligned with Loop Engineering pattern docs."""

from __future__ import annotations

from enum import Enum


class Pattern(str, Enum):
    """High-level loop archetypes LoopForge can scaffold."""

    SIMPLE = "simple"
    REFLECTION = "reflection"
    VERIFICATION = "verification"
    RESEARCH = "research"

    @classmethod
    def choices(cls) -> list[str]:
        return [p.value for p in cls]

    @classmethod
    def from_str(cls, value: str) -> Pattern:
        normalized = value.strip().lower().replace("_", "-")
        aliases = {
            "echo": cls.SIMPLE,
            "reflect": cls.REFLECTION,
            "reflection-loop": cls.REFLECTION,
            "verify": cls.VERIFICATION,
            "verification-loop": cls.VERIFICATION,
            "research-loop": cls.RESEARCH,
        }
        if normalized in aliases:
            return aliases[normalized]
        try:
            return cls(normalized)
        except ValueError as exc:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Unknown pattern {value!r}. Choose one of: {valid}") from exc
