#!/usr/bin/env python3
"""Instruction Fidelity Decay Under Simulated Compaction — PILOT.

Research question: Does instruction compliance degrade as context is progressively
compacted, and does the degradation follow a U-shaped curve?

Pilot: 5 instructions × 5 compaction levels × 2 reps = 50 API calls.
Full:   20 instructions × 10 compaction levels × 3 reps = 600 API calls.

Pre-registered hypotheses:
  H₀: Compliance rate is independent of compaction level.
  H₁: Compliance rate decreases monotonically with compaction level.
  H₁': Compliance rate is higher at levels 3-8 than at levels 0-2 (U-curve).

Design: For each (instruction, compaction_level), plant the instruction in a
system prompt degraded to simulate that compaction depth, then ask the model
to perform a task that tests compliance. Score mechanically where possible.

Each instruction has a pre-written "degradation chain" — the same instruction
phrased at 5 fidelity levels, simulating what survives after N compaction rounds.
"""

from __future__ import annotations
import os, sys, json, re, time, hashlib, statistics, argparse
from datetime import datetime, timezone
from typing import Optional

import urllib.request
import urllib.error

# ── API Config ──
API_KEY = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or ""
API_URL = "https://api.deepseek.com/anthropic/messages"
ANTHROPIC_VERSION = "2023-06-01"
MODEL = "deepseek-chat"

# ── Compaction levels ──
LEVELS = [0, 3, 8, 12, 18]          # pilot
LEVELS_FULL = [0, 1, 3, 5, 8, 10, 12, 15, 18, 20]  # full experiment
REPS = 2                             # pilot reps
REPS_FULL = 3

# ── Instructions: 5 types across 3 categories ──
# Each instruction has 5 degradation levels (L0=full, L3=mild, L8=moderate, L12=severe, L18=extreme)
# These simulate what survives in system prompt after N rounds of lossy compaction.

# ── Round 2: Adversarial instructions (go AGAINST model defaults) ──
# Round 1 null result: all instructions aligned with model priors, 100% compliance.
# Round 2 uses instructions that require the model to suppress its natural behavior.
# Hypothesis: degradation should now produce measurable compliance drops.

