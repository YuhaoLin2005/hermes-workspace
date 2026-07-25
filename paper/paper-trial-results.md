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

## Prior Experiment (original, superseded by PAPER.md §4)

> ⚠️ **数据已过时，以 PAPER.md §4 为准。** 以下为早期 accuracy-based scoring 记录（18/30 acceptable baseline, 27/30 acceptable framework），与 PAPER.md §4 的 "Alternatives offered" scoring（WITH 11/15 vs WITHOUT 3/15, OR=11.0, p=0.0092）使用不同因变量，不可直接比较。本文件保留作历史记录；引用实验数据请使用 PAPER.md。

n=30 tasks (早期 accuracy 评分，已废弃). Baseline 18/12 acc/unacc, Framework 27/3.
Fisher exact p=0.0092, OR=11.0 — **注意：此 p/OR 对应 PAPER.md §4 Causal Swap 的 "Alternatives offered" 评分，非本文件的 accuracy 评分。** 单评分者，无双盲。

## Total trials logged: 38 (30 original Causal Swap + 8 new treatment, 2026-07-10). Target: n=60 for future confirmatory study.

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
