# Agent Identity Drift: Preliminary Evidence That Config Rules Shape LLM Agent Behavior

**Authors**: Yuhao Lin (FAFU)
**Status**: Pre-print, July 2026
**Primary category**: cs.SE | **Cross-list**: cs.CL
**Repository**: https://github.com/YuhaoLin2005/hermes-workspace

---

## Abstract

LLM-based coding agents degrade over extended use. We present a three-part investigation spanning mechanical defense, causal evidence, and format-driven routing: (1) a mechanized identity-persistence pipeline (3/4 steps deterministic) whose compact self-model serves as a file-system-level workspace; (2) a causal swap experiment (n=30, DeepSeek V4 Pro) — WITH rule 73% vs WITHOUT 20%, odds ratio 11.0, Fisher exact p=0.0092; and (3) the discovery that encoding behavioral rules as syllogistic causal structures rather than imperative commands produces measurably different agent behavior — 5/5 rules triggered across 4 blind cross-validation sessions with zero violations and emergent proactive auditing. This third finding converges with independent mechanistic evidence (Pender 2026) that logical prompts induce distinct attention routing regimes. We propose **causal structure encoding** as a candidate approach: preliminary evidence suggests the format of a behavioral constraint may influence which internal processing pathway it activates. Three complementary layers — mechanical gates (filesystem checks), neural gates (constraint echo), and causal encoding (format → routing) — cover the full information pipeline, pending controlled validation.

---

## 1. Introduction: 50 Sessions of Watching an Agent Drift

Over approximately 50 coding sessions with DeepSeek V4 Pro inside Claude Code, I observed a recurring pattern: the agent would start each session coherent, but after extended interaction, it would forget negotiated conventions, relax quality-review enforcement, and drift from its configured identity. In 15 of those 50 sessions (~30%), a specific protocol was forgotten by the session midpoint. In 8 sessions, the agent re-litigated a decision settled in a previous growth-log entry.

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

We interpret this not as homology (shared ancestry) but as **convergent evolution at the functional level**: systems that route information through compact, causally-efficacious intermediate representations — whether emergent or engineered — exhibit measurably better behavioral control. The shared functional constraint (bounded bottleneck × causal placement) produces analogous solutions at different substrate layers (neural activations vs. file-system configurations). This suggests a design principle rather than a specific implementation: **separate identity from mechanism, make the identity representation compact, and place it on the causal path.** J-space is one implementation inside a neural network. Our self-model is one implementation outside [4].

**Trust in Automation.** Lee & See (2004) established that human trust depends on appropriate calibration between perceived and actual system capability [6]. Agent identity drift directly undermines this calibration. Sarter, Woods & Billings (1997) named this "automation surprise" — the gap between expected and actual system behavior [7]. Our pipeline addresses this mechanically rather than through human vigilance.

---

## 3. System Design

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

## 7. Conclusion

LLM agents change over time. Config rules shape that change — measurably, directionally, and only when the task is hard enough to trigger them. n=30: 73% vs. 20%, 95% CI [17.7pp, 73.7pp], p=0.0092. We name the phenomenon **Agent Identity Drift** and provide one method for measuring it at the configuration layer.

**Config rules are not decorative.**

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

---

## 6. Causal Structure Encoding — How Rule Format Changes Attention Routing

### 6.1 The Format Hypothesis

Parts 1-2 established that config rules causally shape behavior and that mechanical gates can detect drift. Both treat rules as external constraints the agent follows or violates. Neither changes how the agent **processes** rules internally.

This section investigates: **does the linguistic form of a behavioral rule change how a transformer processes it?**

We present evidence that encoding the same constraint in **syllogistic causal form** (major premise → minor premise → conclusion) versus **imperative command form** produces measurably different agent behavior. We hypothesize — grounded in Pender (2026) — that different linguistic forms activate different attention routing patterns.

### 6.2 Conversion: Imperative → Syllogistic

Over ~50 sessions, imperative-form rules were violated in ~30% of complex sessions. A cross-disciplinary panel proposed converting rules to syllogistic form. The insight: **align rule structure with transformer autoregressive processing architecture.**

**Example:** "Any decision >30 days must use dual-pool review" → "Major premise: single-perspective review has structural blind spots (Prose Barrier). I must judge: does this span >30 days? If yes: blind spots necessarily exist. Independent views must be introduced — not because a rule demands it, but because blind spot structure demands it."

Five rules were converted: dual-pool enforcement, Read-after-Write verification, pre-action three-question calibration, automatic learning capture, and adversarial self-audit.

