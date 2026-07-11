# Agent Identity Drift: Preliminary Evidence That Config Rules Shape LLM Agent Behavior

**Authors**: Yuhao Lin (FAFU)
**Status**: Pre-print, July 2026
**Primary category**: cs.SE | **Cross-list**: cs.CL
**Repository**: https://github.com/YuhaoLin2005/hermes-workspace

---

## Abstract

LLM-based coding agents degrade over extended use. This paper investigates whether the configuration rules surrounding an agent — its system prompts, behavioral protocols, and self-model — measurably shape its behavior, or are merely decorative text consuming context tokens. We present a three-part investigation: (1) a mechanized identity-persistence pipeline (3/4 steps deterministic) that detects configuration staleness via filesystem checks and triggers self-model regeneration, deployed across 50+ coding sessions; (2) a between-subjects manipulation (n=30, DeepSeek V4 Pro, single-rater unblinded — explicitly noted) in which removing a behavioral rule reduced alternative-seeking behavior from 73% to 20% (risk difference 53pp, OR=11.0, p=0.0092), providing preliminary evidence that config rules causally shape agent behavior; and (3) a controlled A/B experiment (n=150 tasks, 6 sessions) comparing syllogistic-causal vs. imperative rule formats, which found that mechanical enforcement — not rule format — dominates compliance rate (99.3% with hooks active), while format systematically affected reasoning depth in un-gated design tasks. We propose a three-layer architecture for configuration integrity: mechanical gates (filesystem checks, bypassing AI self-assessment), neural gates (constraint echo detection within the generation process), and causal encoding (format → attention routing). All experimental results are scored by the first author (unblinded); independent blind verification is pending. The core contribution is architectural: a demonstration that mechanical verification at the configuration layer can serve as an independent integrity check that does not rely on the agent's compromised self-assessment capability.

---

## Experiment Overview

| Experiment | N | Design | Main Finding | Status |
|------|:--:|------|------|:--:|
| Growth-log Retrospective (§6.2) | 34 sessions | Longitudinal coding, single coder | 55.9%→0.7% violation rate with mechanical gate | ✅ Complete |
| Causal Swap (§4) | 30 tasks | Between-subjects (15+15), DeepSeek V4 Pro | WITH rule 73% vs WITHOUT 20%, OR=11.0, p=0.0092 | ⚠️ Single-rater, unblinded |
| Format A/B (§6.5) | 150 tasks | Between-subjects (75+75), 6 sessions, DeepSeek V4 Pro | Ceiling effect (99.3% compliance); format affects reasoning depth, not compliance | ⚠️ Needs GateGuard-OFF replication |
| Syllogism Blind CV (§6.4) | 4 sessions | 5/5 rules triggered, zero violations + emergent auditing | Preliminary format→reasoning causal chain evidence | ⚠️ Small n, uncontrolled |

> **n-count reconciliation**: Five numbers appear across the repository — 30 (Causal Swap tasks), 34 (growth-log sessions), 38 (cumulative trials in paper-trial-results.md = 30 original + 8 new), 60 (future target sample size), 150 (Format A/B tasks). Each corresponds to a different experiment; they are not conflicting reports of the same data.

---

## Reader's Guide

This paper reports a three-part investigation developed iteratively over 50+ coding sessions. The reader may find it helpful to understand the structure before diving in:

- **Part 1 — Mechanical Gate (§3):** System architecture. A self-model regeneration pipeline with filesystem-level verification. *Note: Part 1 describes the system but does not include a direct A/B experiment of the gate itself; gate effectiveness is demonstrated in Part 3's experiment (§6.5).*
- **Part 2 — Causal Swap (§4):** A between-subjects manipulation (n=30) testing whether removing a config rule changes behavior. The paper's methodologically strongest evidence, with the caveats of single-rater unblinded scoring and non-randomized assignment.
- **Part 3 — Causal Structure Encoding (§6):** The longest section, built on the weakest evidence. Includes a retrospective baseline (§6.2, n=34 sessions, single coder), a small-N syllogism pilot (§6.4, n=4, uncontrolled), and a controlled A/B experiment (§6.5, n=150 tasks) whose primary outcome was confounded by active mechanical hooks. *The A/B experiment validates Layer 1 (mechanical gate effectiveness), not Layer 3 (format effects on compliance).*

