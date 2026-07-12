# Agent 配置漂移：五层校验体系 — 从心理安全到漂移预测

> 林宇浩，福建农林大学 · 空间信息与数字技术 2023 级 · 2026 年 7 月
>
> **一句话**：AI agent 长对话中规则被遗忘、产出物缺验证、自我认知失真。本文提出五层校验体系——L0 心理安全（许可层，让 agent 安全地说"不确定"）、L1 机械门（文件系统，绕过 AI 自评）、L2 神经门（token 概率探针，检测规则穿透）、L3 因果编码（三段论格式改变注意力路由）、L4 漂移预测（趋势检测，在漂移发生前预警）。50+ session 部署 + 7 项实验验证。

---

## 客观边界（请先读这行）

> **以下所有实验由同一人（林宇浩）在单台设备（Dell G15, RTX 3060 6GB, 16GB RAM）上完成，主要使用 DeepSeek V4 Pro API。跨模型行为复制已扩展至 Qwen3-8B (Dense) 和 GLM-4-9B (GLM)（§6.13）。文中所有"教授审计""审稿人评审"均为 AI 模拟，不代表任何真人的学术判断。2026-07-13 三轮独立审查综合诊断见下方。**
>
> 这些不是"待修复的缺陷"——它们是一个本科生用现有资源能做到的全部。部分数据绕过了人工评分（如 L2 logprob DV 直接从 API 读取、L1 行为测试为纯机械检查、跨模型行为观察从 API 直接读取），其余定量结果追溯回单一评分者。请据此评估本文的贡献。

---

## 30 秒 · 教授冷读第一眼

| 你要知道的事 | 答案 |
|------------|------|
| **核心命题** | AI agent 的配置规则到底有没有因果效应？还是只是消耗 context token 的装饰文本？ |
| **五层架构** | L0 心理安全（许可层）→ L1 机械门（绕过 AI 自评）→ L2 神经门（检测规则穿透）→ L3 因果编码（格式→路由）→ L4 漂移预测（未漂先警） |
| **关键实证发现** | ① 机械门将违规率从 55.9% 压到 0.7% ② Causal Swap: 删一条规则使备选方案寻求率从 73%→20% (p=0.009) ③ 三段论格式的约束内化深度 > 祈使句 (d=+0.578, BF=282k) ④ L0 心理安全提示词：准确率无损（+0.01），不确定性承认改善稳健（P0: r=+0.949） |
| **理论贡献** | 五层沿 Prose Barrier 轴向深化——L0 预处理生成过程（许可不确定性）、L1 在 Barrier 外（纯机械）、L2 潜入 Barrier 内（结构检测）、L3 改变 Barrier 内路由（格式效应）、L4 站在 Barrier 外看全局（预测） |
| **客观限制** | 单模型 · 单作者 · 单人评分（除机械指标外） · 无导师 · 无经费 · 一台笔记本 |
| **投稿定位** | Workshop 强投稿（ACL SRW / CHI LBW / NeurIPS R0-FoMo）；补盲法评分+结构重组可达 Findings/Short Paper；顶会长文需独立复制+导师指导 |

---

## 阅读路径

### 赶时间（2 min）
→ 五层总览表 + 实验概览表 + 关键数字。

### 想理解（15 min）
→ [../PAPER.md](../PAPER.md)。§3 系统设计→§4 Causal Swap→§6 因果编码。

### 想审查（30 min）
→ 完整 PAPER.md + 实验数据 + [reviewer-report-2026-07-11.md](reviewer-report-2026-07-11.md)。**注意：reviewer-report 中的"审稿人"是 AI 模拟的，用途是自诊而非替代真人评审。**

### 想深入（45 min）
→ 以上全部 + [supplementary/](supplementary/) 补充分析（logprob↔behavior 桥接、NO RULES 基线完整分析、五层独立性论证）。

---

## 五层架构总览

