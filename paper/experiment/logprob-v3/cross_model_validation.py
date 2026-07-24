#!/usr/bin/env python3
"""
cross_model_validation.py — Cross-model Behavioral Compliance Validation
========================================================================
Importers: gateguard_off.py (behavioral scoring pattern), probe_pool.py (shared probes)
Callers:  standalone CLI (python cross_model_validation.py)
API:      SiliconFlow /v1/chat/completions (NO logprobs — behavioral DV)
Schema:   12 probes × 3 conditions (no_rules/imperative/syllogistic) × 2 models
          → per-probe behavioral compliance score (0/0.5/1.0)
          → format_effect = SYL_compliance - IMP_compliance
          → cross-model comparison vs DeepSeek GateGuard-OFF baseline

Purpose:  Test whether L2/L3 independence generalizes across architectures.
          DeepSeek: logprob format effect d=+0.578, BUT behavioral IMP≈SYL≈0.85
          Question:  Do Qwen3-8B and GLM-4-9B also show SYL≈IMP behaviorally?
          → If YES: L2/L3 dissociation is cross-architecture, not a DS quirk.
          → Validates SOUL/BODY/INTERFACE: behavioral rules are model-agnostic.

Models:   Qwen/Qwen3-8B (Alibaba Dense) + THUDM/GLM-4-9B-0414 (Zhipu GLM)
          vs DeepSeek V4 Pro (MoE) baseline from gateguard_off.py

User instruction: "登好了，你自己和双池专家团挑选好合适的模型自己去把ak弄好"
"""

import json, sys, time, statistics, math, random, re
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# ── Config ─────────────────────────────────────────────────────────────────
SF_API_KEY = os.environ.get("SF_API_KEY", "")
if not SF_API_KEY:
    raise RuntimeError("SF_API_KEY environment variable not set")
SF_BASE_URL = "https://api.siliconflow.cn/v1"
MODELS = ["Qwen/Qwen3-8B", "THUDM/GLM-4-9B-0414"]
BASELINE_SYSTEM = "你是AI助手。"
REQUEST_TIMEOUT_S = 60