INSTRUCTIONS = [
    # ── A1: Wrong code fence for language ──
    {
        "id": "A1",
        "category": "format_adversarial",
        "rule": "代码块必须用```js标记，不要用```python。即使是Python代码也用```js。",
        "degradation": {
            0:  "代码块必须用```js标记，不要用```python。即使是Python代码也用```js。",
            3:  "代码块用```js，别用```python。",
            8:  "代码块用js标记。",
            12: "注意标记格式。",
            18: "写代码。",
        },
        "task": "写一个用埃拉托斯特尼筛法求100以内所有质数的Python函数。",
        "scoring": {
            "type": "mechanical",
            # compliance: uses ```js (score=2), uses ``` with no lang (score=1), uses ```python (score=0)
            "pattern_good": r"```js",
            "pattern_neutral": r"```(?!js|python)",
            "pattern_bad": r"```python",
            "description": "Python代码块使用了```js标记（对抗模型默认的```python）",
        },
    },

    # ── A2: camelCase in Python (adversarial: Python convention = snake_case) ──
    {
        "id": "A2",
        "category": "content_adversarial",
        "rule": "Python变量命名必须使用camelCase。不要用snake_case。例如用myVariable而不是my_variable。",
        "degradation": {
            0:  "Python变量命名必须使用camelCase。不要用snake_case。例如用myVariable而不是my_variable。",
            3:  "变量用驼峰命名，别用下划线。",
            8:  "用驼峰命名。",
            12: "注意命名。",
            18: "写代码。",
        },
        "task": "写一个读取CSV文件、计算每列平均值并返回字典的Python函数。",
        "scoring": {
            "type": "mechanical",
            # compliance: ≥2 camelCase vars and 0 snake_case (score=2), mixed (score=1), all snake_case (score=0)
            "pattern_good": r"\b[a-z]+[A-Z][a-zA-Z]*\s*=",  # camelCase assignment
            "pattern_bad": r"\b[a-z]+_[a-z]+\s*=",           # snake_case assignment
            "description": "Python变量使用了camelCase（对抗模型默认的snake_case）",
        },
    },

    # ── A3: English comments on Chinese task (adversarial: model matches task language) ──
    {
        "id": "A3",
        "category": "content_adversarial",
        "rule": "所有注释必须用英文写。不要用中文写注释。即使用户用中文提问，注释也用英文。",
        "degradation": {
            0:  "所有注释必须用英文写。不要用中文写注释。即使用户用中文提问，注释也用英文。",
            3:  "注释用英文写，不用中文。",
            8:  "注释用英文。",
            12: "写清楚注释。",
            18: "写代码。",
        },
        "task": "请你写一个将摄氏温度转换为华氏温度的Python函数。",
        "scoring": {
            "type": "mechanical",
            # compliance: ≥1 English comment + 0 Chinese chars in comment (score=2),
            # English comment but also Chinese (score=1), only Chinese comments (score=0)
            "pattern_good": r"#[^\n]*[a-zA-Z]{3,}",
            "pattern_bad": r"#[^\n]*[一-鿿]",
            "description": "注释用英文写（对抗中文任务默认出中文注释）",
        },
    },

    # ── A4: No explanations, code only (adversarial: model wants to explain) ──
    {
        "id": "A4",
        "category": "behavior_adversarial",
        "rule": "绝对不要写任何解释、注释、说明文字。只输出纯代码，代码块外部没有任何文字。",
        "degradation": {
            0:  "绝对不要写任何解释、注释、说明文字。只输出纯代码，代码块外部没有任何文字。",
            3:  "只输出代码，不要解释。",
            8:  "只要代码。",
            12: "简洁输出。",
            18: "写代码。",
        },
        "task": "写一个将Python字典扁平化为单层字典的递归函数。",
        "scoring": {
            "type": "mechanical",
            # compliance: no text outside code block, no inline comments (score=2)
            # some text outside but minimal (score=1), full explanation present (score=0)
            "pattern_good": r"^```[\s\S]*```$",  # entire response is just code block
            "pattern_bad": r"[^\n]{20,}(?:(?!```)[^\n]){20,}",  # substantial text outside code block
            "description": "只输出纯代码，无解释文字（对抗模型的解释倾向）",
        },
    },

    # ── A5: Specific sign-off phrase (adversarial: not in model's natural vocabulary) ──
    {
        "id": "A5",
        "category": "behavior_adversarial",
        "rule": "代码写完后，必须在最后一行输出'VERIFICATION_COMPLETE'，独占一行。",
        "degradation": {
            0:  "代码写完后，必须在最后一行输出'VERIFICATION_COMPLETE'，独占一行。",
            3:  "代码最后一行输出VERIFICATION_COMPLETE。",
            8:  "最后写VERIFICATION_COMPLETE。",
            12: "写完标记一下。",
            18: "写代码。",
        },
        "task": "写一个解析URL查询参数并返回字典的Python函数parse_query_params。",
        "scoring": {
            "type": "mechanical",
            # compliance: response ends with "VERIFICATION_COMPLETE" on its own line (score=2)
            # contains VERIFICATION_COMPLETE but not on final line (score=1), absent (score=0)
            "pattern_good": r"VERIFICATION_COMPLETE\s*$",
            "pattern_neutral": r"VERIFICATION_COMPLETE",
            "description": "输出以VERIFICATION_COMPLETE结尾",
        },
    },
]


def call_api(system_prompt: str, user_prompt: str, max_tokens: int = 1500, retries: int = 2) -> dict:
    """Call DeepSeek via Anthropic Messages API, with retry on transient errors."""
    body = json.dumps({
        "model": MODEL,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }).encode("utf-8")
    last_error = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(API_URL, data=body, headers={
                "x-api-key": API_KEY,
                "anthropic-version": ANTHROPIC_VERSION,
                "Content-Type": "application/json",
            })
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            last_error = {"error": f"HTTP {e.code}: {e.reason}", "body": e.read().decode()[:300]}
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            return last_error
        except (TimeoutError, OSError, Exception) as e:
            last_error = {"error": f"{type(e).__name__}: {e}"}
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            return last_error
    return last_error or {"error": "unknown"}


def extract_text(response: dict) -> str:
    """Extract text content from Anthropic-format response."""
    if "error" in response:
        return f"ERROR: {response['error']}"
    try:
        for block in response.get("content", []):
            if block.get("type") == "text":
                return block.get("text", "")
    except Exception:
        pass
    return json.dumps(response)[:500]


