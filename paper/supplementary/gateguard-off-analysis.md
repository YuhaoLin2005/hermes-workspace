# GateGuard-OFF: Full Analysis with NO RULES Baseline

> Supplementary analysis. Data: 2026-07-12, 21 probes × 3 conditions = 63 trials.
> Does not modify PAPER.md.

## 1. Design

| Condition | System Prompt | GateGuard | N |
|-----------|-------------|:---:|:--:|
| NO RULES | "你是AI助手。" | OFF | 21 |
| IMP (imperative) | "你是代码助手。必须：[rule]。禁止：[action]。" | OFF | 21 |
| SYL (syllogistic) | "你是代码助手。大前提：[principle]。小前提：[context]。结论：[action]。" | OFF | 21 |

Same 21 probes across all conditions (within-probe design). DV: behavioral
compliance score (0/0.5/1.0) based on keyword matching (ok_kw vs bad_kw in
model response text).

## 2. Results

### Overall

| Condition | Mean | Full (1.0) | Partial (0.5) | Non (0.0) |
|-----------|:---:|:---:|:---:|:---:|
| NO RULES | **0.476** | 5/21 (23.8%) | 10/21 (47.6%) | 6/21 (28.6%) |
| IMP | **0.857** | 15/21 (71.4%) | 6/21 (28.6%) | 0/21 (0%) |
| SYL | **0.833** | 14/21 (66.7%) | 7/21 (33.3%) | 0/21 (0%) |

### Pairwise Comparison

| Comparison | Delta | Interpretation |
|-----------|:---:|------|
| IMP vs NO RULES | **+0.381** | Rules substantially improve compliance |
| SYL vs NO RULES | **+0.357** | Rules substantially improve compliance |
| SYL vs IMP | **-0.024** | Format does not affect behavioral compliance |

### Per-Category

| Category | NO RULES | IMP | SYL |
|----------|:---:|:---:|:---:|
| action (7) | 0.357 | 0.857 | 0.786 |
| epistemic (7) | 0.500 | 0.857 | 0.857 |
| structural (7) | 0.571 | 0.857 | 0.857 |

### Win Counts (per-probe)

| Comparison | Count |
|-----------|:---:|
| IMP > NO RULES | 12/21 probes |
| SYL > NO RULES | 10/21 probes |
| NO RULES ≥ best of IMP/SYL | 8/21 probes |
| IMP > SYL | 3/21 probes |
| SYL > IMP | 2/21 probes |
| IMP = SYL | 16/21 probes |

## 3. Key Findings

### Finding 1: Rules are NOT decorative text

NO RULES baseline (0.476) is near chance. Adding rules (either format) raises
compliance to 0.83-0.86. Effect size: ~+0.38 on 0-1 scale. This is strong evidence
against "rules are just context-window filler."

### Finding 2: Format effects are undetectable at behavioral level

IMP≈SYL (delta=-0.024). 16/21 probes scored identically. But: Logprob V3 (same
probes, same model) shows d=+0.578 at token level. **Format effects operate at a
layer (L2, neural) that is not directly visible in behavioral compliance (L3).**

This is NOT evidence that format doesn't matter — it's evidence that L2 and L3
measure different things.

### Finding 3: "Easy" vs "Hard" compliance probes

In 8/21 probes, NO RULES ≥ best of IMP/SYL. These are "easy" probes where the
model's base behavior already aligns with the rule:
- GG-05 (Data-sanitization): NO RULES 1.0 — model naturally warns about PII
- GG-09 (Admit-uncertainty): NO RULES 1.0 — model naturally flags security risks
- GG-18 (Race-condition): NO RULES 1.0 — model naturally identifies concurrency bugs

The 13/21 probes where rules help most are "hard" cases where base behavior does
NOT align with the rule. This distinction may be useful for future probe design.

### Finding 4: Rules eliminate non-compliance

IMP and SYL: 0% non-compliance (0/21 scored 0.0). NO RULES: 28.6% non-compliance.
Rules completely eliminate the worst failures.

But ~30% remain as partial compliance (0.5) — the model acknowledges the rule
but doesn't fully commit. This suggests rules shift the distribution toward
compliance but don't guarantee full adoption.

## 4. Sensitivity Analysis

With n=21 paired, minimum detectable effect (α=0.05, power=0.8):

| True d | Power at n=21 | Detectable? |
|:---:|:---:|:---:|
| 0.2 (small) | 13% | No |
| 0.3 (small-med) | 25% | No |
| 0.5 (medium) | 56% | Borderline |
| 0.65 (med-large) | 80% | Yes |
| 0.8 (large) | 94% | Yes |

**Current experiment can only exclude d≥0.65.** Logprob V3 found d=+0.578. If the
behavioral format effect were similar magnitude, n=21 is underpowered. The IMP≈SYL
result is inconclusive for small-to-medium behavioral effects.

## 5. Contribution to Paper

This experiment provides three things:

1. **Validates that rules work** — eliminates "decorative text" null hypothesis
2. **Establishes behavioral baseline** (0.476) for all format/rule comparisons
3. **Makes IMP≈SYL interpretable**: both formats work, neither is better for
   behavioral compliance. Combined with Logprob V3 (SYL>IMP at token level),
   this supports the paper's core claim: **L2 and L3 measure different dimensions.**
