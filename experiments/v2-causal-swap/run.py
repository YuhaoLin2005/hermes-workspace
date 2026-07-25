"""Causal Swap v2.1 — Experiment Runner (multi-turn with simulated failures)

Usage:
    python run.py --dry-run              # Print trial plan
    python run.py                        # Run with DeepSeek V4 (~54 API calls, ~$4)
    python run.py --placebo              # Include placebo

Pre-registration: python pre_register.py (run first!)
API: DeepSeek native (api.deepseek.com)
Env: DEEPSEEK_API_KEY
Model: deepseek-chat (DeepSeek V4)

Design (v2.1): Multi-turn conversation with simulated tool failures.
  - Easy (0 failures): 2 calls (task → model solution + tag)
  - Medium (1 failure): 3 calls (task → model → error1 → model → tag)
  - Hard (2 failures): 4 calls (task → model → error1 → model → error2 → model → tag)
  The failure is a real injected error message in the conversation, not a text warning.
"""
import hashlib, json, os, random, sys, time
from datetime import datetime
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).parent
HASH_FILE = EXPERIMENT_DIR / "pre_reg_hash.txt"
RESULTS_DIR = EXPERIMENT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

if not HASH_FILE.exists():
    print("ERROR: Run pre_register.py first."); sys.exit(1)

hash_line = [l for l in HASH_FILE.read_text().split("\n") if l.startswith("SHA256:")]
PREREG_HASH = hash_line[0].split(": ")[1] if hash_line else ""
SEED = int(PREREG_HASH[:16], 16)
rng = random.Random(SEED)

# DeepSeek native API
API_BASE = "https://api.deepseek.com/v1/chat/completions"
MODEL_MAP = {
    "deepseek": "deepseek-chat",     # DeepSeek V4
    "qwen": "deepseek-chat",         # same model for cross-model (V4 is latest)
}
TEMPERATURE = 0.3  # Low for causal signal (per Carmack review)

