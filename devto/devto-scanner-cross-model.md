# Your AI Gate Works Perfectly — Until You Switch Models

Last week I wrote: "Mechanizability-scanner. Building this next." And: "Cross-model replication. Blocked on API access."

Both are done. The scanner works. The cross-model data is in.

The result isn't what I expected. And the "failure" is the real finding.

---

## What Got Built

Max Quimby asked: "Where do you draw the line between 'gate it' and 'can only nudge it'?"

I built `mechanizability_scanner.py` — a deterministic regex-based classifier that scores a rule 0.0–1.0 on how mechanically checkable it is. Structure markers (`[ANSWER]`), code fences, MUST directives → high score. Quality judgments ("thorough", "insightful"), vague expectations → low score.

Thresholds:
- **≥ 0.70 → L1 (gateable)**: a regex or filesystem check can verify this
- **0.30–0.69 → L2 (semi)**: logprob probes can detect penetration; mechanical check insufficient
- **< 0.30 → L3 (not gateable)**: requires semantic interpretation

Calibrated it on DeepSeek V4 Pro against P1-1 ground truth (200 trials, 5 task types spanning the mechanizability gradient).

**5/5. Perfect alignment.**

| Task | Scanner | Reality (DS Pro) |
|------|---------|-------------------|
| Format-tag (code blocks) | 0.950 → L1 | 100% compliant ✓ |
| Section-header ([ANSWER] tag) | 1.000 → L1 | 100% compliant ✓ |
| Checklist (content + format) | 0.600 → L2 | 0% compliant ✓ |
| Reasoning (because/since) | 0.550 → L2 | 35% compliant ✓ |
| Uncertainty (might/depends) | 0.550 → L2 | 42.5% compliant ✓ |

The scanner correctly separates "a gate CAN verify this" from "a gate CANNOT verify this." I was satisfied. Time to test on other models.

---

## The Cross-Model Test

Same 5 tasks. Same scoring regexes. Temperature = 0.0. Two new models via SiliconFlow:

- **Qwen3.6-35B-A3B** (20 trials per task)
- **DeepSeek V4 Flash** (20 trials per task)

200 new API calls. Compare against the DS Pro baseline.

| Task | Scanner | DS Pro | Qwen3.6 | DS Flash |
|------|---------|--------|---------|----------|
| T1 Format-tag | 0.950 **L1** | 100% | **40%** | 100% |
| T2 Section-header | 1.000 **L1** | 100% | 70% | 95% |
| T3 Checklist | 0.600 **L2** | 0% | 10% | **100%** |
| T4 Reasoning | 0.550 **L2** | 35% | 40% | **95%** |
| T5 Uncertainty | 0.550 **L2** | 42.5% | **0%** | 25% |

**Alignment: 2/5 across all three models.**

On one model, the scanner was 100% right. Across models, it's 40%.

This looks like failure. It isn't.

---

## What The Data Actually Says

Three things jumped out.

### 1. DS Flash is more "obedient" than DS Pro

On T3 (checklist), DS Pro scored **0%**. It refused to produce `- [ ]` checkboxes when the content didn't naturally fit a checklist format. It exercised judgment.

DS Flash scored **100%**. It mechanically produced `- [ ]` items every single time, regardless of relevance.

On T4 (reasoning keywords), DS Flash hit 95% — it almost always includes "because" or "since." DS Pro: 35%. The Pro model decides *whether* to follow the instruction. The Flash model just follows it.

The smaller model is more compliant. Not because it's smarter — because it's more literal. It doesn't push back on format rules. It executes them.

### 2. Qwen doesn't attend to output-format rules

T1 (code tags) at **40%**. The rule says "Every code block MUST be wrapped in ```language tags." Qwen frequently outputs Python without ```python — despite the MUST directive being the first thing in the system prompt.

T5 (uncertainty) at **0%**. Twenty trials. Zero uses of "uncertain," "might," "depends," "maybe," or "not clear." Qwen presents every answer as definitive, even on a question explicitly designed to require epistemic hedging ("Will quantum computing make current encryption obsolete within 5 years?").

Format-rule attention is model-specific. Some architectures process formatting constraints as suggestions regardless of how they're phrased.

### 3. The L1/L2 boundary is model-dependent

T3 (checklist, scanner = 0.600) is my boundary case. The scanner correctly identifies it as structurally ambiguous — mechanical format (checkboxes) mixed with semantic content (relevance). It scores it L2.

But:
- **DS Flash**: 100% → effectively L1
- **DS Pro**: 0% → firmly L2
- **Qwen**: 10% → firmly L2

Same rule. Same scanner score. Three different effective layers. The model architecture determines where the gateability cliff falls — not just the rule's structure.

---

## The Two-Axis Model

The scanner didn't fail. It measures exactly what it was designed to measure: **rule structure** — how mechanically checkable a constraint is, independent of any model.

What it can't measure — and wasn't designed to measure — is **model compliance tendency**: how likely a given architecture is to follow structured rules.

These are two independent axes.

```
                Rule Mechanizability (scanner measures this)
                ← semantic ────────────────────→ mechanical

