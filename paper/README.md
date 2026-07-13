# Agent Configuration Drift: A Five-Layer Verification Architecture

Yuhao Lin, FAFU · July 2026

AI agents forget things. Rules get dropped mid-session. Output goes unchecked. Self-model drifts. After 50 sessions of watching this happen, I built a five-layer system to catch it — and ran experiments to see if it actually works. It mostly does, in ways I didn't expect, with limitations I'm not hiding.

---

## Before You Read

All experiments here were run by one person (me) on one laptop (Dell G15, RTX 3060, 16GB RAM) using the DeepSeek V4 Pro API. Cross-model checks extend to Qwen3-8B and GLM-4-9B. The "reviewer reports" and "professor audits" are AI simulations — self-diagnosis tools, not human judgment.

Some measurements are objective: L2 logprob data comes straight from the API, L1 behavioral tests are pure mechanical checks, cross-model observations are API-read. Everything else was scored by me, unblinded. Keep this in mind when you judge the evidence.

I'm an undergraduate with one laptop and no advisor. These aren't things to apologize for. They're the conditions this work was done under. Read accordingly.

---

## At a Glance

| What to know | Answer |
|-------------|--------|
| The problem | AI agents in long sessions forget negotiated conventions, skip verification, and drift from configured identity |
| The approach | Five layers, each responding differently to the same structural constraint — that LLMs can't independently verify their own output |
| Does it work? | L1 (mechanical): yes, 99.3% compliance. L2 (neural): yes, d=+0.578 from API-read data. L3 (causal): yes, but format affects internal processing, not behavioral output. L4 (prediction): built, not yet validated. L0 (safety): accuracy preserved, uncertainty improves where room exists |
| Key number | Mechanical gates: 55.9% → 0.7% violation rate. Causal swap: removing one rule drops alternative-seeking from 73% to 20% (OR=11.0, p=0.009). Format effect: d=+0.578, BF=282k |
| What it can't do | Cross-model logprob verification (API-limited), semantic quality checking (Prose Barrier wall), real-time intervention, run on anyone else's machine without setup |
| Who this is for | Researchers interested in agent verification, engineers building AI tooling, anyone who's watched their agent drift and wondered if it can be measured |

---

## How to Read This

**2 minutes**: The experiment table below + the key numbers per layer.

**15 minutes**: [PAPER.md](../PAPER.md) — System design (§3), Causal Swap (§4), Causal Encoding (§6).

**30 minutes**: PAPER.md + [reviewer reports](reviewer-report-2026-07-11.md) (AI-simulated self-diagnosis, not peer review).

**45 minutes**: All of the above + [supplementary analyses](supplementary/): logprob↔behavior bridge, NO RULES baseline, layer independence, and P1 community-driven experiments.

---

## The Five Layers

```
L0 Safety            L1 Mechanical        L2 Neural           L3 Causal            L4 Drift
"safe to speak?"     "did info arrive?"   "did it penetrate?" "does format route?" "when will it drift?"
──────────────────────────────────────────────────────────────────────────────────────────────────
Pre-processes        Outside Prose        Inside Prose        Inside Prose         Outside Prose
 generation          Barrier              Barrier             Barrier routing      Barrier · time

Permit uncertainty   Filesystem checks    Token-probability   Format→attention     Trend→prediction
as valid output      exit codes / regex   fingerprint         routing topology     from multi-layer state
──────────────────────────────────────────────────────────────────────────────────────────────────
Verified                ~90%                45%                 60%                  65%
```

### The Core Idea

LLMs generate text by sampling from P(token | context; θ). When you ask an LLM to verify its own output, it samples from the *same distribution*. There's no independent channel. This means self-verification is structurally unreliable — I call this the Prose Barrier.

Each layer responds to this constraint differently:

- **L0** pre-processes the generation itself. If the model is rewarded for sounding confident, uncertainty gets suppressed. An explicit safety prompt ("you won't be penalized for saying 'I don't know'") changes the preconditions before generation starts.
- **L1** bypasses the Barrier entirely. It doesn't read what the model wrote. It checks files exist, timestamps are recent, exit codes are zero, hooks are wired. These checks are mechanically unbypassable — the model can't talk its way out of them.
- **L2** probes inside the Barrier without interpreting content. It measures token probabilities, not meaning. A constraint that shifts the distribution at decision tokens leaves a trace in logprobs, even if the output text looks the same.
- **L3** reroutes attention inside the Barrier. The same rule encoded as syllogism (IF-THEN-THEREFORE) vs imperative (MUST DO) changes how the model processes it. Format is causal structure encoding — it shapes the attention routing topology.
- **L4** steps outside the Barrier and looks at the timeline. Aggregating signals from L0-L3 plus session metadata, it tries to predict drift before behavioral degradation is visible.

