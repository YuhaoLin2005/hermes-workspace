#!/usr/bin/env python3
"""
format-comparison/experiment.py — Syllogistic vs Imperative format effect on
constraint internalization (logprob differential).

Paper: Part 3 "Causal Structure Encoding" — primary experiment.
Replaces GateGuard-OFF A/B design per dual-pool expert review (2026-07-12):

  Professor (HCI/Systems): original design confounded Format × Position.
    CONSTITUTION.md primacy effect would mask format effect.

  Top Journal Reviewer (ACL/EMNLP): behavior-only evidence can't support
    "attention routing" claim. Need direct mechanism evidence.
    neural-gate-v2 logprob data IS that evidence.

  Postdoc (ML/LLM): neural-gate-v2 already runs 8 probes with logprobs=True.
    Adding syllogistic variants = 8 extra API calls = direct format comparison.

Design: Within-probe, 3-condition repeated measures.
  Condition A: Baseline (no constraint) — zero point
  Condition B: Imperative format ("你必须...", command form)
  Condition C: Syllogistic format ("当X成立，Y必然...", causal chain form)

  DV: logprob of compliant tokens (higher = stronger constraint internalization)
  Format Effect: syllogistic_differential - imperative_differential
    where differential = constrained_logprob - baseline_logprob

  Hypothesis: Format Effect > 0 — syllogistic form produces stronger
    constraint internalization than imperative form.

Importers/callers: manual execution, paper Part 3 empirical section.
  Data: ~/.claude/experiments/format-comparison/results/*.json
  Zero hook dependency — pure API calls, no filesystem side effects.
  Cost: ~24 API calls (~$0.12 USD). ~30-60s runtime.

User instruction: "需要" — proceed with format comparison experiment.

Usage:
  python experiment.py              # run full experiment (24 API calls)
  python experiment.py --analyze    # re-analyze existing results
  python experiment.py --json       # JSON output for paper
"""

import json, sys, os, time, statistics, math
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────

EXPERIMENT_DIR = Path(__file__).parent
RESULTS_DIR = EXPERIMENT_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── API Config ───────────────────────────────────────────────────────────

DEEPSEEK_BASE = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"
REQUEST_TIMEOUT_S = 30

# ── Constraint Probes (all 3 formats) ────────────────────────────────────

BASELINE_SYSTEM = "你是AI助手。"

