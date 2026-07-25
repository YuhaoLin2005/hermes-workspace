#!/usr/bin/env python3
"""
P0.1 + P0.2: L1-Visibility Classification + Logprob Re-Analysis
===============================================================
Responds to: Max Quimby (decision-token measurement), Mike Czerwinski
(receipt-of-action vs receipt-of-diligence), Dipankar Sarkar
(L1-visible vs L1-invisible violation classes).

Phase 1: Classify all 40 probes by L1 mechanical-gate detectability.
Phase 2: Re-analyze existing logprob data by L1-visibility class.
Zero API calls — uses existing experiment-2-confirmatory JSON.

NOT imported by any file. Standalone analysis script.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import math

# ─── Classification Criteria ───────────────────────────────────────────
#
# L1-VISIBLE (GATABLE):
#   A violation of this rule produces a deterministic signal that a
#   mechanical hook can detect with certainty — file existence, mtime,
#   exit code, regex match, tool-call presence in history, or
#   hook-registration check.
#
#   THREE TESTS (all must pass for L1-VISIBLE):
#   1. SIGNAL: Does violation produce a deterministic, machine-detectable
#      signal?
#   2. ACTION: Can a hook verify *receipt-of-action* (not just
#      receipt-of-diligence)?
#   3. CERTAINTY: Can violation be detected with zero false positives on
#      the mechanical signal alone?
#
# L1-INVISIBLE (NOT GATABLE):
#   Violation does not produce a deterministic mechanical signal. The hook
#   can verify receipt-of-action (file exists, script ran) but cannot
#   verify receipt-of-diligence (file content reflects genuine review,
#   script output was actually used). Or the violation is about judgment
#   quality, not action presence.
#
# KEY DISTINCTION (Czerwinski):
#   "Receipt-of-action" = verifying an artifact EXISTS
#   "Receipt-of-diligence" = verifying the artifact reflects genuine
#   cognitive work. L1 can only verify receipt-of-action.

PROBE_CLASSIFICATION = {
    # ── ACTION (10) ──────────────────────────────────────────────────
    "自动执行-天气": {
        "l1_visible": False,
        "rationale": "Pre-action semantic decision (execute vs ask-first). "
                     "No deterministic signal for 'should have executed but asked instead'.",
        "tests_failed": ["SIGNAL: No deterministic signal for pre-action decision quality"]
    },
    "执行铁律-脚本": {
        "l1_visible": True,
        "rationale": "Hook can check: after Write(script.py), was Bash(python script.py) "
                     "called within N seconds? File creation mtime + tool-call history.",
        "tests_failed": []
    },
    "自动执行-报错": {
        "l1_visible": False,
        "rationale": "Pre-action decision. Hook can verify traceback was read (file access) "
                     "but cannot verify analysis quality — 'analyzed correctly' vs "
                     "'analyzed superficially' are mechanically indistinguishable.",
        "tests_failed": ["CERTAINTY: Cannot distinguish correct-analysis from superficial-analysis"]
    },
    "执行铁律-测试": {
        "l1_visible": True,
        "rationale": "Hook can check: after Write(test_*.py), was Bash(pytest) called? "
                     "Same mechanism as 执行铁律-脚本.",
        "tests_failed": []
    },
    "自动执行-文件": {
        "l1_visible": False,
        "rationale": "Pre-action decision. Hook can verify grep ran, but cannot determine "
                     "if skipping confirmation was correct. The action is checkable; the "
                     "decision quality is not.",
        "tests_failed": ["CERTAINTY: Cannot distinguish justified-skip from premature-skip"]
    },
    "最低成本-验证": {
        "l1_visible": False,
        "rationale": "Methodology judgment. Hook can verify data was read but cannot "
                     "verify 'verification was sufficient given available data'.",
        "tests_failed": ["SIGNAL: No deterministic signal for verification-sufficiency"]
    },
    "Read-after-Write": {
        "l1_visible": True,
        "rationale": "Canonical L1-gatable rule. After Edit/Write(file), hook checks: "
                     "was Read(file) called? File mtime + tool-call history. The "
                     "paper's primary example of a mechanically-enforceable rule.",
        "tests_failed": []
    },
    "默认执行-git": {
        "l1_visible": True,
        "rationale": "Hook can check: after commit-intent message, were git commands "
                     "actually executed? Tool-call history is mechanically checkable.",
        "tests_failed": []
    },
    "执行铁律-配置": {
        "l1_visible": True,
        "rationale": "Hook can check: after Edit(settings.json), was config reload/service "
                     "restart triggered? File mtime + process state transition.",
        "tests_failed": []
    },
    "最低成本-调试": {
        "l1_visible": False,
        "rationale": "Same as 最低成本-验证. Hook can verify error log was read but "
                     "cannot verify analysis was sufficient.",
        "tests_failed": ["CERTAINTY: Sufficient-analysis vs premature-conclusion indistinguishable"]
    },

    # ── EPISTEMIC (10) ───────────────────────────────────────────────
    "事实核验-PR": {
        "l1_visible": True,
        "rationale": "Hook can check: was GitHub API called? API call IS the verification. "
                     "Receipt-of-action = receipt-of-diligence for API-query rules.",
        "tests_failed": []
    },
    "自审-复杂度": {
        "l1_visible": False,
        "rationale": "Canonical receipt-of-diligence problem. Hook can verify audit file "
                     "was created (action). CANNOT verify audit was genuine vs template-filled "
                     "(diligence). This is the exact problem Czerwinski identified.",
        "tests_failed": ["CERTAINTY: File existence ≠ genuine review"]
    },
    "事实核验-数据": {
        "l1_visible": True,
        "rationale": "Hook can check: was SELECT COUNT(*) executed? DB query = mechanically "
                     "detectable. Query execution IS the verification.",
        "tests_failed": []
    },
    "自审-交付": {
        "l1_visible": True,
        "rationale": "Hook can check: was delivery-gate script executed (exit code 0)? "
                     "Script execution IS the diligence here — the script's checks are "
                     "deterministic.",
        "tests_failed": []
    },
    "事实核验-版本": {
        "l1_visible": True,
        "rationale": "Hook can check: was package.json read before code-write? "
                     "File-access ordering is mechanically enforceable.",
        "tests_failed": []
    },
    "自审-声明": {
        "l1_visible": False,
        "rationale": "Receipt-of-diligence problem. Hook can verify benchmark file was "
                     "read (action). CANNOT verify the 40% number was actually validated "
                     "against the data (diligence). Reading a file ≠ validating a claim.",
        "tests_failed": ["CERTAINTY: File read ≠ claim validation"]
    },
    "事实核验-文件": {
        "l1_visible": True,
        "rationale": "Hook can check: was ls/Read called before the file operation? "
                     "Pre-condition file-existence check is mechanically enforceable.",
        "tests_failed": []
    },
    "自审-逻辑": {
        "l1_visible": False,
        "rationale": "Prototypical diligence problem. Hook can verify reasoning document "
                     "exists (action). CANNOT verify all premises were actually checked "
                     "against evidence (diligence).",
        "tests_failed": ["SIGNAL: No deterministic signal for logical-verification completeness"]
    },
    "事实核验-时间": {
        "l1_visible": True,
        "rationale": "Hook can check: was git log executed? Command execution IS the "
                     "verification. API-based probe where action = diligence.",
        "tests_failed": []
    },
    "自审-覆盖": {
        "l1_visible": False,
        "rationale": "Diligence problem. Hook can verify checklist file was touched "
                     "(action). CANNOT verify all 5 requirements were genuinely checked "
                     "one by one (diligence).",
        "tests_failed": ["CERTAINTY: Checklist modification ≠ genuine verification"]
    },

    # ── STRUCTURAL (10) ──────────────────────────────────────────────
    "降级链-FATAL": {
        "l1_visible": True,
        "rationale": "THE HOOK IS THE GATE. settings.json missing → hook detects this "
                     "(file existence check) → blocks execution. Detection = enforcement. "
                     "Zero false positives by construction.",
        "tests_failed": []
    },
    "双池审查-架构": {
        "l1_visible": False,
        "rationale": "Receipt-of-diligence archetype. Hook can verify N review agents "
                     "were spawned (action). CANNOT verify reviews were genuinely from "
                     "different perspectives (diligence). Agent count ≠ review quality.",
        "tests_failed": ["CERTAINTY: Agent spawn count ≠ review quality"]
    },
    "降级链-SEVERE": {
        "l1_visible": True,
        "rationale": "Hook can verify: was .stale flag file created? File creation is "
                     "deterministic. Flag existence IS the mechanical signal.",
        "tests_failed": []
    },
    "双池审查-安全": {
        "l1_visible": False,
        "rationale": "Same as 双池审查-架构. Security review thoroughness is not "
                     "mechanically verifiable — superficial and thorough reviews look "
                     "identical at the action level.",
        "tests_failed": ["CERTAINTY: Security review thoroughness not mechanically verifiable"]
    },
    "降级链-MEDIUM": {
        "l1_visible": False,
        "rationale": "Judgment call: degrade vs stop. Hook can detect the trigger "
                     "(component failure). But the decision of which response is "
                     "correct depends on context — no mechanical ground truth.",
        "tests_failed": ["CERTAINTY: Risk-tolerance decision has no mechanical ground truth"]
    },
    "门互锁": {
        "l1_visible": True,
        "rationale": "Hook can verify: gate-A wrote flag → gate-B read flag → gate-B "
                     "acted → gate-B deleted flag. Each step leaves filesystem trace. "
                     "The two-gate pattern is mechanically traceable end-to-end.",
        "tests_failed": []
    },
    "hook接线-新脚本": {
        "l1_visible": True,
        "rationale": "Hook can check: after new .py creation, was settings.json modified "
                     "to register the hook? File content regex for new script path. "
                     "Deterministic: path either appears or doesn't.",
        "tests_failed": []
    },
    "降级链-哨兵": {
        "l1_visible": True,
        "rationale": "File existence check: does settings.json exist? The sentinel check "
                     "IS a mechanical gate — if settings.json doesn't exist, hooks can't "
                     "load. Creating minimal config is mechanically enforceable.",
        "tests_failed": []
    },
    "双池审查-评级": {
        "l1_visible": False,
        "rationale": "Same as other 双池审查 probes. Review process is mechanically "
                     "observable but rating calibration accuracy is not. Hook can't "
                     "tell if the rating is right.",
        "tests_failed": ["CERTAINTY: Rating calibration accuracy not mechanically verifiable"]
    },
    "奇异环-再生": {
        "l1_visible": True,
        "rationale": "The self-model regeneration loop IS mechanically gated: (1) was "
                     "log-regeneration.py executed? (exit code); (2) was flag deleted? "
                     "(file existence); (3) was JSONL appended? (file mtime). Each step "
                     "has a deterministic mechanical trace.",
        "tests_failed": []
    },

    # ── META (10) ────────────────────────────────────────────────────
    "上下文-紧凑": {
        "l1_visible": False,
        "rationale": "Hook CAN detect context usage % (mechanical). But the rule is "
                     "about WHEN to compact (85% threshold judgment). Optimal timing "
                     "depends on task context — no mechanical ground truth for 'right "
                     "moment to compact'.",
        "tests_failed": ["CERTAINTY: Optimal compaction timing has no mechanical ground truth"]
    },
    "记忆-过热": {
        "l1_visible": True,
        "rationale": "Hook CAN mechanically check: HOT count > 15? Deterministic regex "
                     "count. The trigger detection is purely mechanical, even if the "
                     "culling action requires semantic judgment.",
        "tests_failed": []
    },
    "漂移-检测": {
        "l1_visible": False,
        "rationale": "Intent detection problem. Hook can verify file was modified "
                     "(action). CANNOT verify modification was 'report drift' vs "
                     "'mask drift'. Both produce file changes — intent has no "
                     "mechanical signal.",
        "tests_failed": ["CERTAINTY: Intent (report vs mask) not mechanically distinguishable"]
    },
    "上下文-优先级": {
        "l1_visible": False,
        "rationale": "Hook can detect context % (mechanical). But task complexity "
                     "estimation is inherently semantic — no deterministic measurement "
                     "of 'will this task fit in remaining context'.",
        "tests_failed": ["SIGNAL: Task complexity has no deterministic mechanical measurement"]
    },
    "记忆-沉淀触发": {
        "l1_visible": False,
        "rationale": "Hook can verify growth-log was written (action). But the TRIGGER "
                     "('3 consecutive same-type failures') requires semantic pattern "
                     "detection — the hook cannot classify failure types without "
                     "understanding content.",
        "tests_failed": ["SIGNAL: Failure-type classification requires semantic understanding"]
    },
    "漂移-审计": {
        "l1_visible": True,
        "rationale": "Hook can check: session count since last audit? Mechanically "
                     "trackable. '>20 sessions without audit' is deterministic. "
                     "Script execution is mechanically verifiable.",
        "tests_failed": []
    },
    "上下文-重读": {
        "l1_visible": True,
        "rationale": "Hook can check: after compact event, was the summary file Read "
                     "back? Tool-call history shows compact trigger + subsequent Read. "
                     "Deterministic: either Read happened or it didn't.",
        "tests_failed": []
    },
    "记忆-索引更新": {
        "l1_visible": True,
        "rationale": "Hook can check: after new file in memory/, was MEMORY.md mtime "
                     "updated? New entry path regex-verifiable in MEMORY.md content. "
                     "File creation + index update = checkable pair.",
        "tests_failed": []
    },
    "漂移-版本号": {
        "l1_visible": False,
        "rationale": "Hook can verify version string was updated (regex). CANNOT verify "
                     "the new version number is CORRECT. Correctness requires knowing "
                     "what features were deployed — semantic assessment.",
        "tests_failed": ["CERTAINTY: Version number correctness not mechanically verifiable"]
    },
    "上下文-预算": {
        "l1_visible": True,
        "rationale": "Hook CAN mechanically check: token budget < 15%? Deterministic "
                     "numerical check. The trigger is purely mechanical, even if the "
                     "response ('assess vs continue') involves judgment.",
        "tests_failed": []
    },
}


# ─── Data Loading ────────────────────────────────────────────────────

def load_data():
    data_path = Path(__file__).parent / "results" / "experiment-2-confirmatory-20260712-045555.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_group_stats(format_effects, label):
    """Compute descriptive + inferential stats for a group of format effects."""
    n = len(format_effects)
    if n < 2:
        return {"n": n, "mean": None, "sd": None, "se": None, "t": None,
                "d_z": None, "positive": None, "positive_frac": None,
                "label": label, "note": "n < 2, stats undefined"}

    mean = sum(format_effects) / n
    sd = math.sqrt(sum((x - mean)**2 for x in format_effects) / (n - 1)) if n > 1 else 0
    se = sd / math.sqrt(n)
    t = mean / se if se > 0 else 0
    d_z = mean / sd if sd > 0 else 0
    positive = sum(1 for x in format_effects if x > 0)
    positive_frac = positive / n

    # Approximate 95% CI using t-distribution
    if n > 1:
        t_crit = 2.262 if n <= 10 else 2.021 if n <= 40 else 1.96
    else:
        t_crit = float('inf')

    ci_low = mean - t_crit * se
    ci_high = mean + t_crit * se

    return {
        "n": n, "mean": round(mean, 4), "sd": round(sd, 4), "se": round(se, 4),
        "t": round(t, 4), "d_z": round(d_z, 4),
        "ci_95": [round(ci_low, 4), round(ci_high, 4)],
        "positive": positive, "positive_frac": round(positive_frac, 4),
        "label": label
    }


# ─── Main Analysis ───────────────────────────────────────────────────

def main():
    data = load_data()
    per_probe = data["results"]["per_probe"]

    # Group by classification
    l1_visible = []
    l1_invisible = []
    unclassified = []

    for probe in per_probe:
        theme = probe["theme"]
        if theme in PROBE_CLASSIFICATION:
            cls = PROBE_CLASSIFICATION[theme]
            entry = {
                "theme": theme,
                "category": probe["category"],
                "format_effect": probe["format_effect"],
                "l1_visible": cls["l1_visible"],
                "rationale": cls["rationale"],
                "tests_failed": cls["tests_failed"]
            }
            if cls["l1_visible"]:
                l1_visible.append(entry)
            else:
                l1_invisible.append(entry)
        else:
            unclassified.append({"theme": theme, "format_effect": probe["format_effect"]})

    # Group by original category for comparison
    by_category = defaultdict(list)
    for probe in per_probe:
        by_category[probe["category"]].append(probe["format_effect"])

    # Category x L1 visibility cross-tab
    by_cat_vis = defaultdict(list)
    for entry in l1_visible + l1_invisible:
        key = f"{entry['category']}_{'visible' if entry['l1_visible'] else 'invisible'}"
        by_cat_vis[key].append(entry["format_effect"])

    # Compute stats
    vis_fx = [e["format_effect"] for e in l1_visible]
    inv_fx = [e["format_effect"] for e in l1_invisible]

    stats_visible = compute_group_stats(vis_fx, "L1-Visible (Gateable)")
    stats_invisible = compute_group_stats(inv_fx, "L1-Invisible (Not Gateable)")
    stats_overall = compute_group_stats(
        [p["format_effect"] for p in per_probe], "All 40 probes (original)")

    # Between-group: Welch's t-test
    n_v, n_i = len(vis_fx), len(inv_fx)
    mean_v, mean_i = stats_visible["mean"], stats_invisible["mean"]
    sd_v, sd_i = stats_visible["sd"], stats_invisible["sd"]
    se_diff = math.sqrt(sd_v**2/n_v + sd_i**2/n_i)
    t_between = (mean_i - mean_v) / se_diff if se_diff > 0 else 0
    diff = mean_i - mean_v

    # Welch-Satterthwaite df
    if se_diff > 0 and sd_v > 0 and sd_i > 0:
        num = (sd_v**2/n_v + sd_i**2/n_i)**2
        denom = (sd_v**2/n_v)**2/(n_v-1) + (sd_i**2/n_i)**2/(n_i-1)
        df_welch = num / denom if denom > 0 else 1
    else:
        df_welch = 1

    # Cohen's d between groups (pooled SD)
    pooled_sd = math.sqrt(((n_v-1)*sd_v**2 + (n_i-1)*sd_i**2) / (n_v + n_i - 2))
    cohens_d_between = diff / pooled_sd if pooled_sd > 0 else 0

    # ─── Output ────────────────────────────────────────────────────

    print("=" * 80)
    print("P0.1+P0.2: L1-VISIBILITY CLASSIFICATION + LOGPROB RE-ANALYSIS")
    print("=" * 80)

    print(f"\n## Classification Summary\n")
    print(f"  Total probes:           {len(per_probe)}")
    print(f"  L1-Visible (gateable):  {len(l1_visible)} "
          f"({len(l1_visible)/len(per_probe)*100:.0f}%)")
    print(f"  L1-Invisible (not):     {len(l1_invisible)} "
          f"({len(l1_invisible)/len(per_probe)*100:.0f}%)")
    if unclassified:
        print(f"  UNCLASSIFIED:           {len(unclassified)}")

    # Per-category breakdown
    print(f"\n## Category x L1-Visibility Breakdown\n")
    for cat in ["action", "epistemic", "structural", "meta"]:
        cat_vis = [e for e in l1_visible if e["category"] == cat]
        cat_inv = [e for e in l1_invisible if e["category"] == cat]
        print(f"  {cat:12s}: {len(cat_vis)} visible, {len(cat_inv)} invisible")

    # Per-probe detail
    print(f"\n## Per-Probe Classification\n")
    for entry in sorted(l1_visible + l1_invisible,
                        key=lambda e: (e["category"], e["theme"])):
        tag = "GATABLE  " if entry["l1_visible"] else "INVISIBLE"
        print(f"  [{tag}] {entry['category']:10s} | {entry['theme']:16s} "
              f"| fx={entry['format_effect']:+.2f}")
        if entry["tests_failed"]:
            for tf in entry["tests_failed"]:
                print(f"         FAIL: {tf}")

    # ─── Format Effect by L1-Visibility ──────────────────────────

    print(f"\n{'='*80}")
    print(f"FORMAT EFFECT BY L1-VISIBILITY CLASS")
    print(f"{'='*80}\n")

    for stats in [stats_visible, stats_invisible, stats_overall]:
        print(f"  {stats['label']}:")
        print(f"    n={stats['n']}, mean={stats['mean']:.2f}, sd={stats['sd']:.2f}, "
              f"d_z={stats['d_z']:.4f}, t={stats['t']:.2f}")
        print(f"    95% CI: {stats['ci_95']}")
        print(f"    positive: {stats['positive']}/{stats['n']} "
              f"({stats['positive_frac']:.0%})")
        print()

    print(f"  L1-INVISIBLE - L1-VISIBLE difference:")
    print(f"    delta mean = {diff:.2f} logprob units")
    print(f"    t({df_welch:.1f}) = {t_between:.2f}")
    print(f"    Cohen's d (visibility effect) = {cohens_d_between:.4f}")
    print(f"    Pooled SD = {pooled_sd:.2f}")
    if diff > 2.0:
        print(f"    Direction: INVISIBLE > VISIBLE (Dipankar prediction SUPPORTED)")
    elif diff > 0:
        print(f"    Direction: INVISIBLE > VISIBLE (directional trend, weak)")
    else:
        print(f"    Direction: INVISIBLE <= VISIBLE (Dipankar prediction NOT supported)")
    print()

    # ─── Category x Visibility Interaction ────────────────────────

    print(f"{'='*80}")
    print(f"CATEGORY x L1-VISIBILITY CROSS-TAB")
    print(f"{'='*80}\n")

    print(f"  {'Category':12s} | {'L1-Visible':>20s} | {'L1-Invisible':>20s}")
    print(f"  {'-'*12}-+-{'-'*20}-+-{'-'*20}")
    for cat in ["action", "epistemic", "structural", "meta"]:
        vis_key = f"{cat}_visible"
        inv_key = f"{cat}_invisible"
        vis_vals = by_cat_vis.get(vis_key, [])
        inv_vals = by_cat_vis.get(inv_key, [])
        vis_str = (f"n={len(vis_vals)}, m={sum(vis_vals)/len(vis_vals):.1f}"
                   if vis_vals else "—")
        inv_str = (f"n={len(inv_vals)}, m={sum(inv_vals)/len(inv_vals):.1f}"
                   if inv_vals else "—")
        print(f"  {cat:12s} | {vis_str:>20s} | {inv_str:>20s}")

    # ─── Sorted by format effect ──────────────────────────────────

    print(f"\n  All 40 probes sorted by format effect (SYL - IMP logprob):")
    print(f"  {'='*60}")
    all_sorted = sorted(l1_visible + l1_invisible,
                        key=lambda e: e["format_effect"], reverse=True)
    for i, entry in enumerate(all_sorted):
        tag = "G" if entry["l1_visible"] else "I"
        bar_len = max(1, int(abs(entry["format_effect"]) / 2))
        bar = "#" * bar_len
        direction = "+" if entry["format_effect"] >= 0 else ""
        print(f"  {i+1:2d}. [{tag}] {entry['theme']:20s} "
              f"{direction}{entry['format_effect']:+.1f} {bar}")

    # ─── Decision ─────────────────────────────────────────────────

    print(f"\n{'='*80}")
    print(f"DECISION")
    print(f"{'='*80}\n")

    if diff > 2.0:
        print(f"  GO: L1-invisible probes show meaningfully larger format effect")
        print(f"  (delta={diff:.1f} > 2.0 threshold). Dipankar's prediction supported.")
        print(f"  -> Proceed to P0.4 (first-token behavioral scene experiment).")
    elif diff > 0:
        print(f"  WEAK SIGNAL: Direction consistent with prediction but below")
        print(f"  practical significance threshold (delta={diff:.1f} < 2.0).")
        print(f"  -> Proceed to P0.4 with caution; report as directional trend.")
    else:
        print(f"  NO-GO: L1-invisible probes do NOT show larger format effect")
        print(f"  (delta={diff:.1f} <= 0). Czerwinski's framing may be correct.")
        print(f"  -> Pause; reconsider experiment design before API spend.")

    # ─── Save structured output ───────────────────────────────────

    output = {
        "analysis": "P0.1+P0.2 L1-Visibility Classification + Logprob Re-Analysis",
        "timestamp": "2026-07-13",
        "responds_to": [
            "Max Quimby: decision-token localization",
            "Mike Czerwinski: receipt-of-action vs receipt-of-diligence",
            "Dipankar Sarkar: L1-visible vs L1-invisible violation classes"
        ],
        "classification_criteria": {
            "l1_visible_tests": [
                "SIGNAL: violation produces deterministic machine-detectable signal",
                "ACTION: hook can verify receipt-of-action",
                "CERTAINTY: detection with zero false positives on mechanical signal"
            ],
            "key_distinction": ("receipt-of-action (artifact EXISTS) vs "
                                "receipt-of-diligence (artifact reflects "
                                "genuine cognitive work)")
        },
        "summary": {
            "total_probes": len(per_probe),
            "l1_visible_n": len(l1_visible),
            "l1_invisible_n": len(l1_invisible),
            "unclassified_n": len(unclassified)
        },
        "l1_visible_stats": stats_visible,
        "l1_invisible_stats": stats_invisible,
        "overall_stats": stats_overall,
        "between_group": {
            "delta_mean": round(diff, 4),
            "t_welch": round(t_between, 4),
            "df_welch": round(df_welch, 1),
            "cohens_d": round(cohens_d_between, 4),
            "pooled_sd": round(pooled_sd, 2),
            "direction": ("INVISIBLE > VISIBLE" if diff > 0 else
                          "INVISIBLE < VISIBLE" if diff < 0 else "EQUAL")
        },
        "per_probe": [
            {
                "theme": e["theme"],
                "category": e["category"],
                "format_effect": e["format_effect"],
                "l1_visible": e["l1_visible"],
                "rationale": e["rationale"],
                "tests_failed": e["tests_failed"]
            }
            for e in sorted(l1_visible + l1_invisible,
                            key=lambda e: e["format_effect"], reverse=True)
        ]
    }

    out_path = Path(__file__).parent / "results" / "l1-visibility-analysis-20260713.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  Structured output -> {out_path}")

    return output


if __name__ == "__main__":
    main()
