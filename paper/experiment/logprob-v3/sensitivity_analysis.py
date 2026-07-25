#!/usr/bin/env python3
"""
Sensitivity Analysis: L1-Visibility Classification Robustness
=============================================================
Tests whether the primary finding (L1-visible > L1-invisible format effect)
is robust to boundary-case reclassification.

Probes with debatable classification are reclassified under 6 scenarios.
Each scenario re-runs the between-group Welch's t and Cohen's d.

NOT imported by any file. Standalone sensitivity check.
"""

import json
import math
from pathlib import Path
from decision_token_analysis import PROBE_CLASSIFICATION, load_data, compute_group_stats

# ─── Boundary Probes ──────────────────────────────────────────────────
# Each entry: (theme, classification_change_label, justification)

BOUNDARY_I_TO_V = [
    ("上下文-紧凑", "L1-INVISIBLE->VISIBLE",
     "85% threshold IS mechanically detectable via token-count regex; "
     "only the 'optimal moment' judgment is semantic. The TRIGGER is mechanical."),
    ("降级链-MEDIUM", "L1-INVISIBLE->VISIBLE",
     "Component failure detection IS mechanical (exit code, timeout); "
     "only the degrade-vs-stop decision is semantic. The trigger is gatable."),
    ("漂移-版本号", "L1-INVISIBLE->VISIBLE",
     "Version string update IS mechanically verifiable (regex on file content); "
     "only version number CORRECTNESS is semantic. The action is gatable."),
    ("记忆-沉淀触发", "L1-INVISIBLE->VISIBLE",
     "Session count and failure-type counting CAN be mechanically tracked; "
     "the pattern '3 consecutive same-type' is regex/counter-gatable."),
]

BOUNDARY_V_TO_I = [
    ("奇异环-再生", "L1-VISIBLE->INVISIBLE",
     "LLM synthesis quality of self-model is diligence, not just mechanical trace. "
     "Flag deletion and JSONL append are mechanical, but the CONTENT regeneration is not."),
    ("门互锁", "L1-VISIBLE->INVISIBLE",
     "Gate-B's triggering decision (whether to act on gate-A's flag) is semantic — "
     "filesystem traces exist but the decision quality is diligence."),
    ("上下文-预算", "L1-VISIBLE->INVISIBLE",
     "Token budget <15% IS mechanical, but the 'assess vs continue' response "
     "to the budget warning is diligence. The response is what matters."),
]


def apply_scenario(probe_data, reclass_map):
    """Apply a reclassification map to probe data. Returns (visible_fx, invisible_fx)."""
    visible_fx = []
    invisible_fx = []
    for probe in probe_data:
        theme = probe["theme"]
        if theme not in PROBE_CLASSIFICATION:
            continue
        cls = PROBE_CLASSIFICATION[theme]
        is_visible = cls["l1_visible"]
        if theme in reclass_map:
            is_visible = reclass_map[theme]
        if is_visible:
            visible_fx.append(probe["format_effect"])
        else:
            invisible_fx.append(probe["format_effect"])
    return visible_fx, invisible_fx


def between_group_test(vis_fx, inv_fx):
    """Welch's t-test + Cohen's d between two groups."""
    n_v, n_i = len(vis_fx), len(inv_fx)
    if n_v < 2 or n_i < 2:
        return {"error": "n < 2 in one group"}

    mean_v = sum(vis_fx) / n_v
    mean_i = sum(inv_fx) / n_i
    sd_v = math.sqrt(sum((x - mean_v)**2 for x in vis_fx) / (n_v - 1))
    sd_i = math.sqrt(sum((x - mean_i)**2 for x in inv_fx) / (n_i - 1))

    se_diff = math.sqrt(sd_v**2/n_v + sd_i**2/n_i)
    t_between = (mean_i - mean_v) / se_diff if se_diff > 0 else 0
    diff = mean_i - mean_v

    pooled_sd = math.sqrt(((n_v-1)*sd_v**2 + (n_i-1)*sd_i**2) / (n_v + n_i - 2))
    cohens_d = diff / pooled_sd if pooled_sd > 0 else 0

    if se_diff > 0 and sd_v > 0 and sd_i > 0:
        num = (sd_v**2/n_v + sd_i**2/n_i)**2
        denom = (sd_v**2/n_v)**2/(n_v-1) + (sd_i**2/n_i)**2/(n_i-1)
        df = num / denom if denom > 0 else 1
    else:
        df = 1

    return {
        "n_visible": n_v, "n_invisible": n_i,
        "mean_visible": round(mean_v, 2), "mean_invisible": round(mean_i, 2),
        "sd_visible": round(sd_v, 2), "sd_invisible": round(sd_i, 2),
        "delta_mean": round(diff, 2),
        "t_welch": round(t_between, 2), "df": round(df, 1),
        "cohens_d": round(cohens_d, 4),
        "direction": "INVISIBLE > VISIBLE" if diff > 0 else
                     "INVISIBLE < VISIBLE" if diff < 0 else "EQUAL"
    }


