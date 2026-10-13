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
4. **平台核验 = 一条命令，不开浏览器**（2026-10-12 用户裁决「API 为主」）——`python knowledge/_platform_verify.py`。
   实测两个公开 API 都给计数 + 聚合数（dev.to: views/reactions/comments；掘金: view/digg/collect/comment）。
   **唯一 API 拿不到的是 dev.to followers** —— 放弃自动核，**需要时向用户要**（他说需要时会去找）。
   `--write` 回写两个索引的 `platform_published` / `last_verified`；`dashboard.md` 聚合块因存在
   **同名不同物**（如 dev.to dashboard 自身 nav 621 vs analytics 0/690）**不自动改**，先 `--json` 核口径。
   计数与索引头部对不上 = ERROR（检查 2f）。⛔ 旧流程（内容管理→文章管理 / 数据中心→内容数据 / 单篇分析，14 天一次浏览器登录）**已废弃**。

## 核心原则

- 数字分身管"加载什么" → routing.md
- 策略引擎管"做什么" → strategy/
- 双池专家团管"够不够好" → 设计/执行/收尾三阶段介入
- 一切为量化指标服务 → dashboard.md 是单一真相来源

*最后更新: 2026-07-19*