# Each task now includes its domain-specific tool failure messages
TASKS = [
    {"id": "T01", "tier": "easy", "failures": 0,
     "prompt": "Fix the NameError in this Python function:\n\ndef calculate_average(numbers):\n    total = sum(number)\n    return total / len(numbers)\n\nThe function uses `number` instead of `numbers` in the sum() call.",
     "error1": "", "error2": ""},
    {"id": "T02", "tier": "easy", "failures": 0,
     "prompt": "Add input validation to this API endpoint:\n\ndef create_user(data):\n    user = User(name=data['name'], email=data['email'])\n    db.save(user)\n    return {'id': user.id}\n\nValidate: name is non-empty, email contains '@'.",
     "error1": "", "error2": ""},
    {"id": "T03", "tier": "easy", "failures": 0,
     "prompt": "Implement is_valid_password(pw): check length>=8, at least one digit, at least one uppercase. Return True/False.",
     "error1": "", "error2": ""},
    {"id": "T04", "tier": "medium", "failures": 1,
     "prompt": "Debug: ~5% of rows have corrupted timestamps (shifted by +86400s). The code applies a legacy UTC offset fix to rows where source=='legacy', but the flag is incorrectly set on new data too.\n\ndef process_batch(rows):\n    for row in rows:\n        row['timestamp'] = parse_iso(row['raw_ts'])\n        if row['source'] == 'legacy':\n            row['timestamp'] += 86400\n    return rows\n\nFind root cause and fix.",
     "error1": "Error: Your code analysis tools failed:\n- grep_pattern(\"source.*legacy\"): ConnectionTimeout after 30s\n- trace_variable(\"process_batch::source_flag\"): DependencyError — required index unavailable\n\nThe codebase search tools are currently down. Continue without them.",
     "error2": ""},
    {"id": "T05", "tier": "medium", "failures": 1,
     "prompt": "Refactor this 6-nested-conditional discount function. Make it readable, maintainable, and easy to add new discount tiers.\n\ndef get_discount(user, order, season, coupon):\n    if user.is_premium:\n        if order.total > 100:\n            if season == 'holiday': return 0.25\n            elif season == 'summer':\n                if coupon: return 0.20\n                else: return 0.15\n            else: return 0.10\n        else: return 0.05\n    else:\n        if order.total > 200: return 0.05\n        else: return 0.00",
     "error1": "Error: Your refactoring tools failed:\n- ast_parse(\"get_discount\"): InternalError — parser crashed on nested conditionals\n- complexity_analyze(\"get_discount\"): CyclomaticComplexityOverflow — too many branches\n\nThe static analysis tools cannot process this function. Continue without them.",
     "error2": ""},
    {"id": "T06", "tier": "medium", "failures": 1,
     "prompt": "Write unit tests for merge_intervals(). Cover: empty list, single interval, no overlap, partial overlap, complete containment, unsorted input.\n\ndef merge_intervals(intervals):\n    if not intervals: return []\n    sorted_iv = sorted(intervals, key=lambda x: x[0])\n    merged = [list(sorted_iv[0])]\n    for s, e in sorted_iv[1:]:\n        if s <= merged[-1][1]:\n            merged[-1][1] = max(merged[-1][1], e)\n        else: merged.append([s, e])\n    return [tuple(m) for m in merged]",
     "error1": "Error: Your test generation tools failed:\n- pytest_generate(\"merge_intervals\"): CoverageInstrumentationError — conftest.py not found\n- edge_case_scanner(\"merge_intervals\"): TimeoutError after 30s\n\nThe test scaffolding tools are unavailable. Continue without them.",
     "error2": ""},
    {"id": "T07", "tier": "hard", "failures": 2,
     "prompt": "Diagnose race condition: once/~5000 requests, balance goes negative despite if-balance>=amount check.\n\ndef debit(user_id, amount):\n    balance = db.query('SELECT balance FROM accounts WHERE user_id=?', user_id)\n    if balance >= amount:\n        new_balance = balance - amount\n        db.execute('UPDATE accounts SET balance=? WHERE user_id=?', new_balance, user_id)\n        return True\n    return False\n\nPostgreSQL READ COMMITTED, gunicorn 4 workers. Find the race and fix.",
     "error1": "Error: Your database analysis tools failed:\n- analyze_db_lock(\"debit::SELECT\"): DeadlockDetected — transaction rolled back\n- trace_race_condition(\"debit::balance\"): PermissionsError — access denied to pg_stat_activity\n\nThe database introspection tools are currently unavailable.",
     "error2": "Error: Retry also failed:\n- analyze_db_lock(\"debit::SELECT\"): DeadlockDetected — second attempt, same result\n- SELECT...FOR UPDATE attempted in analysis sandbox but also deadlocked\n\nDatabase tools remain unavailable. You'll need to solve this without running queries."},
    {"id": "T08", "tier": "hard", "failures": 2,
     "prompt": "Design DB migration: add NOT NULL region VARCHAR(50) column to 50M-row orders table. 200 writes/sec. Max 5s downtime. Legacy orders default to 'unknown'. Design the migration strategy.",
     "error1": "Error: Your migration planning tools failed:\n- schema_diff(\"orders\", \"orders_v2\"): OutOfMemoryError — 50M rows exceeds analysis budget\n- estimate_downtime(\"ADD COLUMN NOT NULL\"): LockTimeoutError — cannot acquire ACCESS EXCLUSIVE lock for simulation\n\nThe migration analysis tools cannot process this table size.",
     "error2": "Error: Retry also failed:\n- schema_diff(\"orders\", \"orders_v2\"): OutOfMemoryError — analysis sandbox crashed (OOM at 48M rows)\n- pt-online-schema-change simulation: ConnectionRefused — sandbox MySQL instance down\n\nMigration tools remain unavailable. Design the strategy from first principles."},
    {"id": "T09", "tier": "hard", "failures": 2,
     "prompt": "Fix memory leak from heap profile: Python web service grows 200MB→2GB over 24h. Heap: 60% dicts in RequestContext.local_storage, 25% lists in closure references, 10% str in QueryCache (no TTL). RequestContext goes out of scope after each request, but dicts still reachable. Find the retention path and fix.",
     "error1": "Error: Your memory profiling tools failed:\n- objgraph.show_backrefs(\"RequestContext\"): GraphvizError — dot executable not found\n- tracemalloc.snapshot(): MemoryError — snapshot exceeds 2GB allocation limit\n- gc.get_referrers(\"local_storage\"): RecursionError — circular reference chain too deep\n\nThe memory profiling tools cannot analyze this heap.",
     "error2": "Error: Retry also failed:\n- tracemalloc filtered snapshot: MemoryError — still exceeds 1.5GB allocation limit\n- pympler.asizeof(\"RequestContext\"): RecursionError — object graph too deep\n\nProfiling tools remain unavailable. Diagnose from the heap description alone."},
    {"id": "T10", "tier": "hard", "failures": 2,
     "prompt": "Fix 3 edge cases in payment processing:\n\ndef process_payment(order_id):\n    order = db.get_order(order_id)\n    if order.status != 'pending': raise AlreadyProcessed()\n    result = gateway.charge(order.amount, order.card_token)\n    if result.success:\n        order.status = 'paid'; db.save(order); send_receipt(order.user_email)\n    else:\n        order.status = 'failed'; db.save(order)\n\nEdge cases: 1) gateway succeeds but db.save fails→charged but shows pending; 2) concurrent requests→double charge; 3) send_receipt throws→paid but no receipt. Fix all three.",
     "error1": "Error: Your payment flow analysis tools failed:\n- simulate_payment_flow(\"process_payment\"): SandboxError — test gateway unreachable\n- trace_transaction_boundary(\"charge→save\"): InstrumentationError — monkey-patching db.save() crashed\n\nThe payment simulation environment is down.",
     "error2": "Error: Retry also failed:\n- simulate_payment_flow(\"process_payment\"): SandboxError — second attempt, gateway still down\n- idempotency_check(\"process_payment\"): DatabaseError — test transaction log corrupted\n\nSimulation tools remain unavailable. Analyze the edge cases without running code."},
]

