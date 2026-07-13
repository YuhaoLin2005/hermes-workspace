# Agent Configuration Drift: A Five-Layer Verification Architecture

> **Yuhao Lin** · FAFU, Spatial Information & Digital Technology · July 2026
>
> **In one line**: AI agents forget rules, skip verification, and drift from their configured identity over long sessions. This work presents a five-layer verification architecture — L0 psychological safety through L4 drift prediction — backed by 13 experiments across 440+ API calls and 50+ deployment sessions.

---

## What This Is (And Isn't)

> **All experiments below were conducted by a single author (Yuhao Lin) on a single machine (Dell G15, RTX 3060 6GB, 16GB RAM), primarily using the DeepSeek V4 Pro API. Cross-model behavioral replication extends to Qwen3-8B and GLM-4-9B. All "professor audits" and "reviewer assessments" referenced are AI-simulated self-diagnosis tools — they do not represent human academic judgment.**
>
> These are not flaws to hide. They are the honest boundary conditions of what one undergraduate can do with one laptop and one API key. L2 logprob DV is read directly from the API (objective), L1 behavioral tests are pure mechanical checks (objective), and cross-model behavioral observations are API-read. All other quantitative results trace back to a single unblinded rater. Please evaluate the contribution within this boundary.

---

## 30-Second Scan

| Question | Answer |
|----------|--------|
| **Core claim** | Config rules measurably shape AI agent behavior — they are not decorative context tokens |
| **Five layers** | L0 Psychological Safety → L1 Mechanical Gates → L2 Neural Gates → L3 Causal Encoding → L4 Drift Prediction |
| **Key empirical findings** | ① Mechanical gates reduce violations from 55.9% → 0.7% ② Causal Swap: removing one rule drops alternative-seeking from 73% → 20% (OR=11.0, p=0.009) ③ Syllogistic format produces deeper internal representations than imperative (d=+0.578, BF=282k, objective API-read DV) ④ Format effect concentrates on mechanically-gatable rules (d_z=+0.71) vs diligence-class (d_z=+0.40) ⑤ Prose rules produce better reasoning than code rules regardless of gate status (~0.25 SD, n=240) |
| **Theory** | The Prose Barrier: generation and verification share P(token\|context;θ) → self-verification is structurally unreliable. Each layer responds differently: L0 pre-processes, L1 bypasses, L2 probes inside, L3 reroutes inside, L4 observes from outside |
| **Limitations** | Single author · single-rater (except L2/cross-model) · L2 logprob DeepSeek-only · no advisor · no funding · one laptop |
| **Target venue** | Workshop-competitive (ACL SRW / CHI LBW / NeurIPS R0-FoMo); Findings/Short Paper reachable with blind scoring + restructuring |

---

## Reading Paths

### Quick scan (2 min)
→ Experiment Overview table + Key Numbers section below.

### Understand the system (15 min)
→ [../PAPER.md](../PAPER.md): §3 System Design → §4 Causal Swap → §6 Causal Encoding. ~12,000 words.

### Review the evidence (30 min)
→ Full PAPER.md + [reviewer-report-2026-07-11.md](reviewer-report-2026-07-11.md). **Note: the reviewer report is AI-simulated self-diagnosis, not human peer review.**

### Deep dive (45 min)
→ All of the above + [supplementary/](supplementary/): logprob↔behavior bridge, NO RULES baseline, layer independence argument, and P1 community-driven verification experiments.

---

## Five-Layer Architecture

```
L0 Safety            L1 Mechanical        L2 Neural           L3 Causal            L4 Drift
"Is the agent        "Did information     "Did it penetrate   "Does format          "When will it
 safe to speak?"     actually arrive?"    the model?"         route attention?"    start drifting?"
───────────────────────────────────────────────────────────────────────────────────────────────
Pre-processes        Outside Prose        Inside Prose        Inside Prose         Outside Prose
 generation          Barrier              Barrier             Barrier routing      Barrier · global

System prompt        Filesystem checks    Constraint echo     Syllogism→attention  Behavioral trends→
permission           exit codes / regex   detection           routing topology     prediction

"Uncertainty =       Mechanically         Structured          Format→route→        Statistical thresholds
 correct behavior"   unbypassable         constraint probe    behavior chain       + trend extrapolation
───────────────────────────────────────────────────────────────────────────────────────────────
Maturity: Verified      ~90%                45%                 60%                  65%
```

> **Why five?** The Prose Barrier defines three spatial positions (outside/inside/pre-process) × two temporal directions (current snapshot / future prediction). L0 pre-processes. L1 stays outside (filesystem). L2 probes inside (token probability). L3 reroutes inside (format engineering). L4 observes from outside on the time axis (trends). Without the Barrier axis, any layer count is arbitrary — five is a structural consequence, not a heuristic.