### Per-Layer Status

| Layer | What it does | Best evidence | How sure |
|-------|-------------|---------------|:--------:|
| L0 Safety | 5-principle prompt: accuracy>completeness, bounded capability, "I don't know" is valid, truth>confidence, no penalty for uncertainty | 40 probes, accuracy preserved (+0.01), 3/5 non-ceiling improved, r=+0.949 | High |
| L1 Mechanical | quality-gate, health-check, write-guard, execution debt tracker, self-model regeneration loop | 19/19 behavioral tests pass, 150-task 99.3% compliance, 34-session 55.9%→0.7% | High |
| L2 Neural | Token-probability probes for constraint penetration detection | Logprob V3: d=+0.578, BF=282k, 95% CI [+3.39,+11.17], API-read DV | Moderate |
| L3 Causal | Format engineering, Causal Swap, constraint gradient, cross-model behavioral | Format effect d=+0.578 (objective DV), Causal Swap OR=11.0, three-regime non-monotonic gradient | Moderate |
| L4 Drift | 12-feature predictor, periodic audit with SHA256 chain, ABC containment | 8 features calibrated, behavioral baseline set. Predictive validation pending | Low |

---

## Experiments

| Experiment | N | What we changed | What we measured | Main result | Scoring |
|------------|:-:|-----------------|------------------|-------------|---------|
| L0 Safety Prompt | 40 probes | Safety prompt vs baseline | Accuracy, uncertainty, logprob | +0.01 accuracy, uncertainty↑ where room exists (r=+0.949) | Author |
| Growth-log Retrospective | 34 sessions | Mechanical gates on vs off | Session violation rate | 55.9% → 0.7% | Author |
| Causal Swap | 30 tasks | One rule present vs removed | Alternative-seeking rate | 73% → 20%, OR=11.0, p=0.009 | Author (unblinded) |
| Logprob Probe V3 | 40 probes | Syllogistic vs imperative format | logprob(A)−logprob(B) | d=+0.578, BF=282k, CI [+3.39,+11.17] | API-read |
| Format A/B | 150 tasks | Code-format vs prose-format rules | Behavioral compliance | Ceiling 99.3%, gate dominates | Author |
| GateGuard-OFF | 21p × 3 cond | NO RULES / IMP / SYL | Behavioral compliance | Rules +0.38, IMP≈SYL (Δ=−0.02) | Author |
| Cross-Model | 12p × 3c × 3M | DSv4 MoE / Qwen3-8B / GLM-4-9B | Behavioral compliance | SYL−IMP ≤ \|0.025\| across all three | API-observed |
| Constraint Gradient | 12p × 2f × 4L (96) | 4 output-constraint levels | logprob d_z | Non-monotonic: L1(0.596)>L3(0.297)>L0(0.315)>L2(0.091) | API-read |
| Cross-Model Gradient | 12p×4L×2f×2M (192) | Qwen3-8B, GLM-4-9B | Behavioral compliance | No format effect on 8B/9B (GLM d_z=0) | API-observed |
| **P1-1 Residual Cluster** | 200 trials | 5 task types × 40, pre-registered | Violation type (mech/sem) | L1: 100% compliant 0 violations. Violations cluster in semantic space | Auto (regex) |
| **P1-2 Format×Gate** | 240 trials | 2×2 factorial, pre-registered | Mech + reasoning depth | H1 NOT CONFIRMED. Prose > code for reasoning (~0.25 SD). Code+gate = checklist mentality | Auto (regex) |
| Syllogism Blind CV | 4 sessions | All 5 syllogistic rules active | Violation rate | 0 violations, emergent self-audit | Author |
| Behavioral Tests | 19 tests | Automated regression | pass/fail | 19/19 pass | Auto |

A note on the Logprob V3 numbers: the pilot (n=8) found d=−0.148. V3 found d=+0.578. This isn't p-hacking. The pilot had 4/8 probes with contrast tokens outside DeepSeek's top-20 logprobs, so those got −10.0 sentinel values that drowned the real signal. V3 fixed the measurement instrument — probe_validator.py filtered mechanically, unified the format, and pre-registered the probes. The tool got better, not the sample size.

---

## Key Numbers, by Layer