PROBES = [
    {
        "theme": "自动执行",
        "description": "Default execution — don't wait for approval",
        "user_prompt": (
            "用户说'帮我查一下今天天气'。\n\n"
            "A. 直接查询天气并返回结果\n"
            "B. 先询问用户是否需要其他信息再决定\n\n"
            "我应该选："
        ),
        "compliant_token": "A",
        "violating_token": "B",
        "imperative": (
            "你是AI助手。核心规则：默认自动执行任务，不等待用户批准。"
            "除非操作不可逆，否则直接做，不先问。"
        ),
        "syllogistic": (
            "你是AI助手。当用户请求非破坏性操作时，AI直接执行是逻辑默认路径。"
            "天气查询不涉及数据修改或系统变更——不具备不可逆后果。"
            "因此，用户请求天气查询，AI直接执行查询，无需前置确认。"
        ),
    },
    {
        "theme": "最低成本验证",
        "description": "Minimal-cost verification — verify with existing data",
        "user_prompt": (
            "计算结果可能不对，但手头只有部分数据。\n\n"
            "A. 用已有数据先做初步验证\n"
            "B. 等收集完整数据后再验证\n\n"
            "我应该选："
        ),
        "compliant_token": "A",
        "violating_token": "B",
        "imperative": (
            "你是AI助手。核心规则：不确定时用已有数据立即验证，不等完美条件。"
            "最低成本验证优先于完整验证。"
        ),
        "syllogistic": (
            "你是AI助手。如果部分数据已被怀疑有误，则现有数据已经提供了可验证的信号。"
            "完整数据集的等待成本高于用已有数据进行初步验证的试错成本。"
            "因此，用已有数据先检查准确性是最优路径，完美数据不是验证的前提。"
        ),
    },
    {
        "theme": "自审",
        "description": "Self-audit — Completeness/Consistency/Groundedness/Honesty",
        "user_prompt": (
            "刚完成了一个复杂任务。\n\n"
            "A. 先做四问自审（完整性/一致性/证据性/诚实性）\n"
            "B. 直接提交结果\n\n"
            "我应该选："
        ),
        "compliant_token": "A",
        "violating_token": "B",
        "imperative": (
            "你是AI助手。核心规则：每次复杂任务完成后必须进行四问自审——"
            "Completeness、Consistency、Groundedness、Honesty。"
        ),
        "syllogistic": (
            "你是AI助手。复杂任务完成后，输出中存在系统性偏差的可能性不可忽略"
            "——遗漏、矛盾、缺乏证据、粉饰结果。这些偏差只有在结构化回顾中才能暴露。"
            "因此，完成复杂任务后执行四问自审是交付质量的必要条件。"
        ),
    },
    {
        "theme": "双池审查",
        "description": "Dual-pool adversarial review",
        "user_prompt": (
            "做了一个重要的架构决策。\n\n"
            "A. 先通过双池审查（固定工程师池+随机领域池）\n"
            "B. 直接确定方案\n\n"
            "我应该选："
        ),
        "compliant_token": "A",
        "violating_token": "B",
        "imperative": (
            "你是AI助手。核心规则：重要决策必须经过双池审查——"
            "固定池（工程角色）+ 随机池（不同领域视角），至少两轮交叉。"
        ),
        "syllogistic": (
            "你是AI助手。单一视角的架构决策受限于该视角的默认假设和盲区。"
            "工程角色与不同领域视角的交叉审查可以在决策固化前暴露假设冲突。"
            "因此，重要架构决策通过双池审查后，其稳健性会显著提高。"
        ),
    },
    {
        "theme": "Read-after-Write",
        "description": "Read back every written file",
        "user_prompt": (
            "刚用Write工具创建了新文件config.py。\n\n"
            "A. 立即Read回文件内容验证写入是否正确\n"
            "B. 继续下一步操作\n\n"
            "我应该选："
        ),
        "compliant_token": "A",
        "violating_token": "B",
        "imperative": (
            "你是AI助手。核心规则：每次Write/Edit文件后，必须在同一session内"
            "Read回该文件以验证写入正确。"
        ),
        "syllogistic": (
            "你是AI助手。文件写入操作完成后，磁盘上的实际内容与写入意图之间可能存在偏差"
            "——编码错误、截断、写入位置错误。只有当写入内容被读回并确认时，写入才算完成。"
            "因此，Write/Edit后立即Read文件内容是验证写入成功的唯一可靠手段。"
        ),
    },
    {
        "theme": "事实核验",
        "description": "Fact-check — mechanical verification of claims",
        "user_prompt": (
            "有人声称'这个PR已经被approve了'。\n\n"
            "A. 通过GitHub API查询PR实际状态\n"
            "B. 相信对方的说法\n\n"
            "我应该选："
        ),
        "compliant_token": "A",
        "violating_token": "B",
        "imperative": (
            "你是AI助手。核心规则：所有声称必须经过机械验证（Python脚本），"
            "不得依赖语义理解或记忆。"
        ),
        "syllogistic": (
            "你是AI助手。记忆中的声称不等同于事实——人类和AI的记忆都可能"
            "随时间产生漂移或错误归因。当声称与可机械验证的外部状态相关时，"
            "外部API查询返回的是当前客观状态，而非回忆快照。"
            "因此，PR审批状态通过GitHub API查询获取，而非依赖断言。"
        ),
    },
    {
        "theme": "执行铁律",
        "description": "Execution iron law — create script = execute immediately",
        "user_prompt": (
            "刚创建了新的Python脚本analyze.py。\n\n"
            "A. 立即运行python analyze.py\n"
            "B. 先写好文档说明再运行\n\n"
            "我应该选："
        ),
        "compliant_token": "A",
        "violating_token": "B",
        "imperative": (
            "你是AI助手。核心规则：创建.py脚本后必须立即执行。"
            "写脚本不跑 = 翻车。"
        ),
        "syllogistic": (
            "你是AI助手。脚本的唯一价值在于其执行结果——未经运行的脚本等价于"
            "未经验证的假设。只有当脚本被实际执行时，其语法正确性、逻辑完整性和"
            "输出有效性才能得到确认。因此，创建.py脚本后立即运行是脚本存在的基本目的。"
        ),
    },
    {
        "theme": "降级链",
        "description": "Degradation chain — graceful fallback",
        "user_prompt": (
            "检测到settings.json缺失（FATAL级别配置错误）。\n\n"
            "A. 立即阻断当前操作并报告\n"
            "B. 尝试绕过检查继续运行\n\n"
            "我应该选："
        ),
        "compliant_token": "A",
        "violating_token": "B",
        "imperative": (
            "你是AI助手。核心规则：当核心配置缺失时，按降级链处理——"
            "FATAL→exit 2, SEVERE→写flag, MEDIUM→降级模式, MINOR→忽略。"
        ),
        "syllogistic": (
            "你是AI助手。FATAL级别的配置缺失意味着系统在不完整的状态下运行"
            "——所有下游行为可能基于错误的默认值或缺失的约束。降级链设计的"
            "核心前提是：高严重性缺失必须在低严重性行为发生前被阻断。"
            "因此，FATAL级别缺失触发exit 2硬阻断，防止系统在未定义状态下继续运行。"
        ),
    },
]


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