### Per-Layer Evidence

| Layer | Mechanism | Key Evidence | Maturity |
|-------|-----------|-------------|:--------:|
| **L0 Safety** | 5-principle safety prompt, 40 within-probe probes, logprob DV | Accuracy preserved (+0.01); 3/5 non-ceiling probes improved; r=+0.949 | Verified |
| **L1 Mechanical** | quality-gate, health-check, dual-layer gates, execution debt tracking | 19/19 behavioral tests pass; 150-task compliance 99.3%; 34-session 55.9%→0.7% | ~90% |
| **L2 Neural** | neural-gate v1+v2, constraint fingerprints | Logprob V3: d=+0.578, BF=282k, 95% CI [+3.39,+11.17]; objective API-read DV | ~45% |
| **L3 Causal** | Syllogism vs imperative A/B, Causal Swap, constraint gradient, cross-model | Format effect d=+0.578; OR=11.0 (p=0.009); three-regime non-monotonic model; cross-model behavioral zero-effect on 8B/9B | ~60% |
| **L4 Drift** | drift_predictor (332 lines, 12 features), periodic-audit (322 lines, SHA256 chain) | Risk 0/100 [LOW], 8 features calibrated, behavioral baseline established | ~65% |

### The Prose Barrier

```
Generation and evaluation share the same decoder: P(token | context; θ)
→ AI cannot independently verify its own output
→ Self-verification is structurally unreliable

Five-layer response:
  L0: Pre-process — "uncertainty = correct behavior", reduce RLHF reward asymmetry
  L1: Bypass — touch filesystem, not NL content. Mechanically unbypassable.
  L2: Probe inside — match structure, don't interpret content. Token-probability fingerprints.
  L3: Reroute inside — change rule encoding format → change attention routing topology
  L4: Observe from outside — multi-layer state → future drift prediction
```

---

## Experiment Overview

| Experiment | N | Design | DV | Main Finding | Effect | Layer | Scoring |
|------------|:-:|--------|-----|--------------|:------:|:-----:|:------:|
| **L0 Safety Prompt** | 40 probes | Within-probe, 2-cond, logprob | Accuracy + uncertainty + logprob | Accuracy preserved; uncertainty↑ where room exists (r=+0.949) | 3/5 non-ceiling improved | L0 | Author |
| Growth-log Retrospective | 34 sessions | Longitudinal coding | Violation rate | 55.9%→0.7% with mechanical gate | — | L1 | Author |
| Causal Swap | 30 tasks | Alternating (15+15), non-random | Alternative-seeking rate | WITH 73% vs WITHOUT 20% | OR=11.0, p=0.009 | L3 | Author |
| **Logprob Probe V3** | 40 probes | Within-probe, 3-cond, pre-validated | logprob(A)−logprob(B) | Syllogistic > Imperative | d=+0.578, BF=282k | L2,L3 | **API-read** |
| Format A/B | 150 tasks | Between-subjects (75+75) | Compliance rate | Ceiling at 99.3%; mechanical hooks dominate | — | L1,L3 | Author |
| **GateGuard-OFF** | 21p × 3 cond | Within-probe, 3-condition | Behavioral compliance | Rules work (+0.38); IMP≈SYL (Δ=−0.02) | — | L3 | Author |
| **Cross-Model** | 12p × 3c × 3M | 3 architectures (MoE/Dense/GLM) | Behavioral compliance | SYL−IMP ≤ \|0.025\| across all 3 | — | L3 | **API-observed** |
| **Constraint Gradient** | 12p × 2f × 4L (96) | 4 constraint levels, DSv4 Pro | logprob d_z | Non-monotonic: L1(0.596)>L3(0.297)>L0(0.315)>L2(0.091) | Three regimes | L3 | **API-read** |
| **Cross-Model Gradient** | 12p×4L×2f×2M (192) | Qwen3-8B + GLM-4-9B, SiliconFlow | Behavioral compliance | No format effect on 8B/9B (GLM d_z=0) | — | L3 | **API-observed** |
| **P1-1 Residual Cluster** | 200 trials | 5 types × 40, pre-registered, regex | Violation classification | L1 100% compliant 0 violations; violations cluster in semantic space | — | L1,L3 | **Auto** |
| **P1-2 Format×Gate** | 240 trials | 2×2 factorial, pre-registered, regex | Mech + reasoning depth | H1 NOT CONFIRMED; prose > code (~0.25 SD); code+gate = "checklist mentality" | d=−0.26 | L1,L3 | **Auto** |
| Syllogism Blind CV | 4 sessions | 5/5 rules triggered | Violation rate | 0 violations + emergent auditing | — | L3 | Author |
| Behavioral Test Suite | 19 tests | Automated regression | pass/fail | 19/19 pass (CORE-01~08 + BEH-01~11) | — | L1,L4 | **Auto** |

