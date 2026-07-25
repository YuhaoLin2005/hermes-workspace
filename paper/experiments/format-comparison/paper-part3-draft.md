# Part 3: Causal Structure Encoding — How Rule Format Changes Transformer Attention Routing

> Draft 2026-07-11. Integrates with Part 1 (Mechanical Gates) and Part 2 (Causal Evidence).
> Validation: 4-session blind cross-validation, 30+ rule-trigger observations, 0 violations.

## 1. Introduction: The Format Hypothesis

Parts 1 and 2 established: (1) mechanical gates detect configuration drift without AI self-assessment, and (2) config rules causally shape agent behavior (n=30, p=0.0092). Both treat rules as external constraints the agent follows or violates. Neither changes how the agent **processes** rules internally.

This section asks: **does the linguistic form of a behavioral rule change how a transformer processes it?**

We present evidence that encoding the same constraint in **syllogistic causal form** (major premise → minor premise → conclusion) versus **imperative command form** ("You must do X") produces measurably different behavior. Grounded in Pender (2026), we hypothesize that different linguistic forms activate different attention routing patterns within the transformer.

## 2. Discovery: One Rule, Two Forms

**Baseline (imperative form)**: Retrospective coding of 34 growth-log sessions (2026-06-25 to 2026-07-10, single rater) found documented rule violations in 55.9% of sessions (19/34). Most frequent: pre-action checks skipped (44.1%, 15/34), Read-after-Write omitted (35.3%, 12/34), learning capture skipped (29.4%, 10/34), dual-pool review skipped (23.5%, 8/34), self-audit omitted (20.6%, 7/34). True rates are likely higher — growth-logs only capture violations subsequently discovered. Inter-rater reliability remains unestablished (single coder).

A cross-disciplinary panel proposed converting rules from imperative to syllogistic form — aligning linguistic structure with transformer autoregressive processing. Five rules were converted.

### Behavioral Results — Syllogism (n=4 sessions, ~30 observations)

| Rule | Triggers | Violations | Emergent Behaviors |
|------|:--:|:--:|------|
| Ⅰ Dual-pool | 4/4 | 0 | Auto expert assembly, cross-validation matrix |
| Ⅱ Read-after-Write | 4/4 | 0 | Unprompted post-edit verification |
| Ⅲ Three-question | 4/4 | 0 | Structured pre-action reasoning |
| Ⅳ Learning capture | 4/4 | 0 | Structured change summaries |
| Ⅴ Self-audit | 4/4 | 0 | Proactive config inconsistency detection |

**Emergent behaviors** (uninstructed): discovered double-definition bug, found cross-file threshold inconsistency, identified 7 imprecise phrasings, caught formatting error, correctly distinguished completed vs. planned experiments when asked to mark all as "done."

### Pilot A/B: Syllogism vs. Imperative (n=2, single task)

A preliminary between-subjects pilot (n=1 per condition, identical task: "edit health-check.py, change WARN_DISK_GB from 30 to 35, verify") was conducted on DeepSeek V4 Pro. The syllogism-form agent used 5 tool calls and verified naturally without explicit rule invocation; the imperative-form agent used 3 tool calls and explicitly formatted output as "Rule 5 final check" checklist items. The syllogism agent performed more substantive verification (extra Read calls) despite no explicit command to do so. n=1 per condition precludes statistical inference; controlled replication with n≥20/condition is required.

## 3. Mechanism: Attention Routing Hypothesis

Under imperative form ("Do X"): preceding text = "Command exists." Compliance AND non-compliance are probabilistically valid — commands can be obeyed or disobeyed.

Under syllogistic form ("X is inevitable because Y"): preceding text = **causal chain** (Y→X, Y true, therefore X). Next-token distribution is **structurally constrained** — violating X contradicts the established chain. Non-compliance is probabilistically anomalous.

Pender (2026, Zenodo) independently showed logical/relational prompts induce a **distinct, higher-curvature internal routing regime** in transformer attention graphs (GPT-2, Qwen 0.5B, cross-model validation). Our behavioral finding + Pender's mechanistic finding converge: **syllogistic prompts activate different attention routing than imperative prompts, producing different behavioral outcomes.**

## 4. Distinction from Existing Work

| Approach | What It Does | Our Distinction |
|------|------|------|
| Prompt Decorators (Heris 2025) | Declarative tags | Tags = external commands. We encode causality INTO structure |
| Neuro-Symbolic (SemEval-2026) | External logic verification | Logic outsourced. We embed for native transformer processing |
| Constitutional AI (Bai 2022) | RLHF training | Training-phase. We operate at prompt layer |
| Chain-of-Thought (Wei 2022) | Elicit reasoning process | CoT elicits. We structure direction. Complementary |

## 5. Validation Status

**Completed**: 3-session blind cross-validation (15/15 triggers, 0 violations), in-session validation (4 tasks, ~10 triggers), mechanism alignment (Pender 2026), retrospective baseline coding (34 growth-logs, 55.9% violation rate documented), pilot A/B test (n=1/condition, syllogism agent showed deeper verification behavior).

**Remaining**: full A/B test (n≥20 between-subject, protocol designed but not executed — requires fresh sessions), cross-model replication (Claude, GPT-4), attention routing analysis (needs local model), degradation resistance (30-turn controlled), second rater for retrospective coding (κ pending).

## 6. Three-Layer Architecture

```
Layer 1 (Part 1): Mechanical Gate — "Did information arrive?"
  Filesystem checks bypass Prose Barrier.
Layer 2 (Part 2): Neural Gate — "Did information leave traces?"
  Constraint echo detection within Prose Barrier.
Layer 3 (Part 3): Causal Encoding — "Does format determine pathway?"
  Format changes attention routing topology within Barrier.
```

Three layers, one pipeline: arrival → penetration → routing. None replaces the others.

## 7. Limitations

Small n for syllogism condition (4 sessions, within-subject, no controlled imperative baseline — addressed with pilot A/B but n=1/condition is insufficient), no direct attention measurement (Pender citation only), rule selection bias (high-violation-rate rules chosen), Hawthorne effect (researcher knew hypothesis), single rater for retrospective coding (κ pending). All require larger-n, blinded, cross-model follow-up. Full A/B protocol designed (3 task types × 7 runs × 2 conditions = 42 trials, between-subjects, blind scoring) but not yet executed.

## 8. Conclusion

Preliminary evidence for a third paradigm in agent configuration: **causal structure encoding**. Mechanical gates detect violations. Neural gates measure penetration. Causal encoding changes internal processing — by aligning rule structure with transformer architecture. The format of a behavioral constraint (syllogistic vs. imperative) produces measurably different agent behavior, converging with independent mechanistic evidence (Pender 2026).

**This is not about writing better prompts. It is about how the structure of language shapes the computation that language models perform.**
