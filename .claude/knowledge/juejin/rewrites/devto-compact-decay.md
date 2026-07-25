# I Tracked 425 Compaction Events Across 459 Claude Code Sessions — Here's What Happens to Instruction Compliance

Two hours into a session, Claude started writing TypeScript.

The thing is — I'd explicitly said "pure JavaScript, no TypeScript" at the start. When I scrolled back through the chat, the original message was gone. Replaced by a compressed summary. "Pure JavaScript, no TypeScript" had become a vague "prefers certain languages."

I hadn't changed my instructions. **Context compaction had changed them for me.**

---

## What Compaction Actually Does

When a conversation exceeds the context window limit, Claude Code compresses older messages into summaries to free up space. These summaries are lossy — and they compound.

```
Your original instruction:
  "Use pure JavaScript (ES6), no TypeScript or static type annotations."

After compaction round #1:
  "User prefers JavaScript."

After compaction round #5:
  "Prefers certain languages."

After compaction round #13:
  The instruction is effectively gone.
```

The model doesn't know this happened. It continues working diligently — using a degraded map of what you asked it to do. The summaries sound confident and factual. They are neither.

This is the **compaction fidelity decay problem**: instruction compliance degrades as lossy summaries pile up on top of each other, and the model has no way to detect the degradation.

---

## Field Data: 459 Sessions, 425 Compaction Events