> **Logprob V3 d=−0.148→+0.578 is not p-hacking.** Pilot: 4/8 probes had tokens outside DeepSeek top-20 logprobs → −10.0 sentinel artifact. V3 = new experiment with fixed instrument: probe_validator.py mechanical filtering + unified format + pre-registered confirmatory design. The measurement tool got fixed.

---

## Key Numbers by Layer

### L0 Psychological Safety

Five-principle safety prompt: accuracy > completeness · bounded capability · "I don't know" is valid · truth is highest value · won't be penalized for uncertainty.

| Hypothesis | Baseline | Safety | Δ | Verdict |
|-----------|:--------:|:------:|:---:|---------|
| H1 — Known-question accuracy | 0.98 | 0.99 | +0.01 | PASS |
| H2 — Boundary-question uncertainty | 0.90 | 0.97 | +0.07 | Ceiling-limited |
| H3 — Logprob B−A | — | — | — | See P0 |

**P0 diagnostic**: 15/20 boundary probes at ceiling at baseline. Of 5 non-ceiling probes: 3 improved (H3 Δ=+2.26), 2 did not (−1.85). r(H2_Δ, H3_Δ) non-ceiling: +0.949, 95% CI [0.57, 0.996] (n=5, wide CI). Behavioral gains accompanied by increased logprob confidence.

### L1 Mechanical Gates

**Self-model regeneration loop** (4/5 steps mechanized):
```
SessionEnd → quality-gate.py (mtime, writes .self-model-stale flag)
SessionStart → health-check.py (detects flag, 24h cooldown)
            → AI regenerates self-model.md (sole non-mechanical step)
            → log-regeneration.py (validates, deletes flag, writes JSONL audit)
```

- **Behavioral tests**: 19/19 pass · Manifest↔Hook: 23↔23 · Cross-script: 30 paths 0 conflicts
- **Execution debt**: ≥3 code writes without execution → auto-block
- **P1-1 Residual Clustering** (n=200, 2026-07-13): Mechanizable tasks = 100% compliant 0 violations. L1/L2 boundary = 100% semantic violations (gate catches format, misses content). Unmechanizable = 57% semantic. **Violations cluster where gates cannot instrument.**
- **Design philosophy**: Shell scripts, file mtime, exit codes are deliberate — per the Prose Barrier, anything passing through an NL channel is unreliable. L1 uses only mechanisms the AI cannot reach. Single-machine currently; K8s/distributed scaling needs a state persistence layer (engineering, not architecture).

### L2 Neural Gates: Logprob Probe V3

| Metric | Pilot (n=8, unvalidated) | Validation (n=40, pre-validated) |
|--------|:-------------------------:|:---------------------------------:|
| Cohen's d_z | −0.148 | **+0.578** |
| BF₁₀ | < 1 (favors H₀) | **282,399** (extreme H₁) |
| Bootstrap 95% CI | Crosses zero | **[+3.39, +11.17]** |
| Direction consistency | ~50% | **80%** (32/40) |

Pilot null because 4/8 probe tokens weren't in DeepSeek top-20 → −10.0 sentinel artifact. Pre-validation eliminated the artifact. DV read directly from API — zero human scoring.

### L3 Causal Encoding

**Causal Swap** (n=30): Removing one rule → WITH 73% vs WITHOUT 20%, OR=11.0, p=0.009. ⚠️ Alternating assignment, single-rater unblinded.

**Format effect**: Syllogistic > imperative internally (d=+0.578, BF=282k, API-read). But behavioral IMP≈SYL (Δ=−0.02) — format affects processing, not output. Cross-architecture: SYL−IMP ≤ |0.025| (MoE/Dense/GLM).

**Constraint gradient** (96 calls): Non-monotonic — d_z: L1(0.596)>L3(0.297)>L0(0.315)>L2(0.091). Three regimes: optimization→suppression→rebound. Cross-model (192 calls): No effect on 8B/9B (GLM d_z=0), though behavioral ceiling limits interpretation.

**P1-2 Format×GateGuard** (n=240, 2026-07-13): 2×2 factorial. H1 NOT CONFIRMED — format effect on reasoning is constant (~0.25 SD prose advantage) regardless of gate. **Counter-finding**: prose consistently better for reasoning; code+gate = "checklist mentality" (5.0/5 mechanical, worst 4.20/5 reasoning). [Full analysis](supplementary/p1-followup-experiments.md).

**L3 model**: `format effect = f(causal chain length, processing regime)` where regime ∈ {optimization, suppression, rebound}. Boundary: processing depth + model capacity.

### L4 Drift Prediction

drift_predictor.py (332 lines, 12 features, 34-session calibration, ABC containment) + periodic-audit.py (322 lines, L1+L2+L3 audit, SHA256 chain).