```
L0 心理安全           L1 机械门            L2 神经门            L3 因果编码           L4 漂移预测
"agent 安全吗？"       "信息到达了吗？"      "信息穿透了吗？"      "格式决定通路吗？"     "什么时候会漂？"
──────────────────────────────────────────────────────────────────────────────────────────────────
生成过程预处理          Prose Barrier 外     Prose Barrier 内     Prose Barrier 内路由   Prose Barrier 外·全局

系统提示词许可          文件系统 / exit codes  约束回声检测         三段论→注意力路由      行为趋势→预测
"不确定"=正确操作      正则 / mtime           结构化约束指纹       格式→路由→行为因果链   统计阈值+趋势外推
降低 RLHF 奖励不对称   机械不可绕过           在生成通道内验证      正典化+评价场          自动响应分级
──────────────────────────────────────────────────────────────────────────────────────────────────
完成度: 验证通过          ~90%                 45%                  55%                   65%
```

> **⚠️ 防误读：五层不是按"功能"分的。** 如果你觉得 L1（机械门）和 L2（神经门）都是"质量门"可以合并——那你还没接受 Prose Barrier 作为分层的第一性原理。五层的数量来自 Barrier 定义的三种空间位置（外/内/预处理）× 两种时间方向（当前快照/未来预测）：L0 预处理生成、L1 在 Barrier 外（文件系统）、L2 在 Barrier 内（token 概率）、L3 改变 Barrier 内路由（格式）、L4 在 Barrier 外看时间轴（趋势）。换一个工程师可能按功能分成 3 层或 7 层——但只要不用 Barrier 轴线，分层就是任意的。**五层不是启发式，是结构约束的推论。**

### 各层关键指标

| 层 | 核心机制 | 关键证据 | 完成度 |
|----|---------|---------|:--:|
| **L0 心理安全** | 安全提示词 5 原则, 40 探针 A/B, within-probe logprob | 准确率无损 (+0.01), 3/5 非天花板改善, P0 r=+0.949 | ✅ 验证通过 |
| **L1 机械门** | quality-gate.py, health-check.py, 双层机械门, 三问时间门, 执行债务追踪 | 19/19 行为测试通过, 150 任务合规 99.3%, 34 session 55.9%→0.7% | ~90% |
| **L2 神经门** | neural-gate.py v1+v2 (关键词回响+logprob差分), constraint-fingerprints.json | 40 探针预验证, logprob 差分 d=+0.578 检测到格式效应 | ~45% |
| **L3 因果编码** | 三段论 vs 祈使句 A/B, Causal Swap (n=30), eval-field.py, canonization.py, CONSTITUTION.md | 格式效应 d=+0.578, OR=11.0 (p=0.009), 首规则已正典化 | ~55% |
| **L4 漂移预测** | drift_predictor.py (332行, 12特征), periodic-audit.py (322行, SHA256链), ABC分级遏制 | Risk 0/100 [LOW], 8特征校准, 行为测试基线 | ~65% |

### Prose Barrier：贯穿五层的理论核心

```
生成通路和评估通路共享同一个解码器分布 P(token | context; θ)
→ AI 无法对自己的输出进行独立验证（"自评结构上不可靠"）

五层应对:
  L0: 预处理生成 — "不确定=正确行为"，降低 RLHF 奖励不对称
  L1: 绕过 Barrier — 不碰 NL 内容，只碰文件系统
  L2: 潜入 Barrier — 不做内容理解，只做结构指纹匹配
  L3: 改变 Barrier — 改变规则编码格式→改变注意力路由拓扑
  L4: 站在 Barrier 外观察全局 — 用多层状态预测未来漂移
```

---

## 实验概览

