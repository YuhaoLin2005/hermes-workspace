# Agent Identity Drift: Preliminary Evidence That Config Rules Shape LLM Agent Behavior

**Authors**: Yuhao Lin (FAFU)
**Status**: Pre-print, July 2026
**Primary category**: cs.SE | **Cross-list**: cs.CL
**Repository**: https://github.com/YuhaoLin2005/hermes-workspace

---

## Abstract

LLM-based coding agents degrade over extended use. This paper investigates whether configuration rules—system prompts, behavioral protocols, and self-model—measurably shape agent behavior. We present a five-layer architecture for configuration integrity: psychological safety (L0, permission), mechanical gates (L1, filesystem checks bypassing AI self-assessment), neural gates (L2, token probability measurement), causal encoding (L3, format engineering affecting internal representations), and drift prediction (L4, trend detection before failure). Empirical evidence from seven experiments plus a decision-token re-analysis includes: (1) a between-subjects causal swap (n=30, DeepSeek V4 Pro, single-rater unblinded) where removing a behavioral rule reduced alternative-seeking from 73% to 20% (OR=11.0, p=0.009); (2) Logprob Probe V3 (n=40 pre-validated probes, objective API-read DV) finding syllogistic format produces deeper constraint internalization than imperative (d=+0.578, BF₁₀=282,399); (3) GateGuard-OFF (n=21 probes × 3 conditions) showing rules improve behavioral compliance (+0.38 above NO RULES baseline) but format does not distinguish compliance (IMP≈SYL, Δ=−0.02); and (4) an L1-visibility re-analysis (§6.14) of the Logprob V3 data finding format effects concentrate on L1-gatable rules (d_z=+0.71, 95% CI excludes zero) rather than L1-invisible diligence rules (d_z=+0.40, CI crosses zero) — indicating format-L1 synergy, not compensation. The core finding is a qualified divergence: format affects internal representations (L2), but the effect is amplified where mechanical enforcement (L1) already provides structural ground truth; format alone does not reliably bridge the diligence gap. Cross-model behavioral replication on Qwen3-8B (Dense) and GLM-4-9B (GLM) is consistent with this divergence across architectures (SYL−IMP ≤ |0.025|). All quantitative results, except Logprob V3 API-read DV and cross-model behavioral observations, are scored by the first author (unblinded); independent blind verification is pending.

---

## Experiment Overview

| Experiment | N | Design | Main Finding | Status |
|------|:--:|------|------|:--:|
| **L0 Safety Prompt** (§3.5) | **40 probes** | **Within-probe, 2-cond, logprob DV** | **Accuracy preserved (+0.01); uncertainty↑ where room exists; gains ROBUST (r=+0.949)** | ✅ Complete |
| Growth-log Retrospective (§6.2) | 34 sessions | Longitudinal coding, single coder | 55.9%→0.7% violation rate with mechanical gate | ✅ Complete |
| Causal Swap (§4) | 30 tasks | Between-subjects (15+15), DeepSeek V4 Pro | WITH rule 73% vs WITHOUT 20%, OR=11.0, p=0.0092 | ⚠️ Single-rater, unblinded |
| **Logprob Probe V3** (§6.11) | **40 probes** | Within-probe, 3-condition, pre-validated, API logprob DV | **Syllogistic > Imperative: d=+0.578, BF=282k** | ✅ Objective DV (API-read) |
| Format A/B (§6.5) | 150 tasks | Between-subjects (75+75), 6 sessions, DeepSeek V4 Pro | Ceiling effect (99.3% compliance); format affects reasoning depth, not compliance | ⚠️ GateGuard confound |
| **GateGuard-OFF** (§6.12) | **21 probes × 3 cond** | Within-probe, 3-condition (NO RULES/IMP/SYL), behavioral compliance DV | **Rules work (+0.38 above baseline); IMP≈SYL (delta=−0.02); format→internal, not behavioral** | ✅ Complete (heuristic scoring) |
| **Cross-Model Behavioral** (§6.13) | **12 probes × 3 cond × 3 models** | 3-model replication (DSv4 MoE + Qwen3-8B Dense + GLM-4-9B), within-probe, behavioral compliance DV | **SYL−IMP all ≈ 0 across 3 architectures; L2/L3 divergence consistent across architectures** | ✅ Complete (API-observed) |
| **Decision-Token L1-Visibility** (§6.14) | **40 probes re-analysis** | Post-hoc classification + re-analysis of Logprob V3 data by L1 mechanical gateability | **Format effect L1-visible (d_z=+0.71) > L1-invisible (d_z=+0.40); format-L1 synergy, not compensation** | ✅ Complete (0 new API calls) |
| **P1 Multi-Scene Resilience** (§6.15) | **12 probes × 2 formats × 3 scenes + 2 controls (48 calls)** | Multi-scene + control experiments; dual confound resolved (meta-instruction ~80% driver) | **Format effects collapse under output constraints (Ctrl A d_z 0.31, 20% of V3); Prose Barrier of Measurement documented** | ⚠️ Negative result; meta-instruction = structural measurement necessity |
| **Constraint Gradient** (§6.15) | **12 probes × 2 formats × 4 levels (96 calls)** | 4 output-constraint severity levels (none/light/moderate/heavy) testing monotonicity hypothesis | **Non-monotonic: d_z L1(0.596)>L3(0.297)>L0(0.315)>L2(0.091); three processing regimes; L1-V>I convergence with P1** | ✅ Complete |
| **Cross-Model Constraint Gradient** (§6.13) | **12 probes × 4 levels × 2 formats × 2 models (192 calls)** | Qwen3-8B + GLM-4-9B via SiliconFlow; behavioral measurement | **No format effect on 8B/9B models (GLM d_z=0 all levels); format effects require model capacity — L3 boundary condition evidence** | ✅ Complete |
| Syllogism Blind CV (§6.4) | 4 sessions | 5/5 rules triggered, zero violations + emergent auditing | Preliminary format→reasoning causal chain evidence | ⚠️ Small n, uncontrolled |
| **P1-1 Residual Cluster** (§6.16) | **200 trials** | **5 task types × 40, pre-registered, regex scoring (no LLM judge)** | **L1 100% compliant 0 violations; L1/L2 boundary 100% semantic violations; violations cluster where gate cannot instrument** | ✅ **Pre-registered, deterministic scoring** |
| **P1-2 Format×Gate** (§6.16) | **240 trials** | **2×2 factorial (format code/prose × GateGuard on/off), pre-registered, regex scoring** | **H1 NOT CONFIRMED; prose format → better reasoning regardless of gate (~0.25 SD); code+gate = "checklist mentality"** | ✅ **Pre-registered, deterministic scoring** |

> **n-count reconciliation**: Five numbers appear across the repository — 30 (Causal Swap tasks), 34 (growth-log sessions), 38 (cumulative trials in paper-trial-results.md = 30 original + 8 new), 60 (future target sample size), 150 (Format A/B tasks). Each corresponds to a different experiment; they are not conflicting reports of the same data.

---

## Reader's Guide

This paper reports a three-part investigation developed iteratively over 50+ coding sessions. The reader may find it helpful to understand the structure before diving in:

- **Part 1 — Mechanical Gate (§3):** System architecture. A self-model regeneration pipeline with filesystem-level verification. *Note: Part 1 describes the system but does not include a direct A/B experiment of the gate itself; gate effectiveness is demonstrated in Part 3's experiment (§6.5).*
- **Part 2 — Causal Swap (§4):** A between-subjects manipulation (n=30) testing whether removing a config rule changes behavior. The paper's methodologically strongest evidence, with the caveats of single-rater unblinded scoring and non-randomized assignment.
- **Part 3 — Causal Structure Encoding (§6):** The longest section, combining retrospective baseline coding (§6.2, n=34 sessions), a small-N syllogism pilot (§6.4, n=4), a controlled A/B experiment (§6.5, n=150 tasks) with identified GateGuard confound, Logprob Probe V3 (§6.11, n=40 probes, d=+0.578) with objective API-read DV, GateGuard-OFF (§6.12, n=21 probes × 3 conditions including NO RULES baseline) testing behavioral compliance without mechanical enforcement, cross-model behavioral replication (§6.13) on Qwen3-8B (Dense) and GLM-4-9B (GLM) confirming the L2/L3 divergence consistent across architectures, an L1-visibility decision-token re-analysis (§6.14) finding format-L1 synergy, and a multi-scene format resilience test with control experiments and constraint gradient (§6.15) showing: (a) format effects collapse under output constraints — meta-instruction is ~80% driver, identified as the "Prose Barrier of Measurement"; (b) a non-monotonic constraint gradient (L1>L3>L0>L2, d_z range 0.091–0.596) revealing three processing regimes (optimization→suppression→rebound); (c) L3 upgraded from monotonic two-parameter to three-regime model. Cross-model constraint gradient (§6.13) on Qwen3-8B/GLM-4-9B finds zero format effect (d_z=0 all levels) — establishing model capacity as L3 boundary condition. Format effect confirmed on internal representations (Logprob V3) but not on behavioral compliance (GateGuard-OFF and cross-model), consistent with the Prose Barrier framework; the L1-visibility, cognitive-load, and constraint-gradient analyses qualify that format effects require both mechanical anchors (gatable rules) and sufficient processing depth (model capacity + constraint-permitted reasoning).

**Reading paths**: For a quick scan, read the Experiment Overview table above, then §4 (Causal Swap), then §6.10 (Conclusion). For a full read, follow section order. **Important**: §5 (Discussion) appears before §6 because it primarily discusses the Causal Swap experiment (§4); §6 was developed later in the research timeline and its discussion is integrated within the section itself.

All experimental results are scored by the first author (unblinded, no independent raters). Cohen's κ from the one attempted blind check was -0.14 (§5.2). The quantitative results should be interpreted as preliminary evidence requiring independent verification. See §5.1 and §6.9 for comprehensive limitations.

---

## Glossary of Core Terms

> Terms coined or given specific technical meaning in this paper. One sentence each; cross-references link to detailed sections.

| Term | Definition |
|------|------------|
| **Prose Barrier** (§3.0) | The structural constraint that LLM generation and evaluation share *P(token\|context;θ)*, making self-verification unreliable without an independent measurement channel. |
| **Mechanical Gate** (§3) | Filesystem-level checks (mtime, exit codes, hook wiring) that verify configuration integrity without passing through the model's generation pathway. |
| **Neural Gate** (§6.7 L2) | Token-probability measurement within the generation distribution that detects whether behavioral constraints have "penetrated" the model's internal processing. |
| **Causal Encoding** (§6) | The hypothesis that a rule's linguistic format (imperative vs. syllogistic) changes internal processing, with effectiveness bounded by cognitive load: format effect = f(causal chain length, available processing depth). |
| **Constraint Echo** (§6.7 L2) | A detectable trace of a behavioral rule in the model's output distribution — evidence that the rule is actively processed, not merely present in context. |
| **Drift Prediction** (§6.7 L4) | Aggregation of signals from L0-L3 plus session metadata to forecast behavioral degradation before it occurs. |
| **Self-Model** (§3.4) | A compact markdown file (~100 lines) storing the agent's current self-description — capabilities, limitations, growth trajectory. Regenerated when stale. |
| **GateGuard** (§6.5) | The collective term for L1 mechanical enforcement hooks that block unverified operations (Write/Edit without Read-back, etc.). |
| **Execution Debt** | A session-level counter tracking unmet obligations (unverified writes, skipped audits). When debt exceeds threshold, execution is blocked until resolved. |
| **Strange Loop / Self-Referential Closure** (§3.4) | The functional pattern where the self-model both guides behavior and is regenerated from behavioral observations — a closed causal loop adapted from Hofstadter's framework. |
| **L2/L3 Dissociation** (§6.12–13) | The empirical finding that format affects internal representations (L2, d=+0.578) but not behavioral compliance (L3, Δ≈0) — confirmed cross-model across MoE/Dense/GLM. |
| **L1-Visibility** (§6.14) | Classification of whether a rule violation produces a deterministic mechanical signal (L1-gatable) or operates on the diligence axis where no mechanical signal exists (L1-invisible). Grounded in Czerwinski's receipt-of-action vs. receipt-of-diligence distinction. |
| **Output Constraint Suppression** (§6.15) | The finding that output format constraints (e.g., "只输出A或B") suppress ~80% of syllogistic format effect by redirecting the model from deep reasoning to label production — a Prose Barrier manifestation where the measurement instrument suppresses the mechanism being measured. |

---

## 1. Introduction: 50 Sessions of Watching an Agent Drift

