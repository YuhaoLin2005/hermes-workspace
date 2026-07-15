#!/usr/bin/env python3
"""Comprehensive analysis of Mike's Prose+Gate experiment.
Reads experiment JSON -> descriptive stats, hypothesis tests, per-rule breakdown, effect sizes.
"""

from __future__ import annotations
import json, sys, statistics
from pathlib import Path
from collections import defaultdict


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("results", data.get("trials", []))
    return []


def cohens_d(a: list[float], b: list[float]) -> float:
    ma, mb = statistics.mean(a), statistics.mean(b)
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return ma - mb
    va = statistics.variance(a) if na > 1 else 0
    vb = statistics.variance(b) if nb > 1 else 0
    pooled_sd = (((na - 1) * va + (nb - 1) * vb) / (na + nb - 2)) ** 0.5
    if pooled_sd == 0:
        return float("inf") if ma != mb else 0.0
    return (ma - mb) / pooled_sd


def analyze(results: list[dict]) -> dict:
    groups = defaultdict(lambda: {"compliance": [], "reasoning": [],
                                   "breakdowns": [], "per_rule": defaultdict(list)})
    for r in results:
        if "error" in r:
            continue
        k = f"{r['format']}_{r['gate']}"
        groups[k]["compliance"].append(r["compliance"])
        groups[k]["reasoning"].append(r["reasoning"])
        groups[k]["breakdowns"].append(r.get("breakdown", {}))
        groups[k]["per_rule"][r["rule_id"]].append({
            "compliance": r["compliance"], "reasoning": r["reasoning"],
            "breakdown": r.get("breakdown", {}),
        })

    # 1. Per-condition
    conditions = {}
    for k, v in sorted(groups.items()):
        comp = v["compliance"]; reas = v["reasoning"]; nv = len(comp)
        if nv == 0:
            continue
        avg_bd = {}
        for bd_key in ["causal", "alt", "evidence", "meta", "struct"]:
            vals = [b.get(bd_key, 0) for b in v["breakdowns"] if b]
            avg_bd[bd_key] = round(statistics.mean(vals), 2) if vals else 0
        conditions[k] = {
            "n": nv,
            "compliance_mean": round(statistics.mean(comp), 3),
            "compliance_sd": round(statistics.stdev(comp), 3) if nv > 1 else 0,
            "compliance_rate": round(sum(1 for c in comp if c >= 0.5) / nv, 3),
            "reasoning_mean": round(statistics.mean(reas), 2),
            "reasoning_sd": round(statistics.stdev(reas), 2) if nv > 1 else 0,
            "reasoning_median": round(statistics.median(reas), 2),
            "avg_breakdown": avg_bd,
        }

    # 2. Primary hypothesis
    ht = {}
    if "prose_ON" in conditions and "code_ON" in conditions:
        pr = conditions["prose_ON"]["reasoning_mean"]
        cr = conditions["code_ON"]["reasoning_mean"]
        pc = conditions["prose_ON"]["compliance_rate"]
        cc = conditions["code_ON"]["compliance_rate"]
        prose_reas = groups["prose_ON"]["reasoning"]
        code_reas = groups["code_ON"]["reasoning"]
        d = cohens_d(prose_reas, code_reas)

        ht["primary"] = {
            "hypothesis": "Prose+Gate outperforms Code+Gate on reasoning while maintaining compliance",
            "prose_gate_ON": {"compliance_rate": pc, "reasoning_mean": pr,
                            "reasoning_sd": conditions["prose_ON"]["reasoning_sd"]},
            "code_gate_ON": {"compliance_rate": cc, "reasoning_mean": cr,
                           "reasoning_sd": conditions["code_ON"]["reasoning_sd"]},
            "delta_reasoning": round(pr - cr, 2),
            "delta_compliance": round(pc - cc, 3),
            "cohens_d_reasoning": round(d, 3),
        }
        if "code_OFF" in conditions:
            ceiling = conditions["code_OFF"]["reasoning_mean"]
            ht["primary"]["code_gate_OFF_ceiling"] = ceiling
            ht["primary"]["gap_to_ceiling"] = round(ceiling - pr, 2)
            ht["primary"]["pct_of_ceiling"] = round(pr / ceiling * 100, 1) if ceiling else None

        if pr > cr and d >= 0.5 and pc >= 0.9:
            ht["primary"]["verdict"] = "SUPPORTED"
        elif pr > cr and d >= 0.2:
            ht["primary"]["verdict"] = "WEAKLY SUPPORTED"
        elif abs(pr - cr) < 0.1:
            ht["primary"]["verdict"] = "NEUTRAL"
        else:
            ht["primary"]["verdict"] = "NOT SUPPORTED"

    # 3. Format effect (gate OFF)
    if "prose_OFF" in conditions and "code_OFF" in conditions:
        poff_r = groups["prose_OFF"]["reasoning"]
        coff_r = groups["code_OFF"]["reasoning"]
        ht["format_effect_gate_off"] = {
            "prose_OFF_reasoning": conditions["prose_OFF"]["reasoning_mean"],
            "code_OFF_reasoning": conditions["code_OFF"]["reasoning_mean"],
            "delta": round(conditions["prose_OFF"]["reasoning_mean"] - conditions["code_OFF"]["reasoning_mean"], 2),
            "cohens_d": round(cohens_d(poff_r, coff_r), 3),
        }

    # 4. Gate effect within prose
    if "prose_ON" in conditions and "prose_OFF" in conditions:
        pon_r = groups["prose_ON"]["reasoning"]; poff_r = groups["prose_OFF"]["reasoning"]
        pon_c = groups["prose_ON"]["compliance"]; poff_c = groups["prose_OFF"]["compliance"]
        ht["gate_effect_within_prose"] = {
            "gate_ON_reasoning": conditions["prose_ON"]["reasoning_mean"],
            "gate_OFF_reasoning": conditions["prose_OFF"]["reasoning_mean"],
            "gate_ON_compliance": round(statistics.mean(pon_c), 3),
            "gate_OFF_compliance": round(statistics.mean(poff_c), 3),
            "delta_reasoning": round(conditions["prose_ON"]["reasoning_mean"] - conditions["prose_OFF"]["reasoning_mean"], 2),
            "delta_compliance": round(statistics.mean(pon_c) - statistics.mean(poff_c), 3),
            "cohens_d_reasoning": round(cohens_d(pon_r, poff_r), 3),
        }

    # 5. Gate effect within code
    if "code_ON" in conditions and "code_OFF" in conditions:
        con_r = groups["code_ON"]["reasoning"]; coff_r = groups["code_OFF"]["reasoning"]
        con_c = groups["code_ON"]["compliance"]; coff_c = groups["code_OFF"]["compliance"]
        ht["gate_effect_within_code"] = {
            "gate_ON_reasoning": conditions["code_ON"]["reasoning_mean"],
            "gate_OFF_reasoning": conditions["code_OFF"]["reasoning_mean"],
            "gate_ON_compliance": round(statistics.mean(con_c), 3),
            "gate_OFF_compliance": round(statistics.mean(coff_c), 3),
            "delta_reasoning": round(conditions["code_ON"]["reasoning_mean"] - conditions["code_OFF"]["reasoning_mean"], 2),
            "delta_compliance": round(statistics.mean(con_c) - statistics.mean(coff_c), 3),
            "cohens_d_reasoning": round(cohens_d(con_r, coff_r), 3),
        }

    # 6. Per-rule
    per_rule = {}
    all_rule_ids = set()
    for g in groups.values():
        all_rule_ids.update(g["per_rule"].keys())
    for rid in sorted(all_rule_ids):
        per_rule[rid] = {}
        for k in sorted(groups.keys()):
            entries = groups[k]["per_rule"].get(rid, [])
            if not entries:
                continue
            comps = [e["compliance"] for e in entries]
            reas = [e["reasoning"] for e in entries]
            per_rule[rid][k] = {
                "n": len(entries),
                "compliance_mean": round(statistics.mean(comps), 3),
                "reasoning_mean": round(statistics.mean(reas), 2),
                "reasoning_sd": round(statistics.stdev(reas), 2) if len(reas) > 1 else 0,
            }

    # 7. Summary
    primary = ht.get("primary", {})
    gate_prose = ht.get("gate_effect_within_prose", {})
    gate_code = ht.get("gate_effect_within_code", {})
    format_off = ht.get("format_effect_gate_off", {})

    findings = []
    pc = primary.get("prose_gate_ON", {}).get("compliance_rate", 0)
    cc = primary.get("code_gate_ON", {}).get("compliance_rate", 0)
    if pc >= cc * 0.95:
        findings.append(f"Q1 (compliance parity): YES -- prose={pc:.1%} vs code={cc:.1%}")
    else:
        findings.append(f"Q1 (compliance parity): PARTIAL -- prose={pc:.1%} vs code={cc:.1%}")

    delta = primary.get("delta_reasoning", 0)
    d_val = primary.get("cohens_d_reasoning", 0)
    if delta > 0.2 and d_val >= 0.5:
        findings.append(f"Q2 (reasoning boost): YES -- delta=+{delta:.2f}, d={d_val:.2f}")
    elif delta > 0:
        findings.append(f"Q2 (reasoning boost): WEAK -- delta=+{delta:.2f}, d={d_val:.2f}")
    else:
        findings.append(f"Q2 (reasoning boost): NO -- delta={delta:.2f}")

    fd = format_off.get("delta", 0)
    findings.append(f"Q3 (format alone): prose_OFF vs code_OFF delta={fd:+.2f}")

    gpd = gate_prose.get("delta_reasoning", 0)
    gcd = gate_code.get("delta_reasoning", 0)
    findings.append(f"Q4 (gate suppression): prose gate cost={gpd:+.2f}, code gate cost={gcd:+.2f}")

    gap = primary.get("gap_to_ceiling")
    pct = primary.get("pct_of_ceiling")
    if gap is not None and pct is not None:
        findings.append(f"Q5 (ceiling): prose_gate_ON reaches {pct}% of code_gate_OFF ceiling (gap={gap:.2f})")

    summary = {
        "verdict": primary.get("verdict", "unknown"),
        "key_findings": findings,
    }

    return {
        "conditions": conditions,
        "hypothesis_tests": ht,
        "per_rule": per_rule,
        "total_valid": len(results),
        "total_errors": sum(1 for r in results if "error" in r),
        "summary": summary,
    }