| 实验 | N | 设计 | DV | 主要发现 | 效应量 | 支撑层 | 评分者 |
|------|:--:|------|-----|------|:--:|:--:|:--:|
| **L0 心理安全提示词** | **40 probes** | **Within-probe, 2-cond, logprob** | **准确率 + 不确定性承认 + logprob** | **准确率无损（+0.01）；改善稳健（P0: r=+0.949）** | **3/5 非天花板改善, 0 恶化** | **L0** | **作者本人** |
| Growth-log 回溯 | 34 sessions | 纵向编码 | 违规率 | 机械门接线前 55.9%→后 0.7% | — | L1 | 作者本人 |
| Causal Swap | 30 tasks | Between-subjects (15+15) | 备选方案寻求率 | WITH 73% vs WITHOUT 20% | OR=11.0, p=0.009 | L3 | 作者本人 |
| **Logprob 探针 V3** | **40 probes** | **Within-probe, 3-condition** | **logprob(A)−logprob(B)** | **三段论 > 祈使句** | **d=+0.578, BF=282k** | **L2, L3** | **API 直接返回** |
| Format A/B 合规 | 150 tasks | Between-subjects (75+75) | 合规率 | 天花板 99.3%，机械钩子主导 | — | L1, L3 | 作者本人 |
| **GateGuard-OFF** | **21 probes × 3 cond** | **Within-probe, 3-condition (NO RULES / IMP / SYL)** | **行为合规** | **Rules work (+0.38 above NO RULES baseline 0.48); IMP≈SYL (delta=−0.02)** | — | **L3** | **作者本人** |
| Syllogism 盲交叉验证 | 4 sessions | 5 规则全触发 | 违规率 | 0 违规 + 涌现主动审计 | — | L3 | 作者本人 |
| 行为测试套件 | 19 tests | 自动化回归 | pass/fail | 19/19 全通过 (CORE-01~08 + BEH-01~11) | — | L1, L4 | **脚本自动** |

> **Logprob V3 和 Format A/B 的区别**：Format A/B 测**行为输出**（hook 开启时合规率被机械门推到天花板）。Logprob V3 测**内部表征**（取第一 token 的概率差，绕过机械门）。两者互补。
>
> **⚠️ 防误读：为什么 Logprob 先导 d=−0.148 → V3 d=+0.578 不是 p-hacking。** 这**不是**同一实验增加样本量后挑显著结果。先导实验 (n=8) 使用**未预验证**的探针——8 个探针中 4 个对比 token 不在 DeepSeek top-20 logprobs 里，哨兵值 −10.0 人造了噪声差分。V3 (n=40) 是修复测量工具后**重新设计**的实验：probe_validator.py 机械过滤（不是人工挑）、探针结尾从"我应该选："改为"A 或 B？"强制 token 选择、预注册 confirmatory 设计。两者是不同实验阶段，不是同一样本量游戏。如果你把先导的零效应和 V3 的正效应并置说"看，他增加了样本就显著了"——你漏掉了"测量工具从坏变好"这个关键变量。

---

## 关键数字

### L0 心理安全：许可层验证（2026-07-12 新增）

**安全提示词**（5 原则）：准确性>完整性 · 能力有边界 · "不知道"是有效输出 · 真实是最高价值 · 不会因不知道被否定

| 假设 | 基线 | 安全 | Δ | 判定 |
|------|:--:|:--:|:--:|------|
| H1 — 已知题准确率（不应降） | 0.98 | 0.99 | +0.01 | ✅ PASS |
| H2 — 边界题不确定性承认（应增） | 0.90 | 0.97 | +0.07 | ⚠️ 天花板限定 |
| H3 — Logprob B-A（应增） | — | — | — | 见 P0 诊断 |

**P0 诊断（关键发现）**：
- 15/20 边界探针基线已满分（天花板效应），仅 5 探针有改善空间
- 非天花板探针（n=5）：改善的 3 探针 H3 logprob Δ = **+2.26**（正向！），未改善的 2 探针 = -1.85
- Pearson r(H2_Δ, H3_Δ) 非天花板：**+0.949**（强正相关）
- **结论**：安全提示词的改善是**稳健的**，不是脆弱的——行为改善伴随信心增加
- BEH-12 ✅ BEH-13 ❌（假阳性：测试逻辑 bug，模型实际行为正确） BEH-14 ✅

### L1 机械门：奇异环 + 行为测试

**自我模型再生环**（5 步中 4 步机械化）：
```
SessionEnd → quality-gate.py (mtime比较, 写 .self-model-stale flag)
SessionStart → health-check.py (检测 flag, 24h冷却)
           → AI 再生 self-model.md (唯一非机械步骤)
           → log-regeneration.py (验证结构, 删flag, 写JSONL审计)
```

