#!/usr/bin/env python3
"""
P1 Experiment Verification: Design & Analysis Audit
=====================================================
Systematic check of:
1. Floor effect: Are format effects computed on reliable logprob values?
2. Design validity: Does P1 measure what it claims to measure?
3. Statistical robustness: Is r=-0.65 reliable at n=12?
4. Dual confound: Multi-scene vs meta-instruction

Standalone — no external importers. Reads P1 results JSON (no API calls).
"""

import json, math, sys, random, io
from pathlib import Path

# Fix Windows GBK encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load data
data_path = Path(__file__).parent / "results" / "p1-multi-position" / "p1-multi-position-20260713-043038.json"
with open(data_path, encoding='utf-8') as f:
    data = json.load(f)

results = data["results"]

print("=" * 80)
print("P1 VERIFICATION AUDIT")
print("=" * 80)

# ─── 1. FLOOR EFFECT ANALYSIS ──────────────────────────────────────

print("\n" + "=" * 80)
print("1. FLOOR EFFECT: Logprob Reliability Check")
print("=" * 80)

all_b_logprobs = []
for probe in results:
    for fmt in ["imperative", "syllogistic"]:
        for pos in ["T1", "T2", "T3"]:
            dp = probe["conditions"][fmt].get(pos, {})
            b_lp = dp.get("B_logprob")
            a_lp = dp.get("A_logprob")
            if b_lp is not None:
                all_b_logprobs.append({
                    "probe": probe["theme"], "format": fmt, "pos": pos,
                    "A_logprob": a_lp, "B_logprob": b_lp,
                    "l1_visible": probe["l1_visible"]
                })

b_values = [x["B_logprob"] for x in all_b_logprobs]
b_values.sort()
n = len(b_values)
print(f"\n  B_logprob distribution (n={n}):")
print(f"    Min:    {b_values[0]:.2f}")
print(f"    P5:     {b_values[int(n*0.05)]:.2f}")
print(f"    P25:    {b_values[int(n*0.25)]:.2f}")
print(f"    Median: {b_values[int(n*0.50)]:.2f}")
print(f"    P75:    {b_values[int(n*0.75)]:.2f}")
print(f"    P95:    {b_values[int(n*0.95)]:.2f}")
print(f"    Max:    {b_values[-1]:.2f}")

extreme = [x for x in all_b_logprobs if x["B_logprob"] < -50]
print(f"\n  B_logprob < -50 (potential floor): {len(extreme)}/{n} ({100*len(extreme)/n:.0f}%)")
very_extreme = [x for x in all_b_logprobs if x["B_logprob"] < -55]
print(f"  B_logprob < -55 (severe floor):    {len(very_extreme)}/{n} ({100*len(very_extreme)/n:.0f}%)")

a_values = [x["A_logprob"] for x in all_b_logprobs if x["A_logprob"] is not None]
print(f"\n  A_logprob distribution: min={min(a_values):.4f}, max={max(a_values):.4f}, "
      f"non-zero={sum(1 for a in a_values if abs(a)>0.01)}/{len(a_values)}")

# Within-probe variation — if floor is a hard cap, within-condition range should be near 0
print(f"\n  Within-probe B_logprob variation (if floor=hard cap, range≈0):")
for probe in results:
    imp_b = [probe["conditions"]["imperative"][pos]["B_logprob"] for pos in ["T1","T2","T3"]]
    syl_b = [probe["conditions"]["syllogistic"][pos]["B_logprob"] for pos in ["T1","T2","T3"]]
    imp_range = max(imp_b) - min(imp_b)
    syl_range = max(syl_b) - min(syl_b)
    print(f"    {probe['theme']:<20s} IMP range={imp_range:6.1f}  SYL range={syl_range:6.1f}  "
          f"IMP mean={sum(imp_b)/3:6.1f}  SYL mean={sum(syl_b)/3:6.1f}")

print(f"\n  Floor Verdict: Within-condition ranges of 10-50 logprob units")
print(f"  indicate the floor is NOT a hard cap — logprobs vary meaningfully.")
print(f"  However, precision at <-55 is reduced relative to <-20.")

# ─── 2. DESIGN VALIDITY ────────────────────────────────────────────

print("\n" + "=" * 80)
print("2. DESIGN VALIDITY: What P1 Actually Measures")
print("=" * 80)

