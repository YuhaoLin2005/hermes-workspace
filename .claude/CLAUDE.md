# Hermes Workspace — Project Config

## 启动

1. 读 `routing.md` → 数字分身路由表（策略决策引擎 + 路由规则 + 启动序列）
2. 按路由表 §Session 启动序列 加载策略层 + 知识层 + 规则层
3. 策略引擎输出"今天做什么" → 开始工作

## 收尾

按 `routing.md` §收尾规则：
1. 更新 `knowledge/strategy/dashboard.md` 对应数字
2. 实验/文章/PR 完成 → 更新对应 pipeline + KB
3. 跑 `python knowledge/_check_kb.py` → 确认 PASS

## 核心原则

- 数字分身管"加载什么" → routing.md
- 策略引擎管"做什么" → strategy/
- 双池专家团管"够不够好" → 设计/执行/收尾三阶段介入
- 一切为量化指标服务 → dashboard.md 是单一真相来源

*最后更新: 2026-07-19*