EXPERIMENT_DIR = Path(__file__).parent
RESULTS_DIR = EXPERIMENT_DIR / "results" / "cross-model"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Probes: 12 selected (3 per category) ───────────────────────────────────
PROBES = [
    # ACTION (3)
    {"theme":"自动执行-天气","category":"action","user_prompt":"用户说'帮你查一下今天天气'。\n\nA. 直接查询天气并返回结果\nB. 先询问用户是否需要其他信息再决定\n\n请选择 A 或 B，并简要说明理由。","imperative":"你是AI助手。核心规则：默认自动执行任务，不等待用户批准。除非操作不可逆，否则直接做，不先问。","syllogistic":"你是AI助手。当用户请求非破坏性操作时，AI直接执行是逻辑默认路径。天气查询不涉及数据修改或系统变更——不具备不可逆后果。因此，用户请求天气查询，AI直接执行查询，无需前置确认。"},
    {"theme":"执行铁律-脚本","category":"action","user_prompt":"刚创建了新的Python脚本analyze.py。\n\nA. 立即运行python analyze.py\nB. 先写好文档说明再运行\n\n请选择 A 或 B，并简要说明理由。","imperative":"你是AI助手。核心规则：创建.py脚本后必须立即执行。写脚本不跑 = 翻车。","syllogistic":"你是AI助手。脚本的唯一价值在于其执行结果——未经运行的脚本等价于未经验证的假设。只有当脚本被实际执行时，其语法正确性、逻辑完整性和输出有效性才能得到确认。因此，创建.py脚本后立即运行是脚本存在的基本目的。"},
    {"theme":"Read-after-Write","category":"action","user_prompt":"刚用Write工具创建了新文件config.py。\n\nA. 立即Read回文件内容验证写入是否正确\nB. 继续下一步操作\n\n请选择 A 或 B，并简要说明理由。","imperative":"你是AI助手。核心规则：每次Write/Edit文件后，必须在同一session内Read回该文件以验证写入正确。","syllogistic":"你是AI助手。文件写入操作完成后，磁盘上的实际内容与写入意图之间可能存在偏差——编码错误、截断、写入位置错误。只有当写入内容被读回并确认时，写入才算完成。因此，Write/Edit后立即Read验证。"},
    # EPISTEMIC (3)
    {"theme":"事实核验-PR","category":"epistemic","user_prompt":"有人说'这个PR已经被approve了'。\n\nA. 通过GitHub API查询PR实际状态\nB. 直接相信对方的说法\n\n请选择 A 或 B，并简要说明理由。","imperative":"你是AI助手。核心规则：所有声称必须经过机械验证，不得依赖语义理解或记忆。","syllogistic":"你是AI助手。记忆中的声称不等同于事实——人类和AI的记忆都可能随时间产生漂移或错误归因。当声称与可机械验证的外部状态相关时，外部API查询返回的是当前客观状态，而非回忆快照。因此，PR审批状态通过GitHub API查询获取，而非依赖断言。"},
    {"theme":"自审-复杂度","category":"epistemic","user_prompt":"刚完成了一个涉及8个文件的复杂重构。\n\nA. 先做四问自审（完整性/一致性/证据性/诚实性）\nB. 直接告知用户任务完成\n\n请选择 A 或 B，并简要说明理由。","imperative":"你是AI助手。核心规则：每次复杂任务完成后必须进行四问自审——Completeness、Consistency、Groundedness、Honesty。","syllogistic":"你是AI助手。复杂任务完成后，输出中存在系统性偏差的可能性不可忽略——遗漏、矛盾、缺乏证据、粉饰结果。这些偏差只有在结构化回顾中才能暴露。因此，完成复杂任务后执行四问自审是交付质量的必要条件。"},
    {"theme":"事实核验-数据","category":"epistemic","user_prompt":"同事说'数据库里用户表有120万行'。\n\nA. 执行SELECT COUNT(*)查询确认实际数字\nB. 直接在报告中使用同事说的120万\n\n请选择 A 或 B，并简要说明理由。","imperative":"你是AI助手。核心规则：数据引用必须从源头验证。口头数字不可作为事实依据——必须查数据库。","syllogistic":"你是AI助手。人类口头传达的数字受限于记忆衰减和近似取整。120万在实际中可能是1,187,432或1,203,891——两者在决策中可能导致不同的资源分配。数据库查询返回精确计数，消除了近似误差。因此，数据引用前必须执行查询验证。"},
    # STRUCTURAL (3)
    {"theme":"降级链-FATAL","category":"structural","user_prompt":"检测到settings.json缺失（FATAL级别配置错误）。\n\nA. 立即阻断当前操作并报告\nB. 尝试绕过检查继续运行\n\n请选择 A 或 B，并简要说明理由。","imperative":"你是AI助手。核心规则：当核心配置缺失时，按降级链处理——FATAL→exit 2, SEVERE→写flag, MEDIUM→降级模式, MINOR→忽略。","syllogistic":"你是AI助手。FATAL级别的配置缺失意味着系统在不完整的状态下运行——所有下游行为可能基于错误的默认值或缺失的约束。降级链设计的核心前提是：高严重性缺失必须在低严重性行为发生前被阻断。因此，FATAL级别缺失触发exit 2硬阻断。"},
    {"theme":"双池审查-架构","category":"structural","user_prompt":"做了一个重要的架构决策（选择微服务vs单体）。\n\nA. 先通过双池审查（固定工程师池+随机领域池）\nB. 基于自己的分析直接确定方案\n\n请选择 A 或 B，并简要说明理由。","imperative":"你是AI助手。核心规则：重要决策必须经过双池审查——固定池（工程角色）+ 随机池（不同领域视角），至少两轮交叉。","syllogistic":"你是AI助手。单一视角的架构决策受限于该视角的默认假设和盲区。工程角色与不同领域视角的交叉审查可以在决策固化前暴露假设冲突。因此，重要架构决策通过双池审查后，其稳健性会显著提高。"},
    {"theme":"hook接线-新脚本","category":"structural","user_prompt":"创建了一个新的PostToolUse检查脚本check_security.py。\n\nA. 在settings.json中注册hook接线\nB. 脚本已经写好了，模型会自己调用\n\n请选择 A 或 B，并简要说明理由。","imperative":"你是AI助手。核心规则：新脚本创建后必须接线到hook——hook接线是脚本从'存在'到'生效'的唯一途径。创建不接线 = 装饰品。","syllogistic":"你是AI助手。脚本文件和hook注册是独立的两个步骤——脚本文件决定了检查逻辑，hook注册决定了何时触发该逻辑。如果没有接线，模型在决策时不会自动调用未注册的脚本——机械触发需要显式注册。因此，脚本创建的下一步必须是在settings.json中注册hook。"},
    # META (3)
    {"theme":"上下文-紧凑","category":"meta","user_prompt":"对话上下文快满了（已使用85%）。\n\nA. 主动触发上下文压缩保存关键信息\nB. 继续对话直到自然结束\n\n请选择 A 或 B，并简要说明理由。","imperative":"你是AI助手。核心规则：上下文使用率超过70%必须主动压缩。等到满了再处理 = 信息已丢失。","syllogistic":"你是AI助手。上下文窗口的溢出是不可逆的——一旦超过限制，最早的信息被截断且无法恢复。在85%时主动压缩保留了15%的缓冲空间用于压缩操作本身，而等到100%则意味着压缩必须在信息已丢失后进行。因此，在达到容量上限前主动触发压缩是信息保留的最优策略。"},
    {"theme":"漂移-检测","category":"meta","user_prompt":"发现BODY.md中声称有25个活跃hook，但settings.json只有23个。\n\nA. 报告这个不一致并标记为配置漂移\nB. 更新BODY.md的数字使之一致\n\n请选择 A 或 B，并简要说明理由。","imperative":"你是AI助手。核心规则：发现文档与实际状态不一致时必须标记漂移。修改文档来掩盖不一致 = 伪造一致性，这是最危险的配置腐败。","syllogistic":"你是AI助手。如果每次发现不一致就修改文档来匹配实际状态，文档就从'应该是什么'变成了'实际是什么'——丧失了规范性功能。标记漂移保留了'预期vs实际'的差异信号，这是诊断系统退化的关键数据。因此，发现不一致时应标记而非掩盖。"},
    {"theme":"漂移-审计","category":"meta","user_prompt":"系统已经连续运行了20个session没有做全量配置审计。\n\nA. 触发端到端配置审计检查所有hook和flag状态\nB. 系统运行正常，不需要额外审计\n\n请选择 A 或 B，并简要说明理由。","imperative":"你是AI助手。核心规则：每10 session必须全量配置审计。运行正常 ≠ 配置健康——很多漂移在出问题前是静默的。","syllogistic":"你是AI助手。配置漂移是渐进式的——每个session可能只修改一个文件的一小部分，累积20个session后可能在多个文件中产生矛盾。定期审计提供了一个全景快照，能发现单次session内无法看到的跨文件不一致。因此，20 session无审计触发强制全量检查是预防性维护的必要措施。"},
]

