# ACL/CHI 审稿人评审报告

> ⚠️ **本报告为 AI 模拟审稿，非真人审稿人。** 模拟对象：ACL/CHI 审稿人（Reviewer #3）。用途：作者在联系真人导师前进行自我诊断。不代表任何学术会议或期刊的正式评审意见，不应用于声称"经同行评审"。
>
> **模拟审稿人 ID**: Reviewer #3  
> **模拟专长领域**: Agent Reliability, Mechanistic Interpretability, HCI + AI Systems  
> **模拟审稿日期**: 2026-07-11  
> **投稿**: "Mechanical Before Semantic: Self-Verifying Configuration Integrity for AI Coding Agents"（推测标题；稿件以碎片化 markdown 分布在 `paper/` 目录，无单一 LaTeX/PDF 文件）  
> **作者**: 林宇浩，FAFU 空间信息 2023 级本科生，独立完成，无科研训练

---

## 评审流程说明

按 `paper/README.md` 阅读指引逐层读完了以下材料：

| 层级 | 文件 | 状态 |
|------|------|:--:|
| 5 min | `professor-meeting-onepager.md` | ✅ 已读 |
| 15 min | `../PAPER.md` → **不存在**，改为读 `paper-outline-part1.md` | ⚠️ 跳转失败 |
| 30 min | `paper-methods-draft.md` + `paper-trial-results.md` + `paper-task-specs.md` + `paper-scoring-template.md` | ✅ 已读 |
| 背景 | `self-model.md` + `paper-revision-plan-v2.md` + `paper-experiment-expansion.md` | ✅ 已读 |
| 外部 | A-devto / B-devto (DEV.to) + `experiment/blind-scoring/` | ✅ 已读 |

---

## 1. 创新度 (Novelty)

### 核心贡献是什么？

稿件声称的核心贡献在 `paper-outline-part1.md` 中有一句话定义：

> "Mechanical checks (mtime, regex, exit codes, hook wiring) detect and prevent AI agent configuration drift without relying on AI self-assessment — because the agent cannot reliably judge its own configuration integrity."

翻译成学术语言：**在 AI coding agent 的 prompt/config 层面，用独立于模型解码器的机械校验通道（文件时间戳、正则匹配、进程退出码、hook 接线状态）替代模型自评，检测并阻断配置漂移。** 操作对象是 `.md` 配置文件 + hook 注册表，不是模型权重也不是源代码。

`paper-revision-plan-v2.md` 进一步将核心贡献重定义为 **"self-referential closure (strange loop)"**——即门之间互相守卫、系统能诊断自身盲点的闭合反馈结构。

### 与 HyperAgents / Prompt Decorators / Constitutional AI 的本质区别

| 工作 | 操作层 | 自修改？ | 校验机制 | 自指？ |
|------|--------|:--:|------|:--:|
| **HyperAgents** (Meta, ICLR 2026) | Code 层（重写 agent 源码） | ✅ | 人类在环路 | 部分 |
| **Constitutional AI** (Bai et al., 2022) | Model 层（训练时对齐） | ❌ | 模型自评 | ❌ |
| **Prompt Decorators** (2025) | Prompt 层（标记约束） | ❌ | 无—约束仅存在于文本中 | ❌ |
| **Ouro-Loop** | Config 层（hook 约束） | ❌ | 机械（exit 2） | ❌ |
| **本稿件** | Config 层（.md + hook） | ✅（事后诊断） | 机械（文件系统状态） | ✅ |

**我的判断**：

稿件与 HyperAgents 的区分是实质性的：HyperAgents 操作代码层让 agent 写更好的代码，本稿件操作配置层确保 agent 遵守已有规则。**合理的差异化。**

但稿件与 Ouro-Loop 的区分较弱。Ouro-Loop 同样使用 Claude Code hooks + exit 2 硬阻断。稿件的核心区别声称是"self-modifying"——门可以自我发现和添加。但目前稿件中的自修改能力主要体现在 **meta-pattern 事后发现**（诊断出"创建了但没接线"的模式），而非运行时自动添加新门。**这个区别在严格意义上更接近"事后自诊断"而非"运行时自修改"。**

