# Core Principles of Loop Engineering

Ten principles that govern the design, evaluation, and improvement of feedback systems.

---

## 1. Closure Before Capability

A loop that cannot verify its own success is not a loop—it is a chain of hope.

**Rule:** Every loop must define an evaluator that returns structured, verifiable signal independent of the actor's self-assessment.

---

## 2. State Lives Outside the Model

Language models forget. Loops remember via external state.

**Rule:** Persist progress, failures, decisions, and metrics to durable storage every cycle. Never rely on context window as memory.

---

## 3. Termination Is Designed, Not Discovered

Unbounded loops are resource attacks on yourself.

**Rule:** Specify termination conditions (goal met, max iterations, budget exhausted, safety triggered) before the first execution.

---

## 4. Separate Actor from Evaluator

The implementer must not grade its own homework.

**Rule:** Use distinct roles, prompts, or models for action and evaluation. Maker-checker is the default, not the exception.

---

## 5. Measure What Matters

If you cannot score the loop, you cannot improve it.

**Rule:** Apply Loop Engineering Score (LES) to every production loop. Track effectiveness, cost, robustness, and safety over time.

---

## 6. Failures Are Data

Every loop failure is a diagnostic signal, not a dead end.

**Rule:** Classify failures using the [Failure Taxonomy](../standards/failure-taxonomy.md). Feed failure modes back into loop design.

---

## 7. Complexity Earns Its Place

Higher taxonomy levels (evolutionary, self-modifying, meta) cost more tokens, latency, and failure modes.

**Rule:** Use the simplest loop level that achieves the objective. Escalate only when LES or task complexity demands it.

---

## 8. Safety Is Specification

Constraints are not guardrails added after deployment—they are fields in the loop spec.

**Rule:** Include `safety_constraints` in every LSS document. Hard-stop on violation; never warn-and-continue for critical constraints.

---

## 9. Patterns Over Reinvention

The loop you need probably exists in the pattern library.

**Rule:** Start from a documented pattern. Customize via LSS. Contribute improvements back.

---

## 10. Loops Compose

Complex systems are graphs of simpler loops, not monolithic prompts.

**Rule:** Design loops as composable units with explicit inputs, outputs, and feedback channels. Document interfaces in LSS.

---

→ [Manifesto](MANIFESTO.md) · [Fundamentals](../fundamentals/README.md) · [Patterns](../patterns/README.md)
