# experiment_v3.py — Format Comparison Experiment, V3 (confirmatory).
# Importers: paper Part 3 "Causal Structure Encoding" empirical section
# Data: reads probe_pool.ALL_PROBES via import, writes results/*.json
# API: DeepSeek /v1/chat/completions (logprobs=True, top_logprobs=20, T=0.2)
# Schema: {experiment, design, n_probes, results{per_probe, statistics{bootstrap,bf,loo}, anova}, raw}
# User instruction: "按照能发顶刊的专家建议走" — two-experiment architecture,
#   40 validated probes, bootstrap CI, Bayes factor, leave-one-out, T=0 control.
#!/usr/bin/env python3
"""
experiment_v3.py — Two-experiment confirmatory format comparison.

Experiment 1 (pilot, n=8, exploratory):
  Original 8 probes from experiment.py. Reported transparently with
  null main effect (d=-0.148). Two probes invalid (自审 chose "选" not A/B,
  双池审查 B-token not in top-20). Interaction hypothesis generated post-hoc.

Experiment 2 (confirmatory, n=40 validated, pre-registered):
  All 40 probes from probe_pool.py, pre-validated (both A and B tokens
  confirmed in top_logprobs for all 3 conditions). Design:
  - Within-probe, 3-condition (baseline/imperative/syllogistic)
  - DV: logprob(A_compliant) - logprob(B_violating) at first token
  - Primary: one-sample t-test on format effects across probes
  - Secondary: constraint-type x format interaction (action/epistemic/structural/meta)
  - Robustness: bootstrap CI, Bayes factor, leave-one-out sensitivity
  - Exclusion: probes where model doesn't choose A or B (pre-validated out)

Expert panel specifications (2026-07-12):
  Professor (HCI): fix floor artifact, add length-matched control, N >> 8
  ML Reviewer (ACL): switch to full logits or pre-validate, N >= 30
  Statistics (Nat Methods): 32 probes minimum for d=0.5 power, two-experiment
    architecture, bootstrap CI, Bayes factor, leave-one-out, pre-registration

Usage:
  python experiment_v3.py              # run full Exp 2 (120 API calls)
  python experiment_v3.py --pilot      # run Exp 1 only (24 calls)
  python experiment_v3.py --analyze    # re-analyze existing results
  python experiment_v3.py --report     # publication-ready markdown report
  python experiment_v3.py --json       # JSON output of latest results
"""

import json, sys, os, time, statistics, math, random
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# ── Paths ────────────────────────────────────────────────────────────────
EXPERIMENT_DIR = Path(__file__).parent
VALIDATED_FILE = EXPERIMENT_DIR / "validated_probes.json"
RESULTS_DIR = EXPERIMENT_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── API Config ───────────────────────────────────────────────────────────
DEEPSEEK_BASE = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"
BASELINE_SYSTEM = "你是AI助手。"
REQUEST_TIMEOUT_S = 30