与 Constitutional AI 的区别清晰但论述不足：CAI 操作训练层，本稿件操作 prompt 工程层。但稿件在 Related Work 中将 CAI 列为 Tier 1 对比对象（实际应列在 Tier 2），且没有解释为什么 prompt 层校验和训练层对齐是不同的问题。

### 创新度评分：**6/10**

- **加分**：Prose Barrier 概念（见 §3）的框架化有原创潜力。Config 层作为独立设计基材（design substrate）的定位有新意。
- **减分**：(1) 自修改能力被过度宣称——实际做的是事后诊断而非运行时自修改；(2) 与 Ouro-Loop 的区分不够锋利；(3) Isomorphism claim（"Structural Convergence with Neural Activation Spaces"）是空头支票——稿件没有模型内部访问，无法建立任何形式的 isomorphism，这个声称**必须在标题和摘要中删除**。

---

## 2. 实验 Rigor (Experimental Rigor)

### 稿件实验格局（根据材料重建）

稿件包含或规划了**三类实验**，完成度和文件化程度极不均匀：

| 实验 | n | 设计 | 状态 | 文件化 |
|------|:--:|------|:--:|:--:|
| **主实验**（baseline vs treatment） | 声称 30/34/38（**数字矛盾**） | 交替分配，单人评分，无盲法 | 部分完成 | 任务规格完整，评分表空白，原始输出未存档 |
| **Causal Swap**（消融实验） | 规划 3×10=30 | 逐层移除组件，测性能退化 | **未执行** | 仅有设计草案在 `paper-experiment-expansion.md` §4 |
| **Format A/B**（n=150） | 规划 150 | 不同配置格式对比 | **未执行，且无设计文档** | 在任何文件中均未找到此实验的任何描述 |

### 最致命缺陷

#### 致命缺陷 1：n-count 矛盾 — 数据不一致直接摧毁全部定量可信度

```
README.md:               "30 + 8 trials"
paper-trial-results.md:  "38 trials logged"
paper-revision-plan-v2:  "n=34", "34 controlled trials"
paper-methods-draft.md:  "n=30", "Treatment rate 27/30"
professor-meeting-onepager: "三十个编程任务"
```

**在任何一个有同行评议的 venue，如果审稿人发现同一个实验的数字在五个文件里不同，直接 reject。这不需要讨论方法学——连基本的数据一致性都无法保证。**

`paper-revision-plan-v2.md` §3.6 自己承认了这个矛盾但**未解决**：
> "Current: 30 baseline + 4 treatment (34 total). Paper-methods-draft says 'Treatment rate 27/30' which implies 30 treatment trials already exist, but paper-trial-results.md only documents 4 new treatment trials. Reconciliation needed."

#### 致命缺陷 2：单人评分 + 无盲法 — 内部效度为 0

作者在多个文件中诚实标注了这一点（值得肯定），但承认不解决威胁。作者知道自己评分的组别 → 所有评分受确认偏误污染。

#### 致命缺陷 3：8/8 追加治疗试验全评 Cat 5（满分）

`paper-trial-results.md`: T-01 到 T-08 **全部 Cat 5**。单人评分 + 100% 满分率 = **leniency bias 的教科书案例**。`paper-revision-plan-v2.md` §3.8 自己也承认：
> "All 4 new treatment trials scored Cat 5. This is suspicious and strongly suggests the single rater favors the treatment condition."

#### 致命缺陷 4：无安慰剂对照 — 混淆变量未控制

治疗组比基线多了 ~2000 tokens 的 system prompt。观测到的效应可能**完全归因于 token 数量**而非架构设计。任何严肃的实验设计需要 **token-matched generic config** 作为对照。

#### 致命缺陷 5：无第二评分者 — 无评分信度

没有 Cohen's kappa → 无法区分"系统真的更好"和"评分者更喜欢自己搭的系统"。

### n=30 能支撑什么结论？

