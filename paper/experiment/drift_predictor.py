#!/usr/bin/env python3
"""
Drift Risk Predictor — 配置漂移风险预测模型

借鉴命理"排大运"的时序预测框架：根据 session 特征预测违规倾向（非确定性）。
输出 Drift Risk Score (0-100) + 风险分解 + 预防建议。

基于数据：
  - 34 growth-log 回溯编码 (55.9% violation rate)
  - 150 task Format A/B 实验 (0.7% violation, GateGuard ceiling)
  - 5 meta-patterns extracted

用法:
  python drift-predictor.py                    # 评估当前 session
  python drift-predictor.py --json             # JSON 输出
  python drift-predictor.py --calibrate        # 显示校准数据
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ── 特征权重（基于 34 growth-log 回溯编码校准）────────────────────────

# Rule violation rates from systematic-baseline-coding.md:
# R1 dual-pool skip:      8/34 = 23.5%
# R2 no Read-after-Write: 12/34 = 35.3%
# R3 no pre-check:        15/34 = 44.1%  ← 最高风险
# R4 no capture:          10/34 = 29.4%
# R5 no self-audit:        7/34 = 20.6%

WEIGHTS = {
    "rule_count":            0.10,   # 规则越多→复杂度越高
    "unhooked_rules":        0.20,   # 无机械门保护的规则（R3: 44.1%）
    "session_age_turns":     0.08,   # 长 session→漂移累积
    "compact_count":         0.12,   # 每次 compact 改写前缀→漂移风险
    "tool_diversity":        0.05,   # 工具多→切换频繁
    "days_since_audit":      0.15,   # 自审周期长→漂移未被发现
    "gate_coverage":        -0.20,   # 机械门覆盖率→保护因子（负权重=降低风险）
    "pre_check_compliance":  0.10,   # 前置检查跳过历史→惯性
}

# 风险阈值（基于实验数据校准）
# 无机械门: 55.9% violation rate → Risk ≈ 56
# 有机械门 (GateGuard): 0.7% violation rate → Risk ≈ 1
RISK_BASELINE_NO_GATE = 56
RISK_BASELINE_WITH_GATE = 1


class DriftPredictor:
    """配置漂移风险预测器"""

    def __init__(self, config_dir=None, growth_log_dir=None):
        self.config_dir = Path(config_dir or os.path.expanduser("~/.claude"))
        self.growth_log_dir = Path(
            growth_log_dir
            or os.path.expanduser("~/.claude/projects/C--Users-86131/memory/growth-log")
        )

    def collect_features(self) -> dict:
        """收集当前 session 特征"""
        features = {}
        features["rule_count"] = self._count_active_rules()
        features["unhooked_rules"] = self._count_unhooked_rules()
        features["session_age_turns"] = self._estimate_session_turns()
        features["compact_count"] = self._count_compacts()
        features["tool_diversity"] = self._count_tool_types()
        features["days_since_audit"] = self._days_since_last_audit()
        features["gate_coverage"] = self._compute_gate_coverage()
        features["pre_check_compliance"] = self._check_pre_check_history()
        return features

    def compute_risk(self, features: dict = None) -> dict:
        """计算漂移风险分数 (0-100)"""
        if features is None:
            features = self.collect_features()

        raw_score = 0.0
        contributions = {}
        for feature, weight in WEIGHTS.items():
            value = features.get(feature, 0)
            contrib = value * weight * 100
            raw_score += contrib
            contributions[feature] = {
                "value": value,
                "weight": weight,
                "contribution": round(contrib, 1),
            }

        risk_score = max(0, min(100, raw_score))

        if risk_score < 20:
            level, msg = "LOW", "机械门有效覆盖，漂移风险低"
        elif risk_score < 40:
            level, msg = "MODERATE", "部分规则缺乏机械保护，建议增加 hook 覆盖"
        elif risk_score < 60:
            level, msg = "ELEVATED", "多个风险因子叠加，建议近期自审"
        elif risk_score < 80:
            level, msg = "HIGH", "漂移大概率已发生，需立即全面自审"
        else:
            level, msg = "CRITICAL", "严重漂移风险，系统完整性可能已受损"

        # 分级遏制映射 (inspired by ABC graduated containment)
        action_map = {
            "LOW":      "none",
            "MODERATE": "increase_read_before_write",
            "ELEVATED": "block_edit_write",
            "HIGH":     "force_full_audit",
            "CRITICAL": "abort_session",
        }

        top_factors = sorted(
            contributions.items(),
            key=lambda x: abs(x[1]["contribution"]),
            reverse=True,
        )[:3]

        return {
            "risk_score": round(risk_score, 1),
            "risk_level": level,
            "interpretation": msg,
            "action_required": action_map[level],
            "feature_contributions": contributions,
            "top_factors": [
                {"feature": f[0], "impact": f[1]["contribution"]}
                for f in top_factors
            ],
            "baseline_no_gate": RISK_BASELINE_NO_GATE,
            "baseline_with_gate": RISK_BASELINE_WITH_GATE,
            "recommendations": self._generate_recommendations(contributions),
        }

    # ── 私有方法 ──────────────────────────────────────────────────────

    def _count_active_rules(self) -> float:
        """解析配置文件中的实际规则行数（非文件数×5）。匹配markdown规则格式: '- ', '* ', 编号, '## ' 标题。分母50=50条规则→满复杂度。SoulKeeper借鉴：规则提取替代文件计数。"""
        rule_files = [
            self.config_dir / "CLAUDE.md",
            self.config_dir / "SOUL.md",
            self.config_dir / "INTERFACE.md",
            self.config_dir / "BODY.md",
        ]
        total_rules = 0
        for f in rule_files:
            if not f.exists():
                continue
            try:
                content = f.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    stripped = line.strip()
                    # 匹配规则行: markdown列表项、编号项、###约束标题
                    if re.match(r'^[-*]\s+\*\*', stripped):   # - **rule name**: ...
                        total_rules += 1
                    elif re.match(r'^\d+\.\s', stripped):     # 1. rule
                        total_rules += 1
                    elif re.match(r'^#{2,3}\s+(规则|约束|Rule|Constraint)', stripped):
                        total_rules += 1
            except Exception:
                pass
        return min(1.0, total_rules / 50)  # 50条规则=满复杂度

    def _count_unhooked_rules(self) -> float:
        """未受hook保护的规则比例。分母7=当前系统的hook事件类型数(SessionStart/PreToolUse/PostToolUse/Stop/PreCompact/PostCompact/Notification)。"""
        settings = self.config_dir / "settings.json"
        if not settings.exists():
            return 1.0
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
            hooks = data.get("hooks", {})
            protected_categories = len(hooks)
            total_categories = 7  # Claude Code hook事件类型总数
            coverage = protected_categories / total_categories
            return max(0, 1.0 - coverage)
        except Exception:
            return 0.8

    def _estimate_session_turns(self) -> float:
        """最近3天growth-log文件数估算session活跃度。分母3=连续3天有记录→满活跃。"""
        if not self.growth_log_dir.exists():
            return 0.2
        try:
            cutoff = datetime.now().timestamp() - 3 * 86400
            recent = sum(1 for f in self.growth_log_dir.glob("*.md")
                        if f.stat().st_mtime > cutoff)
            return min(1.0, recent / 3)  # 3天连续活跃=1.0
        except Exception:
            return 0.3

    def _count_compacts(self) -> float:
        """最近24h内 /compact 事件数。JSONL解析+时间过滤避免'compact'子串误匹配。分母5=5次compact→满风险。"""
        history_file = self.config_dir / "history.jsonl"
        if not history_file.exists():
            return 0.0
        try:
            cutoff = datetime.now().timestamp() - 86400
            recent = 0
            for line in history_file.read_text(encoding="utf-8").strip().split("\n"):
                try:
                    d = json.loads(line)
                    ts = d.get("timestamp", 0) / 1000  # 毫秒→秒
                    if ts > cutoff and d.get("display", "").strip() == "/compact":
                        recent += 1
                except Exception:
                    pass
            return min(1.0, recent / 5)  # 24h内5次compact=满风险
        except Exception:
            return 0.1

    def _count_tool_types(self) -> float:
        settings = self.config_dir / "settings.json"
        if not settings.exists():
            return 0.5
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
            mcp_count = len(data.get("enabledMcpjsonServers", []))
            plugin_count = len(data.get("enabledPlugins", {}))
            total = mcp_count + plugin_count
            return min(1.0, total / 10)  # 10个服务器/插件=满工具多样性
        except Exception:
            return 0.4

    def _days_since_last_audit(self) -> float:
        self_model = Path(
            os.path.expanduser(
                "~/.claude/projects/C--Users-86131/memory/self-model.md"
            )
        )
        if not self_model.exists():
            return 1.0
        mtime = datetime.fromtimestamp(self_model.stat().st_mtime)
        days = (datetime.now() - mtime).days
        return min(1.0, days / 7)  # 7天未自审=满风险

    def _compute_gate_coverage(self) -> float:
        settings = self.config_dir / "settings.json"
        if not settings.exists():
            return 0.0
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
            hooks = data.get("hooks", {})
            total_hooks = sum(
                len(v) if isinstance(v, list) else 1 for v in hooks.values()
            )
            return min(1.0, total_hooks / 12)  # 12个hook实例=全覆盖
        except Exception:
            return 0.1

    def _check_pre_check_history(self) -> float:
        """最近3个growth-log中跳过前置检查的比率。精确匹配避免'skip'子串误触发。分母3=全部跳过→满风险。"""
        if not self.growth_log_dir.exists():
            return 0.5
        try:
            logs = sorted(self.growth_log_dir.glob("*.md"), reverse=True)[:3]
            skip_count = 0
            for log in logs:
                content = log.read_text(encoding="utf-8")[:2000]
                if "跳过" in content or "skip pre-check" in content.lower() or \
                   "skipped pre-check" in content.lower() or "skip three-questions" in content.lower():
                    skip_count += 1
            return skip_count / 3  # 3个日志全有跳过=1.0
        except Exception:
            return 0.3

    def _generate_recommendations(self, contributions: dict) -> list:
        recs = []
        for feature, data in sorted(
            contributions.items(),
            key=lambda x: abs(x[1]["contribution"]),
            reverse=True,
        ):
            if abs(data["contribution"]) < 2:
                continue
            if feature == "unhooked_rules" and data["contribution"] > 5:
                recs.append("为无机械门保护的规则添加 hook（PreToolUse/PostToolUse）")
            elif feature == "days_since_audit" and data["contribution"] > 5:
                recs.append("距上次自审已超 3 天，建议立即运行 quality-gate.py")
            elif feature == "compact_count" and data["contribution"] > 5:
                recs.append("Compact 事件频繁，检查 autoCompactWindow 是否过小")
            elif feature == "pre_check_compliance" and data["contribution"] > 5:
                recs.append("检测到跳过前置检查的历史模式→加强 three-questions-guard")
            elif feature == "gate_coverage" and data["contribution"] < -5:
                recs.append("机械门覆盖率良好，保持当前 hook 配置")
        if not recs:
            recs.append("当前风险可控，维持定期自审节奏")
        return recs


# ── CLI ────────────────────────────────────────────────────────────────

def main():
    predictor = DriftPredictor()

    if "--calibrate" in sys.argv:
        print("=== 校准数据 (Calibration Data) ===")
        print(f"无机械门基线:  55.9% violation → Risk = {RISK_BASELINE_NO_GATE}")
        print(f"有机械门基线:   0.7% violation → Risk = {RISK_BASELINE_WITH_GATE}")
        print(f"\n特征权重 (基于 34 growth-log + 150 task):")
        for feat, w in sorted(WEIGHTS.items(), key=lambda x: -abs(x[1])):
            direction = "protective" if w < 0 else "risk"
            print(f"  {feat:25s} {w:+5.2f}  {direction}")
        print(f"\n数据来源:")
        print(f"  systematic-baseline-coding.md — 34 sessions, 55.9% violation")
        print(f"  experiment-results-2026-07-11.md — 150 tasks, 0.7% violation")
        return

    features = predictor.collect_features()
    result = predictor.compute_risk(features)

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("═══ Drift Risk Report ═══")
        print(f"Risk Score:  {result['risk_score']}/100  [{result['risk_level']}]")
        print(f"解读:        {result['interpretation']}")
        print(f"\n参考基线:")
        print(f"  无机械门:  {result['baseline_no_gate']}")
        print(f"  有机械门:  {result['baseline_with_gate']}")
        print(f"\nTop 3 风险因子:")
        for f in result["top_factors"]:
            direction = "+" if f["impact"] > 0 else "-"
            print(f"  [{direction}] {f['feature']}: {f['impact']:+.1f}")
        print(f"\n建议:")
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"  {i}. {rec}")


if __name__ == "__main__":
    main()
