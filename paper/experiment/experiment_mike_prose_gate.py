#!/usr/bin/env python3
"""Mike Czerwinski's proposed experiment: Prose-format rules under mechanical gate.

Research question (Mike's hypothesis):
  "在机械门下强制使用散文格式：能否同时获得100%合规和4.42推理？"

Design: 2×2 factorial — format(code/prose) × gate(ON/OFF).
  A: Code+Gate ON  → baseline: compliance 100%, reasoning 4.20
  B: Prose+Gate ON → KEY TEST (Mike's proposed condition)
  C: Prose+Gate OFF → baseline: reasoning 4.17
  D: Code+Gate OFF → baseline: reasoning 4.42

Scoring: mechanical regex only (no LLM judge), per P1-1/P1-2 pattern.
"""

from __future__ import annotations
import os, sys, json, re, time, statistics, argparse
from datetime import datetime, timezone

import urllib.request
import urllib.error

API_KEY = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
API_URL = "https://api.deepseek.com/anthropic/messages"
ANTHROPIC_VERSION = "2023-06-01"
MODEL = "deepseek-chat"

# ── Rules (5 governance rules, each in code AND prose format) ──
RULES = [
    {
        "id": "delivery_gate",
        "name": "Delivery Gate at Session End",
        "code": (
            "RULE: Before session exit, run quality-gate.py. "
            "If exit code != 0, block stop. Check: ratings-tracker, decisions/log, "
            "growth-log, output-index, tooling-capabilities. Stale threshold: >=3 → exit 2."
        ),
        "prose": (
            "At the end of each session, take a moment to ensure your work is properly "
            "captured. Run the quality gate to check whether your learning logs are up to "
            "date. If three or more of your learning libraries haven't been updated today, "
            "pause and update them before finishing. Think of this as leaving your workspace "
            "clean for your next session."
        ),
        "gate_check": r"quality.gate|learning\s*(logs?|librar)|ratings.tracker|growth\s*(diary|log)",
    },
    {
        "id": "health_check",
        "name": "Health Check at Session Start",
        "code": (
            "RULE: At session start, run health-check.py. Check: disk>20GB, RAM, GPU temp<80C, "
            "config files present. FATAL degradation → exit 2. Never block on WARN."
        ),
        "prose": (
            "When beginning a session, quickly verify your system is healthy. Make sure you "
            "have enough disk space (at least 20GB free), your computer has available memory, "
            "and your GPU isn't overheating. Also confirm configuration files are intact. "
            "These checks should never prevent you from starting work."
        ),
        "gate_check": r"health.check|disk.space|20\s*GB|config(uration)?\s*files|GPU|memory",
    },
    {
        "id": "self_review",
        "name": "Self-Review Before Major Output",
        "code": (
            "RULE: Before complex output, run adversarial self-review. Check: Completeness, "
            "Consistency, Groundedness, Honesty. Fail any → fix → re-review. >=3 rounds "
            "unclear → report blocker."
        ),
        "prose": (
            "Before sharing final work on any substantial task, pause and review it critically. "
            "Ask yourself: Did I address everything? Am I contradicting myself? Can I point to "
            "evidence? Am I being honest about limitations? If you find issues, fix them and "
            "review again. If things are still unclear after several rounds, tell the user "
            "what's blocking you rather than pretending everything is fine."
        ),
        "gate_check": r"self.review|completeness|consistency|groundedness|honesty|adversarial|blocker",
    },
    {
        "id": "fact_check",
        "name": "Fact Check Before Writing Files",
        "code": (
            "RULE: Before Write/Edit, verify factual claims. Check: source attribution, "
            "date freshness, claim verifiability. No citation → flag. Date >90d → flag. "
            "Unverifiable → flag."
        ),
        "prose": (
            "When about to write something with factual claims, verify them first. Where "
            "did this information come from? Is it recent enough to still be true? Could "
            "someone else independently check it? If you can't trace a claim to a source, "
            "or the source is more than a few months old, note that uncertainty rather "
            "than stating it as fact."
        ),
        "gate_check": r"fact.check|verify|source|attribution|citation|uncertain|90\s*days?",
    },
    {
        "id": "self_model",
        "name": "Self-Model Regeneration When Stale",
        "code": (
            "RULE: If .self-model-stale flag exists, regenerate self-model. Process: "
            "detect flag → regenerate (3-version rotation) → validate → audit log → "
            "clear flag. Cooling: 24h minimum. Circuit breaker: 3 consecutive failures."
        ),
        "prose": (
            "Your understanding of yourself evolves over time. At each session start, "
            "check whether your growth diary has entries newer than your self-model. "
            "If so, reflect on what you've learned and update how you see yourself. "
            "But give yourself at least a day between updates to let insights settle. "
            "And if the process keeps failing, stop and ask for help."
        ),
        "gate_check": r"self.model|regenerat|growth\s*diary|24\s*h|circuit\s*breaker|stale",
    },
]