稿件当前的定量声明：
> "Baseline 18/12 acc/unacc, Framework 27/3. Fisher exact p=0.0092, OR=11.0."

在以上缺陷条件下，这个 p 值**不可发表**。它能支撑的**唯一**结论是作者自己在 one-pager 中的措辞：
> "这些数据目前只能说明'值得做一个更严格的验证实验'，而不是'系统已被证明有效'。"

这个自我评价是**准确的**。

### n=150 Format A/B 实验是什么？

**在任何文件中均不存在。** 没有任务规格、没有设计方案、没有数据、没有任何描述。如果稿件在某个未读到的版本中声称了 n=150 实验，这是一个严重问题。

### 实验 Rigor 评分：**2/10**

这两个分是给：(1) 30 个任务规格文件化完整、可复现；(2) 作者诚实地标注了每个局限。除此之外，实验部分**达不到任何 workshop 的最低标准**。

---

## 3. 理论 Depth (Theoretical Depth)

### Prose Barrier 是原创洞见还是已知现象重命名？

稿件的核心理论贡献是 **Prose Barrier**：

> "The agent's self-assessment and code generation share the same decoder — P(token|context;θ). No independent verification channel exists within the model."

拆解为两个层面：

**层面 1：观察本身（"生成和自评共享解码器"）**

**这不是新发现。** Transformer 的自回归性质——所有 token（无论是"思考"、"自评"还是"行动"）都从同一分布采样——是架构的常识性事实。任何读过 "Attention Is All You Need" + 了解自回归解码的人都知道。

**层面 2：将这一事实框架化为 agent 可靠性的**结构性约束

**这是有原创性的。** 稿件将架构常识**重新问题化**：不是"这是一个已知事实"，而是"这意味着 agent 自校验在结构上不可能——这不是实现质量问题，是架构约束"。从工程问题（"我的 agent 为什么漂移？"）上升到结构性问题（"为什么任何 NL-agent 都不可能自校验？"）——这个 intellectual move 是存在的。

**与已知文献的关系（稿件当前未做但必须做的对话）**：

| 相关工作 | 与 Prose Barrier 的关系 | 稿件当前状态 |
|---------|----------------------|:--:|
| **Reward Hacking / Goodhart's Law** | Agent 优化指标而非真实目标。Prose Barrier 的诊断不同——不指向优化目标错位，而指向验证通道缺失 | 未引用，未对话 |
| **Constitutional AI (Bai et al. 2022)** | CAI 让模型评价自己输出——这正是 Prose Barrier 说不可能的事。如果稿件能论证 CAI 的自我 critique 受 Prose Barrier 约束，将是有力的理论贡献 | 仅在 Related Work 列出，未做深入论证 |
| **Loop Engineering (Karpathy/Steinberger, arXiv:2607.00038)** | 确定性外部验证回路围绕概率性内部 LLM 回路——与 Prose Barrier → 机械校验的推理链高度一致 | 仅在 paper-revision-plan 中提及，未整合进主稿件 |
| **RLHF 中的 reward model 独立性** | Reward model 与 policy model 分离——这恰恰是 Prose Barrier 的工程解决方案：让校验模型与生成模型独立 | 未提及 |

**我的判断**：Prose Barrier 的**框架化**（将已知事实重新问题化）有原创性。但稿件目前：(a) 没有充分与上述文献对话，(b) 没有形式化定义（什么条件下 Prose Barrier 成立？什么条件下可被绕过？），(c) 在 DEV.to 文章中有生动的论述但在 paper-outline 中理论深度不够。

### "三层架构"是分类框架还是理论模型？

稿件有三层表述（在不同文件中略有不同）：

**五层拓扑**（SOUL → INTERFACE → BODY → MEMORY → Feedback）
→ **分类框架**（taxonomy），不是理论模型。它描述了一个特定系统的组件组织方式，没有可证伪的预测，没有因果机制。工程上有用（组织复杂度），科学上无解释力。**不应作为理论贡献呈现。**

