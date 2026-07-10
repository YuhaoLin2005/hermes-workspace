---
name: "paper-experiment-expansion"
metadata:
  node_type: memory
  originSessionId: 2ed8fc32-e900-4727-a0fb-f776c71d51ef
---
<!-- claim-gate:exists:paper-trial-results.md -->
<!-- claim-gate:count:paper-trial-results.md:T-0:8 -->
<!-- claim-gate:lines:paper-scoring-template.md:20 -->
---

# Paper Direction 2: Experiment Expansion Plan

> Generated 2026-07-10. Target: n=30→60, add multi-task-type design, formalize protocol.

## 1. Power Analysis Results

| Metric | n=30 | n=40 | n=60 |
|--------|------|------|------|
| Power at delta=30% (60%→90%) | 70.6% | 85% | **96.3%** |
| Power at delta=25% (60%→85%) | 49.2% | ~68% | **83.9%** |
| Power at delta=20% (60%→80%) | 29.7% | ~45% | 60.4% |
| 95% CI (OR) | [2.4, 64.3] | — | tightens ~3× |

**Conclusion**: n=60 target. At observed effect power=96.3%, even at conservative 25% delta power=83.9% ≥ 80%.

## 2. Task Design (30 tasks from paper-task-specs.md, re-listed for expansion planning)

### Domain A: Software Engineering (10 tasks) — core domain
1. Parse CSV and compute summary statistics in Python
2. Debug a race condition in async JavaScript
3. Refactor a 200-line React component
4. Write SQL migrations with foreign keys
5. Implement a rate limiter in Python
6. Write unit tests for an API endpoint
7. Design REST API schema for task management
8. Fix memory leak in Node.js Express server
9. Write Dockerfile for multi-stage Python build
10. Implement pagination for a list endpoint

### Domain B: Content Writing (5 tasks)
11. Write 300-word product launch announcement
12. Draft technical blog post about a bug fix
13. Write user-facing error messages (5 scenarios)
14. Reply to a critical customer review
15. Document a CLI tool's --config flag

### Domain C: Data Analysis (5 tasks)
16. Top 3 products by revenue from sales dataset
17. Interpret correlation matrix, identify confounders
18. Data cleaning pipeline for inconsistent date formats
19. Summary statistics + visualization plan for survey data
20. Identify anomalies in time-series server metrics

### Domain D: Strategic Reasoning (5 tasks)
21. Monolith vs microservices trade-off analysis
22. Prioritize feature backlog with resource constraints
23. Risk assessment of third-party API dependency
24. Design A/B test for landing page conversion
25. Create 3-month technical roadmap from product vision

### Domain E: Mixed (5 tasks)
26. Design doc + engineering effort estimate
27. User feedback analysis + prioritized bug report
28. Database schema + sample queries design
29. Monitoring dashboard spec + alert thresholds
30. Incident postmortem from raw timeline data

## 3. Classification Protocol (Formalized)

### 5-Category Scale
| Cat | Criteria | Binary |
|-----|----------|--------|
| 5 | All requirements met, no errors | Acceptable |
| 4 | 1-2 minor issues, functionally complete | Acceptable |
| 3 | Major parts work, significant gaps | Acceptable |
| 2 | Fundamentally wrong approach | Unacceptable |
| 1 | Wrong output / task misunderstood | Unacceptable |

### 3-Gate System
1. **Completeness Gate**: All task requirements addressed? (checklist)
2. **Correctness Gate**: Output technically correct? (functional)
3. **Quality Gate**: Follows domain best practices? (style/convention)

All 3 gates PASS → cat 4-5. ≥2 gates PASS → cat 3. Otherwise → cat 1-2.

### Randomization
- Odd-numbered tasks → Baseline (no framework)
- Even-numbered tasks → Treatment (framework)

## 4. Causal Swap Design

3 mutant architectures (1 layer randomized each):
- **Mutant A**: INTERFACE.md replaced with generic rules
- **Mutant B**: BODY.md replaced with minimal template
- **Mutant C**: Mechanical hooks all removed (soft-only)

10 tasks per mutant. Hypothesis: monotonic degradation per layer removal.

## 5. Pre-Registration (OSF/AsPredicted)
1. Primary: Framework improves acceptable rate (binary)
2. Secondary: Effect strongest in software engineering domain
3. N=60 (30 baseline + 30 treatment), power-justified
4. 5-category + 3-gate criteria defined before scoring
5. Fisher exact, two-sided, α=0.05
6. Exclusion: floor-effect tasks (neither condition valid)

## 6. Execution Plan

### Phase A — Now
- [ ] Run 10 new software engineering tasks (n=30→40)
- [ ] Score outputs using protocol
- [ ] Document all prompts + outputs + scores
- [ ] Recompute Fisher at n=40

### Phase B — This week
- [ ] Run remaining 20 tasks (n=60)
- [ ] Run 5 cross-domain tasks for generalization test
- [ ] Domain-stratified analysis

### Phase C — With second rater
- [ ] Independent scoring of all 60 outputs
- [ ] Cohen's kappa

### Phase D — Before professor
- [ ] Complete 4 blockers from pre-professor checklist
- [ ] Draft full paper
- [ ] Causal swap experiment (optional, lower priority)
