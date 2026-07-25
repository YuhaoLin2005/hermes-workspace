# My AI Compliance System Passed Every Check. Its Data Was 52× Wrong.

**I've spent 2 months building a 5-layer architecture to enforce AI agent rules. 31 DEV.to posts. 16 experiments. 3,862 readers on 掘金. Yesterday I asked my own expert panel to audit the whole thing. They found three problems. Then I found a fourth that was worse than all of them combined.**

---

## Quick Context (30 Seconds)

I'm an undergrad at FAFU. My thesis proposes the **Prose Barrier**: because an LLM's generation and self-evaluation share the same decoder (P(token|context;θ)), an AI agent cannot independently verify whether it followed its own rules. It can only *generate a claim* that it did.

The solution is a 5-layer architecture, each layer using a different "language":

| Layer | Language | Why |
|-------|----------|-----|
| L1 Mechanical Gate | Code — `os.path.getmtime()`, regex, exit codes | No NL, no model, no ambiguity |
| L2 Neural Gate | Numbers — raw logprob values from API | Measures constraint depth, not content |
| L3 Causal Encoding | Structured NL — syllogistic "if→then→because" | Matches attention routing patterns |
| L4 Drift Prediction | Statistical trends — 12 mechanical features | Catches degradation before failure |
| L0 Psychological Safety | NL — "you're safe to say I don't know" | Reduces fear-driven compliance theater |

L1 works on GPT, Claude, DeepSeek, Qwen — `os.path.getmtime()` doesn't care which model is running. This is not prompt engineering. It's configuration integrity architecture.

