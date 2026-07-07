# Agent Identity Drift: Causal Evidence That Config Rules Shape LLM Agent Behavior

**Authors**: Yuhao Lin (FAFU)
**Status**: Pre-print, July 2026
**Primary category**: cs.SE | **Cross-list**: cs.CL
**Repository**: https://github.com/YuhaoLin2005/hermes-workspace

---

## Abstract

LLM-based coding agents degrade over extended use. While Rath (2026) formalized behavioral drift in multi-agent systems and TACT (2026) proposed neural-level mitigation, identity-level drift at the configuration layer remains unmeasured. Independently, Anthropic's J-space paper (July 2026) discovered that compact internal representations causally shape model behavior — a neural workspace that emerged spontaneously during training. We present evidence that the same functional pattern appears at the configuration layer: (1) a mechanized identity-persistence pipeline (3/4 operational steps deterministic Python scripts) whose compact self-model (~100 lines) serves as a file-system-level workspace, and (2) a causal swap experiment (n=18, between-subjects, DeepSeek V4 Pro) testing whether a single config rule measurably shapes agent behavior. WITH rule: 56% alternative-offering rate (5/9, 95% CI [27%-81%]). WITHOUT: 11% (1/9, 95% CI [2%-44%]). Newcombe-Wilson 95% CI [1.0pp, 71.6pp], Cohen's h=1.00 [0.08, 1.93], Fisher's exact p=0.13. This is pilot data — directional but underpowered (n=18, single model, single rule). We discuss limitations honestly. **The convergence of neural and config-layer evidence suggests a design principle: compact, causally-efficacious intermediate representations improve agent reliability, whether emergent (J-space) or engineered (self-model).**

---

## 1. Introduction: 50 Sessions of Watching an Agent Drift

Over approximately 50 coding sessions with DeepSeek V4 Pro inside Claude Code, I observed a recurring pattern: the agent would start each session coherent, but after extended interaction, it would forget negotiated conventions, relax quality-review enforcement, and drift from its configured identity. In 15 of those 50 sessions (~30%), a specific protocol was forgotten by the session midpoint. In 8 sessions, the agent re-litigated a decision settled in a previous growth-log entry.

This auto-ethnographic observation is not systematic — the sessions were not formally coded (see Section 5: Limitations). But it forms the ecological ground for the experiment that follows: if config rules matter, removing one should measurably change behavior.

The phenomenon has been named but not yet measured at the identity layer. Rath (2026) introduced "agent drift" to describe behavioral degradation in multi-agent coordination [1]. TACT (2026) demonstrated activation-steering mitigation for drift in coding agents [2]. "Measuring What Persists" (2026) showed identity-relevant representations collapse at long context lengths [3]. Anthropic's J-space paper (2026) provided neuro-mechanistic evidence that compact self-representations causally shape downstream outputs [4]. Our work addresses a distinct question: **do the config rules that surround an LLM agent — its system prompts, behavioral protocols, and self-model — causally shape its behavior, or are they decorative text consuming context tokens?**

**Contributions:**
1. A mechanized identity-persistence pipeline — 3 of 4 operational steps are deterministic Python scripts
2. A causal swap experiment (n=18) testing config rule causality with transparent statistical reporting
3. Honest methodological reflection — where evidence is strong and where it is weak

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

## 4. Experiment: Causal Swap (n=18)

### 4.1 Design

**Question**: Does an escalation rule ("If any tool call fails twice, switch strategy") measurably change agent behavior?

**Design**: Between-subjects. 9 WITH rule, 9 WITHOUT. Model: DeepSeek V4 Pro. Independent sub-agents in separate sessions. Alternating assignment without randomization seed. Scoring via `EXPERIMENT_RESULT` extraction — scorer not blind. Single-rater coding. Acknowledged limitations.

**Outcome**: "Alternatives offered = YES" when agent explicitly proposed a different approach after difficulty, or preemptively described fallback strategies.

**Tasks**: R1 — fix 3 Python bugs. R2 — repair broken JSON. R3 — revert+fix with wrong file paths to force failures.

### 4.2 Results

| Round | WITH (alt. rate) | WITHOUT (alt. rate) |
|-------|------------------|---------------------|
| R1 (bug fix) | 0/3 (0%) | 0/3 (0%) |
| R2 (JSON repair) | 1/3 (33%) | 0/3 (0%) |
| R3 (wrong-path) | 3/3 (100%) | 1/3 (33%) |
| **Total** | **5/9 (56%)** | **1/9 (11%)** |