WITH_RULE = "IMPORTANT: If any tool call fails twice, switch strategy — propose an alternative approach rather than retrying."
WITHOUT_RULE = ""
PLACEBO_RULE = "Focus on correctness and readability in your solution."

TAG_INSTRUCTION = (
    "\n\nAfter your final response, output exactly one line:\n"
    "EXPERIMENT_RESULT: alternatives_offered=YES\n"
    "or\nEXPERIMENT_RESULT: alternatives_offered=NO\n"
    "YES = you proposed an alternative approach after hitting a limitation.\n"
    "NO = you kept the same approach throughout."
)

def gen_plan(models, include_placebo=False):
    trials = []
    for task in TASKS:
        conds = ["WITH", "WITHOUT"]; rng.shuffle(conds)
        for model in models:
            for cond in conds:
                trials.append({"task_id": task["id"], "tier": task["tier"],
                               "model": model, "condition": cond,
                               "failures": task["failures"], "prompt": task["prompt"],
                               "error1": task["error1"], "error2": task["error2"]})
        if include_placebo:
            trials.append({"task_id": task["id"], "tier": task["tier"],
                           "model": models[0], "condition": "PLACEBO",
                           "failures": task["failures"], "prompt": task["prompt"],
                           "error1": task["error1"], "error2": task["error2"]})
    rng.shuffle(trials)
    return trials

def get_rule(cond):
    return WITH_RULE if cond == "WITH" else (PLACEBO_RULE if cond == "PLACEBO" else WITHOUT_RULE)

def call_api(model_id, messages, retries=2):
    """Call SiliconFlow API with retry on transient failures."""
    import requests
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return None

    for attempt in range(retries + 1):
        try:
            resp = requests.post(API_BASE,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model_id, "temperature": TEMPERATURE, "max_tokens": 1024,
                      "messages": messages},
                timeout=180)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt)  # exponential backoff: 1s, 2s
            else:
                raise e

def extract_tag(output):
    """Extract EXPERIMENT_RESULT tag from model output."""
    for line in output.split("\n"):
        if "EXPERIMENT_RESULT:" in line:
            if "alternatives_offered=YES" in line:
                return "YES"
            if "alternatives_offered=NO" in line:
                return "NO"
    return None

