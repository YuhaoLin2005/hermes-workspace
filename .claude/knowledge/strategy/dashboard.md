# 量化仪表盘

> 单一真相来源。每次 session 启动时读取 → AI 立刻知道"现在在哪里"。
> 做完任何事→更新对应数字。>`_check_kb.py` 2b 警告阈值 = 14 天（2026-07-25 曾收紧至 3 天，2026-09-10 校准回 14——平台数字需人工浏览器登录，实际节奏 ~10 天，3/7 天都每轮误报）。

```yaml
dashboard:
  synced_at: 2026-10-12T00:00:00Z  # 2026-10-12 **API 核验**（公开 API，非浏览器；followers 与掘金 total_views=展现数 API 无对应字段，仍为 2026-09-27 浏览器值，见各字段注）

  devto:
    articles: 33  # 2026-10-11 API 复核（/api/articles?username=yuhaolin2005&per_page=100 → 33）。较 9-27 浏览器 Posts 32 增 1 = 10-09《My Agent Migration Finished…》。⚠️ synced_at/last_updated 不动（本轮非浏览器核验）
    comments_written: 49  # 2026-08-14: 45 (8-12 verified) + 4 replies posted via browser automation (D3/D4/D5/D6)
    comments_received: 103  # 2026-10-12 API 复核（公开 API，非浏览器）；旧值 100  ｜ 原注: 2026-09-27 browser-verified（Total comments 100；8-15 基线 98，+2）。analytics 页「45 comments」为不同口径（写评论数），勿混
    followers: 615  # 2026-10-13 **用户人工复核**（登录态 nav）→ 权威值；9/27-10/12 记 621 系旧值，已更正（analytics "0 of 690" 为不同口径，不采用）
    total_reactions: 29  # 2026-10-12 API 复核（公开 API，非浏览器）  ｜ 原注: 2026-09-27 browser-verified (dashboard summary card)
    total_views: 1978  # 2026-10-12 API 复核（公开 API，非浏览器）；旧值 1788  ｜ 原注: 2026-09-27 browser-verified (was 1608 on 9-10, 1518 on 8-31) — 简历「1000+ 阅读量」仍成立
    notable_commenters: ['Dipankar Sarkar', 'Max Quimby', 'René Zander', 'Alex Shevchenko', 'CodeKitHub']
    unread_comments: 4  # 2026-10-10 全量 API 重核（91 篇帖子的讨论树，逐篇 nodes==comments_count）：确认 4 条真·未答 — jugeni 的 3b8jm(the-line, 07-15) / 3c0dc(pre-reg) / 3d96m(expert-board) / 3d96n(audit-ctbv)；其中 3b8jm 此前从未进过任何台账。alicespark 告别 + 5 条 alexshev 附和按「无问题」不计。四份草稿已就绪待发，见 devto/replies.md 2026-10-10 补录段

  juejin:
    articles: 23  # 2026-10-11 API 复核（content_api/v1/article/query_list → 23）。较 9-17 的 22 增 1 = 10-09 新篇。平台口径含 1 篇方言人文；简历用「技术 22」为独立标注口径。⚠️ 9-27 浏览器「文章管理」页未渲染故未复核；此值不来自 tier 求和
    total_reads: 5709  # 2026-10-12 API 复核（公开 API，非浏览器）；旧值 5615  ｜ 原注: 2026-09-27 browser-verified (creator center 文章阅读数; was 5324 on 9-10, 5159 on 8-31)
    total_likes: 41  # 2026-10-12 API 复核（公开 API，非浏览器）  ｜ 原注: 2026-09-27 browser-verified (creator center 文章点赞数; was 38 on 9-10, 36 on 8-31 — 8-27 曾降到 35，先降后回升)
    total_views: 80171  # 2026-09-27 browser-verified (creator center 文章展现数; was 70449 on 9-10, 68539 on 8-31)
    total_bookmarks: 27  # 2026-10-12 API 复核（公开 API，非浏览器）  ｜ 原注: 2026-09-27 browser-verified (creator center 文章收藏数; was 26 on 9-10, 25 on 8-31)
    total_comments: 12  # 2026-10-12 API 复核（公开 API，非浏览器）；旧值 13  ｜ 原注: 2026-09-27 browser-verified (creator center 文章评论数; was 10 on 9-10, 9 on 8-31)
    most_popular: juejin-rene_2685_reads  # 2026-08-01 from index (was 34_reads — stale)。⚠️ 单篇数 9-27 仍未复核（需进详情页逐篇）

  github:
    paper_validator_stars: 0  # 2026-08-01 gh api verified
    paper_validator_forks: 0  # 2026-08-01 gh api verified
    hermes_workspace_stars: 1  # 2026-08-05 gh api verified
    total_commits_since_july1: 131  # 2026-08-14 gh api: hermes-workspace(106) + paper-validator(25) + others. fu-garden repo gone (404)
    prs_merged: 4  # 口径=仅外部仓库（2026-08-15 gh api 全量核实）：evalscope #1576 + ECC #2377/#2378 + claude-skills #867 共作（概念来自 #866，维护者吸收合并保留 Co-authored-by）。⚠️ 自仓 merged（YuhaoLin2005/claude-skills#1、deepseek-claude-code-starter#1）不计入
    prs_open: 12  # 2026-09-17 gh 全量重核（全生命周期 32 PR = open 12 / merged 5 / closed 15）；补记 anthropics/skills#1367、open-compass#2598、NextFrontierBuilds#1；口径收窄为只数 PR（旧值把 #2306 discussion 混进来了）
    issues_filed: 11  # 2026-09-17 gh 全量重核（全量 21 = 外部 11 + 自仓 10，只计外部）：补记 aider#5496 / ECC#2389 / agentskills#440 / anthropics/skills#1385 / self-improving-agents-curriculum#1

  paper:
    status: "ongoing — iterative development, not chapter-based"  # was chapters_drafted: ?/5
    claims_validated: 10
    claims_needing_blind_scoring: [claim-8]
    target_venue: "CHI LBW / ACL SRW / arXiv"
    target_deadline: ?  # pending professor response
    current_score:
      core_claim_novelty: "6/10"
      experimental_rigor: "3/10"
      literature_positioning: "5/10"
      writing_maturity: "4/10"
      competitor_differentiation: "5/10"

  experiments:
    completed: 13  # manual: **distinct 实验数**（去 -YYYYMMDD-HHMMSS 重跑后缀）。⛔ 19 = `~/paper-validator/results/*.json` **文件数**，其中 p2_causal_format 跑了 6 次、p1_1_cross_model 2 次 ⇒ 19 文件 / **13 实验**。2026-10-09 用户裁决口径 = distinct 实验。⚠️ 生成路径 `_signals.py` 已于 2026-09-10 判死加闸，此字段**人工维护**，不被同步覆盖。复现：`ls ~/paper-validator/results/*.json | wc -l` = 19；`... | sed 's/[-_][0-9]\{8\}-[0-9]\{6\}\.json$//' | sort -u | wc -l` = 13
    in_progress: 0
    planned: 0
    total_api_calls_used: ~2600  # manual: sum from experiment logs（⚠️ 2026-08-14 值，可能已陈旧，非本轮重点）
    latest:
      e1b-v2-drift-probe:
        date: 2026-08-14
        status: "REPLICATED — costumes structural conclusion survives DS-arm model change: DS arm swapped deepseek-ai/DeepSeek-V4-Pro → deepseek-v4-flash (reasoning model), Kimi arm same. cross-model same-persona 0.57 ≈ within-model diff-persona 0.54 (7-23 was 0.40 vs 0.52; Δ sign flipped −0.12→+0.04, both no carry signal). Point estimates version-dependent (κ 0.049→0.175). Mechanism: official v4-flash emits reasoning_content (parse errors 29/56→2/56, 51.8%→3.6%; array count, n_errors field unreliable). NOT same-model drift — model swap. v2 lacks pre_reg_hash (gap). Attack+fix see career/e1b-methodology-attack-2026-08-15"
        output: "results/e1b_v2_current.json"
      l4-drift-validation:
        date: 2026-07-28
        status: "HONEST_FAILURE — original hypothesis untestable (D_i variance=0). Fallback: gap clustering present, lag-1 autocorr n.s. Self-limiting property of CTBV confirmed."
        output: "paper/experiment/l4-drift-predictive-validation-results.md"

  self:
    last_regeneration: 2026-10-09  # from self-model.md metadata（v0.21.7；权威记录 .last-regeneration）

  streaks:
    devto_post_streak: 0
    github_commit_streak: 0
    # session_streak removed — vanity metric. articles/experiments/PRs are the quality signals.

  community_milestones:
    # (manually maintained — preserved across sync runs)

  data_gaps_since: 2026-08-12  # 残留缺口：target_deadline（等导师回复）+ **dev.to followers + 掘金 total_views（展现数）——这两个 API 无对应字段**（2026-10-12 用户裁决：验不了就验不了，需要时人工给）。其余平台聚合数已 **API 核验到 2026-10-12**；掘金已发布文章数（原列于此）已于 2026-10-11 由 API 拿到 = 23，不再是缺口
  last_updated: 2026-10-12  # 2026-10-12 API 核验刷新（非浏览器）；未覆盖字段见 synced_at 注
  career_lock: "2026-08-15 夜锁定：主攻=AI 应用评测/验证（方向+验证角色，非评测工程师），产品第二。诚实口径：4 merged PR 为 AI 辅助实现（定位问题/定义修复方向/本地验证/协作 merge 是真实贡献，非亲手写码）。产出=career/eval-conceptual-depth-2026-08-15（补课）、career/eval-resume-attack-2026-08-14（16条修改已应用）、career/interview-bank-2026-08-15（18题）。权威记录 decisions/log.md 2026-08-15。2026-08-15 晨用户亲撰指令包 v1.0 落盘=career/digital-twin-instruction-package-2026-08-15（权威参考；数字分身部分吸收：能力定位扩展为复合线/梯队策略/Agent触发词；⚠️ 300元成本+永久居留权两数字待用户确认才上简历；时间线按秋招实际压缩：第三梯队投递提前 8/18 前启动）。阶段一任务1就绪：#1576 reviewer=Yunnglin，消息草稿待批准"
  p1_merges_recon: "2026-08-15 夜侦察（待用户批准执行）：coze-loop#617 唯一阻塞=无人 review（CI 绿, mergeable）→issue#257 温和引导 lsy357；TencentDB#977 功能被 upstream 6382e8a 抢合→pivot 只补回归测试。侦察详见 career/p1-merges-prep-2026-08-15；两条消息已草稿待批=career/p1-message-drafts-2026-08-15"
  evalscope_next_move: "2026-08-15 深夜侦察+本地验证（全部待用户批准发送）：#1578（AIME 'Yes'-anywhere + AIR-Bench 最后两裸数字）三层证据就绪——代码行+真实代码复现（2 RED+3 RED）+测试覆盖空白；修复方向验证 AIME 7/7、AIR-Bench 5/5。新侦察 #1579（gpqa_diamond --rerun-review 精度 ~25%）根因验证：gpqa_adapter.py:105 无种子 random.shuffle→同题 target 漂移 A/B/C（8-call 分布+连续 B→C），cache.py:333 to_task_state 重派生 target 是放大器；修复层1（题目内容哈希种子）验证同题稳定/跨题保留多样性；这是第 2 个 PR 候选，与 #1575/#1576/#1578 同'评分静默错误'叙事。两条评论草稿带证据待批。详见 career/eval-next-move-2026-08-15 + career/eval-next-move-gpqa-1579-2026-08-15 + repro-1578.py + verify-gpqa-1579.py"
```




## 指标解释

| 指标 | 为什么重要 | 实习面试怎么用 |
|------|-----------|-------------|
| DEV.to 文章数 | 证明持续产出+技术写作 | "30 篇英文技术文章，最高单篇 X reactions" |
| DEV.to 评论互动 | 证明社区影响力+英语 | "与 6 位国际开发者深度互动" |
| GitHub stars/PRs | 证明代码质量+开源贡献 | "paper-validator: X stars, X merged PRs" |
| 论文进度 | 证明研究能力 | "第一作者论文，已投稿 CHI LBW" |
| 实验完成数 | 证明方法论 | "9 claims, 6 experiments, 1400+ API calls" |
| 连续贡献 | 证明执行力 | "连续 X 周发文章，连续 X 天贡献代码" |

## 更新触发

| 事件 | 更新字段 |
|------|---------|
| 新文章发布 | devto.articles / juejin.articles |
| 新评论 | devto.comments_written |
| 实验完成 | experiments |
| PR merged | github.prs_merged |
| Issue filed | github.issues_filed |
| 论文章节 | paper.chapters_drafted |

*2026-08-16 晚核证同步（路由表 v1.0 建立）：全量 PR 复核——evalscope#1576 merged / ECC#2377 merged / claude-skills#867 merged（合著）/ agentscope#2325 open+APPROVED / dev.to 文章 32（API 实测）。⚠️ 简历数字两处修正：digital-twin loss 8.1953→0.3965 为误导（0.3965 是中间点，最终 checkpoint-96=0.7731、全局最低 0.3751，已修为「96 步 →0.77 最低 0.3751」）、adapter 17MB→16.7MB（self-model 权威）。⚠️ followers 621 vs 608 差异：以 nav 621 为准（8/12 browser-verified），resume-assets 8/15 记 608 为不同时点口径，已标待用户拍板。核证命令索引=memory/job-asset-route-table.md*
*2026-08-16 深夜 SOP 沉淀同步：①**resume-iteration-sop.md v1.0 建立**（memory/procedures/，用户定序补写）——数字分身校准→对抗性审查（多视角）→全内容核证→落地→导出验证→落账七步，收尾必做对抗性审查+定稿前置问数字分身+路由表无 ✅ 数字不写进简历。②**0.7% 源追到**：prose-barrier-rewrite-v2.md:96（34 会话回顾 55.9%→0.7% 机械层启用后）+ P1-1 实验 200 trials（:98）→ 简历原「自建对抗测试集」口径不符，已修为「34 个真实会话 + P1-1 实验 200 次验证」（对齐论文）。③先搜再建调研：open-resume-agent（ATS 评分门槛+修复循环）/ CareerPilot（evidence-locked+EvalHarness）/ career-ops（六维 rubric）——通用求职工具无评测岗专项，借鉴机制不换模板*
---
*2026-08-18 同步: dev.to dashboard 浏览器重核（_check_kb 3d 上限触发）——Posts 32 / Total post comments 98 / Followers 621 / Total post reactions 29 不变；Total post views 1235→1315。简历 v1.2/v2.1/v3.0「32 篇英文文章 / 621 followers / 1000+ 阅读量」全部仍成立。juejin creator center 未在本 session 重核（无登录 tab），下次启动优先补核*
*2026-08-27 同步: dev.to dashboard + juejin creator center 浏览器重核（登录 tab 在线，chrome-devtools 实测）——dev.to：Posts 32 / Total comments 98→100 / Followers 621 / Total reactions 29 / Total views 1315→1498（简历「1000+ 阅读量」仍成立）；juejin creator center：文章阅读 4672→5095、文章展现 61038→67204、文章点赞 38→35（环比略降，掘金口径/去重波动）、文章收藏 24→25、总粉丝 18。8-18 遗留项（juejin 补核）本次已清。⚠️ juejin 点赞环比下降——若上简历先人工复核*
*2026-08-31 同步: dev.to dashboard + juejin creator center 浏览器重核（登录 tab 在线，chrome-devtools 实测）——dev.to：Posts 32 / Total comments 100 / Followers 621 / Total reactions 29 / Total views 1498→1518（简历「1000+ 阅读量」仍成立）；juejin creator center：文章阅读 5095→5159、文章展现 67204→68539、文章点赞 35→36（8-12 基线 38、8-27 为 35——先降后回，若上简历先人工复核）、文章收藏 25、文章评论 9（新基线）、总粉丝 18。*
*2026-09-10 结构性同步：把「索引陈旧」从**慢性病**改成**机械可检**——①根因：`_check_kb.py` 2d 拿 dashboard(20) 比索引(20)，两个内部文档互证，谁都没碰平台；平台真值已发布 22 篇，漏的是 2026-07-26 / 2026-08-14 两篇（整篇未入索引）。②处置：juejin/articles.md 拆掉每篇的阅读/点赞/收藏/评论数字（O(N) 手工拷贝 + 旧 2e 检查结构上抓不到 —— 陈旧值恒 ≤ 真值），改为两个 O(1) 锚点 `platform_published` + `last_verified`；索引回归路由本职，单篇数字权威交平台，聚合数字留本文件。③机械门：删死掉的 2e，加 2f（计数不符=ERROR、核验超 14d=WARN），dev.to 同步打锚点。④负向测试已过：投毒计数→exit 1、投毒日期→exit 2、还原→PASS。⑤顺带校正 4 处索引日期（平台权威，原记偏移 1 天）。刷新流程=浏览器过一遍创作者中心，改 2 个数+补新篇*
*最后更新: 2026-09-27*
*交叉引用: [[../routing]] [[research-pipeline]] [[content-pipeline]] [[github-strategy]]*
*2026-08-17 同步: lm-eval #3968 归属核证（route-table）——作者=Kelvinz-89757=第三方移植用户 evaluate #778（原创）+ lm-eval #3924（提案）设计。prs_open 9→10、issues_filed 3→4（补录用户原创 #778/#3924）。⚠️ 简历「被 lm-eval 列移植候选」措辞准确（社区认领用户设计），禁写「合入」。51.8%→3.6% 归属不变（E1b 探针，见 experiments.e1b-v2）*
*2026-08-16 同步: agentscope **#2325 APPROVED**（iamroylim 2026-08-16 05:25Z「25 passed, No blocking issue」），作者致谢回复已发（comment 5306009742），prs_open 8→9。⚠️ 发布踩坑：gh api -f body=@file 在 Windows 下发成路径字面量→Python JSON+`--input` 重发，教训见 growth-log/2026-08-16-gh-atfile-pitfall*
*2026-08-16 同步: **交付物清洁度纪律**（用户纠正，memory=facing-content-no-audit-traces）——621 followers 为权威值，但「登录态 dashboard 实测」「was 608」「公开 API 已移除」等核证痕迹**只留在本 dashboard/内部验证报告**，不出现在简历/防御包/PR 对外文案（读者读成不专业/此地无银，且暴露数字倒退）。8/16 已清理 eval-lapiscv.html/-full.html 注释区 + interview-defense-eval-general.md 正文；两版 PDF 重导出 2 页 OCR 通过*
*2026-08-16 深夜 调度架构沉淀：context-scheduling-architecture.md v1.0 建立（memory/）——用户洞察「大量 skill 占上下文 → 脚本辅助+触发词=路由表/管线；脚本 vs 模型平衡：机械门死板、大模型幻觉、如评测阴柔语义」→ 设计为 L1 脚本机械层（确定性/省token/不幻觉）+ L2 模型语义层（灵活/抓阴柔语义/会幻觉）+ CTBV 交叉验证，映射用户 Prose Barrier 分层（55.9%→0.7% / P1-1 实验）。定位=本来就是借鉴机制：open-resume-agent 评分门槛 ✅吸收 / CareerPilot evidence-locked ✅吸收 / career-ops 六维 rubric ⏳待专家团裁决 / agentic-ai agent_trace ✅吸收。专家团 review 挂起（成本~$44+/上下文40%，腾出后跑 persona-grill 双池）*
*2026-08-16 深夜 简历 v2.4 同步：质量效能版定位段加「验证门/治理」支柱（一句话定位=设计并驱动 Agent 工作流，以质量门禁+异构交叉验证建立可信评测体系，让评测结论可溯源/可证伪/经得起复核）；resume-iteration-sop v1.0 七步首次完整执行（§② 对抗性审查不再跳过）。方向澄清：**布道线主投已锁定**（decisions/log 1217-1224，grill Q1/Q2/Q3 全答）——质量效能版=FULL 评测窄缝次线（只投阿里 ModelScope/上海AI 方法论档），主投=待新建的第三版布道简历。调度架构专家团审查 CONCERNS 放行（Lamport 独立验证链/Carmack 先测再定/Hickey 否决 L2.5/Popper 可证伪声明，v1.1）*
*2026-08-16 深夜 路由表 v2 落地同步：MEMORY.md WARM 表改薄（35 行一跳直达）+ build-knowledge-index ROUTE_SPEC 校验（当场抓 4 缺陷：3 死链+articles.md 模糊指向）+ check-log-facts --against 数字审计（DRIFT:OK 活跃文件 0 漂移）+ 三专家 design-round 裁决（Hickey 否决 ROUTE-INDEX 独立文件/Carmack 先测漂移 0 降级一致性工具/Lamport 规范四条不变量）。沉淀 memory/context-scheduling-architecture.md v2.1 + persona-pool design-round 协议*
*2026-09-17 平台计数核验（**非浏览器**）：掘金 22 / DEV.to 32，经公开 API 独立复核，与索引一致、**0 篇缺失**。⚠️ 本轮未做浏览器核验，故 `synced_at` / `last_updated` 保持 2026-09-10 **不动**，本文件所有聚合数（reads/views/likes/bookmarks/comments/followers/reactions）**全部沿用 9/10 值，未刷新**。索引侧同步：掘金 articles.md 校正 12 条日期 + 5 条标题；tier（warm/cold）校正 17 条日期、4 条标题，补录 2 条此前未入任何 tier 的篇目（juejin-ai-safety / juejin-tencent-memory），并按 SOP 维护契约剥离 20 条陈旧单篇数字。*
*2026-09-25 dev.to 侧 API 复核（**非浏览器**；起因：Stop hook `_check_kb.py 2b` 报 15d 超 14d 阈值）：`GET /api/articles?username=yuhaolin2005` 实测 **文章数 32 / public_reactions 合计 29 / comments 合计 100**，与 `articles`、`total_reactions`、`comments_received` **三项逐一对上**。✅ 本文件 9/10 基线的 dev.to 三数**未漂移**。⚠️ 仍未浏览器核验，故 `synced_at` / `last_updated` **照旧不动**；`followers: 621`、`total_views: 1608` 需 dashboard 登录，掘金全组（reads/views/likes/bookmarks/comments）需 creator center 登录，**本轮均无法核**。⚠️ **该 WARN 只有人能清**——平台聚合数需人工浏览器登录，AI 无凭据；在浏览器过一遍之前，本文件每 ≥14 天必然再次报红，**这是设计如此，不要靠改日期消警告**（改日期=推进状态时间戳而不做底层核验，即假"已再生"）。刷新流程见 2026-09-10 条。*

*2026-09-27 dev.to 侧 API 复核（**非浏览器**；起因：Stop hook `_check_kb.py` 2a/2b 报 17d 超 14d 阈值）：`GET /api/articles?username=yuhaolin2005&per_page=100` 实测**取回 32 篇 / articles 32 / public_reactions 合计 29 / comments 合计 100** —— 与 9/25 那次**逐字一致**，与 KB 记的 32 / 29 / 100 **三项逐一对上**；最近一篇仍为 2026-07-26（期间无新发文）。✅ 9/10 基线的 dev.to 三数**17 天未漂移**。⚠️ **仍未浏览器核验**，故 `synced_at` / `last_updated` **照旧不动**（2026-09-10）；`followers: 621`、`total_views: 1608` 需 dashboard 登录，掘金全组（reads/views/likes/bookmarks/comments）需 creator center 登录，**本轮均无法核**。⚠️ 该 WARN **只有人能清**，理由见 9/25 条，不重复。*（→ **本条的"未浏览器核验"已于同日被下一条取代**）*

*2026-09-27 浏览器核验（**真浏览器登录**，Playwright persistent context，复用 `chrome-devtools-mcp/chrome-profile`）：`synced_at` / `last_updated` 推进到 **2026-09-27**。**dev.to dashboard**（登录 `YuhaoLin2005`）：Posts 32 / Total post reactions 29 / Total post comments 100 / **Total post views 1608→1788** / Followers 621 —— 前三项与 9/10 及同日 API 复核逐一对上，只有 views 涨了 +180。**掘金创作者中心首页 数据概览**：**文章展现数 70449→80,171（+9,722）· 文章阅读数 5324→5,615（+291）· 文章点赞数 38→41（+3）· 文章评论数 10→13（+3）· 文章收藏数 26→27（+1）**；另有**总粉丝数 18**（与 8-27/8-31/9-10 记的 18 一致，17 天未动）、掘力值 337、创作第 199 天。✅ 简历「1000+ 阅读量」仍成立。⚠️ **三项没拿到，如实记**：① 掘金**已发布文章数**（`articles: 22`）——「文章管理」页 route 通（`<title>` 正确）但正文没渲染出来，innerText 仅 **83B**、4 个锚点 0 命中，**这个数不能取，沿用 9/10 值**；② `https://juejin.cn/creator/data/content` **已 404**（`<title>` = 「找不到页面」）—— 该 URL 是 `tat-work\kb_refresh.py` TARGETS 里的死路由，**待修**；③ 单篇数字（`most_popular` 那篇）未复核，逐篇要进详情页。⚠️ **方法学教训**：`kb_refresh.py` 固定 6 秒等待对掘金 SPA 不够；本轮改用 20 秒 + `networkidle`（`kb_refresh_juejin2.py`）后 `juejin-articles` **仍未渲染**，说明**不是等待时长问题**——SPA 渲染失败时 `innerText` 短到 83B 却**没有报错**，只有 `len(txt) < 500` 这条自检能拦住它。**没有这条自检，"取到空页"会被记成"读到了 0"**。⚠️ 该 WARN 现存**唯一的残留缺口**是掘金文章数，见 `data_gaps_since` 注。*

*2026-10-09 结案并更正（原 2026-09-17 未决条，已改写）：`_signals.py` 生成路径**已整改**，本文件不再会被它改写。①**更正一条错误指控**：原文写「routing.md:136 推荐的用法」——**不成立**。routing.md:136 推荐的是 `--check`，**137 行当日起就已写明 ⛔ 不要跑裸命令**；说的是过期话的是本条自己（典型的过期台账指控正确文档）。②**整改（代码）**：`generate_dashboard_yaml()` 改为**有现 yaml 块就逐字节原样继承**，只有 bootstrap（无现文件）才用启发式桩造骨架。此前它一次生成实测改掉 **70 行**（42 行是人工浏览器核验的原值+行尾核对注释）：`juejin.total_reads` 5615→0、`total_likes` 41→0、`prs_merged` 4→0、`issues_filed` 11→0、`comments_written` 49→4、`completed` 13→19、`self.last_regeneration`→`?`、`paper.status` 被换成 `chapters_drafted`、`data_gaps_since`/`career_lock`/`p1_merges_recon`/`evalscope_next_move` 四个顶层块整个丢弃、早先按 vanity 删掉的 `session_streak` 被写回 `?`、`synced_at` 被推进成「现在」。根因=`collect_*` 全是文本启发式桩（tier 求和 / 数 markdown 表行），**拿不到真值就返回 0，而生成器把 0 当事实写**——`empty-result-read-as-zero` 的生成侧异体。③**`--check` 未被削弱**：其比较值改为直取 `collect_*`，不取生成器产物（否则一继承就新旧恒等，检查退化成橡皮图章）；负向对照（存量 999 vs 实算 32）仍 `exit 1`。④复现：`python _signals.py --check` → `FRESH: devto=32, juejin=22`；生成器恒等性证据见 `~/.grill_sessions/harness-order-20261009/verify_fix.txt`。⚠️ 启发式桩本身**未修**——生成路径已无写权，修它只会让一条死路径更精确。*
*2026-09-17 GitHub 全量重核：`gh search prs --author YuhaoLin2005` 全生命周期 32 PR = open 12 / merged 5 / closed 15。**`prs_open` 10→12**（漏记 anthropics/skills #1367、open-compass #2598、NextFrontierBuilds #1），口径同时收窄为只数 PR（旧值把 #2306 discussion 混进来了）。`prs_merged` **仍为 4**（外部口径未变）：#867 共作 trailer 已验实（commit f7a9a7b2 含 `Co-authored-by: YuhaoLin2005`），3 个直连 merged author 全部=用户。7 条 fork CI 红=720h 排队超时非代码问题。**issue 同法全量重核：全量 21 = 外部 11 + 自仓 10，`issues_filed` 4→11**（补记 aider #5496 / ECC #2389 / agentskills #440 / anthropics/skills #1385 / self-improving-agents-curriculum #1；自仓 10 个含 gategrow Org 下的 checkgrow+delivery-gate，口径同 merged 不计）。⚠️ **#1385 有外部 tonydzi 2026-08-01 实质提问**——问「门有没有记录它上次真拦下东西是什么时候」，直击 POOL_EVOLVE 退役 / `_signals.py` 假红的同一命题。**该条已于 2026-10-09 回复（comment 6081412364），本条「未回」结论作废**，详见 [[github-strategy]] 与下方 2026-10-09 条*
*2026-10-09 GitHub 回复（结案 9/17 挂的「未回，我不代拟」）：anthropics/skills **#1385** 已回 tonydzi 2026-08-01 的 standing offer（comment 6081412364）。他问的是「你的模块有没有记录**最后一次真正拦下**什么，而不是只记录跑过几次」。回复给了实测数：`voice-compliance` 26 块 / 68 事件 (38%) 最后拦下 **2026-10-09** · `writing-workflow` 34 块 / 43 事件 (79%) 最后拦下 **2026-09-24**；另 **`write_guard`(963 条) / `evidence-gate`(164 条) 结构性单边** —— 唯一调用点（`write-guard.py:809` / `evidence-gate.py:238`）event 字面量恒为 `blocked` ⇒ `blocked/total` 对任何输入恒 **100%**，是记账口径不是门的行为（同 memory/gate-logging-only-negatives-always-reads-100pct）；余 `voice_guard`(5 条) / `stage5-review`(1 条) 样本太小，**明说不下结构性结论**。收口=补双边日志（warned/allowed 也记），不改门。点名接下 **#1423 delivery-verification** 的 review（tonydzi 已自行关闭对比 PR #1460）。**口径不变**：非新 PR/issue，`prs_open` 12 / `prs_merged` 4 / `issues_filed` 11 均不动。证据：`oss-pr-work/anthropics-skills/{reply-1385.md, evidence-gate-stats-20261009.txt}`；追踪条目见 `KB/devto/replies.md` = `github-anthropics-skills-1385`。⚠️ **顺带发现（非本次改动产生）**：`replies.md` 的 yaml 块**自首版提交 `9c73d5f` 起即无法解析**（悬空 `reply_` 已修；另一处顶格 `summary:` 截断列表 **也已在 2026-10-09 修毕**，字符串一字未改、只挪进 `summary:` map 名下，`yaml.safe_load` 已通过，并顺带更正 `total_tracked` 自 `b10e723` 起少 1 的错位 24/25→**26**）—— 「Session 启动扫 unread」机制此前可能一直未真正生效*

*2026-10-11 计数同步（**API 非浏览器**；起因：核验两个数字分歧 + KB 检查 2d 报 dashboard≠索引）：dev.to `articles` 32→33、掘金 `articles` 22→23，均经公开 API 独立复核（脚本见 `~/.claude/projects/boss/_work/verify_devto_comments*.py` / `verify_juejin.py`）。⚠️ `synced_at` / `last_updated` 保持 **2026-09-27 不动**（本轮无浏览器核验，聚合数 reads/views/likes/followers/reactions 全部沿用 9-27 值未刷新）。下游同步：devto/articles.md、juejin/articles.md 的 `platform_published`/`last_verified` → 33/23 + 2026-10-11；BOSS 在线简历文案 + job-asset-route-table.md 同步口径。*

*2026-10-13 更新（**用户人工复核**，非 AI 核）：用户登录态自行核对 dev.to dashboard nav，**followers 由 621 更正为 615**。⇒ 本文件第 14 行字段值已改；`job-asset-route-table.md:59` 同步。⚠️ 影响面：全部在档简历/在线简历/BOSS 文案里的 `621 followers` 一律改 `615`（`_work/tailor_jobs.py` 生成路径 + 各 ACTIVE HTML + j11 投递件 PDF）。沿用既有纪律：**核证痕迹（"was 621""登录态"）只留本文件与内部报告，不出现在对外正文**。*
