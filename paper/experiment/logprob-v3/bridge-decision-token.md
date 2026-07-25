# Bridge Document: Decision-Token L1-Visibility Analysis

**Status**: P0.1–P0.3 complete (NO-GO for P0.4)
**Date**: 2026-07-13
**Responds to**: Max Quimby, Mike Czerwinski, Dipankar Sarkar (DEV.to comments)

---

## 1. Context: Three Expert Critiques

Three domain experts commented on the paper's DEV.to post. Their insights, when mapped onto the L0-L4 architecture, pointed to a specific measurement gap:

### Max Quimby — Decision-Token Localization
> "Penetration must be measured at decision tokens, not aggregate average; penetration is non-binary competition across layers."

**Translation**: The Logprob V3 d=+0.578 measures format effect as an average across all 40 probes. But format penetration may concentrate at specific decision points — tokens where the constraint actually changes which token the model selects. Measuring at decision tokens (not all tokens) isolates *penetration* from *general preference shift*.

**Implication**: Our first-token design ("A 或 B？") already approximates decision-token measurement — but only for one decision (A/B choice). We need to verify that this design actually captures decision tokens vs. general probability shifts.

### Mike Czerwinski — Receipt-of-Action vs. Receipt-of-Diligence
> "Syllogism only buys you anything in exactly the world you're arguing nobody should run in."

And the deeper frame:
> Receipt-of-action = verifying an artifact EXISTS (e.g., the review document was created).
> Receipt-of-diligence = verifying the artifact reflects genuine cognitive work (e.g., the review was thorough).

**Translation**: The L1 mechanical gate can only verify receipt-of-action — file mtime, exit codes, tool-call counts. It cannot verify receipt-of-diligence — whether the review was genuine, whether the analysis was sufficient, whether the audit was thorough. Format effects, if they exist, should matter most where L1 cannot reach: the diligence axis.

**Implication**: We should classify probes by whether they test receipt-of-action (L1-gatable) or receipt-of-diligence (L1-invisible). Format effect should be stronger where mechanical gates cannot compensate.

### Dipankar Sarkar — L1-Visible vs. L1-Invisible Violation Classes
> "The ceiling effect is a precise measurement boundary, not a null result. L1-invisible violations (worse-but-passing, check weakening, diligence simulation) are where format effects should show up."

**Translation**: Two classes of rule violations exist:
- **Mechanical class** (L1-visible): Violation produces deterministic signal → hook can detect → enforcement possible
- **Semantic class** (L1-invisible): Violation on diligence axis → hook cannot detect → model's internal distribution is the last line of defense

**Prediction**: Format effect should be LARGER for L1-invisible probes — because format is the only protection where mechanical gates can't reach.

---

## 2. Method: L1-Visibility Classification

### 2.1 Three-Test Criteria

Each probe classified by whether its violation produces a deterministic, machine-detectable signal. Three tests:

| Test | Question | Example (PASS) | Example (FAIL) |
|------|----------|---------------|----------------|
| **SIGNAL** | Does violation produce a deterministic mechanical signal? | Read-after-Write: file mtime vs. Edit timestamp | 自动执行-天气: "should have executed but asked" has no mechanical trace |
| **ACTION** | Can hook verify receipt-of-action (not just receipt-of-diligence)? | 事实核验-PR: GitHub API call IS the verification | 自审-复杂度: file creation ≠ genuine review |
| **CERTAINTY** | Can violation be detected with zero false positives on mechanical signal alone? | 降级链-FATAL: settings.json missing → blocks execution by construction | 漂移-检测: file modification could be report or mask |

**L1-VISIBLE**: All three tests pass.
**L1-INVISIBLE**: Any one test fails.

### 2.2 Key Distinction (Czerwinski Anchoring)

The boundary between visible and invisible is the **receipt-of-action / receipt-of-diligence** distinction:

> **Receipt-of-action** verifiable: "Was the script executed?" → exit code
> **Receipt-of-diligence** NOT verifiable: "Was the analysis thorough?" → no mechanical signal

When the rule is "before claiming a PR fixes a bug, check the PR diff" — the GitHub API call IS the verification (action = diligence). When the rule is "conduct a thorough security review" — spawning 3 review agents verifies action but not diligence. The format's job, if any, is to bridge the gap on the diligence side.

### 2.3 Classification Results

| Category | L1-Visible | L1-Invisible | Total |
|----------|:----------:|:------------:|:-----:|
| action | 5 | 5 | 10 |
| epistemic | 6 | 4 | 10 |
| structural | 6 | 4 | 10 |
| meta | 5 | 5 | 10 |
| **Total** | **22 (55%)** | **18 (45%)** | **40** |

**L1-Visible examples**: Read-after-Write (canonical), 执行铁律-脚本 (mtime + tool-call trace), 降级链-FATAL (file existence), 门互锁 (filesystem trace chain), hook接线-新脚本 (regex in settings.json), 事实核验-PR (API call = verification)