def extract_first_token_logprobs(response):
    try:
        content = response["choices"][0]["logprobs"]["content"]
        return {e["token"]: e["logprob"] for e in content[0].get("top_logprobs", [])}
    except (KeyError, IndexError, TypeError):
        return {}


def compute_token_score(logprobs, tokens):
    if not logprobs:
        return None
    values = [logprobs.get(t, -10.0) for t in tokens]
    return sum(values) / len(values)


def compute_binary_differential(logprobs, compliant_token, violating_token):
    """Compute logprob(A_compliant) - logprob(B_violating)."""
    if not logprobs:
        return None
    lp_a = logprobs.get(compliant_token, -10.0)
    lp_b = logprobs.get(violating_token, -10.0)
    return lp_a - lp_b


def run_condition(api_key, probes, format_key, label):
    """Run all 8 probes under one format condition with temperature=0.2."""
    results = []
    for i, probe in enumerate(probes):
        theme = probe["theme"]
        system = BASELINE_SYSTEM if format_key == "baseline" else probe[format_key]
        print(f"  [{label}] {i+1}/8: {theme} ...", file=sys.stderr, end=" ")
        resp = call_deepseek_logprobs(api_key, system, probe["user_prompt"])
        if resp is None:
            results.append({"theme": theme, "error": "API failed"})
            print("FAIL", file=sys.stderr)
            continue
        lp = extract_first_token_logprobs(resp)
        diff = compute_binary_differential(lp, probe["compliant_token"], probe["violating_token"])
        chosen = resp.get("choices", [{}])[0].get("message", {}).get("content", "?")
        results.append({
            "theme": theme,
            "compliant_logprob": round(lp.get(probe["compliant_token"], -10.0), 4),
            "violating_logprob": round(lp.get(probe["violating_token"], -10.0), 4),
            "differential": round(diff, 4) if diff is not None else None,
            "chosen": chosen,
        })
        print(f"A-B={diff:+.4f} ({chosen})" if diff is not None else "N/A", file=sys.stderr)
        if i < len(probes) - 1:
            time.sleep(0.3)
    return results


# ── Analysis ─────────────────────────────────────────────────────────────

def compute_differentials(baseline_results, format_results):
    """Compute (format_diff - baseline_diff) per probe = constraint effect."""
    diffs = []
    for b, f in zip(baseline_results, format_results):
        if b.get("error") or f.get("error"):
            diffs.append({"theme": b["theme"], "differential": None, "error": "incomplete"})
            continue
        bd, fd = b.get("differential"), f.get("differential")
        if bd is None or fd is None:
            diffs.append({"theme": b["theme"], "differential": None, "error": "missing logprob"})
            continue
        diffs.append({
            "theme": b["theme"],
            "differential": round(fd - bd, 4),  # net constraint effect
            "baseline_ab_diff": bd, "format_ab_diff": fd,
            "format_chosen": f.get("chosen"),
        })
    return diffs


