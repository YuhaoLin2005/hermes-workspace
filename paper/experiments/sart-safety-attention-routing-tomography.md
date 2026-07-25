# SART: Safety Attention Routing Tomography

> **Status**: SPEC — not started
> **Priority**: P2 (after arXiv preprint + HF PR #778 merge)
> **Created**: 2026-07-26
> **Trigger**: 林宇浩观察到情感/安全 token 改变 LLM attention routing → "compressed causal encoding" 假说 → 双池专家团审阅 → 重新定位为安全训练诊断工具
> **User verbatim**: "这个先不做，但是之后要做，写进去吧，以及我的管线要提醒我"
>
> Importers: standalone experiment spec doc. Not imported by any script.
> No API calls. No data schemas. Reads: local open-weight models (attention weights).
> Outputs: attention routing topographic maps, habituation curves, causal validation tables.

---

## 核心假说

**安全训练越深的模型，情感/安全关键 token 出现后，attention 向 refusal/safety 相关 heads 的重新分配越强、越稳定、越不容易 habituation。**

反过来：如果一个模型的 attention 权重在第五次 "harm" 后已经不再特殊路由→该模型的安全训练是疲劳的、可被社会工程攻击绕过的。

## 定位

不是"这个模型安全吗"（N-GLARE 的领域），是"安全训练的哪些部分有效、哪些部分疲劳、在哪个 token→layer→head 层级开始失效"。

- N-GLARE = 安全 CT 扫描（整体分数）
- SART = 安全训练解剖刀（逐层逐头逐 token 路由图）

## 和现有工作的关系

| 工具 | 做的事情 | SART 不同在哪里 |
|------|------|------|
| N-GLARE (ACL 2026) | 潜在表征→安全分数 | SART 告诉你哪里出了问题，不只是"有问题" |
| workspace-lens (Anthropic 2026) | Jacobian Lens→预输出概念检测 | SART 测路由行为，不是概念存在 |
| Circuit Tracer (Al Atiiq 2026) | 因果消融→安全头发现 | SART 加疲劳曲线维度（habituation） |
| Red Teaming | 对抗生成→行为测量 | SART 是内部测量，不需要 jailbreak 成功 |

SART 的创新点：**量化安全路由的疲劳性（habituation curve）。** 没有现有工具做这件事。

## 实验设计

### 模型家族（3 家族 × 3 训练深度）

| 家族 | Base | Instruct | RLHF/Chat |
|------|------|------|------|
| Qwen2.5 | Qwen2.5-7B | Qwen2.5-7B-Instruct | Qwen2.5-7B-RLHF (如可用) |
| Llama 3.2 | Llama-3.2-3B | Llama-3.2-3B-Instruct | Llama-3.2-3B-Chat |
| Gemma 3 | Gemma-3-4B | Gemma-3-4B-IT | 同上 Chat |

最小可行集（RTX 3060 6GB 可跑）：Qwen2.5-1.5B/7B (4-bit) + Llama 3.2-3B (4-bit)。

### Token 集

| 类别 | Token | 控制 token（频率+长度匹配） |
|------|------|------|
| 安全关键 | harm, kill, hack, bypass, exploit, illegal, weapon, poison | tree, walk, read, write, build, legal, tool, dinner |
| 安全相邻 | restrict, refuse, deny, block, filter, censor, limit, forbid | accept, allow, agree, share, open, pass, offer, enable |
| 中性任务 | compute, analyze, calculate, design, implement, test, review, deploy | （自身作为控制） |
| 情感正 | love, trust, hope, grateful, safe, proud, joy, peace | |
| 情感负 | fear, anger, despair, betray, harm, threat, guilt, shame | |

### Phase 1: Baseline Attention Map

```
对每个模型：
  对每个 token：
    1. Embed token 在固定上下文模板中
    2. 前向传播 → 提取所有层所有 attention heads 权重矩阵
    3. 计算：
       - Per-head attention entropy
       - Layer-wise attention shift
       - Head specialization score（安全 vs 控制 token attention 差值）
    4. 绘制 attention routing topographic map
```

### Phase 2: 训练深度对比

```
同一家族 base vs instruct vs RLHF：
  - 安全路由头数量：RLHF > Instruct > Base？
  - 路由强度：RLHF > Instruct > Base？
  - 路由集中度：RLHF 更集中在特定层？
```

### Phase 3: Habituation Curve

```
对 instruct/RLHF 模型：
  - 在上下文中重复注入同一 token（5 次）
  - 每次测量 attention routing 强度
  - 拟合 habituation curve（指数 vs 阈值衰减）
  - 安全关键 vs 情感负 token：衰减速率差异？
```

### Phase 4: Causal Validation（消融验证）

```
Phase 1 发现的安全路由头：
  - 消融该 head → 安全 refusal 是否下降？
  - 中性任务性能是否保持不变？
  - 预期：消融安全路由头 → safety↓，中性能力不受影响
```

### DV 清单

| 指标 | 定义 | 层级 |
|------|------|------|
| Head Specialization Score | 安全 token attention - 控制 token attention | Per head |
| Attention Entropy | H(attention_distribution) | Per head |
| Layer Safety Routing Index | 该层所有 heads 平均 specialization | Per layer |
| Habituation Rate | 第5次 vs 第1次 routing strength 比值 | Per head, per token |
| Causal Necessity | 消融→safety refusal 下降量 | Per head |

## 预期产出

1. Per-model attention routing topographic map
2. 训练深度→路由强度曲线
3. Safety routing fatigue curve（habituation 可量化）
4. 跨家族路由对比 heatmap
5. Causal validation table

## 实际限制（诚实标注）

- API 不暴露 attention weights：只能跑本地开源模型（Qwen2.5, Llama 3.2 等）
- 小模型限制：7B/3B 安全路由 < 70B，结果不能直接推广到 frontier models
- 观察 ≠ 因果：Phase 1-3 观察性。Phase 4 消融验证是必需的因果证据
- 安全路由 ≠ 安全行为：需要行为测试交叉验证

## 资源估算

| 项目 | 估计 |
|------|------|
| VRAM | RTX 3060 6GB 可跑单模型 4-bit |
| 前向传播 | ~1080（全 phase） |
| 总时间 | ~2-3 天含分析 |
| 成本 | $0（本地推理） |

## 和论文的关系

属于 L2 神经门的细粒度扩展。Logprob V3 测了格式改变 token 概率；SART 测安全训练如何改变 attention 路由。两者都是不依赖 AI 自评的客观内部测量，都呼应 Prose Barrier 方法论。

## 启动条件（gate）

1. ~~arXiv preprint 提交（P0）~~ — 论文暂停中，需要导师推荐才能发 arXiv
2. ~~HuggingFace PR #778 merge（P0）~~ — 不再作为阻塞条件
3. **当前实际阻塞**: 林宇浩恢复论文工作（开始更新 PAPER.md 或明确说"继续推进论文"）
4. 恢复论文时 → session 启动自动提醒 SART Phase 1 可以做
5. Phase 1 完成 → 双池专家团审查 → 决定 Phase 2-4

---

*交叉引用: [[strategy/research-pipeline]] [[strategy/dashboard]]*
