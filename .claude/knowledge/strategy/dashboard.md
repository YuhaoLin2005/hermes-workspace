# 量化仪表盘

> 单一真相来源。每次 session 启动时读取 → AI 立刻知道"现在在哪里"。
> 做完任何事→更新对应数字。>7天未更新→`_check_kb.py` 警告。

```yaml
dashboard:
  synced_at: 2026-07-28T00:00:00Z

  devto:
    articles: 32
    comments_written: 45  # 2026-07-28 browser: dev.to profile shows "45 comments written"
    comments_received: 93  # 2026-07-28 browser: dashboard shows "93 total post comments"
    followers: 608  # 2026-07-28 browser: dev.to/dashboard sidebar
    total_reactions: 29  # 2026-07-28 DEV.to API: sum across 32 articles
    total_views: 1040  # 2026-07-28 browser: dev.to/dashboard "1,040 total post views"
    notable_commenters: ['Dipankar Sarkar', 'Max Quimby', 'René Zander', 'Alex Shevchenko', 'CodeKitHub']
    unread_comments: 0  # 2026-07-28 browser: notification bell shows no badge

  juejin:
    articles: 20
    total_reads: 74
    total_likes: 8
    most_popular: 34_reads

  github:
    paper_validator_stars: 0  # 2026-07-28 gh api verified
    paper_validator_forks: 0  # 2026-07-28 gh api verified
    hermes_workspace_stars: 0  # 2026-07-28 gh api verified
    total_commits_since_july1: 102  # 2026-07-28: hermes-workspace(50) + fu-complexity(50) + fu-garden(2)
    prs_merged: 3
    prs_open: 5
    issues_filed: 3

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
    completed: 17
    in_progress: 0
    planned: 0
    total_api_calls_used: ~2500  # estimate from claims.md(928) + structure.md + DPO(250) + digital-twin(300) + 150-task(300) + misc
    latest:
      l4-drift-validation:
        date: 2026-07-28
        status: "HONEST_FAILURE — original hypothesis untestable (D_i variance=0). Fallback: gap clustering present, lag-1 autocorr n.s. Self-limiting property of CTBV confirmed."
        output: "paper/experiment/l4-drift-predictive-validation-results.md"

  self:
    last_regeneration: 2026-07-27  # from self-model.md metadata

  streaks:
    devto_post_streak: 0
    github_commit_streak: 0
    # session_streak removed — vanity metric. articles/experiments/PRs are the quality signals.

  community_milestones:
    # (manually maintained — preserved across sync runs)

  data_gaps_since: 2026-07-28  # 1 remaining: target_deadline (pending professor response)
  last_updated: 2026-07-28
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