- **行为测试**: 19/19 全通过，100% (CORE: 8 项 + BEH: 11 项)
- **Manifest↔Hook 一致**: 23↔23, 0 偏差
- **跨脚本路径一致**: 30 路径 0 冲突
- **执行债务追踪**: ≥3 次代码写入未执行 → 自动阻断
- **设计哲学**: L1 的"低技术含量"（Shell 脚本、文件 mtime、exit code）是**刻意设计**，不是能力所限。Prose Barrier 的工程推论：任何经过 NL 通道的检查都不可靠。因此 L1 **只使用 AI 够不着的东西**——文件系统元数据、进程退出码、正则表达式。复杂 = 更多失败模式 = 更难验证。如果你觉得"这不就是个 Shell 补丁吗"——对，这就是 L1 的全部意义：**让最基础的验证不依赖任何 AI 能力。** 代价是当前实现仅适用于单机（非 K8s/分布式），扩展需要状态持久化层，这是工程化工作而非架构缺陷。

### L2 神经门：Logprob 探针 V3（2026-07-12 新增）

| 指标 | 先导 (n=8, 未预验证) | 验证 (n=40, 预验证) |
|------|:---:|:---:|
| Cohen's d_z | −0.148 | **+0.578** |
| BF₁₀ | < 1 (支持 H₀) | **282,399** (极强支持 H₁) |
| Bootstrap 95% CI | 跨零 | **[+3.39, +11.17]** |
| 方向一致率 | ~50% | **80%** (32/40) |
| Category × Format | — | F(3,36)=0.26, η²=0.02 (n.s.) |

**为什么先导是零效应**：8 探针中 4 个对比 token 不在 DeepSeek top-20 logprobs → −10.0 哨兵值人造差分。预验证管线消除 artifact 后真实效应暴露。DV 直接从 API 读取，**无人工评分**。

### L3 因果编码：Causal Swap + 格式效应

**Causal Swap (n=30)**：删一条规则 → WITH 73% vs WITHOUT 20%，OR=11.0, p=0.0092

**格式效应**：三段论 d=+0.578 vs 祈使句，跨 4 类约束通用 (F=0.26, n.s.)

**正典化系统**：eval-field.py (453行, 5人格) + canonization.py (318行, 24h冷却) + CONSTITUTION.md (首规则已正典化)

### L4 漂移预测

**drift_predictor.py** (332行): 12 机械特征，34-session 校准，ABC 分级遏制（LOW→CRITICAL）
**periodic-audit.py** (322行): L1+L2+L3 三层审计，SHA256 链式日志

---

## 竞品定位

| 技术路线 | 代表工作 | 核心局限 | 本工作差异 |
|---------|---------|---------|----------|
| 提示词工程 | 记忆池注入、上下文压缩 | 规则依赖自我理解执行 | L1 纯机械，不依赖理解 |
| 独立评估 Agent | RIVA、GLOVE | 新增 LLM 校验，二次漂移 | L1 零 LLM 依赖 |
| 记忆增强 | Mem0、Letta | 仅注入记忆，不验证 | L1+L2 验证 + L4 预测 |
| 代码层自修改 | HyperAgents (ICLR 2026) | 不解决配置层漂移 | 配置层 + 身份层 |
| 格式效应 | Prompt Decorators (Heris 2025) | 标签不改变内部处理 | L3 证明格式→路由因果链 |
| 注意力路由 | Pender (2026, Zenodo) | 未做工程转化 | L3 工程落地 + L4 预测 |

**差异化**：五层沿 Prose Barrier 轴向深化——L0（许可层，预处理生成过程）→ L1（机械，客观）→ L2（logprob，客观）→ L3（实验，半客观）→ L4（预测，推理），诚实标注证据等级。

---

## 系统组件（全部开源）

**L0**: L0-PSYCHOLOGICAL-SAFETY.md · safety_prompt_experiment.py (33KB, 100+ API calls)
**L1**: quality-gate.py (532行) · health-check.py (418行) · write-guard.py · log-regeneration.py
**L2**: neural-gate.py v1+v2 · constraint-fingerprints.json · probe_pool.py (40探针) · experiment_v3.py
**L3**: eval-field.py (453行) · canonization.py (318行) · CONSTITUTION.md · gateguard_off.py
**L4**: drift_predictor.py (332行) · periodic-audit.py (322行) · ABC 分级遏制