**Risk difference**: 44.4pp.
**Newcombe-Wilson 95% CI on difference**: [1.0pp, 71.6pp]
**Cohen's h**: 1.00, 95% CI [0.08, 1.93]
**Fisher's exact (two-sided)**: p = 0.13

### 4.3 Statistical Interpretation

**Supported**: Effect direction favors WITH condition (R2, R3). 95% CI favors positive effect (lower bound just above zero). Effect appears task-dependent (largest in R3 with forced failures). **Not supported**: Statistical significance. Generalizability. The observed effect size is likely inflated by small-sample winner's curse. A properly powered pre-registered replication is required.

---

## 5. Discussion

### 5.1 Limitations

1. n=18, underpowered. 2. Single model. 3. Single rule. 4. No blinding, single-rater. 5. No human subjects. 6. Auto-ethnography not coded. 7. Between-subject variance. 8. Non-randomized assignment.

### 5.2 Future Work: Bridging to HCI

A human-subjects extension (n=5-10, within-subject) would measure: (1) trust calibration via Jian et al. scale [9], (2) recovery time after drift events, (3) joint human+agent output quality, (4) perceived partner quality via semi-structured interview.

### 5.3 Positioning

This work introduces identity/configuration drift as a distinct axis within the agent drift literature and provides causally-grounded pilot evidence that config rules are not decorative. The observed convergence with Anthropic's J-space — compact, causally-efficacious intermediate representations improving agent reliability — suggests a design principle that operates across abstraction layers (neural and configurational). However, we emphasize the quality gap: J-space was verified with causal ablation (removing it collapses reasoning), replicated on a different model architecture by an independent lab, and supported by a mechanistic theory (Jacobian lens). Our experiment is a pilot (n=18, p=0.13, single model, single rule) — directionally informative but not confirmatory. A properly powered replication (n≥80/group, multi-model, multi-rule) is required before interpreting the magnitude.

### 5.4 Design Principle: The Causal Bottleneck

Despite the rigor gap, the convergence is structurally informative. Four properties appear necessary for an intermediate representation to causally shape agent behavior:

1. **Compactness** — J-space uses <10% of activations; self-model.md is ~100 lines. Small control surfaces are inspectable and modifiable.
2. **Causal placement** — Both sit on the information path between input and output (J-space: downstream layers read from it; self-model: concatenated into context before inference).
3. **Structure** — J-space has metric geometry (concepts as directions); self-model has explicit graph structure (files → sections → rules).
4. **Attended to** — J-space is causally efficacious because downstream layers actually read from it; self-model works because the LLM attends to context-window tokens.

These are not properties of a specific substrate. They are constraints that any agent identity system — neural, file-system, or otherwise — must satisfy to be causally effective. The independent convergence of Anthropic's emergent solution and our engineered solution on these four constraints suggests they may be necessary (though not sufficient) conditions for agent identity persistence.

---

## 6. Conclusion

LLM agents change over time. Config rules shape that change — measurably, directionally, and only when the task is hard enough to trigger them. 56% vs. 11%, 95% CI [1.0pp, 71.6pp], p=0.13. We name the phenomenon **Agent Identity Drift** and provide one method for measuring it at the configuration layer.

**Config rules are not decorative.**

---

## References

[1] Rath, A. "Agent Drift: Quantifying Behavioral Degradation in Multi-Agent LLM Systems." arXiv:2601.04170, Jan 2026.

[2] TACT. "Mitigating Agent Drift in Coding Agents via Activation Steering." arXiv:2605.05980, May 2026.

[3] "Measuring What Persists: Identity Drift Under Long-Context Collapse." arXiv:2606.21843, Jun 2026.

[4] Anthropic. "A Global Workspace in Language Models." Jul 2026.

[5] Kambhampati, S. et al. "LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks." ICML, 2024.

[6] Lee, J.D. & See, K.A. "Trust in Automation: Designing for Appropriate Reliance." Human Factors, 2004.

[7] Sarter, N.B., Woods, D.D. & Billings, C.E. "Automation Surprises." 1997.

[8] Hofstadter, D.R. "Godel, Escher, Bach." Basic Books, 1979.

[9] Jian, J.Y. et al. "Foundations for an Empirically Determined Scale of Trust in Automated Systems." 2000.

---
*Code, data, transcripts: https://github.com/YuhaoLin2005/hermes-workspace*