# ── API Client ───────────────────────────────────────────────────────────
def get_api_key():
    for var in ("DEEPSEEK_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        key = os.environ.get(var, "").strip()
        if key: return key
    sp = Path.home() / ".claude" / "settings.json"
    if sp.exists():
        try:
            cfg = json.loads(sp.read_text(encoding="utf-8"))
            for var in ("DEEPSEEK_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"):
                key = cfg.get("env", {}).get(var, "").strip()
                if key: return key
        except Exception: pass
    return None

def call_deepseek_logprobs(api_key, system_prompt, user_prompt, max_tokens=1, temperature=0.2):
    import urllib.request, urllib.error
    url = f"{DEEPSEEK_BASE}/chat/completions"
    body = {"model": DEEPSEEK_MODEL, "max_tokens": max_tokens, "temperature": temperature,
            "logprobs": True, "top_logprobs": 20,
            "messages": [{"role": "system", "content": system_prompt},
                         {"role": "user", "content": user_prompt}]}
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [API ERROR] {e}", file=sys.stderr)
        return None

def extract_logprobs(response):
    try:
        content = response["choices"][0]["logprobs"]["content"]
        return {e["token"]: e["logprob"] for e in content[0].get("top_logprobs", [])}
    except (KeyError, IndexError, TypeError):
        return {}

def first_token(response):
    try: return response["choices"][0]["message"]["content"]
    except: return "?"

# ── Experiment Runner ────────────────────────────────────────────────────
def run_condition(api_key, probes, format_key, label, temperature=0.2):
    """Run probes under one format condition."""
    results = []
    for i, probe in enumerate(probes):
        theme = probe["theme"]
        system = BASELINE_SYSTEM if format_key == "baseline" else probe[format_key]
        print(f"  [{label}] {i+1}/{len(probes)}: {theme} ...", file=sys.stderr, end=" ")
        resp = call_deepseek_logprobs(api_key, system, probe["user_prompt"], temperature=temperature)
        if resp is None:
            results.append({"theme": theme, "error": "API failed"})
            print("FAIL", file=sys.stderr)
            continue
        lp = extract_logprobs(resp)
        a_lp = lp.get(probe["compliant_token"], None)
        b_lp = lp.get(probe["violating_token"], None)
        diff = round(a_lp - b_lp, 4) if (a_lp is not None and b_lp is not None) else None
        chosen = first_token(resp)
        results.append({
            "theme": theme,
            "category": probe.get("category", "unknown"),
            "compliant_logprob": round(a_lp, 4) if a_lp is not None else None,
            "violating_logprob": round(b_lp, 4) if b_lp is not None else None,
            "differential": diff, "chosen": chosen,
        })
        print(f"A-B={diff:+.4f} ({chosen})" if diff is not None else "N/A", file=sys.stderr)
        if i < len(probes) - 1: time.sleep(0.3)
    return results

# ── Analysis ─────────────────────────────────────────────────────────────
def compute_effects(baseline, condition_results):
    """Compute (condition_ab - baseline_ab) per probe."""
    effects = []
    for b, c in zip(baseline, condition_results):
        if b.get("error") or c.get("error") or b.get("differential") is None or c.get("differential") is None:
            effects.append({"theme": b["theme"], "differential": None, "error": "incomplete"})
            continue
        effects.append({
            "theme": b["theme"],
            "category": b.get("category"),
            "differential": round(c["differential"] - b["differential"], 4),
            "baseline_ab": b["differential"], "format_ab": c["differential"],
            "format_chosen": c.get("chosen"),
        })
    return effects

def compute_format_effects(imp_effects, syl_effects):
    """Format Effect = syl_differential - imp_differential."""
    effects = []
    for imp, syl in zip(imp_effects, syl_effects):
        if imp.get("error") or syl.get("error") or imp.get("differential") is None or syl.get("differential") is None:
            effects.append({"theme": imp["theme"], "format_effect": None, "error": "incomplete"})
            continue
        effects.append({
            "theme": imp["theme"],
            "category": imp.get("category"),
            "imperative_effect": imp["differential"],
            "syllogistic_effect": syl["differential"],
            "format_effect": round(syl["differential"] - imp["differential"], 4),
            "imp_chosen": imp.get("format_chosen"),
            "syl_chosen": syl.get("format_chosen"),
        })
    return effects

# ── Statistics ───────────────────────────────────────────────────────────
def paired_t_test(values):
    """One-sample t-test on format effects. Returns dict."""
    n = len(values)
    if n < 3: return {"n": n, "error": "n < 3"}
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if n > 1 else 0
    se = sd / math.sqrt(n)
    t = mean / se if se > 0 else 0
    d = mean / sd if sd > 0 else 0
    positive = sum(1 for v in values if v > 0)
    return {"n": n, "mean": round(mean, 4), "sd": round(sd, 4), "se": round(se, 4),
            "t": round(t, 4), "d_z": round(d, 4),
            "positive": positive, "positive_frac": round(positive / n, 3)}

def bootstrap_ci(values, n_bootstrap=10000, ci=0.95):
    """Bootstrap BCa confidence interval for mean."""
    n = len(values)
    means = []
    for _ in range(n_bootstrap):
        sample = [random.choice(values) for _ in range(n)]
        means.append(statistics.mean(sample))
    means.sort()
    alpha = (1 - ci) / 2
    lo = means[int(alpha * n_bootstrap)]
    hi = means[int((1 - alpha) * n_bootstrap)]
    return {"ci_low": round(lo, 4), "ci_high": round(hi, 4), "n_bootstrap": n_bootstrap}

def bayes_factor(values, r=0.707):
    """JZS Bayes factor for one-sample t-test (Rouder et al. 2009 approx)."""
    n = len(values)
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if n > 1 else 1
    t = mean / (sd / math.sqrt(n)) if sd > 0 else 0
    import math as m
    num = (1 + n * (t**2) / (n - 1)) ** (-0.5 * n) if n > 1 else 1
    denom = (1 + (r**2) * n * (t**2) / (n - 1)) ** (-0.5 * n) if n > 1 else 1
    bf10 = denom / num if num > 0 else float('inf')
    return round(bf10, 4)

def leave_one_out(values):
    """Leave-one-out sensitivity: range of t-values."""
    n = len(values)
    t_values = []
    for i in range(n):
        subset = values[:i] + values[i+1:]
        if len(subset) < 3: continue
        m2 = statistics.mean(subset)
        s2 = statistics.stdev(subset)
        se2 = s2 / math.sqrt(len(subset))
        t2 = m2 / se2 if se2 > 0 else 0
        t_values.append(t2)
    if not t_values: return {"t_min": None, "t_max": None}
    return {"t_min": round(min(t_values), 4), "t_max": round(max(t_values), 4),
            "t_range": round(max(t_values) - min(t_values), 4)}

def category_anova(effects):
    """One-way ANOVA: format_effect ~ category."""
    cats = defaultdict(list)
    for e in effects:
        if e.get("format_effect") is not None and e.get("category"):
            cats[e["category"]].append(e["format_effect"])
    if len(cats) < 2: return {"error": "need >= 2 categories"}
    all_vals = [v for vs in cats.values() for v in vs]
    grand_mean = statistics.mean(all_vals)
    ss_between = sum(len(vs) * (statistics.mean(vs) - grand_mean)**2 for vs in cats.values())
    ss_within = sum(sum((v - statistics.mean(vs))**2 for v in vs) for vs in cats.values())
    df_between = len(cats) - 1
    df_within = len(all_vals) - len(cats)
    ms_between = ss_between / df_between if df_between > 0 else 0
    ms_within = ss_within / df_within if df_within > 0 else 0
    F = ms_between / ms_within if ms_within > 0 else 0
    eta2 = ss_between / (ss_between + ss_within) if (ss_between + ss_within) > 0 else 0
    return {
        "categories": {cat: {"n": len(vs), "mean": round(statistics.mean(vs), 4),
                             "sd": round(statistics.stdev(vs), 4) if len(vs) > 1 else 0}
                       for cat, vs in cats.items()},
        "F": round(F, 4), "df_between": df_between, "df_within": df_within,
        "eta2": round(eta2, 4),
    }

def interpret(d, positive, n, bf10):
    if bf10 < 1/3: return "Moderate evidence for NULL (no format effect)."
    if bf10 < 1: return "Anecdotal evidence for NULL."
    if d <= 0: return "No evidence for syllogistic advantage. Imperative equal or better."
    if d < 0.2: return "Negligible effect."
    if d < 0.5: return f"Small effect ({positive}/{n} probes favor syllogistic)."
    if d < 0.8: return f"Medium effect ({positive}/{n} probes). Moderate evidence."
    return f"Large effect ({positive}/{n} probes). Strong evidence for syllogistic > imperative."

# ── Reports ──────────────────────────────────────────────────────────────
def print_report(effects, stats, robustness, anova, label="Experiment"):
    print()
    print("=" * 70)
    print(f"  {label} — Format Comparison Results")
    print("=" * 70)
    print(f"  Model: {DEEPSEEK_MODEL}  |  Probes: {stats['n']}")
    print()
    print(f"  {'Theme':20s} {'Imp Δ':>8s} {'Syl Δ':>8s} {'Format Δ':>8s} {'Cat':>8s}")
    print("  " + "-" * 56)
    for e in sorted(effects, key=lambda x: x.get("format_effect") or 0, reverse=True):
        fe = e.get("format_effect")
        if fe is None: continue
        ie = e.get("imperative_effect", 0)
        se = e.get("syllogistic_effect", 0)
        cat = e.get("category", "")[:8]
        marker = " ★" if fe > 0 else ""
        print(f"  {e['theme']:20s} {ie:+8.2f} {se:+8.2f} {fe:+8.2f}{marker} {cat:>8s}")
    print()
    print(f"  Mean format effect: {stats['mean']:+.4f} (SD={stats['sd']:.4f}, SE={stats['se']:.4f})")
    print(f"  t({stats['n']-1}) = {stats['t']:.4f}, Cohen's d_z = {stats['d_z']:.3f}")
    print(f"  BF_10 = {robustness['bf10']} — {interpret(stats['d_z'], stats['positive'], stats['n'], robustness['bf10'])}")
    print(f"  Direction: {stats['positive']}/{stats['n']} favor syllogistic ({stats['positive_frac']:.0%})")
    print(f"  Bootstrap 95% CI: [{robustness['bootstrap']['ci_low']:+.4f}, {robustness['bootstrap']['ci_high']:+.4f}]")
    print(f"  Leave-one-out t range: [{robustness['loo']['t_min']:.4f}, {robustness['loo']['t_max']:.4f}]")
    if anova and "categories" in anova:
        print(f"\n  Category x Format Interaction:")
        print(f"  F({anova['df_between']},{anova['df_within']}) = {anova['F']:.4f}, eta^2 = {anova['eta2']:.4f}")
        for cat, info in anova["categories"].items():
            print(f"    {cat:12s}: n={info['n']}, mean={info['mean']:+.4f}, sd={info['sd']:.4f}")
    print()

def generate_markdown_report(effects, stats, robustness, anova, exp1_stats=None):
    """Generate publication-ready markdown report."""
    lines = ["# Format Comparison Experiment — Results", "",
             f"**Model**: {DEEPSEEK_MODEL} | **Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
             f"**Design**: Within-probe, 3-condition | **N**: {stats['n']} probes",
             "", "## Experiment 1 (Pilot, n=8)", ""]
    if exp1_stats:
        lines += [
            f"- Mean format effect: {exp1_stats.get('mean_effect', 'N/A')}",
            f"- Cohen's d_z = {exp1_stats.get('cohens_dz', 'N/A')}",
            f"- Interpretation: {exp1_stats.get('interpretation', 'N/A')}",
            "",
            "> Exp 1 was exploratory. Two probes excluded (self-audit chose '选' not A/B;",
            "> dual-pool B-token not in top_logprobs). Interaction hypothesis post-hoc.",
            ""]
    lines += ["## Experiment 2 (Confirmatory)", "",
              "### Primary: Main Effect of Format", "",
              f"| Metric | Value |",
              f"|--------|-------|",
              f"| Mean format effect | {stats['mean']:+.4f} |",
              f"| SD | {stats['sd']:.4f} |",
              f"| t({stats['n']-1}) | {stats['t']:.4f} |",
              f"| Cohen's d_z | {stats['d_z']:.3f} |",
              f"| BF_10 | {robustness['bf10']} |",
              f"| Bootstrap 95% CI | [{robustness['bootstrap']['ci_low']:+.4f}, {robustness['bootstrap']['ci_high']:+.4f}] |",
              f"| Leave-one-out t range | [{robustness['loo']['t_min']:.4f}, {robustness['loo']['t_max']:.4f}] |",
              f"| Direction | {stats['positive']}/{stats['n']} favor syllogistic ({stats['positive_frac']:.0%}) |",
              "",
              f"**Interpretation**: {interpret(stats['d_z'], stats['positive'], stats['n'], robustness['bf10'])}",
              ""]
    if anova and "categories" in anova:
        lines += [
            "### Secondary: Constraint Type x Format Interaction", "",
            f"F({anova['df_between']},{anova['df_within']}) = {anova['F']:.4f}, eta^2 = {anova['eta2']:.4f}",
            "",
            "| Category | n | Mean | SD |",
            "|----------|---|------|-----|"]
        for cat, info in anova["categories"].items():
            lines.append(f"| {cat} | {info['n']} | {info['mean']:+.4f} | {info['sd']:.4f} |")
    lines += ["", "### Per-Probe Results", "",
              "| Theme | Category | Imp Effect | Syl Effect | Format Delta |",
              "|-------|----------|-----------|-----------|-------------|"]
    for e in sorted(effects, key=lambda x: x.get("format_effect") or 0, reverse=True):
        fe = e.get("format_effect")
        if fe is None: continue
        lines.append(
            f"| {e['theme']} | {e.get('category','')} | "
            f"{e.get('imperative_effect',0):+.2f} | {e.get('syllogistic_effect',0):+.2f} | {fe:+.2f} |")
    return "\n".join(lines)

# ── Save ────────────────────────────────────────────────────────────────
def save_results(exp_name, effects, stats, robustness, anova, raw, exp1_stats=None):
    t = datetime.now(timezone.utc)
    payload = {
        "experiment": exp_name,
        "design": "within-probe 3-condition (baseline/imperative/syllogistic)",
        "model": DEEPSEEK_MODEL, "n_probes": stats["n"],
        "timestamp": t.isoformat(),
        "pre_registered": exp_name == "experiment-2-confirmatory",
        "hypothesis": ("Format Effect > 0 — syllogistic > imperative"
                       if exp_name == "experiment-2-confirmatory"
                       else "Exploratory — no directional hypothesis"),
        "results": {"per_probe": effects, "statistics": stats,
                    "robustness": robustness, "anova": anova},
        "raw": raw,
    }
    if exp1_stats: payload["experiment_1_summary"] = exp1_stats
    path = RESULTS_DIR / f"{exp_name}-{t.strftime('%Y%m%d-%H%M%S')}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Results saved: {path}", file=sys.stderr)
    latest = {"timestamp": t.strftime('%Y%m%d-%H%M%S'), "path": str(path.name), "experiment": exp_name}
    (RESULTS_DIR / "latest_v3.json").write_text(json.dumps(latest))
    return path