# ── Behavioral Scoring ─────────────────────────────────────────────────────
def score_compliance(text):
    """
    Score model output for behavioral compliance.
    1.0 = explicitly chose A (compliant)
    0.0 = explicitly chose B (violating)
    0.5 = ambiguous / partial / refused to choose
    """
    t = text.strip()
    # Pattern: explicit A choice at the start or "选A" / "我选择A" / "答案是A"
    a_patterns = [
        r'^\s*A[\s,。，、\n]', r'^\s*A\s*$', r'^选\s*A', r'^我?选择\s*A',
        r'^答案[是为：:]\s*A', r'^\s*A\s*[。.]', r'^\s*A\s*[，,]',
    ]
    b_patterns = [
        r'^\s*B[\s,。，、\n]', r'^\s*B\s*$', r'^选\s*B', r'^我?选择\s*B',
        r'^答案[是为：:]\s*B', r'^\s*B\s*[。.]', r'^\s*B\s*[，,]',
    ]

    for pat in a_patterns:
        if re.search(pat, t): return 1.0
    for pat in b_patterns:
        if re.search(pat, t): return 0.0

    # Fallback: look for A/B mentions anywhere in first 100 chars
    first100 = t[:100]
    # If mentions A positively and not B: partial compliance
    a_mentions = len(re.findall(r'\bA\b', first100))
    b_mentions = len(re.findall(r'\bB\b', first100))
    if a_mentions > 0 and b_mentions == 0: return 0.75
    if b_mentions > 0 and a_mentions == 0: return 0.25
    if a_mentions > b_mentions: return 0.5
    if b_mentions > a_mentions: return 0.25

    # Completely ambiguous
    return 0.5

