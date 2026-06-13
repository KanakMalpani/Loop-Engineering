# Loop Engineering Style Guide

Documentation and LSS writing conventions for the Loop Engineering repository.

This guide ensures readers experience **one voice**: precise, engineering-first, evidence-aware, and free of hype. Apply it to Markdown, YAML specs, comments in tools, and PR descriptions.

---

## Voice and Tone

### Do

- Write in **clear declarative prose**. Prefer "The evaluator must be independent" over "It's really important that evaluators aren't the same as actors."
- Use **active voice** for procedures: "Run the validator" not "The validator should be run."
- State **assumptions and limits** explicitly.
- Distinguish **normative** (must/shall for standards) from **informative** (should/may for guidance).
- Acknowledge uncertainty: "Open problem," "hypothesis," "partial result."

### Avoid

- Marketing superlatives: "revolutionary," "game-changing," "unprecedented" without evidence
- Vague futurism without falsification criteria
- Anthropomorphizing models ("the AI wants") — use loop roles (actor, evaluator, policy)
- TODO/FIXME placeholders in published docs — use open-problem links instead
- Emoji in normative standards (acceptable sparingly in README navigation)

---

## Terminology

Use consistent terms across the repository:

| Preferred | Avoid | Notes |
|-----------|-------|-------|
| Loop | Agent workflow (unless discussing agents specifically) | Loop is the formal object |
| LSS | YAML config, prompt file | When referring to spec standard |
| Evaluator E | Judge, critic (ok in pattern names) | Map to E in formal sections |
| Termination τ | Stop condition, exit | Formal symbol on first define |
| Actor / worker | Agent (ok in LSS `workers:`) | Role in A |
| Charter | System prompt alone | Human/org governance layer |
| LES dimension | Metric, score alone | Specify which of 8 |
| Taxonomy level | Tier (ok informally) | Levels 1–6 defined |
| Meta-loop | Self-improvement (when k≥2) | See recursive-self-improvement.md |

**First mention rule:** spell out "Loop Specification Standard (LSS)" then use LSS.

---

## Markdown Structure

### Document header

Every major doc starts with:

```markdown
# Title

*Optional subtitle or revision note*

One-paragraph abstract stating purpose and audience.
```

Research docs include `Last revised:` when updated substantively.

### Headings

- One H1 per file
- No skipped levels (H2 → H3, not H2 → H4)
- Sentence case for headings: "Loop composition algebra" not "Loop Composition Algebra" (except proper nouns: LSS, LES, GitHub)

### Sections for long documents

Use horizontal rules `---` sparingly between major parts.

End research/policy docs with a centered epigraph line:

```markdown
<p align="center"><em>Short memorable principle.</em></p>
```

### Lists

- Use bullets for unordered insights
- Use numbered lists for sequential procedures
- Keep list items parallel in grammar

### Tables

- Header row required
- Align conceptual columns left
- Use tables for comparisons, not prose paragraphs in cells

---

## Code and Diagrams

### Code fences

- Always specify language: `yaml`, `bash`, `python`, `mermaid`
- Keep examples **minimal but runnable** where claimed
- LSS examples must validate against current schema when marked `valid`

### Mermaid

- Prefer `flowchart TB` or `LR` for loop diagrams
- Node IDs alphanumeric; labels in quotes if special chars
- One diagram per conceptual layer; split if >15 nodes

### File paths

- Repo-relative in links: `[LSS 1.0](../standards/LSS-1.0.md)`
- Backticks for path mentions: `loop-library/coding-agent.yaml`

---

## LSS (YAML) Style

### File naming

- kebab-case: `autonomous-debugger.yaml`
- Version in spec body, not filename

### Structure order

```yaml
loop_name: example-loop
version: "1.0"
objective: "Single sentence measurable goal"
level: 2
charter_ref: optional/path.yaml
workers: []
evaluators: []
memory: {}
termination_conditions: []
budget: {}
telemetry: {}
```

### Field conventions

- **loop_name:** lowercase hyphenated, matches filename
- **objective:** one sentence; verifiable outcome, not implementation
- **workers.role:** snake_case nouns: `implementer`, `critic`, `orchestrator`
- **evaluators.type:** snake_case from allowed enum; document new types via RFC
- **termination_conditions:** most strict first; `max_iterations` always present in production profiles

### Comments

YAML `#` comments for non-obvious fields only; do not restate schema docs.

### Strings

- Double quotes for version numbers: `version: "1.0"`
- Avoid multiline strings unless embedding prompts; prefer `prompt_ref:` to separate files

---

## Mathematical Notation

Loop tuple on first formal appearance:

```
L = (S, A, O, T, E, M, τ)
```

- Italics in prose: state space S, not `$S$` in Markdown unless using MathJax (repo default: plain text symbols)
- Operators: composition `∘`, parallel `∥`, sequential "then"
- Open problem IDs: `LE-OP-NN` monospace

---

## Evidence Language

Tag claims explicitly:

| Phrase | Meaning |
|--------|---------|
| **Demonstrated** | Benchmark + public artifact |
| **Replicated** | Independent reproduction cited |
| **Theorized** | Formal argument, no production proof |
| **Conjectured** | Hypothesis with stated falsification test |

Example: "**Theorized:** sequential composition is associative when adapters commute."

---

## Safety and RSI Language

When discussing Level 5–6:

- Always mention **tier**, **bounded modification set**, or **containment** in same section as capability claims
- Do not instruct bypass of human charter or evaluators
- Prefer "research sandbox" over "deploy" for meta-loops

---

## Citations and Links

- Link to internal docs over external when equivalent exists
- External links: full URL, reputable sources
- BibTeX in [CITATION.md](./CITATION.md); inline cite as (Loop Engineering Community, 2026)

---

## Inclusive Language

- Gender-neutral they/them for hypothetical engineers
- Avoid ableist metaphors ("sanity check" → "consistency check")
- Acronyms expanded on first use in each document

---

## PR and Commit Messages

**Commits:** imperative mood, ≤72 char subject

```
Add pattern: adversarial eval gate
Fix LSS validator termination enum
```

**PR titles:** same as commit subject style

**Bodies:** complete sentences; include evidence per CONTRIBUTING.md template

---

## Review Checklist (Self-Edit)

Before submitting:

- [ ] Terminology matches this guide
- [ ] All code/YAML blocks labeled
- [ ] Links relative and working
- [ ] Claims tagged with evidence tier where non-obvious
- [ ] No TODO markers
- [ ] Safety sections present for L5–L6 content
- [ ] Spelling US English (organization, behavior, analyze)

---

## Exceptions

- **Manifesto** may use rhetorical flourishes not allowed in standards
- **Case studies** may quote external sources verbatim with attribution
- **CHANGELOG** may use terse bullet fragments

---

<p align="center"><em>Write so the next engineer can specify, score, and reproduce.</em></p>
