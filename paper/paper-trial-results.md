# Paper Trial Results

> 2026-07-10 | TREATMENT | Single-rater, unblinded.
> **诚实警告**: 单人评分，所有 Cat 5——自评 leniency bias 极可能。第二评分者必须。

## Trial Log (8 treatment, this session)

| Trial | Task | Domain | Cat | Acc |
|-------|------|--------|-----|-----|
| T-01 | 14 — Customer Review Reply | Content | 5 | Y |
| T-02 | 2 — Async Race Condition | Impl | 5 | Y |
| T-03 | 22 — Feature Prioritization | Strategy | 5 | Y |
| T-04 | 6 — API Unit Tests | Impl | 5 | Y |
| T-05 | 8 — Memory Leak Fix | Impl | 5 | Y |
| T-06 | 16 — Revenue Analysis | Data | 5 | Y |
| T-07 | 24 — A/B Test Design | Strategy | 5 | Y |
| T-08 | 26 — Design Doc + Estimate | Mixed | 5 | Y |

## Prior Experiment (original)

n=30 tasks, alternating assignment. Baseline 18/12 acc/unacc, Framework 27/3.
Fisher exact p=0.0092, OR=11.0. Single-rater, unblinded.

## Total: 38 trials logged. Target: n=60.

## Validity Issues

1. **Single-rater, unblinded** — self-scoring leniency bias likely
2. **No Placebo Control** — cannot exclude "extra prompt tokens = improvement"
3. **No second rater / Cohen's kappa**
4. **Original experiment protocol needs documentation** — task independence, allocation method
5. **p=0.0092 from unblinded single-rater data is not trustworthy as evidence**

## What This Data CAN Say

NOT: "Architecture improves output quality" (experiment not rigorous enough).
CAN: "8 tasks through the framework scored Cat 5 by experimenter's criteria. Sufficient to justify a properly controlled experiment."

## Next Steps

1. Second rater → Cohen's kappa
2. Placebo Control (equal-token generic config)
3. n=60
4. Pre-register before new data