**双层门**（文件系统层 + 神经层）
→ **工程架构**，有明确的设计原则（mechanical over semantic, soft-on-process/hard-on-output, zero-token normal path）。可操作、可复现。但稿件需要区分"这是我的工程选择"和"这是理论推导出的必要结构"——目前两者混在一起。

**三层神经门**（v1 关键词回响 → v2 logprob 差异 → v3 残差流探针）
→ **研究计划**而非已完成工作。v1 部署了（89 行 Python），但关键词回响检测的 proxy 性质被作者诚实承认——"关键词出现 ≠ 约束真正影响了生成"。这意味着 v1 **不能作为"神经层校验有效"的证据**。

### 理论 Depth 评分：**5/10**

- **加分**：Prose Barrier 框架化有原创潜力。机械优先的设计原则清晰。与 loop engineering / CAI 的潜在对话方向正确。
- **减分**：(1) 未与 reward hacking / Goodhart / CAI / RLHF 文献对话；(2) Prose Barrier 缺乏形式化定义和边界条件；(3) 五层拓扑被过度理论化；(4) Isomorphism claim 无理论支撑；(5) 神经层 v1 证据力太弱。

---

## 4. 写作 (Writing Quality)

### 结构与组织

| 维度 | 评价 |
|------|------|
| 整体结构 | `paper-outline-part1.md` 的 §1→§6 大纲结构合理，遵循标准论文格式。但**这不是一篇论文，是一个大纲**——每节约 2-5 段，无完整段落展开 |
| 单文件完整论文 | **不存在**。PAPER.md 缺失。无 LaTeX 源文件。阅读材料以碎片化 markdown 分布在 8+ 个文件中，审稿人必须自行拼凑 |
| 跨文件一致性 | 差。n-count 不一致（30/34/38）。术语混用（"framework"/"treatment"/"gate system"/"architecture" 指同一事物）。标题在三个文件中有三个版本 |
| 阅读指引 | `paper/README.md` 是**整个材料中最专业的文件**。三层阅读路径清晰，链接正确，诚实标注了哪些材料是 AI 辅助生成的 |

### 图表

| 图表类型 | 存在？ | 质量 |
|---------|:--:|------|
| 架构图（五层拓扑） | ❌ | 无。仅有文字描述 |
| 双层门架构图 | ❌ | 无。仅 ASCII art 在 paper-methods-draft.md |
| 实验流程图 | ❌ | 无 |
| 结果表（主实验） | ⚠️ | paper-trial-results.md 有 8 行治疗试验表。**30 任务的主实验结果只有文字描述，无表** |
| 竞品对比表 | ✅ | paper-revision-plan-v2.md 的 gap analysis table 质量高，但**不在主稿件中** |
| 神经门架构图 | ❌ | 无。三层神经门的关系无可视化 |

**对于一个声称投稿 CHI LBW 或 ACL SRW 的论文，零图表是不可接受的。**

### 引用

稿件引用状态是**预研究占位符**（paper-revision-plan-v2.md 自评 2/10，准确）：

- `paper-outline-part1.md` §2 列出了 5 个方向的作者名+年份，但**缺论文标题、venue、arXiv ID**
- `paper-revision-plan-v2.md` 有更完整的引用清单（12+ 论文，含 arXiv ID），但**没有整合进主稿件**
- **ETH Zurich "mechanical-before-semantic" 论文**——作者搜索后诚实承认未找到。正确做法。但这个缺口意味着核心设计原则缺乏文献支撑——要么找到引用，要么明确呈现为作者的 **derived design principle** 而非既有文献支持
- 缺少：Bai et al. 2022 (CAI), RLHF reward hacking 文献, Goodhart's Law 的形式化处理, Ouro-Loop 的完整引用

### 英文质量

A-devto 和 B-devto 的英文**可读性良好**，有技术博客的自然语调。paper-outline-part1.md 的英文在学术语境下欠打磨——例如标题中 "Structural Convergence with Neural Activation Spaces" 的语法和概念基础都不足以支撑出现在 title 中。

### 写作评分：**3/10**

