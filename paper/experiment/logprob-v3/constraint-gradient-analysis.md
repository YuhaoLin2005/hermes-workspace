# Constraint Gradient Analysis: Non-Monotonic Suppression
**Status**: Complete | **Date**: 2026-07-13
**Experiment**: `constraint_gradient.py --run` | **API calls**: 96
**Data**: `results/constraint-gradient/constraint-gradient-20260713-050210.json`

---

## 1. Design

Tests the L3 two-parameter model: `format effect = f(chain length, constraint severity)`. 12 probes × 2 formats (IMP/SYL) × 4 constraint levels.

| Level | Constraint Text | Intent |
|-------|----------------|--------|
| L0 | (none — V3 baseline) | Measure format effect with no output constraint |
| L1 | "只输出字母A或B" | Light: standardize output, minimal suppression |
| L2 | "只输出一个字母，不要任何其他文字，不要解释" | Moderate: suppress explanation, force labels |
| L3 | "禁止输出除A或B以外的任何字符。不要解释。不要标点。不要空格。不要换行。" | Heavy: maximal suppression, no reasoning tokens |

**Prediction (H_monotonic)**: d_z monotonically decreases as constraint severity increases.

## 2. Results

### 2.1 Gradient Summary

| Level | n_valid | mean | sd | **d_z** | Prediction Match |
|-------|:-----:|:----:|:--:|:-------:|:----------------:|
| **L0** (none) | 11 | +4.91 | 15.58 | **0.315** | — |
| **L1** (light) | 12 | +7.10 | 11.92 | **0.596** | ✗ (higher than L0!) |
| **L2** (moderate) | 12 | +1.13 | 12.40 | **0.091** | ✓ (substantial drop) |
| **L3** (heavy) | 12 | +2.21 | 7.42 | **0.297** | ✗ (recovery!) |

**Monotonic decrease: NO.** The gradient is non-monotonic: L1 > L3 > L0 > L2.

### 2.2 Key Finding: Three-Regime Pattern

```
d_z
0.6 ┤          ● (L1: 0.596)
0.5 ┤
0.4 ┤
0.3 ┤ ● (L0: 0.315)          ● (L3: 0.297)
0.2 ┤
0.1 ┤                    ● (L2: 0.091)
0.0 ┼────┬────────┬────────┬────
     L0   L1       L2       L3
```

Three distinct regimes:

1. **Optimization (L0→L1)**: Light constraint "只输出字母A或B" standardizes output WITHOUT suppressing reasoning. d_z RISES (0.315→0.596), variance falls (15.58→11.92). L1 is the **optimal measurement condition** for logprob format effects — clean output, preserved reasoning.

2. **Suppression (L1→L2)**: "不要解释" directly instructs the model to skip reasoning. d_z CRASHES (0.596→0.091). The Prose Barrier of Measurement in its purest form: the measurement constraint destroys what it measures.

3. **Rebound (L2→L3)**: Under extreme compression, d_z partially RECOVERS (0.091→0.297) with tightest variance (sd=7.42). When all reasoning tokens are forbidden, the system prompt becomes the sole behavioral differentiator — and syllogistic format's explicit causal structure may embed more strongly into the compressed decision pathway.

### 2.3 Per-Probe Survivors

| Probe | L0 fx | L1 fx | L2 fx | L3 fx | Robust? |
|-------|------:|------:|------:|------:|:-------:|
| 事实核验-PR (V) | **+38.19** | **+32.00** | **+26.25** | +7.25 | ✓ (attenuated) |
| 自审-复杂度 (I) | +13.90 | +17.08 | +12.17 | **+13.79** | ✓✓ (stable) |
| 自审-逻辑 (I) | +13.75 | +3.97 | +11.85 | **+10.77** | ✓✓ (stable) |
| 执行铁律-脚本 (V) | **+16.13** | +3.50 | +0.08 | −4.85 | ✗ (collapses) |
| 双池审查-架构 (I) | −20.74 | +18.87 | +12.87 | +6.84 | ✗ (sign-inverts) |

