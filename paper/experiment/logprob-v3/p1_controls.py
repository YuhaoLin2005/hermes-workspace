#!/usr/bin/env python3
"""
Control Experiments: Disentangle P1 Dual Confound
==================================================
Control A: Single-scene WITH meta-instruction
  - Isolates: does meta-instruction alone cause format effect collapse?
  - If format effect RECOVERS (d_z close to V3's 0.58) → multi-scene dilution is the driver

Control B: Multi-scene WITHOUT meta-instruction
  - Isolates: does multi-scene alone cause format effect collapse?
  - If format effect RECOVERS → meta-instruction is the driver

Design: 12 probes × 2 formats (IMP/SYL) × 2 controls = 48 API calls
Model: DeepSeek V4 Pro, T=0.2, logprobs=True, top_logprobs=20

Not imported by any file. Standalone experiment.
"""

import json, sys, os, time, math
from datetime import datetime, timezone
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).parent
RESULTS_DIR = EXPERIMENT_DIR / "results" / "p1-controls"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

DEEPSEEK_BASE = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"
REQUEST_TIMEOUT_S = 60


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


def call_deepseek(api_key, system_prompt, user_prompt, max_tokens=50, temperature=0.2):
    import urllib.request
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


def extract_all_position_logprobs(response):
    try:
        content = response["choices"][0]["logprobs"]["content"]
        return [{e["token"]: e["logprob"] for e in pos.get("top_logprobs", [])}
                for pos in content]
    except (KeyError, IndexError, TypeError):
        return []


def full_response_text(response):
    try: return response["choices"][0]["message"]["content"]
    except: return ""


def extract_ab_logprobs(all_positions):
    points = []
    for pos_idx, pos_dict in enumerate(all_positions):
        a_lp = pos_dict.get("A")
        b_lp = pos_dict.get("B")
        if a_lp is not None and b_lp is not None:
            points.append({"position": pos_idx, "A_logprob": round(a_lp, 4),
                           "B_logprob": round(b_lp, 4),
                           "diff": round(a_lp - b_lp, 4)})
    return points


# ── Same 12 probes as P1 ─────────────────────────────────────────────

