# Agent 配置漂移：外部机械校验体系

> 林宇浩，福建农林大学 · 空间信息与数字技术 2023 级 · 2026 年 7 月
>
> **一句话**：AI agent 长对话中规则被遗忘、产出物缺验证、自我认知失真。现有方案依赖 AI 自评（不可靠），本文提出脱离 AI 的机械校验，150 任务实验验证。

---

## 阅读指引（给凯斌老师）

### 5 min · 抓核心

→ **[professor-meeting-onepager.md](professor-meeting-onepager.md)**
问题 / 方案 / 数据 / 局限 / 请教事项。

### 15 min · 读论文

→ **[../PAPER.md](../PAPER.md)** （仓库根目录）
三部曲完整论文：Part 1 机械门 → Part 2 神经门 → Part 3 因果编码。含 §4 Causal Swap 实验 (n=30, p=0.0092) + §6.5 Format A/B 实验 (n=150)。

### 30 min · 对竞品 + 查实验

→ **[paper-outline-part1.md](paper-outline-part1.md)** — 文献定位（HyperAgents / Prompt Decorators / Constitutional AI / Pender 2026）

实验数据与协议文件：
→ **[experiment/](experiment/)** 目录
- `experiment-results-2026-07-11.md` — 150 task, 6 session 对照实验原始数据
- `systematic-baseline-coding.md` — 34 growth-log 回溯编码方法与结果
- `reviewer-priority-4-5-protocol.md` — 独立实验方法学家审查意见与修订
- `experiment-execution-guide.md` — 实验执行指南 v2.0（含操作定义手册）

---

## 外部验证

### 开源社区 PR（2026-07）

工程组件（delivery-gate、config-health、aeo-box）已向上游提交并获认可：
- **ECC 仓库**（affaan-m/ECC）：2 个 PR 已合并，1 个已通过维护者审批待合并
- **alirezarezvani/claude-skills**：维护者主动给予 Co-authored-by 署名（PR #866 建议 → 维护者创建 #867 合并）
- **anthropics/skills**：多个 PR 在审查中，与维护者持续讨论
- 方向从社区获得初步外部验证（独立于自评）

### 实验概览

| 实验 | N | 设计 | 主要发现 | 状态 |
|------|:--:|------|------|:--:|
| Growth-log 回溯 | 34 sessions | 纵向编码，单编码者 | 机械门接线前 55.9% → 接线后 0.7% | ✅ 完成 |
| Causal Swap | 30 tasks | Between-subjects (15+15)，DeepSeek V4 Pro | WITH规则 73% vs WITHOUT 20%，OR=11.0, p=0.0092 | ⚠️ 单评分者，无双盲 |
| Format A/B | 150 tasks | Between-subjects (75+75)，6 sessions，DeepSeek V4 Pro | 机械门天花板效应（99.3%合规），格式影响推理深度非合规率 | ⚠️ 需 GateGuard-OFF 复现 |
| Syllogism 盲交叉验证 | 4 sessions | 5规则全触发，零违规+涌现主动审计 | 格式→推理深度因果链初步证据 | ⚠️ n过小，非对照 |

> **n-count 一致性说明**：仓库中出现 30/34/38/60/150 五个数字。30 = Causal Swap 任务数，34 = growth-log session 数，38 = paper-trial-results.md 累积试验次数（30原始 + 8新增），60 = 未来目标样本量，150 = Format A/B 任务数。各数字对应不同实验，非同一实验的数据矛盾。

### 竞品定位

当前 LLM Agent 可靠性研究均未覆盖配置层外部客观校验：

| 技术路线 | 代表工作 | 核心局限 |
|---------|---------|---------|
| 提示词工程优化 | 记忆池注入、上下文压缩 | 规则依赖 Agent 自我理解执行，无法强制校验 |
| 独立评估 Agent | RIVA、GLOVE | 新增 LLM 做校验，成本高、二次漂移风险 |
| 记忆增强方案 | Mem0、Letta、ASF | 仅注入记忆，不验证行为合规性 |
| 代码层自修改 | HyperAgents (Meta, ICLR 2026) | 操作代码层，不解决配置层漂移 |
| 格式效应 | Prompt Decorators (Heris 2025) | 声明式标签，不改变内部处理路径 |
| 注意力路由 | Pender (2026, Zenodo) | 证明格式→路由机制，未做工程转化 |

**本工作差异化**：无模型参与、可量化、可复现的外部机械校验。三层架构覆盖信息管线全程（到达→穿透→路由）。

### 独立学术审查

> ⚠️ **以下全部为 AI 模拟审查，非真人教授/审稿人。** 用途：作者在联系真人导师前进行自我诊断，识别论文最脆弱的环节。不代表任何学术机构的正式评审意见。

论文及实验经四轮 AI 模拟审查：