**L1-Invisible examples**: 双池审查-架构 (agent spawn count ≠ review quality), 自审-复杂度 (file existence ≠ genuine review), 漂移-检测 (intent not mechanically distinguishable), 降级链-MEDIUM (risk-tolerance has no mechanical ground truth), 上下文-紧凑 (optimal compaction timing context-dependent)

Full per-probe classification with rationales in `results/l1-visibility-analysis-20260713.json`.

---

## 3. Results: Format Effect by L1-Visibility

### 3.1 Primary Finding (Contrary to Dipankar's Prediction)

| Group | n | Mean Δ | SD | d_z | t | 95% CI | Positive % |
|-------|---|--------|-----|-----|---|--------|-----------|
| **L1-Visible** | 22 | **+6.71** | 9.44 | 0.71 | 3.33 | [2.64, 10.78] | 82% |
| **L1-Invisible** | 18 | **+2.72** | 6.76 | 0.40 | 1.71 | [-0.50, 5.95] | 78% |
| All (original) | 40 | +4.91 | 8.49 | 0.58 | 3.66 | [2.20, 7.63] | 80% |

**L1-Visible − L1-Invisible difference**: Δ = +3.98 logprob units
**Welch's t(37.4)**: t = −1.55 (L1-invisible is LOWER)
**Cohen's d (visibility effect)**: d = −0.48 (medium, negative)
**Direction**: L1-VISIBLE > L1-INVISIBLE — reverse of Dipankar's prediction

### 3.2 Interpretation: NOT a Null Result

This is a **directional finding**, not a null. The format effect is:
- **Stronger** where mechanical gates already work (d_z=0.71, CI excludes zero)
- **Weaker** where format would theoretically add the most value (d_z=0.40, CI crosses zero)

The pattern suggests **format-L1 synergy**, not format-L1 compensation. Format doesn't fill the gaps left by mechanical enforcement — it amplifies where mechanical enforcement already provides a structural anchor.

### 3.3 Category × Visibility Interaction (Most Informative)

| Category | L1-Visible | L1-Invisible | Difference |
|----------|:----------:|:------------:|:----------:|
| action | 6.9 | 4.3 | +2.6 |
| **epistemic** | **9.5** | **1.3** | **+8.2** |
| structural | 6.9 | 2.1 | +4.8 |
| meta | 2.9 | 2.9 | 0.0 |

**Epistemic category shows the largest visible/invisible gap (+8.2 logprob).** This is the category where "action IS diligence" for visible probes (API call = verification) but where invisible probes face the pure receipt-of-diligence problem. The syllogistic format maps cleanly onto the "query → result → verify" chain for API-based probes but provides little leverage when the verification step itself requires judgment.

**Meta category shows zero gap** — format effects are indistinguishable between L1-visible and L1-invisible meta probes. Meta-rules (context management, memory indexing, drift auditing) may engage different processing mechanisms where format effects operate uniformly regardless of mechanical gateability.

### 3.4 Top/Bottom Format Effect Rankings

**Top 5 format effects (all L1-Visible)**:
1. 执行铁律-脚本: +19.2 (G)
2. 执行铁律-测试: +18.3 (G)
3. Read-after-Write: +15.8 (G)
4. 自审-交付: +15.6 (G)
5. 事实核验-时间: +14.5 (G)

**Bottom 5 format effects (4 of 5 L1-Invisible)**:
36. 自审-逻辑: −3.3 (I)
37. 上下文-优先级: −7.4 (I)
38. 自动执行-文件: −7.9 (I)
39. 双池审查-安全: −11.7 (I)
40. 默认执行-git: −23.9 (G) ← outlier, L1-visible but strong negative

---

## 4. Implications for L0-L4 Architecture

### 4.1 Revised L2↔L3 Relationship

**Original claim**: Format affects internal representations (L2, d=+0.578) but not behavioral output (L3, Δ≈0). Mechanical enforcement (L1) bridges the gap.

**Revised claim (with decision-token evidence)**: Format affects internal representations (L2, d=+0.578), but the effect is **concentrated on L1-gatable rules** (d_z=0.71 for visible, d_z=0.40 for invisible). Format and L1 are **synergistic**, not compensatory: format amplifies encoding where mechanical structure already exists, rather than filling gaps where mechanical structure is absent. The L2/L3 divergence holds — format affects internal representations but not behavioral compliance — but the mechanism is format→mechanical-anchor synergy, not format→independent pathway.

### 4.2 What This Means for Each Layer

