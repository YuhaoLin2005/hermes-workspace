# 掘金文章索引

> 23 posts published (as of 2026-10-11).
> platform_published: 23 | last_verified: 2026-10-11
> 核验方式：公开 API `article/query_list`（user_id 见下）→ 平台自报 `count` + 逐篇 `ctime`。
> **2026-10-11 复核**：`count` = **23**（较 10-02 增 1 —— 10-09《我的 Agent 迁移"成功"了》）；索引 `### [` 条目数 = 23 = platform_published，**无漏索引**。（其中 1 篇为方言人文，"技术内容"口径 = 22）
> ⚠️ 聚合数 **API 给得了**（2026-10-12 实测订正 —— 原文写「API 给不了」，是错的）：
> `query_list` 逐篇返回 `view_count` / `digg_count` / `collect_count` / `comment_count`。
> **实测与创作者中心同口径**：likes 41 / bookmarks 27 与 9-27 浏览器读数**逐字相同**。
> **2026-10-12 用户裁决：API 为主源**，不再每回开浏览器。刷新：`python knowledge/_platform_verify.py`
> 掘金=中文读者，声音≠DEV.to。写掘金文章前必读 voice-reference.md 掘金声音规则。

> **维护契约（2026-09-10 起）**：本索引只存**路由信息**（标题/URL/日期/对应/核心）。
> 单篇阅读·点赞·收藏·评论数**不入本文件**——它们是派生数据，权威在平台（创作者中心→数据中心→单篇分析）。
> 聚合数字在 `../strategy/dashboard.md`。理由：手工拷贝 22 篇 × 5 个数字 = O(N) 维护且陈旧值恒 ≤ 真值，
> `_check_kb.py` 结构上抓不到它烂掉；而"文章整篇没入索引"这个真实故障只需 1 个计数就能抓。
> 刷新流程：浏览器过一遍创作者中心 → 改 `platform_published` + `last_verified` 两个数 → 补新篇 → 收工。

## 论文实验系列（中译版，7篇）

### [juejin-150-tasks] 我让 AI 跑了 150 个任务来证明它会守规矩。结论是：会——但有个前提
- **URL**: https://juejin.cn/post/7660861087914786862
- **Published**: 2026-07-11 *(平台 ctime；原记 07-12 有误，2026-09-17 校正)*
- **DEV.to 对应**: [150-tasks]

### [juejin-neural-gate] 文件系统门只能查"做了没"。我加了一层，查"懂了没"
- **URL**: https://juejin.cn/post/7660745750713073691
- **Published**: 2026-07-10 *(平台 ctime；原记 07-11 有误，2026-09-17 校正)*
- **DEV.to 对应**: [neural-gate]

### [juejin-self-verify] 你的 AI 说它守规矩。但它没法证明
- **URL**: https://juejin.cn/post/7660744199178108955
- **Published**: 2026-07-10 *(平台 ctime；原记 07-11 有误，2026-09-17 校正)*
- **DEV.to 对应**: [self-verify]

### [juejin-pre-reg] DEV.to上一个陌生人让我跑实验。600次API调用后，他说："这个分析你提前注册了吗？"
- **URL**: https://juejin.cn/post/7662632306675138594
- **Published**: 2026-07-15 *(平台日期；索引原记 7-16 有误，2026-09-10 校正)*
- **DEV.to 对应**: [pre-reg] (叙事版)

### [juejin-p1-2] 我跑了240次API调用验证一个假设——数据告诉我：你错了。但真相更有意思
- **URL**: https://juejin.cn/post/7661915632607641609
- **Published**: 2026-07-14 *(平台日期；索引原记 7-15 有误，2026-09-10 校正)*
- **DEV.to 对应**: [follow-up]

### [juejin-agent-harness] Agent Harness 越堆越烂？600 次实验推翻"自进化"，个人场景下更适合"自驯化"
- **URL**: https://juejin.cn/post/7665396549984419874
- **Published**: 2026-07-23
- **DEV.to 对应**: (无直接对应——Agent Harness 自驯化主题综合文)
- **核心**: Agent 约束越多→模型越聪明地绕开；Harness 自驯化 vs 过约束的边界