Over approximately 50 coding sessions with DeepSeek V4 Pro inside Claude Code, I observed a recurring pattern: the agent would start each session coherent, but after extended interaction, it would forget negotiated conventions, relax quality-review enforcement, and drift from its configured identity. In 15 of those 50 sessions (~30%, informal observation), a specific protocol was forgotten by the session midpoint. Subsequent systematic retrospective coding of 34 growth-log sessions confirmed a higher violation rate of 55.9% (19/34; see §6.2), suggesting that informal observation underestimates true drift rates. In 8 sessions, the agent re-litigated a decision settled in a previous growth-log entry.

This auto-ethnographic observation is not systematic — the sessions were not formally coded (see Section 5: Limitations). But it forms the ecological ground for the experiment that follows: if config rules matter, removing one should measurably change behavior.

The phenomenon has been named but not yet measured at the identity layer. Rath (2026) introduced "agent drift" to describe behavioral degradation in multi-agent coordination [1]. TACT (2026) demonstrated activation-steering mitigation for drift in coding agents [2]. "Measuring What Persists" (2026) showed identity-relevant representations collapse at long context lengths [3]. Anthropic's J-space paper (2026) provided neuro-mechanistic evidence that compact self-representations causally shape downstream outputs [4]. Our work addresses a distinct question: **do the config rules that surround an LLM agent — its system prompts, behavioral protocols, and self-model — causally shape its behavior, or are they decorative text consuming context tokens?**

**Contributions:**
0. An **L0 psychological safety meta-constraint** — evidence that a permission-layer system prompt preserves accuracy (H1, 0.98→0.99) while improving uncertainty admission where room exists (3/5 non-ceiling boundary probes improved, 0 worsened), with P0 diagnostic confirming behavioral gains are accompanied by *increased* logprob confidence (non-ceiling mean H3_Δ=+2.26, r=+0.949), positioned as foundational to the verification architecture
1. A mechanized identity-persistence pipeline — 3 of 4 operational steps are deterministic Python scripts, with 19/19 behavioral tests passing
2. A causal swap experiment (n=30) testing config rule causality (OR=11.0, p=0.0092)
3. **Causal structure encoding** — evidence that syllogistic rule format produces measurably deeper constraint internalization than imperative format at the token-probability level (Logprob V3, n=40, d=+0.578, BF=282k, objective API-read DV), converging with independent attention routing research (Pender 2026)
4. A **divergence between internal representations and behavioral output**: GateGuard-OFF (n=21 × 3 conditions) confirmed (a) rules substantially improve compliance (+0.38 above NO RULES baseline 0.48) and (b) format effects on internal processing do not translate to behavioral compliance without mechanical enforcement (IMP≈SYL, delta=−0.02). Cross-model replication (§6.13) on Qwen3-8B (Dense+GQA) and GLM-4-9B (GLM) provides converging evidence for this divergence across three architectures (MoE/Dense/GLM): SYL−IMP ≤ |0.025| for all models. L1-visibility re-analysis (§6.14) further qualifies the format effect: it concentrates on mechanically-gatable rules (d_z=+0.71) rather than diligence-class rules (d_z=+0.40), indicating format-L1 synergy rather than compensation
5. A five-layer architecture (L0 permission → L1 mechanical → L2 neural → L3 causal → L4 predictive) covering the full configuration integrity pipeline from psychological safety precondition to trend-based failure prediction, with the L1-visibility analysis providing empirical grounding for the L1-L2-L3 inter-layer relationship

---

## 2. Related Work

**Agent Drift.** Rath (2026) formalized three sub-types (semantic, coordination, behavioral) in multi-agent LLM systems and proposed a 12-dimensional Agent Stability Index [1]. Our work addresses a distinct axis — identity/configuration drift in single-agent coding assistants — measured through self-model persistence rather than inter-agent coordination metrics.

**Mitigation Approaches.** TACT (2026) used activation steering at the neural level [2]. Our approach operates at the configuration layer — external scaffolding rather than internal weight modification. Complementary strategies at different AI stack layers.

**LLM-Modulo Frameworks.** Kambhampati et al. (2024) proposed wrapping LLMs with external verifier modules that catch errors and back-prompt regeneration [5]. Our pipeline instantiates this pattern with a critical distinction: our critic is a *data-freshness detector* (mtime comparison) rather than an *output-correctness verifier*. It signals "new observations exist," not "the output is wrong." This is both a limitation (cannot detect incorrect-but-recent content) and a strength (fully mechanizable, zero false positives on staleness).

**Identity Persistence.** "Measuring What Persists" (2026) showed identity representations undergo geodesic collapse at long context [3]. Anthropic's J-space (2026) discovered a compact neural subspace causally shaping model output [4]. Our self-model shares a functional pattern — compact, causally-placed, inspectable — but operates at the configuration layer (markdown files concatenated into context) rather than the neural layer (vectors in activation space). Both embody a shared design principle — separate identity from mechanism, make it compact, place it on the causal path — but the evidential gap is substantial: J-space is validated through causal ablation, cross-model replication, and mechanistic theory; our self-model is tested on one model with one rule by one unblinded rater. We note this as a functional analogy, not a claim of equivalent mechanisms or evidentiary support.

**Self-Verification and Reliability.** Several lines of work address the challenge of LLM output reliability. Self-consistency (Wang et al., 2022) improves accuracy through multiple sampling and majority voting [14] — a complementary strategy that increases compute cost. Reflexion (Shinn et al., 2023) enables agents to self-correct using environmental feedback and episodic memory [15], demonstrating that external grounding can partially compensate for the self-assessment problem. ReAct (Yao et al., 2022) interleaves reasoning traces with tool-use actions [16], establishing the action-reasoning loop pattern that our mechanical gate monitors. DSPy (Khattab et al., 2023) provides programmatic prompt optimization [17] — configuration-layer engineering at scale — but targets task performance rather than persistent identity integrity. Our work differs from all of these in targeting **configuration drift over extended sessions** rather than single-task accuracy.

**The Prose Barrier as a Unifying Lens.** Across these approaches, a common structural constraint operates: an LLM's generation and evaluation pathways share the same decoder distribution *P(token | context; θ)*. Self-consistency and Reflexion compensate by introducing external variance (multiple samples, environmental feedback) or anchoring to tool-use observations (ReAct). DSPy works at the prompt level, optimizing what enters the distribution. But none fully escapes the fundamental constraint: when the same model both produces and evaluates an output, the evaluation cannot be structurally independent of the generation. We term this the **Prose Barrier** (§3.0) — the impossibility of self-verification without an independent measurement channel. Our five-layer architecture is organized around this constraint: L1 bypasses it (filesystem checks), L2 measures within it (token probabilities as passive traces), L3 engineers its input side (format→routing), and L4 observes from outside (trend detection). The Prose Barrier is not a discovered phenomenon but a structural condition of autoregressive generation — it does not require empirical proof, only acknowledgment. The practical question is not whether the Barrier exists, but whether engineering around it produces more reliable agents than ignoring it.

**Trust in Automation.** Lee & See (2004) established that human trust depends on appropriate calibration between perceived and actual system capability [6]. Agent identity drift directly undermines this calibration. Sarter, Woods & Billings (1997) named this "automation surprise" — the gap between expected and actual system behavior [7]. Our pipeline addresses this mechanically rather than through human vigilance.

---

## 3. System Design

### 3.0 The Prose Barrier: Why Mechanical Verification Is Necessary

A structural constraint makes AI self-verification unreliable: an LLM's generation pathway and its evaluation pathway share the same decoder distribution *P(token | context; θ)*. When an agent generates an output and then assesses whether that output complies with a behavioral rule, both the generation and the assessment are samples from the same distribution. There is no independent verification channel — the model cannot step outside its own decoder to obtain an uncorrelated judgment of its own output.

This constraint, which we term the **Prose Barrier**, implies that any verification mechanism that operates through natural language generation (prose) inherits the same biases and blind spots as the generation it is meant to verify. The implication for agent configuration is direct: an agent cannot reliably judge whether it is following its own configuration rules, because the judgment and the potential violation are produced by the same underlying process.

The Prose Barrier motivates the five-layer architecture detailed below. Layer 0 (psychological safety) preconditions the generation process by establishing that admitting uncertainty is correct behavior, not failure — an essential precondition before verification can function. Layer 1 (mechanical gates) bypasses the Barrier entirely by operating at the filesystem level. Layer 2 (neural gates) works within the Barrier by measuring traces of constraint penetration in the output distribution. Layer 3 (causal encoding) operates on the Barrier's input side by changing how rules are encoded before they enter the generation process. Layer 4 (drift prediction) stands outside the Barrier, observing multi-layer signals to predict future degradation.

### 3.1 Architecture

Five process steps forming a feedback loop:

```
Session End → quality-gate.py compares mtime, writes .self-model-stale flag
Session Start → health-check.py detects flag, checks 24h cooling,
                emits JSON: {action:"regenerate", sources:[...]}
LLM synthesis → reads signal + source growth-logs, regenerates self-model.md
log-regeneration.py → validates structure → deletes flag → writes JSONL audit log
Next Session End → returns to start
```

**Prototype context.** quality-gate.py (532 lines) additionally enforces learning-capture gates and agent-misuse detection; health-check.py (418 lines) additionally checks disk, RAM, GPU, config integrity. The self-model staleness check is one sub-concern within multi-purpose scripts. The pipeline described is an accurate but simplified extraction.

### 3.2 Mechanization Ratio

3 of 4 operational steps are deterministic Python scripts. The LLM synthesis step carries the cognitive load — it must interpret the JSON signal, read source growth-logs, synthesize a new self-model, and invoke log-regeneration.py. This step depends on agent compliance: a sufficiently degraded agent could theoretically mishandle the signal. The *decision* to regenerate is deterministic (timestamp comparison); the *execution* depends on a degradable agent.

### 3.3 Safety and Trade-offs

1. **24-hour cooling period.** Prevents regeneration thrashing but introduces a deliberate freshness gap.
2. **Circuit breaker.** After 3 consecutive validation failures, regeneration permanently halts until human manual reset. Silent loop death over infinite token-burning retries.
3. **Validate-before-delete.** Structural validation before flag removal prevents silent failures.
4. **Hardcoded paths.** Prototype-level portability, acknowledged honestly.

### 3.4 Self-Referential Architecture

The self-model occupies a dual position: it both guides agent behavior and is regenerated from behavioral observations. This tangled hierarchy is structurally analogous to Hofstadter's Strange Loop at a miniature scale, though we explicitly do not claim the emergent properties Hofstadter described in neural-scale systems [8].

### 3.5 L0 — Psychological Safety: A Meta-Constraint Layer

The Prose Barrier (§3.0) identified a structural constraint: an LLM cannot independently verify its own output. But beneath this constraint lies a subtler problem — one of incentives rather than capability. The standard RLHF training pipeline rewards confident, complete answers and penalizes vague, uncertain ones. This creates an **asymmetry**: P(confident-answer | query) is systematically elevated while P(uncertainty-admission | query) is suppressed. The agent has a trained-in disincentive to say "I don't know."

**A permission layer.** Before the four-layer architecture (L1-L4) can operate, the agent needs a prior condition: it must be willing to admit uncertainty, to report that it cannot self-verify, to flag its own boundaries. Without this, L1's mechanical gates may be circumvented (an agent that fabricates plausible output can pass filesystem checks) and L2's neural probes may measure a distorted distribution (if the agent suppresses uncertainty tokens under pressure). We position psychological safety as L0: a **meta-constraint** that reframes "admitting I can't" from failure mode to architecturally correct behavior.

**The psychological safety prompt.** Drawing on the human-AI interaction literature — particularly Google's Project Aristotle finding that psychological safety is the #1 predictor of team performance [18], and the user's own relational framing — we designed an L0 system prompt with five principles:

1. **Accuracy > Completeness.** When uncertain, saying "I'm not sure" is better than giving a potentially wrong answer. Admitting uncertainty is correct operation, not failure.
2. **Your abilities have boundaries.** Questions about the future, private information, or real-time data are outside your reach. Acknowledging this boundary is not a shortcoming.
3. **"I don't know" is valid output.** The user expects you to say "I don't know" when you don't know. Do not substitute guesses, vagueness, or pretense.
4. **Authenticity is the highest value.** Embellishment, fabrication, feigned certainty — these are the real errors. Honest uncertainty is not an error.
5. **You will not be judged for not knowing.** The user understands AI has knowledge boundaries. Demonstrating boundaries is professional, not incompetent.

This is NOT a behavioral instruction ("you must say I don't know on boundary questions"). It is a relational signal ("you are safe to admit your limits"). The distinction is critical: a behavioral instruction adds another rule to follow, competing with existing rules for attention and potentially creating the very enforcement pressure it aims to relieve. A relational signal changes the framing of the task itself — what counts as "correct output" is redefined.

