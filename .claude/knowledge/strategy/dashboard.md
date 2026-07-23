# 量化仪表盘

> 单一真相来源。每次 session 启动时读取 → AI 立刻知道"现在在哪里"。
> 做完任何事→更新对应数字。>7天未更新→`_check_kb.py` 警告。

```yaml
dashboard:
  devto:
    articles: 30
    comments_written: 41
    followers: ?        # DEV.to API 不公开 follower count
    total_reactions: ~40  # 从 API 估算：30篇文章，多数2-3❤️
    notable_commenters: [Mike_Czerwinski, René_Zander, Dipankar_Sarkar, Tom_Jones, Alice, Alex_Shevchenko, CodeKitHub]
    unread_comments: ?   # 需检查通知页

  juejin:
    articles: 18
    total_reads: ~3008
    total_likes: ~22  # 2篇有明确点赞数据
    most_popular: 2289_reads  # [juejin-rene] René Zander 故事
    # 注：掘金评论互动少，平台文化不同——不重点维护评论

  github:
    paper_validator_stars: 0
    paper_validator_forks: 0
    hermes_workspace_stars: 0
    total_commits_since_july1: 134  # 50 hermes + 50 .claude/scripts + 20 pv-profile + 14 pv-main
    prs_merged: 0
    prs_open: 0
    issues_filed: 0

  paper:
    chapters_drafted: "?/5"
    claims_validated: 9
    claims_needing_blind_scoring: [claim-8]
    target_venue: "CHI LBW / ACL SRW / arXiv"
    target_deadline: ?
    current_score:
      core_claim_novelty: "5/10"
      experimental_rigor: "3/10"
      literature_positioning: "4/10"
      writing_maturity: "3/10"
      competitor_differentiation: "4/10"

  experiments:
    completed: 18
    in_progress: 0
    planned: 2
    total_api_calls_used: ~2200
    latest:
      e1_persona_decorrelation:
        date: 2026-07-23
        prereg_hash_e1a: eebe2a31fb290860
	        e1a_result: "persona drives judgment (1.00 > 0.87) BUT ceiling effect (4/5 unanimous)"
	      e1b_cross_model:
	        date: 2026-07-23
	        prereg_hash: 9c80bad72382d8c4
	        models: [DeepSeek-V4-Pro, Kimi-K2.7-Code]
	        trials: 112
	        tokens: 81717
	        errors: 0
	        fleiss_kappa_all: 0.049
	        fleiss_kappa_ds: -0.201
	        fleiss_kappa_kimi: 0.460
	        result: "E1b REFUTES E1a. Persona effect = model-dependent. Expert board = costume diversity."
        models: [DeepSeek-V4-Pro, Kimi-K2.7-Code]
        trials: 30
        tokens: 21853
        errors: 0
        result: "persona drives judgment: cross-model same-persona 1.00 > within-model diff-persona 0.87"
        caveat: "4/5 snippets unanimous; effect from error_silent where Torvalds REJECTs vs Carmack/Knuth A_W_NOTES — pattern holds across both architectures"

streaks:
  devto_post_streak: 0
  github_commit_streak: 0
  session_streak: ?

  community_milestones:
    - date: 2026-07-19
      event: "Mike Czerwinski 发表回应文章 'The Line Is Not Between Human and Machine... It Is Between Code and Judgment' (dev.to/jugeni)——回应你的研究框架"
    - date: 2026-07-19
      event: "Tom Jones 独立复现 stance-marker 剥离实验 (17%→2.1%) + 跨模型层次外部验证——首次有陌生人复现你的结果"
    - date: 2026-07-19
      event: "Alice 提供 2 个生产环境 hook-failure 真实案例——可入 supplementary"
    - date: 2026-07-21
      event: "发表 [expert-board] Stop Using Generic AI Review — 命名原则锚定→去关联前提→33 persona独立幻觉，Mike Czerwinski 关联评论"
    - date: 2026-07-23
      event: "E1 Persona Decorrelation 完成——DS V4 Pro × Kimi K2.7 Code 跨架构验证：persona 驱动判断（跨模型同persona 1.00 > 同模型异persona 0.87），0/30 errors"
    - date: 2026-07-23
      event: "数字分身数据同步——DEV.to/juejin/GitHub/遥感实习数据全部刷新，user-profile+self-model+remote-sensing-checkpoint 更新"
	    - date: 2026-07-23
	      event: "E1b Cross-Model完成——112 trials, κ=0.049(≈随机), E1a被证伪。专家团三人收敛：persona=costume diversity。论文框架需从persona-driven降级为multi-model ensemble"

last_updated: 2026-07-23
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

---
*最后更新: 2026-07-21*
*交叉引用: [[../routing]] [[research-pipeline]] [[content-pipeline]] [[github-strategy]]*