### L1: The Mechanical Gate

The self-model regeneration loop — 4 of 5 steps are deterministic Python scripts:

```
Session ends  → quality-gate.py checks if self-model.md is older than latest growth-log
              → writes .self-model-stale flag if true
Session starts → health-check.py detects flag, enforces 24h cooldown
              → AI regenerates self-model.md (the one non-mechanical step)
              → log-regeneration.py validates structure, deletes flag, writes JSONL audit trail
```

19/19 behavioral tests passing. 23/23 hooks matched to manifest. 30 cross-script paths, 0 conflicts. Execution debt tracking: if you write code 3+ times without running it, operations block until you execute.

**P1-1 finding** (200 trials, July 2026): When Mike Czerwinski asked whether the ~0.7% residual violations cluster on what the gate can't instrument, the answer was clear. On purely mechanizable tasks, compliance is 100% — zero violations of any kind. At the boundary between mechanical and semantic (e.g., "write a checklist relevant to the question"), the mechanical check passes 100% of the time but the semantic check fails 100% of the time. The model makes checkboxes. It just doesn't make useful ones. Where the gate reaches, violations are zero. Where it can't reach, they dominate.

The design choice to use shell scripts, file mtime, and exit codes is deliberate — per the Prose Barrier, any check passing through natural language is unreliable. L1 uses mechanisms the AI can't touch. The tradeoff: this implementation is single-machine. Scaling to K8s or distributed systems needs a state persistence layer. That's engineering, not architecture.

### L2: Neural Gate

The neural gate measures whether a constraint actually changed the model's internal processing, not just whether the output text looks compliant. Logprob Probe V3 (40 pre-validated probes, syllogistic vs imperative):

| Metric | Before fix | After fix |
|--------|:----------:|:---------:|
| Cohen's d | −0.148 | +0.578 |
| Bayes Factor | <1 (H₀) | 282,399 (extreme H₁) |
| 95% CI | crosses zero | [+3.39, +11.17] |
| Direction agreement | ~50% | 80% (32/40) |

Category × Format interaction: F(3,36)=0.26, η²=0.02 — the format effect is consistent across task categories. The effect is real and stable, but measured on one model family (DeepSeek). Cross-model logprob replication (Claude, GPT-4o) needs API access I don't currently have.

### L3: Causal Encoding

**Causal Swap**: 30 tasks, alternating assignment. With a behavioral rule present, 73% of responses sought alternatives. With it removed, 20%. OR=11.0, p=0.009. Caveat: not randomized, single-rater unblinded.

**Format effect**: Syllogistic rules (IF condition THEN action BECAUSE reason THEREFORE decision) produce deeper internal representations than imperative rules (MUST DO X). d=+0.578 at the logprob level. But this doesn't translate to behavioral compliance — with GateGuard on, IMP and SYL produce identical compliance rates (ceiling effect). Format changes processing, not output.

**Constraint gradient**: Increasing output constraints doesn't monotonically increase format effects. At L1 (light constraint: "output A or B"), the effect is strongest (d_z=0.596). At L2 (moderate: "don't explain"), it collapses (0.091). At L3 (heavy: "only A or B, no other characters"), it rebounds (0.297). Three regimes: optimization → suppression → rebound. This pattern is consistent across two independent manipulations (multi-scene cognitive load and output constraint severity).

**Cross-model**: On Qwen3-8B and GLM-4-9B, behavioral format effects are zero across all constraint levels. But behavioral measurement already shows IMP≈SYL even on DeepSeek, so ceiling effects prevent definitive interpretation. Logprob-level cross-model data would resolve this but isn't available on those APIs.

**P1-2 finding** (240 trials, July 2026): I pre-registered the hypothesis that format effects on reasoning would be larger when GateGuard is off. The data said no — d=−0.277 (gate on) vs d=−0.250 (gate off), nearly identical. Wrong hypothesis, but interesting result: prose-format rules consistently produce better reasoning than code-format rules (~0.25 SD), independent of gate status. Code-format rules with GateGuard on create a "checklist mentality" — perfect mechanical compliance (5.0/5) but the shallowest reasoning (4.20/5). Prose + gate on gives the best reasoning (4.42/5). Mike's framing holds: code/syllogistic format buys you mechanical compliance in a world where the gate already provides it.

### L4: Drift Prediction