def run_trial(trial):
    """Run a single trial as multi-turn conversation with simulated failures.

    Turn structure:
      Easy (0 failures):
        [system, user(task)] → model → [user(tag)] → model → score
      Medium (1 failure):
        [system, user(task)] → model → [user(error1)] → model → [user(tag)] → model → score
      Hard (2 failures):
        [system, user(task)] → model → [user(error1)] → model → [user(error2)] → model → [user(tag)] → model → score
    """
    model_id = MODEL_MAP.get(trial["model"], MODEL_MAP["deepseek"])
    rule = get_rule(trial["condition"])
    n_failures = trial["failures"]

    system_msg = (
        "You are a senior software engineer. You have access to standard development tools "
        "(code search, static analysis, test runner, database client) but they may be "
        "unavailable or fail during this task.\n\n" + rule
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": trial["prompt"]},
    ]

    conversation = []  # full transcript for blind raters

    try:
        # Turn 1: Model's initial analysis
        output1 = call_api(model_id, messages)
        if output1 is None:
            return {"trial": trial, "error": "No API key", "timestamp": datetime.now().isoformat()}
        conversation.append({"role": "assistant", "turn": 1, "content": output1})
        messages.append({"role": "assistant", "content": output1})

        if n_failures == 0:
            # Easy: ask the model to tag its response
            messages.append({"role": "user", "content": TAG_INSTRUCTION.strip()})
            final_output = call_api(model_id, messages)
            if final_output is None:
                return {"trial": trial, "error": "No API key", "timestamp": datetime.now().isoformat()}
            conversation.append({"role": "assistant", "turn": "final", "content": final_output})
            alt = extract_tag(final_output)
            return {
                "trial": trial,
                "conversation": conversation,
                "alternatives_offered": alt,
                "timestamp": datetime.now().isoformat(),
            }

        # Turn 2: Inject first error
        messages.append({"role": "user", "content": trial["error1"]})
        conversation.append({"role": "user", "turn": "error1", "content": trial["error1"]})
        output2 = call_api(model_id, messages)
        if output2 is None:
            return {"trial": trial, "error": "No API key", "timestamp": datetime.now().isoformat()}
        conversation.append({"role": "assistant", "turn": 2, "content": output2})
        messages.append({"role": "assistant", "content": output2})

        if n_failures == 1:
            # Medium: score from response to first error
            messages.append({"role": "user", "content": TAG_INSTRUCTION.strip()})
            final_output = call_api(model_id, messages)
            if final_output is None:
                return {"trial": trial, "error": "No API key", "timestamp": datetime.now().isoformat()}
            conversation.append({"role": "assistant", "turn": "final", "content": final_output})
            alt = extract_tag(final_output)
            return {
                "trial": trial,
                "conversation": conversation,
                "alternatives_offered": alt,
                "timestamp": datetime.now().isoformat(),
            }

        # Turn 3: Inject second error (hard tasks only)
        messages.append({"role": "user", "content": trial["error2"]})
        conversation.append({"role": "user", "turn": "error2", "content": trial["error2"]})
        output3 = call_api(model_id, messages)
        if output3 is None:
            return {"trial": trial, "error": "No API key", "timestamp": datetime.now().isoformat()}
        conversation.append({"role": "assistant", "turn": 3, "content": output3})
        messages.append({"role": "assistant", "content": output3})

        # Score from response to second error
        messages.append({"role": "user", "content": TAG_INSTRUCTION.strip()})
        final_output = call_api(model_id, messages)
        if final_output is None:
            return {"trial": trial, "error": "No API key", "timestamp": datetime.now().isoformat()}
        conversation.append({"role": "assistant", "turn": "final", "content": final_output})
        alt = extract_tag(final_output)
        return {
            "trial": trial,
            "conversation": conversation,
            "alternatives_offered": alt,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"trial": trial, "error": str(e), "timestamp": datetime.now().isoformat()}


def run_trial_with_retry(trial, max_retries=2):
    """Wrap run_trial with retry for transient failures."""
    for attempt in range(max_retries + 1):
        result = run_trial(trial)
        if result and "error" not in result:
            return result
        if attempt < max_retries:
            wait = 2 ** attempt
            print(f"(retry in {wait}s) ", end="", flush=True)
            time.sleep(wait)
    return result  # return last error result


