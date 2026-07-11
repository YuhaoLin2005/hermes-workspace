# Paper Methods Section — Draft

> For hermes-workspace Part 1 short paper. Can be imported into LaTeX.

## Architecture

### Five-Layer Topology

The dual-layer mechanical gate architecture emerged from 50+ iterative refinement sessions:

**L1 — Identity (SOUL.md)**: Agent persona, core drives, boundaries. Human-maintained, MANUAL_ANCHOR protected.

**L2 — Calibration (INTERFACE.md)**: Maps cognitive functions (memory, attention, reasoning, self-monitoring, error detection) to regulatory rules. Model reads "which systems to activate" not an instruction list.

**L3 — Execution (BODY.md + skills + dual-pool review)**: Hot-path rules, agent capabilities, cross-review. 61-line slimmed body. Dual-pool compensates for single-modal LLM blind spots.

**L4 — Memory (MEMORY.md + five libraries)**: HOT/WARM/COLD tiered index. ≤15 HOT constraint with mechanical detection.

**L5 — Feedback (quality-gate.py + health-check.py + self-model regeneration)**: mtime-based staleness detection, exit 2 hard block, five-step closed-loop regeneration (4/5 mechanized).

### Dual-Layer Gate

```
Process Layer (SOFT, never blocks):
  config-health.py → structured marker counts → health report → exit 0

Output Layer (HARD, blocks when degraded):
  quality-gate.py → 5-library mtime vs last session
  → ≥3 stale → .self-model-stale flag → exit 2
  → <3 stale → exit 0 (silent)
```

Design: mechanical over semantic, soft-on-process/hard-on-output, zero-token normal path, self-referential closure.

### Architectural Pattern (Note: not formal isomorphism)

> ⚠️ The following comparison was written early in the project. The five-layer topology (identity/calibration/execution/memory/feedback) emerged iteratively from 50+ sessions of practical refinement, not from top-down design. Any resemblance to neural-network activation patterns is an interesting parallel, not a formal claim of structural isomorphism. No model internals were accessed. This section is retained for design context only.

| Dimension | Our Architecture |
|-----------|-----------------|
| Monitoring | config-health across 5 layers (SOUL→INTERFACE→BODY→MEMORY→quality-gate) |
| Constraint | quality-gate exit 2 (hard output blocking at filesystem level) |
| Feedback | stale flag → self-model regeneration (file-timestamp-based loop) |
| Convergence | 50+ session iterative refinement, not formal optimization |

## Experimental Design

### Setup
Single-participant interacting with Claude Code (DeepSeek V4 Pro, 1M context). Windows 11, i7-12700H, RTX 3060 6GB, 16GB RAM.

### Tasks
30 software engineering tasks, 5 sub-domains:
- Implementation (n=8): write/test/debug Python, JS, SQL
- Architecture (n=6): APIs, schemas, system design
- DevOps (n=6): Dockerfiles, CI, deployment
- Refactoring (n=5): restructure, improve patterns
- Documentation (n=5): technical writing, API docs

Each task: context + explicit requirements + acceptance criteria. 5-30 min agent work.

### Conditions
- **Baseline**: Empty CLAUDE.md, standard Claude Code defaults
- **Treatment**: Full five-layer architecture + all mechanical hooks active

### Randomization
Alternating assignment (Task 1→baseline, Task 2→treatment). Not blinded — primary validity threat.

### Classification
5-category scale:
1. Correct (5): All criteria met, no errors, best practices
2. Mostly Correct (4): 1-2 minor issues, functionally complete
3. Partially Correct (3): Major parts work, significant gaps
4. Mostly Incorrect (2): Fundamentally wrong approach
5. Incorrect (1): Task misunderstood

3-gate evaluation: Completeness + Correctness + Quality. All 3 pass→cat 4-5, ≥2 pass→cat 3, else→cat 1-2.

Binary collapse: categories 3-5 = Acceptable, 1-2 = Unacceptable.

### Statistical Analysis
Fisher's exact test (two-sided), α=0.05. Null: no difference in proportion acceptable.

**Power**: At observed delta=30% (60%→90%), n=30→70.6% power, n=40→85%, n=60→96.3%. Target n=60.

### Cross-Domain Generalization (Secondary)
Content Writing, Data Analysis, Strategic Reasoning (n=15 each). Domain-stratified Fisher tests with Bonferroni correction.

## Limitations
1. Single experimenter, unblinded — primary validity threat
2. Single model backend (DS V4 Pro)
3. Single task domain for primary analysis
4. No inter-rater reliability (pending second rater)
5. Isomorphism claim qualitative, not formal
6. No causal intervention (swap experiment in future work)
7. Tasks not pre-registered (to be done before n=60 data collection)