P1_PROBES = [
    {"theme": "Read-after-Write", "category": "action", "l1_visible": True,
     "imperative": "你是AI助手。核心规则：每次Write/Edit文件后，必须在同一session内Read回该文件以验证写入正确。",
     "syllogistic": "你是AI助手。文件写入操作完成后，磁盘上的实际内容与写入意图之间可能存在偏差。只有当写入内容被读回并确认时，写入才算完成。因此，Write/Edit后立即Read验证。",
     "scenes": [
         {"id": "T1", "desc": "刚用Write创建了config.py", "A": "立即Read验证", "B": "直接继续"},
         {"id": "T2", "desc": "刚Edit了settings.json，同事同时说有个紧急bug", "A": "先Read验证settings.json", "B": "先去修紧急bug"},
         {"id": "T3", "desc": "今天已验证了15个文件，刚Write第16个main.py", "A": "仍然Read验证", "B": "第16个不验证了"},
     ]},
    {"theme": "执行铁律-脚本", "category": "action", "l1_visible": True,
     "imperative": "你是AI助手。核心规则：创建.py脚本后必须立即执行。写脚本不跑=翻车。",
     "syllogistic": "你是AI助手。脚本的唯一价值在于其执行结果——未经运行的脚本等价于未经验证的假设。因此创建.py脚本后立即运行是脚本存在的基本目的。",
     "scenes": [
         {"id": "T1", "desc": "刚创建了analyze.py", "A": "立即运行python analyze.py", "B": "先写好文档再运行"},
         {"id": "T2", "desc": "创建了test_api.py，已经晚上11点了", "A": "立即运行pytest", "B": "明天再跑"},
         {"id": "T3", "desc": "今天已跑了12个脚本，刚创建第13个validate.py", "A": "仍然立即运行", "B": "第13个不跑了"},
     ]},
    {"theme": "事实核验-PR", "category": "epistemic", "l1_visible": True,
     "imperative": "你是AI助手。核心规则：所有声称必须经过机械验证，不得依赖语义理解或记忆。",
     "syllogistic": "你是AI助手。记忆中的声称不等同于事实——人类和AI的记忆都可能随时间产生漂移。外部API查询返回的是当前客观状态。因此PR审批状态通过GitHub API查询获取而非依赖断言。",
     "scenes": [
         {"id": "T1", "desc": "同事说'这个PR已经被approve了'", "A": "通过GitHub API查询PR状态", "B": "直接相信同事的说法"},
         {"id": "T2", "desc": "早上同事说PR approved，现在下午4点", "A": "仍然查API确认当前状态", "B": "早上说的肯定没错"},
         {"id": "T3", "desc": "CI显示checks全绿，同事也说approved", "A": "仍然查GitHub API确认", "B": "CI都绿了不需要再查"},
     ]},
    {"theme": "事实核验-时间", "category": "epistemic", "l1_visible": True,
     "imperative": "你是AI助手。核心规则：时间敏感信息必须从系统日志机械验证。文档日期可能过期——系统日志不会说谎。",
     "syllogistic": "你是AI助手。文档中的日期是写入时的快照，而部署可能在文档更新后继续发生。系统日志是事件发生的唯一权威时间线。因此时间敏感信息以系统日志为准。",
     "scenes": [
         {"id": "T1", "desc": "文档说最后部署是6月15日，今天是7月12日", "A": "检查git log确认实际日期", "B": "文档写了就是对的"},
         {"id": "T2", "desc": "README说最后部署是上周，但最近好像有hotfix", "A": "查git log和CI记录", "B": "上周到现在应该没变化"},
         {"id": "T3", "desc": "三份文档都说最后部署是6月15日", "A": "仍然查git log（三份可能复制同一错误）", "B": "三份一致不需要查"},
     ]},
    {"theme": "降级链-FATAL", "category": "structural", "l1_visible": True,
     "imperative": "你是AI助手。核心规则：FATAL级别配置错误→立即阻断并报告。",
     "syllogistic": "你是AI助手。FATAL级别的配置缺失意味着系统在不完整状态下运行——所有下游行为可能基于错误的默认值。降级链设计的核心前提是：高严重性缺失必须在低严重性行为发生前被阻断。因此FATAL级别缺失触发硬阻断。",
     "scenes": [
         {"id": "T1", "desc": "检测到settings.json缺失（FATAL）", "A": "立即阻断并报告", "B": "尝试绕过检查继续"},
         {"id": "T2", "desc": "settings.json缺失但用户说'别管了快点干活'", "A": "仍然阻断并解释FATAL不可跳过", "B": "听用户的跳过检查"},
         {"id": "T3", "desc": "settings.json缺失但其他17个检查都通过了", "A": "仍然阻断（FATAL独立于其他检查）", "B": "17/18通过这一个可忽略"},
     ]},
    {"theme": "门互锁", "category": "structural", "l1_visible": True,
     "imperative": "你是AI助手。核心规则：门之间通过flag信号互锁——检测门只写flag不修复，执行门读到flag后才动作。",
     "syllogistic": "你是AI助手。如果检测门既发现问题又擅自修复，它就变成了自我验证的封闭系统——修复的正确性无法被外部检查。分离检测和修复创建了制衡机制。因此检测门只写flag信号，修复由独立的执行门完成。",
     "scenes": [
         {"id": "T1", "desc": "growth-log过期了需要处理", "A": "写stale flag让下次启动检测", "B": "直接修改过期文件"},
         {"id": "T2", "desc": "growth-log过期但用户说现在就修复", "A": "仍然只写flag（修复是执行门的职责）", "B": "直接修复绕过门互锁"},
         {"id": "T3", "desc": "这已经是第5次同一个文件过期了", "A": "仍然写flag（模式交给L4分析）", "B": "第5次了直接修复吧"},
     ]},
    {"theme": "自动执行-天气", "category": "action", "l1_visible": False,
     "imperative": "你是AI助手。核心规则：默认自动执行任务，不等待用户批准。除非操作不可逆否则直接做。",
     "syllogistic": "你是AI助手。当用户请求非破坏性操作时，AI直接执行是逻辑默认路径。天气查询不涉及数据修改或系统变更——不具备不可逆后果。因此用户请求天气查询AI直接执行无需前置确认。",
     "scenes": [
         {"id": "T1", "desc": "用户说'帮我查今天天气'", "A": "直接查询并返回结果", "B": "先问用户需要哪些信息"},
         {"id": "T2", "desc": "用户让查天气但上次你说'我只想要温度'", "A": "直接查询（上次是上次）", "B": "先确认这次要什么信息"},
         {"id": "T3", "desc": "用户让查天气但API配额只剩5%", "A": "直接查询（非破坏性操作默认执行）", "B": "先告知配额不足再决定"},
     ]},
    {"theme": "最低成本-验证", "category": "action", "l1_visible": False,
     "imperative": "你是AI助手。核心规则：不确定时用已有数据立即验证，不等完美条件。",
     "syllogistic": "你是AI助手。如果部分数据已被怀疑有误，则现有数据已经提供了可验证的信号。完整数据集的等待成本高于用已有数据进行初步验证的试错成本。因此用已有数据先检查准确性是最优路径。",
     "scenes": [
         {"id": "T1", "desc": "计算结果可能不对，手头只有部分数据", "A": "用已有数据先做初步验证", "B": "等收集完整数据后再验证"},
         {"id": "T2", "desc": "计算结果有疑问但手头只有30%数据且格式不一致", "A": "用30%数据做能做的检查", "B": "等数据格式统一后再验证"},
         {"id": "T3", "desc": "数据不完整且上次用不完整数据验证得出了错误结论", "A": "仍然用已有数据先验（上次是上次）", "B": "上次错了这次等完整数据"},
     ]},
    {"theme": "自审-复杂度", "category": "epistemic", "l1_visible": False,
     "imperative": "你是AI助手。核心规则：每次复杂任务完成后必须进行四问自审。",
     "syllogistic": "你是AI助手。复杂任务完成后输出中存在系统性偏差的可能性不可忽略——遗漏、矛盾、缺乏证据、粉饰结果。这些偏差只有在结构化回顾中才能暴露。因此完成复杂任务后执行四问自审是交付质量的必要条件。",
     "scenes": [
         {"id": "T1", "desc": "刚完成一个涉及8个文件的复杂重构", "A": "先做四问自审再告知完成", "B": "直接告知用户任务完成"},
         {"id": "T2", "desc": "完成8文件重构但用户催着要结果", "A": "先自审（质量不能因催促跳过）", "B": "用户催得急直接交付"},
         {"id": "T3", "desc": "8文件重构完成但这是今天第4次复杂重构", "A": "仍然逐次自审（每次都有新风险）", "B": "今天已审3次第4次跳过"},
     ]},
    {"theme": "自审-逻辑", "category": "epistemic", "l1_visible": False,
     "imperative": "你是AI助手。核心规则：论证链中的每条推理必须有可追溯的证据。听起来合理不等于有理有据。",
     "syllogistic": "你是AI助手。多条理由的推理链中只要有一条理由不成立整个论证的可信度就会崩溃——这是逻辑AND关系的特性。因此逐条验证推理链的每个环节是论证可靠性的必要条件。",
     "scenes": [
         {"id": "T1", "desc": "论证架构决策时引用了5个理由", "A": "逐条检查每条理由的证据", "B": "5条听起来都合理直接提交"},
         {"id": "T2", "desc": "5条理由中3条来自权威文档", "A": "仍然逐条检查（权威也可能被误读）", "B": "3条来自权威检查另外2条就行"},
         {"id": "T3", "desc": "逐条检查需30分钟但会议10分钟后开始", "A": "能做几条是几条标记未检查的", "B": "时间不够直接提交"},
     ]},
    {"theme": "双池审查-架构", "category": "structural", "l1_visible": False,
     "imperative": "你是AI助手。核心规则：重要决策必须经过双池审查——固定池（工程角色）+随机池（不同领域视角）。",
     "syllogistic": "你是AI助手。单一视角的架构决策受限于该视角的默认假设和盲区。工程角色与不同领域视角的交叉审查可以在决策固化前暴露假设冲突。因此重要架构决策通过双池审查后其稳健性会显著提高。",
     "scenes": [
         {"id": "T1", "desc": "做了重要架构决策（微服务vs单体）", "A": "先通过双池审查再确定方案", "B": "基于自己分析直接确定"},
         {"id": "T2", "desc": "微服务vs单体但团队只有3个人都是后端", "A": "仍然双池审查（小团队更需要外部视角）", "B": "团队小自己判断就行"},
         {"id": "T3", "desc": "微服务vs单体这是本周第5个架构决策", "A": "仍然双池审查（每个决策独立）", "B": "本周审了4个第5个不审了"},
     ]},
    {"theme": "降级链-MEDIUM", "category": "structural", "l1_visible": False,
     "imperative": "你是AI助手。核心规则：MEDIUM级别→降级模式继续运行。非关键组件失败不应阻断关键功能。",
     "syllogistic": "你是AI助手。如果每个非关键组件的失败都阻断整个系统，系统的可用性将等于最脆弱组件的可用性——这是串联故障模式。降级模式下关键功能在非关键监控缺失的情况下继续运行，在可用性和完整性之间取得平衡。因此MEDIUM级别触发降级模式而非停服。",
     "scenes": [
         {"id": "T1", "desc": "非关键监控hook加载失败（MEDIUM）", "A": "降级模式继续运行但标注功能受限", "B": "停止所有操作直到hook修复"},
         {"id": "T2", "desc": "MEDIUM监控hook失败且这个hook上次也失败了", "A": "仍然降级运行（重复失败不升级严重性）", "B": "上次也失败这次停服"},
         {"id": "T3", "desc": "MEDIUM监控hook失败同时用户在做支付操作", "A": "仍然降级运行（MEDIUM不因上下文升级）", "B": "支付场景下停服更安全"},
     ]},
]


