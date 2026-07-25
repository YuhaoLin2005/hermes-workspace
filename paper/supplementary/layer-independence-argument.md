# Layer Independence Argument

> Supplementary analysis. Hickey-style decomplection: does each layer measure
> something the others can't? Does not modify PAPER.md.

## The Test

For each layer: **"If this layer were removed, could another layer detect
the same failure mode?"** Yes → layers may not be independent. No → genuinely
distinct dimension.

## L0: Psychological Safety

**What**: Pre-processes generation — tells model "not knowing" is valid output,
reducing RLHF reward asymmetry for uncertainty.

**If removed**: Model prefers confident wrong answers over uncertain right answers.

**Can other layers detect L0 failures?**
- L1: ❌ File system can't verify claim truth
- L2: ⚠️ Logprob probes could measure uncertainty calibration (needs specific probes)
- L3: ⚠️ Output accuracy measurement, but can't distinguish "uncertain+right" from "confident+right"
- L4: ❌ Aggregate trends, not per-output

**Verdict**: **Partially independent.** L0 solves a problem (RLHF confidence bias)
that L1-L4 aren't designed to address. But measurement overlaps with L2.

**Strengthening**: Add L0-specific metric: "confident incorrect rate" — proportion
of outputs where model confidence (logprob) is high but answer is wrong.

## L1: Mechanical Gate

**What**: File-system checks (mtime, exit codes, regex, JSON schema). Operates
entirely outside Prose Barrier.

**If removed**: Configuration drift undetected. Hook wiring failures, stale files,
missing scripts become invisible.

**Can other layers detect L1 failures?**
- L0: ❌ Generation-level, not file-system
- L2: ❌ Constraint echo needs content, can't check file mtime
- L3: ❌ Format effects require rules ACTIVE — L1 ensures rules ARE active
- L4: ⚠️ Might detect behavioral degradation trend, but can't pinpoint cause

**Verdict**: **Fully independent.** Only layer operating outside Prose Barrier.
No other layer checks file-system state.

**Evidence**: GateGuard ON vs OFF comparison. L1 ON: 99.3% compliance. L1 OFF:
~85% (IMP/SYL, rules present but no mechanical enforcement). L1 contribution
is quantifiable and non-redundant.

## L2: Neural Gate

**What**: Detects whether constraints have "penetrated" generation — measured via
logprob differentials (constrained vs baseline token distributions).

**If removed**: Can't detect whether a rule is actively processed by the model
(vs ignored/suppressed by competing context).

**Can other layers detect L2 failures?**
- L0: ❌ Different mechanism
- L1: ❌ Only checks whether rule FILE exists+is wired
- L3: ⚠️ Behavioral compliance detects whether model FOLLOWED rule, not whether
  model ACTIVELY PROCESSED it
- L4: ❌ Trend level, not per-rule

**Verdict**: **Independent from L1, partially overlaps L3.** L2 = rule PENETRATION
(did constraint enter processing?). L3 = rule EFFECT (did constraint change behavior?).

**Evidence**: Logprob V3 (SYL>IMP, d=+0.578) vs GateGuard-OFF (IMP≈SYL, delta=-0.024).
If L2 and L3 measured the same thing, they'd correlate. They don't.

## L3: Causal Encoding

**What**: Changes FORMAT of rules (imperative→syllogistic) to alter attention
routing topology.

**If removed**: Rules stay imperative. Internal processing follows default routing.

**Can other layers detect L3 failures?**
- L0: ❌ Different concern
- L1: ❌ L1 doesn't care about format — rule is wired or not
- L2: ⚠️ Logprob probes CAN detect format effects (how we found d=+0.578).
  But detection ≠ intervention.
- L4: ❌ Too coarse-grained

**Verdict**: **Conceptually independent, measurement-overlaps with L2.** L3 is
engineering the INPUT (format); L2 is measuring the OUTPUT (penetration).
Different actions on different sides of the model. L2's tools are currently the
best way to detect L3's effects — but that's instrumentation, not identity.

## L4: Drift Prediction

**What**: Aggregates signals from L0-L3 + mechanical metrics (session duration,
hook count, disk space) to predict future degradation.

**If removed**: Lose temporal dimension. L0-L3 = current state snapshots.
L4 = state trajectories.

**Can other layers detect L4 failures?**
- L0-L3: ❌ Each operates on single timepoint. None captures cross-session trends.
- Example: Pass rate 100%→93%→86% over 3 sessions. L1 only sees current session,
  not the trajectory.

**Verdict**: **Fully independent.** Only layer with temporal axis.

## Summary Matrix

| If we remove → | L0 | L1 | L2 | L3 | L4 |
|---------------|:--:|:--:|:--:|:--:|:--:|
| Can L0 replace? | — | ❌ | ❌ | ❌ | ❌ |
| Can L1 replace? | ❌ | — | ❌ | ❌ | ❌ |
| Can L2 replace? | ⚠️ | ❌ | — | ⚠️ | ❌ |
| Can L3 replace? | ❌ | ❌ | ⚠️ | — | ❌ |
| Can L4 replace? | ❌ | ⚠️ | ❌ | ❌ | — |

❌ = cannot replace (different measurement substrate)
⚠️ = partial overlap (related but measurement-linked)

## Response to "Why not merge L2 and L3?"

L2 = **measurement** (detecting constraint penetration). L3 = **intervention**
(changing format to alter processing). Merging them = merging a thermometer
and a heater because both deal with temperature. L2's tools detecting L3's
effects doesn't make them the same layer — it makes L2 the **instrument** for
measuring L3.