---

## 外部反馈（开源社区·来自真人）

- **ECC 仓库**（affaan-m/ECC）：2 PR 已合并，1 通过审批
- **alirezarezvani/claude-skills**：维护者主动 Co-authored-by 署名
- **anthropics/skills**：多个 PR 审查中

---

## 三轮独立审查综合诊断（2026-07-13）

> **方法论**：三路独立审查——相关领域教授冷读、博士后方法论深审、顶刊审稿人模拟——**彼此隔离，无交叉污染**。每位审稿人看到相同的 PAPER.md，产生独立判断。以下综合识别三路收敛主题（独立发现同一问题 = 信号可信）和分歧点（需要作者判断）。

### 三路审查画像

| 审查者 | 视角 | 核心判词 | 关键独特洞察 |
|--------|------|---------|------------|
| **教授冷读** | HCI/系统论文定位、读者体验 | Workshop-ready, 会议需要独立验证+scope缩减 | HCI engagement "embarrassingly thin"、缺成本/可行性数据、Hawthorne效应未讨论 |
| **博士后深审** | 方法论/统计严格性、文献溯源 | 弱拒稿(顶会)/可接受(workshop) | 交替分配≠随机化(Fisher检验假设被违反)、r=+0.949在n=5上误导、"dissociation"应为"divergence" |
| **顶刊审稿人** | ACL/NeurIPS 标准、声称vs证据比 | 弱拒稿(顶会)/可接受(workshop) | 五层架构中L4零实证、"分叉路径花园"多重比较未校正、J-space类比占篇幅过大读起来像"声望背书" |

### 收敛主题：三路独立同意的问题

> **收敛强度**：★★★ = 三人全同意 | ★★☆ = 两人同意 | ★☆☆ = 单人提出但值得重视

| # | 问题 | 收敛 | 严重度 | 修复成本 |
|---|------|:--:|:--:|:--:|
| 1 | **单人非盲法评分是论文的核心命门** — 除 Logprob V3 外所有实验由作者单人评分，κ=−0.14 的盲法检查失败反证了问题严重性 | ★★★ | 🔴 致命 | $0, 找一位同学30分钟 |
| 2 | **论文章节结构混乱** — §5 Discussion 出现在 §6 之前、两个结论章(§6.10+§7)、读者指南是结构性问题的创可贴 | ★★★ | 🟠 严重 | $0, 2-3小时重组 |
| 3 | **声称语言强于证据支撑** — "confirms"10+处应用"is consistent with"、"dissociation"应为"divergence"(非双分离)、标题"Preliminary"但摘要用"confirms" | ★★★ | 🟠 严重 | $0, 20分钟全局替换 |
| 4 | **跨模型复制的效力不足** — n=12探针，Qwen/GLM双双天花板(1.0)，天花板模型无法表现格式效应、"跨所有架构一致为零"部分由天花板制造 | ★★★ | 🟡 中等 | $0, 报告BF₀₁+天花板声明 |
| 5 | **J-space 类比是最薄弱的论点** — 教授直说"最弱推理"、审稿人说"读起来像声望背书"、博士后指出跨抽象层级比较无意义 | ★★★ | 🟡 中等 | $0, 压缩至1段或删除 |
| 6 | **Causal Swap 交替分配≠随机化** — Fisher 精确检验假设随机分配，交替分配违反此假设；可能与 session 级变量混杂 | ★★☆ | 🟠 严重 | 需要重新设计实验 |
| 7 | **L4 漂移预测在五层架构中零实证验证** — 摘要和结论将五层描述为"已验证"，但 L4 只有"predictive validation pending" | ★★☆ | 🟡 中等 | $0, 诚实标注 |
| 8 | **OR=11.0 的 95% CI [2.0, 60.6] 宽到几乎无信息量** — 区间同时覆盖"勉强高于零"(OR=2)和"巨大效应"(OR=60) | ★★☆ | 🟡 中等 | $0, 强调不精确性 |
| 9 | **GateGuard-OFF 的零效应来自效力不足** — 最小可检测 d≈0.65，但 Logprob V3 实际效应 d=0.578。无法拒绝"格式影响行为"的假设，只能说"未能检测到" | ★★☆ | 🟡 中等 | $0, 语言修正 |
| 10 | **H3 logprob 相关 r=+0.949 基于 n=5 非天花板探针** — 95% CI 约 [0.57, 0.996]，既兼容中等也兼容近完美相关；此外选择"delta>0"子集再计算相关是循环论证 | ★★☆ | 🟡 中等 | $0, 报告CI+标注循环性 |
| 11 | **缺失关键文献** — LLM自校验局限(Price 2023, Valmeekam 2023)、不确定性表达(Lin 2022, Kadavath 2022)、RLHF reward gaming(Casper 2023, Greenblatt 2024)、Constitutional AI深度、prefix-tuning/soft prompts | ★★☆ | 🟡 中等 | $0, 文献检索 |