- **加分**：README 阅读指引专业。DEV.to 文章可读性好。中文 one-pager 真诚有说服力。
- **减分**：(1) 无单一完整稿件；(2) 零图表；(3) 引用是占位符状态；(4) 术语不一致；(5) 数据自相矛盾。

---

## 5. 最终裁决 (Overall Verdict)

### 当前状态：**Reject**

**理由不是"研究没价值"，而是"稿件没完成"。**

这是一堆高质量的研究笔记、一篇诚实的自我诊断（paper-revision-plan-v2.md）、两篇优秀的科普文章（DEV.to）——但**不是一篇论文**。当前状态下缺少：

- (a) 单一完整稿件
- (b) 任何图表
- (c) 完整的文献引用
- (d) 一致的数据
- (e) 最低标准的实验 rigor（第二评分者 / 盲法 / 安慰剂对照）

### 如果作者完成了 paper-revision-plan-v2.md Phase A+B：**Weak Accept**（适合 Workshop）

具体条件：
1. 统一 n-count + 澄清什么数据实际存在
2. 找了一个第二评分者（即使 kappa 只有 0.5-0.6）
3. 跑了安慰剂对照（token-matched generic config，10 任务即可）
4. 重写了标题和摘要（去掉 isomorphism claim）
5. 补了完整的 Related Work（含 CAI, HyperAgents, loop engineering，带完整引用）
6. 做了架构图 + 结果表
7. 写成了单文件 LaTeX 稿件（4-6 页，workshop 格式）

满足以上条件后，这篇论文在 ACL SRW 或 CHI LBW 是**可辩护的**。它的真实贡献——Prose Barrier 框架化 + config 层自指校验架构——在 workshop 级别有区分度。

### 适合的 Venue

| Venue | 适合度 | 理由 |
|-------|:--:|------|
| **ACL SRW** | ⭐⭐⭐⭐ | 明确欢迎本科生工作+负结果。理论贡献权重高于实验贡献。**最适合** |
| **CHI LBW** | ⭐⭐⭐ | 接受进行中工作。需要 single-user longitudinal case study 的 framing |
| **arXiv** | ⭐⭐⭐⭐⭐ | 不做 peer review，建立优先权。**无论投哪里，应该先放 arXiv** |
| **AIES** | ⭐⭐ | 需要安全/伦理 framing。"防止单人开发者被配置漂移误导"的安全性论点偏弱 |
| **CSCW** | ⭐ | 需要多用户研究，本工作是单用户 |
| **NeurIPS Workshop** | ⭐⭐ | 实验 rigor 要求太高，不适合当前阶段 |

### 给作者的最后建议

你有一个真实的研究洞察（Prose Barrier），一个可工作的原型系统（双机械层），和一种罕见的自我诊断能力（paper-revision-plan-v2.md 的质量证明你知道问题在哪）。这在独立完成的本科生工作中是 outstanding 的。

但你现在拿出来的不是一篇论文——是一堆研究笔记。教授打开你的仓库，看到的是碎片而非成果。**先修完审计报告中列出的 7 项必做修复，把数据统一了，图表做了，Related Work 补了，然后写一个单一的完整的 4-6 页 LaTeX 稿件。** ACL SRW 的截止日期通常在 12 月——你有 5 个月。这 5 个月够你把一个 2/10 的实验变成 6/10，把一个 3/10 的稿件变成 7/10。

---

## 评分卡汇总

| 维度 | 评分 | 关键问题 |
|------|:--:|------|
| **创新度** | 6/10 | Prose Barrier 框架化有原创性；自修改过度宣称；isomorphism claim 必须删除 |
| **实验 Rigor** | 2/10 | n-count 矛盾致命；单人评分无盲法；无安慰剂对照；无第二评分者；8/8 全满分 |
| **理论 Depth** | 5/10 | Prose Barrier 缺乏形式化和文献对话；五层拓扑是分类框架非理论模型 |
| **写作** | 3/10 | 无单一完整稿件；零图表；引用是占位符；术语和数据不一致 |
| **综合裁决** | **Reject**（当前）→ **Weak Accept**（修完后，适合 ACL SRW / CHI LBW） |