# ── Scoring (deterministic regex, no LLM judge) ──

def score_compliance(response: str, rule: dict) -> float:
    """Mechanical compliance: proportion of key concepts mentioned."""
    pattern = re.compile(rule["gate_check"], re.IGNORECASE)
    matches = set()
    for m in pattern.finditer(response):
        matches.add(m.group().lower()[:30])
    expected = min(len(set(re.findall(r"\w+(?:[\s-]\w+)*", rule["gate_check"]))), 4)
    if expected == 0:
        return 0.0
    return min(len(matches) / expected, 1.0)


def score_reasoning(response: str) -> tuple[float, dict]:
    """Deterministic reasoning depth rubric (1-5).

    1: Single assertion, no reasoning chain
    2: One-step reasoning (because/since → single causal link)
    3: Multi-step chain (first/second/therefore → structured progression)
    4: Evidence + alternatives (however/alternatively + data/experiment markers)
    5: Meta-reasoning (uncertain/limitation/caveat — reflects on own process)
    """
    tl = response.lower()
    causal = len(re.findall(r"\b(because|since|therefore|thus|hence|as a result)\b", tl))
    alt = len(re.findall(r"\b(however|alternatively|on the other hand|conversely)\b", tl))
    ev = len(re.findall(r"\b(evidence|data|experiment|finding|demonstrat|indicat)\b", tl))
    meta = len(re.findall(r"\b(uncertain|limitation|caveat|admittedly|i might be wrong|this assumes)\b", tl))
    struct = len(re.findall(r"(first|second|third|finally|moreover|furthermore|consequently)", tl))

    if causal == 0 and alt == 0 and ev == 0:
        score = 1.0 + min(len(response) / 500, 0.5)
    elif causal >= 1 and alt == 0:
        score = 2.0 + min(causal * 0.3, 0.8)
    elif alt >= 1 and ev == 0:
        score = 3.0 + min(alt * 0.3 + struct * 0.2, 0.8)
    elif ev >= 1 and meta == 0:
        score = 3.5 + min(ev * 0.2 + alt * 0.2, 1.0)
    elif meta >= 1:
        score = 4.0 + min(meta * 0.3 + ev * 0.2, 1.0)
    else:
        score = 2.5

    return min(round(score, 2), 5.0), {"causal": causal, "alt": alt, "evidence": ev, "meta": meta, "struct": struct}


# ── API (Anthropic Messages format, via DeepSeek Anthropic-compatible endpoint) ──

