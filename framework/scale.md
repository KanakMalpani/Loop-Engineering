# Scale Phase

Scale deploys validated loops from single-run experiments to fleet operation under cost, safety, and observability constraints.

---

## Scale Readiness Gates

| Gate | Criterion |
|------|-----------|
| Spec frozen | LSS version tagged; no experimental fields |
| LES floor | Composite ≥ target for domain (typically 65+) |
| Safety | All critical constraints tested; kill switch verified |
| Cost | Per-run and cumulative limits enforced in runtime |
| Observability | Metrics, logs, state persistence defined |
| Failure playbook | Top 5 failure modes documented with response |

---

## Horizontal Scale

**Many independent runs** (e.g., one loop per repo, per ticket):

- Idempotent workers; external memory with clear ownership
- Queue + worker pool; rate limits per cost_limits
- Central LES dashboard aggregated from run artifacts

---

## Vertical Scale

**Richer loops** (more workers, deeper taxonomy):

- Complexity analyzer score < 80 before production
- Staged rollout: Level N proven before Level N+1
- Human-in-loop for evaluators until automated eval matches human judgment

---

## Multi-Tenant Scale

- Namespace loop_name per tenant
- Safety constraints include tenant isolation rules
- Separate cost_limits per tenant; global circuit breaker

---

## De-Scale / Kill Criteria

Roll back or disable when:

- Safety constraint violated (any severity: critical)
- Cost overrun > 2× budget for 24h
- Effectiveness drops > 15 LES points week-over-week
- Evaluator divergence (automated vs human) > agreed threshold

---

## Operations Checklist

- [ ] Runtime injects cost_limits before each cycle
- [ ] State persisted for audit (`memory` block)
- [ ] Alerts on termination_reason = cost_limit
- [ ] Weekly LES sample on production traffic
- [ ] Quarterly spec review against taxonomy roadmap

See [dd-mis-checklists.md](dd-mis-checklists.md) for role-specific lists.
