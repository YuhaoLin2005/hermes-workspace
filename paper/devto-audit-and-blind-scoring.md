# I Discovered AI Agents Can't Self-Verify. The Real Problem Is Much Bigger.

**Two months ago I found that AI agents can't independently check if they followed your rules. I built mechanical gates to work around it. They worked — 55.9% violations down to 0.7%. But last week I realized I'd been solving the wrong problem.**

The real problem isn't verification.

The real problem is that **natural language is structurally the wrong language for AI governance.**

---

## Here's What I Mean

Right now, every layer of AI governance speaks the same language:

```
Human writes NL rules → Model reads NL → Model generates behavior
Human writes NL checks → Model reads NL → Model generates "yes I followed the rules"
```

But every autoregressive transformer — GPT, Claude, DeepSeek, Qwen — generates text and evaluates text through the exact same decoder: `P(token | context; θ)`. When you ask "did you follow rule X?", the model runs the same forward pass it uses to write poetry. It can't step outside itself to verify. It can only *generate a claim* that it complied.

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

**The rule-compliance DPO pipeline has run on 82.4K causal preference pairs** — Qwen2.5-1.5B, QLoRA on RTX 3060 (6GB), 38 steps, 1 epoch. The results: loss ↓, but behavioral metrics caught something the loss curve didn't — the model collapsed into digit-repeating on certain probes. Behavioral drift detection matters more than training loss. A broader rule-compliance preference dataset (building on these results) is gated on blind-scored behavioral data (P0).

**This path bypasses NL entirely.** You're not telling the model to change. You're changing what the model *is*. The "language" here is the geometry of embedding space, shifted by behavioral data.

---

## This Changes Everything About "Related Work"

When people hear "AI rule compliance," they think: prompt engineering. Better system prompts. Chain-of-thought. Constitutional AI self-critique.

That's the wrong lineage. The actual intellectual tradition this builds on:

- **Bender, Gebru, McMillan-Major & Shmitchell (2021)** — *On the Dangers of Stochastic Parrots*: LMs distribute, they don't understand. The verification problem is structural.
- **Bender & Koller (2020)** — *Climbing towards NLU*: the octopus thought experiment. Form alone doesn't produce understanding.
- **Kambhampati (2024)** — *LLM-Modulo*: LLMs need external verifiers. Self-verification is architecturally impossible.
- **Bai et al. (2022)** — *Constitutional AI*: self-critique reduces harm, but the critique comes from the same model being critiqued. The ceiling is baked in.
- **Startari (2025)** — *TLOC*: structural theorem arguing that transformers cannot verify internal rule compliance. Mathematical ceiling.

This isn't a prompt engineering paper. It's an architecture paper. The question isn't "what's the best way to tell the model to behave?" It's "what are the structural limits of transformer verification, and what architecture works around them at each layer?"

---

## Quick Context (For Those Just Joining)

I'm an undergrad at FAFU (福建农林大学). Building this in public:

- [AI Agents Can't Self-Verify](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) — Prose Barrier discovery
- [I Ran 150 Tasks](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) — 55.9%→0.7% with mechanical gates
- [I Pre-Registered a Hypothesis](https://dev.to/yuhaolin2005/i-pre-registered-a-hypothesis-600-api-calls-later-the-data-killed-it-1aec) — 600 API calls killed my prediction, taught me more than confirmation would have
- [Stop Using Generic AI Review](https://dev.to/yuhaolin2005/stop-using-generic-ai-review-build-your-own-board-of-experts-196n) — build your own expert panel

31 posts. 16 experiments. One thesis. [All on dev.to/yuhaolin2005](https://dev.to/yuhaolin2005).

---

## Two Things I Need Help With

### 1. Blind Scoring (P0 — blocks everything)

Every behavioral number in my paper — the 55.9%, the 0.7% — was scored by me. I designed the experiments. I ran them. I rated the results.

**κ = 0.00.** That's inter-rater reliability *exactly at chance.* Not because the raters disagreed — they agreed 87.5% of the time. But when one rater (me) scores every agent the same way, Cohen's kappa is mathematically constrained to zero regardless of actual consistency. This is the "kappa paradox" — high raw agreement, zero kappa. It means the scoring protocol was never actually tested. The architecture's answer: verification lives outside the system. In independent human raters.

**→ [Click here: Blind Scoring Package](https://github.com/YuhaoLin2005/hermes-workspace/tree/main/paper/blind-scoring)**

You'll find:
- A 5-minute scoring guide (what to look for, with examples)
- 5 anonymized AI conversation transcripts
- A score table template — copy, fill, send back

**Zero AI expertise needed.** You're scoring what the AI *did*, not what it *said*. If 2+ raters agree (κ > 0.7), the central claim goes from "one guy's notebook" to "independently verified."

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
| **P0** | Blind scoring: 2+ raters → κ > 0.7 | 🔴 [Help here](https://github.com/YuhaoLin2005/hermes-workspace/tree/main/paper/blind-scoring) |
| P1 | Separate "proof" from "best explanation" in paper | ✅ Done |
| P2 | Design Implications: who needs which layer | ✅ Done |
| **P3** | Cross-model: need Claude/GPT/Gemini API access | 🟡 [Help here](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/experiment/logprob-v3/cross_model_validation.py) |
| P4 | Generalize checker + pip install | ⬜ Planned |

---

*Building an AI governance thesis in public. All code: [paper-validator](https://github.com/YuhaoLin2005/paper-validator). All experiments: [hermes-workspace](https://github.com/YuhaoLin2005/hermes-workspace).*

*The architecture is universal. The evidence needs your eyes.*