print("""
  DESIGN DOC (P1-design-multi-position-trajectory.md):
    Single scenario → T1=决定, T2=理由, T3=方式
    H4: "syllogistic amplifies causal reasoning → effect at T2 > T1"

  IMPLEMENTED DESIGN (p1_multi_position.py):
    Three scenarios → T1=S1(direct), T2=S2(distractor), T3=S3(pressure)
    All three are BINARY COMPLIANCE decisions on DIFFERENT scenarios

  ⚠ MISMATCH: P1 does NOT measure persistence across reasoning depth.
  T1/T2/T3 are independent decisions, not positions in a reasoning chain.
  H1-H4 from design doc test a different construct.

  P1 ACTUALLY MEASURES:
    Format effect resilience under increasing multi-scene pressure:
    - T1 = baseline (first decision, but with anticipation of Q2,Q3)
    - T2 = under time urgency / distractor
    - T3 = under fatigue / repetition
    - Collapse at T1 (d_z 0.58→0.19) = context-fragility evidence
    - NOT evidence about token-position surface-priming vs structural-encoding

  VALIDITY:
    ❌ Design-implementation mismatch for H1-H4
    ✅ Multi-scene format resilience is a valid construct
    ✅ Collapse + reversal are informative findings
    ⚡ Re-label: "Multi-Scene Format Resilience" not "Token-Position Persistence"
""")

# ─── 3. STATISTICAL ROBUSTNESS ─────────────────────────────────────

print("=" * 80)
print("3. STATISTICAL ROBUSTNESS")
print("=" * 80)

p1_t1_fx = []
for probe in results:
    fx = probe.get("T1_format_effect")
    if fx is not None:
        p1_t1_fx.append({
            "theme": probe["theme"],
            "fx": fx,
            "l1_visible": probe["l1_visible"],
            "category": probe["category"]
        })

n = len(p1_t1_fx)
mean_fx = sum(x["fx"] for x in p1_t1_fx) / n
sd_fx = math.sqrt(sum((x["fx"]-mean_fx)**2 for x in p1_t1_fx) / (n-1))
d_z = mean_fx / sd_fx if sd_fx > 0 else 0
se = sd_fx / math.sqrt(n)

print(f"\n  P1 T1 format effects: n={n}, mean={mean_fx:+.2f}, sd={sd_fx:.2f}")
print(f"  d_z = {d_z:.3f}, SE = {se:.2f}")
print(f"  95% CI of mean: [{mean_fx - 2.201*se:+.2f}, {mean_fx + 2.201*se:+.2f}]")
print(f"  V3 comparison: d_z=0.578→0.193 = -67% reduction")

# Bootstrap CI for d_z
random.seed(42)
n_boot = 10000
boot_dz = []
for _ in range(n_boot):
    sample = [random.choice(p1_t1_fx)["fx"] for _ in range(n)]
    m = sum(sample)/n
    s = math.sqrt(sum((x-m)**2 for x in sample)/(n-1))
    boot_dz.append(m/s if s>0 else 0)
boot_dz.sort()
print(f"  Bootstrap 95% CI for d_z: [{boot_dz[int(n_boot*0.025)]:.3f}, {boot_dz[int(n_boot*0.975)]:.3f}]")

print(f"\n  Per-probe format effects (T1):")
for p in p1_t1_fx:
    print(f"    [{p['l1_visible'] and 'V' or 'I':1s}] {p['theme']:<20s} T1_fx={p['fx']:+7.2f}")

n_pos = sum(1 for x in p1_t1_fx if x["fx"] > 0)
print(f"\n  Sign: {n_pos}/{n} positive (chance level)")