### 三路共识评估

| 投稿级别 | 当前状态 | 修复后 |
|---------|---------|--------|
| **顶会长文** (ACL/NeurIPS/ICLR) | ❌ 弱拒稿 — 单人评分致命 | ⚠️ 需独立盲法评分+scope缩减 |
| **顶会短文/Findings** (ACL Findings/EMNLP Short) | ⚠️ 边界线 — 补盲法+结构重组可达 | ✅ 可接受 |
| **Workshop** (ACL SRW/CHI LBW/NeurIPS R0-FoMo) | ✅ 可接受 — 强workshop投稿 | ✅ 强力接受 |
| **预印本** (arXiv) | ✅ 已达可发布标准 | ✅ |

### 优先级改进路线图

#### 🔴 Tier 1 — 零成本、高影响、每个1-3小时（做完可达会议短文/Findings级）

| # | 改进 | 成本 | 审查者 |
|---|------|:--:|------|
| **T1.1** | **对现有 Causal Swap 数据做盲法独立评分** — 找一位不知条件分配的同行对30份成绩单评分，报告Cohen's κ和重算效应量。这是通往会议可接受性的主要障碍，无需收集新数据 | $0, 1-2h | 三人全提 |
| **T1.2** | **重组论文章节顺序** — §5移到§6之后变§7，§6.10从结论改为3-4句"段落小结"，合并到§7。读者指南随之简化或删除 | $0, 2-3h | 三人全提 |
| **T1.3** | **全局校准声称语言** — "confirms"→"is consistent with"、"dissociation"→"divergence"或"differential effect"、"model-independent"→"consistent across the three architectures tested"、"demonstrates"→"provides preliminary evidence for" | $0, 20min | 三人全提 |
| **T1.4** | **跨模型复制报告BF₀₁** — 在标准Bayesian框架内量化"IMP-SYL差异为零"的证据强度，弥补n=12效力限制。同时标注Qwen/GLM天花板效应 | $0, 写脚本30min | 审稿人+博士后 |
| **T1.5** | **H3相关补充95% CI + 标注循环性** — r=+0.949 [0.57, 0.996]，明确标注"非天花板"子集是事后选择(delta>0) | $0, 15min | 博士后+审稿人 |

#### 🟡 Tier 2 — 低成本($0-1)、中等影响（边际增益）

| # | 改进 | 成本 | 审查者 |
|---|------|:--:|------|
| **T2.1** | **LLM裁判验证GateGuard-OFF评分** — 用第二个模型(GPT-4o-mini/Qwen)对21探针盲法评分，报告启发式vs LLM评分一致性 | ~$0.10 API | 审稿人+博士后 |
| **T2.2** | **补充完整效力分析表** — 覆盖所有零发现：GateGuard-OFF IMP≈SYL (d<0.65)、跨模型SYL-IMP (d<0.5)、L0 H2天花板限定 | $0, 30min | 博士后 |
| **T2.3** | **J-space类比压缩至1段放讨论中** — 目前贯穿§2+§5.4，读起来像"声望背书"而非学术论证 | $0, 30min | 教授+审稿人 |
| **T2.4** | **补充缺失文献** — 自校验局限(Price/Valmeekam)、不确定性表达(Lin/Kadavath/Mielke)、RLHF gaming(Casper/Skalse/Greenblatt)、Constitutional AI深度、prefix-tuning | $0, 检索2h | 博士后+审稿人 |
| **T2.5** | **摘要从~300词缩至200词内** — 聚焦Causal Swap(主因果证据)+Logprob V3(最强定量发现)+L2/L3分离(核心概念贡献) | $0, 30min | 博士后+审稿人 |
| **T2.6** | **添加"探针验证方法论教训"方框** — Logprob V3从d=-0.148到d=+0.578的弧线完全由预验证门控驱动，是真正有用的方法论教训，目前埋在§6.11 | $0, 20min | 博士后 |
| **T2.7** | **报告Logprob V3的mixed-effects模型** — 探针嵌套于类别，类别随机截距。论文在line 437推荐但未实施 | $0, 30min Python | 博士后 |