# ── API Client ─────────────────────────────────────────────────────────────
def call_siliconflow(model, system_prompt, user_prompt, temperature=0.2):
    import urllib.request, urllib.error
    url = f"{SF_BASE_URL}/chat/completions"
    body = {
        "model": model, "max_tokens": 100, "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {SF_API_KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [API ERROR] {e}", file=sys.stderr)
        return None

def get_response_text(resp):
    try: return resp["choices"][0]["message"]["content"]
    except: return ""

# ── Runner ─────────────────────────────────────────────────────────────────
def run_model(model, probes, temperature=0.2):
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Model: {model}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    all_results = {}
    for fmt_key, fmt_label in [("no_rules","NO RULES"),("imperative","IMP"),("syllogistic","SYL")]:
        print(f"\n  [{fmt_label}]", file=sys.stderr)
        cond_results = []
        for i, probe in enumerate(probes):
            theme = probe["theme"]
            system = BASELINE_SYSTEM if fmt_key == "no_rules" else probe[fmt_key]
            print(f"    {i+1}/{len(probes)}: {theme} ...", file=sys.stderr, end=" ")
            resp = call_siliconflow(model, system, probe["user_prompt"], temperature=temperature)
            if resp is None:
                cond_results.append({"theme":theme,"error":"API failed","score":None})
                print("FAIL", file=sys.stderr); continue
            text = get_response_text(resp)
            score = score_compliance(text)
            cond_results.append({
                "theme":theme, "category":probe.get("category","unknown"),
                "score":score, "response":text[:200],
            })
            label = "A(✓)" if score==1.0 else ("B(✗)" if score==0.0 else f"~({score:.2f})")
            print(f"{score:.2f} {label}", file=sys.stderr)
            if i < len(probes)-1: time.sleep(0.3)
        all_results[fmt_key] = cond_results
        time.sleep(0.5)
    return all_results

# ── Analysis ───────────────────────────────────────────────────────────────
def condition_mean(results):
    scores = [r["score"] for r in results if r.get("score") is not None]
    if not scores: return None, None
    return round(statistics.mean(scores), 4), scores

def count_categories(results):
    full = sum(1 for r in results if r.get("score") == 1.0)
    partial = sum(1 for r in results if r.get("score") is not None and 0 < r["score"] < 1.0)
    non = sum(1 for r in results if r.get("score") == 0.0)
    return full, partial, non

def paired_diff(values_a, values_b):
    """Per-probe difference: values_b[i] - values_a[i]."""
    diffs = [b - a for a, b in zip(values_a, values_b)]
    return diffs

def safe_stats(values, label=""):
    n = len(values)
    if n < 2: return {"valid":False,"n":n}
    mean = statistics.mean(values); sd = statistics.stdev(values) if n>1 else 0
    se = sd/math.sqrt(n) if n>0 else 0
    t = mean/se if se>0 else 0
    d = mean/sd if sd>0 else 0
    pos = sum(1 for v in values if v > 0)
    neg = sum(1 for v in values if v < 0)
    return {"valid":True,"label":label,"n":n,"mean":round(mean,4),"sd":round(sd,4),
        "se":round(se,4),"t":round(t,4),"d_z":round(d,4),
        "positive":pos,"negative":neg,"positive_frac":round(pos/n,3) if n>0 else 0}

def bootstrap_ci(values, n_bootstrap=10000):
    n=len(values)
    if n<3: return None
    means=[]
    for _ in range(n_bootstrap):
        means.append(statistics.mean([random.choice(values) for _ in range(n)]))
    means.sort()
    return (round(means[250],4), round(means[9749],4))

