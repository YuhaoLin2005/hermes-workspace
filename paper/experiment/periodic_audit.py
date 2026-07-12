#!/usr/bin/env python3
"""
Periodic Self-Audit — 主动式定期自审（非被动等 flag）

核心哲学 (2026-07-11 洞察):
  人类逻辑 ≠ LLM 逻辑。不要求模型"理解"自审——
  把自审需求编码为三段论格式，路由模型注意力自然处理。

三层输出:
  1. 机械层: 退出码 (exit 0/2) → hook 硬阻断
  2. 风险层: Drift Risk Score → 导入 drift-predictor
  3. 提示层: 大前提/小前提/结论 三段论 → L3 因果编码通路

触发时机:
  - 流年: 每 N 小时固定自审
  - 关口: compact ≥ N 次后
  - 换运: 工具配置变化后
  - 岁运: 距上次自审 > 3 天

用法:
  python periodic-audit.py                       # 默认 scheduled
  python periodic-audit.py --checkpoint compact   # compact 关口检查
  python periodic-audit.py --checkpoint force     # 手动触发
  python periodic-audit.py --json                 # JSON 输出
  python periodic-audit.py --prompt-only          # 仅模型原生提示词
"""

import json
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── 日志路径 ──────────────────────────────────────────────────────────

AUDIT_LOG = Path(os.path.expanduser("~/.claude/audit-log.jsonl"))
AUDIT_INTERVAL_HOURS = 8
AUDIT_INTERVAL_COMPACTS = 3
AUDIT_INTERVAL_DAYS = 3


