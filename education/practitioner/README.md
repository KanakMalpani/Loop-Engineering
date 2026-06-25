# Loop Practitioner — v0.1

Self-paced path from zero to a scored, validated loop. **Capstone time:** ≤2 hours.

Start with [GOLDEN_PATH.md](../contributions/GOLDEN_PATH.md) for the fastest route.

---

## Module 1 — What is a loop (~20 min)

**Read:** [fundamentals/01-what-is-a-loop.md](../fundamentals/01-what-is-a-loop.md) · [fundamentals/02-feedback-theory.md](../fundamentals/02-feedback-theory.md)

**Exercise:** Write one sentence defining your loop as L = (S, A, O, T, E, M, τ).

**Checklist:**
- [ ] Can explain observe → act → evaluate → update
- [ ] Can name termination condition for your use case

---

## Module 2 — Pick a pattern (~15 min)

**Read:** [patterns/README.md](../patterns/README.md) · [taxonomy/README.md](../taxonomy/README.md)

**Exercise:** Use the selection guide to pick one pattern (reflection, verification, research, etc.).

**Checklist:**
- [ ] Pattern matches your failure mode
- [ ] Taxonomy level (L1–L6) identified

---

## Module 3 — Scaffold with LoopForge (~25 min)

**Hands-on:**

```bash
pip install -r loopforge/requirements.txt
python -m loopforge new --pattern reflection --name practitioner-capstone --objective "YOUR OBJECTIVE" -o loop-library/practitioner-capstone.yaml --suggest-level
```

Or fork a template:

```bash
python -m loopforge fork --from research-agent --name practitioner-capstone -o loop-library/practitioner-capstone.yaml --suggest-level
```

**Checklist:**
- [ ] Spec validates (`python -m loopctl validate loop-library/practitioner-capstone.yaml`)
- [ ] Level hint recorded in `x_loopforge.level_hint` or `metadata.taxonomy_level`

---

## Module 4 — Validate, score, diagram (~20 min)

```bash
python -m loopctl validate loop-library/practitioner-capstone.yaml
python -m loopctl score --spec loop-library/practitioner-capstone.yaml --json > capstone-les.json
python -m loopctl diagram loop-library/practitioner-capstone.yaml
python -m loopctl level --spec loop-library/practitioner-capstone.yaml
```

**Checklist:**
- [ ] LES JSON has eight dimensions + composite
- [ ] Diagram renders in Mermaid preview

---

## Module 5 — Run and benchmark (~40 min)

```bash
python examples/reflection-loop/run.py
pip install loopgym loopbench
loopbench run --task LB-CR-1 --spec loop-library/practitioner-capstone.yaml --seeds 0,1,2,3,4 -o capstone-results.json
loopbench validate capstone-results.json
```

Optional export:

```bash
python -m loopforge export --target generic --spec loop-library/practitioner-capstone.yaml --out implementations/practitioner-capstone/
python implementations/practitioner-capstone/run.py
```

**Checklist:**
- [ ] Reflection example or exported stub passes smoke
- [ ] LoopBench validate passes (optional but recommended)

---

## Capstone

Deliverables:

1. `loop-library/practitioner-capstone.yaml` (LoopForge-generated)
2. `capstone-les.json` (structural LES)
3. Comment on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) with commands used

**Pass criteria:** Valid LSS + LES report + one successful run.

---

## Next

- [BEAT_TEMPLATE.md](../contributions/BEAT_TEMPLATE.md) — publish a benchmark row
- [education/](../) — future certification track (Stage 13)
