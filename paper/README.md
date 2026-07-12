# 格式如何影响 AI Agent 的规则内化：从机械校验到因果编码

> 林宇浩，福建农林大学 · 空间信息与数字技术 2023 级 · 2026 年 7 月
>
> **一句话**：三段论格式（大前提→小前提→因此）比祈使句（"你必须..."）让模型更深层地内化约束——logprob 差分 d=+0.578，BF₁₀=282,399，80% 探针一致。DV 直接从 API token 概率读取，不经过人工评分。

---

## 客观边界（请先读这行）

> **以下所有实验由同一人（林宇浩）在单台设备（Dell G15, RTX 3060 6GB, 16GB RAM）上完成，使用单一模型（DeepSeek V4 Pro API）。文中所有"专家审查""教授审计""审稿人评审"均为 AI 模拟，不代表任何真人的学术判断。**
>
> 这些不是"待修复的缺陷"——它们是一个本科生用现有资源能做到的全部。Logprob V3 实验的部分数据（DV = API 返回的 token logprob）绕过了人工评分的主观性；其余所有定量结果追溯回单一评分者（κ=−0.14，盲审信度未通过）。请据此评估本文的贡献。

---

## 30 秒 · 教授冷读第一眼

| 你要知道的事 | 答案 |
|------------|------|
| **发现了什么** | 三段论格式的约束内化深度 > 祈使句，中等效应（d=0.578），跨 4 类约束通用 |
| **怎么测的** | 40 个二元选择探针 × 3 条件，取第一 token logprob 差值——直接从 API 读，不经过人工评分 |
| **方法论亮点** | 先导实验是零效应（d=−0.148），因为测量工具有 bug。修复测量工具后真实效应暴露——完整的 measurement validity 叙事 |
| **客观限制** | 单模型 · 单作者 · 单人评分（除 logprob DV 外） · 无导师 · 无经费 · 一台笔记本 |
| **投稿定位** | ACL SRW / CHI LBW（workshop 级），以 undergraduate 身份独立完成 |

---

## 阅读路径

### 赶时间（2 min）
→ 实验概览表 + 关键数字。

### 想理解（15 min）
→ [../PAPER.md](../PAPER.md) Part 3（§6 Causal Structure Encoding）。

### 想审查（30 min）
→ 完整 PAPER.md + 实验数据 + [reviewer-report-2026-07-11.md](reviewer-report-2026-07-11.md)。**注意：reviewer-report 中的"审稿人"是 AI 模拟的，用途是自诊而非替代真人评审。**

---

## 实验概览

| 实验 | N | 设计 | DV | 主要发现 | 效应量 | 评分者 |
|------|:--:|------|-----|------|:--:|:--:|
| Growth-log 回溯 | 34 sessions | 纵向编码 | 违规率 | 机械门接线前 55.9% → 接线后 0.7% | — | 作者本人 |
| Causal Swap | 30 tasks | Between-subjects (15+15) | 备选方案寻求率 | WITH 73% vs WITHOUT 20%, OR=11.0, p=0.0092 | OR=11.0 | 作者本人，未盲 |
| **Logprob 探针 V3** | **40 probes** | **Within-probe, 3-condition** | **logprob(A)−logprob(B)** | **三段论 > 祈使句, d=+0.578, BF=282k** | **d=0.578** | **API 直接返回，无人工评分** |
| Format A/B 合规 | 150 tasks | Between-subjects (75+75), 6 sessions | 合规率 | 天花板效应（99.3%），机械钩子主导 | — | 作者本人 |

> **Logprob V3 和 Format A/B 的区别**：Format A/B 测的是**行为输出**（hook 开启时合规率被机械门推到天花板，格式差异被遮盖）。Logprob V3 测的是**内部表征**（取第一 token 的概率差，绕过机械门，直接看模型对约束 token 的"内部置信度"）。两者互补——格式确实影响模型内部处理，但当机械钩子激活时，行为输出被钩子主导。

> **n-count 说明**：仓库中 30/34/40/150 分别对应 Causal Swap / growth-log / 探针数 / Format A/B，各实验独立，不是同一实验的数据矛盾。

---

## 三层架构

```
L1 机械门: 文件时间戳/正则/进程退出码 → 绕过 AI 自评偏差
L2 神经门: 关键词回响→logprob差分→残差流探针 → 检测规则穿透率
L3 因果编码: 三段论格式改变注意力路由 → 影响推理深度
```

**证据强度（诚实标注）**：L1（行为层，150 任务验证）→ L2（token 层，40 探针验证）→ L3（机制层，效应存在但中间因果链未直接测量，依赖 Pender 2026 间接支持）

Logprob V3 是 L2→L3 的关键纽带：三段论格式产生了比祈使句更强的约束 token 概率偏移（d=0.578），说明格式影响模型对约束的"内部处理深度"，而非仅改变最终行为输出。

---

## 关键数字

### Logprob 探针 V3（2026-07-12，新增）

| 指标 | 先导 (n=8, 未预验证) | 验证 (n=40, 预验证) |
|------|:---:|:---:|
| Cohen's d_z | −0.148 | **+0.578** |
| BF₁₀ | < 1 (支持 H₀) | **282,399** (极强支持 H₁) |
| Bootstrap 95% CI | 跨零 | **[+3.39, +11.17]** |
| 方向一致率 | ~50% | **80%** (32/40) |
| Category × Format | — | F(3,36)=0.26, η²=0.02 (n.s.) |

