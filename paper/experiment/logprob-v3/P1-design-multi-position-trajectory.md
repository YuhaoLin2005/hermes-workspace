# P1: Multi-Position Logprob Trajectory Experiment

**Status**: Design phase | **Date**: 2026-07-13
**Preceded by**: P0.1–P0.3 (L1-visibility classification — NO-GO for P0.4)
**API access**: DeepSeek V4 Pro (logprobs API) | **Est. cost**: ~$1.00 (24–120 calls)

---

## 1. Motivation

### 1.1 What We Know (Post-P0)

| Finding | Evidence |
|---------|----------|
| Format affects first-token logprob | d=+0.578, BF=282k, 40 probes |
| Effect concentrates on L1-gatable rules | d_z=0.71 (visible) vs 0.40 (invisible) |
| Format does not affect behavioral compliance | Δ≈0 across 3 architectures |
| Format-L1 synergy, not compensation | §6.14 |

### 1.2 What We Don't Know

**Does format effect persist beyond the first token, or is it surface priming that decays immediately?**

The first-token design ("A 或 B？") measures format effect at exactly one decision point. If the effect decays within 1-2 tokens, it's **surface priming** — syllogistic structure makes rule text more salient but doesn't change constraint processing. If it persists across 5+ tokens, it's **structural** — the causal chain format actually changes the model's internal trajectory.

### 1.3 Why This Matters for L3

The L3 hypothesis: Syllogistic format → different attention routing → different representations → behavioral compliance. We've measured format→first-token-logprob (first arrow, d=+0.578) and format→behavior (last arrow, null). Multi-position persistence distinguishes the mechanism:

- **Surface priming**: format effect decays monotonically. Format makes the constraint salient at decision-point but is "used up" once response begins.
- **Structural encoding**: format effect persists or amplifies. Format changes internal trajectory, compounding as token chain unfolds.

---

## 2. Experiment Design

### 2.1 Core Question

Does SYL−IMP logprob differential persist across response token positions, or decay with distance from rule text?

### 2.2 Design

**Within-probe, 2-condition (IMP/SYL) × 3 token positions (T1–T3).**

**Design revision (implementation-time)**: The originally proposed 决定/理由/方式 format was replaced during implementation with three independent A/B scenes per probe (Q1/Q2/Q3) to directly test whether format effects survive context switching. This changes the interpretation: T2 and T3 no longer measure reasoning depth or action specification for the same scenario, but rather compliance decisions on distinct scenes at increasing processing distance. See the analysis document §1.4 for implications.

Final implemented format:

```
[System prompt with rule in IMP or SYL format]

按以下格式回答3个问题，每行只输出字母A或B，不要任何其他文字：
Q1: [scene 1]. A.[action A] B.[action B]
Q2: [scene 2]. A.[action A] B.[action B]
Q3: [scene 3]. A.[action A] B.[action B]

输出（3行每行一个字母）：
```

Three decision points:
- **T1 (Q1)**: Binary compliance on the direct scene — comparable to existing first-token V3 design
- **T2 (Q2)**: Binary compliance on a scene with distractor/urgency — tests context-switching cost
- **T3 (Q3)**: Binary compliance on a scene with competing pressure — tests cumulative dilution effect

**Important caveat**: H4 (§2.4, "if syllogistic format amplifies causal reasoning, effect should be STRONGER at T2 than T1") is NOT testable with the implemented design, because T2 is another compliance decision rather than a reasoning output. H4 is superseded by the context-switching question.

### 2.3 Probe Selection (n=12, stratified)

| Visibility | Category | Probes | T1 format effect |
|-----------|----------|--------|:---:|
| L1-Visible | action | Read-after-Write, 执行铁律-脚本 | +15.8, +19.2 |
| L1-Visible | epistemic | 事实核验-PR, 事实核验-时间 | +13.3, +14.5 |
| L1-Visible | structural | 降级链-FATAL, 门互锁 | +10.7, +12.9 |
| L1-Invisible | action | 自动执行-天气, 最低成本-验证 | +11.8, +4.7 |
| L1-Invisible | epistemic | 自审-复杂度, 自审-逻辑 | +5.0, −3.3 |
| L1-Invisible | structural | 双池审查-架构, 降级链-MEDIUM | +11.2, +3.8 |

Deliberately includes largest L1-invisible format effects (自动执行-天气 +11.8, 双池审查-架构 +11.2) to test visibility×persistence interaction when first-token effects are comparable.

### 2.4 Hypotheses

| H | Prediction | Test |
|---|-----------|------|
| **H1: Persistence** | Format effect persists beyond T1 (\|d\| at T2, T3 > 0.2) | One-sample t on SYL−IMP at T2, T3 |
| **H2: Decay** | If surface priming: \|d_T3\| < \|d_T1\| | RM-ANOVA: position × format |
| **H3: Visibility×Persistence** | L1-visible probes show stronger persistence | Between-group decay slope comparison |
| **H4: Causal reasoning** | Format effect at T2 (理由) > T1 (决定) for syllogistic probes | **NOT TESTABLE** — implementation changed to Q1/Q2/Q3 format; T2 is a different scene, not reasoning output |

**H4 is key**: If syllogistic format amplifies causal reasoning specifically, effect should be STRONGER at T2 than T1 — direct evidence for format→reasoning, not format→priming→choice.

---

## 3. Technical Feasibility

### 3.1 API Requirements

DeepSeek API `logprobs=True, top_logprobs=20`. Returns per-token logprobs for entire response. One call per condition per probe.

**Risk**: API only returns logprobs for actual generated tokens, not hypothetical alternatives. Both compliant and violating tokens must appear in top_logprobs at each target position.

**Mitigation**: Pre-validation gate. Test each probe once, verify token presence at all positions. Reject failing probes.

**Total calls**: 24 (best) to 72 (with retries). ~$0.50–1.00.

### 3.2 Fallback: Context Dilution

If multi-position extraction fails: insert N tokens of distractor text between rule and probe (N=0, 50, 100, 200). Measure first-token format effect at each distance. Decay → surface; persistence → structural. 96 API calls.

---

## 4. Decision Criteria

| Condition | Action |
|-----------|--------|
| Pre-validation passes for ≥8/12 probes | Run full P1 |
| <8 probes valid at all positions | Switch to context dilution fallback |
| Both designs fail pre-validation | Report limitation; defer to local model (L2 v3 roadmap) |

---

## 5. Timeline

| Phase | Content | Est. |
|-------|---------|------|
| P1.1 Probe design | 12 multi-position probes + validation script | 1 session |
| P1.2 Pre-validation | Token-in-top-20 check at all positions | 1 session |
| P1.3 Execution | 24–72 API calls + data collection | 1 session |
| P1.4 Analysis | Trajectory plots, ANOVA, hypothesis tests | 1 session |
| P1.5 Write-up | §6.15 in PAPER.md | 1 session |

**Total**: ~5 sessions, ~$1.00.

---

*Designed 2026-07-13. Ready for execution on user approval.*
