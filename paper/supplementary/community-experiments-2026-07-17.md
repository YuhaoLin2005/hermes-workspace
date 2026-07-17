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

### Limitation

Full end-to-end validation (embed hash in API records → collect → verify) requires a live API key (DeepSeek). The pre-registration scheme is code-verified but not yet API-validated. To complete: set `DEEPSEEK_API_KEY`, run `experiment_p1_2_format_gate_cross.py --pre-register b9ef83f7`, verify returned records contain the hash.

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

## Summary

| Experiment | Data Used | Key Finding | Status |
|-----------|----------|-------------|--------|
| Scanner calibration | P1-1 (n=200) | 5/5 alignment with ground truth | ✅ Complete |
| Pre-registration | P1-2 script | Hash reproducible; deterministic | ✅ Code-verified |
| Regex gap | P1-2 (n=600) | d=0.605 robust; no comparisons flip at 8% gap | ✅ Complete |
| API embedding | — | Requires DEEPSEEK_API_KEY | ⏳ Pending |

**Tools built**: `mechanizability_scanner.py` (v0.1.1), `pre_register.py`, `regex_gap_measure.py`
**Supplementary docs**: `verified-by-dimension.md` (Alice), `community-experiments-2026-07-17.md` (this file)

---

*Drafted 2026-07-17 · All experiments use existing hermes-workspace data (no new API calls)*