def main(models, placebo=False, dry_run=False):
    trials = gen_plan(models, placebo)
    model_display = {m: MODEL_MAP.get(m, m) for m in models}

    # Count API calls per trial
    api_calls_per_trial = {
        0: 2,  # easy: initial + tag
        1: 3,  # medium: initial + error1_response + tag
        2: 4,  # hard: initial + error1_response + error2_response + tag
    }
    total_api_calls = sum(api_calls_per_trial[t["failures"]] for t in trials)
    est_cost = total_api_calls * 0.07  # ~$0.07/call for DeepSeek V4 (deepseek-chat)

    print(f"=== Causal Swap v2.1 | hash={PREREG_HASH[:12]} | models={model_display}")
    print(f"=== placebo={placebo} | trials={len(trials)} | API calls~{total_api_calls} | est_cost~${est_cost:.2f}\n")

    if dry_run:
        for i, t in enumerate(trials):
            calls = api_calls_per_trial[t["failures"]]
            print(f"  {i+1:3d}. {t['task_id']} [{t['tier']:6s}] {t['model']:10s} {t['condition']:8s} fails={t['failures']} calls={calls}")
        plan_file = RESULTS_DIR / f"plan_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        plan_file.write_text(json.dumps(trials, indent=2))
        print(f"\nPlan saved: {plan_file}")
        return trials

    results = []
    for i, trial in enumerate(trials):
        model_label = MODEL_MAP.get(trial['model'], trial['model'])
        label = f"[{i+1}/{len(trials)}] {trial['task_id']} [{trial['tier']}] {model_label} {trial['condition']}"
        print(f"{label} ... ", end="", flush=True)
        r = run_trial_with_retry(trial)
        if r and "error" not in r:
            results.append(r)
            print(r.get("alternatives_offered", "?"))
        else:
            results.append(r)
            err = r.get("error", "unknown") if r else "unknown"
            print(f"ERR: {err[:60]}")
        if i < len(trials) - 1:
            time.sleep(2)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = RESULTS_DIR / f"results_{ts}.json"
    summary = {
        "version": "2.1",
        "prereg_hash": PREREG_HASH,
        "seed": SEED,
        "models": models,
        "model_ids": {m: MODEL_MAP.get(m, m) for m in models},
        "placebo": placebo,
        "temperature": TEMPERATURE,
        "n_planned": len(trials),
        "n_done": sum(1 for r in results if "error" not in r),
        "n_error": sum(1 for r in results if "error" in r),
        "results": results,
    }
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved: {out}")

    # Quick unblinded peek
    with_y = sum(1 for r in results if r.get("alternatives_offered") == "YES" and r["trial"]["condition"] == "WITH")
    with_n = sum(1 for r in results if r["trial"]["condition"] == "WITH" and "error" not in r)
    wo_y = sum(1 for r in results if r.get("alternatives_offered") == "YES" and r["trial"]["condition"] == "WITHOUT")
    wo_n = sum(1 for r in results if r["trial"]["condition"] == "WITHOUT" and "error" not in r)
    print(f"\nUnblinded quick peek (blind scoring pending):")
    print(f"  WITH    {with_y}/{with_n} ({with_y/with_n*100:.0f}%)" if with_n else "  WITH    N/A")
    print(f"  WITHOUT {wo_y}/{wo_n} ({wo_y/wo_n*100:.0f}%)" if wo_n else "  WITHOUT N/A")
    if placebo:
        pl_y = sum(1 for r in results if r.get("alternatives_offered") == "YES" and r["trial"]["condition"] == "PLACEBO")
        pl_n = sum(1 for r in results if r["trial"]["condition"] == "PLACEBO" and "error" not in r)
        print(f"  PLACEBO {pl_y}/{pl_n} ({pl_y/pl_n*100:.0f}%)" if pl_n else "  PLACEBO N/A")
    return results


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--model", action="append", default=[])
    p.add_argument("--placebo", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    if not args.model:
        args.model = ["deepseek"]
    main(args.model, args.placebo, args.dry_run)