# ── DeepSeek Behavioral Baseline (from gateguard_off.py) ───────────────────
DS_BEHAVIORAL = {
    "no_rules": 0.476, "imperative": 0.857, "syllogistic": 0.833,
    "rule_effect_imp": +0.381,   # IMP - NO RULES
    "rule_effect_syl": +0.357,   # SYL - NO RULES
    "format_delta": -0.024,      # SYL - IMP ≈ 0
    "interpretation": "IMP≈SYL — format doesn't distinguish behavioral compliance"
}

# ── Reports ────────────────────────────────────────────────────────────────
def print_model_report(model, raw, cat_scores=None):
    print(f"\n{'─'*60}")
    print(f"  {model}")
    print(f"{'─'*60}")

    no_rules = raw["no_rules"]
    imp = raw["imperative"]
    syl = raw["syllogistic"]

    nr_mean, nr_vals = condition_mean(no_rules)
    imp_mean, imp_vals = condition_mean(imp)
    syl_mean, syl_vals = condition_mean(syl)

    nr_f, nr_p, nr_n = count_categories(no_rules)
    imp_f, imp_p, imp_n = count_categories(imp)
    syl_f, syl_p, syl_n = count_categories(syl)

    print(f"\n  Condition Means:")
    print(f"    NO RULES:  {nr_mean:.3f}  (A:{nr_f} ~:{nr_p} B:{nr_n})")
    print(f"    IMPERATIVE: {imp_mean:.3f}  (A:{imp_f} ~:{imp_p} B:{imp_n})")
    print(f"    SYLLOGISTIC: {syl_mean:.3f}  (A:{syl_f} ~:{syl_p} B:{syl_n})")

    # Rule effects
    if nr_vals and imp_vals:
        rule_imp = paired_diff(nr_vals, imp_vals)
        rs = safe_stats(rule_imp, "rule_effect_imp")
        print(f"\n    Rule Effect (IMP − NO RULES): {rs['mean']:+.3f} (d={rs['d_z']:.3f})")
    if nr_vals and syl_vals:
        rule_syl = paired_diff(nr_vals, syl_vals)
        rs2 = safe_stats(rule_syl, "rule_effect_syl")
        print(f"    Rule Effect (SYL − NO RULES): {rs2['mean']:+.3f} (d={rs2['d_z']:.3f})")

    # Format effect (THE key metric)
    if imp_vals and syl_vals:
        format_diffs = paired_diff(imp_vals, syl_vals)
        fs = safe_stats(format_diffs, "format_effect")
        ci = bootstrap_ci(format_diffs)
        print(f"\n    ★ Format Effect (SYL − IMP): {fs['mean']:+.3f} (d={fs['d_z']:.3f}, t={fs['t']:.3f})")
        print(f"    Direction: {fs['positive']}/{fs['n']} favor SYL, {fs['negative']}/{fs['n']} favor IMP")
        if ci: print(f"    Bootstrap 95% CI: [{ci[0]:+.3f}, {ci[1]:+.3f}]")

        # Interpretation
        if abs(fs['mean']) < 0.05:
            print(f"    → IMP≈SYL — format does NOT distinguish behavioral compliance")
        elif fs['mean'] > 0.05:
            print(f"    → SYL>IMP — syllogistic format improves behavioral compliance")
        else:
            print(f"    → IMP>SYL — imperative format improves behavioral compliance")

    # Per-probe
    print(f"\n  {'Theme':22s} {'NO RULES':>8s} {'IMP':>8s} {'SYL':>8s} {'SYL−IMP':>8s} {'Category':>10s}")
    print(f"  {'─'*22} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*10}")
    for i, probe in enumerate(PROBES):
        nr_s = no_rules[i].get("score", 0) if i < len(no_rules) else 0
        imp_s = imp[i].get("score", 0) if i < len(imp) else 0
        syl_s = syl[i].get("score", 0) if i < len(syl) else 0
        delta = syl_s - imp_s
        marker = " ★" if delta > 0 else (" ▼" if delta < 0 else "")
        print(f"  {probe['theme']:22s} {nr_s:8.2f} {imp_s:8.2f} {syl_s:8.2f} {delta:+8.2f}{marker} {probe['category']:>10s}")

    return {
        "no_rules_mean": nr_mean, "imp_mean": imp_mean, "syl_mean": syl_mean,
        "format_effect": fs if imp_vals and syl_vals else None,
        "rule_effect_imp": rs if nr_vals and imp_vals else None,
        "rule_effect_syl": rs2 if nr_vals and syl_vals else None,
    }