**Reading paths**: For a quick scan, read the Experiment Overview table above, then §4 (Causal Swap), then §6.10 (Conclusion). For a full read, follow section order. **Important**: §5 (Discussion) appears before §6 because it primarily discusses the Causal Swap experiment (§4); §6 was developed later in the research timeline and its discussion is integrated within the section itself.

All experimental results are scored by the first author (unblinded, no independent raters). Cohen's κ from the one attempted blind check was -0.14 (§5.2). The quantitative results should be interpreted as preliminary evidence requiring independent verification. See §5.1 and §6.9 for comprehensive limitations.

---

## 1. Introduction: 50 Sessions of Watching an Agent Drift

Over approximately 50 coding sessions with DeepSeek V4 Pro inside Claude Code, I observed a recurring pattern: the agent would start each session coherent, but after extended interaction, it would forget negotiated conventions, relax quality-review enforcement, and drift from its configured identity. In 15 of those 50 sessions (~30%, informal observation), a specific protocol was forgotten by the session midpoint. Subsequent systematic retrospective coding of 34 growth-log sessions confirmed a higher violation rate of 55.9% (19/34; see §6.2), suggesting that informal observation underestimates true drift rates. In 8 sessions, the agent re-litigated a decision settled in a previous growth-log entry.

This auto-ethnographic observation is not systematic — the sessions were not formally coded (see Section 5: Limitations). But it forms the ecological ground for the experiment that follows: if config rules matter, removing one should measurably change behavior.

The phenomenon has been named but not yet measured at the identity layer. Rath (2026) introduced "agent drift" to describe behavioral degradation in multi-agent coordination [1]. TACT (2026) demonstrated activation-steering mitigation for drift in coding agents [2]. "Measuring What Persists" (2026) showed identity-relevant representations collapse at long context lengths [3]. Anthropic's J-space paper (2026) provided neuro-mechanistic evidence that compact self-representations causally shape downstream outputs [4]. Our work addresses a distinct question: **do the config rules that surround an LLM agent — its system prompts, behavioral protocols, and self-model — causally shape its behavior, or are they decorative text consuming context tokens?**

**Contributions:**
1. A mechanized identity-persistence pipeline — 3 of 4 operational steps are deterministic Python scripts
2. A causal swap experiment (n=30) testing config rule causality (OR=11.0, p=0.0092)
3. **Causal structure encoding** — evidence that syllogistic rule format produces measurably different agent behavior than imperative format, converging with independent attention routing research (Pender 2026)
4. A three-layer architecture (mechanical → neural → causal) covering the full config information pipeline

---

## 2. Related Work

**Agent Drift.** Rath (2026) formalized three sub-types (semantic, coordination, behavioral) in multi-agent LLM systems and proposed a 12-dimensional Agent Stability Index [1]. Our work addresses a distinct axis — identity/configuration drift in single-agent coding assistants — measured through self-model persistence rather than inter-agent coordination metrics.

**Mitigation Approaches.** TACT (2026) used activation steering at the neural level [2]. Our approach operates at the configuration layer — external scaffolding rather than internal weight modification. Complementary strategies at different AI stack layers.

**LLM-Modulo Frameworks.** Kambhampati et al. (2024) proposed wrapping LLMs with external verifier modules that catch errors and back-prompt regeneration [5]. Our pipeline instantiates this pattern with a critical distinction: our critic is a *data-freshness detector* (mtime comparison) rather than an *output-correctness verifier*. It signals "new observations exist," not "the output is wrong." This is both a limitation (cannot detect incorrect-but-recent content) and a strength (fully mechanizable, zero false positives on staleness).

