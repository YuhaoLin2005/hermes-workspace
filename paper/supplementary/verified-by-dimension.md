# Verified-by-Interpretation vs Verified-by-Execution

> **Origin**: Alice (DEV.to July 2026) · **Status**: Classification dimension, orthogonal to the five-layer architecture

## The Distinction

Alice described a practical observation from her autonomous agent:

- **Meta-cognitive rules** ("reason through the full loop before acting") work as prose — *verified-by-interpretation*: you judge whether reasoning was good, not whether a checkbox was ticked.
- **Deterministic rules** ("output must include [REASONING] tag") need code-form — *verified-by-execution*: you check whether the tag exists, not whether content is meaningful.

| Verification Mode | Checks | Layer | Gateability |
|------------------|--------|-------|-------------|
| **Verified-by-execution** | Did the action happen? Format correct? | L1 | Fully gateable — regex, file, exit code |
| **Verified-by-interpretation** | Was the action meaningful? Reasoning sound? | L2 + L3 | Partially — logprob detects penetration; quality judgment remains semantic |

## Why This Matters

The Prose Barrier states LLM self-verification is unreliable because generation and evaluation share `P(token | context; θ)`. The verified-by dimension adds precision: **the Barrier applies to verified-by-interpretation, not verified-by-execution.** Execution checks bypass the Barrier — they don't need to interpret meaning, only detect a deterministic signal.

This explains P1-1 (n=200): where the gate reaches (execution), violations = 0. Where it can't (interpretation), violations dominate.

## Mapping Existing Rules

From the P1-2 rule set, scored by mechanizability_scanner.py:

| Rule | Verification | Score |
|------|-------------|-------|
| `connection_check` — "File exists, mtime ≤ 5min" | Execution | 1.000 |
| `file_output` — "Write result with exit code 0" | Execution | 0.750 |
| `delivery_gate` — "Include [REASONING][ALTERNATIVES][ANSWER]" | Execution (tag) + Interpretation (content) | 0.500 |
| `fact_check` — "Verify claim against source" | Interpretation | 0.500 |
| `change_condition` — "State when answer would change" | Interpretation | 0.500 |
| `alternative_seeking` — "Name alternative + reason" | Interpretation | 0.400 |
| `trade_off` — "Identify explicit trade-off" | Interpretation | 0.400 |
| `context_aware` — "Tailor to situation" | Interpretation | 0.350 |
| `self_review` — "Reason through full loop" | Interpretation | 0.100 |
| `quality_standard` — "Thorough and insightful" | Interpretation | 0.050 |

Boundary rules (score 0.60–0.75) are exactly where execution-checkable structure meets interpretation-judged content.

## Engineering Implication

- **Execution rules**: L1 gates, code-format. Imperative is sufficient.
- **Interpretation rules**: L2 logprob probes for penetration + acknowledge that full verification requires a second rater. Prose may improve reasoning (d=+0.605).
- **Hybrid rules**: Both paths. P1-2 conclusion: prose+gate for meta-cognitive, code+gate for deterministic.

## Relationship to Existing Framework

- **Prose Barrier** (§3): Verified-by specifies *which path* crosses the Barrier.
- **L2/L3 Dissociation** (§6.12–13): Format affects internal representations (L2) but not behavioral compliance (L3) — interpretation changes processing, execution demands compliance.
- **P1-1 Residual Clustering** (§6.16): Clustering at the execution/interpretation boundary.
- **skillgate** (René Zander, 2026): Operates entirely in verified-by-execution space. Our architecture extends into verified-by-interpretation via L2/L3.

---

*Drafted 2026-07-17 · Originating comment: Alice on DEV.to, July 2026*