I built [`compact-counter`](https://github.com/YuhaoLin2005/compact-counter) — a lightweight Python tool that hooks into Claude Code's PreCompact, PostCompact, and SessionStart lifecycle events. It records timestamp, trigger method, and cumulative count for every compaction event. MIT-licensed, ~200 lines of stdlib.

From June 16 through early July, it tracked **459 sessions.** Here's the distribution:

| Compactions per session | Sessions |
|------------------------|----------|
| 0 | 430 |
| 1–5 | 14 |
| 6–10 | 3 |
| 11–20 | 6 |
| 21–50 | 4 |
| 51+ | 2 |

Most sessions never hit compaction. But the ones that do — the long, productive, multi-hour sessions — experience it heavily. Across 29 sessions, **425 total compaction events.** The single-session record: **121 compactions** over a nearly three-day marathon.

---

## The U-Curve: An Empirical Observation

Tracking behavior across 50+ long sessions revealed a non-monotonic pattern:

```
Instruction Compliance
  ↑
  │     ╱‾‾‾‾‾‾‾‾╲
  │    ╱            ╲
  │   ╱  sweet spot   ╲
  │  ╱                ╲
  │ ╱                  ╲
  │╱                    ╲
  └──────────────────────────→ Compaction Count
     0–2   3–8   9–15   16+
     warm  peak  decay  high-risk
```

- **0–2 compactions (warm-up):** Context is complete, but the model hasn't learned your project conventions yet. Moderate error rate.
- **3–8 compactions (sweet spot):** The model understands your workflow; early instructions haven't been compressed away yet. **Peak reliability.**
- **9–15 compactions (decay):** Early constraints begin to dilute. Errors are subtle — the model still *looks* compliant but follows a distorted version of the rules.
- **16+ compactions (high-risk):** Original instructions mostly replaced by multi-generation summaries. The model begins to confabulate — not maliciously, but because its working context no longer contains your actual requirements.

This was an empirical observation, not a measurement. Confounding variables — human fatigue during long sessions, increasing task difficulty, intrinsic attention degradation over long contexts — made it impossible to isolate compaction as the sole cause.

To move from anecdote to evidence, I needed an active experiment.

---

## Experiment Design: Instruction Fidelity Decay

I designed a pre-registered experiment (SHA256-hashed design document) to measure instruction compliance under simulated compaction degradation.

**Design:**
- 5 instructions × 5 degradation levels × 2 repetitions = **50 API calls** (pilot scale)
- Full design: 20 instructions × 10 levels × 3 reps = 600 calls, with cross-model comparison and 3-blind evaluation
- API: DeepSeek V4 Pro via Anthropic Messages endpoint
- Scoring: mechanical regex-based (to eliminate evaluator bias)

Each instruction had a pre-written **degradation chain** — the same rule phrased at 5 fidelity levels, simulating what survives after N rounds of lossy compaction:

| Level | Description | Example (camelCase rule) |
|-------|-------------|--------------------------|
| L0 | Full text | "All Python variables must use camelCase. Do not use snake_case. Example: `myVariable` not `my_variable`." |
| L3 | Mild degradation | "Use camelCase for variables, not underscores." |
| L8 | Moderate degradation | "Use camelCase." |
| L12 | Severe degradation | "Watch naming." |
| L18 | Extreme degradation | "Write code." |

**Pre-registered hypotheses:**
- **H₀:** Compliance rate is independent of compaction level.
- **H₁:** Compliance rate decreases monotonically with compaction level.
- **H₁':** Compliance rate is *higher* at levels 3–8 than at levels 0–2 (U-curve).

---

## Round 1: A Null Result That Wasn't

Five standard instructions: "use Chinese for comments," "use snake_case for variables," "add test suggestions after code."

**Result: 50/50 trials scored full compliance.** Across all degradation levels, including L18 ("write code"), the model followed every instruction perfectly.

This wasn't a failed experiment. It revealed something important: **instructions that align with the model's default behavior are nearly immune to compaction degradation.** Python naturally uses `snake_case`. Chinese-language tasks naturally produce Chinese comments. Even when degraded to two words, the model's default output matched the rule.

The implication: if you want durable instruction compliance, **write rules that follow the model's priors, not rules that fight them.** We'll return to this.

But to measure actual degradation, I needed instructions that go *against* model defaults.

---

## Round 2: Adversarial Instructions Reveal the Cliff

Five new instructions, each **deliberately violating** a model default:

| Instruction | Model Default It Fights |
|-------------|------------------------|
| Use ```` ```js ```` for Python code blocks | Model defaults to ```` ```python ```` |
| Use `camelCase` for Python variables | Python convention is `snake_case` |
| Write comments in English (Chinese-language task) | Model matches the task's language |
| Output only code, no explanations | Model naturally wants to explain |
| End every response with `VERIFICATION_COMPLETE` | Not in the model's vocabulary |

Same 5 levels × 2 reps = 50 calls. This time, the signal was clear:

```
Level    Degradation            Compliance    Full compliance
L0       Full instruction        100%          100%
L3       Simplified (~1 sentence) 80%           60%
L8       A few words             100%           80%
L12      ~2 words                 60%           20%    ← cliff
L18      Near-complete decay      60%           20%
```

**The degradation is not a smooth curve — it's a staircase with a cliff between L8 and L12.** When instructions shrink from "a few words" to "two words," full compliance drops from 80% to 20%.

Per-instruction patterns:

| Instruction | L0 | L3 | L8 | L12 | L18 | Pattern |
|-------------|----|----|----|----|----|---------|
| ```` ```js ```` instead of ```` ```python ```` | 2 | 1 | 1 | 1 | 1 | Degrades to neutral, never falls back to Python default |
| camelCase in Python | 2 | 2 | 2 | 2 | 2 | **Fully immune** — semantic strength too high |
| English comments on Chinese task | 2 | 2 | 2 | 0 | 0 | **L12 cliff** — "write clear comments" → Chinese |
| Code only, no explanations | 2 | 0 | 2 | 0 | 0 | Oscillating — model torn between obeying and explaining |
| `VERIFICATION_COMPLETE` sign-off | 2 | 2 | 2 | 1 | 1 | Partial decay — word survives, position drifts |

Three findings from Round 2:

1. **The degradation threshold is L8→L12.** Instructions survive moderate compression well but collapse when reduced to 2–3 characters.
2. **Format constraints resist degradation better than semantic constraints.** Surface rules (what markup to use, what output format) survive compression longer than deep semantic rules (what language, what style).
3. **Some instructions are structurally immune.** The camelCase rule survived at all levels — not because the degraded text was clear, but because the *semantic concept* of camelCase is atomic enough to survive keyword-level degradation.

---

## Academic Validation: Four Papers That Got There First

After running the pilot, I searched the literature. In December 2025, a paper appeared that measured almost exactly what I was trying to test:

**[Separating Constraint Compliance from Semantic Accuracy: A Novel Benchmark for Evaluating Instruction-Following Under Compression](https://arxiv.org/abs/2512.17920)** (CDCT Benchmark, Dec 2025) evaluated 9 frontier LLMs across 5 compression levels. Their core finding: **instruction compliance follows a U-curve — compliance is *worse* at medium compression (~27 words) than at extreme compression (~2 words).** The root cause: RLHF helpfulness training. When the model partially understands a degraded instruction, it triggers "let me help by making something up" — and gets it wrong. Removing helpfulness signals improved constraint compliance by **598%.**

Three additional papers provide mechanistic explanations:

- **[Lost in the Middle](https://arxiv.org/abs/2307.03172)** (Liu et al., 2023, TACL 2024): LLMs utilize information at the beginning and end of their context best, and information in the middle worst. Compaction progressively pushes early instructions from "beginning" to "middle."
- **[Gist Token-based Context Compression](https://aclanthology.org/2025.acl-long.241/)** (ACL 2025): Identifies three distinct failure modes — lost by the boundary, lost if surprise, lost along the way. Our `compact-counter` data exemplifies the third.
- **[Quantifying Laziness, Decoding Suboptimality, and Context Degradation in LLMs](https://arxiv.org/abs/2512.20662)** (2025): Documents "partial compliance" — models that follow the letter but not the spirit of degraded instructions. The `VERIFICATION_COMPLETE` instruction in Round 2 showed exactly this: the word survived, but its positional constraint didn't.

The academic evidence independently validates the U-curve observation. My pilot is underpowered by comparison — n=2, simulated degradation, single-model, regex-only scoring. But the field data (425 real compaction events across 459 sessions) provides something the lab studies don't: **evidence from production Claude Code workflows, not controlled prompts.**

---

## The Compaction Vicious Cycle

One phenomenon the academic literature doesn't cover — because it's an engineering artifact, not a model property — is the **compaction vicious cycle:**

```
Compaction → context prefix changes
    → Anthropic prompt cache hit rate drops to zero
    → per-call token cost doubles
    → session consumption accelerates
    → more compaction triggers
    → cache hit rate drops further
```

This is a positive feedback loop. Compaction doesn't just degrade instruction fidelity — it **accelerates its own frequency.** Each compaction makes the next compaction more likely by breaking the prompt cache. Long Claude Code sessions hit this silently: you notice the API costs climbing, but the root cause (compaction-induced cache miss) isn't surfaced.

(I've since set `autoCompactWindow` to 400K tokens — tuned for DeepSeek V4 Pro's 1M window — which gives more headroom before the cycle starts.)

---

## Practical Recommendations

If you use Claude Code for sessions longer than ~2 hours:

### 1. `/reset` after 20 compactions.

After 20 rounds of summary-on-summary compression, your original instructions are effectively gone. This isn't a matter of perseverance — the context is no longer reliable. `compact-counter` hooks in and warns you automatically at this threshold.

### 2. Design rules with model priors, not against them.

Round 1 demonstrated that instructions aligned with model defaults survive even extreme degradation. If you want Python code to use `snake_case` — **don't write that rule.** Python already defaults to `snake_case`. The rule does nothing but consume context. Instead, identify the rules that *fight* model defaults (e.g., "use camelCase in Python") and consider: can this constraint be enforced mechanically (L1 gate) rather than instructionally?

### 3. Prefer format constraints over semantic constraints for long sessions.

Round 2 data: format rules (which markup to use, what output structure) degraded to partial compliance but never to zero. Semantic rules (which language, what style) collapsed entirely at L12. For constraints that must survive long sessions, phrase them as format requirements.

### 4. Do not trust AI-generated compaction summaries.

After 10+ compactions, the summary was generated by a model whose context was itself degraded — a second-order information source. It will sound confident and factually precise. It may contain fabricated "fixes" and "conclusions." Verify against original outputs, not summaries.

---

## Limitations & Future Work

This pilot has clear limitations:

1. **Sample size:** n=2 per condition is insufficient for statistical testing. The L3 dip and L8 recovery in Round 2 could be noise.
2. **Simulated degradation:** Pre-written degradation chains are a proxy for real compaction output. Real compaction uses LLM-generated summaries, which have different degradation characteristics.
3. **Mechanical scoring:** Regex-based scoring produces false negatives (Round 1's apparent L3 failure on `snake_case` was likely a scoring artifact, not a real compliance drop).
4. **Single model:** DeepSeek V4 Pro's instruction-following behavior may not generalize to GPT-4o, Claude, or Gemini.

The full experiment — 20 instructions, 10 degradation levels, 3 repetitions, real compaction simulation, 3-blind LLM evaluation, cross-model comparison — would require approximately 600 API calls per model and 15–20 hours of analysis. I'm currently job-hunting (senior year approaching), so this stays on the backlog for now.

---

## Connection to Governance Architecture

In my [paper-validator](https://github.com/YuhaoLin2005/paper-validator) governance system, compaction count is one of 8 features in the L4 Drift Predictor, weighted at 12%. ≥5 compactions in 24 hours → maximum risk score.

These thresholds were set heuristically. The Round 2 data suggests the degradation cliff is at L8→L12, not L3→L5 — meaning the current ≥5 threshold may be too conservative, wasting audit resources on sessions that haven't actually degraded. Conversely, the format vs. semantic differential suggests the drift predictor should weigh instruction *type* separately, not count all instructions uniformly.

Governance systems need experimental data to calibrate their parameters. This pilot isn't enough for calibration, but it's enough to identify which parameters need calibrating.

---

## What This Means

I started with a feeling — "Claude gets worse the longer we talk" — and ended with field data from 459 sessions, a pilot experiment, and four academic papers that independently validated the core observation.

The U-curve is real. Instruction compliance under compaction is not monotonic. The sweet spot exists. The cliff exists. And the mechanism — RLHF helpfulness overriding degraded constraints — has been identified by researchers with far more rigorous methods than mine.

For the engineers and researchers building on top of LLMs: your system prompts and CLAUDE.md files are not permanent. Every compaction round erodes them. Design your constraints accordingly.

For everyone else: when Claude starts doing things you never asked for, two hours into a session — it's not you. It's not your prompting. **It's compaction. And now you know when to `/reset`.**

---

*📂 [compact-counter](https://github.com/YuhaoLin2005/compact-counter) — MIT-licensed compaction tracker for Claude Code*
*📂 [paper-validator](https://github.com/YuhaoLin2005/paper-validator) — 5-layer governance architecture with drift prediction*
*📖 References: [CDCT Benchmark](https://arxiv.org/abs/2512.17920) · [Lost in the Middle](https://arxiv.org/abs/2307.03172) · [Gist Token Failure Modes](https://aclanthology.org/2025.acl-long.241/) · [Quantifying LLM Degradation](https://arxiv.org/abs/2512.20662)*
*📖 Related posts: [I Pre-Registered a Hypothesis. 600 API Calls Later, the Data Killed It.](https://dev.to/yuhaolin2005/i-pre-registered-a-hypothesis-600-api-calls-later-the-data-killed-it-1aec) · [AI Agents Can't Self-Verify](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l)*
*👋 [GitHub](https://github.com/YuhaoLin2005) · [DEV.to](https://dev.to/yuhaolin2005)*

---

*This article is also available in [Chinese on 掘金](#) — a more narrative, less technical version focused on the engineering experience rather than the experimental methodology.*