def main():
    data = load_data()
    per_probe = data["results"]["per_probe"]

    # ─── Baseline ──────────────────────────────────────────────────
    vis_fx_base = []
    inv_fx_base = []
    for probe in per_probe:
        theme = probe["theme"]
        if theme not in PROBE_CLASSIFICATION:
            continue
        if PROBE_CLASSIFICATION[theme]["l1_visible"]:
            vis_fx_base.append(probe["format_effect"])
        else:
            inv_fx_base.append(probe["format_effect"])

    baseline = between_group_test(vis_fx_base, inv_fx_base)

    # ─── Scenarios ──────────────────────────────────────────────────

    reclass_A = {t: True for t, _, _ in BOUNDARY_I_TO_V}
    vis_A, inv_A = apply_scenario(per_probe, reclass_A)
    result_A = between_group_test(vis_A, inv_A)

    reclass_B = {t: False for t, _, _ in BOUNDARY_V_TO_I}
    vis_B, inv_B = apply_scenario(per_probe, reclass_B)
    result_B = between_group_test(vis_B, inv_B)

    reclass_C = {}
    reclass_C.update({t: True for t, _, _ in BOUNDARY_I_TO_V})
    reclass_C.update({t: False for t, _, _ in BOUNDARY_V_TO_I})
    vis_C, inv_C = apply_scenario(per_probe, reclass_C)
    result_C = between_group_test(vis_C, inv_C)

    reclass_D = {"降级链-MEDIUM": True, "漂移-版本号": True}
    vis_D, inv_D = apply_scenario(per_probe, reclass_D)
    result_D = between_group_test(vis_D, inv_D)

    reclass_E = {"奇异环-再生": False, "门互锁": False}
    vis_E, inv_E = apply_scenario(per_probe, reclass_E)
    result_E = between_group_test(vis_E, inv_E)

    # Scenario F: Worst-case adversarial — flip probes that reduce delta most
    probes_with_fx = []
    for probe in per_probe:
        theme = probe["theme"]
        if theme not in PROBE_CLASSIFICATION:
            continue
        probes_with_fx.append({
            "theme": theme,
            "format_effect": probe["format_effect"],
            "l1_visible": PROBE_CLASSIFICATION[theme]["l1_visible"]
        })

    visible_sorted = sorted(
        [p for p in probes_with_fx if p["l1_visible"]],
        key=lambda x: x["format_effect"]
    )
    invisible_sorted = sorted(
        [p for p in probes_with_fx if not p["l1_visible"]],
        key=lambda x: x["format_effect"], reverse=True
    )

    worst_case_results = []
    for n_flip in [1, 2, 3]:
        flip_visible = set(p["theme"] for p in visible_sorted[:n_flip])
        flip_invisible = set(p["theme"] for p in invisible_sorted[:n_flip])
        reclass_F = {}
        for t in flip_visible:
            reclass_F[t] = False
        for t in flip_invisible:
            reclass_F[t] = True
        vis_F, inv_F = apply_scenario(per_probe, reclass_F)
        result_F = between_group_test(vis_F, inv_F)
        result_F["flipped_visible_to_invisible"] = list(flip_visible)
        result_F["flipped_invisible_to_visible"] = list(flip_invisible)
        worst_case_results.append(result_F)

    # ─── Output ────────────────────────────────────────────────────

    print("=" * 80)
    print("SENSITIVITY ANALYSIS: L1-VISIBILITY CLASSIFICATION ROBUSTNESS")
    print("=" * 80)

    print(f"\n## Baseline (Original Classification)")
    print(f"  n_visible={baseline['n_visible']}, mean_visible={baseline['mean_visible']}")
    print(f"  n_invisible={baseline['n_invisible']}, mean_invisible={baseline['mean_invisible']}")
    print(f"  delta={baseline['delta_mean']}, t={baseline['t_welch']}, "
          f"d={baseline['cohens_d']}")
    print(f"  direction: {baseline['direction']}")

    scenarios = [
        ("A: All 4 I->V reclassified", result_A, BOUNDARY_I_TO_V),
        ("B: All 3 V->I reclassified", result_B, BOUNDARY_V_TO_I),
        ("C: Both sets (7 changes)", result_C, BOUNDARY_I_TO_V + BOUNDARY_V_TO_I),
        ("D: Most defensible I->V (2 probes)", result_D,
         [e for e in BOUNDARY_I_TO_V if e[0] in reclass_D]),
        ("E: Most defensible V->I (2 probes)", result_E,
         [e for e in BOUNDARY_V_TO_I if e[0] in reclass_E]),
    ]

    for label, result, probes in scenarios:
        print(f"\n## Scenario {label}")
        for theme, change, _ in probes:
            print(f"  -> {theme}: {change}")
        print(f"  n_visible={result['n_visible']}, mean_visible={result['mean_visible']}")
        print(f"  n_invisible={result['n_invisible']}, mean_invisible={result['mean_invisible']}")
        print(f"  delta={result['delta_mean']}, t={result['t_welch']}, "
              f"d={result['cohens_d']}")
        print(f"  direction: {result['direction']}")

    print(f"\n## Worst-Case Adversarial Reclassification")
    for i, result in enumerate(worst_case_results):
        n = i + 1
        print(f"\n  F{n}: Flip {n} from each side")
        print(f"    V->I: {result['flipped_visible_to_invisible']}")
        print(f"    I->V: {result['flipped_invisible_to_visible']}")
        print(f"    n_visible={result['n_visible']}, mean_visible={result['mean_visible']}")
        print(f"    n_invisible={result['n_invisible']}, mean_invisible={result['mean_invisible']}")
        print(f"    delta={result['delta_mean']}, t={result['t_welch']}, "
              f"d={result['cohens_d']}")
        print(f"    direction: {result['direction']}")

    # ─── Summary ──────────────────────────────────────────────────

    all_deltas = [baseline['delta_mean']]
    all_deltas += [r['delta_mean'] for _, r, _ in scenarios]
    all_deltas += [r['delta_mean'] for r in worst_case_results]

    min_delta = min(all_deltas)
    max_delta = max(all_deltas)
    any_sign_flip = any(d > 0 for d in all_deltas)

    print(f"\n{'='*80}")
    print(f"ROBUSTNESS SUMMARY")
    print(f"{'='*80}")
    print(f"  Delta range across all scenarios: [{min_delta:.1f}, {max_delta:.1f}]")
    print(f"  Any scenario flips sign? {'YES - WARNING' if any_sign_flip else 'NO - ROBUST'}")
    print(f"  Min |delta|: {abs(min_delta):.1f} logprob")
    print(f"  Max |delta|: {abs(max_delta):.1f} logprob")

    if not any_sign_flip:
        print(f"\n  CONCLUSION ROBUST: L1-visible > L1-invisible in ALL scenarios.")
    else:
        print(f"\n  CONCLUSION SENSITIVE: At least one scenario flips direction.")

    out_path = Path(__file__).parent / "results" / "sensitivity-analysis-20260713.json"
    output = {
        "analysis": "Sensitivity Analysis: L1-Visibility Classification Robustness",
        "timestamp": "2026-07-13",
        "baseline": baseline,
        "scenarios": {
            "A_all_I_to_V": {"probes": [t for t, _, _ in BOUNDARY_I_TO_V], "result": result_A},
            "B_all_V_to_I": {"probes": [t for t, _, _ in BOUNDARY_V_TO_I], "result": result_B},
            "C_both_sets": {"probes": [t for t, _, _ in BOUNDARY_I_TO_V + BOUNDARY_V_TO_I], "result": result_C},
            "D_defensible_I_to_V": {"probes": list(reclass_D.keys()), "result": result_D},
            "E_defensible_V_to_I": {"probes": list(reclass_E.keys()), "result": result_E},
        },
        "worst_case_adversarial": [
            {"n_flip": i+1, **r} for i, r in enumerate(worst_case_results)
        ],
        "robustness": {
            "delta_range": [min_delta, max_delta],
            "any_sign_flip": any_sign_flip,
            "conclusion_robust": not any_sign_flip,
        }
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  Structured output -> {out_path}")


if __name__ == "__main__":
    main()