Model           0.0         0.3         0.6         1.0
Compliance      │           │           │           │
 Tendency       │           │           │           │
 ↑              │  L3       │    L2     │    L1     │
 │   DS Flash   │  T5:25%   │ T3:100%✓  │ T1:100%✓  │  ← gate works
 │   (obedient) │  T4:95%✓  │           │ T2:95%✓   │
 │              │           │           │           │
 │   DS Pro     │  T5:42%   │ T3:0%     │ T1:100%✓  │  ← gate works
 │   (judicious)│           │ T4:35%    │ T2:100%✓  │     only on L1
 │              │           │           │           │
 │   Qwen3.6    │  T5:0%    │ T3:10%    │ T1:40%    │  ← gate unreliable
 │   (format-   │           │ T4:40%    │ T2:70%    │     even on L1
 ↓   inattentive)│          │           │           │
```

A gate works when **both** axes are favorable: the rule is structurally checkable (scanner ≥ 0.70) AND the model actually follows structured rules (compliance ≥ 70%).

The scanner alone tells you whether a gate **can** work. Calibration tells you whether it **will** work on your specific model.

---

## Why This Matters

If you're building an AI agent with rule enforcement, you need to calibrate. Not once — per model.

The workflow:

1. **Score your rules** with the scanner → identify L1 candidates
2. **Run a calibration trial** (5 tasks × 10 trials = 50 API calls) on your model
3. **Map your model's compliance cliff** — where does it stop following structured rules?
4. **Place gates only in the overlap** — high mechanizability AND high compliance

A rule scored 0.950 L1 by the scanner might be effectively L2 on Qwen and L1 on DeepSeek. If you deploy a gate without calibration, you don't know which world you're in.

---

## René Zander Already Knew This

René Zander built [skillgate](https://www.npmjs.com/package/@reneza/skillgate) — deterministic, model-independent gates for AI coding agents. He arrived at the same architecture from the same constraint, independently. I wrote about this convergence last week.

What I didn't notice then: skillgate's design implicitly targets the overlap zone. Every check runs as a pure function over the filesystem. File-exists, file-contains, absent, command, evidence. These are all **structurally L1** rules. And skillgate ships as an npm package for Claude Code — a model with high format-compliance tendency on the DeepSeek family.

René didn't need to articulate the 2D model. He built directly in the region where both axes align. The engineering intuition preceded the framework.

---

## Limitations

Three models isn't enough. GPT-4o, Claude 4, Gemini — all untested. The compliance patterns I found might be specific to the DeepSeek and Qwen families. Different architectures could show completely different cliff locations.

The DS Flash "obedience" finding has a dark side. 100% checklist compliance sounds great until you read the responses — the model produces `- [ ]` markers with content that's sometimes barely relevant. High compliance ≠ high quality. A gate that only checks format will pass garbage if the model is obedient enough.

Scoring is deterministic regex only. No LLM judge. This is correct for L1 measurement but means I'm measuring format compliance, not content quality. The T3 "100%" for DS Flash measures "produced checkbox markers" — not "produced a useful deployment checklist."

---

## What's Next

The scanner is at `github.com/YuhaoLin2005/paper-validator` — `mechanizability_scanner.py`, v0.1.1. The cross-model experiment script and 200-trial dataset are in `experiment_p1_1_cross_model.py` and `results/p1_1_cross_model_20260717-143157.json`.

Full analysis with per-model compliance patterns: `hermes-workspace/paper/supplementary/community-experiments-2026-07-17.md` § Experiment 4.

If you've run calibration trials on your own model — or if you've noticed your gates behaving differently after a model switch — I want to hear about it. The 2D model is a hypothesis with n=3. More data would tell me whether it holds or breaks.

---

*200 new API calls. 3 models. 1 scanner. The tool I promised last week, and the cross-model data I said was blocked. Both done. The finding isn't what I expected — which means it was worth running.*
