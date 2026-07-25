# 模拟审稿人重评估报告

> ⚠️ **全部为 AI 模拟。** 基于 2026-07-11 首次评审后的修订进行重新评估。
> 修订内容：Logprob 探针 V3 实验 (n=40, d=+0.578)、四层架构系统化文档、
> Prose Barrier 理论框架、README 冷读改造、测量工具有效性叙事。
>
> 评估对象：https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/README.md
> 参考 DEV.to 文章：https://dev.to/yuhaolin2005/my-experiment-showed-zero-effect-a-statistician-told-me-my-measurement-was-broken-4g26

---

## 审稿人 #1：模拟 ACL/CHI 审稿人

### 重评分

| 维度 | 上次 (07-11) | 本次 (07-12) | 变化 | 理由 |
|------|:---:|:---:|:---:|------|
| 创新度 | 6/10 | 7/10 | +1 | Prose Barrier 从"一段话"升级为四层的统一理论脊柱。四层架构(L1→L4)的区分——绕过/潜入/改变/观察——比初稿的"三层"更有分析深度。Logprob 探针本身不新，但把它用作"绕过行为天花板测量内部表征"的方法论选择是聪明的。 |
| 实验 Rigor | 2/10 | 5/10 | +3 | **这是本次修订最大的改进。** Logprob V3 (n=40) 的 DV 直接从 API 读取，零人工评分——部分规避了单评分者问题。预验证探针池消除了 floor artifact——这是 measurement validity 的正面对待。双实验架构（先导 n=8→验证 n=40）为叙事增加了可信度。bootstrap CI + Bayes + LOO 是合适的稳健性检查。BUT：仍只有单模型(DeepSeek)，Causal Swap 仍是单评分者未盲，无跨模型复制。5/10 不是 8/10。 |
| 理论 Depth | 5/10 | 6/10 | +1 | Prose Barrier 现在有了清晰的架构含义——每层对应 Barrier 的一个操作（绕过/潜入/改变/观察）。这比初稿的"有三层"更有理论骨架。但核心主张（格式→注意力路由→行为）仍依赖 Pender(2026)的间接支持，缺乏直接因果证据。J-space 类比仍然是类比。 |
| 写作 | 3/10 | 6/10 | +3 | README 现在是一流的冷读文档——客观边界前置、30s 速查表、四层总览 ASCII 图、实验概览含评分者列、每层证据强度诚实标注。"我能做的和不能做的"部分诚实且有尊严。如果论文正文达到这个标准，Weak Accept 是合理的。 |

### 裁决

**上次**: Reject（当前）→ Weak Accept（修后适合 ACL SRW）
**本次**: **Weak Accept（ACL SRW）→ 可尝试 ACL 短论文（Findings）如果补上跨模型复制**

### 关键建议

1. **跨模型复制是下一个 10x 改进**。在 Claude 或 GPT-4 上跑同样的 40 探针实验——如果效应跨模型稳定，Rigor 从 5→7，论文可以从 SRW 升级到主会短论文。
2. **Causal Swap 的评分者问题仍未解决**。至少找一个人（同学/朋友）做 8 个 transcripts 的独立评分，算出真正的 κ。κ=−0.14 是 8 个样本的噪声估计——30 个样本的 κ 可能不同。
3. **论文正文需要和 README 同等质量**。README 现在是 7/10 的写作水平——但 PAPER.md 的 §6 仍然"最长但证据最弱"。
4. **"预验证探针池"本身就是一个小的方法论贡献**。可以考虑单独写一个 2 页的 short paper 讲 logprob-based 实验的 measurement validity 问题。

---

## 审稿人 #2：模拟 HCI 博士后（UCL）

### 视角

HCI 方向关注：用户研究 rigor、生态效度、诚实报告、对实践者的价值。

### 重评估

**上次核心批评**（07-11）：所有定量结果追溯回单评分者；结构倒置（最长章节证据最弱）；J-space 类比是隐喻不是机制。当前适合 workshop。

**本次评估**：

Logprob V3 实验给了我一些信心。DV 是客观的——token logprob 直接从 API JSON 读，没有任何人（作者本人也不行）能影响这个数字。这是真正的"客观测量"。先导 n=8 零效应→修复测量→验证 n=40 真实效应的叙事，比大多数本科生论文做得更好的 measurement validity 实践。

但我仍然有一些 concerns：

1. **生态效度问题**。40 个探针都是"二元选择 A/B"，这是一个高度人工的实验设置。真实世界的 agent 不会在每一步做 "A 或 B？" 的选择。logprob 差分告诉我们格式影响了内部表征——但内部表征的变化是否转化为真实世界中可观察的行为差异？Format A/B 合规实验说"不"（天花板效应）。所以 Logprob V3 证明了一个真实但可能在实际中没有可见后果的效应。这不是缺陷——这是诚实的——但需要明确讨论。

2. **四层架构的证据不均衡**。L1 有 150 任务和 19/19 行为测试——强。L2 有 40 探针——中。L3 的因果编码声称（格式→注意力路由→行为）仍然没有直接证据。L4 的"预测"还没验证过。论文的 center of gravity 在 L1，但 L3 占了最长篇幅。这个结构倒置问题仍然存在。

3. **对 HCI 社区的贡献**：我认为最大的 HCI 贡献是"机械门绕过 AI 自评"这个设计理念，以及诚实报告 κ=−0.14 的做法。HCI 社区重视 reflexive practice 和 limitations 的诚实讨论——这篇论文在这些维度上做得比大多数本科生论文好。

### 评分

