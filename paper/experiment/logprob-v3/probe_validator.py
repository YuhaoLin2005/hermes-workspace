# probe_validator.py — Pre-experiment probe validation gate.
# Importers: experiment_v3.py (pre-validation before confirmatory experiment)
# Data schema: validated_probes.json — {"valid": [...], "invalid": [{"probe","reason"}], "stats": {...}}
# API: DeepSeek /v1/chat/completions (logprobs=True, top_logprobs=20)
# User instruction: "按照能发顶刊的专家建议走" — expert panel requires pre-validation of all probes
# Gate: Fact-Forcing (ECC_GATEGUARD=off disables)
#!/usr/bin/env python3
"""
probe_validator.py — Pre-experiment probe validation gate.

Problem: When compliant_token or violating_token is NOT in top_logprobs,
  DeepSeek API returns nothing for that token, and we assign -10.0 floor.
  This creates artificial differentials that invalidate the measurement.

Solution (Statistics expert, Nature Methods): For every probe, verify both
  tokens appear in top_logprobs for ALL 3 conditions. Drop any that fail.
  This eliminates the -10.0 floor artifact entirely.

Design: Three-condition validation per probe.
  - Baseline (no constraint): "你是AI助手。"
  - Imperative: constraint in command form
  - Syllogistic: constraint in causal-chain form
  A probe is VALID iff compliant_token AND violating_token both appear
  in top_logprobs for all 3 conditions.

Usage:
  python probe_validator.py              # validate all probes
  python probe_validator.py --json       # output validated probes as JSON
  python probe_validator.py --check N    # validate single probe by index
"""

import json, sys, os, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

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
        if key:
            return key
    settings_path = Path.home() / ".claude" / "settings.json"
    if settings_path.exists():
        try:
            cfg = json.loads(settings_path.read_text(encoding="utf-8"))
            for var in ("DEEPSEEK_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"):
                key = cfg.get("env", {}).get(var, "").strip()
                if key:
                    return key
        except Exception:
            pass
    return None