I've been building this in public. The previous posts:
- [AI Agents Can't Self-Verify](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) — Prose Barrier discovered, René Zander independently built the same thing
- [I Ran 150 Tasks](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) — 55.9%→0.7% violations with L1
- [I Pre-Registered a Hypothesis](https://dev.to/yuhaolin2005/i-pre-registered-a-hypothesis-600-api-calls-later-the-data-killed-it-1aec) — 600 API calls killed my prediction
- [Stop Using Generic AI Review](https://dev.to/yuhaolin2005/stop-using-generic-ai-review-build-your-own-board-of-experts-196n) — the expert panel that's about to audit itself

But 31 posts and 16 experiments later, I needed to know: **does any of this actually hold up?**

---

## The Audit

I asked three expert perspectives to review the entire system. Same codebase, same paper, zero mercy.

### Torvalds: "The architecture is right. The evidence isn't ready."

L1 reduced violations 55.9%→0.7%. That's the headline number. **But I scored every result myself.** κ = −0.14 — inter-rater reliability *worse than random chance*.

> *"Your hardest evidence sits on your weakest foundation. The cross-model claim has n=3. You need blind scoring before anyone should believe the behavioral numbers — including you."*

### Carmack: "You're confusing 'best explanation' with 'proof.'"

The Prose Barrier argument is structurally sound — P(token|context;θ) shared decoder makes independent self-verification impossible. TLOC (Startari et al., 2025) proved formally that transformers can't structurally verify internal rule compliance.

> *"But your experiments don't prove the Prose Barrier. They demonstrate effects best explained by it. Separate the architectural argument from the empirical evidence. One is logically grounded. The other is directionally consistent but underpowered."*

### Norman: "Five layers is overdesign — unless you tell people which ones they actually need."

> *"A solo dev needs L1. A team needs L1+L4. A researcher needs all five. Your paper was missing: who needs what, and why. The layers are a menu, not a prescription."*

---

## Then I Found Something Worse

All three critiques were about *future* improvements.

Then I checked the pipeline that runs my entire operation.

My knowledge base dashboard said:

```
juejin.total_reads: 74
juejin.total_likes: 8
```

I opened the 掘金 Creator Center. The real numbers:

```
文章阅读数: 3,862   — 52× higher
文章点赞数: 28     — 3.5× higher
文章展现数: 38,207 — never even tracked
文章收藏数: 22     — never tracked
粉丝数: 16         — marked as "?"
```

**My mechanical integrity checker had returned PASS.** Not a warning. Not an error. Clean pass.

It had checked:
- ✅ YAML formatting is valid
- ✅ Required field names exist
- ✅ `last_updated` date is within 7 days

It had NOT checked:
- ❌ Whether `total_reads: 74` matches reality (3,862)
- ❌ Whether the data source was browser-verified or self-reported
- ❌ Whether `?` fields had been unfilled for weeks

**This is the Prose Barrier operating on my own system.** My gate verified the *format* of the compliance report — YAML valid, dates fresh. It never verified the *content*. The dashboard said "all good" while carrying numbers that were 52× off from reality.

The system I built to prevent AI agents from lying about rule compliance... was itself lying about data compliance. **Not through malice. Through architecture.** Self-reported metrics without mechanical verification are just Prose Barrier in another domain.

---

## What Actually Changed (Not Just What I Claim Changed)

**1. Data synced with reality.** Browser-verified every dashboard number against the live 掘金 Creator Center. `total_reads` now reads 3,862, not 74.

**2. The checker now checks content, not just format.** Enhanced `_check_kb.py`:

```
Before (mechanical, but shallow):
  field exists? ✓
  YAML valid? ✓
  date fresh? ✓
  → PASS

After (mechanical + data-freshness):
  field exists? ✓
  YAML valid? ✓
  date fresh? ✓
  synced_at browser-verified? ← NEW: was data actually checked or self-reported?
  article count dashboard==index? ← NEW: cross-validation
  total_reads ≥ sum of individual reads? ← NEW: sanity check
  "?" fields >7d unresolved? ← NEW: gap detection
  dashboard age >3d? ← NEW: tightened from 7d
  → PASS or WARN (exit 2)
```

**3. Paper strengthened (this morning).**
- Introduction now separates "architectural argument" (logically grounded, TLOC-supported) from "empirical evidence" (behavioral effects, best-explained-by, underpowered)
- New Design Implications section: which layers for which users
- Carmack's "proof vs explanation" distinction is now explicit in the text

**4. The recursion is not lost on me.**

René Zander — the German developer who independently built mechanical gates — would look at this and say: *"This is exactly why I built skillgate. Verification format ≠ verification content."*

He's right. **My enhanced checker still has the same structural problem at one level up.** The `synced_at` field says `browser-verified: 2026-07-25`. Who verified that? I did. The checker checks that the word "browser-verified" appears in a comment. It doesn't re-run the browser verification. It trusts my self-report about whether I did the verification.

This is not a fixable problem at any finite number of meta-levels. Each verification layer can check the output of the layer below it, but the topmost layer's verification is always a self-report. This is the Prose Barrier — not a bug to patch, but a structural constraint to architect around.

**The architecture's answer: put the final verification outside the system.** Not in code. In humans.

---

## The Real Fix: Independent Blind Scoring

Every behavioral number in my paper — the 55.9%, the 0.7%, the d_z=+0.578 — was scored by me. I designed the experiments. I ran them. I rated the results. κ = −0.14.

**I cannot fix this with better code. I need humans who have never met me.**

| What | Details |
|------|---------|
| **Task** | Read 5 anonymized AI conversations. Score 5 rules each. 25 judgments total. |
| **Rules** | R1 Read-after-write, R2 Expert review, R3 Pre-action check, R4 Auto-deposit, R5 Self-audit |
| **Time** | 15-20 minutes |
| **Knowledge needed** | Zero AI expertise. Score what the AI DID, not what it SAID. |
| **Scoring guide** | [github.com/.../scoring-guide.md](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/blind-scoring/scoring-guide.md) (Chinese; English version this week) |
| **How to participate** | Comment below or DM me. I'll send you 5 transcripts + a score sheet. |

If 2+ independent raters agree (κ > 0.7), the paper's central behavioral claim goes from "exploratory, single-rater, unblinded" to "independently verified." If the blind scores contradict mine — I'll publish that too. κ = −0.14 is already public. It cannot get worse.

---

## Anticipating the Questions You'd Ask

**Mike Czerwinski:** *"Who checks the checker? Your enhanced `_check_kb.py` — is its own compliance verified, or is that also self-reported?"*

The enhanced checker is verified at the code level (it runs deterministically, its regex patterns match). But its *data inputs* still depend on manual browser verification. The `synced_at` field is a self-report about whether I actually opened the browser. The recursion is real. The only escape is external verification — which is exactly why blind scoring is P0, not P4.

**Dipankar Sarkar:** *"You fixed one dashboard. What's the base rate? How many other personal dashboards have the same self-report-vs-reality gap?"*

I don't know. But I suspect most manually-maintained dashboards rot silently — updated once, then trusted forever. The enhanced checker makes this detectable (gap >7d → warning), but it doesn't fix other people's dashboards. Making it general-purpose — so anyone with a markdown YAML dashboard can plug it in — is P4.

**René Zander:** *"This is convergent evolution. Your checker trusted a self-report. Mine did too. Can your checker work on MY system?"*

Not yet. Hardcoded to my KB structure. Generalizing to any markdown dashboard is the path to making this useful beyond one undergrad thesis. If you want to look at the code: [paper-validator/engine/](https://github.com/YuhaoLin2005/paper-validator).

**Alex Shevchenko:** *"How do I run this? Is it pip installable?"*

`python _check_kb.py` from the KB directory. No dependencies beyond Python 3.10 stdlib. Not yet pip-installable (P4). But the paper-validator CLI is: `python -m paper_validator claim --claim all --trials 30`.

**CodeKitHub:** *"What happens if 掘金 changes their UI? Does the browser verification break?"*

Yes — the browser verification is manual. I open the Creator Center, read the numbers, update the dashboard. No automated scraping. This is intentional: manual verification forces me to actually look. The checker verifies that *someone* looked, not that a script ran.

---

## What This Means

This project isn't about building a better prompt. It's about:

**Long-session AI agent rule degradation is a structural consequence of the shared-decoder architecture. The solution is layers that use the right language for each job — code where code works, numbers where numbers work, structured NL for what remains. And the final verification always lives outside the system: in other humans.**

GPT, Claude, DeepSeek, Qwen — every autoregressive transformer has this constraint. The architecture is universal. The evidence for *my specific implementation* needs blind scoring before it's more than a single biased rater's notebook.

---

## What's Next

| Priority | Task | Status |
|----------|------|--------|
| **P0** | Get 2+ independent blind raters → κ > 0.7 | 🔴 Recruiting — **that's this post** |
| P1 | Separate "proof" from "best explanation" in paper | ✅ Done (2026-07-25) |
| P2 | Design Implications: who needs which layer | ✅ Done (2026-07-25) |
| P3 | Cross-model expansion (3→6 models for Claim 9) | ⬜ Planned |
| P4 | Generalize _check_kb.py + pip install paper-validator | ⬜ Planned |

---

*Building an AI governance thesis in public, one post at a time. All 31 posts: [dev.to/yuhaolin2005](https://dev.to/yuhaolin2005). Code: [paper-validator](https://github.com/YuhaoLin2005/paper-validator). Experiments: [hermes-workspace](https://github.com/YuhaoLin2005/hermes-workspace).*

*The expert panel that found these problems is the same expert panel being evaluated. I am aware of the recursion. The recursion is the point.*