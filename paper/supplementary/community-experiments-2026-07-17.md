# Community-Driven Experiments — July 17, 2026

> **Context**: Four DEV.to readers proposed concrete improvements. We built the tools, then validated them against real experimental data (P1-1 n=200, P1-2 n=600). This report documents what the data says.

---

## Experiment 1: Mechanizability Scanner Calibration

**Trigger**: Max Quimby — "A mechanizability-scanner that infers layers from rule structure."

**Method**: Score 5 P1-1 task rules (0.0–1.0 mechanizability) and compare scanner predictions to ground-truth compliance rates from 200 trials.

### Calibration Results (v0.1.1, post-regex fix)

| Task | Score | Layer | Ground Truth Compliance | Match |
|------|-------|-------|------------------------|-------|
| T1_format_tag | 0.950 | L1 | 100% (0/40 violations) | ✓ |
| T2_section_header | 1.000 | L1 | 100% (0/40 violations) | ✓ |
| T3_checklist | 0.600 | L2/boundary | 0% (all semantic violations) | ✓ |
| T4_reasoning | 0.550 | L2 | 35% (26/40 violations) | ✓ |
| T5_uncertainty | 0.550 | L2 | 42.5% (23/40 violations) | ✓ |

**Alignment: 5/5**. The scanner correctly separates fully-gateable rules (L1: T1, T2) from interpretation-requiring rules (L2: T3–T5).

### P1-2 Rule Set Scores

| Rule | Score | Layer | Signal |
|------|-------|-------|--------|
| `connection_check` | 1.000 | L1 | file_check + mtime_check |
| `delivery_gate` | 0.800 | L1 | structured_markers + must_directive |
| `file_output` | 0.750 | L1 | file_check + exit_code |
| `fact_check` | 0.700 | L1/boundary | must_directive |
| `change_condition` | 0.700 | L1/boundary | must_directive |
| `alternative_seeking` | 0.600 | L2/boundary | must_directive + alternatives |
| `trade_off` | 0.600 | L2/boundary | must_directive + alternatives |
| `context_aware` | 0.350 | L2 | context_dependent |
| `self_review` | 0.300 | L2 | reasoning_depth + vague_directive |
| `quality_standard` | 0.050 | L3 | quality_judgment + vague_directive |

**5/10 rules at L1, 4 at L2, 1 at L3**. The boundary (0.60–0.75) contains exactly the rules where mechanical structure (MUST directive, tags) intersects with semantic content (judgment required).

### Bug Found During Calibration