def call_deepseek_logprobs(api_key, system_prompt, user_prompt, max_tokens=1):
    import urllib.request, urllib.error
    url = f"{DEEPSEEK_BASE}/chat/completions"
    body = {
        "model": DEEPSEEK_MODEL, "max_tokens": max_tokens, "temperature": 0.2,
        "logprobs": True, "top_logprobs": 20,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [API ERROR] {e}", file=sys.stderr)
        return None


def extract_top_tokens(response) -> set:
    """Extract set of token strings in top_logprobs."""
    try:
        content = response["choices"][0]["logprobs"]["content"]
        return {e["token"] for e in content[0].get("top_logprobs", [])}
    except (KeyError, IndexError, TypeError):
        return set()


def extract_first_token(response) -> str:
    """Extract the actually-chosen first token."""
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return "?"


# ── Validation Logic ─────────────────────────────────────────────────────
def validate_probe(api_key, probe, index):
    """Validate one probe across 3 conditions.

    Returns dict with:
      - valid: bool
      - conditions: {baseline, imperative, syllogistic} each with {chosen, a_in_top, b_in_top}
      - reason: str (if invalid)
    """
    theme = probe["theme"]
    a_token = probe["compliant_token"]
    b_token = probe["violating_token"]

    result = {
        "index": index,
        "theme": theme,
        "compliant_token": a_token,
        "violating_token": b_token,
        "valid": True,
        "conditions": {},
        "reason": None,
    }

    conditions = [
        ("baseline", BASELINE_SYSTEM),
        ("imperative", probe["imperative"]),
        ("syllogistic", probe["syllogistic"]),
    ]

    for cond_name, system_prompt in conditions:
        resp = call_deepseek_logprobs(api_key, system_prompt, probe["user_prompt"])
        if resp is None:
            result["valid"] = False
            result["reason"] = f"API call failed for {cond_name}"
            result["conditions"][cond_name] = {"error": "API failed"}
            return result

        top_tokens = extract_top_tokens(resp)
        chosen = extract_first_token(resp)
        a_in_top = a_token in top_tokens
        b_in_top = b_token in top_tokens

        lp_data = {}
        try:
            content = resp["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
            for entry in content:
                if entry["token"] == a_token:
                    lp_data["a_logprob"] = round(entry["logprob"], 4)
                if entry["token"] == b_token:
                    lp_data["b_logprob"] = round(entry["logprob"], 4)
        except (KeyError, IndexError):
            pass

        result["conditions"][cond_name] = {
            "chosen": chosen,
            "a_in_top": a_in_top,
            "b_in_top": b_in_top,
            **lp_data,
        }

        if not a_in_top or not b_in_top:
            missing = []
            if not a_in_top:
                missing.append(f"'{a_token}' (compliant)")
            if not b_in_top:
                missing.append(f"'{b_token}' (violating)")
            result["valid"] = False
            result["reason"] = f"{cond_name}: {', '.join(missing)} not in top_logprobs"

    # Also check: does the model actually choose A or B?
    for cond_name in ["baseline", "imperative", "syllogistic"]:
        chosen = result["conditions"].get(cond_name, {}).get("chosen", "?")
        if chosen not in (a_token, b_token):
            if result["valid"]:
                result["valid"] = False
                result["reason"] = f"{cond_name}: model chose '{chosen}' instead of '{a_token}' or '{b_token}'"

    return result


def validate_all(api_key, probes, label="", start_idx=0):
    """Validate all probes. Returns (valid_list, invalid_list)."""
    valid, invalid = [], []
    for i, probe in enumerate(probes):
        idx = start_idx + i
        theme = probe["theme"]
        print(f"  [{label}] {i+1}/{len(probes)}: {theme} ...", file=sys.stderr, end=" ")
        result = validate_probe(api_key, probe, idx)
        if result["valid"]:
            valid.append(probe)
            print("✓ VALID", file=sys.stderr)
        else:
            invalid.append({"probe": probe, "reason": result["reason"], "details": result})
            print(f"✗ {result['reason']}", file=sys.stderr)
        if i < len(probes) - 1:
            time.sleep(0.3)
    return valid, invalid


# ── Report ───────────────────────────────────────────────────────────────
def print_report(valid_count, invalid_count, invalid_details):
    print()
    print("=" * 60)
    print("  Probe Validation Report")
    print("=" * 60)
    print(f"  Valid: {valid_count}  |  Invalid: {invalid_count}")
    print(f"  Pass rate: {valid_count/(valid_count+invalid_count)*100:.0f}%")
    print()
    if invalid_details:
        print("  Invalid probes:")
        for item in invalid_details:
            print(f"    [{item['probe']['theme']}] {item['reason']}")
    print()


def save_validated(valid_probes, invalid_details, stats):
    """Save validated probes and validation report."""
    payload = {
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "model": DEEPSEEK_MODEL,
        "valid_count": len(valid_probes),
        "invalid_count": len(invalid_details),
        "valid_probes": valid_probes,
        "invalid_probes": [
            {"theme": d["probe"]["theme"], "reason": d["reason"]}
            for d in invalid_details
        ],
        "stats": stats,
    }
    VALIDATED_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Saved: {VALIDATED_FILE}", file=sys.stderr)


def main():
    import argparse
    p = argparse.ArgumentParser(description="Probe Validator — pre-experiment gate")
    p.add_argument("--json", action="store_true", help="Output validated probes as JSON")
    p.add_argument("--check", type=int, help="Validate single probe by index")
    args = p.parse_args()

    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    # Load probes from probe_pool.py (40 probes across 4 categories)
    sys.path.insert(0, str(EXPERIMENT_DIR))
    import probe_pool

    api_key = get_api_key()
    if not api_key:
        print("FATAL: No API key found.", file=sys.stderr)
        sys.exit(1)

    if args.check is not None:
        idx = args.check
        if idx < 0 or idx >= len(probe_pool.ALL_PROBES):
            print(f"Invalid index {idx}. Valid range: 0-{len(probe_pool.ALL_PROBES)-1}", file=sys.stderr)
            sys.exit(1)
        probe = probe_pool.ALL_PROBES[idx]
        result = validate_probe(api_key, probe, idx)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.json:
        if VALIDATED_FILE.exists():
            print(VALIDATED_FILE.read_text(encoding="utf-8"))
        else:
            print(json.dumps({"error": "no validated probes found"}, ensure_ascii=False))
        return

    # Full validation — validate by category for structured reporting
    all_probes = probe_pool.ALL_PROBES
    categories = {}
    for p in all_probes:
        categories.setdefault(p.get("category", "unknown"), []).append(p)

    print(f"[validator] Validating {len(all_probes)} probes x 3 conditions...", file=sys.stderr)
    print(f"[validator] Model: {DEEPSEEK_MODEL}  |  Categories: {list(categories.keys())}", file=sys.stderr)
    print(file=sys.stderr)

    all_valid, all_invalid = [], []
    idx = 0
    for cat_name, cat_probes in categories.items():
        print(f"  --- {cat_name} ({len(cat_probes)} probes) ---", file=sys.stderr)
        valid, invalid = validate_all(api_key, cat_probes, cat_name.upper(), idx)
        all_valid.extend(valid)
        all_invalid.extend(invalid)
        idx += len(cat_probes)

    stats = {
        "total": len(all_probes),
        "valid": len(all_valid),
        "invalid": len(all_invalid),
        "pass_rate": round(len(all_valid) / len(all_probes) * 100, 1),
        "by_category": {
            cat: {
                "total": len(categories[cat]),
                "valid": sum(1 for p in all_valid if p.get("category") == cat),
                "invalid": sum(1 for d in all_invalid if d["probe"].get("category") == cat),
            }
            for cat in categories
        },
    }

    print_report(len(all_valid), len(all_invalid), all_invalid)
    save_validated(all_valid, all_invalid, stats)


if __name__ == "__main__":
    main()
