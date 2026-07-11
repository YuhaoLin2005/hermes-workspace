# 林宇浩 · 个人能力全景文档

> 最后更新：2026-07-11
>
> 用途：简历素材库 / 面试准备 / 个人定位参考。按需抽取，不直接当简历投。

---

## 基本信息

| 项 | 内容 |
|------|------|
| 姓名 | 林宇浩 (Yuhao Lin) |
| 学校 | 福建农林大学 (FAFU) |
| 专业 | 空间信息与数字技术 |
| 年级 | 2023 级（大三） |
| 方向 | HCI · AI Systems · LLM Agent Reliability |
| 研究状态 | 独立研究，无导师/无实验室 |
| GitHub | [github.com/YuhaoLin2005](https://github.com/YuhaoLin2005) |
| DEV.to | [dev.to/yuhaolin2005](https://dev.to/yuhaolin2005) |
| 掘金 | [juejin.cn/user/4250072430682412](https://juejin.cn/user/4250072430682412) |
| 硬件 | Dell G15 5520 · i7-12700H · RTX 3060 6GB · 16GB RAM · 512GB NVMe |

---

## 一句话定位

**独立构建 LLM Agent 配置漂移检测与自校验系统，完成 150 任务对照实验，组件已合并至 228k★ 开源项目。**

---

## 核心研究：Agent 配置完整性自校验

### 问题

AI coding agent 长对话中遗忘规则、产出物缺验证、自我认知漂移——现有方案依赖 AI 自评（不可靠），因为生成和验证共享同一解码器分布。

### 核心理论贡献：Prose Barrier

> LLM 的生成和自评共享同一解码器 P(token|context;θ) — 不存在独立验证通道。因此 **agent 自校验在结构上不可能**，这不是实现质量问题，是架构约束。

### 方案：三层架构

| 层 | 机制 | 状态 |
|:--:|------|:--:|
| L1 机械门 | 文件时间戳/正则/exit 2 硬阻断 — 绕过 AI 自评偏差 | ✅ 已部署 + 实验验证 |
| L2 神经门 | 关键词回响→logprob差分→残差流探针 | 📐 v1 已部署, v2/v3 已设计 |
| L3 因果编码 | 三段论格式→注意力路由→推理深度 | 🗺️ 路线图, 初步证据 |

### 实验

| 实验 | N | 设计 | 关键结果 | 文件 |
|------|:--:|------|------|------|
| Growth-log 回溯 | 34 sessions | 纵向编码, 单编码者 | 违规率 55.9%→0.7% | [paper/experiment/](https://github.com/YuhaoLin2005/hermes-workspace/tree/main/paper/experiment) |
| Causal Swap | 30 tasks | Between-subjects, 15+15, DeepSeek V4 Pro | OR=11.0, p=0.0092 (Fisher exact) | [PAPER.md §4](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/PAPER.md) |
| Format A/B | **150 tasks** | Between-subjects, 75+75, 6 sessions | 99.3% 合规率, 天花板效应 | [experiment-results](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/experiment/experiment-results-2026-07-11.md) |
| Syllogism 交叉验证 | 4 sessions | 5规则全触发, 零违规+涌现主动审计 | 格式→推理深度因果链初步 | [PAPER.md §6-7](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/PAPER.md) |

> ⚠️ 诚实标注：所有定量结果由作者单人评分、非盲法。盲审信度检查 κ=-0.14 (n=8, 未通过)。已在论文和所有对外材料中明确标注。

### 论文

- 完整论文：[PAPER.md](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/PAPER.md)（三部曲：机械门 + 神经门 + 因果编码）
- 教授摘要：[professor-meeting-onepager.md](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/professor-meeting-onepager.md)
- AI 模拟审稿报告：[reviewer-report-2026-07-11.md](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/reviewer-report-2026-07-11.md)
- 发表目标：arXiv 预印本 → ACL SRW / CHI LBW

---

## 技术项目

### ⭐ hermes-workspace — 论文三部曲主仓库

- **角色**：独立作者 + 实验设计者 + 系统架构师
- **技术栈**：Claude Code Hooks, Python (标准库), DeepSeek V4 Pro API, Git
- **亮点**：
  - 设计并实现 7 类机械门（文件时间戳/正则/exit code/hook 接线检测/规则空转检测/配置一致性校验/产出物完整性校验）
  - 自指环 (strange loop)：quality-gate.py → health-check.py → LLM 再生 self-model → log-regeneration.py → quality-gate.py 闭合
  - 双池审查系统 (Named-Persona Adversarial Review)：3 视角交叉审查替代多 agent
  - 60+ Python 工具脚本（hook 系统 + 质量门 + 审查工具）
- **仓库**：[github.com/YuhaoLin2005/hermes-workspace](https://github.com/YuhaoLin2005/hermes-workspace)

### digital-twin-trainer — QLoRA 行为内化实验

- **角色**：独立实现
- **技术栈**：PyTorch, QLoRA (bitsandbytes 4-bit + PEFT), Qwen2.5-1.5B, HuggingFace Transformers
- **核心发现**：253 样本微调→loss 下降但行为质量崩塌→微调需要行为级评测指标，不能只看 loss
- **产出**：behavioral_drift 指标（已提交 HuggingFace evaluate PR #778）
- **仓库**：[github.com/YuhaoLin2005/digital-twin-trainer](https://github.com/YuhaoLin2005/digital-twin-trainer)

### compact-counter — 上下文压缩 sweet-spot 检测

- **角色**：独立开发
- **技术栈**：Python 标准库
- **核心发现**：LLM 上下文压缩并非线性——过早压缩**反而改善**输出质量。工具检测不同模型的 sweet-spot
- **仓库**：[github.com/YuhaoLin2005/compact-counter](https://github.com/YuhaoLin2005/compact-counter)

---

## 开源贡献

### 上游 PR（已合并）

| 仓库 | Stars | PR 内容 | 状态 |
|------|:--:|------|:--:|
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | 228k | delivery-gate Stop hook + growth-log skill — 完整工程组件 | ✅ 已合并 |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | 22k | #867 对抗性审查 skill（维护者主动给予 Co-authored-by 署名） | ✅ 已合并 |

### 上游 PR（审查中）

| 仓库 | PR 内容 | 状态 |
|------|------|:--:|
| [anthropics/skills](https://github.com/anthropics/skills) | quality-gate + adversarial review 提案 | 🔄 与维护者讨论中 |
| [HuggingFace/evaluate](https://github.com/huggingface/evaluate) | #778 behavioral_drift 指标 | 🔄 Pending review |

### 独立工具（已开源）

| 仓库 | 描述 | Stars |
|------|------|:--:|
| [gategrow](https://github.com/YuhaoLin2005/gategrow) | 确定性质量门禁（已合并入 ECC 228k★） | — |
| [training-gate](https://github.com/YuhaoLin2005/training-gate) | 微调行为漂移检测 | — |
| [imprint](https://github.com/YuhaoLin2005/imprint) | AI identity continuity protocol — 文件系统级会话持久化 | — |
| [pre-pr-check](https://github.com/YuhaoLin2005/pre-pr-check) | PR 提交前质量检查工具 | — |
| [compact-counter-concept](https://github.com/YuhaoLin2005/compact-counter-concept) | 上下文压缩理论分析 | — |
| [open-source-flywheel](https://github.com/YuhaoLin2005/open-source-flywheel) | 个人 OSS 贡献方法论 | — |
| [deepseek-claude-code-starter](https://github.com/YuhaoLin2005/deepseek-claude-code-starter) | DeepSeek V4 + Claude Code 脚手架 | 2 |
| [gis-map-story](https://github.com/YuhaoLin2005/gis-map-story) | 交互式 GIS 叙事地图 (Baidu Maps WebGL API) | — |

---

## 技术写作

### DEV.to（英文，2026 年 7 月）

| 文章 | 链接 | 内容 |
|------|------|------|
| AI Agents Can't Self-Verify | [dev.to](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) | Prose Barrier 理论 — 为什么 AI 自校验在结构上不可能 |
| I Built a Neural Gate | [dev.to](https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2) | 神经门三阶段方案设计 |
| 150 Tasks to Test AI Agents | [dev.to](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) | 150 任务对照实验完整报告 |

### DEV.to（早期）

| 文章 | 链接 |
|------|------|
| Meta-Cognition / RAG vs Internalization | [dev.to](https://dev.to/yuhaolin2005/meta-cognition-is-the-future-of-ai-personalization-a-4-quadrant-framework-to-build-it-5fki) |
| Behavioral Drift Metric | [dev.to](https://dev.to/yuhaolin2005/my-loss-went-down-but-my-model-still-broke-so-i-built-a-drift-metric-e8f) |

### 掘金（中文版对应）

- J-space 独立复现：[juejin.cn/post/7659251094817341490](https://juejin.cn/post/7659251094817341490)
- 全部中文文章：[juejin.cn/user/4250072430682412](https://juejin.cn/user/4250072430682412)

---

## 技能详表

### LLM / AI 系统工程

| 技能 | 熟练度 | 证据 |
|------|:--:|------|
| Claude Code Hooks 架构 | ★★★★★ | 7 类机械门 + 自指环 + 双池审查系统 |
| Prompt Engineering | ★★★★☆ | 三段论格式设计 + 命令式规则 + 30 任务规格化 |
| Agent 架构设计 | ★★★★☆ | 三层架构 (L1/L2/L3) + 五层拓扑 (SOUL→INTERFACE→BODY→MEMORY→Feedback) |
| DeepSeek API | ★★★★☆ | Anthropic 兼容端点 + 成本优化 (50-70% 预期节省) |
| API 缓存策略 | ★★★★☆ | 自动前缀缓存机制 + ToolSearch Bug 诊断 + cache_control 适配 |
| QLoRA 微调 | ★★★☆☆ | bitsandbytes 4-bit + PEFT + Qwen2.5-1.5B + 253 样本 |
| HuggingFace 生态 | ★★★☆☆ | Transformers / PEFT / evaluate (PR #778) / datasets |

### 实验设计与统计

| 技能 | 熟练度 | 证据 |
|------|:--:|------|
| Between-subjects 设计 | ★★★★☆ | 30 task Causal Swap + 150 task Format A/B |
| 纵向编码 | ★★★★☆ | 34 growth-log session 系统性编码 |
| Fisher Exact Test | ★★★☆☆ | p=0.0092, OR=11.0 计算与解释 |
| Cohen's κ | ★★★☆☆ | 评分信度检查, κ=-0.14 诚实报告 |
| 评分量表设计 | ★★★★☆ | Cat 1-5 五级评分 + 操作定义手册 |
| 实验文档化 | ★★★★★ | 任务规格 / 评分模板 / 操作定义 / 配置快照 全套 |

### Python

| 技能 | 熟练度 | 证据 |
|------|:--:|------|
| 标准库开发 | ★★★★★ | 60+ CLI 工具脚本, 零外部依赖 |
| PyTorch | ★★★☆☆ | QLoRA 微调 + 训练循环 + 行为评测 |
| HuggingFace | ★★★☆☆ | evaluate 指标开发 + Transformers 训练 |
| CLI 设计 | ★★★★☆ | 统一 JSON + 人类可读输出, 完整 help/--version |

### 工具与基础设施

| 技能 | 熟练度 |
|------|:--:|
| Git / GitHub | ★★★★★ |
| VS Code | ★★★★☆ |
| Jupyter | ★★★☆☆ |
| Bash (Git Bash on Windows) | ★★★★☆ |
| Windows 开发环境配置 | ★★★★☆ |

### 写作与沟通

| 技能 | 熟练度 | 证据 |
|------|:--:|------|
| 学术论文写作 | ★★★☆☆ | PAPER.md (markdown), 标准论文结构 (Abstract→Related Work→Methods→Results→Discussion) |
| 技术博客 (英文) | ★★★★☆ | 5 篇 DEV.to 文章 |
| 技术博客 (中文) | ★★★★☆ | 3+ 篇掘金文章 |
| 英文技术读写 | ★★★★☆ | 独立文献检索 + 论文阅读 + DEV.to 写作 |
| 双语技术沟通 | ★★★★☆ | 中英文材料互翻 + 并行维护 |

---

## 方法论与工作流

### 自指环 (Strange Loop)

```
quality-gate.py  → 检测 self-model 过期
health-check.py  → SessionStart 读取 flag
LLM 合成再生     → 重写 self-model.md（3 版本轮转）
log-regeneration → 删 flag + 机械日志
quality-gate.py  → 下次收尾再次检测 ...（闭合）
```

5 步中 4 步已机械化，1 步需 AI（内容再生）——"奇异环"闭合。

### 双池审查系统

Named-Persona Adversarial Review — 补偿单模态 LLM 盲区：
- 联网搜索真实工程师画像 → 角色扮演多视角审查 → CRITICAL/WARNING/NOTE 报告
- 每次审查 ≥3 轮，每轮换人物组合
- 不依赖多 agent（成本更低、更可控）

### 开放源码贡献飞轮 (Open-Source Flywheel)

```
个人工具 → 发现互补缺口 → PR 审查硬化 → 独立贡献
验证案例：delivery-gate / self-audit / RapidOCR
```

### 质量基础设施

- **7 类机械门**：文件时间戳/正则匹配/进程退出码/hook 接线检测/规则空转检测/配置一致性/产出物完整性
- **3 道 PreToolUse 审查**：three-questions-guard + execution-gate + pre-edit-guard
- **2 道 PostToolUse 验证**：fact-check-hook + mid-session-check
- **8 道 Stop 收尾**：config-health / usage-tracker / quality-gate / honesty-check / heartbeat / review-logger / claim-gate / neural-gate

---

## 项目时间线

| 时间 | 里程碑 |
|------|------|
| 2026-06 | 启动 hermes-workspace · 发现 Agent 配置漂移问题 |
| 2026-06 | 五层拓扑架构 (SOUL→INTERFACE→BODY→MEMORY→Feedback) |
| 2026-06 | 双池审查系统 v1.0 · quality-gate.py 上线 |
| 2026-06 | ECC delivery-gate PR 提交 |
| 2026-07-01 | Causal Swap 30 task 实验完成 (OR=11.0, p=0.0092) |
| 2026-07-04 | ECC PR 合并 · claude-skills PR #867 Co-authored-by 合并 |
| 2026-07-06 | behavioral_drift 指标 · HF evaluate PR #778 提交 |
| 2026-07-09 | Format A/B 150 task 实验完成 (99.3% 合规率) |
| 2026-07-10 | 系统审计 — 53→15 HOT 记忆精简 · 9 CRITICAL 修 7 |
| 2026-07-11 | 论文冷读审查 ×4 · 教授邮件 · PAPER.md 完整修订 |
| 2026-07-11 | DeepSeek V4 成本优化 — 9 参数调优, 50-70% 预期节省 |
| 2026-07-11 | 个人品牌梳理 — 双语 Profile + 仓库描述 + 能力全景文档 |

---

## 当前局限与成长方向

### 诚实自评

| 局限 | 影响 | 改进方向 |
|------|------|------|
| 无导师/无实验室 | 缺方法论训练、文献覆盖不系统 | 寻求教授指导 (已发邮件) |
| 独立评分 (κ=-0.14) | 实验结论需外部验证 | 找第二评分者 + 安慰剂对照 |
| RTX 3060 6GB | 无法多模型消融、v3 探针受限于 1.5B | 升级硬件或使用云 GPU |
| 文献盲区 | 漏引 Self-consistency / Reflexion / DSPy 等基础文献 | 系统文献综述 |
| 英文学术写作 | 论文当前是 markdown 碎片，非 LaTeX 单文件 | 撰写完整 LaTeX 稿件 |

### 期望发展方向

- **短期**：完成 ACL SRW / CHI LBW 投稿 · 找导师 · 实习
- **中期**：多模型消融实验 · 神经门 v3 残差流探针 · 第二评分者验证
- **长期**：HCI + AI Systems 交叉方向研究生 · Agent Reliability 持续研究

---

## 代表性工作样本（面试可展示）

1. **[PAPER.md](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/PAPER.md)** — 完整论文，展示研究思维完整链条
2. **[experiment-results-2026-07-11.md](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/experiment/experiment-results-2026-07-11.md)** — 150 任务原始数据，展示实验严谨性
3. **[DEEPSEEK_OPTIMIZATION.md](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/experiment/DEEPSEEK_OPTIMIZATION.md)** — 成本优化分析，展示工程思维
4. **[reviewer-report-2026-07-11.md](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/reviewer-report-2026-07-11.md)** — 审稿级自我诊断，展示学术诚实
5. **ECC delivery-gate PR** — 合并至 228k★ 项目的完整工程组件
6. **DEV.to 三篇** — 技术沟通能力

---

*本文档由 Claude Code (DeepSeek V4 Pro) 辅助整理，内容基于实际项目产出。*
