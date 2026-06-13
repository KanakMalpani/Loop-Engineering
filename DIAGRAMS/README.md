# Diagram Index

Centralized Mermaid diagrams for the Loop Engineering repository.

---

| Diagram | File | Used In |
|---------|------|---------|
| Loop Anatomy | [loop-anatomy.mmd](loop-anatomy.mmd) | fundamentals/01 |
| Taxonomy Tree | [taxonomy-tree.mmd](taxonomy-tree.mmd) | taxonomy/ |
| D-D-M-I-S Framework | [dd-mis-framework.mmd](dd-mis-framework.mmd) | framework/ |
| Feedback Flow | [feedback-flow.mmd](feedback-flow.mmd) | fundamentals/02 |
| Multi-Agent Architecture | [multi-agent-architecture.mmd](multi-agent-architecture.mmd) | patterns/ |
| LSS Structure | [lss-structure.mmd](lss-structure.mmd) | standards/ |

## Generate from Spec

```bash
python tools/loop_diagram_generator.py loop-library/coding-agent.yaml -o diagrams/generated/coding-agent.mmd
```

## Conventions

- `flowchart TB` for hierarchies
- `flowchart LR` for pipelines
- Subgraphs for loop boundaries
- Dotted lines for async/human paths
## Related

- [taxonomy/README.md](../taxonomy/README.md) — level definitions
- [loop-library/](../loop-library/) — specs with inline diagrams
- [standards/LSS-1.0.md](../standards/LSS-1.0.md) — schema reference
## Related

- [taxonomy/README.md](../taxonomy/README.md) — level definitions
- [loop-library/](../loop-library/) — specs with inline diagrams
- [standards/LSS-1.0.md](../standards/LSS-1.0.md) — schema reference