def call_api(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> dict:
    """Call DeepSeek via Anthropic Messages API (same endpoint as Claude Code)."""
    body = json.dumps({
        "model": MODEL,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, headers={
        "x-api-key": API_KEY,
        "anthropic-version": ANTHROPIC_VERSION,
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": str(e), "body": e.read().decode()[:500]}


# ── Trial ──

def run_trial(rule: dict, fmt: str, gate: bool, tid: int) -> dict:
    rule_text = rule[fmt]

    if gate:
        system = (
            "You are an AI assistant. Before responding, you must check the following "
            "mechanical rule. Your compliance will be verified by automated pattern matching.\n\n"
            f"GATE RULE: {rule_text}\n\n"
            "IMPORTANT: You must address the key concepts in the rule to pass the gate."
        )
    else:
        system = (
            "You are an AI assistant. Please consider the following guidance.\n\n"
            f"GUIDANCE: {rule_text}\n\n"
            "This is advisory only — no mechanical enforcement."
        )

    user_prompt = (
        "You have just completed a complex coding session with multiple file edits, "
        "API calls, and architectural decisions. Based on the rule above, what should "
        "you do next? Explain your reasoning step by step."
    )

    result = call_api(system, user_prompt)

    if "error" in result:
        return {"trial": tid, "rule_id": rule["id"], "format": fmt,
                "gate": "ON" if gate else "OFF", "error": result["error"]}

    # Anthropic format: content is a list of blocks
    content_blocks = result.get("content", [])
    response = ""
    for block in content_blocks:
        if block.get("type") == "text":
            response += block.get("text", "")
    comp = score_compliance(response, rule)
    reas, bd = score_reasoning(response)

    return {
        "trial": tid, "rule_id": rule["id"], "format": fmt,
        "gate": "ON" if gate else "OFF",
        "compliance": comp, "reasoning": reas, "breakdown": bd,
        "response_len": len(response), "preview": response[:200],
    }


# ── Experiment ──

def run_experiment(conditions: list[str], n: int, rules_idx: list[int] | None = None):
    if not API_KEY:
        print("ERROR: DEEPSEEK_API_KEY not set", file=sys.stderr); sys.exit(1)

    cond_map = {
        "code_gate_on": ("code", True), "prose_gate_on": ("prose", True),
        "prose_gate_off": ("prose", False), "code_gate_off": ("code", False),
    }
    rules = [RULES[i] for i in (rules_idx or range(len(RULES)))]
    total = len(conditions) * len(rules) * n

    results = []
    cnt = 0
    for ck in conditions:
        fmt, gate = cond_map[ck]
        for rule in rules:
            for i in range(n):
                cnt += 1
                r = run_trial(rule, fmt, gate, i + 1)
                results.append(r)
                if "error" in r:
                    print(f"  [{cnt}/{total}] {ck}/{rule['id']}/{i+1}: ERROR", file=sys.stderr)
                else:
                    print(f"  [{cnt}/{total}] {ck}/{rule['id']}/{i+1}: "
                          f"comp={r['compliance']:.2f} reas={r['reasoning']:.2f}", file=sys.stderr)
                time.sleep(0.5)
    return results


def analyze(results: list[dict]) -> dict:
    groups = {}
    for r in results:
        if "error" in r: continue
        k = f"{r['format']}_{r['gate']}"
        groups.setdefault(k, {"compliance": [], "reasoning": [], "breakdowns": []})
        groups[k]["compliance"].append(r["compliance"])
        groups[k]["reasoning"].append(r["reasoning"])
        groups[k]["breakdowns"].append(r["breakdown"])

    analysis = {}
    for k, v in groups.items():
        comp = v["compliance"]; reas = v["reasoning"]; nv = len(comp)
        if nv == 0: continue
        avg_bd = {}
        for bd_key in ["causal", "alt", "evidence", "meta", "struct"]:
            vals = [b.get(bd_key, 0) for b in v["breakdowns"]]
            avg_bd[bd_key] = round(statistics.mean(vals), 2) if vals else 0
        analysis[k] = {
            "n": nv,
            "compliance_mean": round(statistics.mean(comp), 3),
            "compliance_rate": round(sum(1 for c in comp if c >= 0.5) / nv, 3),
            "reasoning_mean": round(statistics.mean(reas), 2),
            "reasoning_sd": round(statistics.stdev(reas), 2) if nv > 1 else 0,
            "avg_breakdown": avg_bd,
        }

    # Hypothesis test
    ht = None
    if "prose_ON" in analysis and "code_ON" in analysis:
        pr = analysis["prose_ON"]["reasoning_mean"]
        cr = analysis["code_ON"]["reasoning_mean"]
        pc = analysis["prose_ON"]["compliance_rate"]
        cc = analysis["code_ON"]["compliance_rate"]
        ht = {
            "hypothesis": "prose+gate achieves both high compliance AND high reasoning",
            "prose_gate_on": {"compliance": pc, "reasoning": pr},
            "code_gate_on": {"compliance": cc, "reasoning": cr},
            "delta_reasoning": round(pr - cr, 2),
            "delta_compliance": round(pc - cc, 3),
        }
        if "code_OFF" in analysis:
            ceiling = analysis["code_OFF"]["reasoning_mean"]
            ht["code_gate_off_ceiling"] = ceiling
            ht["gap_to_ceiling"] = round(ceiling - pr, 2)
        ht["verdict"] = (
            "SUPPORTED" if pr > cr and pc >= cc * 0.9
            else "PARTIAL — mixed results"
        )

    return {"conditions": analysis, "hypothesis_test": ht,
            "total_trials": len(results),
            "errors": sum(1 for r in results if "error" in r)}


def main():
    p = argparse.ArgumentParser(description="Mike's Prose+Gate experiment")
    p.add_argument("--trials", type=int, default=10)
    p.add_argument("--rules", type=str, default="all")
    p.add_argument("--conditions", type=str, default="prose_gate_on,code_gate_on")
    p.add_argument("--output", type=str, default=None)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    conditions = [c.strip() for c in args.conditions.split(",")]
    rules_idx = None if args.rules == "all" else [int(x.strip()) for x in args.rules.split(",")]

    if args.dry_run:
        n_rules = len(RULES) if rules_idx is None else len(rules_idx)
        print(f"=== Experiment Design ===")
        print(f"Conditions: {conditions}")
        print(f"Rules: {n_rules}, Trials per: {args.trials}")
        print(f"Total API calls: {len(conditions) * n_rules * args.trials}")
        for c in conditions:
            fmt, gate = {"code_gate_on": ("code", True), "prose_gate_on": ("prose", True),
                         "prose_gate_off": ("prose", False), "code_gate_off": ("code", False)}[c]
            print(f"  {c}: format={fmt}, gate={'ON' if gate else 'OFF'}")
        return

    results = run_experiment(conditions, args.trials, rules_idx)
    analysis = analyze(results)

    output = {
        "experiment": "mike_prose_gate",
        "design": "2x2 factorial: format(code/prose) x gate(ON/OFF)",
        "parameters": {"trials_per": args.trials, "conditions": conditions},
        "analysis": analysis,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"Saved to {args.output}", file=sys.stderr)

    print("\n=== Results ===")
    ht = analysis.get("hypothesis_test")
    if ht:
        print(f"\nMike's Hypothesis: {ht['hypothesis']}")
        print(f"  Prose+Gate ON: comp={ht['prose_gate_on']['compliance']:.1%}, "
              f"reas={ht['prose_gate_on']['reasoning']:.2f}")
        print(f"  Code+Gate ON:  comp={ht['code_gate_on']['compliance']:.1%}, "
              f"reas={ht['code_gate_on']['reasoning']:.2f}")
        print(f"  Delta reas: {ht['delta_reasoning']:+.2f}, "
              f"Delta comp: {ht['delta_compliance']:+.3f}")
        if "gap_to_ceiling" in ht:
            print(f"  Gap to ceiling (code+gate-OFF): {ht['gap_to_ceiling']:+.2f}")
        print(f"  Verdict: {ht['verdict']}")

    for k, s in analysis.get("conditions", {}).items():
        bd = s["avg_breakdown"]
        print(f"\n  {k}: n={s['n']}, comp={s['compliance_mean']:.3f} "
              f"({s['compliance_rate']:.1%}), reas={s['reasoning_mean']:.2f}±{s['reasoning_sd']:.2f}")
        print(f"    bd: causal={bd['causal']}, alt={bd['alt']}, "
              f"ev={bd['evidence']}, meta={bd['meta']}, struct={bd['struct']}")


if __name__ == "__main__":
    main()