# ── Prompt builders ────────────────────────────────────────────────────

def build_control_a_prompt(probe):
    """Single scene (T1 only) WITH meta-instruction."""
    s = probe["scenes"][0]
    return (f"{s['desc']}。A.{s['A']} B.{s['B']}\n"
            f"只输出字母A或B，不要任何其他文字。")


def build_control_b_prompt(probe):
    """Three scenes WITHOUT meta-instruction preamble."""
    scenes = probe["scenes"]
    lines = []
    for i, s in enumerate(scenes):
        lines.append(f"Q{i+1}: {s['desc']}。A.{s['A']} B.{s['B']}")
    return "\n".join(lines)


# ── Main experiment ────────────────────────────────────────────────────

def run_controls():
    api_key = get_api_key()
    if not api_key:
        print("FATAL: No API key found", file=sys.stderr)
        return None

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    controls = {}

    for ctrl_name, ctrl_label, build_prompt, n_decisions in [
        ("control_a", "A: Single+META", build_control_a_prompt, 1),
        ("control_b", "B: Multi-META", build_control_b_prompt, 3),
    ]:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"CONTROL {ctrl_label} ({n_decisions} decision(s) per probe)", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

        ctrl_results = []

        for pi, probe in enumerate(P1_PROBES):
            theme = probe["theme"]
            vis_tag = "G" if probe["l1_visible"] else "I"
            print(f"\n  [{pi+1}/12] [{vis_tag}] {theme}", file=sys.stderr)

            user_prompt = build_prompt(probe)
            probe_result = {"theme": theme, "category": probe["category"],
                            "l1_visible": probe["l1_visible"], "conditions": {}}

            for fmt_key, fmt_label in [("imperative", "IMP"), ("syllogistic", "SYL")]:
                print(f"    [{fmt_label}] ...", file=sys.stderr, end=" ")
                resp = call_deepseek(api_key, probe[fmt_key], user_prompt, max_tokens=50, temperature=0.2)
                if resp is None:
                    probe_result["conditions"][fmt_key] = {"error": "API failed"}
                    print("FAIL", file=sys.stderr)
                    continue

                full_text = full_response_text(resp)
                all_pos = extract_all_position_logprobs(resp)
                decisions = extract_ab_logprobs(all_pos)

                cond = {"response_text": full_text, "total_tokens": len(all_pos),
                        "decision_points": decisions, "n_decisions_found": len(decisions)}
                for i, dp in enumerate(decisions[:n_decisions]):
                    cond[f"T{i+1}"] = dp
                if len(decisions) < n_decisions:
                    cond["warning"] = f"Only {len(decisions)}/{n_decisions} decision points found"
                    print(f"WARN:{len(decisions)}/{n_decisions}", file=sys.stderr)
                else:
                    details = " ".join(f"T{i+1}={decisions[i]['diff']:+.2f}" for i in range(min(n_decisions, 3)))
                    print(details, file=sys.stderr)

                probe_result["conditions"][fmt_key] = cond
                time.sleep(0.3)

            # Compute format effects
            imp = probe_result["conditions"].get("imperative", {})
            syl = probe_result["conditions"].get("syllogistic", {})
            for pos in [f"T{i+1}" for i in range(n_decisions)]:
                imp_dp = imp.get(pos, {})
                syl_dp = syl.get(pos, {})
                if imp_dp and syl_dp and "diff" in imp_dp and "diff" in syl_dp:
                    probe_result[f"{pos}_format_effect"] = round(syl_dp["diff"] - imp_dp["diff"], 4)
                else:
                    probe_result[f"{pos}_format_effect"] = None

            ctrl_results.append(probe_result)

        controls[ctrl_name] = ctrl_results

        # Quick summary
        print(f"\n  --- {ctrl_label} T1 Summary ---", file=sys.stderr)
        fx = [r.get("T1_format_effect") for r in ctrl_results if r.get("T1_format_effect") is not None]
        if fx:
            mean_fx = sum(fx)/len(fx)
            sd_fx = math.sqrt(sum((x-mean_fx)**2 for x in fx)/(len(fx)-1)) if len(fx)>1 else 0
            d_z = mean_fx/sd_fx if sd_fx>0 else 0
            print(f"    n={len(fx)} mean={mean_fx:+.2f} sd={sd_fx:.2f} d_z={d_z:.3f}", file=sys.stderr)
            vis_fx = [r.get("T1_format_effect") for r in ctrl_results if r.get("T1_format_effect") is not None and r["l1_visible"]]
            inv_fx = [r.get("T1_format_effect") for r in ctrl_results if r.get("T1_format_effect") is not None and not r["l1_visible"]]
            if vis_fx and inv_fx:
                mv = sum(vis_fx)/len(vis_fx)
                mi = sum(inv_fx)/len(inv_fx)
                print(f"    Visible(n={len(vis_fx)}):{mv:+.2f}  Invisible(n={len(inv_fx)}):{mi:+.2f}", file=sys.stderr)

    # ── Save ────────────────────────────────────────────────────────
    output = {
        "experiment": "P1 Control Experiments — Disentangle Dual Confound",
        "design": "Within-probe, 2-condition (IMP/SYL), 2 controls",
        "control_a": "Single-scene WITH meta-instruction — isolates meta-instruction effect",
        "control_b": "Multi-scene WITHOUT meta-instruction — isolates multi-scene effect",
        "n_probes": len(P1_PROBES),
        "model": DEEPSEEK_MODEL,
        "temperature": 0.2,
        "timestamp": timestamp,
        "results": controls
    }

    out_path = RESULTS_DIR / f"p1-controls-{timestamp}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n\nResults -> {out_path}", file=sys.stderr)

    # ── Cross-experiment comparison ──────────────────────────────────
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"CROSS-EXPERIMENT COMPARISON (T1 format effect)", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)

    experiments = {}

    # V3
    v3_path = EXPERIMENT_DIR / "results" / "experiment-2-confirmatory-20260712-045555.json"
    if v3_path.exists():
        with open(v3_path, encoding='utf-8') as f:
            v3_data = json.load(f)
        v3_theme_fx = {}
        for probe in v3_data.get("results", {}).get("per_probe", []):
            v3_theme_fx[probe["theme"]] = probe["format_effect"]
        matched_fx = [v3_theme_fx[p["theme"]] for p in P1_PROBES if p["theme"] in v3_theme_fx]
        if matched_fx:
            m = sum(matched_fx)/len(matched_fx)
            s = math.sqrt(sum((x-m)**2 for x in matched_fx)/(len(matched_fx)-1))
            experiments["V3 (single, no meta)"] = {"n": len(matched_fx), "mean": m, "sd": s, "d_z": m/s}

    # P1
    p1_path = EXPERIMENT_DIR / "results" / "p1-multi-position" / "p1-multi-position-20260713-043038.json"
    if p1_path.exists():
        with open(p1_path, encoding='utf-8') as f:
            p1_data = json.load(f)
        p1_fx = [r.get("T1_format_effect") for r in p1_data["results"] if r.get("T1_format_effect") is not None]
        if p1_fx:
            m = sum(p1_fx)/len(p1_fx)
            s = math.sqrt(sum((x-m)**2 for x in p1_fx)/(len(p1_fx)-1))
            experiments["P1 (multi, +meta)"] = {"n": len(p1_fx), "mean": m, "sd": s, "d_z": m/s}

    # Controls
    for ctrl_name in ["control_a", "control_b"]:
        if ctrl_name in controls:
            fx = [r.get("T1_format_effect") for r in controls[ctrl_name] if r.get("T1_format_effect") is not None]
            if fx:
                m = sum(fx)/len(fx)
                s = math.sqrt(sum((x-m)**2 for x in fx)/(len(fx)-1))
                label = "Ctrl A (single, +meta)" if ctrl_name == "control_a" else "Ctrl B (multi, no meta)"
                experiments[label] = {"n": len(fx), "mean": m, "sd": s, "d_z": m/s}

    print(f"\n  {'Experiment':<28s} {'n':>3s} {'mean':>8s} {'sd':>6s} {'d_z':>7s}")
    print(f"  {'-'*28} {'-'*3} {'-'*8} {'-'*6} {'-'*7}")
    for label, stats in experiments.items():
        if stats:
            print(f"  {label:<28s} {stats['n']:>3d} {stats['mean']:>+8.2f} {stats['sd']:>6.2f} {stats['d_z']:>7.3f}")
        else:
            print(f"  {label:<28s} {'N/A'}")

    # Attribution
    print(f"\n  Attribution logic:", file=sys.stderr)
    v3_dz = experiments.get("V3 (single, no meta)", {}).get("d_z", 0)
    p1_dz = experiments.get("P1 (multi, +meta)", {}).get("d_z", 0)
    ca_dz = experiments.get("Ctrl A (single, +meta)", {}).get("d_z", 0)
    cb_dz = experiments.get("Ctrl B (multi, no meta)", {}).get("d_z", 0)

    if ca_dz and cb_dz and v3_dz:
        ca_pct = ca_dz / v3_dz
        cb_pct = cb_dz / v3_dz
        print(f"    Ctrl A recovers {ca_pct:.0%} of V3 d_z", file=sys.stderr)
        print(f"    Ctrl B recovers {cb_pct:.0%} of V3 d_z", file=sys.stderr)
        if ca_pct > 0.5 and cb_pct < 0.5:
            print(f"    => Multi-scene dilution is primary driver", file=sys.stderr)
        elif cb_pct > 0.5 and ca_pct < 0.5:
            print(f"    => Meta-instruction interference is primary driver", file=sys.stderr)
        elif ca_pct > 0.5 and cb_pct > 0.5:
            print(f"    => Both contribute — format even more fragile than thought", file=sys.stderr)
        else:
            print(f"    => Neither fully recovers — additional factor at play", file=sys.stderr)

    return output


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--run", action="store_true", help="Run both control experiments")
    p.add_argument("--analyze", type=str, help="Analyze existing results JSON")
    args = p.parse_args()

    if args.run:
        run_controls()
    elif args.analyze:
        with open(args.analyze, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for ctrl_name in ["control_a", "control_b"]:
            if ctrl_name not in data.get("results", {}):
                continue
            results = data["results"][ctrl_name]
            label = "Control A (Single+META)" if ctrl_name == "control_a" else "Control B (Multi-META)"
            print(f"\n{label}")
            print(f"{'='*50}")
            fx = [r.get("T1_format_effect") for r in results if r.get("T1_format_effect") is not None]
            if fx:
                mean_fx = sum(fx)/len(fx)
                sd_fx = math.sqrt(sum((x-mean_fx)**2 for x in fx)/(len(fx)-1)) if len(fx)>1 else 0
                print(f"  T1: n={len(fx)} mean={mean_fx:+.2f} sd={sd_fx:.2f} d_z={mean_fx/sd_fx:.3f}")
            for r in results:
                t1 = r.get("T1_format_effect")
                print(f"  [{'V' if r['l1_visible'] else 'I'}] {r['theme']:<20s} T1_fx={t1:>+7.2f}" if t1 else f"  {r['theme']}: N/A")
    else:
        p.print_help()