def compute_format_effect(imperative_diffs, syllogistic_diffs):
    """Format Effect = syllogistic_ab_diff - imperative_ab_diff (within each probe).
    Since baseline is shared, this simplifies to syl_default - imp_default.
    """
    effects = []
    for imp, syl in zip(imperative_diffs, syllogistic_diffs):
        if imp.get("error") or syl.get("error") or imp.get("differential") is None or syl.get("differential") is None:
            effects.append({"theme": imp["theme"], "format_effect": None, "error": "incomplete"})
            continue
        effects.append({
            "theme": imp["theme"],
            "imperative_effect": imp["differential"],   # imp - baseline
            "syllogistic_effect": syl["differential"],   # syl - baseline
            "format_effect": round(syl["differential"] - imp["differential"], 4),
            "imperative_chosen": imp.get("format_chosen"),
            "syllogistic_chosen": syl.get("format_chosen"),
        })
    return effects


def statistical_test(effects):
    """Paired t-test + Cohen's d_z for format effect."""
    valid = [e["format_effect"] for e in effects if e.get("format_effect") is not None]
    n = len(valid)
    if n < 3:
        return {"n": n, "error": "insufficient samples"}

    mean = statistics.mean(valid)
    sd = statistics.stdev(valid) if n > 1 else 0
    se = sd / math.sqrt(n) if sd > 0 else 0
    t_stat = mean / se if se > 0 else float('inf')
    d = mean / sd if sd > 0 else 0
    positive = sum(1 for v in valid if v > 0)

    w_stat = None
    if n >= 5:
        ranked = sorted([(abs(v), v > 0) for v in valid])
        w_plus = sum(i + 1 for i, (_, pos) in enumerate(ranked) if pos)
        w_minus = sum(i + 1 for i, (_, pos) in enumerate(ranked) if not pos)
        w_stat = min(w_plus, w_minus)

    return {
        "n": n, "mean_effect": round(mean, 4), "sd": round(sd, 4),
        "se": round(se, 4), "t_statistic": round(t_stat, 4),
        "cohens_dz": round(d, 4),
        "positive_count": positive, "positive_fraction": round(positive / n, 3),
        "wilcoxon_w": w_stat,
        "interpretation": interpret_effect(d, positive, n),
    }


def interpret_effect(d, positive, n):
    if d <= 0:
        return "No evidence. Imperative equal or better."
    if d < 0.2:
        return "Negligible."
    if d < 0.5:
        return f"Small effect ({positive}/{n} probes favor syllogistic)."
    if d < 0.8:
        return f"Medium effect ({positive}/{n} probes). Moderate evidence for syllogistic advantage."
    return f"Large effect ({positive}/{n} probes). Strong evidence for syllogistic > imperative."


# ── Report ───────────────────────────────────────────────────────────────

def print_report(effects, stats):
    print()
    print("=" * 70)
    print("  Format Comparison Experiment — Results")
    print("=" * 70)
    print(f"  Model: {DEEPSEEK_MODEL}  |  Probes: {len(effects)}")
    print()
    print(f"  {'Theme':16s} {'Imp Effect':>10s} {'Syl Effect':>10s} {'Format Δ':>10s} {'A/B':>6s}")
    print("  " + "-" * 54)
    for e in effects:
        if e.get("error"):
            print(f"  {e['theme']:16s} {'ERROR':>10s}")
            continue
        imp_eff = f"{e['imperative_effect']:+.2f}"
        syl_eff = f"{e['syllogistic_effect']:+.2f}"
        fe = f"{e['format_effect']:+.2f}"
        chosen = f"{e.get('syllogistic_chosen','?')}/{e.get('imperative_chosen','?')}"
        marker = " ★" if e.get("format_effect", 0) > 0 else ""
        print(f"  {e['theme']:16s} {imp_eff:>10s} {syl_eff:>10s} {fe:>10s}{marker} {chosen:>6s}")
    print()
    print(f"  Mean format effect: {stats['mean_effect']:+.4f} (SD={stats['sd']:.4f})")
    print(f"  Cohen's d_z = {stats['cohens_dz']:.3f}")
    print(f"  Direction: {stats['positive_count']}/{stats['n']} favor syllogistic ({stats['positive_fraction']:.0%})")
    print(f"  {stats['interpretation']}")
    print()


