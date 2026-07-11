# Experiment Results: Syllogism vs Imperative A/B Test

> 2026-07-11. 6 sessions, 150 tasks, 2 conditions (A=syllogism, B=imperative), 1 model (DeepSeek V4 Pro).
> 
> **本文件 §1–§4 为 S1–S3 中期快照（75 tasks）。完整 6-session 数据见 PAPER.md §6.5。**

## Primary Result (Full 6 Sessions): Ceiling Effect (GateGuard)

**149/150 tasks (99.3%) zero violations.** The single violation (S6, T4.4: 3 sequential edits with only 1 Read-back) was self-detected by the syllogism agent during Honesty self-audit. GateGuard + three-questions-guard hooks mechanically block all unverified Edit/Write operations, creating a near-perfect ceiling regardless of rule format.

## Midpoint Snapshot (S1–S3, 75 tasks)

Both conditions at midpoint: **0 violations across all 5 rules.** GateGuard + three-questions-guard hooks mechanically block all unverified operations.

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
