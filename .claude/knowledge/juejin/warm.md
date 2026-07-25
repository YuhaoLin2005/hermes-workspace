# 掘金 Warm (≤60d, paper/tech series)
> 按需加载标题+finding。

```yaml
articles:
  - slug: juejin-150-tasks
    title: "我让 AI 跑了 150 个任务来证明它会守规矩。结论是：会——但有个前提"
    url: https://juejin.cn/post/7660861087914786862
    date: 2026-07-12
    domain: experiment
    reads: 19
    claims: [claim-2]
    devto: 150-tasks
    finding: "L1 Gate + ceiling effect"
    status: active

  - slug: juejin-neural-gate
    title: "文件系统门只能查'做了没'。我加了一层，查'懂了没'"
    url: https://juejin.cn/post/7660745750713073691
    date: 2026-07-11
    domain: experiment
    reads: 18
    claims: [claim-3]
    devto: neural-gate
    finding: "L2 Neural Gate——logprob差分检测约束穿透"
    status: active

  - slug: juejin-self-verify
    title: "你的 AI 说它守规矩。但它没法证明"
    url: https://juejin.cn/post/7660744199178108955
    date: 2026-07-11
    domain: architecture
    reads: 25
    claims: [claim-1]
    devto: self-verify
    finding: "Prose Barrier——自验证结构性不可靠"
    status: active

  - slug: juejin-identity
    title: "让1.5B模型记住'我是谁'有多难"
    url: https://juejin.cn/post/7660717249692696585
    date: 2026-07-11
    domain: architecture
    reads: 14
    finding: "小模型身份持久化"
    status: active

  - slug: juejin-power-analysis
    title: "测了10个领域就说模型没效果？功效分析告诉你为什么不该下结论"
    url: https://juejin.cn/post/7660675677138354227
    date: 2026-07-11
    domain: experiment
    reads: 15
    devto: zero-effect
    finding: "统计功效——小样本不能下结论"
    status: active

  - slug: juejin-sft-random
    title: "专家团80%时间分不出模型好坏：我的SFT循环是怎么变成随机游走的"
    url: https://juejin.cn/post/7660744199176667163
    date: 2026-07-11
    domain: experiment
    reads: 15
    finding: "SFT评估——专家团分不出好坏"
    status: active

  - slug: juejin-rouge
    title: "ROUGE-L=0.0不是bug，是ROUGE量不了的东西"
    url: https://juejin.cn/post/7660745750711631899
    date: 2026-07-11
    domain: experiment
    reads: 16
    finding: "自动指标失效——量错了东西"
    status: active

  - slug: juejin-qlora-pitfalls
    title: "6GB显存上做QLoRA微调的5个翻车记录"
    url: https://juejin.cn/post/7660496737153925147
    date: 2026-07-11
    domain: tutorial
    reads: 18
    finding: "QLoRA实操踩坑"
    status: active

  - slug: juejin-loss-down
    title: "loss从8.11降到0.77，模型为什么反而更差了"
    url: https://juejin.cn/post/7660007537018617883
    date: 2026-07-10
    domain: experiment
    reads: 35
    finding: "Loss≠质量，SFT过拟合陷阱"
    status: active

  - slug: juejin-anthropic
    title: "在DeepSeek上撞见了一个和Anthropic论文里一样的架构模式"
    url: https://juejin.cn/post/7659251094817341490
    date: 2026-07-08
    domain: architecture
    reads: 48
    devto: self-referential
    finding: "自指环——和Anthropic论文平行发现"
    status: active

  - slug: juejin-prompt-vs-qlora
    title: "30组对照实验告诉你：Prompt规则不是装饰品，但QLoRA内化还差得远"
    url: https://juejin.cn/post/7659671273129705522
    date: 2026-07-08
    domain: experiment
    reads: 22
    finding: "Prompt规则 vs QLoRA内化——30组对照"
    status: active
```
*tier: warm | count: 11 | 2026-07-24*