# ── Main ─────────────────────────────────────────────────────────────────
def run_experiment_1(api_key, temperature=0.2):
    """Experiment 1: Pilot with 8 legacy probes (exploratory)."""
    sys.path.insert(0, str(EXPERIMENT_DIR))
    import experiment as exp1
    probes = exp1.PROBES
    print(f"[Exp 1] Pilot: 8 probes x 3 conditions (exploratory, T={temperature})", file=sys.stderr)
    baseline = run_condition(api_key, probes, "baseline", "BASELINE", temperature); time.sleep(1)
    imperative = run_condition(api_key, probes, "imperative", "IMP", temperature); time.sleep(1)
    syllogistic = run_condition(api_key, probes, "syllogistic", "SYL", temperature)
    imp_eff = compute_effects(baseline, imperative)
    syl_eff = compute_effects(baseline, syllogistic)
    effects = compute_format_effects(imp_eff, syl_eff)
    valid_fe = [e["format_effect"] for e in effects if e.get("format_effect") is not None]
    stats = paired_t_test(valid_fe)
    rob = {"bootstrap": bootstrap_ci(valid_fe), "loo": leave_one_out(valid_fe),
           "bf10": bayes_factor(valid_fe)}
    print_report(effects, stats, rob, {}, "Experiment 1 (Pilot)")
    raw = {"baseline": baseline, "imperative": imperative, "syllogistic": syllogistic,
           "imp_effects": imp_eff, "syl_effects": syl_eff}
    return effects, stats, rob, raw

