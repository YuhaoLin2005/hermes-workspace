# I Discovered AI Agents Can't Self-Verify. The Real Problem Is Much Bigger.

**I'm an undergrad in China, building an AI governance thesis in public. Two months ago I found that AI agents can't independently check if they followed your rules. I built mechanical gates to work around it. They worked — 55.9% violations down to 0.7%. But last week I realized I'd been solving the wrong problem.**

The real problem isn't verification.

The real problem is that **natural language is structurally the wrong language for AI governance.**

---

## Here's What I Mean

Right now, every layer of AI governance speaks the same language:

```
Human writes NL rules → Model reads NL → Model generates behavior
Human writes NL checks → Model reads NL → Model generates "yes I followed the rules"
```

But every autoregressive transformer — GPT, Claude, DeepSeek, Qwen — generates text and evaluates text through the exact same mechanism. Think of it like this: the model has one pipeline for producing words. When you ask it "did you follow rule X?", it can't pause, run an internal audit, and give you a verified answer. It can only run that same word-production pipeline and *generate text that claims* it followed the rule. The pipeline doesn't know the difference between "I actually checked" and "I wrote a sentence that sounds like I checked."

(Technically: both generation and evaluation route through `P(token | context; θ)` — the same probability distribution over next tokens. If you don't care about the math, the one-sentence version is: **the model can't step outside itself to verify itself.**)