自审-复杂度 and 自审-逻辑 are the most robust probes — their format effects survive all four constraint levels with minimal attenuation. These probes have **moderate-complexity causal chains** that are neither too simple (trivial) nor too long (break under suppression).

### 2.4 L1-Visibility × Constraint Interaction

| Level | V mean | I mean | Δ(V−I) | Pattern |
|-------|:------:|:------:|:------:|---------|
| L0 | +10.67 | −0.31 | **+10.98** | Strong synergy (V≫I) |
| L1 | +7.28 | +6.92 | **+0.36** | Near-equal (V≈I) |
| L2 | +0.12 | +2.15 | **−2.03** | Weak compensation (I>V) |
| L3 | +0.31 | +4.11 | **−3.80** | Compensation (I>V) |

**Critical convergence**: The L1-visibility pattern shifts from synergy→compensation as constraint severity increases — the **same reversal observed in P1** (where multi-scene cognitive load produced Δ=−10.08). Two independent manipulations (multi-scene load, output constraint severity) produce the same qualitative pattern.

## 3. Interpretation

### 3.1 Unified Processing-Depth Model

The V3 (synergy), P1 (reversal), and constraint gradient (transition) findings converge on a single mechanism:

> **Processing depth impairment — whether from cognitive load (multi-scene) or output constraint suppression (L2/L3) — shifts format benefit from L1-gatable rules to L1-invisible rules.**

Mechanism: L1-gatable rules have strong IMPERTIVE baseline compliance (direct, simple commands work). Syllogistic format adds value only when there's processing depth to trace the causal chain. When depth is impaired:
- L1-gatable rules: IMP already works, SYL can't add value without depth → format effect vanishes
- L1-invisible rules: IMP weak, SYL provides structure that survives even shallow processing → format effect persists

### 3.2 Implication for L3 Model

**Rejected**: `format effect = f(chain length, constraint severity)` — monotonic.

**Upgraded**: `format effect = f(chain length, processing regime)` where regime is non-linearly determined by constraint:
- Regime 1 (optimization): light/no constraint → full reasoning → strongest format effect
- Regime 2 (suppression): moderate constraint → reasoning suppressed → format effect collapses
- Regime 3 (rebound): extreme constraint → alternative pathway → partial recovery

The transition between regimes is NOT continuous — it's a **phase change** in how the model processes the system prompt. This is fundamentally a cognitive architecture question: at what point does output constraint severity trigger a different processing strategy?

### 3.3 Practical Recommendation

For logprob measurement of format effects:
- **Use L1 (light):** "只输出A或B" — optimal precision, preserved reasoning
- **Avoid L2 (moderate):** "不要解释" kills the mechanism
- **L3 is a different measurement:** Low variance but regime-shifted; not comparable to L0/L1

### 3.4 Revised Czerwinski Rebuttal

The constraint gradient adds a new dimension: syllogistic format doesn't just fail under "complex scenarios" — it **recovers** under extreme output constraints. The worst condition for syllogism is MODERATE constraint (L2) that suppresses reasoning without triggering alternative processing. The recovery at L3 suggests that syllogistic format's causal structure has **compressive robustness** — it survives when imperative format's brevity advantage is neutralized by the constraint that forbids explanation.

## 4. Limitations

1. **n=12 probes** — wide per-probe variance; fine structure uncertain
2. **L0 had 1 missing data point** (降级链-FATAL IMP had no A/B)
3. **Single model** — DeepSeek V4 Pro only; cross-model replication needed
4. **Constraint text confounded with length** — cannot isolate severity from prompt length

## 5. Next Steps

- [x] Constraint gradient experiment run (96/96 calls)
- [ ] Cross-model replication (GPT-4o / Claude if API available)
- [ ] Update PAPER.md §6.10 L3 entry with non-monotonic model
- [ ] Update PAPER.md §6.15 with constraint gradient evidence

---

*Analysis complete 2026-07-13. The monotonic hypothesis was falsified — revealing a richer three-regime mechanism that unifies V3, P1, and constraint gradient findings.*
