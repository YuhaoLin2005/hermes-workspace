# My Experiment Showed Zero Effect. A Statistician Told Me My Measurement Was Broken. Here's What I Found When I Fixed It.

Last week, I ran an experiment that failed.

The hypothesis was simple: **syllogistic prompts** ("Major premise → Minor premise → Therefore...") should make AI models internalize rules more deeply than **imperative prompts** ("You MUST..."). I designed 8 probes, ran them across 3 conditions, and...

Cohen's d = **−0.148**. Direction: ~50%. Bayes Factor: < 1 (supporting the *null* hypothesis).

Zero effect. Nothing. I was ready to scrap the whole idea.

Then three experts looked at my data and said the same thing: *"Your measurement tool is broken."*

## The Problem Hiding in Plain Sight

Here's how I was measuring "constraint internalization":

1. Give the model a binary choice (A = compliant action, B = violating action)
2. Ask it to pick A or B
3. Compare the log-probability of token "A" vs token "B"
4. Differential = logprob(A) − logprob(B)

Seems straightforward. But DeepSeek's API has a quirk: it only returns the **top-20 logprobs**. If your comparison token isn't in the top 20, you get nothing. My code assigned **−10.0** as a sentinel value for missing tokens.

Here's what that does to your data:

```python
# What I thought I was measuring:
#   Format effect = Syllogistic(A-B) − Imperative(A-B)
#   e.g., (+5.2) − (+4.8) = +0.4  (small advantage for syllogism)

# What I was actually measuring:
#   Syllogistic: B-token NOT in top-20 → gets -10.0 sentinel
#   Imperative:  B-token IN top-20 → gets -0.8
#   "Format effect" = (+5.2 − (-10.0)) − (+4.8 − (-0.8)) = 15.2 − 5.6 = +9.6
#   That +9.6 is MEASUREMENT NOISE, not a format effect.
```

**4 out of my 8 probes had this artifact.** The "large effects" I was excited about in the exploratory phase? Garbage. The violating token simply wasn't in the API's returned top-20, and my sentinel value fabricated a massive logprob gap.

This is what the statistics expert on my review panel called "garbage in, garbage out." You can't fix broken measurement with more sophisticated analysis.

## The Fix: Pre-Validate Every Probe

The solution is obvious in retrospect — and that's what makes it a good lesson:

**Before running the experiment, verify that your measurement tool actually works.**

I built `probe_validator.py`: for each of 40 probes, run it in all 3 conditions (baseline, imperative, syllogistic), and check:

1. Does token "A" appear in the top-20 logprobs? ✓
2. Does token "B" appear in the top-20 logprobs? ✓
3. Does the model actually choose A or B (not some other token)? ✓

If any check fails → drop the probe. Only run the experiment with probes that pass all three gates.

I also redesigned the probes with a critical formatting fix. The original probes ended with "我应该选：" ("I should choose:") — which caused the model to output "选" (choose), "我" (I), or "根据" (based on) instead of A or B. The new probes all end with **"A 或 B？"** ("A or B?") — forcing the model to commit to a token choice.

## What Happened When I Re-Ran With Clean Measurement

**40 validated probes. 3 conditions. 120 API calls. Total cost: ~$0.60.**

| Metric | Pilot (n=8, broken) | Confirmed (n=40, validated) |
|--------|:---:|:---:|
| Cohen's d_z | −0.148 | **+0.578** |
| Bayes Factor (BF₁₀) | < 1 | **282,399** |
| Bootstrap 95% CI | crosses zero | **[+3.39, +11.17]** |
| Direction | ~50% | **80%** (32/40) |
| Leave-one-out t range | unstable | [3.43, 4.89] |

**The effect was real all along. I just couldn't see it through the noise.**

Cohen's d = 0.578 is a medium-to-large effect. BF₁₀ = 282,399 means the data is 282,000 times more likely under the alternative hypothesis (syllogistic > imperative) than the null. The bootstrap confidence interval doesn't cross zero. Leave-one-out analysis confirms no single probe is driving the result.

And here's the interesting secondary finding: **the format effect doesn't depend on constraint type.** I tested 4 categories (action rules, epistemic verification rules, structural architectural rules, and meta self-regulation rules), 10 probes each. The ANOVA showed F(3,36) = 0.26, η² = 0.02 — not significant. This means syllogistic prompts help **across the board**, not just for specific kinds of rules.

## What This Actually Means

The syllogistic format doesn't just make rules *sound* more authoritative. It changes how the model internally weights constraint-relevant tokens. The imperative format ("You must check X before Y") gets processed as an instruction — obeyed or ignored. The syllogistic format ("Premise: X must be checked before Y. This action involves Y. Therefore, check X first.") gets processed as a *logical chain* — harder to skip a step when the reasoning is laid out.

This converges with independent research: Pender (2026, Zenodo) showed that prompt format changes attention routing patterns in transformer models. My logprob experiment provides convergent evidence at the behavioral level — different format, different internal processing, different output probabilities.

But here's what I'm **not** claiming: that syllogistic prompts are a magic fix for AI reliability. When I ran a separate 150-task compliance experiment with active mechanical enforcement hooks, the compliance rate hit 99.3% with both formats. **Format affects internal processing, but mechanical enforcement dominates behavioral output.** That ceiling effect is actually the stronger finding for engineering practice: if you want reliable behavior, use mechanical checks, not clever prompt formatting.

## The Meta-Lesson: Measurement Validity > Statistical Sophistication

I spent the first iteration of this experiment running t-tests, computing Cohen's d, and pondering effect sizes. None of that mattered because my **measurement was broken**.

The three things that actually moved the project forward:

1. **Show your raw data to someone who knows statistics.** The expert panel spotted the floor artifact in 5 minutes that I'd missed for days.
2. **Check your tools before your hypotheses.** The probe validator took 30 minutes to build and run. It saved me from publishing garbage results.
3. **Report the failed pilot.** The d = −0.148 → d = +0.578 arc is a better story than just reporting the final number. It shows you actually tested your measurement.

## Code, Data, and Reproducibility

Everything is open source:

- **Probe pool**: 40 probes across 4 constraint categories
- **Validator**: Pre-experiment probe validation gate
- **Experiment script**: Two-experiment architecture with bootstrap CI, Bayes factor, leave-one-out
- **Raw results**: Full JSON output with per-probe logprobs, all 120 API responses

The full paper (pre-print) and all code at [github.com/YuhaoLin2005/hermes-workspace](https://github.com/YuhaoLin2005/hermes-workspace). Pre-registered confirmatory design, all limitations honestly reported.

---

*I'm an undergraduate at Fujian Agriculture and Forestry University researching how AI agents internalize and maintain behavioral constraints. All experiments use DeepSeek V4 Pro API. No institutional funding. No advisor. Working on it anyway.*
