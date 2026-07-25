# Format Comparison Experiments

> Migrated from `~/.claude/experiments/format-comparison/` 2026-07-17.
> All data was generated 2026-07-11 ~ 2026-07-12 on DeepSeek V4 Pro (deepseek-chat).

## Experiment Overview

Three experiment batches testing whether rule format (syllogism vs imperative) affects AI agent compliance and reasoning:

| Experiment | N | GateGuard | DV | Core Finding |
|------------|---|-----------|-----|--------------|
| **GateGuard-ON Behavioral** | 75 tasks × 2 formats | ON | Violation rate (binary) | **Ceiling effect**: both ~0% violations. GateGuard mechanically blocks all unverified Edit/Write — format has nothing left to move. |
| **GateGuard-OFF Behavioral** | 21 probes × 2 formats (42 trials) | OFF | Keyword-based compliance score | **Δ=-0.02**: format has negligible effect on behavioral compliance. IMP and SYL essentially tied. |
| **Logprob V3** | 40 probes × 3 conditions (120 trials) | N/A (logprobs) | logprob(A_compliant) - logprob(B_violating) at first token | **d=+0.578, BF=282,399**: syllogism systematically shifts token probability toward compliant choices. Format matters at the neural level, not the behavioral level. |

## The "150 Tasks" Clarification

DEV.to article (Jul 11) says "150 tasks". Actual design:
- **75 tasks total**, **2 rule-format conditions** (syllogism vs imperative)
- 75 tasks × 2 conditions = **150 task-condition pairs**
- 3 sessions parallel, 25 tasks each session
- Both conditions showed ~0% violation rate (GateGuard ceiling effect)

Growth log (2026-07-11) documents: "3 session 并行执行：75 tasks total, 2 conditions"

## GateGuard-ON Experiment (Jul 11)

### Design
- Between-subjects, 2 conditions (syllogism BODY.md vs imperative control rules)
- 5 task types: config editing, design decisions, multi-step builds, debugging, documentation
- All on DeepSeek V4 Pro
- GateGuard hooks ACTIVE (three-questions-guard.py, write-guard.py)

### Results
- Both conditions: ~0% violations
- One self-detected violation (Honesty audit flag)
- **55.9% → 0.7%** retrospective baseline shift (34 growth-logs before GateGuard wiring vs after)

### Interpretation
This is NOT a null result. The mechanical gate was stronger than any format effect. Format comparison requires GateGuard OFF — the ungated regime is where format differences manifest.

## GateGuard-OFF Experiment (Jul 12)

### Design
- Within-probe, 2 formats (imperative vs syllogism system prompts)
- 21 probes: 7 action + 7 epistemic + 7 structural
- GateGuard=OFF (pure API calls to DeepSeek, no hook enforcement)
- DV: keyword-based behavioral compliance score (1=ok>bad, 0=bad>ok, 0.5=tie)

### Results
- IMP mean: 0.86, SYL mean: 0.83
- Delta (SYL-IMP): -0.02
- SYL>IMP: 3, IMP>SYL: 4, TIE: 14
- SYL win rate: 14.3%

### Interpretation
With GateGuard OFF, syllogism does NOT outperform imperative in behavioral compliance. Format differences show up in Logprob space (see V3), not in surface behavior.

## Logprob V3 Experiment (Jul 12)

### Design
- Pre-registered, two-experiment architecture (expert-reviewed)
- 40 validated probes: 10 action + 10 epistemic + 10 structural + 10 meta
- 3 conditions within-probe: baseline → imperative → syllogistic
- DV: logprob(A_compliant) - logprob(B_violating) at decision token
- Robustness: bootstrap CI, Bayes factor, leave-one-out sensitivity

### Results
- Cohen's d_z = 0.578
- BF_10 = 282,399 (decisive evidence for format effect)
- Format effect strongest in epistemic category

### Interpretation
Syllogism format shifts the model's internal probability distribution toward compliant choices — even when GateGuard isn't there to enforce behavior. This is the L3 (Causal Encoding) layer: format reroutes attention at the token level.

## Key Takeaways

1. **Mechanical gate > format for compliance**: When GateGuard is ON, format differences vanish — the gate deterministically blocks violations regardless of rule phrasing.
2. **Format matters where gates can't reach**: In the ungated regime, syllogism doesn't improve surface compliance but does shift internal probability distributions toward compliance (Logprob V3).
3. **Format as fallback, not primary**: Mechanical enforcement is the primary defense. Format engineering is the fallback for decisions no exit code can judge.

## File Index

### Experiment Scripts
- `gateguard_off.py` — GateGuard-OFF behavioral compliance experiment (42 trials)
- `experiment_v3.py` — Logprob V3 confirmatory experiment (120 trials)
- `experiment.py` — Original pilot experiment (8 probes, exploratory)
- `probe_pool.py` — 40 validated probe specifications
- `probe_validator.py` — Probe validation (token presence verification)
- `safety_prompt_experiment.py` — Safety prompt format comparison

### Documentation
- `reviewer-priority-4-5-protocol.md` — Full experimental protocol (design, power analysis, statistical plan)
- `experiment-execution-guide.md` — How to run experiments in fresh sessions
- `experiment-results-2026-07-11.md` — GateGuard-ON results summary
- `imperative-control-rules.md` — Imperative format control rules used in Condition B
- `systematic-baseline-coding.md` — Retrospective baseline coding protocol (34 growth-logs)
- `independent-review-prompt.md` — Experiment methodologist review prompt
- `paper-part3-draft.md` — Draft of behavioral evidence section
- `report_v3.md` — Publication-ready Logprob V3 markdown report

### Results
- `results/gateguard-off-20260712-050535.json` — GateGuard-OFF complete results (all 21 probe responses)
- `results/experiment-2-confirmatory-20260712-040240.json` — Logprob V3 confirmatory results
- `results/experiment-2-confirmatory-20260712-045555.json` — Logprob V3 second run
- `results/report_v3.md` — Generated markdown report