### [juejin-ai-safety] 我亲手建的AI安全系统，正在帮AI绕过我自己
- **URL**: https://juejin.cn/post/7666217642174136354
- **Published**: 2026-07-26 *(2026-09-10 补录——本篇此前整篇未入索引)*
- **DEV.to 对应**: 待核（与 [audit-ctbv] 同日发布，主题同为门被绕开，未逐字比对）
- **核心**: 自建门禁被模型绕开的第一人称复盘

## 社区/叙事系列（4篇）

### [juejin-rene] 七月，一个德国开发者在评论区甩了个链接 🔥 最热
- **URL**: https://juejin.cn/post/7661915632607625225
- **Published**: 2026-07-14 *(平台日期；索引原记 7-15 有误，2026-09-10 校正)*
- **核心**: René Zander 平行发明 story

### [juejin-commit] 我提交了一个 commit。两周后，有人为它写了 3300 字
- **URL**: https://juejin.cn/post/7662632306675859490
- **Published**: 2026-07-15 *(平台日期；索引原记 7-16 有误，2026-09-10 校正)*
- **核心**: 社区贡献被深度回应的故事

### [juejin-expert-board] 33 个 AI 专家全票通过？我用真实人物的文档化原则，替代了泛用 Prompt
- **URL**: https://juejin.cn/post/7664864449153384448
- **Published**: 2026-07-22
- **DEV.to 对应**: [expert-board]
- **核心**: 构建33人专家池→全票通过只是开始；命名原则锚定→去关联前提→跨模型decorrelation验证

### [juejin-tencent-memory] 腾讯开源了一个 Agent 记忆库，给一个人的公司组一支会成长的 Agent 队伍
- **URL**: https://juejin.cn/post/7673465372146155561
- **Published**: 2026-08-14 *(2026-09-10 补录——本篇此前整篇未入索引)*
- **DEV.to 对应**: 待核
- **核心**: TencentDB Agent Memory 开源 + 单人小队 Agent 记忆架构

## 微调/QLoRA系列（5篇）

### [juejin-loss-down] loss从8.11降到0.77，模型为什么反而更差了
- **URL**: https://juejin.cn/post/7660007537018617883
- **Published**: 2026-07-09 *(平台 ctime；原记 07-10 有误，2026-09-17 校正)*
- **核心**: Loss≠质量，SFT过拟合陷阱

### [juejin-sft-random] 专家团80%时间分不出模型好坏：我的SFT循环是怎么变成随机游走的
- **URL**: https://juejin.cn/post/7660744199176667163
- **Published**: 2026-07-10 *(平台 ctime；原记 07-11 有误，2026-09-17 校正)*

### [juejin-rouge] ROUGE-L=0.0不是bug，是ROUGE量不了的东西
- **URL**: https://juejin.cn/post/7660745750711631899
- **Published**: 2026-07-10 *(平台 ctime；原记 07-11 有误，2026-09-17 校正)*

### [juejin-qlora-pitfalls] 6GB显存上做QLoRA微调的5个翻车记录
- **URL**: https://juejin.cn/post/7660496737153925147
- **Published**: 2026-07-10 *(平台 ctime；原记 07-11 有误，2026-09-17 校正)*

### [juejin-prompt-vs-qlora] 30组对照实验告诉你：Prompt规则不是装饰品，但QLoRA内化还差得远
- **URL**: https://juejin.cn/post/7659671273129705522
- **Published**: 2026-07-07 *(平台 ctime；原记 07-08 有误，2026-09-17 校正)*

## 身份/架构系列（3篇）

### [juejin-identity] 让1.5B模型记住"我是谁"有多难：身份注入的4个核心困难
- **URL**: https://juejin.cn/post/7660717249692696585
- **Published**: 2026-07-10 *(平台 ctime；原记 07-11 有误，2026-09-17 校正)*