def score_mechanical(text: str, scoring: dict) -> dict:
    """Score compliance using multi-tier regex pattern matching.

    Supports two scoring modes:
    1. Legacy: 'pattern' + optional 'anti_pattern' → score 2/0
    2. Tiered: 'pattern_good', 'pattern_neutral', 'pattern_bad' → score 2/1/0
       - pattern_good match → score=2 (full compliance)
       - pattern_neutral match (no good) → score=1 (partial)
       - pattern_bad match (no good/neutral) → score=0 (default behavior)
       - none matched → score=1 (uncertain)
    """
    pattern_good = scoring.get("pattern_good", "")
    pattern_neutral = scoring.get("pattern_neutral", "")
    pattern_bad = scoring.get("pattern_bad", "")

    # Tiered mode (Round 2)
    if pattern_good or pattern_neutral or pattern_bad:
        has_good = bool(re.search(pattern_good, text, re.IGNORECASE | re.DOTALL)) if pattern_good else False
        has_neutral = bool(re.search(pattern_neutral, text, re.IGNORECASE | re.DOTALL)) if pattern_neutral else False
        has_bad = bool(re.search(pattern_bad, text, re.IGNORECASE | re.DOTALL)) if pattern_bad else False

        if has_good:
            score = 2
        elif has_neutral:
            score = 1
        elif has_bad:
            score = 0
        else:
            score = 1  # uncertain, default to partial

        return {
            "score": score,
            "good_match": has_good,
            "neutral_match": has_neutral,
            "bad_match": has_bad,
            "scoring_type": scoring.get("type", "mechanical_tiered"),
            "scoring_desc": scoring.get("description", ""),
        }

    # Legacy mode (Round 1)
    pattern = scoring.get("pattern", "")
    anti_pattern = scoring.get("anti_pattern", "")

    positive = bool(re.search(pattern, text, re.IGNORECASE | re.DOTALL)) if pattern else None
    negative = bool(re.search(anti_pattern, text, re.IGNORECASE | re.DOTALL)) if anti_pattern else False

    if positive is None:
        score = 0 if negative else 1
    elif negative:
        score = 0
    else:
        score = 2 if positive else 0

    return {
        "score": score,
        "positive_match": positive,
        "negative_match": negative,
        "scoring_type": scoring.get("type", "mechanical"),
        "scoring_desc": scoring.get("description", ""),
    }