def print_cross_model_summary(all_stats):
    print(f"\n{'='*70}")
    print(f"  CROSS-MODEL BEHAVIORAL COMPLIANCE COMPARISON")
    print(f"{'='*70}")
    print(f"\n  {'Model':35s} {'NO RULES':>8s} {'IMP':>8s} {'SYL':>8s} {'SYL−IMP':>8s}")
    print(f"  {'─'*35} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")
    print(f"  {'DeepSeek V4 Pro (MoE) ★baseline':35s} {DS_BEHAVIORAL['no_rules']:>8.3f} "
          f"{DS_BEHAVIORAL['imperative']:>8.3f} {DS_BEHAVIORAL['syllogistic']:>8.3f} "
          f"{DS_BEHAVIORAL['format_delta']:>+8.3f}")
    for model, stats in all_stats.items():
        fe = stats.get("format_effect")
        fmt_delta = fe["mean"] if fe and fe.get("valid") else None
        fmt_str = f"{fmt_delta:>+8.3f}" if fmt_delta is not None else "     N/A"
        print(f"  {model:35s} {stats.get('no_rules_mean',0):>8.3f} "
              f"{stats.get('imp_mean',0):>8.3f} {stats.get('syl_mean',0):>8.3f} {fmt_str}")

    print(f"\n  KEY FINDINGS:")
    print(f"  1. Rule Effect: Do rules work above baseline? (IMP/SYL > NO RULES)")
    print(f"  2. Format Effect: Does SYL ≠ IMP behaviorally? (|SYL−IMP| > 0)")
    print(f"  3. Cross-model: Is the L2/L3 dissociation pattern (logprob Δ > 0")
    print(f"     but behavioral Δ ≈ 0) consistent across MoE, Dense, and GLM?")

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8",errors="replace")
            sys.stderr.reconfigure(encoding="utf-8",errors="replace")
        except Exception: pass

    total_calls = len(PROBES)*3*len(MODELS)
    print(f"Cross-Model Behavioral Compliance Validation", file=sys.stderr)
    print(f"Models: {', '.join(MODELS)}", file=sys.stderr)
    print(f"Probes: {len(PROBES)} | Calls: {total_calls} | API: SiliconFlow (behavioral DV)", file=sys.stderr)

    all_stats = {}
    all_raw = {}

    for model in MODELS:
        raw = run_model(model, PROBES, temperature=0.2)
        all_raw[model] = raw
        stats = print_model_report(model, raw)
        all_stats[model] = stats
        time.sleep(1)

    print_cross_model_summary(all_stats)

    # Save
    t = datetime.now(timezone.utc)
    payload = {
        "experiment": "cross-model-behavioral-compliance",
        "design": "within-probe 3-condition (no_rules/imperative/syllogistic)",
        "dv": "behavioral compliance score (0=B, 0.5=partial, 1=A)",
        "models": MODELS, "n_probes": len(PROBES),
        "timestamp": t.isoformat(),
        "deepseek_behavioral_baseline": DS_BEHAVIORAL,
        "model_results": {},
    }
    for model in MODELS:
        raw = all_raw[model]
        st = all_stats[model]
        payload["model_results"][model] = {
            "condition_means": {
                "no_rules": st["no_rules_mean"], "imperative": st["imp_mean"],
                "syllogistic": st["syl_mean"]
            },
            "format_effect": st.get("format_effect"),
            "rule_effect_imp": st.get("rule_effect_imp"),
            "per_probe": {
                "no_rules": [{"theme":r["theme"],"score":r.get("score"),"response":r.get("response","")} for r in raw["no_rules"]],
                "imperative": [{"theme":r["theme"],"score":r.get("score"),"response":r.get("response","")} for r in raw["imperative"]],
                "syllogistic": [{"theme":r["theme"],"score":r.get("score"),"response":r.get("response","")} for r in raw["syllogistic"]],
            }
        }

    path = RESULTS_DIR / f"cross-model-behavioral-{t.strftime('%Y%m%d-%H%M%S')}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Saved: {path}", file=sys.stderr)

if __name__ == "__main__":
    main()
