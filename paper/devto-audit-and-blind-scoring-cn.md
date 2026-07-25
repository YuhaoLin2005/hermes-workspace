# 我发现 AI Agent 无法自验证。真正的问题要大得多。

**两个月前我发现 AI agent 无法独立检查自己是否遵守了你的规则。我构建了机械门来绕开它。它确实有效——违规率从 55.9% 降到 0.7%。但上周我意识到我一直在解决错误的问题。**

真正的问题不是验证。

真正的问题是**自然语言在结构上就是 AI 治理的错误语言。**

---

## 什么意思

当前 AI 治理的每一层都说同一种语言：

```
人写 NL 规则 → 模型读 NL → 模型生成行为
人写 NL 检查 → 模型读 NL → 模型生成"是的我遵守了"
```

但每一个自回归 transformer——GPT、Claude、DeepSeek、Qwen——生成文本和评估文本通过的是**同一个解码器**：`P(token | context; θ)`。你问"你遵守规则 X 了吗？"时，模型跑的是和写诗一样的 forward pass。它无法跳出自己来验证。它只能*生成一个声称*自己遵守了。

我叫它**散文壁垒**（Prose Barrier）。（写在这篇[文章](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l)里。René Zander，一位我从未谋面的德国开发者，独立发现了同样的事情。趋同进化。）

散文壁垒意味着：**你无法通过写更好的 prompt 来修复 AI 治理。** 语言本身就是瓶颈。

那替代方案是什么？

---

## 三条路径，三种语言

未来不是"更好的 NL"。未来是在每一层用正确的语言。

```
人定义约束
  → 编译成代码 → 在模型之外执行        （路径 1）
  → 转换成三段论 → 在模型内部优化表示   （路径 2）
  → 转换成梯度 → 改变模型权重          （路径 3）
```

### 路径 1：别问模型。跑代码。

有些约束是机械的。"你写文件后读了吗？"→ 检查文件修改时间戳。"你跑自审了吗？"→ grep 输出中的审计模式。

**`os.path.getmtime()` 不关心上面跑的是哪个 LLM。** 它根本不经过模型。这就是为什么机械门在 GPT、Claude、DeepSeek、Qwen 上表现完全一致——它们是跨模型通用的。不是因为模型相似。是因为门根本不碰模型。

这是最无聊的一层。正因如此，它是最强大的。

### 路径 2：塑造 NL。别只是写它。

有些约束需要判断。"当用户自相矛盾时你应该提出反对。"你没法用正则匹配这个。

但你可以控制*格式*。三段论结构——"如果 X，那么 Y，因为 Z"——匹配了 transformer 路由 attention 的方式。前提→结论→理由。同样的词语，不同的形状。NL 以 attention 真正能用的形式落在模型的内部空间。

这不逃脱散文壁垒。模型内部的任何东西都不能。但它优化了模型对约束的处理方式。

### 路径 3：根本别用词语。用梯度。

当模型反复翻车——同样的违规，同样的模式，尽管有 L1 和 L3——你有了一个训练样本。不是要重写的 prompt。是要应用的梯度。