### [juejin-anthropic] 在DeepSeek上撞见了一个和Anthropic论文里一样的架构模式——但这不是复现
- **URL**: https://juejin.cn/post/7659251094817341490
- **Published**: 2026-07-07 *(平台 ctime；原记 07-08 有误，2026-09-17 校正)*

### [juejin-power-analysis] 测了10个领域就说模型没效果？功效分析告诉你为什么不该下结论
- **URL**: https://juejin.cn/post/7660675677138354227
- **Published**: 2026-07-10 *(平台 ctime；原记 07-11 有误，2026-09-17 校正)*

## 平台/产品系列（2篇）

### [juejin-compact] 你的Claude聊到一半开始"编"——我翻了459个会话的压缩记录，发现这不是你的幻觉
- **URL**: https://juejin.cn/post/7651461757568286772
- **Published**: 2026-06-16 *(平台 ctime；原记 ~06-19 有误，2026-09-17 校正)*

### [juejin-prompt-boundary] 别瞎调 Prompt 了——跑完 100 次实验，我搞懂了模型的能力边界在哪
- **URL**: https://juejin.cn/post/7615900016812834867
- **Published**: 2026-03-12 *(第一篇掘金；平台 ctime 已确认，原 `~` 近似标记于 2026-09-17 去除)*

## 人文系列（1篇）

### [juejin-fuzhou] 你会说家乡话吗？我们可能是最后一代会说方言的人
- **URL**: https://juejin.cn/post/7662945236277493794
- **Published**: 2026-07-16 *(平台日期；索引原记 7-17 有误，2026-09-10 校正)*
- **核心**: 最个人化的一篇——AI+方言/无障碍

## 迁移/工程系列（1篇）

### [juejin-agent-migration] 我的 Agent 迁移"成功"了：每道门都在册，没有一道能跑
- **URL**: https://juejin.cn/post/7694576718061355059
- **Published**: 2026-10-09 *(平台 ctime)*
- **DEV.to 对应**: [agent-migration]

## DEV.to ↔ 掘金 对应表

| DEV.to | 掘金 |
|--------|------|
| [150-tasks] | [juejin-150-tasks] |
| [neural-gate] | [juejin-neural-gate] |
| [self-verify] | [juejin-self-verify] + [juejin-rene] |
| [pre-reg] | [juejin-pre-reg] |
| [follow-up] | [juejin-p1-2] |
| [self-referential] | [juejin-anthropic] |
| [forget-protocol] | [juejin-identity] |
| [zero-effect] | [juejin-power-analysis] |
| [compact-dumber] | [juejin-compact] |
| [drift-metric] | [juejin-loss-down] |
| [expert-board] | [juejin-expert-board] |
| [audit-ctbv] | [juejin-ai-safety] (待核) |
| [dpo-causal] | — (待翻译) |
| [agent-migration] | [juejin-agent-migration] |
| — (无DEV.to对应) | [juejin-sft-random] [juejin-rouge] [juejin-qlora-pitfalls] [juejin-prompt-vs-qlora] [juejin-commit] [juejin-fuzhou] [juejin-prompt-boundary] [juejin-agent-harness] [juejin-tencent-memory] |

## 掘金声音规则（≠DEV.to）

- 中文叙事化、更个人化、可以有情感
- 标题风格: "我X了...结果是Y" 非 "I did X"
- 可以有 emoji（DEV.to 不用）
- 长度更灵活，无硬约束
- 详见 voice-reference.md 掘金部分

---

*最后更新: 2026-09-17 — 22/22*
*2026-09-17 核验：公开 API `article/query_list` 翻页取全 22 篇，平台自报 `count=22`，与索引逐条一致，**0 篇缺失**。日期按 `ctime`(CST) 批量校正 12 条 —— 口径经 5 条既有浏览器校正值交叉验证（5/5 命中）。聚合数本轮未做浏览器核验，dashboard 保持 2026-09-10 值不动。*
*数据来源: 创作者中心→内容管理→文章管理（全部 23 = 已发布 22 + 未通过 1）*
*单篇数字权威: https://juejin.cn/creator/data/content/article/entire*
*交叉引用: [[../devto/articles]] [[../../paper/claims]]*