**Identity Persistence and Convergent Evolution Across Abstraction Layers.** "Measuring What Persists" (2026) showed identity representations undergo geodesic collapse at long context [3]. Anthropic's J-space (July 2026) discovered a compact neural subspace (<10% activation variance, ~25 concepts) that emerged spontaneously during training — not designed, but discovered by gradient descent [4]. Five properties were demonstrated: verbal reportability, directed modulation, internal reasoning traces, flexible generalization across question types, and selectivity (removing J-space collapses reasoning but preserves fluency). DeepMind replicated the finding on Qwen 3.6 27B [4], confirming it is not Claude-specific.

Our self-model (~100 lines) and J-space share a functional pattern but differ fundamentally in mechanism. J-space is a learned representational bottleneck — vectors in activation space, operated on by linear algebra during the forward pass. Our self-model is an engineered routing table — a directed graph of markdown files concatenated into the context window before the forward pass. Both are compact, causally on the information path, and attended to by downstream processes. Both admit surgical modification (concept-swap in J-space, rule-deletion in self-model). Both were not designed top-down — J-space emerged from gradient descent; our architecture emerged from iterating on session failures.

We note this as a **functional analogy** rather than a formal equivalence: both systems route information through compact, causally-placed intermediate representations, and both exhibit measurable behavioral effects. This shared pattern — bounded bottleneck × causal placement — may reflect a more general design principle: **separate identity from mechanism, make the identity representation compact, and place it on the causal path.** However, the evidential gap between the two systems is substantial. J-space is a neural subspace validated through causal ablation, cross-model replication, and mechanistic theory (Jacobian lens). Our self-model is a markdown file concatenated into the context window, tested on one model with one rule by one unblinded rater. We present the analogy as a conceptual bridge — an observation that similar functional constraints may produce structurally similar solutions at different abstraction layers — not as a claim of equivalent mechanisms or equivalent evidentiary support.

**Self-Verification and Reliability.** Several lines of work address the challenge of LLM output reliability. Self-consistency (Wang et al., 2022) improves accuracy through multiple sampling and majority voting [14] — a complementary strategy that increases compute cost. Reflexion (Shinn et al., 2023) enables agents to self-correct using environmental feedback and episodic memory [15], demonstrating that external grounding can partially compensate for the self-assessment problem. ReAct (Yao et al., 2022) interleaves reasoning traces with tool-use actions [16], establishing the action-reasoning loop pattern that our mechanical gate monitors. DSPy (Khattab et al., 2023) provides programmatic prompt optimization [17] — configuration-layer engineering at scale — but targets task performance rather than persistent identity integrity. Our work differs from all of these in targeting **configuration drift over extended sessions** rather than single-task accuracy.

**Trust in Automation.** Lee & See (2004) established that human trust depends on appropriate calibration between perceived and actual system capability [6]. Agent identity drift directly undermines this calibration. Sarter, Woods & Billings (1997) named this "automation surprise" — the gap between expected and actual system behavior [7]. Our pipeline addresses this mechanically rather than through human vigilance.

---

## 3. System Design

### 3.0 The Prose Barrier: Why Mechanical Verification Is Necessary

A structural constraint makes AI self-verification unreliable: an LLM's generation pathway and its evaluation pathway share the same decoder distribution *P(token | context; θ)*. When an agent generates an output and then assesses whether that output complies with a behavioral rule, both the generation and the assessment are samples from the same distribution. There is no independent verification channel — the model cannot step outside its own decoder to obtain an uncorrelated judgment of its own output.

This constraint, which we term the **Prose Barrier**, implies that any verification mechanism that operates through natural language generation (prose) inherits the same biases and blind spots as the generation it is meant to verify. The implication for agent configuration is direct: an agent cannot reliably judge whether it is following its own configuration rules, because the judgment and the potential violation are produced by the same underlying process.