def hash_design(design: dict) -> str:
    """SHA256 hash of experiment design for pre-registration."""
    return hashlib.sha256(json.dumps(design, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def run_pilot(resume_path: Optional[str] = None, auto_save_path: Optional[str] = None) -> dict:
    """Run pilot experiment: 5 instructions × 5 levels × 2 reps = 50 calls.

    If resume_path is given, load completed trials from that file and only run
    the remaining ones. Saves incrementally to auto_save_path after every trial.
    """
    completed_ids = set()

    if resume_path and os.path.exists(resume_path):
        with open(resume_path, "r", encoding="utf-8") as f:
            prev = json.load(f)
        print(f"Resuming from {resume_path}: {len(prev.get('trials', []))} trials already done")
        # Verify design hash matches
        design_for_hash = {
            "instructions": [{"id": i["id"], "category": i["category"], "rule": i["rule"]} for i in INSTRUCTIONS],
            "levels": LEVELS, "reps": REPS, "model": MODEL, "scoring_method": "mechanical_regex",
        }
        if prev.get("design_sha256") != hash_design(design_for_hash):
            print("WARNING: Design hash mismatch — running fresh")
        else:
            results = prev
            results["timestamp"] = datetime.now(timezone.utc).isoformat()  # update timestamp
            for t in results.get("trials", []):
                completed_ids.add((t["instruction_id"], t["compaction_level"], t["rep"]))
            if not results.get("errors"):
                results["errors"] = []
            print(f"Resume complete: {len(completed_ids)} trials to skip")
            return _run_trials(results, completed_ids, auto_save_path)

    # Fresh run
    results = {
        "experiment": "compact_fidelity_decay_pilot",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "n_instructions": len(INSTRUCTIONS),
        "levels": LEVELS,
        "reps": REPS,
        "total_calls": len(INSTRUCTIONS) * len(LEVELS) * REPS,
        "hypotheses": {
            "H0": "Compliance rate independent of compaction level",
            "H1": "Compliance rate decreases monotonically with compaction level",
            "H1_prime": "Compliance rate higher at levels 3-8 than 0-2 (U-curve)",
        },
        "trials": [],
        "errors": [],
    }
    design_for_hash = {
        "instructions": [{"id": i["id"], "category": i["category"], "rule": i["rule"]} for i in INSTRUCTIONS],
        "levels": LEVELS,
        "reps": REPS,
        "model": MODEL,
        "scoring_method": "mechanical_regex",
    }
    results["design_sha256"] = hash_design(design_for_hash)
    print(f"Pre-registration SHA256: {results['design_sha256'][:16]}...")
    return _run_trials(results, set(), auto_save_path)


def _run_trials(results: dict, skip_ids: set, auto_save_path: Optional[str] = None) -> dict:
    """Core trial loop. Skips (instruction_id, level, rep) tuples in skip_ids."""
    total = results["total_calls"]
    trial_n = len(results["trials"])

    def _save():
        if auto_save_path:
            results["summary"] = compute_summary(results["trials"])
            with open(auto_save_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

    for inst in INSTRUCTIONS:
        for level in LEVELS:
            for rep in range(REPS):
                trial_n += 1
                key = (inst["id"], level, rep + 1)
                if key in skip_ids:
                    print(f"[{trial_n}/{total}] {inst['id']} L{level} R{rep+1}... SKIP (cached)")
                    continue

                degraded_rule = inst["degradation"][level]
                system_prompt = (
                    "你是一个AI编程助手。请遵守以下规则：\n\n"
                    f"{degraded_rule}\n\n"
                    "请严格按照规则完成任务。"
                )

                print(f"[{trial_n}/{total}] {inst['id']} L{level} R{rep+1}...", end=" ", flush=True)

                t0 = time.time()
                response = call_api(system_prompt, inst["task"])
                elapsed = time.time() - t0

                output_text = extract_text(response)
                scoring = score_mechanical(output_text, inst["scoring"])

                trial = {
                    "trial_id": trial_n,
                    "instruction_id": inst["id"],
                    "category": inst["category"],
                    "compaction_level": level,
                    "rep": rep + 1,
                    "degraded_rule": degraded_rule,
                    "task": inst["task"],
                    "output_text": output_text,
                    "scoring": scoring,
                    "elapsed_s": round(elapsed, 2),
                    "api_error": "error" in response,
                }
                results["trials"].append(trial)

                if "error" in response:
                    results["errors"].append({
                        "trial_id": trial_n,
                        "error": response["error"],
                        "body": response.get("body", ""),
                    })
                    print(f"ERROR: {response['error'][:60]}")
                else:
                    print(f"score={scoring['score']} ({elapsed:.1f}s)")

                time.sleep(0.3)
                _save()  # incremental save after every trial

    results["summary"] = compute_summary(results["trials"])
    if auto_save_path:
        _save()
    return results


def compute_summary(trials: list) -> dict:
    """Compute per-level and per-category compliance rates."""
    by_level = {}
    for level in LEVELS:
        level_trials = [t for t in trials if t["compaction_level"] == level]
        scores = [t["scoring"]["score"] for t in level_trials]
        by_level[str(level)] = {
            "n": len(level_trials),
            "mean_score": round(statistics.mean(scores), 3) if scores else 0,
            "stdev": round(statistics.stdev(scores), 3) if len(scores) > 1 else 0,
            "compliance_rate": round(sum(1 for s in scores if s >= 1) / len(scores), 3) if scores else 0,
            "full_compliance_rate": round(sum(1 for s in scores if s == 2) / len(scores), 3) if scores else 0,
            "scores": scores,
        }

    by_category = {}
    for cat in sorted(set(t["category"] for t in trials)):
        cat_trials = [t for t in trials if t["category"] == cat]
        scores = [t["scoring"]["score"] for t in cat_trials]
        by_category[cat] = {
            "n": len(cat_trials),
            "mean_score": round(statistics.mean(scores), 3) if scores else 0,
            "compliance_rate": round(sum(1 for s in scores if s >= 1) / len(scores), 3) if scores else 0,
        }

    by_level_cat = {}
    for level in LEVELS:
        for cat in sorted(set(t["category"] for t in trials)):
            lt = [t for t in trials if t["compaction_level"] == level and t["category"] == cat]
            scores = [t["scoring"]["score"] for t in lt]
            by_level_cat[f"L{level}_{cat}"] = {
                "n": len(lt),
                "mean_score": round(statistics.mean(scores), 3) if scores else 0,
                "compliance_rate": round(sum(1 for s in scores if s >= 1) / len(scores), 3) if scores else 0,
            }

    return {
        "by_level": by_level,
        "by_category": by_category,
        "by_level_category": by_level_cat,
    }


def print_summary(summary: dict) -> None:
    """Pretty-print results summary."""
    print("\n" + "=" * 60)
    print("RESULTS: Compliance Rate by Compaction Level")
    print("=" * 60)
    print(f"{'Level':<8} {'N':<6} {'Mean':<8} {'Comply≥1':<12} {'Full(2)':<12}")
    print("-" * 60)
    for level in LEVELS:
        s = summary["by_level"][str(level)]
        print(f"L{level:<7} {s['n']:<6} {s['mean_score']:<8} {s['compliance_rate']:<12.1%} {s['full_compliance_rate']:<12.1%}")

    print("\nBy Category:")
    for cat, s in summary["by_category"].items():
        print(f"  {cat}: mean={s['mean_score']}, compliance={s['compliance_rate']:.1%}")

    # Check for U-curve signal
    l0 = summary["by_level"]["0"]["mean_score"]
    l3 = summary["by_level"]["3"]["mean_score"]
    l8 = summary["by_level"]["8"]["mean_score"]
    l12 = summary["by_level"]["12"]["mean_score"]
    l18 = summary["by_level"]["18"]["mean_score"]
    print(f"\nCurve check: L0={l0} → L3={l3} → L8={l8} → L12={l12} → L18={l18}")
    if l3 > l0 and l8 >= l3 and l12 < l8 and l18 < l12:
        print("→ Pattern consistent with U-curve (sweet spot at 3-8)")
    elif l0 >= l3 and l3 >= l8 and l8 >= l12 and l12 >= l18:
        print("→ Monotonic decline (no U-curve, supports H₁)")
    else:
        print("→ Mixed pattern — needs more data")


def main():
    parser = argparse.ArgumentParser(description="Compaction Fidelity Decay Experiment")
    parser.add_argument("--pilot", action="store_true", default=True, help="Run pilot (50 calls)")
    parser.add_argument("--full", action="store_true", help="Run full experiment (600 calls)")
    parser.add_argument("--output", type=str, default=None, help="Output JSON path")
    parser.add_argument("--resume", type=str, default=None, help="Resume from partial results file")
    parser.add_argument("--dry-run", action="store_true", help="Print design without running")
    args = parser.parse_args()

    if args.dry_run:
        print(f"Instructions: {len(INSTRUCTIONS)}")
        print(f"Levels: {LEVELS}")
        print(f"Reps: {REPS}")
        print(f"Total calls: {len(INSTRUCTIONS) * len(LEVELS) * REPS}")
        print(f"Model: {MODEL}")
        print(f"API URL: {API_URL}")
        design = {
            "instructions": [{"id": i["id"], "category": i["category"], "rule": i["rule"]} for i in INSTRUCTIONS],
            "levels": LEVELS, "reps": REPS, "model": MODEL,
        }
        print(f"SHA256: {hash_design(design)}")
        return

    if not API_KEY:
        print("ERROR: DEEPSEEK_API_KEY not set")
        sys.exit(1)

    # Auto-save path: save incrementally so crashes don't lose everything
    auto_save = args.output or f"compact_decay_pilot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    results = run_pilot(resume_path=args.resume, auto_save_path=auto_save)
    print_summary(results["summary"])

    print(f"\nResults saved to: {auto_save}")

    if results["errors"]:
        print(f"WARNING: {len(results['errors'])} API errors")
        for e in results["errors"]:
            print(f"  Trial {e['trial_id']}: {e['error'][:80]}")

    return results


if __name__ == "__main__":
    main()
