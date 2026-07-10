# Paper Materials — AI Agent Self-Verifying Configuration Integrity

> 林宇浩, 大三, FAFU 空间信息. 2026-07-10.
> For professor review.

## 给老师的阅读指引

**如果您只有 5 分钟** → 读这篇：
→ **[professor-meeting-onepager.md](professor-meeting-onepager.md)** — 做了什么、发现了什么、局限在哪、想问什么

**如果您想了解理论框架** → 接着读：
→ **[paper-outline-part1.md](paper-outline-part1.md)** — 论文大纲 + Part 1（文件系统层）+ Part 2（神经层）+ 竞品分析

**如果您想看数据和方法** → 再深入：
→ [paper-methods-draft.md](paper-methods-draft.md) — 实验设计、架构、统计方法
→ [paper-trial-results.md](paper-trial-results.md) — 12 次 treatment trial 原始数据
→ [paper-task-specs.md](paper-task-specs.md) — 30 个任务规格（5 领域）
→ [paper-scoring-template.md](paper-scoring-template.md) — 评分模板（5 分类 + 3 门）

**如果您想了解突破点** → 最近两篇：
→ [A-devto-prose-barrier.md](A-devto-prose-barrier.md) — Prose Barrier：为什么 AI agent 无法自验证（EN, 已发 DEV.to）
→ [B-devto-neural-gate.md](B-devto-neural-gate.md) — 神经门：验证的第二层（EN, 已发 DEV.to）

**背景材料**：
→ [self-model.md](self-model.md) — 系统自我模型 v0.10（经过 5 位专家多轮审查）
→ [paper-revision-plan-v2.md](paper-revision-plan-v2.md) — 专家团完整修订方案
→ [paper-experiment-expansion.md](paper-experiment-expansion.md) — 统计效力分析、n=60 目标、双盲方案

## 核心贡献（一句话）

机械检查（mtime、regex、exit code、hook wiring）能检测和防止 AI agent 配置漂移，不依赖 AI 自我评估——因为 agent 无法可靠判断自身配置完整性。

## 突破：双层架构

| 层 | 检查什么 | 状态 |
|---|---------|:--:|
| 文件系统层 | 信息到达了吗？ | 4 gate 部署 |
| 神经层 | 信息穿透了吗？ | v1 部署, v2 设计, v3 路线图 |

哲学家和 AI 架构师从不同前提独立收敛到同一拓扑。

## 诚实状态

- 系统：可用，4 机械检查 + 1 神经检查运行中
- 数据：初步（单人评分、非盲法、无安慰剂对照——我知道）
- 声称：值得做更严格的对照实验，**不是**"已被证明有效"
- 需求：方向判断 + 投稿建议 + 可能的话，指导

## 仓库链接

- [hermes-workspace](https://github.com/YuhaoLin2005/hermes-workspace) — 主仓库（架构 + 论文材料）
- [digital-twin-trainer](https://github.com/YuhaoLin2005/digital-twin-trainer) — QLoRA 行为内化实验
- [compact-counter](https://github.com/YuhaoLin2005/compact-counter) — 上下文压缩计数追踪
- DEV.to: [dev.to/yuhaolin2005](https://dev.to/yuhaolin2005)
- 掘金: [juejin.cn/user/4250072430682412](https://juejin.cn/user/4250072430682412)