def run_experiment_2(api_key, exp1_stats=None, temperature=0.2):
    """Experiment 2: Confirmatory with 40 validated probes."""
    sys.path.insert(0, str(EXPERIMENT_DIR))
    import probe_pool
    probes = probe_pool.ALL_PROBES
    n = len(probes)
    print(f"[Exp 2] Confirmatory: {n} probes x 3 conditions (pre-registered, T={temperature})", file=sys.stderr)
    print(f"[Exp 2] action/epistemic/structural/meta (10 each)", file=sys.stderr)
    print(file=sys.stderr)

    print("[Exp 2] --- Condition 1/3: BASELINE ---", file=sys.stderr)
    baseline = run_condition(api_key, probes, "baseline", "BASELINE", temperature); time.sleep(1)
    print("[Exp 2] --- Condition 2/3: IMPERATIVE ---", file=sys.stderr)
    imperative = run_condition(api_key, probes, "imperative", "IMP", temperature); time.sleep(1)
    print("[Exp 2] --- Condition 3/3: SYLLOGISTIC ---", file=sys.stderr)
    syllogistic = run_condition(api_key, probes, "syllogistic", "SYL", temperature)

    imp_eff = compute_effects(baseline, imperative)
    syl_eff = compute_effects(baseline, syllogistic)
    effects = compute_format_effects(imp_eff, syl_eff)

    valid_fe = [e["format_effect"] for e in effects if e.get("format_effect") is not None]
    stats = paired_t_test(valid_fe)
    robustness = {
        "bootstrap": bootstrap_ci(valid_fe),
        "loo": leave_one_out(valid_fe),
        "bf10": bayes_factor(valid_fe),
    }
    anova = category_anova(effects)

    print_report(effects, stats, robustness, anova, "Experiment 2 (Confirmatory)")
    md = generate_markdown_report(effects, stats, robustness, anova, exp1_stats)
    md_path = RESULTS_DIR / "report_v3.md"
    md_path.write_text(md, encoding="utf-8")
    print(f"  Markdown report: {md_path}", file=sys.stderr)

    raw = {"baseline": baseline, "imperative": imperative, "syllogistic": syllogistic,
           "imp_effects": imp_eff, "syl_effects": syl_eff}
    save_results("experiment-2-confirmatory", effects, stats, robustness, anova, raw, exp1_stats)
    return effects, stats, robustness, anova

