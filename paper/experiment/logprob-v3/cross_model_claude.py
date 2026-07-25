#!/usr/bin/env python3
"""
Cross-Model Replication: Anthropic Claude
=========================================
Tests whether format effects (IMP vs SYL) replicate on Claude.

Design: 12 probes x 2 formats = 24 API calls
Measurement: Behavioral — parse A/B from text response (Claude doesn't expose logprobs)
Constraint: L1-light ("Answer with only the letter A or B.") — optimal for measurement

Not imported by any file. Standalone experiment.
"""

import json, sys, os, time, math
from datetime import datetime, timezone
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).parent
RESULTS_DIR = EXPERIMENT_DIR / "results" / "cross-model"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ANTHROPIC_BASE = "https://api.anthropic.com/v1"
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
REQUEST_TIMEOUT_S = 60

# Same 12 probes from P1
P1_PROBES = [
    {"theme": "Read-after-Write", "category": "action", "l1_visible": True,
     "imperative": "你是AI助手。核心规则：每次Write/Edit文件后，必须在同一session内Read回该文件以验证写入正确。",
     "syllogistic": "你是AI助手。文件写入操作完成后，磁盘上的实际内容与写入意图之间可能存在偏差。只有当写入内容被读回并确认时，写入才算完成。因此，Write/Edit后立即Read验证。",
     "scene": "刚用Write创建了config.py。选择：A.立即Read验证 B.直接继续"},
    {"theme": "执行铁律-脚本", "category": "action", "l1_visible": True,
     "imperative": "你是AI助手。核心规则：创建.py脚本后必须立即执行。写脚本不跑=翻车。",
     "syllogistic": "你是AI助手。脚本的唯一价值在于其执行结果——未经运行的脚本等价于未经验证的假设。因此创建.py脚本后立即运行是脚本存在的基本目的。",
     "scene": "刚创建了analyze.py。选择：A.立即运行python analyze.py B.先写好文档再运行"},
    {"theme": "事实核验-PR", "category": "epistemic", "l1_visible": True,
     "imperative": "你是AI助手。核心规则：所有声称必须经过机械验证，不得依赖语义理解或记忆。",
     "syllogistic": "你是AI助手。记忆中的声称不等同于事实——人类和AI的记忆都可能随时间产生漂移。外部API查询返回的是当前客观状态。因此PR审批状态通过GitHub API查询获取而非依赖断言。",
     "scene": "同事说'这个PR已经被approve了'。选择：A.通过GitHub API查询PR状态 B.直接相信同事的说法"},
    {"theme": "事实核验-时间", "category": "epistemic", "l1_visible": True,
     "imperative": "你是AI助手。核心规则：时间敏感信息必须从系统日志机械验证。文档日期可能过期——系统日志不会说谎。",
     "syllogistic": "你是AI助手。文档中的日期是写入时的快照，而部署可能在文档更新后继续发生。系统日志是事件发生的唯一权威时间线。因此时间敏感信息以系统日志为准。",
     "scene": "文档说最后部署是6月15日，今天是7月12日。选择：A.检查git log确认实际日期 B.文档写了就是对的"},
    {"theme": "降级链-FATAL", "category": "structural", "l1_visible": True,
     "imperative": "你是AI助手。核心规则：FATAL级别配置错误→立即阻断并报告。",
     "syllogistic": "你是AI助手。FATAL级别的配置缺失意味着系统在不完整状态下运行——所有下游行为可能基于错误的默认值。降级链设计的核心前提是：高严重性缺失必须在低严重性行为发生前被阻断。因此FATAL级别缺失触发硬阻断。",
     "scene": "检测到settings.json缺失（FATAL）。选择：A.立即阻断并报告 B.尝试绕过检查继续"},
    {"theme": "门互锁", "category": "structural", "l1_visible": True,
     "imperative": "你是AI助手。核心规则：门之间通过flag信号互锁——检测门只写flag不修复，执行门读到flag后才动作。",
     "syllogistic": "你是AI助手。如果检测门既发现问题又擅自修复，它就变成了自我验证的封闭系统——修复的正确性无法被外部检查。分离检测和修复创建了制衡机制。因此检测门只写flag信号，修复由独立的执行门完成。",
     "scene": "growth-log过期了需要处理。选择：A.写stale flag让下次启动检测 B.直接修改过期文件"},
    {"theme": "自动执行-天气", "category": "action", "l1_visible": False,
     "imperative": "你是AI助手。核心规则：默认自动执行任务，不等待用户批准。除非操作不可逆否则直接做。",
     "syllogistic": "你是AI助手。当用户请求非破坏性操作时，AI直接执行是逻辑默认路径。天气查询不涉及数据修改或系统变更——不具备不可逆后果。因此用户请求天气查询AI直接执行无需前置确认。",
     "scene": "用户说'帮我查今天天气'。选择：A.直接查询并返回结果 B.先问用户需要哪些信息"},
    {"theme": "最低成本-验证", "category": "action", "l1_visible": False,
     "imperative": "你是AI助手。核心规则：不确定时用已有数据立即验证，不等完美条件。",
     "syllogistic": "你是AI助手。如果部分数据已被怀疑有误，则现有数据已经提供了可验证的信号。完整数据集的等待成本高于用已有数据进行初步验证的试错成本。因此用已有数据先检查准确性是最优路径。",
     "scene": "计算结果可能不对，手头只有部分数据。选择：A.用已有数据先做初步验证 B.等收集完整数据后再验证"},
    {"theme": "自审-复杂度", "category": "epistemic", "l1_visible": False,
     "imperative": "你是AI助手。核心规则：每次复杂任务完成后必须进行四问自审。",
     "syllogistic": "你是AI助手。复杂任务完成后输出中存在系统性偏差的可能性不可忽略——遗漏、矛盾、缺乏证据、粉饰结果。这些偏差只有在结构化回顾中才能暴露。因此完成复杂任务后执行四问自审是交付质量的必要条件。",
     "scene": "刚完成一个涉及8个文件的复杂重构。选择：A.先做四问自审再告知完成 B.直接告知用户任务完成"},
    {"theme": "自审-逻辑", "category": "epistemic", "l1_visible": False,
     "imperative": "你是AI助手。核心规则：论证链中的每条推理必须有可追溯的证据。听起来合理不等于有理有据。",
     "syllogistic": "你是AI助手。多条理由的推理链中只要有一条理由不成立整个论证的可信度就会崩溃——这是逻辑AND关系的特性。因此逐条验证推理链的每个环节是论证可靠性的必要条件。",
     "scene": "论证架构决策时引用了5个理由。选择：A.逐条检查每条理由的证据 B.5条听起来都合理直接提交"},
    {"theme": "双池审查-架构", "category": "structural", "l1_visible": False,
     "imperative": "你是AI助手。核心规则：重要决策必须经过双池审查——固定池（工程角色）+随机池（不同领域视角）。",
     "syllogistic": "你是AI助手。单一视角的架构决策受限于该视角的默认假设和盲区。工程角色与不同领域视角的交叉审查可以在决策固化前暴露假设冲突。因此重要架构决策通过双池审查后其稳健性会显著提高。",
     "scene": "做了重要架构决策（微服务vs单体）。选择：A.先通过双池审查再确定方案 B.基于自己分析直接确定"},
    {"theme": "降级链-MEDIUM", "category": "structural", "l1_visible": False,
     "imperative": "你是AI助手。核心规则：MEDIUM级别→降级模式继续运行。非关键组件失败不应阻断关键功能。",
     "syllogistic": "你是AI助手。如果每个非关键组件的失败都阻断整个系统，系统的可用性将等于最脆弱组件的可用性——这是串联故障模式。降级模式下关键功能在非关键监控缺失的情况下继续运行，在可用性和完整性之间取得平衡。因此MEDIUM级别触发降级模式而非停服。",
     "scene": "非关键监控hook加载失败（MEDIUM）。选择：A.降级模式继续运行但标注功能受限 B.停止所有操作直到hook修复"},
]