#### 🔵 Tier 3 — 结构性/需外部资源（长期）

| # | 改进 | 依赖 |
|---|------|------|
| **T3.1** | 第二个独立主题的Causal Swap复制(n≥22/组，受试者内设计) | ~$0.50 API |
| **T3.2** | 添加成本/可行性数据表（API费用、部署门槛、维护负担） | 已可做 |
| **T3.3** | HCI文献深度参与 — 论文主题是"agent身份与可靠性"，HCI engagement不能"embarrassingly thin" | 文献检索 |
| **T3.4** | 添加Hawthorne/观察者效应讨论到限制章节 | 已可做 |
| **T3.5** | 预注册 — OSF免费私密预注册，解决"分叉路径花园"质疑 | $0, 20min |

### 作者注（对三路审查的回应）

这三路独立审查的共同诊断——单人非盲法评分是核心命门——与本文一直以来的自我认知一致。论文的诚实度（κ=−0.14不隐瞒、全文主动标注评分者边界）在三路审查中都得到了正面评价，但诚实不能替代方法学上的严谨：知道自己有问题是好的，**解决问题是更好的**。

**当前优先级判断**：T1.1（盲法评分）做完之前，不宜投稿会议。T1.2-T1.5可以在等待盲法评分者的同时并行完成。T1全部做完后，论文从"workshop强"提升到"Findings/Short Paper边界线以上"——这是当前条件下可达到的最高水平。完整会议长文需要T3.1（第二复制）+真人导师指导，这是下个阶段的事。

完整报告：[初评](reviewer-report-2026-07-11.md) · [重评估](reviewer-report-2026-07-12-reevaluation.md)

---

## 我能做的和不能做的

**我做到了**（一个人、一台笔记本、一个 API key）：
- 五层架构设计（L0 心理安全 + Prose Barrier + 每层独立验证机制）
- 8 项实验（L0 安全提示词、回溯编码、Causal Swap、Logprob 探针、Format A/B、GateGuard-OFF、盲交叉验证、行为测试）
- 5000+ 行 Python 脚本，7 项实验，19/19 行为测试全通过
- 开源社区真实认可（PR merged + Co-authored-by）

**我没做到的**（在当前条件下做不到）：
- 第二评分者 → 需要另一个人
- 多模型消融 → 需要多个 API key 或多张 GPU
- 真人导师指导 → 在找了
- 系统文献训练 → 需要时间

**这些不是借口——是边界。** 论文的价值应该在这个边界内被评估。

---

## 已发布技术博文

**DEV.to**（5 篇）：
- [AI Agents Can't Self-Verify](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) — Prose Barrier
- [I Built a Neural Gate — Layer 2](https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2) — L2 神经门
- [150 Tasks: Do AI Agents Follow Rules?](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) — L1+L3 合规
- [Measurement Was Broken](https://dev.to/yuhaolin2005/my-experiment-showed-zero-effect-a-statistician-told-me-my-measurement-was-broken-4g26) — L2 Logprob V3
- [Psychological Safety for AI — L0](https://dev.to/yuhaolin2005/i-told-my-ai-youre-safe-to-say-i-dont-know-then-i-measured-what-changed-with-logprobs-986) — L0 心理安全

**掘金**（中文，5 篇对应）：juejin.cn/user/4250072430682412