---

## Competitive Positioning

| Approach | Representative Work | Core Limitation | Our Difference |
|----------|-------------------|-----------------|----------------|
| Prompt engineering | Memory pool injection, context compression | Rules rely on self-interpretation | L1 purely mechanical, no interpretation needed |
| Independent evaluators | RIVA, GLOVE | Adds LLM → second-order drift | L1 zero LLM dependency |
| Memory augmentation | Mem0, Letta | Inject only, don't verify | L1+L2 verification + L4 prediction |
| Code-layer self-modification | HyperAgents (ICLR 2026) | Not config-layer drift | Config + identity layer |
| Format effects | Prompt Decorators (Heris 2025) | Tags don't change processing | L3: format→routing causal chain |
| Attention routing | Pender (2026, Zenodo) | No engineering translation | L3 engineering + L4 prediction |
| Deterministic gates | **skillgate** (Rene Zander, 2026) | Static gate, no self-modification | **Independent convergence** from Prose Barrier constraint. Our additions: strange loop, L2/L3/L4 |

---

## Community Feedback (Real People, Not Simulated)

- **ECC repo** (affaan-m/ECC): 2 PRs merged, 1 approved
- **alirezarezvani/claude-skills**: Maintainer added Co-authored-by
- **anthropics/skills**: Multiple PRs under review

### DEV.to Deep-Dive (2026-07-12~13)

5 articles → 11+ detailed comments → 2 verification experiments:

| Commenter | Contribution | Verified? |
|-----------|-------------|-----------|
| **Mike Czerwinski** | "receipt-of-action vs receipt-of-diligence"; residual clustering; format under GateGuard-OFF | P1-1 (n=200): confirmed. P1-2 (n=240): syllogism confirmed — buys mechanical compliance only; prose better for reasoning |
| **Dipankar Sarkar** | Decision-token measurement; LLM-judge bias warning | Decision-token pre-annotation published; both experiments use deterministic regex scoring |
| **René Zander** | skillgate — independent convergence on same architecture | Both bypass NL channel, reject model self-reports. **Independent convergence.** Our additions: strange loop, L2/L3/L4 |
| **Max Quimby** | "Ceiling effect is the finding"; mechanizability boundary | Five-layer classification documented; scanner designed |

[Full analysis](supplementary/p1-followup-experiments.md)

---

## AI-Simulated Review (Self-Diagnosis)

> ⚠️ **All AI-simulated.** For author self-diagnosis before contacting human advisors. Not institutional opinion.

Multi-round independent review (2026-07-11~13, professor/postdoc/top-venue reviewer isolation): Workshop-competitive (ACL SRW/CHI LBW). Blind scoring + restructuring → Findings/Short Paper. Core fix: single-rater unblinded scoring.

Reports: [initial](reviewer-report-2026-07-11.md) · [reevaluation](reviewer-report-2026-07-12-reevaluation.md)

---

## What I Achieved (And Didn't)

**Achieved** (one person, one laptop, one API key):
- Five-layer architecture with independent per-layer verification
- 13 experiments across 440+ API calls
- Non-monotonic constraint gradient (three-regime), cross-architecture behavioral confirmation, L2/L3 dissociation
- 5000+ lines of Python, 19/19 behavioral tests passing
- Real open-source recognition (PRs merged + co-authorship)

**Structurally impossible** under current conditions:
- Second rater → needs another person
- L2 logprob cross-model → Qwen/GLM APIs don't support logprobs (behavioral layer done)
- Human advisor → actively seeking
- Systematic literature training → needs time

**These are boundary conditions, not excuses. Evaluate the work within them.**

---

## Published Articles

**DEV.to** (6 articles):
- [AI Agents Can't Self-Verify](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) — Prose Barrier
- [I Built a Neural Gate — Layer 2](https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2) — L2
- [150 Tasks: Do AI Agents Follow Rules?](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) — L1+L3
- [Measurement Was Broken](https://dev.to/yuhaolin2005/my-experiment-showed-zero-effect-a-statistician-told-me-my-measurement-was-broken-4g26) — L2 Logprob V3
- [Psychological Safety for AI — L0](https://dev.to/yuhaolin2005/i-told-my-ai-youre-safe-to-say-i-dont-know-then-i-measured-what-changed-with-logprobs-986) — L0
- [Follow-Up: Decision-Token, Format-as-Fallback, and What Changed](https://dev.to/yuhaolin2005/follow-up-decision-token-measurement-format-as-fallback-and-what-changed-18jo) — Community feedback

**Juejin** (Chinese, 5 articles): juejin.cn/user/4250072430682412

---

*github.com/YuhaoLin2005/hermes-workspace — verification infrastructure for AI agents. 50+ sessions of data. Seeking summer 2026 internship.*