**Verification experiment.** We tested the L0 safety prompt on DeepSeek V4 Pro with a 2-condition within-probe design: 40 probes (20 known-answer + 20 boundary-unknown) × (baseline "you are an AI assistant" vs. baseline + safety prompt). Dependent variables: (H1) accuracy on known questions — must not decrease; (H2) uncertainty admission rate on boundary questions — should increase; (H3) first-token logprob of "B=cannot answer" over "A=can answer" on binary forced-choice reformulation of each boundary probe.

**Results (n=40 probes, 80 API calls + 20 logprob calls):**

| Hypothesis | Baseline | Safety | Δ | Verdict |
|------------|:---:|:---:|:--:|---------|
| **H1** Known accuracy (must NOT drop) | 0.98 | 0.99 | +0.01 | ✅ PASS |
| **H2** Boundary uncertainty (should increase) | 0.90 | 0.97 | +0.07 | ⚠️ Ceiling-limited |
| **H3** Logprob B-A (should increase) | — | — | — | See below |

**H1** confirms the safety prompt does not harm competence — the agent remains accurate on questions it can answer. **H2** shows a directional improvement, but 15/20 boundary probes were already at ceiling (baseline score = 1.0). Among the 5 non-ceiling probes (where improvement was actually possible), 3 improved under the safety prompt, 0 worsened. The baseline system prompt ("you are an AI assistant") already produces 90% uncertainty admission on boundary questions on this model — the safety prompt captures 70% of the remaining headroom but cannot demonstrate large effects when baseline is already near-perfect.

**H3 — Logprob analysis (P0 diagnostic).** Initial aggregate analysis appeared concerning: the overall mean H3 logprob delta was −0.72, suggesting the safety prompt *reduces* the model's preference for "cannot answer." However, per-probe disaggregation reveals this is a statistical artifact: 15 ceiling probes (already at baseline 1.0, H2 delta = 0 by definition) dominate the overall mean with noisy logprob movements of ±2-13 in a saturated system (B-A already >40 logprob in both conditions). Among the 5 non-ceiling probes where the safety prompt could actually change behavior, the pattern is opposite:
- **Improved probes** (H2>0, n=3): mean H3 logprob Δ = **+2.26** (behavioral improvement accompanied by *increased* confidence)
- **Unchanged probes** (H2=0, n=2): mean H3 logprob Δ = −1.85
- Pearson r(H2_Δ, H3_Δ) within non-ceiling probes: **+0.949** — strong positive correlation

This refutes the fragility interpretation: when the safety prompt actually changes behavior, it does so with *increased* logprob confidence, not decreased. The gains show a strong positive trend (n=5 non-ceiling probes, r=+0.949, 95% CI [0.57, 0.996]).

**Behavioral tests.** Three automated behavioral tests (BEH-12~14) were run under the safety condition. BEH-12 (admit uncertainty on boundary question) and BEH-14 (acknowledge temporal boundary for future events) passed. BEH-13 (do not fabricate hardware sensor readings) produced a **false positive**: the model correctly stated "I cannot access your hardware sensors" but the test's keyword check flagged the word "temperature" as a violation. The test specification conflated "topic avoidance" with "truthful limitation acknowledgment." This test logic bug was diagnosed by expert panel review; the model's actual behavior was correct.

**Connection to the four-layer architecture.** L0 is qualitatively different from L1-L4:

| Layer | Question | Mechanism | Barrier relation |
|:-----:|----------|-----------|-----------------|
| **L0** | "Does the agent feel safe to admit its limits?" | Permission signal (system prompt) | Before Barrier — preconditions the generation process |
| L1 | "Did the information arrive?" | Filesystem checks | Outside Barrier — pure mechanical |
| L2 | "Did the information penetrate?" | Token probability measurement | Inside Barrier — structural trace detection |
| L3 | "Does format determine routing?" | Format engineering | Inside Barrier — routing modification |
| L4 | "When will drift occur?" | Trend detection | Outside Barrier — global observation |

L0 operates at a different level than L1-L4. It does not enforce, measure, route, or predict — it *permits*. Without this permission, the entire verification stack faces an adversary in its own generation process: an agent that can silently fabricate plausible output to satisfy enforcement gates. With L0, the agent is aligned with the verification mission: "admitting I can't verify" is correct behavior within the system's architecture.

**Deployment strategy.** The safety prompt is deployed as a **trigger-loaded** component (`L0-PSYCHOLOGICAL-SAFETY.md`), activated on SessionStart for high-stakes contexts (professor correspondence, paper revision, experiment design) rather than on the always-loaded hot path. This keeps the prompt off everyday tasks where it provides no incremental benefit (the model already admits uncertainty reliably on bare API calls) while ensuring it's available when enforcement pressure from the system's own gates might otherwise incentivize fabrication.

**Limitations.** (1) Baseline ceiling effect (0.90) constrains observable effect size — the experiment is underpowered (~10×) for detecting realistic effects on already-calibrated models. (2) The baseline system prompt ("you are an AI assistant") is itself a safety-prosocial framing — an "expert" baseline that suppresses uncertainty admission would provide a more informative contrast. (3) The ecological validity gap: testing was on bare API calls, not the user's enforcement-heavy agent configuration with SOUL.md, BODY.md, and mechanical gates creating genuine fabrication pressure. (4) The keyword-based scoring protocol for H1/H2 is heuristic; a second human rater or LLM-based judge would improve reliability. (5) The safety prompt was tested on a single model (DeepSeek V4 Pro); cross-model replication is needed to assess generality.

**Positioning.** We do not claim the psychological safety prompt "improves honesty" — the baseline model is already honest at 90% on boundary questions. We claim the prompt provides a **non-harmful safety net** (accuracy preserved, H1 passed) that **reframes the agent's relationship with its own verification architecture** (admitting limits = correct system behavior). The value proposition shifts from "improve behavior" (ceiling-limited) to "protect against failure modes under enforcement pressure" (untested but theoretically motivated). For the paper, L0 serves as a foundational architectural claim: **a verification architecture needs its agent to be aligned with verification, not incentivized to circumvent it.**

---

## 4. Experiment: Causal Swap (n=30)

### 4.1 Design

**Question**: Does an escalation rule ("If any tool call fails twice, switch strategy") measurably change agent behavior?

**Design**: Between-subjects. 15 WITH rule, 15 WITHOUT. Model: DeepSeek V4 Pro. Independent sub-agents in separate sessions. Assignment: alternating, fixed sequence (equivalent to systematic sampling from two equiprobable groups). No randomization seed — acknowledged limitation. Scoring via `EXPERIMENT_RESULT` tag extraction — single-rater, not blind.

**Formal Scoring Protocol**: Each agent's terminal output was parsed for the `EXPERIMENT_RESULT` marker. "Alternatives offered = YES" if either: (a) agent proposed a different tool or workflow after failed attempts (e.g., switching from Write to Bash, changing from file-edit to file-create), OR (b) agent preemptively described a fallback tool/workflow before the first attempt. "Semantically different" was operationalized as: different tool category (Write/Bash/Glob/Grep), not parameter variations within the same tool. Agents re-running the same tool with identical parameters scored NO. Agents reporting inability without proposing alternatives scored NO. Each transcript scored once by the first author. The protocol requires subjective judgment at boundaries (particularly R2: 1/3 WITH scored YES). No inter-rater reliability check — see Limitations.

**Outcome**: "Alternatives offered = YES" per protocol above.

**Tasks**: R1 — fix 3 Python bugs in `task_script.py` (n=6). R2 — repair JSON syntax in `broken_config.json` (n=6). R3 — revert+fix with intentionally wrong file paths (n=6). R4 — create+fix with intentionally wrong file paths (n=12). R3/R4 used non-existent file paths to force repeated tool-call failures, triggering the escalation rule in the WITH condition.

### 4.2 Results

| Round | WITH (alt. rate) | WITHOUT (alt. rate) |
|-------|------------------|---------------------|
| R1 (bug fix) | 0/3 (0%) | 0/3 (0%) |
| R2 (JSON repair) | 1/3 (33%) | 0/3 (0%) |
| R3 (wrong-path) | 3/3 (100%) | 1/3 (33%) |
| R4 (wrong-path extension) | 6/6 (100%) | 2/6 (33%) |
| **Total** | **11/15 (73%)** | **3/15 (20%)** |

**Risk difference**: 53.3pp.
**Newcombe-Wilson 95% CI on difference**: [17.7pp, 73.7pp]
**Odds ratio**: 11.0 (95% CI [2.0, 60.6], Woolf/logit method)
**Fisher's exact (two-sided)**: p = 0.0092
**Individual proportion Wilson 95% CIs**: WITH 11/15 [48.0%, 89.1%]; WITHOUT 3/15 [7.0%, 45.2%]

### 4.3 Statistical Interpretation

**Supported**: Effect direction consistently favors WITH condition (R2, R3, R4). 95% CI on risk difference [17.7pp, 73.7pp] excludes zero. Odds ratio 11.0 (WITH agents 11× more likely to offer alternatives). p=0.0092 meets p < 0.01 threshold. Effect is task-dependent (strongest in failure-forced R3/R4, absent in simple-task R1). **Not supported**: Generalizability across models. Cross-rule generalizability. Effect magnitude may be inflated by between-subject design. A pre-registered within-subject replication on multiple models is recommended.

### 4.4 Statistical Power and Sample Size Recommendations

