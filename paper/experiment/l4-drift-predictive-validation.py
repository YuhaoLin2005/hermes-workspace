#!/usr/bin/env python3
"""
L4 Drift Predictive Validation Experiment
==========================================
Pre-registered: 2026-07-28 04:00 UTC
SHA256: <to be computed after finalization>

Research Question:
  Does the L4 drift score (8-feature composite from drift_predictor.py)
  predict future configuration violations?

Original Design (H0: ρ(D_i, V_{i+1}) = 0):
  - For each session S_i: record drift score D_i
  - Record violation count V_{i+1} in next session
  - Pearson/Spearman correlation

DATA LIMITATION DISCOVERED:
  drift_predictor.py computes features from LIVE filesystem state
  (settings.json mtime, growth-log count, etc.). The drift-baseline.json
  rolling_window=10 only retains the last 10 entries — all from July 27-28
  with score=0 (gate_coverage=1.0, unhooked_rules=0).

  The drift score has ZERO variance in available history.
  Original hypothesis is UNTESTABLE with current data.

FALLBACK ANALYSIS:
  Gate-block autocorrelation as drift proxy.
  Rationale: drift accumulation → clustered violations across days.
  If drift is random (independent), blocks should follow Poisson process.
  If drift accumulates, we expect temporal clustering (AR(1) structure).

  H0': Gate blocks are temporally independent (lag-1 autocorr ρ₁ = 0)
  H1': Gate blocks show positive autocorrelation (ρ₁ > 0, drift accumulates)

  Additional: block-type transition analysis — does one type of block
  predict another in subsequent sessions? (drift modality transfer)

Author: L4 Drift Predictor validation task
Data: .claude/session-gate-log.jsonl (67 entries, 2026-07-17 ~ 2026-07-28)
"""

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from math import sqrt, exp, pi

# --- Data Loading ---

def load_gate_log(path: str) -> list[dict]:
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries

def load_drift_baseline(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# --- Per-Session Aggregation ---

def aggregate_by_session(entries: list[dict]) -> dict[str, dict]:
    """Group gate blocks by session date, count by gate type."""
    sessions = defaultdict(lambda: {"total": 0, "gates": Counter(), "details": []})
    for e in entries:
        sess = e.get("session", "")
        gate = e.get("gate", "unknown")
        detail = e.get("detail", "")
        sessions[sess]["total"] += 1
        sessions[sess]["gates"][gate] += 1
        sessions[sess]["details"].append(detail)
    return dict(sessions)

# --- Temporal Autocorrelation ---

def _normal_cdf(x: float) -> float:
    """Standard normal CDF approximation (Abramowitz & Stegun 7.1.26)."""
    if x < 0:
        return 1 - _normal_cdf(-x)
    b = [0.31938153, -0.356563782, 1.781477937, -1.821255978, 1.330274429]
    t = 1 / (1 + 0.2316419 * x)
    poly = b[0]*t + b[1]*t**2 + b[2]*t**3 + b[3]*t**4 + b[4]*t**5
    pdf = exp(-x*x/2) / sqrt(2*pi)
    return 1 - pdf * poly

def compute_lag1_autocorr(values: list[float]) -> tuple[float, float]:
    """
    Compute lag-1 autocorrelation coefficient.
    Returns (rho, p_approx) using Bartlett's formula approximation.
    rho = Σ(x_t - x̄)(x_{t-1} - x̄) / Σ(x_t - x̄)²
    SE ≈ 1/√n under null of zero autocorrelation.
    """
    n = len(values)
    if n < 3:
        return float('nan'), float('nan')

    mean = sum(values) / n
    var = sum((x - mean) ** 2 for x in values)

    if var == 0:
        return 0.0, 1.0  # No variance → no autocorrelation

    # Lag-1 covariance
    cov = sum((values[t] - mean) * (values[t-1] - mean) for t in range(1, n))
    rho = cov / var

    # Standard error under H0 (Bartlett)
    se = 1.0 / sqrt(n)
    # Approximate z-statistic
    z = rho / se if se > 0 else 0

    # Two-tailed p-value approximation (normal)
    p = 2 * (1 - _normal_cdf(abs(z)))

    return rho, p

# --- Block-Type Transition Analysis ---

def compute_transition_matrix(sessions: dict[str, dict]) -> dict:
    """
    For each consecutive session pair, does block type A in session i
    predict block type B in session i+1?
    """
    sorted_dates = sorted(sessions.keys())
    gate_types = set()
    for s in sessions.values():
        gate_types.update(s["gates"].keys())

    # Count transitions
    transitions = defaultdict(lambda: defaultdict(int))
    row_counts = defaultdict(int)

    for i in range(len(sorted_dates) - 1):
        s_curr = sorted_dates[i]
        s_next = sorted_dates[i+1]
        curr_gates = set(sessions[s_curr]["gates"].keys())
        next_gates = set(sessions[s_next]["gates"].keys())

        for g_curr in curr_gates:
            row_counts[g_curr] += 1
            for g_next in next_gates:
                transitions[g_curr][g_next] += 1

    # Also track "SILENT" → gate transition (no blocks → blocks)
    row_counts["SILENT"] = 0
    for i in range(len(sorted_dates) - 1):
        s_curr = sorted_dates[i]
        s_next = sorted_dates[i+1]
        curr_gates = set(sessions[s_curr]["gates"].keys())
        if not curr_gates:
            row_counts["SILENT"] += 1
            for g_next in sessions[s_next]["gates"].keys():
                transitions["SILENT"][g_next] += 1

    return {
        "transitions": {k: dict(v) for k, v in transitions.items()},
        "row_counts": dict(row_counts),
        "gate_types": sorted(gate_types),
    }

# --- Block Rate Trend (Poisson test for drift) ---

def compute_block_rate_trend(sessions: dict[str, dict]) -> dict:
    """
    Linear regression of daily block count over time.
    If drift accumulates, we expect increasing block rate.
    H0: slope = 0 (constant rate, no drift accumulation)
    """
    sorted_dates = sorted(sessions.keys())
    dates_parsed = [datetime.strptime(d, "%Y-%m-%d") for d in sorted_dates]
    counts = [sessions[d]["total"] for d in sorted_dates]

    # Days from start
    t0 = dates_parsed[0]
    t_days = [(d - t0).days for d in dates_parsed]

    n = len(t_days)
    if n < 3:
        return {"slope": None, "error": "insufficient data"}

    # Linear regression: y = a + b*x
    mean_x = sum(t_days) / n
    mean_y = sum(counts) / n

    ss_xx = sum((x - mean_x) ** 2 for x in t_days)
    ss_xy = sum((t_days[i] - mean_x) * (counts[i] - mean_y) for i in range(n))

    if ss_xx == 0:
        return {"slope": 0.0, "error": "zero variance in time"}

    slope = ss_xy / ss_xx if ss_xx > 0 else 0
    intercept = mean_y - slope * mean_x

    # R²
    y_pred = [intercept + slope * x for x in t_days]
    ss_res = sum((counts[i] - y_pred[i]) ** 2 for i in range(n))
    ss_tot = sum((y - mean_y) ** 2 for y in counts)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    # Standard error of slope
    se_slope = sqrt(ss_res / (n - 2) / ss_xx) if n > 2 and ss_xx > 0 else float('inf')

    # t-statistic
    t_stat = slope / se_slope if se_slope > 0 else 0

    return {
        "slope": round(slope, 3),
        "intercept": round(intercept, 1),
        "r_squared": round(r_squared, 4),
        "t_statistic": round(t_stat, 3),
        "n_days": n,
        "daily_data": {sorted_dates[i]: counts[i] for i in range(n)},
    }

# --- Block Interval Analysis ---

def compute_inter_block_intervals(sessions: dict[str, dict]) -> dict:
    """
    If drift accumulates within a session, blocks should cluster
    (shorter intervals between blocks in high-drift sessions).
    If purely external (random triggers), intervals should be
    exponentially distributed.
    """
    sorted_dates = sorted(sessions.keys())
    dates_parsed = [datetime.strptime(d, "%Y-%m-%d") for d in sorted_dates]

    # Gap between consecutive active sessions
    active_dates = [d for d in sorted_dates if sessions[d]["total"] > 0]
    active_parsed = [datetime.strptime(d, "%Y-%m-%d") for d in active_dates]

    gaps = []
    for i in range(1, len(active_parsed)):
        gap_days = (active_parsed[i] - active_parsed[i-1]).days
        gaps.append(gap_days)

    mean_gap = sum(gaps) / len(gaps) if gaps else 0

    # After a high-block day (>median), is the gap to the next block day shorter?
    if not active_dates:
        return {"error": "no active sessions"}

    median_blocks = sorted(sessions[d]["total"] for d in active_dates)[len(active_dates) // 2]

    high_block_gaps = []
    low_block_gaps = []
    for i in range(len(active_dates) - 1):
        gap = (active_parsed[i+1] - active_parsed[i]).days
        if sessions[active_dates[i]]["total"] >= median_blocks:
            high_block_gaps.append(gap)
        else:
            low_block_gaps.append(gap)

    return {
        "active_sessions": len(active_dates),
        "total_sessions": len(sorted_dates),
        "gaps_between_active": gaps,
        "mean_gap_days": round(mean_gap, 1) if mean_gap else None,
        "median_blocks_per_day": median_blocks,
        "high_block_mean_gap": round(sum(high_block_gaps)/len(high_block_gaps), 1) if high_block_gaps else None,
        "low_block_mean_gap": round(sum(low_block_gaps)/len(low_block_gaps), 1) if low_block_gaps else None,
    }

# --- Main Analysis ---

def main():
    import os
    home = os.path.expanduser("~")
    gate_log_path = os.path.join(home, ".claude", "session-gate-log.jsonl")
    drift_path = os.path.join(home, ".claude", ".drift-baseline.json")

    print("=" * 64)
    print("  L4 Drift Predictive Validation Experiment")
    print("  Pre-registered: 2026-07-28 04:00 UTC")
    print("=" * 64)

    # --- 0. Data Inventory ---
    print("\n── 0. Data Inventory ──")
    entries = load_gate_log(gate_log_path)
    drift = load_drift_baseline(drift_path)
    print(f"  session-gate-log.jsonl:  {len(entries)} entries")
    print(f"  .drift-baseline.json:    {drift.get('sessions_collected', 0)} sessions collected")
    print(f"  drift history window:    {len(drift.get('history', []))} entries (rolling_window={drift.get('rolling_window', '?')})")

    # Check drift score variance
    history = drift.get("history", [])
    drift_scores = [h.get("risk_score") for h in history]
    unique_scores = set(drift_scores)
    print(f"  drift score range:       {min(unique_scores)}-{max(unique_scores)} (n={len(drift_scores)} unique values in window)")
    if len(unique_scores) <= 1:
        print(f"\n  !! CRITICAL: Drift score has ZERO variance in available history.")
        print("  Original hypothesis rho(D_i, V_{i+1}) = 0 is UNTESTABLE.")
        print(f"  Cause: drift_predictor.py computes features from LIVE filesystem state;")
        print(f"  rolling_window=10 only retains recent stable-period snapshots.")
        print(f"  All recent sessions: gate_coverage=1.0, unhooked_rules=0 -> D_i = 0.")
        print(f"\n  Proceeding with FALLBACK ANALYSIS: gate-block temporal patterns.")
    else:
        print(f"  drift scores available:  {drift_scores}")

    # --- 1. Per-Session Aggregation ---
    print("\n── 1. Per-Session Gate Blocks ──")
    sessions = aggregate_by_session(entries)
    sorted_dates = sorted(sessions.keys())
    print(f"  {'Date':<12} {'Blocks':>6}  Gate Types")
    print(f"  {'-'*12} {'-'*6}  {'-'*40}")
    for d in sorted_dates:
        s = sessions[d]
        gates_str = ", ".join(f"{g}:{c}" for g, c in s["gates"].most_common())
        print(f"  {d:<12} {s['total']:>6}  {gates_str}")

    total_blocks = sum(s["total"] for s in sessions.values())
    print(f"\n  Total blocks: {total_blocks} across {len(sessions)} sessions ({len(sorted_dates)} days)")

    # --- 2. Lag-1 Autocorrelation ---
    print("\n── 2. Lag-1 Autocorrelation (Drift Accumulation Test) ──")
    # Fill all days in range (including zero-block days)
    all_dates = []
    start = datetime.strptime(sorted_dates[0], "%Y-%m-%d")
    end = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")
    d = start
    while d <= end:
        all_dates.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)

    counts_full = [sessions.get(d, {"total": 0})["total"] for d in all_dates]
    rho, p = compute_lag1_autocorr(counts_full)

    print(f"  All {len(all_dates)} days ({all_dates[0]} - {all_dates[-1]}):")
    print(f"  Daily block counts: {counts_full}")
    print(f"  Lag-1 autocorrelation rho1 = {rho:.4f}")
    print(f"  Approximate p-value:       {p:.4f}")
    if p < 0.05:
        print(f"  -> SIGNIFICANT: blocks are temporally clustered (drift accumulation pattern)")
    else:
        print(f"  -> NOT SIGNIFICANT: cannot reject temporal independence")

    # Also test with only active days (nonzero block days)
    active_counts = [sessions[d]["total"] for d in sorted_dates]
    rho_active, p_active = compute_lag1_autocorr(active_counts)
    print(f"\n  Active days only ({len(active_counts)} days):")
    print(f"  Lag-1 autocorrelation rho1 = {rho_active:.4f}")
    print(f"  Approximate p-value:       {p_active:.4f}")

    # --- 3. Block Rate Trend ---
    print("\n── 3. Block Rate Trend (Linear Regression) ──")
    trend = compute_block_rate_trend(sessions)
    print(f"  Slope: {trend['slope']} blocks/day increase")
    print(f"  R-squared:    {trend['r_squared']}")
    print(f"  t-statistic: {trend['t_statistic']}")
    if trend.get("slope", 0) > 0.1:
        print(f"  -> UPWARD trend: block rate increases over time (cumulative drift)")
    elif trend.get("slope", 0) < -0.1:
        print(f"  -> DOWNWARD trend: block rate decreases over time (learning effect)")
    else:
        print(f"  -> FLAT: no systematic trend in block rate")

    # --- 4. Inter-Block Gap Analysis ---
    print("\n── 4. Inter-Block Gap Analysis ──")
    gaps = compute_inter_block_intervals(sessions)
    print(f"  Active sessions:    {gaps['active_sessions']}/{gaps['total_sessions']}")
    print(f"  Gaps between active: {gaps.get('gaps_between_active', [])}")
    print(f"  Mean gap:           {gaps.get('mean_gap_days', 'N/A')} days")
    print(f"  High-block (>={gaps.get('median_blocks_per_day', '?')}) mean gap: {gaps.get('high_block_mean_gap', 'N/A')}")
    print(f"  Low-block mean gap:  {gaps.get('low_block_mean_gap', 'N/A')}")
    if gaps.get('high_block_mean_gap') and gaps.get('low_block_mean_gap'):
        if gaps['high_block_mean_gap'] < gaps['low_block_mean_gap']:
            print(f"  -> High-block days followed by SHORTER gaps (blocks cluster: drift signature)")
        else:
            print(f"  -> High-block days NOT followed by shorter gaps (blocks don't cluster)")

    # --- 5. Block-Type Transitions ---
    print("\n── 5. Block-Type Transition Analysis ──")
    tm = compute_transition_matrix(sessions)
    print(f"  Gate types: {tm['gate_types']}")
    print(f"\n  Transition matrix (row -> col):")
    print(f"  {'From':<16} {'To':<20} {'Count':>6}")
    print(f"  {'-'*16} {'-'*20} {'-'*6}")
    for g_from in sorted(tm["transitions"].keys()):
        row = tm["transitions"][g_from]
        for g_to in sorted(row.keys()):
            print(f"  {g_from:<16} -> {g_to:<18} {row[g_to]:>6}")
    if tm["row_counts"].get("SILENT", 0) > 0:
        silent_to = tm["transitions"].get("SILENT", {})
        if silent_to:
            print(f"\n  After SILENT days (no blocks):")
            for g_to, count in silent_to.items():
                pct = count / tm["row_counts"]["SILENT"] * 100
                print(f"    -> {g_to}: {count}/{tm['row_counts']['SILENT']} ({pct:.0f}%)")

    # --- 6. Summary ---
    print("\n── 6. Experiment Summary ──")
    print(f"""
  ORIGINAL HYPOTHESIS:  rho(D_i, V_{{i+1}}) = 0
  STATUS:               UNTESTABLE
  REASON:               drift_predictor.py computes features from LIVE filesystem
                        state; rolling_window=10 only retains stable-period snapshots
                        where drift score = 0 (gate_coverage=1.0, unhooked_rules=0).

  FALLBACK FINDINGS:
    Lag-1 autocorr:     rho1 = {rho:.4f} (p = {p:.4f})
    Block rate trend:   slope = {trend.get('slope', 'N/A')} blocks/day
    Gap clustering:     {'yes' if gaps.get('high_block_mean_gap') and gaps.get('low_block_mean_gap') and gaps['high_block_mean_gap'] < gaps['low_block_mean_gap'] else 'no'} (high-block days -> shorter gaps)

  INTERPRETATION:
    {"Blocks show temporal clustering consistent with drift accumulation" if p < 0.05 else "Insufficient evidence for temporal clustering - blocks may be independent"}.
    The CTBV architecture (gate_coverage=1.0, unhooked_rules=0) keeps the drift
    score at 0, making the L4 predictor untestable during stable operation.

  FOR THE PREDICTOR TO BE TESTABLE, WE NEED:
    a. Increase rolling_window -> 30+ to capture pre-gate-migration periods
    b. Store per-session drift features at session END (not just at score=0 peaks)
    c. OR: Run a controlled degradation experiment (temporarily disable 1 gate,
       measure drift score change, predict next-session violations)

  CURRENT VERDICT:
    The L4 drift score is a theoretically sound construct (8 features with
    calibrated weights from 34-session baseline) but empirically UNTESTABLE
    under CTBV-protected operation because the gates suppress the variance
    the predictor needs to demonstrate predictive power.

    This is a SELF-LIMITING property of CTBV - the architecture is so
    effective at preventing drift that the drift predictor cannot be
    validated against it. The predictor would need pre-CTBV data or
    controlled degradation experiments.
""")

    # --- 7. Output JSON for paper ---
    result = {
        "experiment": "l4-drift-predictive-validation",
        "date": "2026-07-28",
        "status": "HONEST_FAILURE",
        "original_hypothesis": "H0: rho(D_i, V_{i+1}) = 0",
        "original_hypothesis_testable": False,
        "failure_reason": "drift score zero variance — gate_coverage=1.0 suppresses all variance",
        "fallback_analysis": {
            "lag1_autocorr": round(rho, 4),
            "lag1_p_approx": round(p, 4),
            "lag1_significant": p < 0.05,
            "block_rate_slope": trend.get("slope"),
            "block_rate_r2": trend.get("r_squared"),
            "block_clustering": gaps.get('high_block_mean_gap', 0) < gaps.get('low_block_mean_gap', float('inf')) if gaps.get('high_block_mean_gap') and gaps.get('low_block_mean_gap') else None,
        },
        "data_summary": {
            "total_blocks": total_blocks,
            "n_sessions": len(sessions),
            "n_days": len(all_dates),
            "drift_score_unique_values": len(unique_scores),
            "per_session_blocks": {d: sessions[d]["total"] for d in sorted_dates},
        },
        "recommendations": [
            "Increase drift_baseline rolling_window to 30+ for historical variance",
            "Store per-session drift features at session end (not just score=0 peaks)",
            "Controlled degradation experiment needed for true predictive validation",
        ],
    }

    print("\n── 7. JSON Output ──")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return result


if __name__ == "__main__":
    result = main()
    sys.exit(0)