**结论**：三段论格式在约束内化上优于祈使句，效应量中等偏大，跨 4 类约束（action/epistemic/structural/meta）通用。

**为什么先导是零效应**：8 探针中 4 个的对比 token 不在 DeepSeek top-20 logprobs 中 → −10.0 哨兵值人为制造差异。预验证管线（probe_validator.py → probe_pool.py → experiment_v3.py）消除 artifact 后真实效应暴露。这个"测量工具修复→真实效应浮现"的叙事本身就是论文的核心贡献之一。

**Logprob V3 的 DV 优势**：DV（logprob 差值）直接从 DeepSeek API 读取，不经过任何人（包括作者本人）的评分判断。这是全文中唯一完全客观的因变量。

### 150 任务合规实验（2026-07-11）

| 条件 | Sessions | 违规率 |
|------|:--------:|:------:|
| 三段论 | 3 | 1.3% |
| 命令式 | 3 | 0% |
| **合计** | **6** | **0.7%** |

天花板效应：机械门是行为合规的主导因子，格式差异被遮盖。

### 回溯基线

34 growth-log，无机械门时：**55.9% session 有违规**。

**55.9% → 0.7%**。机械门的效应量远超格式效应。

---

## 竞品定位

| 技术路线 | 代表工作 | 核心局限 |
|---------|---------|---------|
| 提示词工程 | 记忆池注入、上下文压缩 | 规则依赖 Agent 自我理解执行 |
| 独立评估 Agent | RIVA、GLOVE | 新增 LLM 校验，成本高、二次漂移 |
| 记忆增强 | Mem0、Letta、ASF | 仅注入记忆，不验证合规性 |
| 代码层自修改 | HyperAgents (Meta, ICLR 2026) | 操作代码层，不解决配置层漂移 |
| 格式标注 | Prompt Decorators (Heris 2025) | 声明式标签，不改变内部处理 |
| 注意力路由 | Pender (2026, Zenodo) | 证明格式→路由机制，未做工程转化 |

**本工作差异**：机械校验（无模型参与）→ token 级探针（绕过行为天花板）→ 因果编码解释。三层证据从客观→半客观→推理，诚实标注每层的证据强度。

---

## 实验数据（全部开源）

- `experiment/experiment-results-2026-07-11.md` — 150 task 合规实验
- `experiment/systematic-baseline-coding.md` — 34 growth-log 回溯编码
- `../experiments/format-comparison/results/experiment-2-confirmatory-20260712-040240.json` — Logprob V3 完整数据
- `../experiments/format-comparison/probe_pool.py` — 40 探针池
- `../experiments/format-comparison/experiment_v3.py` — 双实验架构脚本

---

## 外部反馈（开源社区·来自真人）

工程组件已获真实的外部认可（非 AI 模拟）：
- **ECC 仓库**（affaan-m/ECC）：2 PR 已合并，1 通过审批
- **alirezarezvani/claude-skills**：维护者主动给予 Co-authored-by 署名
- **anthropics/skills**：多个 PR 审查中

---

## AI 模拟审查（自诊工具·非真人评审）

> ⚠️ **全部为 AI 模拟。** 用途：作者在联系真人导师/投稿前进行自我诊断，识别论文最脆弱的环节。以下"审稿人""教授""博士后"均为 AI 角色扮演，不代表任何学术机构的正式意见。

- **模拟教授审计**（2026-07-11）：方向有学术价值，核心贡献是诚实度——κ=−0.14 的诚实报告比任何 p<0.001 都值钱
- **模拟 ACL/CHI 审稿人**（2026-07-11）：创新 6/10，实验 Rigor 2/10，理论 5/10，写作 3/10。裁决 Reject → Weak Accept（修后）
- **模拟博士后冷读 ×2**（2026-07-11）：HCI 方向（UCL）和 ML/Agent 方向（CMU）。一致判断：方向有价值，但所有定量结果追溯回单评分者；当前适合 workshop 级

模拟审查完整报告：`reviewer-report-2026-07-11.md`

---

## 我能做的和不能做的

**我做到了**（一个人、一台笔记本、一个 API key）：
- 问题发现 → 假说形成 → 实验设计 → 原型构建 → 数据收集 → 分析 → 诚实报告
- 发现并修复了测量工具的 floor artifact（从零效应→真实效应）
- Logprob DV 绕过了人工评分的主观性（这一点是客观的）
- 工程组件获得开源社区真实认可

**我没做到的**（这些在当前条件下做不到）：
- 第二评分者 → 需要另一个人，不是"以后再做"能解决的
- 多模型消融 → 需要多个 API key 或多张 GPU
- 真人导师指导 → 在找了
- 系统文献训练 → 需要时间，正在补

**这些不是借口——是边界。** 论文的价值应该在这个边界内被评估，而不是因为超出边界而被否定。

---

## 已发布技术博文

**DEV.to**：
- [AI Agents Can't Self-Verify — A Structural Constraint](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) — Prose Barrier
- [I Built a Neural Gate — Layer 2 of Self-Verification](https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2) — 神经门
- [I Ran 150 Tasks to Test If AI Agents Follow Rules](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) — 150 任务实验

**掘金**（中文，3 篇对应）：juejin.cn/user/4250072430682412