The Prose Barrier motivates the three-layer architecture below. Layer 1 (mechanical gates) bypasses the Barrier entirely by operating at the filesystem level. Layer 2 (neural gates) works within the Barrier by measuring traces of constraint penetration in the output distribution. Layer 3 (causal encoding) operates on the Barrier's input side by changing how rules are encoded before they enter the generation process.

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

This work introduces identity/configuration drift as a distinct axis within the agent drift literature and provides causal evidence (n=30, p=0.0092) that config rules measurably shape agent behavior. Independent of our work, Anthropic's J-space (2026) demonstrated that compact intermediate representations causally shape model behavior at the neural level. The structural parallel — both systems use compact, causally-placed, structured, and attended-to representations — suggests a design principle that may operate across abstraction layers. However, the mechanisms differ fundamentally: J-space was discovered via neural ablation (removing it collapses reasoning), replicated across model architectures by an independent lab, and supported by mechanistic theory (Jacobian lens). Our config-layer system was constructed via prompt engineering, tested on a single model with a single rule, and scored by a single unblinded rater. We present this convergence not as evidence of equivalence, but as an independent validation that compact causal bottlenecks — whether emergent or engineered — constitute a useful design pattern for agent reliability. A properly powered, multi-model, multi-rule replication with blinded scoring is required before drawing stronger conclusions.

### 5.5 Observed Pattern: The Causal Bottleneck

Four properties are associated with causally-efficacious intermediate representations in both the neural and config layers (observed, not proven necessary):

1. **Compactness** — J-space uses <10% of activations; self-model.md is ~100 lines. Small control surfaces are inspectable and modifiable.
2. **Causal placement** — Both sit on the information path between input and output (J-space: downstream layers read from it; self-model: concatenated into context before inference).
3. **Structure** — J-space has metric geometry (concepts as directions); self-model has explicit graph structure (files → sections → rules).
4. **Attended to** — J-space is causally efficacious because downstream layers actually read from it; self-model works because the LLM attends to context-window tokens.

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

### 6.7 Three-Layer Architecture

```
Layer 1 (Part 1): Mechanical Gate — "Did information arrive?"
  Filesystem checks (mtime, exit codes, hook wiring). Bypasses Prose Barrier.
  Status: ✅ Deployed and validated (150-task experiment, §6.5).
Layer 2 (Part 2): Neural Gate — "Did information leave traces?"
  v1 Constraint echo detection (keyword presence in output, 86 lines Python) — ✅ Deployed.
  v2 Logprob differential (compare token probabilities with/without constraint) — 📐 Designed, script written, needs API key.
  v3 Residual stream probes (train linear classifiers on Qwen2.5-1.5B) — 🗺️ Roadmap, needs local model access.
  All versions operate within the Prose Barrier; only v1 has been empirically tested.
Layer 3 (Part 3): Causal Encoding — "Does format determine pathway?"
  Format changes attention routing topology within Barrier.
  Status: ⚠️ Preliminary behavioral evidence (n=4 syllogism pilot, n=150 GateGuard-confounded A/B); direct attention measurement pending.
```

Three layers, one information pipeline: **arrival → penetration → routing.** None replaces the others. Layers 1 and 2 have working implementations; Layer 3 is a research hypothesis with preliminary behavioral support.

### 6.8 Related Work on Format Effects

Pender (2026) provided the mechanistic evidence linking prompt format to attention routing [10]. Heris (2025) proposed Prompt Decorators — declarative tags for LLM control [11] — but tags remain external commands; the current work tests whether format changes behavior when rules are embedded in the agent's operational context. Chain-of-Thought prompting (Wei et al., 2022) demonstrated that reasoning format substantially affects output quality [12], but CoT studies format as a task-solving scaffold rather than as a persistent behavioral constraint. Constitutional AI (Bai et al., 2022) operates at training time through RL from AI feedback [13]; we operate at prompt time through configuration files loaded at session start. Self-consistency (Wang et al., 2022) improves reliability through multiple sampling [14] — a complementary strategy that increases compute cost rather than restructuring the configuration layer.