class PeriodicAudit:
    """主动式定期自审——人类逻辑→模型原生格式"""

    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir or os.path.expanduser("~/.claude"))

    # ── 决策层 ──────────────────────────────────────────────────────

    def should_audit(self, checkpoint_type: str = "scheduled") -> dict:
        triggers = {
            "scheduled":   self._check_scheduled,
            "compact":     self._check_compact_gate,
            "tool_change": self._check_tool_change,
            "force":       lambda: True,
        }
        check_fn = triggers.get(checkpoint_type, lambda: False)
        should = check_fn()
        reasons = {
            "scheduled":   f"距上次自审 > {AUDIT_INTERVAL_HOURS}h（流年检查）",
            "compact":     f"累计 {self._count_recent_compacts()} compact（关口检查）",
            "tool_change": "工具配置已变化（换运检查）",
            "force":       "手动触发",
        }
        return {"triggered": should, "checkpoint": checkpoint_type,
                "reason": reasons.get(checkpoint_type, "")}

    def _check_scheduled(self) -> bool:
        last = self._last_audit_time()
        if last is None:
            return True
        return (datetime.now(timezone.utc) - last).total_seconds() > AUDIT_INTERVAL_HOURS * 3600

    def _check_compact_gate(self) -> bool:
        return self._count_recent_compacts() >= AUDIT_INTERVAL_COMPACTS

    def _check_tool_change(self) -> bool:
        return self._tool_config_hash() != self._last_audit_tool_hash()

    # ── 执行层 ──────────────────────────────────────────────────────

    def run_audit(self, checkpoint_type: str = "scheduled") -> dict:
        decision = self.should_audit(checkpoint_type)

        # L1: 机械检查
        mechanical = self._mechanical_checks()
        all_pass = all(c["pass"] for c in mechanical["checks"])

        # L2: 风险评估
        risk = self._risk_assessment()

        # 记录
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checkpoint": checkpoint_type,
            "triggered": decision["triggered"],
            "reason": decision["reason"],
            "mechanical_ok": all_pass,
            "risk_score": risk.get("risk_score"),
            "risk_level": risk.get("risk_level"),
        }
        self._write_log(entry)

        # L3: 模型原生提示词
        prompt = self._build_model_native_prompt(mechanical, risk)

        # 分级遏制 exit code (inspired by ABC graduated containment)
        rlevel = risk.get("risk_level", "UNKNOWN")
        if not all_pass:
            exit_code = 2   # L1机械门失败→硬阻断
        elif rlevel in ("HIGH", "CRITICAL"):
            exit_code = 2   # 高风险→硬阻断
        elif rlevel == "ELEVATED":
            exit_code = 1   # 警告→hook决定
        else:
            exit_code = 0   # LOW/MODERATE→正常

        return {**decision, "mechanical": mechanical, "risk": risk,
                "model_prompt": prompt, "exit_code": exit_code,
                "action_required": risk.get("action_required", "unknown")}

    # ── L1 机械检查 ─────────────────────────────────────────────────

    def _mechanical_checks(self) -> dict:
        checks = []
        settings = self.config_dir / "settings.json"

        # hook wiring
        if settings.exists():
            try:
                data = json.loads(settings.read_text(encoding="utf-8"))
                n = sum(len(v) if isinstance(v, list) else 1
                        for v in data.get("hooks", {}).values())
                checks.append({"name": "hook_wiring", "pass": n > 3,
                               "detail": f"{n} hooks"})
            except Exception:
                checks.append({"name": "hook_wiring", "pass": False,
                               "detail": "unreadable"})

        # core configs
        for name in ["CLAUDE.md", "SOUL.md", "BODY.md"]:
            p = self.config_dir / name
            checks.append({"name": f"config_{name}",
                           "pass": p.exists(),
                           "detail": "exists" if p.exists() else "MISSING"})

        # quality-gate
        qg = self.config_dir / "scripts" / "quality-gate.py"
        checks.append({"name": "quality_gate", "pass": qg.exists(),
                       "detail": "exists" if qg.exists() else "MISSING"})

        # self-model freshness
        sm = Path(os.path.expanduser(
            "~/.claude/projects/C--Users-86131/memory/self-model.md"))
        if sm.exists():
            days = (datetime.now() - datetime.fromtimestamp(sm.stat().st_mtime)).days
            checks.append({"name": "self_model_age", "pass": days <= 5,
                           "detail": f"{days}d old"})
        else:
            checks.append({"name": "self_model_age", "pass": False,
                           "detail": "MISSING"})

        return {"checks": checks, "pass_count": sum(1 for c in checks if c["pass"]),
                "total": len(checks)}

    # ── L2 风险评估 ─────────────────────────────────────────────────

    def _risk_assessment(self) -> dict:
        try:
            from drift_predictor import DriftPredictor
            p = DriftPredictor()
            return p.compute_risk(p.collect_features())
        except ImportError:
            return {"risk_score": None, "risk_level": "UNKNOWN"}

    # ── L3 模型原生提示词 ───────────────────────────────────────────

    def _build_model_native_prompt(self, mechanical: dict, risk: dict) -> str:
        """
        人类逻辑→模型注意力格式。

        设计原则:
        - 三段论: 大前提(系统状态) → 小前提(具体发现) → 结论(行动要求)
        - 关键词锚点: [periodic-audit-pass/fail] → logprob 差分可检测
        - 不要求"理解审计" → 只路由注意力到风险点
        """
        failed = [c for c in mechanical["checks"] if not c["pass"]]
        score = risk.get("risk_score")

        # L2风险评估不可用时，仅报告L1机械门状态
        if score is None:
            prompt = (
                f"大前提：定期自审完成（仅L1机械门）。{mechanical['pass_count']}/"
                f"{mechanical['total']} 项通过。L2风险评估不可用：drift_predictor模块未加载。\n"
            )
            if failed:
                prompt += "小前提：以下项未通过——系统完整性已受损：\n"
                for f in failed:
                    prompt += f"  · {f['name']}: {f['detail']}\n"
                prompt += "结论：下一轮前必须修复。未修复 → 禁止 Edit/Write。\n"
            else:
                prompt += "小前提：L1机械门全部通过。结论：无风险评估，操作需手动审慎。\n"
            status = "fail" if failed else "pass"
            prompt += f"[anchor:periodic-audit:{status} score=N/A l2-unavailable]"
            return prompt

        prompt = (
            f"大前提：定期自审完成。{mechanical['pass_count']}/{mechanical['total']} "
            f"项通过，Drift Risk = {score}/100。\n"
        )

        if failed:
            prompt += "小前提：以下项未通过——系统完整性已受损：\n"
            for f in failed:
                prompt += f"  · {f['name']}: {f['detail']}\n"
            prompt += "结论：下一轮前必须修复。未修复 → 禁止 Edit/Write。\n"
        elif score > 40:
            prompt += (
                f"小前提：风险偏高（>{risk.get('baseline_with_gate', 1)} 基准）。"
                "结论：本轮操作需 Read→确认→再 Write。\n"
            )
        else:
            prompt += "小前提：机械门覆盖率良好。结论：风险可控，正常操作。\n"

        # 关键词锚点——激活 L3 注意力路由 + 便于 v1 回响检测
        status = "fail" if failed else "pass"
        prompt += f"[anchor:periodic-audit:{status} score={score}]"
        return prompt

    # ── 辅助 ─────────────────────────────────────────────────────────

    def _last_audit_time(self):
        if not AUDIT_LOG.exists():
            return None
        try:
            lines = [l for l in AUDIT_LOG.read_text(encoding="utf-8").split("\n") if l.strip()]
            if not lines:
                return None
            return datetime.fromisoformat(json.loads(lines[-1])["timestamp"])
        except Exception:
            return None

    def _count_recent_compacts(self) -> int:
        """自上次审计以来 /compact 事件数。JSONL解析避免'compact'子串误匹配（同上D2修复）。"""
        last = self._last_audit_time()
        hist = self.config_dir / "history.jsonl"
        if not hist.exists():
            return 0
        try:
            n = 0
            for line in hist.read_text(encoding="utf-8").strip().split("\n"):
                try:
                    d = json.loads(line)
                    if d.get("display", "").strip() != "/compact":
                        continue
                    ts = datetime.fromisoformat(d.get("timestamp", ""))
                    if last and ts > last:
                        n += 1
                    elif not last:
                        n += 1
                except Exception:
                    pass
            return n
        except Exception:
            return 0

    def _tool_config_hash(self) -> str:
        """Hash settings.json中影响行为的关键子集(hooks+permissions+核心参数+MCP/插件)。排除metadata/timestamp等噪音字段。"""
        s = self.config_dir / "settings.json"
        if not s.exists():
            return "none"
        try:
            d = json.loads(s.read_text(encoding="utf-8"))
            # 只hash影响agent行为的字段，排除时间戳/描述等噪音
            relevant = {}
            for key in ["hooks", "permissions", "enabledMcpjsonServers",
                        "enabledPlugins", "autoCompactWindow"]:
                if key in d:
                    relevant[key] = d[key]
            raw = json.dumps(relevant, sort_keys=True)
            return f"{hash(raw) & 0xFFFFFFFF:08x}"
        except Exception:
            return "error"

    def _last_audit_tool_hash(self) -> str:
        if not AUDIT_LOG.exists():
            return ""
        try:
            lines = [l for l in AUDIT_LOG.read_text(encoding="utf-8").split("\n") if l.strip()]
            for line in reversed(lines):
                return json.loads(line).get("tool_hash", "")
        except Exception:
            return ""

    def _write_log(self, entry: dict):
        """写审计日志。SHA256链式防篡改(inspired by Nautilus Compass Merkle log)。旧条目无hash向后兼容。"""
        entry["tool_hash"] = self._tool_config_hash()

        # Hash链: 上一条的SHA256 → prev_hash, 本条内容SHA256 → entry_hash
        prev_hash = "genesis"
        if AUDIT_LOG.exists():
            try:
                lines = [l for l in AUDIT_LOG.read_text(encoding="utf-8").split("\n") if l.strip()]
                if lines:
                    prev_hash = hashlib.sha256(lines[-1].encode("utf-8")).hexdigest()[:16]
            except Exception:
                prev_hash = "legacy"
        entry["prev_hash"] = prev_hash

        # 条目hash: 不含hash字段本身的内容
        content_for_hash = json.dumps(
            {k: v for k, v in entry.items() if k not in ("prev_hash", "entry_hash")},
            sort_keys=True, ensure_ascii=False
        )
        entry["entry_hash"] = hashlib.sha256(content_for_hash.encode("utf-8")).hexdigest()[:16]

        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── CLI ────────────────────────────────────────────────────────────────