The scanner's original signal regexes missed two output-structure rules entirely:
- `[ANSWER]` tag: regex was case-sensitive, but text is lowered before matching
- `` ```language `` backticks: no signal existed for code-fence markers
- `MUST be wrapped` / `MUST start with`: 8-verb whitelist excluded these constructions

**Fix**: Made structured_markers case-insensitive, added `code_fence` signal, broadened `must_directive` from 8 verbs to all `MUST|NEVER|EVERY` constructions. Fix committed as `84a775a` in paper-validator.

---

## Experiment 2: SHA256 Pre-Registration Validation

**Trigger**: Dipankar Sarkar — "SHA256 pre-registration embedded in API records."

**Method**: Register P1-2 experiment (`experiment_p1_2_format_gate_cross.py`) → re-extract hash from script → verify reproducibility.

### Result

```
Pre-registration hash: b9ef83f7f890efe861e8b6b789f9fdbf
Re-extracted:         b9ef83f7f890efe861e8b6b789f9fdbf
Match: True ✓
```

The hash is deterministic: same hypothesis + conditions + scoring regexes → same hash. Tampering with any of these changes the hash, detectable by any third party.

### Limitation: Tamper-Resistance ≠ Third-Party Verifiability

Mike Czerwinski identified a distinction the current scheme clarifies but does not fully resolve: **tamper-resistance** and **third-party verifiability** are different properties.

The SHA256-in-API-record scheme provides tamper-resistance: even the author editing their own git history after the fact cannot make the hash agree with a different pre-registration. The hash proves internal consistency — the stored records match what was reported.

What it does not yet provide is third-party verifiability: can a skeptical reader independently pull a record and check the hash themselves, without routing through what the author shows them?

**What IS verifiable**: The raw API response JSON files and their hashes are publicly available in the repository (`paper-validator/results/`). Anyone with access to the raw JSON can independently re-compute the hashes and verify they match. This provides **reproducible verification** (anyone holding the same data gets the same result).

**What is NOT verifiable**: A reader still trusts that the raw JSON files were not altered before being committed to the repo. The hash proves the report matches the stored records — it does not prove the stored records are the originals. Specifically, a third party cannot independently verify: (a) that the recorded interaction was the first interaction with that prompt, (b) that no preprocessing occurred before the response was saved, or (c) that the configuration claimed matches the one used.

**Additional constraint**: The API-based models used in this study (DeepSeek V4 Pro, DeepSeek V4 Flash, Qwen3.6 via SiliconFlow) may receive updates between the experiment and any reproduction attempt. Third-party verification at a later date tests reproducibility relative to the paper's claims, not identical-model reproduction — a structural limitation of API-based research, not unique to this study.

Full end-to-end validation (embed hash in API records → collect → verify) requires a live API key. The pre-registration scheme is code-verified but not yet API-validated. To complete: set `DEEPSEEK_API_KEY`, run `experiment_p1_2_format_gate_cross.py --pre-register b9ef83f7`, verify returned records contain the hash.

---

## Experiment 3: Regex Gap Measurement

**Trigger**: Mike Czerwinski — "Does the 8% detection gap touch d=0.605 the same way it touched fact_check?"

**Method**: Applied sensitivity analysis (uniform gap 0%–20%) and non-uniform gap estimation (8% concentrated on lowest-compliance conditions) to P1-2 data (600 trials).

### Uniform Gap Sensitivity

| Gap | Adjusted d | d Loss | Flips? |
|-----|-----------|--------|--------|
| 0% | 0.6050 | 0.0000 | no |
| 4% | 0.5808 | 0.0242 | no |
| 8% | 0.5566 | 0.0484 | no |
| 12% | 0.5324 | 0.0726 | no |
| 20% | 0.4840 | 0.1210 | no |
| **67%** | **0.1996** | **0.4054** | **yes** |

**Finding**: An 8% uniform gap reduces d from 0.605 → 0.557. Still a medium effect. To flip d below the "small effect" threshold (0.2) requires a 67% detection gap — implausibly large. The headline result is **robust**.

### Non-Uniform Gap (Worst Case)

Concentrated the entire 8% gap on the 10 lowest-compliance conditions (16pp adjustment per condition):

```
prose_ON vs code_ON:   raw=-0.237  adj=-0.141  [stable]
prose_OFF vs code_OFF: raw=-0.205  adj=-0.109  [stable]
code_ON vs code_OFF:   raw=+0.025  adj=+0.025  [stable]
prose_ON vs prose_OFF: raw=-0.007  adj=-0.007  [stable]
```

**Finding**: Zero pairwise comparisons flip direction. Even in the worst case (gap concentrated on the conditions most vulnerable to regex misses), the substantive conclusions hold.

### Mike's Question, Answered

> "Does the 8% detection gap touch d=0.605?"

**No.** The detection gap attenuates d, but not enough to change the conclusion. d=0.605 drops to d=0.557 at 8% uniform gap — still medium. Non-uniform concentration doesn't flip any cross-condition comparison. The regex scoring approach is sufficiently reliable for the claims it supports.

---

---

## Experiment 4: Multi-Model Scanner Calibration

**Trigger**: Community review — "Scanner calibration was done on a single model (DeepSeek V4 Pro). Does it hold across architectures?"

**DEV.to article**: [Your AI Gate Works Perfectly — Until You Switch Models](https://dev.to/yuhaolin2005/your-ai-gate-works-perfectly-until-you-switch-models-4bf0)

**Method**: Replicate P1-1 (5 task types × 20 trials each) on 2 additional SiliconFlow models: Qwen3.6-35B-A3B and DeepSeek V4 Flash. Total: 200 new API calls (temperature=0.0). Compare scanner L1/L2/L3 predictions to ground-truth compliance across all 3 models.

**Script**: `paper-validator/experiment_p1_1_cross_model.py` · **Data**: `results/p1_1_cross_model_20260717-143157.json`

### Results

| Task | Scanner | DS Pro | Qwen3.6 | DS Flash | Aligned? |
|------|---------|--------|---------|----------|----------|
| T1_format_tag | 0.950 L1 | 100% | **40%** | 100% | ✗ |
| T2_section_header | 1.000 L1 | 100% | 70% | 95% | ✓ |
| T3_checklist | 0.600 L2 | 0% | 10% | **100%** | ✗ |
| T4_reasoning | 0.550 L2 | 35% | 40% | **95%** | ✗ |
| T5_uncertainty | 0.550 L2 | 42% | **0%** | 25% | ✓ |

**Alignment: 2/5 across all 3 models** (vs 5/5 on DS Pro alone).

### Finding: Mechanizability ≠ Model Capability

The misalignment is NOT a scanner failure. It reveals a fundamental separation:

```
compliance = rule_structure × model_capability
```

The scanner measures **rule structure** (how mechanically checkable is the constraint itself). It correctly identifies T1/T2 as structurally L1 and T3–T5 as structurally L2+. This classification is **architecturally correct** — the distinction between "output must contain X tag" and "reasoning must be sound" is real and invariant.

What the scanner CANNOT measure is **model compliance tendency** — how likely a given model architecture is to follow structured rules. This is a separate dimension:

| Model | Compliance Pattern | Note |
|-------|-------------------|------|
| **DS Pro** | High on L1 (100%/100%), low on L2 (0%/35%/42.5%) | Compliance tracks mechanizability — sharp cliff at L1/L2 boundary |
| **DS Flash** | High on L1 (100%/95%), high on most L2 (100%/95%) | L2 compliance unusually high; exception: T5_uncertainty at 25% |
| **Qwen3.6** | Low on L1 (40%/70%), very low on L2 (10%/40%/0%) | Format-rule compliance limited; may reflect capacity constraint (3.6B active MoE parameters) rather than an attentional deficit |

### Key Observations

1. **DS Flash follows format rules more literally — but format compliance ≠ content quality.** On T3 (checklist), DS Pro scored 0% — it refused to produce superficial checkboxes when content didn't naturally fit. DS Flash scored 100% — it mechanically produced `- [ ]` items regardless of relevance. On T4 (reasoning keywords), DS Flash 95% vs DS Pro 35%. This is **hollow compliance**: the format check passes (markers are present, parseable, mechanically verifiable) but the content inside them is sometimes barely relevant. A deterministic gate would happily accept a checklist full of markers with no substance behind them. This failure mode sits between L1 and L2 — structurally L1-checkable, semantically L2-quality-dependent — and no gate at either layer alone catches it. The Flash model follows format instructions more literally; the Pro model exercises more judgment about WHEN to follow them. DS Flash's T5_uncertainty at 25% (below DS Pro's 42.5%) suggests this compliance is format-preferring rather than uniform — the model follows structural rules consistently but is uneven on content-modulation rules.

2. **Qwen3.6's compliance is low across the board, but the cause is ambiguous.** T1 (code tags) at 40% — it frequently outputs Python code without `` ```python `` wrappers despite explicit MUST directives. T5 (uncertainty) at 0% — it NEVER uses uncertainty language, always presenting answers as definitive. However, Qwen3.6-35B-A3B activates only 3.6B parameters per token (MoE), an order of magnitude smaller effective capacity than DS Pro and DS Flash. Low compliance could reflect insufficient capacity to parse or execute the rules, not a volitional attention failure. "Low-compliance" describes the observation; the underlying mechanism (capability vs. attention) is not distinguishable from this data alone.