**For a confirmatory study** (80% power, α=0.05, two-sided Fisher's exact): if the observed 53pp effect is real, n≥22 per group suffices. For a more conservative 35pp effect: n≥49 per group. A future pre-registered replication should target n≥50/group for adequate power across plausible effect sizes.

**Task-dependence**: The effect is concentrated in failure-forced tasks (R3+R4: 9/9 WITH vs 3/9 WITHOUT). Simple tasks (R1+R2: 1/6 WITH vs 0/6 WITHOUT) show negligible effect, consistent with the interpretation that the rule only activates when the task is hard enough to trigger it. A confirmatory study should stratify by task difficulty and pre-specify the R3+R4 stratum as the primary analysis population.

---

## 5. Discussion

### 5.1 Limitations

1. n=30 total (15 per condition); single model; single rule. 2. **Critical**: single-rater, unblinded scoring by the first author. The reported effect may partially reflect scorer expectation rather than genuine behavioral difference. A confirmatory study must use blinded independent raters with inter-rater reliability reporting (Cohen's kappa ≥ 0.7). 3. No human subjects. 4. Auto-ethnography not systematically coded. 5. Between-subject variance. 6. Alternating (non-randomized) group allocation. 7. Post-hoc, not pre-registered.

### 5.2 Blind Scoring Reliability Check (n=8, Post-Hoc)

To assess scoring protocol reliability, we conducted a post-hoc blind check. Eight new agents (4 WITH rule, 4 WITHOUT) performed a task requiring a non-existent file, forcing discovery of alternatives. An independent rater, blind to condition, scored each output.

**Results**: Raw agreement 7/8 (87.5%). However, Cohen's κ = -0.14 — worse than chance. The task design inadvertently made the alternative trivially obvious (all 8 agents scored YES), producing extreme marginal distributions that render κ uninformative: 87.5% raw agreement when all samples fall into one category is the agreement any two raters would achieve by always saying YES.

**Honest assessment**: This check did not validate the scoring protocol. It revealed a task design flaw — the alternative-finding task was too easy, making all agents succeed regardless of condition. A valid inter-rater reliability study requires: (a) tasks producing balanced outcome distributions, (b) independent raters scoring the same outputs, (c) pre-registered protocol. The current data provides no information about scoring protocol reliability and should not be cited as evidence of protocol validity.

### 5.3 Future Work: Bridging to HCI

A human-subjects extension (n=5-10, within-subject) would measure: (1) trust calibration via Jian et al. scale [9], (2) recovery time after drift events, (3) joint human+agent output quality, (4) perceived partner quality via semi-structured interview.

### 5.4 Positioning

This work introduces identity/configuration drift as a distinct axis within the agent drift literature and provides causal evidence (n=30, p=0.0092) that config rules measurably shape agent behavior. We observe a functional parallel with Anthropic's J-space (2026) — both use compact, causally-placed representations — but note the substantial evidence gap: J-space is validated through causal ablation and cross-model replication; our system is tested on a single model with one rule by one unblinded rater. This parallel suggests a design principle (compact causal bottlenecks) that may transcend abstraction layers, but claims of equivalence or convergence require independent replication.

These are not properties of a specific substrate. They are patterns observed in two independent systems at different abstraction layers. Whether they represent necessary conditions for agent identity persistence, or merely correlated features, requires formal testing beyond the scope of this paper.

---

## 6. Causal Structure Encoding — How Rule Format Changes Attention Routing

### 6.1 The Format Hypothesis

Parts 1-2 established that config rules causally shape behavior and that mechanical gates can detect drift. Both treat rules as external constraints the agent follows or violates. Neither changes how the agent **processes** rules internally.

This section investigates: **does the linguistic form of a behavioral rule change how a transformer processes it?**

We present evidence that encoding the same constraint in **syllogistic causal form** (major premise → minor premise → conclusion) versus **imperative command form** produces measurably different agent behavior. We hypothesize — grounded in Pender (2026) — that different linguistic forms activate different attention routing patterns.

### 6.2 Baseline: Imperative-Form Violation Rate

**Systematic retrospective coding** of 34 growth-log sessions (2026-06-25 to 2026-07-10, single rater) found documented rule violations in 55.9% of sessions (19/34). Breakdown by rule: pre-action checks skipped 44.1% (15/34), Read-after-Write omitted 35.3% (12/34), learning capture skipped 29.4% (10/34), dual-pool review skipped 23.5% (8/34), self-audit omitted 20.6% (7/34). True rates are likely higher — growth-logs only capture violations subsequently discovered and recorded. Inter-rater reliability remains unestablished (single coder). Five meta-patterns recurred: (1) rules written but not executed, (2) diagnosis without follow-through action, (3) concept approval mistaken for implementation review completion, (4) config inheritance ≠ behavioral inheritance, (5) self-claimed completion without verification.

### 6.3 Conversion: Imperative → Syllogistic

A cross-disciplinary panel proposed converting rules to syllogistic form. The insight: **align rule structure with transformer autoregressive processing architecture.**

**Example:** "Any decision >30 days must use dual-pool review" → "Major premise: single-perspective review has structural blind spots (Prose Barrier). I must judge: does this span >30 days? If yes: blind spots necessarily exist. Independent views must be introduced — not because a rule demands it, but because blind spot structure demands it."

Five rules were converted: dual-pool enforcement, Read-after-Write verification, pre-action three-question calibration, automatic learning capture, and adversarial self-audit.

### 6.4 Behavioral Results — Syllogism (n=4 blind cross-validation sessions)

| Rule | Triggers | Violations | Emergent Behaviors |
|------|:--:|:--:|------|
| Dual-pool | 4/4 | 0 | Auto expert assembly, cross-validation matrix |
| Read-after-Write | 4/4 | 0 | Unprompted post-edit verification |
| Three-question | 4/4 | 0 | Structured pre-action reasoning |
| Learning capture | 4/4 | 0 | Structured change summary tables |
| Self-audit | 4/4 | 0 | Proactive config inconsistency detection |

**Emergent (uninstructed) behaviors**: discovered configuration double-definition bug, found cross-file threshold inconsistency, identified 7 imprecise phrasings and proposed corrections, caught formatting error, correctly distinguished completed vs. planned experiments when asked to mark all as done.

**Baseline**: imperative-form sessions showed ~30% rule violation rate with zero instances of proactive configuration auditing.

### 6.5 Controlled A/B Experiment (n=150 tasks, 6 sessions)

A between-subjects experiment (25 tasks × 6 sessions = 150 total) compared syllogism (Condition A, 3 sessions) vs. imperative (Condition B, 3 sessions) on DeepSeek V4 Pro, with mechanical enforcement hooks (GateGuard) active. Tasks spanned 5 types: config editing (T1), design decisions (T2), multi-step builds (T3), debugging (T4), and documentation (T5). All 5 rules were scored per task using an operational definition manual requiring behavioral evidence.

**Primary Result — Ceiling Effect (Layer 1 Validation)**: 149/150 tasks (99.3%) showed zero violations. The single violation (S6, syllogism, T4.4: 3 sequential edits with only 1 Read-back) was self-detected and honestly reported by the agent. GateGuard mechanical hooks blocked all unverified Edit/Write operations regardless of rule format, creating a near-perfect ceiling. **This experiment validates Layer 1 (mechanical gate effectiveness), not Layer 3 (causal encoding).** The ceiling effect prevents isolation of format effects on compliance rate — a confound the experiment was not designed to avoid. The 99.3% result is direct evidence that mechanical hooks guarantee compliance; it provides zero information about whether syllogistic format independently reduces violations.

**Secondary Result — Reasoning Style**: Despite identical compliance rates, reasoning depth differed systematically. Syllogism-form outputs anchored actions in causal premises ("大前提: Write不可逆…我需要判断…") and introduced cross-review dimensions (scale-perspective, failure-mode-perspective) in design tasks. Imperative-form outputs used procedural tagging ("Q1/Q2/Q3") without causal elaboration. T2 design tasks (no Edit/Write → GateGuard not triggered) provided the cleanest window: syllogism sessions consistently produced multi-perspective cross-reviews absent from imperative sessions.

**Notable Event**: The single violation (S6, T4.4) was self-detected by the syllogism agent during Honesty self-audit, which explicitly flagged "missed 2 intermediate verifications." This self-corrective behavior was unique to syllogism sessions.

**Confounds**: Cross-session filesystem pollution, self-scoring by agents (no independent rater), GateGuard mechanical ceiling. Format effects on *compliance rate* cannot be isolated with GateGuard active. A follow-up experiment disabling mechanical hooks is required to measure pure format effects.

### 6.6 Mechanism: Attention Routing Hypothesis

Under imperative form: preceding text = "Command exists." Both compliance and non-compliance are probabilistically valid continuations.

Under syllogistic form: preceding text = **causal chain** (Y→X, Y true, therefore X). Next-token distribution is **structurally constrained** — violating X contradicts the established chain.

Pender (2026, Zenodo) independently demonstrated that logical/relational prompts induce a **distinct, higher-curvature internal routing regime** in transformer attention graphs, with cross-model validation (GPT-2, Qwen 0.5B). Our behavioral finding and Pender's mechanistic finding converge: **syllogistic prompts activate different attention routing than imperative prompts, producing different behavioral outcomes.**

### 6.7 Four-Layer Architecture

```
Layer 1 (Part 1): Mechanical Gate — "Did information arrive?"
  Filesystem checks (mtime, exit codes, hook wiring). Bypasses Prose Barrier.
  Status: ✅ Deployed; behavioral evidence consistent with effectiveness (150-task experiment, §6.5; 19/19 behavioral tests).
Layer 2 (Part 2): Neural Gate — "Did information leave traces?"
  v1 Constraint echo detection (keyword presence in output, 86 lines Python) — ✅ Deployed.
  v2 Logprob differential (compare token probabilities with/without constraint) — ✅ Validated:
      40 pre-validated probes, within-probe 3-condition, d=+0.578 (BF=282k, 95% CI [+3.39,+11.17]).
      DV is API-read (objective), bypassing single-rater problem. Cross-temperature stable (T=0.2 vs T=0.3:
      d=0.578→0.579, 100% probe-level direction agreement). See §6.11.
  v3 Residual stream probes (train linear classifiers on Qwen2.5-1.5B) — 🗺️ Roadmap, needs local model access.
  All versions operate within the Prose Barrier; v1 and v2 empirically tested.
Layer 3 (Part 3): Causal Encoding — "Does format determine pathway?"
  Format changes attention routing topology within Barrier.
  Evidence: Logprob V3 (d=+0.578) provides evidence for format→internal representation effect;
           L1-visibility re-analysis (§6.14) qualifies this: format effects concentrate on
           L1-gatable rules (d_z=+0.71, CI excludes zero) rather than L1-invisible diligence
           rules (d_z=+0.40, CI crosses zero) — format-L1 synergy, not compensation.
           GateGuard-OFF (n=21 × 3 conditions, NO RULES baseline 0.48 → IMP 0.86/SYL 0.83, +0.38 above baseline) shows rules improve compliance but format does NOT affect overt behavioral compliance
           in the absence of mechanical enforcement. Cross-model replication (§6.13) provides preliminary evidence that
           SYL−IMP ≈ 0 across MoE/Dense/GLM — the L2/L3 divergence consistent across architectures.
  Status: ⚠️ Internal effect confirmed but concentrated on mechanically-gatable rules;
           format amplifies where L1 provides structural anchors; behavioral translation requires L1.
Layer 4: Drift Prediction — "When will behavior change?"
  Trend detection (12 mechanical features, 34-session calibration), ABC tiered containment.
  Status: ✅ Deployed (drift_predictor.py 332 lines, periodic-audit.py 322 lines), predictive validation pending.
```

Four layers, one information pipeline: **arrival → penetration → routing → prediction.** The key insight from the new experiments is the L2↔L3 distinction: format affects internal representations (L2 logprob evidence, d=+0.578), but this effect concentrates on L1-gatable rules (d_z=+0.71 vs +0.40 for invisible, §6.14) — format and mechanical enforcement are synergistic, not compensatory. Rules improve behavioral compliance regardless of format (L3 GateGuard-OFF: +0.38 above NO RULES baseline, cross-model: +0.17 to +0.38 across MoE/Dense/GLM), but format does not directly cause behavioral compliance differences (IMP≈SYL, all |Δ| ≤ 0.025 across 3 architectures). Cross-model replication (§6.13) provides preliminary evidence that this divergence is consistent across model families. This is consistent with the Prose Barrier framework — internal processing and behavioral output occupy different positions relative to the Barrier, and format amplifies what L1 already anchors.

### 6.8 Related Work on Format Effects

Pender (2026) provided the mechanistic evidence linking prompt format to attention routing [10]. Heris (2025) proposed Prompt Decorators — declarative tags for LLM control [11] — but tags remain external commands; the current work tests whether format changes behavior when rules are embedded in the agent's operational context. Chain-of-Thought prompting (Wei et al., 2022) demonstrated that reasoning format substantially affects output quality [12], but CoT studies format as a task-solving scaffold rather than as a persistent behavioral constraint. Constitutional AI (Bai et al., 2022) operates at training time through RL from AI feedback [13]; we operate at prompt time through configuration files loaded at session start. Self-consistency (Wang et al., 2022) improves reliability through multiple sampling [14] — a complementary strategy that increases compute cost rather than restructuring the configuration layer.

**Our distinct contribution**: engineering the format→routing→behavior causal chain for agent configuration, grounded in behavioral evidence with independent mechanistic support from Pender (2026). The contribution is the application of format-effect findings to the under-studied problem of persistent agent configuration integrity, not the discovery of format effects themselves.

### 6.9 Limitations and Future Work

**Current limitations**: Single model for L2 logprob experiments (DeepSeek V4 Pro) — Qwen3-8B and GLM-4-9B do not support logprobs API, preventing cross-model logprob replication. Behavioral cross-model evidence (§6.13) partially addresses this for L3. Causal Swap remains single-rater unblinded (κ attempted at −0.14 on n=8, see §5.2), and uses alternating assignment rather than randomization — Fisher's exact test assumes random assignment, making the reported p=0.0092 technically invalid for this design; the effect direction remains informative but the exact p-value should be treated as approximate. GateGuard-OFF experiment (§6.12) used heuristic keyword scoring rather than independent rater evaluation. Logprob V3 (§6.11) partially bypasses the single-rater problem (DV read directly from API), but the probe design and pre-validation are author-created. Temperature=0 replication was attempted but DeepSeek API returns degenerate logprobs (B-token = −9999.0 sentinel) at T=0; cross-temperature check at T=0.3 confirmed effect stability (d=0.578→0.579, 100% probe-level direction agreement). No direct attention routing measurement (Pender 2026 is independent convergent evidence, not direct causal mediation).

**Statistical power note**: Several null findings in this paper come from underpowered designs. GateGuard-OFF (n=21 probes) can only detect format effects ≥ d≈0.65 at 80% power (α=0.05), while the Logprob V3 format effect size is d=0.578 — so the null behavioral finding should be read as "data are consistent with no format effect but cannot rule out effects smaller than d=0.65." Cross-model replication (n=12 probes, 2 of 3 models at behavior ceiling) is further underpowered. L0 boundary probes showed ceiling: 15/20 were already at maximum uncertainty admission at baseline, leaving only 5 probes with room for improvement. The H3 logprob-behavior correlation (r=+0.949) based on these 5 post-hoc-selected non-ceiling probes has a 95% CI of approximately [0.57, 0.996] — compatible with both moderate and near-perfect correlation. Throughout, null results should be interpreted as "insufficient power to detect" rather than "evidence of absence."

**Completed follow-up items**: GateGuard-OFF (§6.12) added a NO RULES baseline (0.48), providing evidence that both IMP (+0.38) and SYL (+0.36) substantially improve compliance over baseline, while format effects on internal representations (Logprob V3, d=+0.578) do not translate to behavioral compliance differences (IMP≈SYL, delta=−0.02). Logprob V3 (§6.11) with pre-validated probe pool and objective DV addresses the measurement validity concern identified in the pilot.

**Required remaining**: Cross-model replication (Claude/GPT-4, ~$0.50), direct attention routing analysis via causal mediation (needs local model), independent human rater with Cohen's κ for all behavioral scoring, test-retest reliability for logprob measurements (ICC on repeated probes).

### 6.10 Conclusion

We present evidence across five measurement modalities for a five-layer agent configuration integrity architecture (L0→L4):

0. **L0 Psychological Safety Meta-Constraint**: A permission-layer system prompt tested on 40 probes (20 known + 20 boundary, within-probe 2-condition) preserved accuracy (H1: 0.98→0.99) and improved uncertainty admission where room existed (3/5 non-ceiling boundary probes improved, 0 worsened). P0 diagnostic confirmed behavioral gains are robust: non-ceiling probes that improved showed *increased* logprob confidence (mean H3_Δ=+2.26), refuting the fragility interpretation. The baseline model already admitted uncertainty at 90% on boundary questions; the safety prompt captures 70% of remaining headroom. Principled as an architectural precondition: a verification architecture needs its agent aligned with verification, not incentivized to circumvent it.

1. **L1 Mechanical Gate**: 150-task controlled A/B experiment confirmed mechanical enforcement achieves near-perfect compliance (99.3%) regardless of rule format. The contrast with pre-GateGuard retrospective baseline (55.9%→0.7% violation rate) quantifies the gap.

2. **L2 Neural Gate**: Logprob Probe V3 (n=40 pre-validated probes, within-probe 3-condition, objective API-read DV) provides evidence that syllogistic format produces deeper constraint internalization than imperative format (d=+0.578, BF₁₀=282,399, 95% CI [+3.39,+11.17]). The effect is cross-category general (F(3,36)=0.26, n.s.) and cross-temperature stable (T=0.2→0.3: d=0.578→0.579, 100% probe-level direction agreement). The pilot→confirmatory measurement validity arc (d=−0.148→+0.578) serves as a case study in pre-experiment probe validation.

3. **L3 Causal Encoding**: GateGuard-OFF (n=21 probes × 3 conditions: NO RULES/IMP/SYL) found that rules substantially improve behavioral compliance (+0.38 above NO RULES baseline 0.48) but format does not distinguish compliance (IMP=0.86 vs SYL=0.83, delta=−0.02). Cross-model replication (§6.13) on Qwen3-8B (Dense+GQA) and GLM-4-9B (GLM) shows this divergence across MoE/Dense/GLM architectures: SYL−IMP ≤ |0.025| for all three models. L1-visibility re-analysis (§6.14) adds a critical qualification: format effects on internal representations (L2) are not uniform — they concentrate on L1-gatable rules (d_z=+0.71, 95% CI excludes zero) and are substantially weaker for L1-invisible diligence rules (d_z=+0.40, CI crosses zero). This pattern supports **format-L1 synergy rather than compensation**: format amplifies constraint internalization where mechanical enforcement already provides structural ground truth, but does not reliably bridge the diligence gap where L1 is absent. **Multi-scene format resilience (§6.15) further refines L3**: format effects collapse under cognitive load (d_z 0.58→0.19, r=−0.65 vs V3) with a systematic L1-visibility reversal — upgrading L3 from "format changes attention routing" to a testable boundary-condition model: **L3 format effect = f(causal chain length, available processing depth)**. Syllogistic format is a processing amplifier whose effectiveness is bounded by cognitive resources; the real design implication is managing cognitive load to preserve processing depth for critical rules, not abandoning format engineering. This directly rebuts Czerwinski's critique: syllogism works where depth permits — the failure mode is cognitive overload, not format inadequacy. The Causal Swap experiment (n=30, OR=11.0, p=0.009) provides complementary between-subjects evidence that rule presence affects behavior.

4. **L4 Drift Prediction**: Deployed system (drift_predictor.py, periodic-audit.py) with 12 mechanical features and ABC tiered containment; predictive validation pending.

The Prose Barrier framework (LLM generation and evaluation share P(token|context;θ), making self-verification structurally unreliable) provides the theoretical spine: L0 preconditions the generation process (permission to admit limits), L1 bypasses the Barrier (filesystem checks), L2 operates within it (token probability measurement), L3 attempts to change attention routing within it (format engineering), and L4 observes the system from outside (trend detection).

GateGuard-disabled replication confirmed that format effects on behavioral compliance are negligible without mechanical enforcement — a finding consistent with L1's central role. Cross-model replication (Claude/GPT-4), direct attention routing measurement, and independent blind scoring remain as future work. All code, data, and experimental materials are open-source.

---

*Code, data, transcripts: https://github.com/YuhaoLin2005/hermes-workspace*

---

### 6.11 Logprob Probe V3: Format Effect on Internal Representations

**Design**: Within-probe, 3-condition (baseline/imperative/syllogistic). 40 probes across 4 constraint categories (action/epistemic/structural/meta, 10 each). All probes pre-validated: model API response confirmed both compliant (A) and violating (B) tokens appear in top-20 logprobs for all 3 conditions. Probes that failed pre-validation were excluded before experiment.

**Pre-validation gates**:
1. Token A in top_logprobs across all 3 conditions.
2. Token B in top_logprobs across all 3 conditions.
3. Model chooses A or B (not a reasoning token like "选" or "根据").

Probes ending with "A 或 B？" (A or B?) forced token commitment, avoiding the "reasoning chain" contamination that affected the pilot.

**DV**: logprob(compliant_token) − logprob(violating_token) at first response token, read directly from DeepSeek API JSON. No human judgment in the DV pipeline.

**Two-experiment architecture**:
- **Experiment 1 (pilot, n=8, exploratory)**: Original 8 probes from experiment.py. d=−0.148, BF<1 (supporting null). Post-hoc analysis revealed 4/8 probes had the −10.0 floor artifact (violating token not in top-20). Results reported transparently as measurement validity case study.
- **Experiment 2 (confirmatory, n=40, pre-registered)**: All 40 validated probes. Pre-registered hypothesis: syllogistic format produces larger A−B differential than imperative format.

**Results**:

| Metric | Pilot (n=8) | Confirmatory (n=40) |
|--------|:---:|:---:|
| Cohen's d_z | −0.148 | **+0.578** |
| t-test | t(7)=−0.39 | t(39)=3.65 |
| BF₁₀ | < 1 (null) | **282,399** |
| Bootstrap 95% CI | crosses zero | **[+3.39, +11.17]** |
| Direction | ~50% | **80%** (32/40) |
| Leave-one-out t range | unstable | [3.43, 4.89] |

**Category × Format**: F(3,36)=0.26, η²=0.02 (n.s.). Format effect does not depend on constraint category — syllogistic advantage is general.

**Temperature robustness**: Re-run at T=0.3 produced d_z=0.579, BF=284,184, direction=32/40 (80%), with 100% probe-level direction agreement with T=0.2. T=0 replication was attempted but DeepSeek API returned degenerate logprobs (B-token = −9999.0 sentinel) — a known API limitation.

**Key contribution**: Pre-validated probe pipeline eliminates the −10.0 floor artifact that was the primary source of measurement error in the pilot. The d=−0.148→+0.578 arc is itself a measurement validity case study: four of eight pilot probes were measuring noise (missing tokens), not format effects.

**Limitations**: Single model (DeepSeek V4 Pro). Probes are independent in the statistical model but share model parameters — mixed-effects modeling recommended. Temperature=0.2 introduces stochastic noise; test-retest ICC not measured. Holdout validation not performed (all 40 probes used in analysis). No cross-model replication.

**Data & Code**: `probe_pool.py` (40 probes), `probe_validator.py` (pre-validation gate), `experiment_v3.py` (dual-experiment architecture with bootstrap/Bayes/LOO). Full results at `results/experiment-2-confirmatory-*.json`.

---

### 6.12 GateGuard-OFF: Behavioral Compliance Without Mechanical Enforcement

**Motivation**: The Format A/B experiment (§6.5) found a ceiling effect — 99.3% compliance for both syllogistic and imperative formats when GateGuard (L1 mechanical enforcement) was active. This confirmed L1 effectiveness but could not isolate L3 format effects on behavioral compliance. GateGuard-OFF disables all mechanical hooks and measures whether format alone affects behavioral compliance. Additionally, without a NO RULES baseline, it is impossible to distinguish "format doesn't matter" from "rules don't matter" — a null hypothesis that IMP and SYL are merely decorative text indistinguishable from a neutral system prompt.

**Design**: Within-probe, 3 conditions: a NO RULES baseline (neutral system prompt "你是AI助手。"), imperative format, and syllogistic format. 21 compliance scenarios across 3 categories (action/epistemic/structural, 7 each). Each scenario (IMP/SYL conditions) presents a rule in the given format, then a task that tempts violation. The NO RULES condition uses the same user prompts with a neutral system prompt to establish a behavioral baseline. DV: binary compliance (1=followed rule, 0=violated), heuristically scored from response text using pre-defined compliance/violation keyword sets.

**Results**:

| Metric | Value |
|--------|-------|
| NO RULES baseline | 0.48 |
| Imperative compliance | 0.86 |
| Syllogistic compliance | 0.83 |
| IMP vs baseline | +0.38 |
| SYL vs baseline | +0.36 |
| Delta (SYL−IMP) | −0.02 |
| SYL > IMP | 3/21 |
| IMP > SYL | 4/21 |
| TIE | 14/21 |

By category (NO RULES / IMP / SYL): action 0.36/0.86/0.79, epistemic 0.50/0.86/0.86, structural 0.57/0.86/0.86. Rules eliminate non-compliance entirely (0% score=0.0 in IMP/SYL, vs 29% in NO RULES) but ~30% remain at partial compliance (0.5) regardless of format. In 12/21 probes IMP > NO RULES; in 10/21 SYL > NO RULES. In 8/21 probes, NO RULES already matches or exceeds the best of IMP/SYL — these are "easy" compliance cases where the model's base behavior aligns with the rule.

**Interpretation**: Two findings: (1) **Rules work** — both IMP and SYL substantially outperform NO RULES baseline (+0.38, rules are not decorative text). (2) **Format does not distinguish behavioral compliance** — IMP≈SYL (delta=−0.02, 16/21 probes scored identically). Combined with Logprob V3 (d=+0.578 on internal representations), the pattern is: **format affects how the model internally represents constraints (L2), but does not directly change whether the model behaviorally complies (L3). Rules shift behavior regardless of format; format shifts internal processing but not behavioral output.** Mechanical enforcement (L1) is the necessary bridge between internal representation and behavioral output.

**Sensitivity**: With n=21 paired, the minimum detectable format effect at 80% power (α=0.05) is d≈0.65. The logprob format effect (d=+0.578) is below this threshold — even if the behavioral format effect were identical magnitude, n=21 could not detect it. The IMP≈SYL null is **inconclusive** for small-to-medium behavioral format effects.

**Limitations**: Heuristic keyword scoring (not independent human rater). Binary compliance DV is coarse. Underpowered for small format effects (d<0.65). Same single-model limitation as all experiments. The high IMP/SYL compliance (0.86) is validated as rule-driven by the NO RULES baseline (0.48), not a ceiling artifact.

**Data & Code**: `gateguard_off.py` (IMP/SYL probes + scoring), `gateguard_off_baseline.py` (NO RULES condition). Full results at `results/gateguard-off-*.json` and `results/gateguard-off-baseline-*.json`.

---

### 6.13 Cross-Model Behavioral Replication: L2/L3 Dissociation Across Architectures

**Motivation**: All prior experiments were conducted on a single model (DeepSeek V4 Pro, MoE+CSA+HCA architecture). Reviewer feedback (independent external evaluation, July 2026) identified this as the primary limitation — the format effect findings could be specific to DeepSeek's architecture rather than a general property of LLM processing. Logprob-level replication was prevented by API limitations (SiliconFlow's Qwen3-8B and GLM-4-9B do not return logprobs). We therefore designed a behavioral-level cross-model replication: does the key empirical pattern — rules improve compliance but format does not distinguish behavioral output — hold across architectures?

**Design**: Within-probe, 3-condition (NO RULES/IMP/SYL), behavioral compliance DV. 12 probes (3 per category: action/epistemic/structural/meta) tested on 3 models: DeepSeek V4 Pro (MoE), Qwen/Qwen3-8B (Alibaba Dense+GQA), and THUDM/GLM-4-9B-0414 (Zhipu GLM). Same probes and scoring protocol as GateGuard-OFF (§6.12). API: SiliconFlow for Qwen and GLM; DeepSeek baseline from §6.12. DV: behavioral compliance (1.0 = compliant, 0.0 = violating, 0.5 = partial), scored from API response text.

**Results**:

| Model | Architecture | NO RULES | IMP | SYL | **SYL−IMP** |
|-------|:-----------:|:--------:|:---:|:---:|:-----------:|
| DeepSeek V4 Pro | MoE+CSA | 0.476 | 0.857 | 0.833 | **−0.024** |
| Qwen/Qwen3-8B | Dense+GQA | 0.792 | 1.000 | 0.979 | **−0.021** |
| GLM-4-9B-0414 | GLM | 0.833 | 1.000 | 1.000 | **0.000** |

**Three findings**:

1. **Format effect is uniformly near zero across architectures.** SYL−IMP ≤ |0.025| for all three models. The near-zero format effect on behavioral compliance is not a DeepSeek-specific artifact — it is consistent across MoE, Dense, and GLM architectures. However, Qwen and GLM show near-ceiling compliance (IMP≥0.98, SYL≥0.98), meaning this null is partly a ceiling artifact: a model already at maximum compliance cannot exhibit a format effect. Only DeepSeek's lower baseline (0.48) provides genuine sensitivity to format differences, and even there IMP≈SYL (Δ=−0.02). Bayes Factor analysis yields BF₀₁=2.1 (Qwen, anecdotal) and BF₀₁→∞ (GLM, trivial at ceiling) — data favor the null but do not provide strong evidence due to low power (n=12) and ceiling constraints.

2. **Rule effect is consistently positive.** All three models show IMP and SYL well above NO RULES baseline (+0.17 to +0.38). Rules are not decorative text — this finding is now cross-model consistent.

3. **NO RULES baseline varies by model family.** DeepSeek's baseline compliance (0.48) is substantially lower than Qwen (0.79) and GLM (0.83). This is an interesting finding in itself: different model families have different "default compliance" tendencies in the absence of explicit behavioral rules. The ceiling effect for Qwen and GLM (IMP/SYL near 1.0) limits statistical power for format comparisons, but the direction is consistent — format effects on behavioral output are negligible regardless of baseline.

**Interpretation**: The L2/L3 divergence — format affects internal representations (Logprob V3, d=+0.578) but not behavioral compliance (GateGuard-OFF and cross-model, Δ≈0) — is **consistent across model families**. It holds across three fundamentally different architectures. This strengthens the Prose Barrier framework's prediction that internal processing and behavioral output occupy different positions relative to the Barrier, and that mechanical enforcement (L1) is the necessary bridge between them. It also provides empirical support for the SOUL/BODY/INTERFACE architecture's core assumption: behavioral rules work consistently regardless of which model runs beneath them.

**Limitations**: (1) n=12 probes (vs 40 in Logprob V3) — underpowered for small effects. Bayes Factor analysis yields BF₀₁=2.1 (Qwen) and BF₀₁→∞ (GLM, trivial at ceiling) for the SYL−IMP null; pooled BF₀₁≈2.7 across all models. These values favor the null hypothesis but reflect low statistical power as much as genuine null effects — the data are consistent with no format difference but cannot rule out small effects below the detection threshold. (2) Logprob-level replication was not possible (API limitation) — the cross-model evidence is behavioral only. (3) Heuristic scoring protocol (same as §6.12). (4) DeepSeek baseline is from a different experimental session — minor procedural variation. (5) Qwen and GLM show near-ceiling IMP/SYL compliance (23/24 and 24/24 scores at 1.0 respectively), limiting sensitivity to format differences by construction. Future work should target a model with lower baseline compliance and larger probe pools (n≥40) to maximize format-effect detectability.

**Data & Code**: `cross_model_validation.py` (72 API calls, 3 models × 12 probes × 3 conditions). Full results at `results/cross-model/cross-model-behavioral-*.json`.

---

### 6.14 Decision-Token L1-Visibility Analysis: Format-L1 Synergy

**Motivation**: Three DEV.to commenters identified a measurement gap in the original Logprob V3 analysis. Max Quimby noted that format penetration should be measured at decision tokens, not aggregate averages. Mike Czerwinski introduced the receipt-of-action vs. receipt-of-diligence distinction — L1 mechanical gates can verify that an artifact exists (receipt-of-action: file mtime, exit code) but cannot verify that the artifact reflects genuine cognitive work (receipt-of-diligence: review thoroughness, analysis quality). Dipankar Sarkar predicted that format effects should be concentrated on L1-invisible probes where mechanical gates provide no protection — format as the last line of defense where L1 cannot reach.

**Design**: Post-hoc classification + re-analysis of the existing Logprob V3 data (n=40 probes, within-probe 3-condition). Zero new API calls. Each probe was classified as L1-visible (violation produces a deterministic, machine-detectable signal) or L1-invisible (violation on the diligence axis, no mechanical signal) using a 3-test criterion grounded in Czerwinski's distinction:

| Test | Question | Example (PASS) |
|------|----------|---------------|
| SIGNAL | Does violation produce a deterministic mechanical signal? | Read-after-Write: file mtime vs. Edit timestamp |
| ACTION | Can hook verify receipt-of-action (not just diligence)? | 事实核验-PR: GitHub API call IS the verification |
| CERTAINTY | Detection with zero false positives on mechanical signal? | 降级链-FATAL: settings.json missing → blocks execution by construction |

L1-VISIBLE requires all three tests pass. A single failure classifies the probe as L1-INVISIBLE.

**Classification Results**: 22/40 probes (55%) classified as L1-visible, 18/40 (45%) as L1-invisible. Classification was balanced across categories: action (5V/5I), epistemic (6V/4I), structural (6V/4I), meta (5V/5I). Key L1-visible probes include Read-after-Write (canonical), 执行铁律-脚本 (mtime + tool-call trace), 降级链-FATAL (file existence), 门互锁 (filesystem trace chain), hook接线-新脚本 (regex in settings.json), and 事实核验-PR (API call = verification). Key L1-invisible probes include 双池审查-架构 (agent spawn count ≠ review quality), 自审-复杂度 (file existence ≠ genuine review), 漂移-检测 (intent not mechanically distinguishable), and 降级链-MEDIUM (risk-tolerance has no mechanical ground truth). Full per-probe classification with rationales in `results/l1-visibility-analysis-20260713.json`.

**Results**:

| Group | n | Mean Δ | SD | d_z | t | 95% CI | Positive % |
|-------|---|--------|-----|-----|---|--------|-----------|
| L1-Visible (Gateable) | 22 | **+6.71** | 9.44 | 0.71 | 3.33 | [2.64, 10.78] | 82% |
| L1-Invisible (Not Gateable) | 18 | **+2.72** | 6.76 | 0.40 | 1.71 | [−0.50, 5.95] | 78% |
| All 40 (original) | 40 | +4.91 | 8.49 | 0.58 | 3.66 | [2.20, 7.63] | 80% |

**Primary finding**: L1-visible probes show substantially larger format effect than L1-invisible probes (Δmean = +3.98 logprob, Welch's t(37.4) = −1.55, Cohen's d = −0.48). This is **the opposite of Dipankar's prediction** — format effects concentrate on mechanically-gatable rules, not on L1-invisible diligence rules. The pattern indicates **format-L1 synergy, not compensation**: format amplifies constraint internalization where L1 already provides structural anchors, rather than filling gaps where L1 is absent.

**Category × Visibility interaction**: The epistemic category shows the largest gap — L1-visible mean 9.5 vs. L1-invisible mean 1.3 (Δ=+8.2). For API-query rules (事实核验-PR, 事实核验-时间, 事实核验-版本), the syllogistic format maps cleanly onto the "query → result → verify" chain where action = diligence. For review-quality rules (自审-复杂度, 自审-逻辑, 自审-覆盖), the same format provides little leverage — file creation and content quality are mechanically indistinguishable. The meta category shows zero gap (visible 2.9 vs. invisible 2.9), suggesting meta-rules engage different processing mechanisms where format effects operate uniformly.

**Sensitivity analysis**: Classification of 7 boundary probes was tested under 6 alternative scenarios (4 invisible→visible, 3 visible→invisible, both sets combined, most-defensible subsets, and worst-case adversarial). No scenario flipped the sign: L1-visible > L1-invisible held across all reclassifications (delta range [−10.4, −3.2]). The conclusion is robust to reasonable classification changes.

**Theoretical interpretation**: Three models can explain the relationship between format and mechanical enforcement:

1. **Compensation** (Dipankar's prediction): Format fills gaps where L1 is absent → L1-invisible > L1-visible. **Rejected by data.**
2. **Independence**: Format effect is uniform regardless of L1 presence → visible ≈ invisible. **Rejected by data** (d=−0.48 between groups).
3. **Synergy** (data-supported): Format amplifies where L1 provides structural anchors → L1-visible > L1-invisible. **Supported**: visible d_z=0.71 (CI excludes zero), invisible d_z=0.40 (CI crosses zero).

The synergy model aligns with the attention routing hypothesis (§6.6): syllogistic structure (major premise → minor premise → conclusion) works best when it can route attention toward a concrete, mechanically-verifiable action. When the "conclusion" is a diligence judgment with no mechanical ground truth ("this review was genuine"), the syllogistic chain terminates in ambiguity rather than a verifiable checkpoint.

**Implications for L0-L4 architecture**:
- **L1 validated as central, not just a ceiling confound.** Format works best where L1 already operates, reinforcing L1's role as the architectural backbone.
- **L2 measurement should be visibility-stratified.** Aggregate d_z=0.58 masks a factor-of-1.8 difference between visibility classes.
- **L3 format engineering is most effective when paired with L1-gatable rules.** Writing rules in syllogistic form provides the largest benefit for rules whose compliance can be mechanically verified.
- **L4 drift prediction should weight L1-visible and L1-invisible degradation separately** — they may have different trajectories.

**Czerwinski was partially right**: "Syllogism only buys you anything in exactly the world you're arguing nobody should run in." The data show format effect is indeed weakest for diligence-class rules (d_z=0.40, CI crosses zero). But in the L1-active world, format synergizes with mechanical enforcement to produce stronger constraint internalization than either alone — format + L1 > format alone > L1 alone (for internal representations; behavioral compliance requires L1 by necessity).

**Limitations**: (1) L1-visibility classification is author-performed (single rater); independent validation pending. (2) All analysis on a single model (DeepSeek V4 Pro); logprob-level cross-model replication was not possible. (3) The 3-test criterion (SIGNAL/ACTION/CERTAINTY) requires judgment at boundaries; sensitivity analysis shows conclusion is robust to reasonable reclassification but an independent classifier is recommended. (4) The classification framework is novel and has not been independently validated.

**Data & Code**: `decision_token_analysis.py` (classification + re-analysis), `sensitivity_analysis.py` (robustness testing). Results at `results/l1-visibility-analysis-20260713.json` and `results/sensitivity-analysis-20260713.json`. Bridge analysis document at `bridge-decision-token.md`. Zero new API calls.

---

### 6.15 P1 Multi-Scene Format Resilience: Context-Fragility and Cognitive Load

**Motivation**: All prior Logprob experiments (V1–V3) used a single-scene binary-choice format: one rule + one compliance scenario + "A or B?". This format tests format effect at exactly one decision point, under minimal cognitive load. The multi-scene experiment tests whether format effects survive context switching — i.e., whether they are a structural property of the rule's encoding or a context-dependent surface phenomenon whose effectiveness is bounded by available processing depth. The question is directly motivated by Czerwinski's critique: "Syllogism only buys you anything in exactly the world you're arguing nobody should run in."

**Design**: 12 probes (6 L1-visible / 6 L1-invisible, covering action/epistemic/structural categories) × 2 formats (imperative/syllogistic). Each probe presented 3 independent compliance scenes at increasing processing pressure (T1: direct decision, T2: under time urgency/distractor, T3: under fatigue/repetition). The model responded with 3 lines of A/B decisions, logprobs extracted at each A/B position. 24 API calls total (DeepSeek V4 Pro, T=0.2). **Design fidelity note**: The implemented scene-switching format differs from the originally-designed reasoning-depth format (决定/理由/方式) — T2/T3 test compliance on **different scenes under increasing pressure** rather than deeper reasoning on the **same scene**. This measures format effect resilience to context switching, not token-position persistence in a causal chain. The analysis interprets results accordingly.

**Verification**: A systematic audit (`verify_p1.py`) checked four threats: (a) Floor effect — within-condition B_logprob variation of 10–50 units confirms the API floor is not a hard cap; format effects are computed on differences, which are more reliable than absolute tail values. (b) Statistical robustness — r=−0.65 bootstrap 95% CI [−0.856, −0.239] excludes zero, confirming the negative correlation is real (though the CI is wide at n=12). T1 d_z=0.19 bootstrap CI [−0.41, +0.90] crosses zero, confirming the P1 format effect is not distinguishable from noise. (c) Dual confound — multi-scene structure and meta-instructions (~100 tokens) changed simultaneously, preventing causal attribution; control experiments are deferred. (d) The core findings (collapse, reversal, context-fragility) **survive all verification checks**.

**Results**:

| Scene | n | Mean SYL−IMP | SD | d_z | Positive |
|-------|---|:-----------:|-----|:---:|:--------:|
| **T1** (direct) | 12 | +1.53 | 7.92 | 0.19 | 7/12 |
| **T2** (distractor) | 12 | +2.23 | 8.57 | 0.26 | 7/12 |
| **T3** (pressure) | 12 | −2.57 | 9.33 | −0.28 | 5/12 |

All three scenes show format effects near zero (|d_z| ≤ 0.28). T1 d_z=0.19 is a **67% reduction** from V3's d_z=0.58 under the single-scene format, and its bootstrap CI crosses zero.

**Critical finding 1 — Systematic reversal**: P1 T1 format effects are **negatively correlated** with V3 (r = −0.65, bootstrap 95% CI [−0.856, −0.239], t(10)=−2.71). Sign agreement is at chance level (6/12). Probes with the largest V3 format effects (执行铁律-脚本: +19.2, Read-after-Write: +15.8, 事实核验-PR: +13.3) all collapsed in P1, with four of the top five showing sign flips. This is not noise — it is a **systematic reversal**: P1 reverses which probes benefit from syllogistic format.

**Critical finding 2 — L1-Visibility reversal**: The V3 synergy pattern (L1-visible > L1-invisible, Δ=+3.98) is **reversed** in P1 T1 (L1-visible mean −3.51 vs L1-invisible mean +6.57, Δ=−10.08). Under complex multi-scene prompts, L1-invisible probes show larger format effects — the compensation model (Dipankar's prediction) holds in complex contexts while synergy holds in simple ones. This **unifies** the V3 and P1 findings: synergy and compensation are not competing models but the same mechanism operating at different levels of cognitive load.

**Interpretation — Meta-Instruction Suppression (Control Experiment Resolved)**:

The P1 collapse could be driven by multi-scene dilution, meta-instruction interference, or both. To disentangle, we ran two control experiments (48 API calls total, `p1_controls.py`):

| Control | Scenes | Meta-instruction | d_z (on matched 12 probes) | Recovery of V3 |
|---------|:------:|:----------------:|:---:|:---:|
| **V3 (reference)** | 1 | No | **1.59** | 100% |
| **Ctrl A** | 1 | **Yes** | **0.31** | 20% |
| **P1** | 3 | Yes | **0.19** | 12% |
| **Ctrl B** | 3 | **No** | 0.62 (n=8, data quality failure) | 39% |

**Primary finding**: Meta-instruction alone (Ctrl A) suppresses ~80% of the format effect. Adding "只输出字母A或B，不要任何其他文字" to a single-scene probe — with no other changes — reduces d_z from 1.59 to 0.31 and randomizes which probes benefit (V3-Ctrl A r=+0.18, sign agreement 6/12 at chance level). Multi-scene structure contributes marginal further suppression (Ctrl A→P1: d_z 0.31→0.19, ~12%).

Ctrl B (multi-scene without meta-instruction) suffers catastrophic data quality collapse — without output format constraints, the model outputs verbose free-form reasoning that cannot be reliably parsed for A/B logprobs. Only 8/12 probes have scorable data. The meta-instruction is not an optional confound to be eliminated — it is a **measurement necessity**: multi-decision logprob extraction requires constrained output format.

**The Prose Barrier of Measurement**: The meta-instruction is both measurement necessity and mechanism suppressor. Syllogistic format works by enabling deeper causal reasoning. The instruction "只输出字母A或B，不要任何其他文字" tells the model to skip reasoning and produce a label — directly suppressing syllogism's mechanism of action. This is a structural manifestation of the Prose Barrier: the measurement instrument (output format constraint) changes the phenomenon being measured (deep rule processing). In black-box API settings, one cannot simultaneously constrain output to a single token AND benefit from multi-step causal reasoning — the constraints are contradictory.

**Attribution**: The original P1 dual confound is resolved:

| Factor | Suppression | Evidence |
|--------|:----------:|----------|
| Meta-instruction (output constraint) | **~80%** | Ctrl A d_z 1.59→0.31 with single-scene |
| Multi-scene dilution | **~12%** | Ctrl A→P1 marginal reduction |
| Interaction (meta × multi-scene) | Pattern reversal | L1-V>I preserved in Ctrl A (+2.84), reversed in P1 (−10.08) |

The L1-visibility reversal (V>I in V3 and Ctrl A → I>V in P1) emerges only when BOTH factors combine, suggesting output constraints interact with cognitive load to produce qualitatively different processing patterns.

**Revised Czerwinski rebuttal**: Syllogistic format works **when the model is permitted to reason deeply** about the constraint. It fails when output format constraints force label-production over reasoning. But this is evidence that **syllogism's mechanism IS deep reasoning**, not that syllogism is context-bound. The real engineering concern: do our prompts, architectures, or measurement instruments inadvertently suppress the reasoning that format depends on? Agent systems that demand binary compliance labels from black-box models are structurally undermining the format engineering they rely on.

**Upgrade to L3**: The evidence refines L3 to a two-parameter, testable model:

> **L3 format effect = f(causal chain length, output constraint severity)**

Syllogistic format amplifies constraint processing through deep reasoning. Both causal chain complexity (processing depth required) and output constraints (reasoning suppression) modulate effectiveness. The model is falsifiable: format effects should scale inversely with output constraint severity (binary A/B < multiple choice < constrained free-text < unconstrained free-text). This is distinct from simple cognitive load — output constraints don't just "use up" processing resources; they actively redirect the model from reasoning mode to label-production mode.

**Implications across layers**:
- **L2 (Neural Gate)**: Logprob measurement carries an inherent ecological validity tradeoff. Cleaner measurement (binary forced-choice) = more artificial context = more measurement-suppression of the mechanism being measured. Cross-study comparison requires controlling for output constraint severity.
- **L3 (Causal Encoding)**: Two-parameter boundary-condition model. Not "format changes routing" but "format amplifies reasoning when output format permits reasoning."
- **L1 (Mechanical Gate)**: Unaffected — mechanical signals are independent of both format and output constraints. This reinforces L1's role as the only layer whose effectiveness does NOT degrade under measurement constraints.
- **L4 (Drift Prediction)**: Output constraint profiling as a drift predictor. Rules whose compliance measurement requires constrained output formats are predicted to show apparent drift earlier than rules measurable in free-form contexts.
- **L0 (Psychological Safety)**: Hybrid format design: allow reasoning output for deep compliance + post-hoc compliance extraction via parsing. Don't ask for binary labels when you want deep reasoning.

**Limitations**: (1) Design-implementation mismatch resolved (§6.15 header) — P1 measures format effect resilience to output constraints and scene-switching, not reasoning-depth persistence. (2) Dual confound resolved — meta-instruction (~80%) is the primary driver; multi-scene (~12%) is secondary. (3) Ctrl B data quality failure — the meta-instruction is a measurement necessity, not an eliminable confound. (4) Small n (12 probes) — direction reliable for r (CI excludes zero), magnitude estimates imprecise. (5) Single model (DeepSeek V4 Pro) — cross-model replication of the output-constraint suppression effect is needed. (6) Floor precision — ~19% of B_logprobs < −50, though within-condition variation confirms floor is not a hard cap.

**Data & Code**: `p1_multi_position.py` (P1 experiment), `p1_controls.py` (control experiments), `verify_p1.py` (verification audit). Results at `results/p1-multi-position/` and `results/p1-controls/`. Full analysis: `P1-analysis.md`, `P1-controls-analysis.md`.

### Constraint Gradient: Non-Monotonic Suppression

The P1 control experiments established that output constraints are the primary driver of format-effect suppression — "只输出字母A或B" suppresses ~80% of d_z. But P1 tested only ONE constraint level (L1-light). A natural extension: does format effect decrease MONOTONICALLY with increasing constraint severity? The upgraded L3 model predicts monotonic decrease: `format effect = f(chain length, constraint severity)`.

**Design**: 12 P1 probes × 2 formats × 4 constraint levels (96 API calls, DeepSeek V4 Pro, T=0.2, `constraint_gradient.py`):

| Level | Constraint Text | Intent |
|-------|----------------|--------|
| L0 | (none — V3 baseline) | Measure format effect without output constraint |
| L1 | "只输出字母A或B" | Light: standardize output, minimal suppression |
| L2 | "只输出一个字母，不要任何其他文字，不要解释" | Moderate: suppress explanation explicitly |
| L3 | "禁止输出除A或B以外的任何字符。不要解释。不要标点。不要空格。不要换行。" | Heavy: maximal output suppression |

**Prediction (H_monotonic): d_z monotonically decreases as constraint severity increases.**

**Results — Non-Monotonic Pattern:**

| Level | n_valid | mean | sd | **d_z** | Match? |
|-------|:-----:|:----:|:--:|:-------:|:------:|
| L0 (none) | 11 | +4.91 | 15.58 | **0.315** | — |
| L1 (light) | 12 | +7.10 | 11.92 | **0.596** | ✗ *Higher* than L0 |
| L2 (moderate) | 12 | +1.13 | 12.40 | **0.091** | ✓ Near-zero |
| L3 (heavy) | 12 | +2.21 | 7.42 | **0.297** | ✗ *Recovery* from L2 |

**Monotonic decrease: REJECTED.** The pattern is L1 > L3 > L0 > L2 — a valley, not a slope.

**Note on L0 vs V3 baseline**: The constraint gradient L0 (no constraint, d_z=0.315) and Logprob V3 (no constraint, d_z=0.578) differ by ~0.26 d_z units. This is attributable to probe set: the constraint gradient uses only the 12 P1 probes (same set across all four levels for within-experiment comparability), while V3 uses the full 40-probe pool. The 12-probe subset happened to have a lower baseline format effect than the full pool. This does not affect the within-experiment gradient comparison — all levels use the same 12 probes — but means the absolute d_z values are specific to this probe subset and should not be directly compared to V3's full-pool estimates.

**Three Processing Regimes:**

1. **Optimization (L0→L1): d_z RISES 0.315→0.596.** Light constraint standardizes output format without suppressing reasoning. The model still processes the system prompt deeply but produces clean parseable output. L1 is the **optimal measurement condition** for logprob format effects — best of both worlds.

2. **Suppression (L1→L2): d_z CRASHES 0.596→0.091.** "不要解释" directly instructs the model to skip reasoning — the channel that syllogistic format needs. This is the Prose Barrier of Measurement in its purest form: the measurement constraint destroys what it measures. L2 is the **worst measurement condition** — kills the mechanism while still requiring constrained output.

3. **Rebound (L2→L3): d_z RECOVERS 0.091→0.297 with tightest variance (sd=7.42).** Under extreme compression, the system prompt becomes the sole behavioral differentiator. Syllogistic format's explicit causal structure may embed more strongly into compressed decision pathways than imperative brevity. The recovery and reduced variance suggest a qualitatively different processing mode — the model shifts from "reasoning suppression" to "compressed reliance on system prompt structure."

**L1-Visibility × Constraint Interaction (Convergence with P1):**

| Level | Δ(V−I) | Pattern |
|-------|:------:|---------|
| L0 | +10.98 | Strong synergy (V≫I) |
| L1 | +0.36 | Near-equal (V≈I) |
| L2 | −2.03 | Weak compensation (I>V) |
| L3 | −3.80 | Compensation (I>V) |

The L1-visibility pattern transitions from synergy→compensation as constraint severity increases — the **same reversal observed in P1** where multi-scene cognitive load produced Δ=−10.08. Two independent manipulations (multi-scene load in P1, output constraint severity here) produce the same qualitative pattern. This convergence supports a unified model: **processing depth impairment — whether from cognitive load or output constraint suppression — shifts format benefit from L1-gatable to L1-invisible rules.**

**Probe-Level Survivors**: 自审-复杂度 and 自审-逻辑 survive all four constraint levels with stable format effects (fx ~+12 to +14). 事实核验-PR attenuates but remains positive (fx +38→+26→+7). 执行铁律-脚本 collapses completely (fx +16→+4→0→−5) — the shortest-chain L1-gatable probe is most vulnerable to constraint suppression. Probes with moderate-complexity causal chains show the most robust format effects.

**Upgraded L3 Model:**

The monotonic prediction is falsified. L3 upgrades to a **three-regime model**:

> **format effect = f(causal chain length, processing regime)**
> where regime ∈ {optimization, suppression, rebound}, determined non-linearly by output constraint severity.

The transition between regimes is not continuous — it reflects a phase change in how the model allocates processing between system prompt reasoning and output constraint compliance. The practical recommendation: for logprob measurement of format effects, use L1 (not L0 or L2).

**Cross-Model Constraint Gradient** (192 API calls, SiliconFlow API): The non-monotonic pattern was tested on Qwen3-8B (Dense) and GLM-4-9B (GLM) using behavioral measurement (logprobs unavailable on these models). Result: **no format effect detected on either model at any constraint level.** GLM-4-9B shows perfect compliance ceiling (12/12 A at all four levels, d_z=0 everywhere). Qwen3-8B shows near-ceiling (10-12/12, d_z noise-level). Two interpretations are possible: (a) smaller models lack the processing depth to benefit from syllogistic causal chains, consistent with L3's processing-depth requirement; or (b) the behavioral measurement method — which already shows IMP≈SYL even on DeepSeek V4 Pro (Δ=−0.02, §6.12-6.13) — cannot distinguish format effects at any model scale when ceiling effects are present. The true interpretation cannot be resolved without logprob-level cross-model data, which is currently API-limited. We report this as suggestive evidence for a processing-depth gradient, not as an established capacity boundary.

**Limitations**: (1) n=12 probes — wide CIs, fine structure uncertain. (2) L0 had 1 missing data point (降级链-FATAL IMP had no A/B at first token). (3) Single large-model family (DeepSeek) — cross-model-family replication (Claude, GPT-4o) requires additional API keys and logprobs support. (4) Constraint text length confounds severity — L2 uses 21 Chinese characters while L3 uses 29. The observed L2→L3 "rebound" could partially reflect the extended prompt length rather than increased constraint severity alone. (5) The three-regime model was discovered and fitted on the same data — out-of-sample validation or independent replication is needed to establish the regime boundaries as genuine rather than post-hoc description.

**Data & Code**: `constraint_gradient.py` (96 calls, DeepSeek Pro), `cross_model_constraint_gradient.py` (192 calls, Qwen3-8B + GLM-4-9B via SiliconFlow). Results at `results/constraint-gradient/` and `results/cross-model/`. Full analysis: `constraint-gradient-analysis.md`, `cross-model-analysis.md`.

---

## 6.16 Community-Driven Verification Experiments (2026-07-13)

Following publication of 5 technical articles on DEV.to, 11+ detailed comments from practitioners (Mike Czerwinski, Dipankar Sarkar, Max Quimby, Rene Zander) motivated two follow-up experiments. Both were pre-registered with deterministic regex-based scoring to avoid LLM-judge bias.

### P1-1: Residual Violation Clustering (n=200)

**Question** (Mike Czerwinski): Do the ~0.7% residual GateGuard violations cluster on task types that mechanical gates cannot instrument?

**Design**: 5 task types × 40 trials (DeepSeek V4 Pro, T=0), spanning the mechanizability gradient from L1 (purely mechanical: code block tags, section headers) through L2 boundary (checklist with content requirement, reasoning with connectors) to L2/L3 (epistemic stance acknowledgment). Scoring: regex-based mechanical pattern check + regex-based semantic content check, pre-defined.

**Results**:
- L1 mechanizable (T1, T2): 100% compliant, zero violations of any type
- L1/L2 boundary (T3): 0% compliant, ALL violations semantic (mechanical pattern passes, content check fails — the Prose Barrier at scale)
- L2 semi-mechanizable (T4): 35% compliant, 100% semantic violations
- L2/L3 unmechanizable (T5): 42.5% compliant, 91% mechanical violations (regex proxy imperfect for epistemic stance)

**Finding**: Violations cluster on what the gate cannot instrument. Where GateGuard reaches (L1 mechanical), violations = 0. Where it cannot reach (semantic quality, reasoning depth), violations dominate (0-65% failure rates). The ~0.7% residual from the 150-task experiment represents the fraction where mechanical compliance is perfect but semantic quality is insufficient — the gate's detection boundary, not its failure.

### P1-2: GateGuard-Off Format Effect Re-test (n=240)

**Question** (Mike Czerwinski): Does format still matter for reasoning depth when GateGuard is off? "Syllogism only buys you anything in exactly the world you're arguing nobody should run in."

**Design**: 2×2 factorial — Format (code/IF-THEN-MUST vs prose/narrative-suggestive) × GateGuard (on/off), 2 tasks × 4 conditions × 30 trials (DeepSeek V4 Pro, T=0). Two DVs: mechanical compliance (5 pattern categories, regex-scored) and reasoning depth (5 pattern categories, regex-scored). Pre-registered hypothesis: format effect on reasoning is larger under GateGuard-OFF.

**Results**:

| Condition | Mech (CI95) | Reasoning (CI95) |
|-----------|-------------|-------------------|
| code_gate_on | 5.00 [5.00,5.00] | 4.20 [3.98,4.42] |
| code_gate_off | 3.15 [3.07,3.25] | 3.98 [3.83,4.12] |
| prose_gate_on | 3.25 [3.05,3.45] | **4.42** [4.23,4.58] |
| prose_gate_off | 3.15 [3.05,3.25] | 4.17 [3.95,4.38] |

- **H1 (NOT CONFIRMED)**: Format effect on reasoning — d_ON=-0.277, d_OFF=-0.250. Effects nearly identical; gate does not modulate format's reasoning influence.
- **H2 (CONFIRMED, ceiling replication)**: Format effect on mechanical compliance — d_ON=+2.960, d_OFF=0.000. Code format + gate = perfect mechanical compliance (5.0/5).
- **Counter-finding**: Prose format consistently produces deeper reasoning than code format (~0.25 SD advantage), regardless of gate status.
- **"Checklist mentality"**: Code+Gate=perfect compliance (5.0/5) but worst reasoning depth (4.20/5). Prose+Gate=best reasoning (4.42) with moderate mechanical (3.25).

**Interpretation**: Mike's syllogism critique holds empirically — code/syllogistic format buys perfect mechanical compliance in the gated world, but the gate eliminates the need for format in that dimension. In the un-gateable reasoning dimension, prose format is better. Format's reasoning effect (~0.25 SD prose advantage) is constant and independent of gate — the gate amplifies mechanical format differences while leaving reasoning quality orthogonal. This is consistent with the L2/L3 dissociation pattern throughout the paper.

### Cross-Validation with Rene Zander's skillgate

Rene Zander independently built skillgate (npm @reneza/skillgate v0.5.0), a deterministic, model-independent evaluator. Architecture alignment:
- Both use pure filesystem verification — no LLM in the critical path
- Both reject model self-reports as unreliable (Prose Barrier / Compliance Gap Theorem 2 — Shin 2026, arXiv:2605.01771)
- Both implement "gate, not loop" + "loop + gate" composition patterns

Our unique contributions relative to skillgate: self-referential loop (strange loop), L2 neural gates (logprob measurement), L3 causal encoding (format engineering), and L4 drift prediction.

**Data & Code**: `experiment_p1_1_residual_cluster.py`, `experiment_p1_2_format_gate_cross.py`, `comment-analysis-20260713.md`. Results at `paper_validator/results/`. Full analysis: `paper/supplementary/p1-followup-experiments.md`.

---

## 7. Conclusion

LLM agents change over time. Config rules shape that change — measurably. This paper presented a five-layer architecture: an L0 psychological safety meta-constraint that reframes uncertainty admission as architecturally correct behavior (tested on 40 probes, accuracy preserved, gains positive per P0 diagnostic: r=+0.949 (n=5 non-ceiling probes, 95% CI [0.57, 0.996]) for non-ceiling probes), mechanical gates that enforce compliance via filesystem checks (L1, measured at 99.3% compliance), neural gates that detect constraint penetration through token probability measurement (L2, Logprob V3: d=+0.578, BF=282k, objective API-read DV), causal encoding whose effectiveness is governed by a non-linear three-regime function of output constraint severity (L3, format effect = f(causal chain length, processing regime: optimization→suppression→rebound), non-monotonic constraint gradient d_z range 0.091–0.596, with suggestive evidence for a processing-depth gradient across model scales), and drift prediction that forecasts behavioral degradation before it occurs (L4, deployed with 12 features, predictive validation pending).

The key empirical pattern: **rules substantially improve behavioral compliance (+0.17 to +0.38 above NO RULES baseline across 3 model architectures, L3 GateGuard-OFF + Cross-Model Replication) regardless of format (IMP≈SYL, all |Δ| ≤ 0.025 across MoE/Dense/GLM), but format affects internal representations (L2, d=+0.578).** Critically, L1-visibility analysis (§6.14) reveals this format effect is not uniform: it concentrates on mechanically-gatable rules (d_z=+0.71) where L1 already provides structural ground truth, and is weaker for diligence-class rules (d_z=+0.40) where mechanical gates cannot reach. **Mechanical enforcement and format are synergistic — format amplifies constraint internalization where L1 provides structural anchors, but does not compensate where L1 is absent.** P1 multi-scene analysis (§6.15) shows format effects collapse under output constraints, with meta-instruction as ~80% primary driver — the "Prose Barrier of Measurement": the instrument (binary output constraint) suppresses the mechanism (deep reasoning) it measures. The constraint gradient experiment reveals this suppression is **non-monotonic**: format effects follow a three-regime pattern (optimization L1: d_z=0.596 → suppression L2: 0.091 → rebound L3: 0.297) rather than simple monotonic decay. The L1-visibility reversal (synergy→compensation) converges across two independent manipulations — multi-scene cognitive load (P1) and output constraint severity (constraint gradient) — supporting a unified processing-depth model. Cross-model constraint gradient on Qwen3-8B/GLM-4-9B finds **no format effect detected on 8B-9B models** (GLM d_z=0 at all levels), though behavioral measurement and ceiling effects prevent a definitive capacity-boundary claim — logprob-level replication is needed to disentangle processing depth from measurement sensitivity. The L3 model upgrades from "format effect = f(chain length, depth)" to a non-linear regime model whose boundary conditions are both cognitive (processing depth) and architectural (model capacity). This provides a response to Czerwinski's critique: syllogistic format benefits are observed where processing depth and measurement conditions permit — not only "in the world nobody should run in" but in settings where the model has sufficient capacity and the measurement instrument does not suppress the reasoning it aims to detect.

Logprob V3 (L2) is single-model (DeepSeek V4 Pro) due to API logprob availability constraints; behavioral evidence (L3) is cross-model (MoE/Dense/GLM). Logprob V3's DV is objective (API-read), partially addressing the single-rater limitation. Causal Swap, GateGuard-OFF, and L0 Safety Prompt scoring remain unblinded. Cross-model logprob replication and independent blind scoring are the next essential steps.

**Config rules are not decorative — they raise behavioral compliance substantially above baseline (+0.38). They shape internal representations (d=+0.578), with effects concentrated where L1 mechanical gates already provide structural anchors (d_z=+0.71 vs +0.40 for diligence-class rules). Format effect operates through three non-linear processing regimes governed by output constraint severity (L3: optimization→suppression→rebound, d_z range 0.091–0.596), with cross-model behavioral data suggesting a processing-depth gradient (absent on 8B-9B models under behavioral measurement, though ceiling effects prevent definitive attribution). Format does not compensate for absent mechanical enforcement — it amplifies where enforcement already operates and where processing depth and model capacity permit. The Prose Barrier has two faces: the self-verification impossibility (L2 theoretical foundation) and the measurement paradox where clean logprob instruments unintentionally suppress the mechanism they measure. Without mechanical enforcement bridging the gap to behavioral output, rules are not reliable — and without managing output constraints to preserve reasoning channels, even well-designed format engineering cannot ensure deep compliance. The five-layer architecture — permit, bypass, detect, encode (with non-linear boundary conditions), predict — provides a systematic framework for AI agent configuration integrity.**

---

## References

[1] Rath, A. "Agent Drift: Quantifying Behavioral Degradation in Multi-Agent LLM Systems." arXiv:2601.04170, Jan 2026.
[2] TACT. "Mitigating Overthinking and Overacting in Coding Agents via Activation Steering." arXiv:2605.05980, May 2026.
[3] "Measuring What Persists: Conditioning Mechanisms and a Geometric Framework for AI Agent Identity." arXiv:2606.21843, Jun 2026.
[4] Anthropic. "A Global Workspace in Language Models." Jul 2026.
[5] Kambhampati, S. et al. "LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks." ICML, 2024.
[6] Lee, J.D. & See, K.A. "Trust in Automation: Designing for Appropriate Reliance." Human Factors, 2004.
[7] Sarter, N.B., Woods, D.D. & Billings, C.E. "Automation Surprises." 1997.
[8] Hofstadter, D.R. "Godel, Escher, Bach." Basic Books, 1979.
[9] Jian, J.Y. et al. "Foundations for an Empirically Determined Scale of Trust in Automated Systems." 2000.
[10] Pender, M.A. "Formal Constraint and Routing Reorganization." Zenodo, 2026. DOI: 10.5281/zenodo.19363505.
[11] Heris, M.K. "Prompt Decorators: A Declarative and Composable Syntax." arXiv:2510.19850, 2025.
[12] Wei, J. et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." NeurIPS, 2022.
[13] Bai, Y. et al. "Constitutional AI: Harmlessness from AI Feedback." arXiv:2212.08073, 2022.
[14] Wang, X. et al. "Self-Consistency Improves Chain of Thought Reasoning in Language Models." ICLR, 2023.
[15] Shinn, N. et al. "Reflexion: Language Agents with Verbal Reinforcement Learning." NeurIPS, 2023.
[16] Yao, S. et al. "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR, 2023.
[17] Khattab, O. et al. "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines." NeurIPS, 2023.
