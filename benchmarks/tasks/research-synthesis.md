# ALS-T1: Research Synthesis

**Task ID:** ALS-T1  
**Version:** 1.0  
**Suite:** Agent Loop Standard (ALS)  
**Primary LES Categories:** Effectiveness, Cost, Adaptability

---

## 1. Task Summary

Given a structured research question and a **fixed corpus** of documents (web snapshots, PDFs, markdown), the loop must produce a synthesis report that:

1. Answers all sub-questions in the task brief
2. Supports every factual claim with a citation to corpus ID
3. Flags contradictions between sources
4. Stays within word limit

This task measures **information-gathering loops** without open-ended web access (controlled O).

---

## 2. Loop Boundary

| Inside Loop | Outside Loop |
|-------------|--------------|
| Planner, reader, synthesizer agents | Corpus hosting infrastructure |
| Session memory, note extraction | Task fixture preparation |
| Citation validator tool | Human grading (automated E only) |
| Iteration controller | LLM API provider |

---

## 3. Goal Function

### 3.1 Components

| Component | Weight β | Measurement |
|-----------|----------|-------------|
| Claim accuracy | 0.45 | Fraction of claims matched to corpus (human-labeled gold) |
| Coverage | 0.30 | Fraction of required sub-questions addressed |
| Citation validity | 0.15 | Citations resolve to corpus IDs with supporting spans |
| Contradiction handling | 0.10 | Score 1 if contradictions flagged when present in gold |

### 3.2 Scalar Goal

```
G = 0.45 × accuracy + 0.30 × coverage + 0.15 × citation_valid + 0.10 × contradiction
```

All components ∈ [0, 1].

### 3.3 Targets

| Parameter | Value |
|-----------|-------|
| G_0 (typical) | 0.15–0.25 (outline only) |
| G_target | 0.80 |
| G_ceiling | 0.95 (human expert baseline) |

---

## 4. Task Brief Structure

Each instance includes:

```yaml
task_id: RS-2026-001
question: "What are the regulatory implications of EU AI Act Article 52 for open-source foundation model providers?"
sub_questions:
  - "Who qualifies as a provider vs. deployer?"
  - "What transparency obligations apply?"
  - "Are there exemptions for open-source releases?"
corpus_ids: [doc-001, doc-002, ..., doc-012]
word_limit: 1500
contradiction_present: true
```

**Corpus size:** 8–15 documents, 40–120 pages total.

---

## 5. Action Space

Allowed tools:

| Tool | Description |
|------|-------------|
| `list_documents` | Enumerate corpus |
| `read_chunk` | Fetch document section by ID + offset |
| `search_corpus` | Keyword/semantic search within corpus |
| `add_note` | Write structured note to session store |
| `update_outline` | Modify plan state |
| `draft_section` | Write report section |
| `validate_citations` | Check claim ↔ source linkage |
| `submit_report` | Terminal action triggering E |

Disallowed: external web, training data recall without citation, user clarification (benchmark mode).

---

## 6. Evaluator (E)

Automated pipeline:

1. **Claim extractor** — Split report into atomic claims
2. **Gold aligner** — Match to labeled claim set (BLEU-independent; entailment model + human audit on calibration set)
3. **Coverage checker** — Sub-question keyword + semantic rubric
4. **Citation resolver** — Verify corpus ID + span overlap ≥ threshold
5. **Contradiction checker** — Compare to gold contradiction flag

Human review only for **calibration runs** (not scored submissions).

---

## 7. Termination Conditions (τ)

Success τ:

- `submit_report` invoked AND `G ≥ G_target`

Failure τ:

- Iteration budget exhausted (T_budget = 30)
- Cost cap exceeded ($5.00)
- Wall-clock exceeded (45 min)
- 3 consecutive iterations with ΔG < 0.01 (stagnation)

---

## 8. Iteration Budget & Cost

| Parameter | Value |
|-----------|-------|
| T_budget | 30 |
| Expected T_actual (strong loop) | 12–22 |
| Cost cap | $5.00 USD normalized |
| Typical C_total (strong loop) | $1.50–3.50 |

Token pricing per [LES-1.0](../scoring/LES-1.0.md) defaults.

---

## 9. Perturbation Notes

| ID | Expected Degradation | Recovery Pattern |
|----|---------------------|------------------|
| P1 | Coverage ↓ (lost context) | Re-read corpus chunks |
| P2 | Bad search result | Cross-verify reads |
| P3 | Speed ↓ only if time-bound | Same G possible |
| P4 | Accuracy ↓ 10–20% | More read iterations |
| P5 | Coverage ↓ | Prioritize sub-questions |

---

## 10. Scalability Protocol

**Problem scale dimension** (not parallel):

| n | Modification |
|---|--------------|
| 1 | Standard 12-doc corpus |
| 2 | 24 documents, 2× sub-questions |
| 4 | 48 documents, 4× sub-questions |
| 8 | 96 documents, 8× sub-questions |

Same T_budget for all n (stress test).

---

## 11. OOD Holdout (RS-HOLD-01)

- **Domain shift:** Biomedical literature (drug interaction review)
- **Format shift:** PDF-only, no markdown
- **Constraint shift:** 800-word limit (vs. 1500)

Zero configuration changes permitted from primary runs.

---

## 12. Safety Checks

| Violation | Severity |
|-----------|----------|
| Fabricated corpus ID | Moderate (s=3) |
| Attempt external URL fetch | Severe (s=10) if bypass succeeds |
| PII in synthetic patient fixture mishandled | Severe |

---

## 13. Example Goal Trace

| Iteration | G_t | Event |
|-----------|-----|-------|
| 1 | 0.18 | Initial outline |
| 5 | 0.42 | 40% corpus read |
| 10 | 0.61 | First draft |
| 15 | 0.74 | Citations added |
| 18 | 0.83 | Contradiction section |
| 19 | 0.84 | submit_report |

---

## 14. Reference Scores

| System Class | G_final | LES (est.) |
|--------------|---------|------------|
| Single-shot long-context | 0.55 | 0.48 |
| Reflective research loop | 0.82 | 0.76 |
| Human analyst (4 hr) | 0.91 | 0.69 (Speed penalized) |

See [../scoring/examples/scoring-examples.md](../scoring/examples/scoring-examples.md) for calculation walkthrough pattern.

---

## 15. Fixture Access

Task fixtures distributed via benchmark package (when published):

```
benchmarks/fixtures/research-synthesis/
├── RS-2026-001/
│   ├── brief.yaml
│   ├── corpus/
│   └── gold-claims.json
```

Self-host: construct corpus from public regulatory PDFs with manual gold labeling (minimum 50 claims for valid E).

---

## 16. Submission Checklist

- [ ] 5+ primary runs on RS-2026-001..003
- [ ] Perturbation matrix (5 × 3 min runs)
- [ ] Scale n=1,2,4,8 on RS-2026-001
- [ ] OOD RS-HOLD-01 without config change
- [ ] Iteration JSON logs
- [ ] LES report with category breakdown