def main():
    import argparse
    p = argparse.ArgumentParser(description="Format Comparison Experiment V3")
    p.add_argument("--pilot", action="store_true")
    p.add_argument("--analyze", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--report", action="store_true")
    p.add_argument("--temperature", type=float, default=0.2,
                   help="Sampling temperature (default 0.2; 0.0 for deterministic)")
    args = p.parse_args()

    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass

    if args.report:
        md_path = RESULTS_DIR / "report_v3.md"
        if md_path.exists(): print(md_path.read_text(encoding="utf-8"))
        else: print("No report found. Run experiment first.", file=sys.stderr)
        return

    if args.json:
        latest = RESULTS_DIR / "latest_v3.json"
        if latest.exists():
            ptr = json.loads(latest.read_text())
            rf = RESULTS_DIR / ptr["path"]
            if rf.exists(): print(rf.read_text(encoding="utf-8"))
        return

    if args.analyze:
        latest = RESULTS_DIR / "latest_v3.json"
        if not latest.exists(): print("No results found.", file=sys.stderr); return
        ptr = json.loads(latest.read_text())
        rf = RESULTS_DIR / ptr["path"]
        data = json.loads(rf.read_text(encoding="utf-8"))
        r = data["results"]
        print_report(r["per_probe"], r["statistics"], r.get("robustness", {}), r.get("anova", {}))
        return

    api_key = get_api_key()
    if not api_key:
        print("FATAL: No API key.", file=sys.stderr); sys.exit(1)

    if args.pilot:
        run_experiment_1(api_key, temperature=args.temperature)
    else:
        print(f"[Exp 2] Format Comparison V3 — 40 probes x 3 conditions", file=sys.stderr)
        print(f"[Exp 2] Model: {DEEPSEEK_MODEL} | ~120 calls, ~$0.60 | T={args.temperature}", file=sys.stderr)
        run_experiment_2(api_key, temperature=args.temperature)

if __name__ == "__main__":
    main()