### 6.3 Behavioral Results (n=4 blind cross-validation sessions)

| Rule | Triggers | Violations | Emergent Behaviors |
|------|:--:|:--:|------|
| Dual-pool | 4/4 | 0 | Auto expert assembly, cross-validation matrix |
| Read-after-Write | 4/4 | 0 | Unprompted post-edit verification |
| Three-question | 4/4 | 0 | Structured pre-action reasoning |
| Learning capture | 4/4 | 0 | Structured change summary tables |
| Self-audit | 4/4 | 0 | Proactive config inconsistency detection |

**Emergent (uninstructed) behaviors**: discovered configuration double-definition bug, found cross-file threshold inconsistency, identified 7 imprecise phrasings and proposed corrections, caught formatting error, correctly distinguished completed vs. planned experiments when asked to mark all as done.

**Baseline**: imperative-form sessions showed ~30% rule violation rate with zero instances of proactive configuration auditing.

### 6.4 Mechanism: Attention Routing Hypothesis

Under imperative form: preceding text = "Command exists." Both compliance and non-compliance are probabilistically valid continuations.

Under syllogistic form: preceding text = **causal chain** (Y→X, Y true, therefore X). Next-token distribution is **structurally constrained** — violating X contradicts the established chain.

Pender (2026, Zenodo) independently demonstrated that logical/relational prompts induce a **distinct, higher-curvature internal routing regime** in transformer attention graphs, with cross-model validation (GPT-2, Qwen 0.5B). Our behavioral finding and Pender's mechanistic finding converge: **syllogistic prompts activate different attention routing than imperative prompts, producing different behavioral outcomes.**

### 6.5 Three-Layer Architecture

```
Layer 1 (Part 1): Mechanical Gate — "Did information arrive?"
  Filesystem checks (mtime, exit codes, hook wiring). Bypasses Prose Barrier.
Layer 2 (Part 2): Neural Gate — "Did information leave traces?"
  Constraint echo detection (keyphrase presence in output). Works within Barrier.
Layer 3 (Part 3): Causal Encoding — "Does format determine pathway?"
  Format changes attention routing topology within Barrier.
```

Three layers, one information pipeline: **arrival → penetration → routing.** None replaces the others.

### 6.6 Related Work on Format Effects

Pender (2026) provided the mechanistic evidence linking prompt format to attention routing. Heris (2025) proposed Prompt Decorators — declarative tags for LLM control — but tags remain external commands. SemEval-2026 systems achieved 100.0 on syllogistic reasoning via neuro-symbolic approaches, but these delegate logic externally rather than embedding it in prompt structure. "The Magic of IF" showed code-LLMs outperform on causal reasoning with conditional structures — directly supporting our finding that structure matters more than format. Constitutional AI (Bai 2022) operates at training time; we operate at prompt time.

**Our distinct contribution**: engineering the format→routing→behavior causal chain for agent configuration, grounded in both behavioral evidence and independent mechanistic research.

### 6.7 Limitations and Future Work

**Current limitations**: n=4 sessions (preliminary), single model (DeepSeek V4 Pro), within-subject design, no direct attention measurement (Pender citation only), rule selection bias (high-violation-rate rules chosen), Hawthorne effect.

**Required follow-up**: cross-model replication (Claude, GPT-4), larger-n between-subject A/B test (n≥20), direct attention routing analysis via causal mediation (needs local model access), 30-turn degradation resistance test, controlled imperative baseline comparison.

### 6.8 Conclusion

We present pilot evidence (n=4 sessions, single model, no control condition) for **causal structure encoding** as a candidate approach in agent configuration design. Mechanical gates detect violations. Neural gates measure constraint penetration. Causal encoding — if validated at larger scale with proper controls — may change internal processing by aligning rule structure with transformer architecture, making rule-consistent behavior the highest-probability continuation.

Our preliminary behavioral results converge with Pender's (2026) independent mechanistic finding that logical prompts induce distinct attention routing regimes. Whether this convergence reflects a causal mechanism or surface-level correlation remains to be tested. Controlled experiments with imperative baselines, larger n, and cross-model replication are needed before drawing strong conclusions.

[10] Pender, M. A. (2026). Formal Constraint and Routing Reorganization: A Constrained-Transport View of Transformer Attention. Zenodo. DOI: 10.5281/zenodo.19363505
[11] Heris, M. K. (2025). Prompt Decorators: A Declarative and Composable Syntax. arXiv:2510.19850

---
*Code, data, transcripts: https://github.com/YuhaoLin2005/hermes-workspace*
