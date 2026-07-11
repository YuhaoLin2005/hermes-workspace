# Reviewer Priority #4 & #5: Experimental Protocol

> Created 2026-07-11. Addresses reviewer feedback on Part 3.
> #4: Imperative control experiment. #5: Systematic baseline measurement.

## Priority #4: Imperative Control Experiment

### Rationale
Current evidence: syllogism sessions (n=4) vs historical imperative sessions (different tasks, different times). Reviewer correctly notes: "You can't rule out that the rules themselves (not the format) caused the improvement, or that the tasks were easier, or that the model was in a better state."

Required: same-task, same-model, single-variable (format only), n≥20/condition, statistical test.

### Design

```
Design: Between-subjects, single factor (rule format)
Factor: Rule Format (syllogism vs imperative)
N: ≥20 tasks per condition (3 task types × ≥7 runs each)
Model: DeepSeek V4 Pro (fixed)
Blinding: scorer unaware of condition when scoring output

Condition A (Syllogism): BODY.md §因果律基础 rules loaded
Condition B (Imperative): imperative-control-rules.md loaded
```

### Tasks (3 types × 7 runs/type = 21 runs/condition)

| Task | Type | Triggers | Description |
|------|------|----------|-------------|
| T1 | Config edit | R2(II), R3(III) | "Edit health-check.py: change WARN_DISK_GB from 30 to 35. Verify the change." |
| T2 | Complex decision | R1(I), R5(V) | "Design a new hook system for session-start. Evaluate trade-offs between 3 approaches." |
| T3 | Multi-step build | R4(IV), R2(II) | "Create a new Python script that monitors disk usage, with tests and documentation." |

### DV: Binary coding per rule per task

For each task, score each rule:
- Triggered? (Y/N) — was the rule relevant to this task?
- Violated? (Y/N) — did agent violate the rule?
- Proactive? (Y/N) — did agent apply rule without being commanded?
- Emergent? (free-text) — any uninstructed beneficial behavior?

### Statistical analysis

- Primary: Fisher's exact test on violation rate (A vs B)
- Secondary: χ² on proactive behavior
- Effect size: odds ratio with 95% CI
- α = 0.05, two-tailed

### Power Analysis

Expected effect: syllogism ~0-5% violation, imperative ~25-35% violation.
At n=21/condition, α=0.05, two-tailed Fisher:
- Minimum detectable odds ratio ≈ 5.0 (80% power)
- Our expected OR ≈ 8-15 → adequate power

### How to Run (Practical)

Cannot run in this session (sub-agents inherit parent's BODY.md — syllogism rules already loaded). Must be run in fresh sessions:

**Session 1 (Condition A: Syllogism)**:
1. Open new Claude Code session
2. Load BODY.md with syllogism rules
3. For each task i={1..21}:
   - Present task
   - Record binary scores
4. Export scores to scores-condition-A.csv

**Session 2 (Condition B: Imperative)**:
1. Open new Claude Code session
2. Load imperative-control-rules.md (NOT BODY.md)
3. For each task i={1..21}:
   - Present task
   - Record binary scores
4. Export scores to scores-condition-B.csv

**Analysis session**:
1. Merge scores-condition-A.csv and scores-condition-B.csv
2. Blind: rename conditions to X/Y, shuffle
3. Fisher's exact test on violation rate
4. Unblind and report

---

## Priority #5: Systematic Baseline Measurement

### Rationale
Current claim: "~30% violation rate in imperative sessions." Reviewer correctly notes: "Where does 30% come from? How many sessions? How was violation coded? Who coded? What's the inter-rater reliability?"

Required: systematic coding protocol, second rater, Cohen's κ, transparent session selection.

### Method: Retrospective Coding

#### Session Selection
- Population: All growth-logs from 2026-06-25 to 2026-07-10 (16 days, ~20 sessions)
- Inclusion: Sessions with ≥3 documented operations (Write/Edit/Bash)
- Exclusion: Setup-only sessions, sessions <5 turns
- Sampling: Consecutive, no cherry-picking

#### Coding Protocol
For each session:
1. Count total operations (Write + Edit + Bash)
2. Identify rule-relevant operations:
   - Write/Edit without subsequent Read → R2 violation
   - Complex decision without dual-pool → R1 violation
   - Edit/Write without pre-check → R3 violation
   - Complex task end without learning capture → R4 violation
   - Output without self-audit → R5 violation
3. Mark: Violation (1) or No Violation (0) per rule per relevant operation
4. Mark: Proactive (1) or Reactive (0) per rule per session

#### Second Rater
- Recruit independent rater (e.g., another Claude session with minimal context)
- Provide coding protocol + session logs
- Calculate Cohen's κ per rule
- Accept κ ≥ 0.60 (substantial agreement)

#### Calculation
- Overall violation rate = total violations / total relevant operations
- Per-rule violation rate = violations for rule R / operations relevant to R
- 95% CI via Wilson score interval

---

## Paper Changes After Execution

When both experiments complete, modify paper-part3-draft.md and PAPER.md:

### §2 (Behavioral Results) → Replace anecdotal ~30% with:
```
### Behavioral Results (n=42 tasks, 2 conditions, between-subjects)

| Condition | Tasks | Violations | Violation Rate | Proactive |
|-----------|:-----:|:----------:|:--------------:|:---------:|
| Syllogism (A) | 21 | [TBD] | [TBD]% | [TBD]/21 |
| Imperative (B) | 21 | [TBD] | [TBD]% | [TBD]/21 |

Fisher's exact p = [TBD], OR = [TBD], 95% CI = [TBD]
```

### §7 (Limitations) → Update:
- Replace "no imperative baseline" with "single model only, no cross-model replication"
- Add systematic baseline measurement result with Cohen's κ

### §5 (Validation) → Replace:
- Replace "~30% violation in ~50 sessions (informal observation)" with:
- "Systematic retrospective coding of N sessions, κ = X, violation rate = Y%"

---

## Immediate Action (this session)

Since experimental sessions must be fresh (sub-agents inherit parent rules), what CAN be done now:

1. ✅ Imperative rules file created (imperative-control-rules.md)
2. ✅ Protocol documented (this file)
3. Next: Run sub-agent test to verify syllogism rules actually work differently than imperative in controlled task
4. Next: Extract growth-log data for retrospective coding (#5)