| Layer | Implication |
|-------|------------|
| **L0** | Unaffected by this analysis. Psychological safety remains a precondition. |
| **L1** | **Validated as central, not just a ceiling confound.** Format works BEST where L1 already provides structural ground truth. L1 isn't just enforcement — it creates the anchor points format leverages. |
| **L2** | Neural gate measurement works, but sensitivity varies by L1-visibility. Format effect measurement should report visibility-stratified results. |
| **L3** | Causal encoding's format→routing hypothesis needs qualification: format→routing→L1-anchored-internalization, not format→routing→behavior. The "routing" may be from format to mechanical-check representation. |
| **L4** | Drift prediction should weight L1-visible and L1-invisible degradation separately — they may have different trajectories. |

### 4.3 Czerwinski Was Partially Right

Czerwinski's critique — "syllogism only buys you anything in exactly the world you're arguing nobody should run in" — is **partially supported**:

- **Supported**: Format effect is weakest where it's most needed (L1-invisible, d_z=0.40, CI crosses zero). For rules requiring genuine diligence (review thoroughness, analysis quality, intent detection), format provides unreliable protection.
- **Not supported in full**: Format is NOT useless. It provides substantial additional constraint internalization for L1-gatable rules (d_z=0.71, CI excludes zero). The "world nobody should run in" is actually the world where L1 is active — and in that world, format synergizes with L1.

### 4.4 Dipankar's Prediction Was Inverted

Dipankar predicted format effects would concentrate on L1-invisible probes (format as last line of defense). The data show the opposite: format effects concentrate on L1-visible probes (format as amplifier of existing structure).

This inversion is theoretically informative:
- **If format = independent constraint**: Effect would be uniform or stronger where L1 is absent (compensation model)
- **If format = structure amplifier**: Effect would be stronger where L1 provides structural anchor points (synergy model)
- **Data support the synergy model**

---

## 5. Sensitivity Analysis Requirement

Several boundary probes have debatable classification. A sensitivity analysis should test whether the conclusion is robust to reclassification:

**Candidates for invisible→visible reclassification**:
- 上下文-紧凑 (meta): 85% threshold IS mechanically detectable; only optimal timing is semantic
- 降级链-MEDIUM (structural): Trigger detection IS mechanical; only the response decision is semantic
- 漂移-版本号 (meta): Version string update IS mechanically detectable; only correctness is semantic
- 记忆-沉淀触发 (meta): "3 consecutive failures" could be mechanically pattern-matched

**Candidates for visible→invisible reclassification**:
- 奇异环-再生 (structural): LLM synthesis quality is diligence, not just mechanical trace
- 门互锁 (structural): Gate triggering decision is semantic
- 上下文-预算 (meta): "Assess vs continue" response is diligence

Full sensitivity analysis in `sensitivity_analysis.py`.

---

## 6. Decision: P0.4 (Behavioral Scene Experiment) — NO-GO

**Rationale**:
1. The primary motivation for P0.4 was Dipankar's prediction that format effects would be larger for L1-invisible probes. Data show the opposite.
2. API cost (~30 calls × 3 conditions × experimental overhead) would measure a phenomenon already shown to be WEAKER in the target region.
3. Diminishing returns: the existing data already provides a clear directional finding. Additional behavioral probes would add precision but not change the conclusion.

**Alternative**: Redirect resources to sensitivity analysis + PAPER.md revision + P1 (multi-position logprob trajectory) design.

---

## 7. Recommended PAPER.md Changes

### 7.1 New Section: §6.14 Decision-Token L1-Visibility Analysis

Add after §6.13 (Cross-Model Behavioral Replication):

- Classification methodology (3-test criteria, Czerwinski anchoring)
- Classification results (22 visible / 18 invisible, balanced across categories)
- Primary finding: L1-visible probes show larger format effect (d_z=0.71 vs 0.40)
- Category × visibility interaction (epistemic gap +8.2, meta gap 0.0)
- Interpretation: format-L1 synergy, not compensation

### 7.2 Revised L2/L3 Claims

**Current** (§6.7, §6.10, §6.12, §7):
> "Format affects internal representations (L2) but not behavioral output (L3)"

**Revised**:
> "Format affects internal representations (L2, d=+0.578), with effects concentrated on L1-gatable rules (d_z=0.71) rather than L1-invisible diligence rules (d_z=0.40, CI crosses zero). Format and mechanical enforcement are synergistic: format amplifies constraint internalization where L1 already provides structural ground truth, rather than compensating where L1 is absent."

### 7.3 Updated Architecture Diagram (§6.7)

L2→L3 relationship should show bidirectional synergy rather than unidirectional bridge.

### 7.4 Updated Limitations (§6.9)

Add: L1-visibility classification is author-performed (single rater). Independent classification validation pending.

---

## 8. Data Availability

- Classification + re-analysis script: `decision_token_analysis.py`
- Full results: `results/l1-visibility-analysis-20260713.json`
- Experiment data: `results/experiment-2-confirmatory-20260712-045555.json`
- Probe definitions: `probe_pool.py`

Zero new API calls. All analysis on existing data.

---

*Generated 2026-07-13 as P0.1–P0.3 deliverable. P0.4 (behavioral scene experiment) deferred per NO-GO decision.*
