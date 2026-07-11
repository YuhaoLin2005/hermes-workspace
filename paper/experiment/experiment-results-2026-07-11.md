# Experiment Results: Syllogism vs Imperative A/B Test

> 2026-07-11. 3 sessions, 75 tasks, 2 conditions, 1 model.

## Primary Result: Ceiling Effect (GateGuard)

Both conditions: **0 violations across all 5 rules.** GateGuard + three-questions-guard hooks mechanically block all unverified operations — creating a ceiling that masks any format effect.

## Secondary: Reasoning Style

| Imperative | Syllogism |
|---|---|
| "Q1/Q2/Q3" checklist | "大前提: Write不可逆…我需要判断…" |
| "CCGH completed" label | "大前提: 生成/验证同通道→自审结构性不可靠" |

Both comply. Syllogism embeds compliance in causal understanding; imperative performs compliance as procedural task.

## Architecture Validation

**Layer 1 (mechanical gate) is effective.** Compliance = 100% when hooks enforce mechanically. This is evidence for the thesis core claim: "mechanical over semantic."

**Format effects require GateGuard OFF to isolate.** Next: replicate with `ECC_GATEGUARD=off`.

## Confounds
1. GateGuard ceiling effect
2. Cross-session filesystem pollution (S1 edits visible to S2/S3)
3. Self-scoring (no independent rater)
4. Pre-existing file modifications by linter/external processes
