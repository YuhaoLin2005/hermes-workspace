# Agent 配置漂移外部机械校验体系研究

> 林宇浩, 福建农林大学 2023级 空间信息与数字技术专业. 2026-07-10.

## 课题摘要

**课题定义**：Agent 配置漂移（Configuration Drift）指 LLM 智能体在长上下文多轮交互下，预设执行规则、约束范式、自我认知出现持续性、系统性偏移。该现象由模型解码分布的原生架构约束导致——Agent 的自我评估与任务执行共享同一概率分布 P(token|context;θ)，不存在独立验证通道，无法通过提示词优化根除。

**核心创新**：摒弃模型自校验闭环，搭建独立于大模型的外部客观校验通道，依托文件时间戳、正则匹配、进程退出码等程序底层可量化指标拦截漂移偏差。双层架构——文件系统层校验"信息到达"，神经层校验"规则穿透"。

**现存局限**：硬件仅单张 RTX 3060，无法开展多模型消融实验；实验执行与评分单人完成，无双盲机制与安慰剂对照组；底层理论体系碎片化，缺乏系统科研方法训练。

---

## 现有研究竞品短板

当前 LLM Agent 可靠性研究聚焦以下路线，均未覆盖配置层的外部客观校验：

| 技术路线 | 代表工作 | 核心局限 |
|---------|---------|---------|
| Prompt 工程优化 | 记忆池注入、上下文压缩 | 规则仍依赖 Agent 自我理解执行，无法强制校验 |
| 独立评估 Agent | RIVA、GLOVE | 新增独立 LLM 做校验，成本高、存在二次漂移风险 |
| 记忆增强方案 | Mem0、Letta、ASF | 仅注入记忆，不验证行为合规性 |
| 代码层自修改 | HyperAgents (Meta, ICLR 2026) | 操作代码层，不解决配置/规则层漂移 |

本课题的差异化定位：**无模型参与、可量化、可复现的外部机械校验**，填补了"不依赖 LLM 自评、不新增独立 Agent、低成本本地部署"的技术空白。

---

## 阅读指引

### 5分钟：课题概览

→ **[professor-meeting-onepager.md](professor-meeting-onepager.md)**
研究问题定义、自研方案概述、30组对照实验趋势、诚实局限性说明、咨询诉求。

### 15分钟：论文框架与理论深化

→ **[paper-outline-part1.md](paper-outline-part1.md)**
完整论文大纲（Introduction→Related Work→Architecture→Experiments→Discussion→Conclusion），Part 1 文件系统层设计，Part 2 神经层三阶段方案（v1关键词回响/v2 logprob差异/v3残差流探针），竞品对比，已识别局限与待办清单。

### 30分钟：实验数据与方案细节

→ **[paper-methods-draft.md](paper-methods-draft.md)** — 架构设计、实验范式、统计方法
→ **[paper-trial-results.md](paper-trial-results.md)** — 8次 treatment trial 原始记录，含 validity caveats
→ **[paper-task-specs.md](paper-task-specs.md)** — 30个标准化编程任务规格，5领域分类
→ **[paper-scoring-template.md](paper-scoring-template.md)** — 5分类+3门评分标准框架

### 神经层突破方案

文件系统层仅解决"信息到达性"，不解决"规则穿透率"。因为在 transformer 架构下，Agent 的自我认知叙述与任务执行共享同一解码分布——声明"我能做 X"与执行 X 两个动作从同一分布采样。此结构性约束提示：验证必须发生在信息实际流动的层面。

→ **[paper-outline-part1.md](paper-outline-part1.md)** Part 2 章节——神经层三阶段方案：
- **v1（已部署）**：约束关键词回响检测——86行 Python，8个约束主题，全通过
- **v2（已设计）**：Logprob 差异检测——带/不带约束提示的 token 概率偏移对比，脚本完成待 API key
- **v3（路线图）**：残差流线性探针——Qwen2.5-1.5B（RTX 3060 可行），训练探针检测约束信息可解码性

→ **[B-devto-neural-gate.md](B-devto-neural-gate.md)** — 英文技术博文，神经门完整方案（已发 DEV.to）

→ **[A-devto-prose-barrier.md](A-devto-prose-barrier.md)** — 英文技术博文，自校验分布悖论论述（已发 DEV.to）

### 背景材料

→ **[self-model.md](self-model.md)** — 系统自我认知文档 v0.10，记录 50+轮架构演进。⚠️ 此文档为 AI 辅助写成的内省记录，非客观研究报告
→ **[paper-revision-plan-v2.md](paper-revision-plan-v2.md)** — 多轮专家审查后完整修订方案
→ **[paper-experiment-expansion.md](paper-experiment-expansion.md)** — 统计效力分析、n=60 目标、双盲方案设计

---

## 研究现存瓶颈

本课题从问题发现、方案设计、原型开发到实验落地均由个人独立完成，当前已触达自学模式的能力上限：

1. **硬件资源约束**：仅单张 RTX 3060 显卡，无法开展多模型消融对照、大样本定量实验，缺失横向对比数据
2. **实验范式不标准**：实验执行、效果测评、数据统计均由单人完成，缺少同行交叉核验机制（双盲评分、Cohen's Kappa），主观偏差无法剥离，实验结论可信度不足
3. **理论体系碎片化**：依靠自主检索与 AI 辅助查阅文献，缺乏系统的大模型底层理论、标准化科研实验设计训练，难以严谨论证架构相关假设，无法清晰界定课题创新学术价值

---

## 相关仓库

- [hermes-workspace](https://github.com/YuhaoLin2005/hermes-workspace) — 主仓库（架构设计 + 论文材料）
- [digital-twin-trainer](https://github.com/YuhaoLin2005/digital-twin-trainer) — QLoRA 行为内化实验
- [compact-counter](https://github.com/YuhaoLin2005/compact-counter) — 上下文压缩计数追踪
- DEV.to: [dev.to/yuhaolin2005](https://dev.to/yuhaolin2005)
- 掘金: [juejin.cn/user/4250072430682412](https://juejin.cn/user/4250072430682412)
