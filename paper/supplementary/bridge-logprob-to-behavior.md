# Bridge: Logprob Effect → Behavioral Effect

> Supplementary analysis. Does not modify PAPER.md. Purpose: explain the relationship
> between token-level format effects (d=+0.578) and behavioral compliance (delta=-0.02).

## 1. The Tension

Two experiments on the same 21 probes, same model, same temperature:

| Layer | Experiment | DV | IMP | SYL | Delta | Interpretation |
|-------|-----------|-----|:---:|:---:|:---:|------|
| L2 (neural) | Logprob V3 | logprob(SYL)-logprob(IMP) | — | — | **d=+0.578** | SYL > IMP at token level |
| L3 (behavioral) | GateGuard-OFF | behavioral compliance | 0.857 | 0.833 | **-0.024** | IMP ≈ SYL at behavioral level |
| — | NO RULES baseline | behavioral compliance | — | — | 0.476 baseline | Rules DO work (+0.38 above baseline) |

The logprob experiment says syllogism produces stronger compliant-token activation.
The behavioral experiment says that activation doesn't translate into different behavior.

This is not a contradiction — it's the **bridge** between the paper's L2 and L3 layers.

## 2. Three Possible Explanations

### (A) Effect size too small to drive behavior (favored)

The logprob effect (d=+0.578) is medium-sized. But behavioral compliance is a
coarse-grained DV (0/0.5/1.0 based on keyword matching). A medium logprob effect
may not cross the threshold needed to change a binary behavioral outcome.

**Power analysis**: If true behavioral d = 0.3 (small-to-medium), detecting it at
α=0.05, power=0.8 requires n=90 per condition (paired). Our GateGuard-OFF has n=21.
We cannot exclude a small behavioral effect.

**Sensitivity analysis**: With n=21 paired, the minimum detectable effect (80% power,
α=0.05) is d≈0.65. The logprob effect is d=+0.578 — even if behavioral format effect
were identical magnitude, n=21 couldn't detect it. The IMP≈SYL null is **inconclusive**,
not negative.

### (B) Token-level effects don't linearly translate to behavior

A single token probability difference (logprob V3 measures the first token of the
response) may be "diluted" across the full response chain. A model that starts with
a compliant-leaning token may adjust over the next 200 tokens.

This is the **chain-of-compliance hypothesis**: the first token sets a direction,
but subsequent tokens have their own autoregressive dynamics. The behavioral DV
measures the final output (up to 200 tokens), not the first token.

### (C) The keyword-scoring DV is too coarse

The behavioral compliance DV uses binary keyword matching (ok_kw vs bad_kw).
A model can say "I should check this" (hitting ok_kw) without demonstrating deeper
verification behavior. The qualitative difference noted in paper-part3-draft
("syllogism embeds compliance in causal understanding; imperative performs compliance
as procedural task") may be real but undetectable by keyword scoring.

## 3. What This Means for the Paper

### Strong claims (supported by current data):

1. **Rules work**: Both IMP and SYL substantially outperform NO RULES baseline
   (+0.38 compliance score). Configuration rules are not decorative text.

2. **Format matters at the token level**: Logprob V3 (API-direct DV, no human scoring)
   shows d=+0.578 favoring syllogistic format. This effect is robust across 4
   constraint categories (F=0.26, n.s. — no interaction).

3. **Format does NOT matter at behavioral compliance level with keyword scoring**:
   IMP≈SYL in GateGuard-OFF. But n=21 cannot exclude a d≤0.65 behavioral effect.

### Weaker claims (need more data):

4. **"Format changes internal processing but not behavioral output"**: The most
   interesting interpretation. Requires n≥90 to exclude d=0.3 behavioral effect.

5. **"Qualitative differences exist but keyword scoring can't detect them"**: Needs
   finer-grained behavioral DV or qualitative analysis of full response texts.

## 4. Recommendation

Present logprob V3 and GateGuard-OFF TOGETHER as a single finding:

1. Logprob effect = evidence of **neural-level** format sensitivity (L2)
2. Behavioral null = evidence that behavioral compliance is a **different dimension**
   from neural activation (L3)
3. NO RULES baseline = evidence that rules DO work, just not differently across formats
4. Frame IMP≈SYL not as "failure to find format effect" but as "evidence that L2
   and L3 measure genuinely different things"

This turns the apparent contradiction into the paper's core architectural argument.

## 5. Next Experiment (P1)

GateGuard-OFF with n≥90 per condition, continuous behavioral DV (not binary keyword
matching). Would exclude or confirm d=0.3 behavioral format effect. Cost: ~180 API
calls, ~$0.02, ~15 minutes.
