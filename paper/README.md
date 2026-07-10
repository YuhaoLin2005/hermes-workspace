# Paper Materials — AI Agent Self-Verifying Configuration Integrity

> 林宇浩, FAFU 空间信息 23级. 2026-07-10.
> 给凯斌老师的补充材料——邮件里说了做了什么、卡在哪，这里是可以深入看的内容。

## 阅读指引（按你想了解的深度）

### 5分钟：了解核心想法
→ **[professor-meeting-onepager.md](professor-meeting-onepager.md)**
里面是：遇到了什么问题（agent配置漂移）、做了什么（4个机械门+双层检查）、30个任务的趋势、诚实的局限（单人评分/无安慰剂/RTX3060）、想请教什么。一页纸，不展开。

### 15分钟：看论文框架
→ **[paper-outline-part1.md](paper-outline-part1.md)**
里面是：论文大纲（Introduction→Related Work→Architecture→Experiments→Discussion→Conclusion）、Part1文件系统层的完整设计、Part2神经层的三阶段方案（v1关键词回响/v2 logprob差异/v3残差流探针）、竞品对比（HyperAgents/Ouro Loop等）、实验数据说明、已知局限和待办清单。

### 30分钟：看实验细节
→ **[paper-methods-draft.md](paper-methods-draft.md)** — 架构细节、实验设计、统计方法怎么选的
→ **[paper-trial-results.md](paper-trial-results.md)** — 12次treatment trial的原始记录，每次的任务、结果、validity caveats
→ **[paper-task-specs.md](paper-task-specs.md)** — 30个任务的具体规格，分5个领域
→ **[paper-scoring-template.md](paper-scoring-template.md)** — 5分类+3门评分标准

### 想了解最新进展（神经层突破）
文件系统层只检查"信息到没到"，不检查"信息有没有真的改变输出"。因为 agent 的自我评估和代码执行共享同一个 decoder——声明和行动从同一个分布采样。这是结构性约束，不是 prompt 工程能解的。

→ **[paper-outline-part1.md#part-2](paper-outline-part1.md)** 的 Part 2 章节——神经层三阶段完整方案：
  - **v1（已部署）**：约束回响检测——BODY.md 的规则关键词在输出中出现吗？86行Python，8个约束主题，全通过
  - **v2（已设计）**：Logprob 差异检测——用 DeepSeek `logprobs=True` 对比带/不带约束时 token 概率偏移。脚本已写好，等 API key
  - **v3（路线图）**：残差流线性探针——在 Qwen2.5-1.5B（RTX 3060 可行）训练探针检测约束信息可解码性

→ **[B-devto-neural-gate.md](B-devto-neural-gate.md)** — 英文，已发DEV.to。神经门的完整故事

→ **[A-devto-prose-barrier.md](A-devto-prose-barrier.md)** — 英文，已发DEV.to。为什么AI agent无法自我验证是结构性约束

### 背景
→ **[self-model.md](self-model.md)** — 系统自我认知文档（v0.10），记录架构演进。⚠️ AI辅助写成，不是客观研究报告
→ **[paper-revision-plan-v2.md](paper-revision-plan-v2.md)** — 专家审查后完整修订方案
→ **[paper-experiment-expansion.md](paper-experiment-expansion.md)** — 统计效力分析、要多少样本、双盲怎么做

## 一句话总结

文件系统层检查"到达"，神经层检查"穿透"。双层互补——因为 agent 的自我评估和代码生成共享同一 decoder，机械验证必须在信息流动的每一层都存在。

## 诚实状态

- 做了什么：4个文件系统门部署 + 神经层v1运行 + v2脚本写好 + v3设计完成 + 30任务对比 + 8追加（paper-trial-results.md记录）
- 没做到什么：没有第二评分者、没有双盲、没有安慰剂对照、v2缺API key、v3未实现
- 能声称什么："值得做更严格的实验"，不是"已经被证明有效"
- 需要什么帮助：方向判断 + 投稿建议