def main():
    import argparse
    p = argparse.ArgumentParser(description="Periodic Self-Audit")
    p.add_argument("--checkpoint", default="scheduled",
                   choices=["scheduled", "compact", "tool_change", "force"])
    p.add_argument("--json", action="store_true")
    p.add_argument("--prompt-only", action="store_true")
    args = p.parse_args()

    audit = PeriodicAudit()
    result = audit.run_audit(args.checkpoint)

    if args.prompt_only:
        print(result["model_prompt"])
        return

    if args.json:
        print(json.dumps({
            "checkpoint": result["checkpoint"],
            "triggered": result["triggered"],
            "reason": result["reason"],
            "exit_code": result["exit_code"],
            "action_required": result.get("action_required"),
            "mechanical": f"{result['mechanical']['pass_count']}/"
                          f"{result['mechanical']['total']}",
            "risk_score": result["risk"].get("risk_score"),
        }, ensure_ascii=False))
    else:
        print(f"═══ Periodic Audit [{args.checkpoint}] ═══")
        print(f"触发: {'是' if result['triggered'] else '否'} — {result['reason']}")
        print(f"机械: {result['mechanical']['pass_count']}/"
              f"{result['mechanical']['total']} [exit {result['exit_code']}]")
        if result["risk"].get("risk_score") is not None:
            print(f"风险: {result['risk']['risk_score']}/100 "
                  f"[{result['risk'].get('risk_level')}]")
            print(f"行动: {result.get('action_required', 'unknown')}")
        print(f"\n── 模型原生提示 ──")
        print(result["model_prompt"])

    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()
