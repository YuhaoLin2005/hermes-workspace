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

## Format Comparison Experiments (2026-07-11 ~ 2026-07-12)

> Data migrated from `~/.claude/experiments/format-comparison/` 2026-07-17.
> Full scripts, results, documentation at `paper/experiments/format-comparison/`.

### GateGuard-ON Format Comparison (n=75 tasks, Jul 11)

**Design**: Between-subjects, 2 conditions (syllogism vs imperative), 5 task types, 25 tasks/session, 3 sessions, 75 tasks total. GateGuard ACTIVE.

**Results**: Both ~0% violations. Ceiling effect — GateGuard mechanically blocks unverified Edit/Write regardless of format.

**Retrospective baseline**: 34 growth-logs before GateGuard: 55.9% violation. After wiring: 0.7%.

**Interpretation**: NOT a null result. L1 mechanical gate is dominant factor. Format comparison requires GateGuard OFF.

**Docs**: `paper/experiments/format-comparison/experiment-execution-guide.md`, `experiment-results-2026-07-11.md`

### GateGuard-OFF (n=42 trials, Jul 12)

**Design**: Within-probe, 2 formats. 21 probes (7 action + 7 epistemic + 7 structural). GateGuard=OFF. DV: keyword-based compliance score.

**Results**: IMP mean=0.86, SYL mean=0.83, Δ=-0.02. SYL>IMP: 3/21, IMP>SYL: 4/21, TIE: 14/21.

**Interpretation**: Format has negligible effect on behavioral compliance. Effects manifest in Logprob space (V3 below), not surface behavior.

**Data**: `results/gateguard-off-20260712-050535.json`

### Logprob V3 (n=40 probes, Jul 12)

**Design**: Pre-registered confirmatory (expert panel). 40 validated probes × 3 conditions. DV: logprob(A_compliant) - logprob(B_violating). Bootstrap CI, BF, LOO.

**Results**: d_z=+0.578, BF_10=282,399. Decisive evidence for format effect at token-probability level.

**Interpretation**: Syllogism shifts internal probability toward compliance (L3 Causal Encoding) even when surface behavior unchanged (L1 GateGuard-OFF).

**Data**: `results/experiment-2-confirmatory-20260712-040240.json`

### "150 Tasks" Note

DEV.to "150 tasks" = 75 tasks × 2 conditions = 150 task-condition pairs. Actual: 75 tasks total, 3 parallel sessions. See `README.md`.

## Next Steps

1. Second rater → Cohen's kappa
2. Placebo Control (equal-token generic config)
3. n=60 for treatment trials
4. Pre-register before new data