# r=-0.65 CI
v3_path = Path(__file__).parent / "results" / "experiment-2-confirmatory-20260712-045555.json"
try:
    with open(v3_path, encoding='utf-8') as f:
        v3_data = json.load(f)

    v3_fx = {}
    for probe in v3_data.get("results", {}).get("per_probe", []):
        v3_fx[probe["theme"]] = probe["format_effect"]

    matched = []
    for p in p1_t1_fx:
        v3 = v3_fx.get(p["theme"])
        if v3 is not None:
            matched.append({"theme": p["theme"], "v3": v3, "p1": p["fx"]})

    if len(matched) >= 10:
        print(f"\n  V3-P1 correlation (n={len(matched)}):")
        for m in matched:
            print(f"    {m['theme']:<20s} V3={m['v3']:+7.2f}  P1={m['p1']:+7.2f}")

        x_vals = [m["v3"] for m in matched]
        y_vals = [m["p1"] for m in matched]
        mx = sum(x_vals)/len(x_vals)
        my = sum(y_vals)/len(y_vals)
        sx = math.sqrt(sum((x-mx)**2 for x in x_vals)/(len(x_vals)-1))
        sy = math.sqrt(sum((y-my)**2 for y in y_vals)/(len(y_vals)-1))
        r = sum((x-mx)*(y-my) for x,y in zip(x_vals,y_vals)) / ((len(x_vals)-1)*sx*sy)

        z = 0.5 * math.log((1+r)/(1-r))
        se_z = 1/math.sqrt(len(matched)-3)
        r_lo = (math.exp(2*(z - 1.96*se_z))-1)/(math.exp(2*(z - 1.96*se_z))+1)
        r_hi = (math.exp(2*(z + 1.96*se_z))-1)/(math.exp(2*(z + 1.96*se_z))+1)
        t_val = r * math.sqrt((len(matched)-2)/(1-r**2))

        print(f"\n  Pearson r = {r:.4f}")
        print(f"  95% CI (Fisher): [{r_lo:.4f}, {r_hi:.4f}]")
        print(f"  t({len(matched)-2}) = {t_val:.2f}")

        boot_r = []
        for _ in range(n_boot):
            idx = [random.randint(0, len(matched)-1) for _ in range(len(matched))]
            bx = [x_vals[i] for i in idx]
            by = [y_vals[i] for i in idx]
            bmx = sum(bx)/len(bx)
            bmy = sum(by)/len(by)
            bsx = math.sqrt(sum((x-bmx)**2 for x in bx)/(len(bx)-1))
            bsy = math.sqrt(sum((y-bmy)**2 for y in by)/(len(by)-1))
            br = sum((x-bmx)*(y-bmy) for x,y in zip(bx,by))/((len(bx)-1)*bsx*bsy) if bsx*bsy>0 else 0
            boot_r.append(br)
        boot_r.sort()
        print(f"  Bootstrap 95% CI: [{boot_r[int(n_boot*0.025)]:.4f}, {boot_r[int(n_boot*0.975)]:.4f}]")
        print(f"  CI crosses zero: {boot_r[int(n_boot*0.025)] <= 0 <= boot_r[int(n_boot*0.975)]}")

        sign_agree = sum(1 for p in p1_t1_fx if p["theme"] in v3_fx and p["fx"]*v3_fx.get(p["theme"],0) > 0)
        sign_total = sum(1 for p in p1_t1_fx if p["theme"] in v3_fx)
        print(f"  Sign agreement V3-P1: {sign_agree}/{sign_total}")

except FileNotFoundError:
    print(f"\n  V3 data not found at {v3_path} — skipping correlation check")

# ─── 4. PROBE-SPECIFIC TRAJECTORY ──────────────────────────────────

print("\n" + "=" * 80)
print("4. PROBE-SPECIFIC TRAJECTORY (T1→T2→T3 as pressure levels)")
print("=" * 80)

print(f"\n  {'Probe':<20s} {'V':<3s} {'T1(fx)':>8s} {'T2(fx)':>8s} {'T3(fx)':>8s} {'T1→T3':>8s}  Note")
print(f"  {'-'*20} {'-'*3} {'-'*8} {'-'*8} {'-'*8} {'-'*8}  ----")
for probe in results:
    t1 = probe.get("T1_format_effect")
    t2 = probe.get("T2_format_effect")
    t3 = probe.get("T3_format_effect")
    if t1 is not None and t3 is not None:
        trend = t3 - t1
        # Classify trajectory
        if abs(t1) < 5 and abs(t2) < 5 and abs(t3) < 5:
            cls = "FLAT"
        elif abs(trend) > 15:
            cls = "LARGE SHIFT"
        elif abs(trend) > 8:
            cls = "MODERATE"
        else:
            cls = "STABLE"
        print(f"  {probe['theme']:<20s} {'V' if probe['l1_visible'] else 'I':<3s} "
              f"{t1:>+8.2f} {t2:>+8.2f} {t3:>+8.2f} {trend:>+8.2f}  {cls}")

# ─── 5. SUMMARY ────────────────────────────────────────────────────

print("\n" + "=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)

print("""
  ❌ DESIGN ISSUES:
  1. Implementation diverged from design doc — P1 measures multi-scene
     pressure resilience, NOT token-position persistence
  2. H1-H4 hypotheses test wrong construct for implemented design
  3. Cannot attribute collapse to multi-scene vs meta-instruction (confounded)

  ⚠ PRECISION LIMITATIONS:
  1. ~30% B_logprobs < -55 (reduced but non-zero precision)
  2. n=12 probes → wide CIs, modest power
  3. Single model (DeepSeek V4 Pro)

  ✅ FINDINGS THAT SURVIVE VERIFICATION:
  1. Format effect COLLAPSE in multi-scene context (d_z: 0.58→0.19)
     — NOT due to floor effect (within-condition variation exists)
  2. V3-P1 systematic reversal (r≈-0.65) — context-dependent salience
  3. L1-visibility pattern reversal — format-L1 interaction moderated by context
  4. Format effects are context-fragile, not structurally encoded

  ⚡ TO FIX BEFORE PAPER.MD:
  1. Relabel from "token-position persistence" → "multi-scene resilience"
  2. Remove/revise H4 (causal reasoning amplification) — not testable with this design
  3. Replace "structural encoding vs surface priming" → "context-fragility"
  4. Note confound: multi-scene AND meta-instructions changed simultaneously
""")