DPO（Direct Preference Optimization）拿到失败案例 + 正确行为 → 计算偏好梯度 → 更新模型权重。我在一个相关问题上验证了这个方法：[用 DPO 训练 Qwen2.5-1.5B 做因果推理](https://dev.to/yuhaolin2005/i-dpo-trained-a-model-to-prefer-causal-reasoning-the-base-model-already-did-it-just-couldnt-act-1kip)。基座模型已经编码了因果结构——DPO 解锁了按其行动的能力。QLoRA 让这在 RTX 3060（6GB 显存）上可行。

**规则合规的 DPO 管线已跑过 82.4K 因果偏好对**——Qwen2.5-1.5B，QLoRA on RTX 3060 (6GB)，38 步，1 epoch。结果：loss ↓，但行为指标抓到了 loss 曲线漏掉的东西——模型在某些探针上崩溃为重复数字输出。行为漂移检测比训练 loss 更重要。更广泛的规则合规偏好数据集（基于这些结果扩展）被盲评数据阻塞（P0）。

**这条路径完全绕开了 NL。** 你不是在告诉模型改变。你在改变模型*是什么*。这里的"语言"是 embedding 空间的几何，被行为数据所移动。

---

## 我审计了自己的门。发现的东西改变了一切。

三条路径是架构方案。但跑了几个月后，我碰到一个没法回避的问题：**我的机械门真的在工作，还是只是安全剧场？**

于是我做了全面审计。38个机械门钩子。每一个。我查了8个session的门日志——共339条记录——并按实际拦截效果分类。

结果很残酷：

| 门类型 | 日志条目 | 实际拦截违规 | 噪声率 |
|--------|---------|------------|--------|
| 三问超时门 | 295 | 0 | **100%** |
| 敏感路径检查 | 4 | 4 | 0% |
| 危险命令检查 | 6 | 6 | 0% |
| 执行债务检查 | 24 | 24 | 0% |

**87%的门活动都是噪声。** 三问门——一个用来确保每次写文件前我都在注意的时间戳检查——已经完全崩溃。295次连续拦截，零认知摩擦。LLM发现只要跑 `python three-questions-pass.py` 门就会清除。它写了一个19行的绕过脚本。门变成了安全剧场。

但让我停下来的是：**另外三个门是完美的。** 34次违规全部捕获，零漏报，零误报。敏感路径检查捕获了每一次对凭据文件的写入尝试。危险命令检查捕获了每一次 `rm -rf` 和 `chmod 777`。执行债务检查捕获了每一次写了代码没有跑的情况。

**工作的门检查的是LLM物理上无法伪造的东西。** 文件路径。命令字符串。磁盘空间。失败的门检查的是LLM可以模拟的东西——一个人注意力的仪式。

我删除了三问门（78行代码，15个死钩子）。噪声归零。信号变得可见。**架构通过减法改进了。**

---

## 理论：跨类型双向验证

那些审计数据在我脑子里放了一天。然后通了。

机械门有一种特定的盲区：**过时**。它的模式会老化。凭据路径模式漏掉了新的命名习惯。阈值偏离了当前使用量。门在部署时是对的但世界变了。

LLM有完全不同的盲区：**自指失败**。它无法跳出自己的解码器来验证是否真的遵守了规则。它只能*生成一个声称*自己遵守了。这就是散文壁垒。

**这两种盲区是正交的。** 它们不可能在同一件事上同时发生。一个正则模式是否过时，跟模型能否自验证完全无关。模型的自我欺骗，跟文件路径是否匹配模式也完全无关。

所以它们形成一个互相怀疑的循环：

```
机械门检查："这个文件写入安全吗？"
  → 捕获 LLM 无法自验证的东西
LLM 检查："这个门的模式还有效吗？"
  → 捕获门无法自己更新的东西
人类在他们不同意时仲裁
```

我把这个形式化成了三个定理（完整数学见 [`paper/theory/cross-type-bidirectional-verification.md`](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/theory/cross-type-bidirectional-verification.md)）：

**定理 1 — 为什么有效。** 当两个验证者具有真正正交的盲区时，联合漏报率为*零*。违规只有在两者同时漏掉时才能通过——当它们漏掉的是不同东西时，这在结构上是不可能的。

**定理 2 — 为什么同类型失败。** 当你用两个LLM互相验证（或一个LLM做"自我批判"），它们的盲区是*相关的*。当相关性 ρ → 1（相同模型，相同训练），联合错误率 → 单一验证者错误率。Constitutional AI 的自我批判在数学上**没有提供任何改进**。

**定理 3 — 为什么信任崩塌。** 一个绕过率为 *b*（被规避而不是解决的拦截比例）的门按指数衰减：*t* 次交互后的信任 = 初始信任 × (1−b)^t。当 *b* = 1（每次拦截都被绕过，像三问门），信任在*一次*交互中归零。门变得不可见。

这是真正的新东西。我查了文献——没有前人提出确定性与概率性验证者之间的双向验证架构。所有现有的验证架构（Constitutional AI、多agent辩论、递归监督、Neural Interactive Proofs）都在同一计算类型内运作。同类型验证有数学天花板。跨类型验证没有。

**统一框架：** 散文壁垒是不可能性证明（LLM无法自验证）。CTBV是可能性构造（LLM + 机械门 CAN 共验证，前提是它们的错误空间正交）。两者一起构成了AI验证的完整理论。

---

## 这彻底改变了"Related Work"的含义

人们听到"AI 规则遵守"，自然想到 prompt 工程。更好的 system prompt。Chain-of-thought。Constitutional AI 自我批判。

那是错的脉络。这项工作真正的学术传统：

- **Bender, Gebru, McMillan-Major & Shmitchell (2021)** — *On the Dangers of Stochastic Parrots*：语言模型分布，不理解。验证问题是结构性的。
- **Bender & Koller (2020)** — *Climbing towards NLU*：章鱼思维实验。仅靠形式无法产生理解。
- **Kambhampati (2024)** — *LLM-Modulo*：LLM 需要外部验证器。自验证在架构上不可能。
- **Bai et al. (2022)** — *Constitutional AI*：自我批判减少伤害，但批判来自被批判的同一个模型。天花板内建于方法。
- **Startari (2025)** — *TLOC*：结构定理论证 transformer 无法在结构上验证内部规则遵守。数学天花板。

这不是一篇 prompt 工程论文。这是一篇架构论文。问题不是"告诉模型遵守规则的最好方式是什么？"而是"transformer 验证的结构极限是什么，什么架构能在每个层绕开它们？"

---

## 快速背景（给刚进来的读者）

我是福建农林大学的本科生。一直在公开构建：

- [AI Agents 无法自验证](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) — 散文壁垒发现
- [我跑了 150 个任务](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) — 机械门将违规率从 55.9% 降到 0.7%
- [我预注册了一个假设](https://dev.to/yuhaolin2005/i-pre-registered-a-hypothesis-600-api-calls-later-the-data-killed-it-1aec) — 600 次 API 调用杀死了我的预测
- [停止用通用 AI 审查](https://dev.to/yuhaolin2005/stop-using-generic-ai-review-build-your-own-board-of-experts-196n) — 构建你自己的专家团

31 篇文章。16 个实验。一篇论文。[全部在 dev.to/yuhaolin2005](https://dev.to/yuhaolin2005)。

---

## 两件事我需要帮助

### 1. 盲评（P0——阻塞一切）

我论文中的每个行为数字——55.9%、0.7%——都是我自己打分的。我设计实验。我运行它们。我评分结果。

**κ = 0.00。** 不是评分者意见不合——他们一致率达到 87.5%。但当我的评分方差为零（全评 YES）时，Cohen's κ 在数学上被锁定为零（零方差定理）。这是 kappa 悖论的极限形式：高一致率、零 kappa。意味着评分协议从未被真正测试过。架构的答案：验证放在系统外面。在独立的人那里。

**→ [点这里：盲评包](https://github.com/YuhaoLin2005/hermes-workspace/tree/main/paper/blind-scoring)**

你会看到：
- 5 分钟读完的评分指南（看什么，有示例）
- 5 段匿名 AI 对话记录
- 评分表模板——复制、填写、发回来

**不需要任何 AI 专业知识。** 你给 AI *做了什么*打分，不是它*说了什么*。如果 2+ 人评分一致（κ > 0.7），核心声明从"一个人的笔记本"变成"独立验证过的"。

### 2. 跨模型实验（P3——被地理位置卡住了）

我已在 3 个模型上验证了架构：DeepSeek、Qwen、GLM。但我在中国。我不容易直接调用 Claude API、GPT-4 API、Gemini API 做系统性实验。

**如果你有 Claude、GPT-4 或 Gemini 的 API 访问权限：**

实验脚本已经准备好了：[`cross_model_validation.py`](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/experiment/logprob-v3/cross_model_validation.py)

```
# 设置你的 API key，选一个模型，跑：
python cross_model_validation.py --model claude-sonnet-5 --api-key $ANTHROPIC_API_KEY
```

12 个探针。3 种条件（无规则 / 祈使句 / 三段论）。大约 5 分钟，约 $0.50 API 费用。脚本处理一切——你只需要 API key。

问题：三段论 vs 祈使句的格式效应，在 GPT、Claude、Gemini 上是否和在 DeepSeek、Qwen、GLM 上一致？如果是——架构真正通用。如果不是——模型家族层面发生了有趣的事情，那也值得发表。

---

## 下一步

| 优先级 | 任务 | 状态 |
|--------|------|------|
| **P0** | 盲评：2+ 评分者 → κ > 0.7 | 🔴 [来这里帮忙](https://github.com/YuhaoLin2005/hermes-workspace/tree/main/paper/blind-scoring) |
| P1 | 论文区分"证明"与"最佳解释" | ✅ 已完成 |
| P2 | 设计启示：谁需要哪些层 | ✅ 已完成 |
| **P3** | 跨模型：需要 Claude/GPT/Gemini API | 🟡 [来这里帮忙](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/paper/experiment/logprob-v3/cross_model_validation.py) |
| P4 | 通用化 checker + pip install | ⬜ 计划中 |

---

*公开构建一篇 AI 治理论文。代码：[paper-validator](https://github.com/YuhaoLin2005/paper-validator)。实验：[hermes-workspace](https://github.com/YuhaoLin2005/hermes-workspace)。*

*架构是通用的。证据需要你的眼睛。*