**Our distinct contribution**: engineering the format→routing→behavior causal chain for agent configuration, grounded in behavioral evidence with independent mechanistic support from Pender (2026). The contribution is the application of format-effect findings to the under-studied problem of persistent agent configuration integrity, not the discovery of format effects themselves.

### 6.9 Limitations and Future Work

**Current limitations**: Single model (DeepSeek V4 Pro), GateGuard mechanical ceiling prevents isolation of pure format effects on compliance rate, self-scoring by agents (no independent rater), no direct attention measurement (Pender citation only), cross-session filesystem pollution, single rater for retrospective coding (κ pending). While n=6 sessions (150 tasks) provides reasonable behavioral coverage, the GateGuard confound means these results validate Layer 1 (mechanical gate effectiveness) rather than Layer 3 (causal encoding).

**Required follow-up**: GateGuard-disabled replication to isolate format effects, cross-model replication (Claude, GPT-4), direct attention routing analysis via causal mediation (needs local model), independent rater with Cohen's κ for all scoring.

### 6.10 Conclusion

We present controlled experimental evidence (n=6 sessions, 150 tasks, between-subjects) that **mechanical gates guarantee agent configuration compliance** regardless of rule format — 149/150 tasks (99.3%) showed zero violations when GateGuard hooks enforced pre-action checks. The single violation was self-detected through Honesty self-audit. This is direct evidence for Layer 1 (mechanical gate) effectiveness: when filesystem-level hooks block unverified operations, compliance approaches 100% irrespective of rule format. **The experiment was designed to test Layer 3 (format effects on behavior), but the GateGuard ceiling prevents isolating format effects on compliance rate.** The secondary finding — that format affects reasoning depth in un-gated tasks — is qualitative and unscored. A GateGuard-disabled replication with independent blind raters is required to test the format-effect hypothesis.

Retrospective baseline coding of 34 growth-log sessions under imperative format (pre-GateGuard era) documented violations in 55.9% of sessions, establishing that rules without mechanical enforcement are routinely violated. The contrast — 55.9% without GateGuard vs. 0.7% with GateGuard — quantifies the gap between purely textual rules and mechanically enforced ones.

Syllogism-form rules produced systematically deeper causal reasoning than imperative-form rules, particularly in open-ended design tasks where GateGuard did not intervene. Our behavioral findings converge with Pender's (2026) independent mechanistic evidence that logical prompts induce distinct attention routing regimes. GateGuard-disabled replication, cross-model validation, and independent blind scoring remain as future work.

---

*Code, data, transcripts: https://github.com/YuhaoLin2005/hermes-workspace*

---

## 7. Conclusion

LLM agents change over time. Config rules shape that change — measurably, though the current evidence is preliminary (single-rater, unblinded; independent verification pending). This paper presented a three-layer architecture: mechanical gates that enforce compliance via filesystem checks (Layer 1, validated: 55.9%→0.7% violation rate reduction, though the pre- and post-measures come from different populations), neural gates that detect constraint penetration (Layer 2, v1 keyword echo deployed; v2 logprob differential and v3 residual stream probes designed but not yet implemented), and causal encoding that changes how rules are processed internally (Layer 3, preliminary qualitative evidence of reasoning depth effects; direct attention measurement pending). The dominant experimental finding is that mechanical enforcement is the primary factor in agent compliance — it determines whether rules are followed; rule format appears to determine how deeply they are understood, though this finding requires GateGuard-disabled replication with independent blind raters to be conclusive.

**Config rules are not decorative. But without mechanical enforcement, they are not effective either. All quantitative results in this paper require independent blind verification before they can be considered reliable.**

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
