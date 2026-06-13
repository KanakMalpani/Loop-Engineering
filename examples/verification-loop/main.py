#!/usr/bin/env python3
"""
Verification Loop — Level 3 (Multi-Agent)
Implement → Test Oracle → Repair with verifier gate.

LSS mapping:
  loop_name: verification-loop-example
  workers: [implementer, verifier]
  evaluators: [test_oracle]
"""

from __future__ import annotations

import dataclasses
import textwrap
from typing import Callable


@dataclasses.dataclass
class CodeState:
    source: str
    iteration: int = 0
    patch_history: list[str] = dataclasses.field(default_factory=list)


MAX_ITERATIONS = 5

# Simulated buggy module source (string-based for portability)
INITIAL_SOURCE = textwrap.dedent("""
    def divide(a, b):
        return a / b  # bug: no zero check

    def normalize(values):
        total = sum(values)
        return [v / total for v in values]  # bug: empty list
""")


def run_tests(source: str) -> tuple[bool, list[str]]:
    """Test oracle: exec source and run assertions."""
    failures: list[str] = []
    namespace: dict = {}
    try:
        exec(source, namespace)
        divide = namespace["divide"]
        normalize = namespace["normalize"]

        try:
            divide(10, 0)
            failures.append("divide(10,0) should raise ZeroDivisionError")
        except ZeroDivisionError:
            pass

        if normalize([]) != []:
            failures.append("normalize([]) should return []")

        result = normalize([1, 2, 3])
        if abs(sum(result) - 1.0) > 1e-9:
            failures.append(f"normalize should sum to 1, got {sum(result)}")

    except Exception as e:
        failures.append(f"exec error: {e}")

    return len(failures) == 0, failures


def implementer(state: CodeState) -> str:
    """Apply progressive patches based on iteration."""
    patches = [
        # iter 1: symptom fix only (will be rejected by verifier)
        ("symptom", INITIAL_SOURCE.replace(
            "return a / b",
            "try:\n        return a / b\n    except ZeroDivisionError:\n        return 0",
        )),
        # iter 2: proper divide fix
        ("proper_divide", INITIAL_SOURCE.replace(
            "return a / b  # bug: no zero check",
            "if b == 0:\n        raise ZeroDivisionError('division by zero')\n    return a / b",
        )),
        # iter 3: add normalize fix
        ("proper_normalize", INITIAL_SOURCE.replace(
            "return a / b  # bug: no zero check",
            "if b == 0:\n        raise ZeroDivisionError('division by zero')\n    return a / b",
        ).replace(
            "return [v / total for v in values]  # bug: empty list",
            "if not values:\n        return []\n    total = sum(values)\n    return [v / total for v in values]",
        )),
    ]

    idx = min(state.iteration - 1, len(patches) - 1)
    label, source = patches[idx]
    state.patch_history.append(label)
    return source


def verifier(patch_label: str, test_failures: list[str]) -> tuple[bool, str]:
    """Reject symptom-only fixes."""
    if patch_label == "symptom":
        return False, "Symptom fix rejected: must raise on divide by zero, not return 0"
    return True, "Patch direction approved"


def run_verification_loop(
    initial: str = INITIAL_SOURCE,
    max_iterations: int = MAX_ITERATIONS,
) -> CodeState:
    state = CodeState(source=initial)

    while state.iteration < max_iterations:
        state.iteration += 1
        state.source = implementer(state)
        passed, failures = run_tests(state.source)
        patch_label = state.patch_history[-1]

        print(f"[iter {state.iteration}] patch={patch_label}")
        if failures:
            print(f"  test_oracle: FAIL — {failures}")
        else:
            print("  test_oracle: PASS")

        if passed:
            print("\n[OK] Terminated: all tests pass")
            break

        approved, msg = verifier(patch_label, failures)
        print(f"  verifier: {'APPROVE' if approved else 'REJECT'} — {msg}")
        if not approved:
            continue  # next iteration tries proper fix

    else:
        print("\n[WARN] Terminated: max_iterations reached")

    return state


def main() -> None:
    final = run_verification_loop()
    print("\n--- Final Source ---")
    print(final.source)
    print(f"\nMetrics: iterations={final.iteration}, patches={final.patch_history}")


if __name__ == "__main__":
    main()
