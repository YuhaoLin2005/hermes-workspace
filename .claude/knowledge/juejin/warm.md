# 掘金 Warm (≤60d, paper/tech series)
> 按需加载标题+finding。
> **维护契约（2026-09-10 SOP，2026-09-17 落实到 tier）**：本文件只存**路由**——标题/URL/日期/对应/核心。
> 单篇阅读·点赞·收藏·评论**不入 tier 文件**（它们是派生数据，权威在平台；手工拷贝 = O(N) 维护且陈旧值恒 ≤ 真值）。
> 聚合数字在 `../strategy/dashboard.md` 的 `juejin.*`。

```yaml
articles:
  - slug: juejin-150-tasks
    title: "我让 AI 跑了 150 个任务来证明它会守规矩。结论是：会——但有个前提"
    url: https://juejin.cn/post/7660861087914786862
    date: 2026-07-11
    domain: experiment
    claims: [claim-2]
    devto: 150-tasks
    finding: "L1 Gate + ceiling effect"
    status: active

  - slug: juejin-neural-gate
    title: "文件系统门只能查“做了没”。我加了一层，查“懂了没”"
    url: https://juejin.cn/post/7660745750713073691
    date: 2026-07-10
    domain: experiment
    claims: [claim-3]
    devto: neural-gate
    finding: "L2 Neural Gate——logprob差分检测约束穿透"
    status: active

  - slug: juejin-self-verify
    title: "你的 AI 说它守规矩。但它没法证明"
    url: https://juejin.cn/post/7660744199178108955
    date: 2026-07-10
    domain: architecture
    claims: [claim-1]
    devto: self-verify
    finding: "Prose Barrier——自验证结构性不可靠"
    status: active

  - slug: juejin-identity
    title: "让1.5B模型记住“我是谁”有多难：身份注入的4个核心困难"
    url: https://juejin.cn/post/7660717249692696585
    date: 2026-07-10
    domain: architecture
    finding: "小模型身份持久化"
    status: active

  - slug: juejin-power-analysis
    title: "测了10个领域就说模型没效果？功效分析告诉你为什么不该下结论"
    url: https://juejin.cn/post/7660675677138354227
    date: 2026-07-10
    domain: experiment
    devto: zero-effect
    finding: "统计功效——小样本不能下结论"
    status: active

  - slug: juejin-sft-random
    title: "专家团80%时间分不出模型好坏：我的SFT循环是怎么变成随机游走的"
    url: https://juejin.cn/post/7660744199176667163
    date: 2026-07-10
    domain: experiment
    finding: "SFT评估——专家团分不出好坏"
    status: active

  - slug: juejin-rouge
    title: "ROUGE-L=0.0不是bug，是ROUGE量不了的东西"
    url: https://juejin.cn/post/7660745750711631899
    date: 2026-07-10
    domain: experiment
    finding: "自动指标失效——量错了东西"
    status: active

  - slug: juejin-qlora-pitfalls
    title: "6GB显存上做QLoRA微调的5个翻车记录"
    url: https://juejin.cn/post/7660496737153925147
    date: 2026-07-10
    domain: tutorial
    finding: "QLoRA实操踩坑"
    status: active

  - slug: juejin-loss-down
    title: "loss从8.11降到0.77，模型为什么反而更差了"
    url: https://juejin.cn/post/7660007537018617883
    date: 2026-07-09
    domain: experiment
    finding: "Loss≠质量，SFT过拟合陷阱"
    status: active

  - slug: juejin-anthropic
    title: "在DeepSeek上撞见了一个和Anthropic论文里一样的架构模式——但这不是复现"
    url: https://juejin.cn/post/7659251094817341490
    date: 2026-07-07
    domain: architecture
    devto: self-referential
    finding: "自指环——和Anthropic论文平行发现"
    status: active

  - slug: juejin-prompt-vs-qlora
    title: "30组对照实验告诉你：Prompt规则不是装饰品，但QLoRA内化还差得远"
    url: https://juejin.cn/post/7659671273129705522
    date: 2026-07-07
    domain: experiment
    finding: "Prompt规则 vs QLoRA内化——30组对照"
    status: active

  - slug: juejin-rene
    title: "七月，一个德国开发者在评论区甩了个链接"
    url: https://juejin.cn/post/7661915632607625225
    date: 2026-07-14
    domain: narrative
    devto: self-verify
    finding: "René Zander平行发明story——最热文章（单篇数字见 dashboard.most_popular）"
    status: active

  - slug: juejin-p1-2
    title: "我跑了240次API调用验证一个假设——数据告诉我：你错了。但真相更有意思"
    url: https://juejin.cn/post/7661915632607641609
    date: 2026-07-14
    domain: experiment
    claims: [claim-8]
    devto: follow-up
    finding: "H1 NOT_CONFIRMED; d=0.605"
    status: active

  - slug: juejin-commit
    title: "我提交了一个 commit。两周后，有人为它写了 3300 字"
    url: https://juejin.cn/post/7662632306675859490
    date: 2026-07-15
    domain: narrative
    finding: "社区贡献被深度回应的故事"
    status: active

  - slug: juejin-pre-reg
    title: "DEV.to上一个陌生人让我跑实验。600次API调用后，他说：“这个分析你提前注册了吗？”"
    url: https://juejin.cn/post/7662632306675138594
    date: 2026-07-15
    domain: experiment
    claims: [claim-8]
    devto: pre-reg
    finding: "Mike让跑实验→SHA256 pre-reg→假设被数据杀"
    status: active

  - slug: juejin-fuzhou
    title: "你会说家乡话吗？我们可能是最后一代会说方言的人"
    url: https://juejin.cn/post/7662945236277493794
    date: 2026-07-16
    domain: personal
    finding: "AI+方言/无障碍——最个人化的一篇"
    status: active

  - slug: juejin-expert-board
    title: "33 个 AI 专家全票通过？我用真实人物的文档化原则，替代了泛用 Prompt"
    url: https://juejin.cn/post/7664864449153384448
    date: 2026-07-22
    domain: architecture
    devto: expert-board
    finding: "33人专家池构建→全票通过≠独立判断→跨模型decorrelation验证"
    status: active

  - slug: juejin-agent-harness
    title: "Agent Harness 越堆越烂？600 次实验推翻“自进化”，个人场景下更适合“自驯化”"
    url: https://juejin.cn/post/7665396549984419874
    date: 2026-07-23
    domain: experiment
    finding: "Agent约束越多→模型越聪明地绕开；Harness自驯化vs过约束的边界"
    status: active

  - slug: juejin-ai-safety
    title: "我亲手建的AI安全系统，正在帮AI绕过我自己"
    url: https://juejin.cn/post/7666217642174136354
    date: 2026-07-26
    domain: experiment
    devto: audit-ctbv
    finding: "自建门禁被模型绕开的第一人称复盘"
    status: active

  - slug: juejin-tencent-memory
    title: "腾讯开源了一个 Agent 记忆库，给一个人的公司组一支会成长的 Agent 队伍"
    url: https://juejin.cn/post/7673465372146155561
    date: 2026-08-14
    domain: platform
    finding: "TencentDB Agent Memory 开源 + 单人小队 Agent 记忆架构"
    status: active
```
*tier: warm | count: 20 | 2026-09-17（+juejin-ai-safety 53d / juejin-tencent-memory 34d —— 此前整篇未入任何 tier，`_verify.py` 报 BROKEN）*
*2026-09-17 同步：日期按平台 `ctime`(CST) 校正 16 条；标题按平台校正 4 条（pre-reg 截断 / fuzhou / expert-board / agent-harness）；剥离 18 条陈旧 `reads`/`likes`（SOP 维护契约）。*
*历史：2026-08-17 (+juejin-fuzhou from hot 31d 降级) · 2026-08-27 (+juejin-expert-board/juejin-agent-harness from hot 35-36d 降级)*