| 维度 | 上次 | 本次 |
|------|:---:|:---:|
| 研究设计 | 3/10 | 5/10 |
| 效度 | 2/10 | 5/10 |
| 贡献清晰度 | 5/10 | 7/10 |
| 诚实度 | 8/10 | 9/10 |

### 裁决

**上次**: workshop 级（CHI LBW / DIS poster）
**本次**: **CHI LBW 可投 → 修后 CHI 短论文**

### 建议

- 把"Prose Barrier"的概念更早引入（现在藏在 §3.0 太晚了），它是整篇论文最原创的理论贡献
- 在 paper 正文中明确区分"Logprob V3 的 DV 是客观的"和"Causal Swap 的 DV 是主观的"——不同实验有不同效度水平
- HCI 审稿人会赞赏你"我能做的和不能做的"这个 section——保留它

---

## 审稿人 #3：模拟 ML/Agent 博士后（CMU）

### 视角

ML/Agent 方向关注：方法 novelty、实验 rigor、与 SOTA 的区分度、可复现性。

### 重评估

**上次核心批评**（07-11）：结构倒置；所有定量证据追溯回单评分者；GateGuard 实验验证了 L1 而非 L3；J-space 类比是 overclaim。

**本次评估**：

Logprob V3 实验在方法上做对了几件事：
- 预验证探针（消除 floor artifact）——这是做 logprob 实验的人应该做但很少做的事
- 双实验架构——先导+验证是成熟的方法论选择
- Bootstrap CI + Bayes factor + leave-one-out——分析 pipeline 是现代的
- DV 的客观性——从 API 读 token 概率，不经过人类判断

但我也需要指出：

1. **40 个探针不是 40 个独立样本**。同一个模型（DeepSeek V4 Pro）回答所有 40 个探针，探针之间的相关性没有建模。你报告的 SE=2.03 和 t(39)=3.65 假设探针独立——但它们有共享的模型参数、共享的温度噪声。这可能导致 Type I error inflation。如果要严格处理，应该用 mixed-effects model（probes as random effects nested within categories）或 cluster-robust SE。

2. **温度 0.2 的噪声**。你坦率地说了 DeepSeek T=0 返回 −9999 的问题。但 T=0.2 意味着每次运行会有不同的 logprob 值——你的实验只跑了一次。至少应该跑 3-5 次重复测量（相同探针多次调用）来估计 measurement reliability。这是基本的 test-retest 可靠性。

3. **效应量解释**。d=0.578 是中等效应——但"中等"在 logprob 空间意味着什么？+7.43 logprob 单位 ≈ 概率比 e^7.43 ≈ 1690:1？如果正确，这是巨大的。但 logprob 值似乎异常极端（baseline A-B 经常 >±30）。这可能是因为 top-20 logprobs 在 temperature=0.2 时仍然是确定性主导的——模型在大多数探针上非常确定选 A 或 B。如果是这样，effect size 在概率空间可能比 d=0.578 看起来更小。建议直接报告概率比（exp(differential)）而非仅报告 logprob 差分。

4. **Category × Format 不显著 (F=0.26)** ——这是一个重要的 null finding。但 4 组 × 10 探针的 ANOVA 可能 underpowered 来检测交互。n=10 per cell 检测中等交互效应（f=0.25）的 power 只有 ~30%。

### 评分

| 维度 | 上次 | 本次 |
|------|:---:|:---:|
| 方法 novelty | 5/10 | 6/10 |
| 实验 rigor | 2/10 | 5/10 |
| 分析恰当性 | 3/10 | 6/10 |
| 可复现性 | 6/10 | 8/10 |

### 裁决

**上次**: workshop 级
**本次**: **ACL SRW → 补 test-retest + mixed-effects model → Findings/Short Paper**

### 建议

1. **跑 test-retest**。随机选 10 个探针，每个跑 5 次重复。Report ICC (intraclass correlation) for logprob differential。如果 ICC > 0.8，T=0.2 噪声不是问题。
2. **用 mixed-effects model 替代 paired t-test**。`lmer(format_effect ~ 1 + (1|category/probe))`——这会给审稿人更多信心。
3. **报告概率比而非 logprob 差分**。`exp(syllogistic_A - syllogistic_B) / exp(imperative_A - imperative_B)` 比 +7.43 logprob 单位更直观。
4. **不要把 40 探针全部当作"pre-registered confirmatory"**。你用了全部 40 个来生成结果——没有 holdout。建议：留 10 个探针做真正的 holdout validation，只报告一次。这才是真正的 pre-registration。

---

## 三人共识

### 一致同意的改进

1. **实验 Rigor 从 2→5**（三人平均）。Logprob V3 的客观 DV + 预验证 + 双实验架构是实质性改进。
2. **写作从 3→6**（审稿人 #1）。README 现在是高质量的冷读文档。
3. **当前投稿级别**：三人一致认为 ACL SRW / CHI LBW 是合理目标。审稿人 #1 和 #3 认为修后可达主会短论文。
4. **诚实度**：三人一致认为论文的诚实报告（κ=−0.14, 单模型, 客观边界前置）是 notable strength。

### 一致指出的剩余问题

1. **跨模型复制**：三个人都说这是下一个最重要的改进
2. **Causal Swap 的评分者问题**：Logprob V3 部分规避了，但 Causal Swap 仍是单评分者
3. **L3 的证据仍然最弱**：四层中格式效应虽然被 Logprob V3 验证了，但因果机制（格式→注意力路由）仍无直接证据
4. **论文正文需要重构**：README 的质量应该映射到 PAPER.md

### 如果只做一件事

跨模型复制（Claude API 或 GPT-4 API 跑 20 个探针）。成本 ~$0.50。如果效应跨模型稳定 → 可以从 workshop 升级到 short paper。