def print_report(analysis: dict):
    print("=" * 70)
    print("  MIKE'S EXPERIMENT -- FULL ANALYSIS")
    print("=" * 70)

    print("\n-- 1. Per-Condition Summary --\n")
    for k, s in analysis["conditions"].items():
        bd = s["avg_breakdown"]
        print(f"  {k}:")
        print(f"    n={s['n']}, compliance={s['compliance_mean']:.3f}+/-{s['compliance_sd']:.3f} "
              f"(rate={s['compliance_rate']:.1%})")
        print(f"    reasoning={s['reasoning_mean']:.2f}+/-{s['reasoning_sd']:.2f} "
              f"(median={s['reasoning_median']:.2f})")
        print(f"    bd: causal={bd['causal']}, alt={bd['alt']}, ev={bd['evidence']}, "
              f"meta={bd['meta']}, struct={bd['struct']}")

    ht = analysis["hypothesis_tests"]
    p = ht.get("primary", {})
    print("\n-- 2. Primary Hypothesis --\n")
    for k, v in p.items():
        if k not in ("verdict", "hypothesis"):
            print(f"  {k}: {v}")
    print(f"\n  >> VERDICT: {p.get('verdict', 'N/A')}")

    fe = ht.get("format_effect_gate_off", {})
    if fe:
        print("\n-- 3. Format Effect (Gate OFF) --\n")
        for k, v in fe.items():
            print(f"  {k}: {v}")

    ge_p = ht.get("gate_effect_within_prose", {})
    if ge_p:
        print("\n-- 4. Gate Effect Within Prose --\n")
        for k, v in ge_p.items():
            print(f"  {k}: {v}")

    ge_c = ht.get("gate_effect_within_code", {})
    if ge_c:
        print("\n-- 5. Gate Effect Within Code --\n")
        for k, v in ge_c.items():
            print(f"  {k}: {v}")

    print("\n-- 6. Per-Rule Breakdown --\n")
    for rid, conds in analysis["per_rule"].items():
        print(f"  {rid}:")
        for ck, cs in conds.items():
            print(f"    {ck}: comp={cs['compliance_mean']:.3f}, "
                  f"reas={cs['reasoning_mean']:.2f}+/-{cs['reasoning_sd']:.2f} (n={cs['n']})")

    print("\n-- 7. Bottom Line --\n")
    for line in analysis["summary"]["key_findings"]:
        print(f"  {line}")
    print(f"\n  VERDICT: {analysis['summary']['verdict']}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_mike_full.py <experiment.json> [--json]")
        sys.exit(1)

    results = load(sys.argv[1])
    if not results:
        print(f"ERROR: No results found in {sys.argv[1]}")
        sys.exit(1)

    if isinstance(results, dict):
        raw = results.get("results", results.get("trials", []))
        if raw:
            results = raw

    analysis = analyze(results)

    if "--json" in sys.argv:
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
    else:
        print_report(analysis)

    out = Path(sys.argv[1]).with_suffix(".analysis.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"\nSaved analysis to {out}")