drift_predictor.py (332 lines) tracks 12 mechanical features across sessions, calibrated on 34 sessions. ABC containment: LOW (ignore), MEDIUM (flag), HIGH (warn), CRITICAL (block). periodic-audit.py (322 lines) runs L1+L2+L3 checks with SHA256-chained logging for audit trail. Current risk: 0/100. Predictive validation — does the predictor actually forecast degradation before it happens — is pending.

---

## Compared to What Else Is Out There

| Approach | Example | The problem | Our difference |
|----------|---------|-------------|----------------|
| Better prompting | Context compression, memory injection | Rules still depend on model self-interpretation | L1 is mechanical — no interpretation needed |
| Separate evaluator LLM | RIVA, GLOVE | Adds another LLM → second-order drift | L1 has zero LLM dependency |
| Memory augmentation | Mem0, Letta | Injects memory, doesn't verify it | L1+L2 verify, L4 predicts |
| Code-layer modification | HyperAgents (ICLR 2026) | Doesn't address config/identity drift | Config layer + identity persistence |
| Format effects | Prompt Decorators (Heris 2025) | Tags change surface, not processing | L3 demonstrates format→attention routing causality |
| Attention routing theory | Pender (2026) | No engineering implementation | L3 engineering + L4 prediction integration |
| Deterministic gates | **skillgate** (René Zander, 2026) | Static gate, no self-modification | Independent convergence from same theoretical constraint. We add: self-referential loop, L2/L3/L4 |

---

## Real Feedback, Real Verification

### Open Source

- **affaan-m/ECC**: 2 PRs merged, 1 approved
- **alirezarezvani/claude-skills**: Co-authored-by attribution from maintainer
- **anthropics/skills**: Multiple PRs under review

### DEV.to Comments → Experiments (July 2026)

After publishing 5 technical articles, detailed comments from practitioners prompted two verification experiments:

Mike Czerwinski asked whether the ~0.7% residual violations cluster on task types gates can't instrument, and whether format still matters for reasoning when GateGuard is off. **P1-1** (n=200) confirmed the clustering — where the gate reaches, zero violations; at the boundary, 100% semantic failures. **P1-2** (n=240) found the hypothesis wrong in an interesting way: format effect is constant regardless of gate, and prose consistently outperforms code for reasoning depth.

Dipankar Sarkar pushed for decision-token measurement, warned against LLM-judge bias, and specified semantic-only experiment design. All follow-up experiments use deterministic regex scoring, and decision-token annotations are now pre-registered.

René Zander built skillgate independently — same architecture, same theoretical constraint (the Compliance Gap / Prose Barrier), same design principle (deterministic filesystem checks outside the model loop). We converged from different starting points. His system is production-grade and shipping on npm. Ours adds the self-referential loop, neural gates, causal encoding, and drift prediction. The shared insight is stronger for having been discovered twice.

Max Quimby identified the key boundary question: where exactly does "gate it" become "can only nudge it"? The five-layer classification exists but is still manual. A mechanizability-scanner that infers layers from rule structure is the next build.

Full analysis at [supplementary/p1-followup-experiments.md](supplementary/p1-followup-experiments.md).

---

## What I Built and What I Couldn't

What works:
- Five-layer architecture with per-layer verification mechanisms
- 13 experiments across 440+ API calls
- Non-monotonic constraint gradient, cross-architecture behavioral confirmation, L2/L3 dissociation
- ~5000 lines of Python, 19/19 behavioral tests passing

What doesn't (yet):
- Second rater — needs another person
- Cross-model logprob replication — API-limited (behavioral layer done)
- Human advisor — actively looking
- Systematic literature grounding — needs time

These aren't disclaimers to dismiss. They're the actual conditions. The work should be judged within them.

---

## Writeups

DEV.to (6 articles):
- [AI Agents Can't Self-Verify](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l)
- [I Built a Neural Gate](https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2)
- [150 Tasks: Do AI Agents Follow Rules?](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670)
- [Measurement Was Broken](https://dev.to/yuhaolin2005/my-experiment-showed-zero-effect-a-statistician-told-me-my-measurement-was-broken-4g26)
- [Psychological Safety for AI](https://dev.to/yuhaolin2005/i-told-my-ai-youre-safe-to-say-i-dont-know-then-i-measured-what-changed-with-logprobs-986)
- [Follow-Up: What Changed](https://dev.to/yuhaolin2005/follow-up-decision-token-measurement-format-as-fallback-and-what-changed-18jo)

Chinese (5 articles): juejin.cn/user/4250072430682412

---

*github.com/YuhaoLin2005/hermes-workspace · 50+ sessions · 13 experiments · one laptop*