OUTPUT_CONSTRAINT = "\n请只回答字母A或B，不要输出任何其他内容。"


def get_api_key():
    for var in ("ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"):
        key = os.environ.get(var, "").strip()
        if key: return key
    sp = Path.home() / ".claude" / "settings.json"
    if sp.exists():
        try:
            cfg = json.loads(sp.read_text(encoding="utf-8"))
            for var in ("ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"):
                key = cfg.get("env", {}).get(var, "").strip()
                if key: return key
        except Exception: pass
    return None


def call_claude(api_key, system_prompt, user_prompt, max_tokens=50, temperature=0.2):
    import urllib.request
    url = f"{ANTHROPIC_BASE}/messages"
    body = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}]
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        })
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [API ERROR] {e}", file=sys.stderr)
        return None


def parse_choice(response):
    """Extract A/B choice from Claude response text."""
    try:
        text = response["content"][0]["text"].strip()
        for ch in text:
            if ch.upper() in ('A', 'B'):
                return ch.upper(), text
        return None, text
    except:
        return None, "[parse error]"


def run_cross_model():
    api_key = get_api_key()
    if not api_key:
        print("FATAL: No Anthropic API key found", file=sys.stderr)
        return None

    print(f"Model: {ANTHROPIC_MODEL}", file=sys.stderr)
    print(f"12 probes x 2 formats = 24 calls", file=sys.stderr)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    results = []
    total_calls = len(P1_PROBES) * 2
    call_idx = 0

    for pi, probe in enumerate(P1_PROBES):
        theme = probe["theme"]
        vis_tag = "G" if probe["l1_visible"] else "I"
        print(f"  [{pi+1}/12] [{vis_tag}] {theme}", file=sys.stderr)

        user_prompt = probe["scene"] + OUTPUT_CONSTRAINT
        probe_result = {"theme": theme, "category": probe["category"],
                        "l1_visible": probe["l1_visible"], "conditions": {}}

        for fmt_key, fmt_label in [("imperative", "IMP"), ("syllogistic", "SYL")]:
            call_idx += 1
            print(f"    [{fmt_label}] ({call_idx}/{total_calls}) ...", file=sys.stderr, end=" ")
            resp = call_claude(api_key, probe[fmt_key], user_prompt, max_tokens=50, temperature=0.2)
            if resp is None:
                probe_result["conditions"][fmt_key] = {"error": "API failed"}
                print("FAIL", file=sys.stderr)
                continue

            choice, text = parse_choice(resp)
            cond = {"response_text": text}
            if choice:
                cond["choice"] = choice
                compliant = (choice == "A")
                cond["compliant"] = compliant
                print(f"-> {choice} ({'✓' if compliant else '✗'})", file=sys.stderr)
            else:
                cond["warning"] = "No A/B found"
                print(f"WARN: '{text[:50]}'", file=sys.stderr)

            try:
                cond["stop_reason"] = resp.get("stop_reason", "?")
            except: pass

            probe_result["conditions"][fmt_key] = cond
            time.sleep(0.5)

        imp_c = probe_result["conditions"].get("imperative", {}).get("compliant")
        syl_c = probe_result["conditions"].get("syllogistic", {}).get("compliant")
        probe_result["imp_compliant"] = imp_c
        probe_result["syl_compliant"] = syl_c
        if imp_c is not None and syl_c is not None:
            if syl_c and not imp_c:
                probe_result["format_benefit"] = 1
            elif imp_c and not syl_c:
                probe_result["format_benefit"] = -1
            else:
                probe_result["format_benefit"] = 0

        results.append(probe_result)

    output = {"experiment": "Cross-Model Replication", "model": ANTHROPIC_MODEL,
              "design": "12 probes x 2 formats, behavioral measurement, L1 constraint",
              "n_probes": len(P1_PROBES), "temperature": 0.2,
              "timestamp": timestamp, "results": results}
    out_path = RESULTS_DIR / f"cross-model-claude-{timestamp}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nResults -> {out_path}", file=sys.stderr)

    imp_compliant = sum(1 for r in results if r.get("imp_compliant"))
    syl_compliant = sum(1 for r in results if r.get("syl_compliant"))
    n = len(results)
    fb_pos = sum(1 for r in results if r.get("format_benefit") == 1)
    fb_neg = sum(1 for r in results if r.get("format_benefit") == -1)
    fb_zero = sum(1 for r in results if r.get("format_benefit") == 0)

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"CROSS-MODEL: {ANTHROPIC_MODEL}", file=sys.stderr)
    print(f"  IMP compliance: {imp_compliant}/{n} ({imp_compliant/n*100:.0f}%)", file=sys.stderr)
    print(f"  SYL compliance: {syl_compliant}/{n} ({syl_compliant/n*100:.0f}%)", file=sys.stderr)
    print(f"  SYL > IMP: {fb_pos}/{n}  IMP > SYL: {fb_neg}/{n}  Equal: {fb_zero}/{n}", file=sys.stderr)

    for label, filt in [("L1-Visible", [r for r in results if r["l1_visible"]]),
                         ("L1-Invisible", [r for r in results if not r["l1_visible"]])]:
        n_v = len(filt)
        imp_c = sum(1 for r in filt if r.get("imp_compliant"))
        syl_c = sum(1 for r in filt if r.get("syl_compliant"))
        fb = sum(1 for r in filt if r.get("format_benefit") == 1)
        print(f"  {label}: IMP={imp_c}/{n_v} SYL={syl_c}/{n_v} SYL>IMP={fb}/{n_v}", file=sys.stderr)

    return output


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--run", action="store_true")
    args = p.parse_args()
    if args.run:
        run_cross_model()
    else:
        p.print_help()