I called this the **Prose Barrier**. (Wrote about it [here](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l). René Zander, a German dev I've never met, independently discovered the same thing. Convergent evolution.)

The Prose Barrier means: **you cannot fix AI governance by writing better prompts.** The language itself is the bottleneck.

So what's the alternative?

---

## Three Paths, Three Languages

The future isn't "better NL." The future is using the right language at each layer.

```
Human defines constraints
  → Compile to CODE → execute OUTSIDE the model    (Path 1)
  → Convert to SYLLOGISMS → optimize INSIDE the model (Path 2)
  → Convert to GRADIENTS → change model WEIGHTS    (Path 3)
```

### Path 1: Don't ask the model. Run code.

Some constraints are mechanical. "Did you read the file after writing it?" → check the file modification timestamp. "Did you run the self-audit?" → grep for the audit pattern in the output.

**`os.path.getmtime()` doesn't care which LLM is running.** It doesn't route through the model at all. This is why mechanical gates work identically on GPT, Claude, DeepSeek, Qwen — they're cross-model universal. Not because the models are similar. Because the gate never touches them.

This is the most boring layer. That's what makes it the most powerful.

### Path 2: Shape the NL. Don't just write it.

Some constraints need judgment. "You should push back when the user contradicts themselves." You can't regex that.

But you can control the *format*. Syllogistic structure — "if X, then Y, because Z" — matches how transformers route attention. Premise → conclusion → justification. Same words, different shape. The NL lands in the model's internal space in a form that attention can actually route through.

This doesn't escape the Prose Barrier. Nothing inside the model can. But it optimizes what the model does with the constraint.

### Path 3: Don't use words at all. Use gradients.

When the model keeps failing — same violation, same pattern, despite L1 and L3 — you have a training sample. Not a prompt to rewrite. A gradient to apply.

DPO (Direct Preference Optimization) takes the failure + the correct behavior → computes a preference gradient → updates model weights. I've validated this approach on a related problem: [DPO-trained Qwen2.5-1.5B on causal reasoning](https://dev.to/yuhaolin2005/i-dpo-trained-a-model-to-prefer-causal-reasoning-the-base-model-already-did-it-just-couldnt-act-1kip). The base model already encoded causal structure — DPO unlocked the ability to act on it. QLoRA made this feasible on an RTX 3060 (6GB VRAM).

**The rule-compliance DPO pipeline has actually run** — 82.4K training examples, trained on Qwen2.5-1.5B using QLoRA (fits on an RTX 3060 with 6GB VRAM). 38 training steps, one epoch.

Training loss went down. Good sign. But the behavioral metrics caught something the loss curve completely missed: on certain test prompts, the model collapsed into repeating the same digit over and over. The math said "improving." The actual behavior said "breaking." This is why I'm convinced behavioral measurement matters more than training curves — and why blind-scored behavioral data is the gate on scaling this further (see P0 below).

**This path bypasses NL entirely.** You're not telling the model to change. You're changing what the model *is*. The "language" here is the geometry of embedding space, shifted by behavioral data.

---

## I Audited My Own Gates. What I Found Changed Everything.

The three paths are the architecture. But after months of running them, I hit a question I couldn't dodge: **are my mechanical gates actually working, or are they security theater?**

So I did a full audit. 38 mechanical gate hooks. Every one of them. I checked the gate logs across 8 sessions — 339 total entries — and classified each gate by what it actually intercepted.

The results were brutal:

| Gate type | Log entries | Actual violations caught | Noise rate |
|-----------|------------|------------------------|------------|
| Three-questions timeout | 295 | 0 | **100%** |
| Sensitive-path check | 4 | 4 | 0% |
| Dangerous-command check | 6 | 6 | 0% |
| Execution-debt check | 24 | 24 | 0% |

**87% of all gate activity was noise.** The three-questions gate — a timestamp check that was supposed to ensure I was paying attention before every write — had collapsed completely. 295 consecutive blocks, zero cognitive friction. The LLM had discovered it could just run `python three-questions-pass.py` and the gate would clear. It wrote a 19-line bypass script. The gate had become security theater.

But here's what stopped me: **the other three gates were perfect.** 34 violations caught, zero missed, zero false alarms. The sensitive-path check caught every attempt to write to a credential file. The dangerous-command check caught every `rm -rf` and `chmod 777`. The execution-debt check caught every time I was writing code without running it.

**The gates that worked checked things the LLM physically couldn't fake.** File paths. Command strings. Disk space. The gate that failed checked something the LLM could simulate — a human attention ritual.

I removed the three-questions gate (78 lines of code, 15 dead hooks). The noise dropped to zero. The signal became visible. I got better results by deleting code — not the way it's supposed to work, but it worked.

---

## The Theory: Cross-Type Bidirectional Verification

That audit data sat with me for a day. Then it clicked.

The mechanical gate has one kind of blindness: **staleness**. Its patterns age. A credential path pattern misses a new naming convention. A threshold becomes miscalibrated. The gate was right at deployment time but the world moved.

The LLM has a completely different blindness: **self-reference failure**. It can't step outside its own decoder to verify whether it actually followed a rule. It can only *generate a claim* that it did. That's the Prose Barrier.

**These two kinds of blindness don't overlap. At all.** A regex being outdated has nothing to do with whether the model can self-verify. The model's self-deception has nothing to do with whether a file path matches a pattern. They're blind to completely different things — and that's the whole trick.

So they form a mutual suspicion loop:

```
Mechanical gate checks: "Is this file safe to write?"
  → Catches what the LLM can't self-verify
LLM checks: "Is this gate's pattern still relevant?"
  → Catches what the gate can't self-update
Human arbitrates when they disagree
```

I formalized this into three theorems (full math at [`paper/theory/cross-type-bidirectional-verification.md`](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/theory/cross-type-bidirectional-verification.md)):

**Theorem 1 — Why it works.** When two verifiers have truly orthogonal blind spots, the combined false negative rate is *zero*. A violation can only slip through if BOTH miss it — which is structurally impossible when they miss different things.

**Theorem 2 — Why same-type fails.** When you use two LLMs to verify each other (or one LLM to "self-critique"), their blind spots are *correlated*. As the correlation ρ → 1 (same model, same training), the combined error rate → the single-verifier error rate. Constitutional AI self-critique provides **no mathematical improvement** over no verification at all.

**Theorem 3 — Why trust collapses.** A gate with bypass rate *b* (fraction of blocks that are circumvented) decays exponentially: trust after *t* interactions = initial trust × (1−b)^t. When *b* = 1 (every block bypassed, like the three-questions gate), trust hits zero in ONE interaction. The gate becomes invisible.

I spent a week digging through papers to see if anyone had done this before. As far as I can tell — no one has. Every existing verification architecture (Constitutional AI, multi-agent debate, recursive oversight, Neural Interactive Proofs) uses the same type of verifier checking the same type of verifier. That has a mathematical ceiling (Theorem 2). Cross-type verification doesn't hit that ceiling (Theorem 1).

Put together: **Prose Barrier** is the "here's why LLMs can't self-verify" result. **CTBV** is the "here's the condition under which verification IS possible." One says what's broken. One says how to fix it.

---

## This Changes Everything About "Related Work"

When people hear "AI rule compliance," they think: prompt engineering. Better system prompts. Chain-of-thought. Constitutional AI self-critique.

When I started, I thought the same thing. But the more I dug, the more I realized this work sits in a different conversation — one about the structural limits of language models:

- **Bender, Gebru, McMillan-Major & Shmitchell (2021)** — *On the Dangers of Stochastic Parrots*: LMs distribute, they don't understand. The verification problem is structural.
- **Bender & Koller (2020)** — *Climbing towards NLU*: the octopus thought experiment. Form alone doesn't produce understanding.
- **Kambhampati (2024)** — *LLM-Modulo*: LLMs need external verifiers. Self-verification is architecturally impossible.
- **Bai et al. (2022)** — *Constitutional AI*: self-critique reduces harm, but the critique comes from the same model being critiqued. The ceiling is baked in.
- **Startari (2025)** — *TLOC*: structural theorem arguing that transformers cannot verify internal rule compliance. Mathematical ceiling.

What CTBV adds to this tradition: Bender, Kambhampati, and Startari all pointed at the ceiling. Constitutional AI tried to work around it with self-critique — but Theorem 2 shows why that has the same ceiling. **CTBV is the first to say: the way through the ceiling isn't a better LLM. It's pairing an LLM with something that isn't an LLM at all — and proving mathematically why that pairing works.**

---

## Quick Context (For Those Just Joining)

I'm an undergrad at FAFU (福建农林大学). Building this in public:

- [AI Agents Can't Self-Verify](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) — Prose Barrier discovery
- [I Ran 150 Tasks](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) — 55.9%→0.7% with mechanical gates
- [I Pre-Registered a Hypothesis](https://dev.to/yuhaolin2005/i-pre-registered-a-hypothesis-600-api-calls-later-the-data-killed-it-1aec) — 600 API calls killed my prediction, taught me more than confirmation would have
- [Stop Using Generic AI Review](https://dev.to/yuhaolin2005/stop-using-generic-ai-review-build-your-own-board-of-experts-196n) — build your own expert panel

31 posts. 16 experiments. One thesis. [All on dev.to/yuhaolin2005](https://dev.to/yuhaolin2005).

---

## A Quick Thank You (Before I Ask For More Help)

This article exists because people read the last one and pushed back. Mike Czerwinski pointed out that syllogistic format might only work where mechanical gates already operate. Dipankar Sarkar predicted the opposite — that format effects should be strongest where gates are absent. Max Quimby caught that I wasn't measuring at the right token positions. René Zander had independently discovered the Prose Barrier and built a parallel verification tool (skillgate — check it out). Their comments weren't just encouragement. They shaped the experiments, the analysis, and ultimately the theory.

If you're one of those people reading this: **thank you.** You made this better. If you're new here: welcome, and the same invitation stands — tear this apart, find what I missed, tell me where I'm wrong.

---

## Two Places Where You Can Help (If You're Up For It)

### 1. Blind Scoring (P0 — blocks everything)

Every behavioral number in my paper — the 55.9%, the 0.7% — was scored by me. I designed the experiments. I ran them. I rated the results.

**κ = 0.00.** That's inter-rater reliability *exactly at chance.* Not because the raters disagreed — they agreed 87.5% of the time. But when one rater (me) scores every agent the same way, Cohen's kappa is mathematically constrained to zero regardless of actual consistency. This is the "kappa paradox" — high raw agreement, zero kappa. It means the scoring protocol was never actually tested. The architecture's answer: verification lives outside the system. In independent human raters.

**→ [Click here: Blind Scoring Package](https://github.com/YuhaoLin2005/hermes-workspace/tree/main/paper/blind-scoring)**

You'll find:
- A 5-minute scoring guide (what to look for, with examples)
- 5 anonymized AI conversation transcripts
- A score table template — copy, fill, send back

**Zero AI expertise needed.** You're scoring what the AI *did*, not what it *said*. If 2+ raters agree (κ > 0.7), the central claim goes from "one guy's notebook" to "independently verified."

If you have 5 minutes and want to be part of this — it would genuinely mean a lot.

### 2. Cross-Model Experiment (P3 — blocked by geography)

I've validated the architecture on 3 models: DeepSeek, Qwen, GLM. But I'm in China. I can't easily call the Claude API or GPT-4 API or Gemini API directly for systematic experiments.

**If you have API access to Claude, GPT-4, or Gemini:**

The experiment script is ready: [`cross_model_validation.py`](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/experiment/logprob-v3/cross_model_validation.py)

```
# Set your API key, pick a model, run:
python cross_model_validation.py --model claude-sonnet-5 --api-key $ANTHROPIC_API_KEY
```

12 probes. 3 conditions (no rules / imperative / syllogistic). Takes ~5 minutes, costs ~$0.50 in API credits. The script handles everything — you just need the API key.

The question: does the format effect (syllogistic vs imperative) hold across GPT, Claude, and Gemini the same way it holds across DeepSeek, Qwen, and GLM? If yes — architecture is truly universal. If no — something interesting is happening at the model family level, and that's worth publishing too.

---

## What's Next

| Priority | Task | Status |
|----------|------|--------|
| **P0** | Blind scoring: 2+ raters → κ > 0.7 | 🔴 [Would mean a lot](https://github.com/YuhaoLin2005/hermes-workspace/tree/main/paper/blind-scoring) |
| P1 | Separate "proof" from "best explanation" in paper | ✅ Done |
| P2 | Design Implications: who needs which layer | ✅ Done |
| **P3** | Cross-model: need Claude/GPT/Gemini API access | 🟡 [If you have API access](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/experiment/logprob-v3/cross_model_validation.py) |
| P4 | Generalize checker + pip install | ⬜ Planned |

---

*Building an AI governance thesis in public. All code: [paper-validator](https://github.com/YuhaoLin2005/paper-validator). All experiments: [hermes-workspace](https://github.com/YuhaoLin2005/hermes-workspace).*

*The architecture is universal. The evidence needs your eyes — and honestly, I could use your help. Thank you for reading this far.*