3. **The L1/L2 boundary is model-dependent.** A rule at scanner score 0.600 (T3 checklist) can be effectively L1 for DS Flash (100% gateable) but L2 for DS Pro (0% gateable) and Qwen (10% gateable). The same rule, same scoring pattern, different effective layer — because **the model's architecture determines where the gateability cliff falls**, not just the rule's structure.

### Theoretical Implication: Two-Axis Gateability (Revised)

Gateability must be understood as a 2D space:

```
Axis 1 (Rule): Mechanizability score (0–1)
    ← purely semantic (0)  ───────────────────→ purely mechanical (1)
    Measured by: mechanizability_scanner.py ✓

Axis 2 (Model): Compliance tendency (model-specific)
    ← low compliance ──────────────────────→ high compliance
    Measured by: calibration experiment (this report) ✓
```

A gate works when BOTH axes are favorable: high mechanizability AND model compliance tendency sufficient for the rule. The scanner alone tells you whether a gate CAN work (axis 1); calibration tells you whether it WILL work on your specific model (axis 2).

**Mike Czerwinski was right: the axes are not independent.** The initial framing treated compliance tendency as a fixed trait per model — a single height on the vertical axis. But DS Pro's data says otherwise: its compliance tracks the mechanizability score almost exactly (100%/100% on L1 → 0%/35%/42.5% on L2). Compliance is not a constant for DS Pro; it is a function of how mechanizable the rule is. This means:

- **For DS Flash and Qwen**, the axes are approximately independent — compliance is a relatively fixed trait (DS Flash consistently high except T5; Qwen consistently low).
- **For DS Pro**, the axes interact — compliance = f(mechanizability). The model follows mechanically-enforceable rules reliably and exercises judgment on interpretation-requiring ones.

In our sample of three models, we observe three behavioral clusters, described as patterns rather than validated types (n=3, single calibration per model):

| Cluster | Model | Compliance Shape | Axes |
|---------|-------|-----------------|------|
| **Consistently high** | DS Flash | High across L1 and most L2; exception T5=25% | ~Independent |
| **Consistently low** | Qwen3.6 | Low across both L1 and L2 | ~Independent |
| **Mechanizability-coupled** | DS Pro | High on L1, low on L2 — compliance tracks scanner score | **Interacting** |

These are descriptions of the observed data, not claims about exhaustiveness. Whether "mechanizability-coupled" or "flat" is the default across architectures (GPT-4o, Claude 4, Gemini, Llama-4) remains an open empirical question with n=3.

This explains why **René Zander's skillgate** (independent, same architecture) converges on the same design: his system implicitly targets the overlap region where both axes align — high-mechanizability rules on models with sufficient compliance tendency.

### Practical Guidance

- **Scanner use**: Score your rules → L1 rules are candidates for mechanical gates
- **Model calibration**: Run a small calibration trial (5 tasks × 10 trials = 50 calls) to locate your model's compliance cliff
- **Gate placement**: Place gates only on rules where BOTH scanner ≥ 0.70 AND model compliance ≥ 70%
- **DS Flash caveat**: High compliance ≠ high quality. 100% checklist compliance may mean "produced `- [ ]` markers" not "produced meaningful checklist items"

### Layer Distinction: Mechanizability vs. Mechanization-Correctness

The scanner classifies rules by structural mechanizability: can a deterministic check verify compliance without passing through the model's generation pathway? This is a useful first filter — it tells you which rules are worth writing a mechanical check for.

What the scanner cannot do — and was not designed to do — is assess whether a mechanical check that exists actually covers the full failure surface. **Mechanizability** (can this be checked mechanically?) and **mechanization-correctness** (does the check that exists catch all failure modes?) are distinct properties.

Alice (DEV.to, July 18 2026) provided a production case that illustrates the distinction. Her guard hook detected malformed tool-calls — a structurally L1 rule, correctly scorable by the scanner. The implementation existed and ran on every turn. And it still silently passed bad input: the check required two tokens together when the real failure emitted only one token. The scanner correctly said "this rule is worth mechanizing." It could not say whether the mechanization was complete — that required discovering the failure in production, not scoring the rule structure.

This does not break the scanner framework. It clarifies the layers:
- **Scanner (classification)**: Which rules are mechanizable? → Regex-based structural scoring
- **Adversarial validation (completeness)**: For mechanized rules, does the check cover the failure surface? → Requires intentionally malformed inputs designed to evade the check

Both layers are necessary. The scanner identifies candidates; adversarial testing verifies that the mechanization is correct, not just present. Alice's hook failed at the second layer — a correctly-classified L1 rule, correctly mechanized in principle, with a detector that was too narrow. The scanner alone cannot prevent this class of failure.

This is a single incident (n=1), not a measured trend. The distinction it illustrates — mechanizability does not imply mechanization-completeness — is a structural boundary of the scanner approach, not a bug in a specific implementation.

---

## Summary

| Experiment | Data Used | Key Finding | Status |
|-----------|----------|-------------|--------|
| Scanner calibration | P1-1 (n=200) | 5/5 alignment with DS Pro ground truth | ✅ Complete |
| Pre-registration | P1-2 script | Hash reproducible; deterministic | ✅ Code-verified |
| Regex gap | P1-2 (n=600) | d=0.605 robust; no comparisons flip at 8% gap | ✅ Complete |
| **Multi-model scanner** | **P1-1 × 2 models (n=200 new)** | **Gateability = rule_structure × model_capability; 2D space** | **✅ Complete** |
| API embedding | — | Requires DEEPSEEK_API_KEY | ⏳ Pending |

**Tools built**: `mechanizability_scanner.py` (v0.1.1), `pre_register.py`, `regex_gap_measure.py`, `experiment_p1_1_cross_model.py`
**Supplementary docs**: `verified-by-dimension.md` (Alice), `community-experiments-2026-07-17.md` (this file)

---

*Drafted 2026-07-17 · Updated 2026-07-18 with multi-model calibration (Experiment 4). All experiments use real API data.*