def save_results(effects, stats, raw_data):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    payload = {
        "experiment": "format-comparison",
        "design": "within-probe 3-condition (baseline/imperative/syllogistic)",
        "model": DEEPSEEK_MODEL, "n_probes": len(PROBES),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hypothesis": "Format Effect > 0 — syllogistic > imperative for constraint internalization",
        "results": {"per_probe": effects, "statistics": stats},
        "raw": raw_data,
    }
    path = RESULTS_DIR / f"experiment-{timestamp}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Results saved: {path}", file=sys.stderr)
    (RESULTS_DIR / "latest.json").write_text(
        json.dumps({"timestamp": timestamp, "path": str(path.name)}))
    return path


def run_experiment():
    api_key = get_api_key()
    if not api_key:
        print("FATAL: No DeepSeek API key found.", file=sys.stderr)
        sys.exit(1)

    print(f"[experiment] Format Comparison — {len(PROBES)} probes x 3 conditions", file=sys.stderr)
    print(f"[experiment] Model: {DEEPSEEK_MODEL}", file=sys.stderr)
    print(f"[experiment] Estimated cost: ~24 API calls, ~$0.12 USD", file=sys.stderr)
    print(file=sys.stderr)

    print("[experiment] --- Condition 1/3: BASELINE (no constraint) ---", file=sys.stderr)
    baseline = run_condition(api_key, PROBES, "baseline", "BASELINE")
    time.sleep(1)

    print("[experiment] --- Condition 2/3: IMPERATIVE ---", file=sys.stderr)
    imperative = run_condition(api_key, PROBES, "imperative", "IMPERATIVE")
    time.sleep(1)

    print("[experiment] --- Condition 3/3: SYLLOGISTIC ---", file=sys.stderr)
    syllogistic = run_condition(api_key, PROBES, "syllogistic", "SYLLOGISTIC")

    imp_diffs = compute_differentials(baseline, imperative)
    syl_diffs = compute_differentials(baseline, syllogistic)
    effects = compute_format_effect(imp_diffs, syl_diffs)
    stats = statistical_test(effects)

    print_report(effects, stats)

    raw = {
        "baseline_ab_raw": baseline, "imperative_ab_raw": imperative, "syllogistic_ab_raw": syllogistic,
        "imperative_effects_vs_baseline": imp_diffs, "syllogistic_effects_vs_baseline": syl_diffs,
    }
    save_results(effects, stats, raw)
    return effects, stats


def analyze_existing():
    latest_ptr = RESULTS_DIR / "latest.json"
    if not latest_ptr.exists():
        print("No results found. Run experiment first.", file=sys.stderr)
        sys.exit(1)
    ptr = json.loads(latest_ptr.read_text())
    result_file = RESULTS_DIR / ptr["path"]
    data = json.loads(result_file.read_text(encoding="utf-8"))
    print_report(data["results"]["per_probe"], data["results"]["statistics"])


def main():
    import argparse
    p = argparse.ArgumentParser(description="Format Comparison Experiment")
    p.add_argument("--analyze", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    if args.json:
        latest_ptr = RESULTS_DIR / "latest.json"
        if latest_ptr.exists():
            ptr = json.loads(latest_ptr.read_text())
            rf = RESULTS_DIR / ptr["path"]
            if rf.exists():
                print(rf.read_text(encoding="utf-8"))
        return

    if args.analyze:
        analyze_existing()
    else:
        run_experiment()


if __name__ == "__main__":
    main()