- **AI 模拟教授审计**（2026-07-11）：按 README 阅读指引逐层检查。结论：方向有学术价值，核心贡献是诚实度——κ=-0.14 的诚实报告比任何 p<0.001 都值钱。实验需修：独立评分者 + GateGuard-OFF 复现 + 实验概览表。
- **AI 模拟 ACL/CHI 审稿人评审**（2026-07-11）：创新度 6/10，实验 Rigor 2/10，理论 Depth 5/10，写作 3/10。裁决：Reject（当前）→ Weak Accept（修完后适合 ACL SRW）。
- **AI 模拟博士后冷读 ×2**（2026-07-11）：模拟 HCI 方向博士后（UCL）和 ML/Agent 方向博士后（CMU）独立审查。一致判断：方向有学术价值，但所有定量结果追溯回单评分者；GateGuard 实验验证了 L1（机械门）而非 L3（因果编码）；结构倒置（最长章节证据最弱）；J-space 类比是隐喻不是机制。当前适合 workshop，修好实验可达 CHI LBW / ACL SRW。

所有模拟审查报告见 paper/reviewer-report-2026-07-11.md。

---

## 关键数据

### 150 任务对照实验（2026-07）

| 条件 | Sessions | 违规率 |
|------|:--------:|:------:|
| 三段论 (A) | 3 | 1.3% |
| 命令式 (B) | 3 | 0% |
| **合计** | **6** | **0.7%** |

唯一违规由 agent 自己的 Honesty 自审发现。

### 回溯基线（无机械门时）

34 growth-log: **55.9% session 有违规**。最常见：跳过前置检查 (44.1%)。

**55.9% → 0.7%。** 机械门是主导因子。

---

## 三层架构

```
L1 机械门: 文件时间戳/正则/进程退出码 → 绕过 AI 自评偏差
L2 神经门: 关键词回响→logprob差分→残差流探针 → 检测规则穿透率
L3 因果编码: 三段论格式改变注意力路由 → 影响推理深度
```

---

## 神经门：从文件校验到模型内部

文件系统层（L1）校验信息到达性，不解决规则穿透率。L2 神经门检测规则是否真实作用于模型输出：

- **v1 关键词回响检测**（已部署，86行 Python）：从 BODY.md 提取 8 个约束主题，扫描输出关键词回响。沉默约束=可能失效。经 150 任务实验验证。
- **v2 Logprob 差分**（已设计）：DeepSeek `logprobs=True` 对比带/不带约束时 token 概率偏移。delta>0.3=约束活跃。脚本已完成，待 API key。
- **v3 残差流探针**（路线图）：Qwen2.5-1.5B 上训练线性探针（RTX 3060 6GB 可行），按层检测约束信息可解码性，追踪跨 session 层位移→预警衰减。

审计 7 个主流 Agent 框架，0 个做神经层约束检测。

## 研究基础设施

### DeepSeek V4 Pro 成本优化（2026-07-11）

实验基础设施从 Claude API 迁移至 DeepSeek V4 Pro 后，针对 1M 上下文 + 自动前缀缓存特性进行了系统参数调优。详见 [experiment/DEEPSEEK_OPTIMIZATION.md](experiment/DEEPSEEK_OPTIMIZATION.md)

| 关键优化 | 效果 |
|------|------|
| ToolSearch → false | 消除每次工具加载后的缓存摧毁 (GitHub Issue #53132) |
| autoCompactWindow: 600K→400K | 利用 1M 窗口, 稳定前缀→提高缓存命中 |
| subagent → flash | 子任务成本 3x 降低 |
| 实验配置快照 | `experiment-config-snapshot.json` 确保补充实验可复现 |

---

## 已发布技术博文

**DEV.to（3篇）**：
- [AI Agents Can't Self-Verify — A Structural Constraint](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) — Prose Barrier 理论
- [I Built a Neural Gate — Layer 2 of Self-Verification](https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2) — 神经门三阶段方案
- [I Ran 150 Tasks to Test If AI Agents Follow Rules](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) — 150任务对照实验报告

**掘金（中文版 3篇对应）**：juejin.cn/user/4250072430682412

---

## 诚实局限清单

1. 单张 RTX 3060，无法多模型消融（此条仅限制神经门 v3；主实验使用 DeepSeek V4 Pro API）
2. 评分由自己完成，无双盲 · 无第二评分者 · **κ=-0.14（盲审信度检查 n=8，未通过——这是论文最致命的缺陷）**
3. 文献依赖自主检索+AI辅助，缺系统训练（漏引 Self-consistency / Reflexion / DSPy / CoT 等基础文献）
4. 本方向为个人独立探索，无导师指导

**我能做**：问题发现→方案设计→原型→实验。**需要帮助**：创新度定级、实验缺陷修正、学术论证规范、发表路径。
