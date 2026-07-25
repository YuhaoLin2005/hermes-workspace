# 量化仪表盘

> 单一真相来源。每次 session 启动时读取 → AI 立刻知道"现在在哪里"。
> 做完任何事→更新对应数字。>7天未更新→`_check_kb.py` 警告。

```yaml
dashboard:
  synced_at: 2026-07-25T03:30:00Z  # browser-verified via 掘金 creator center + DEV.to profile

  devto:
    articles: 31                  # browser-verified: 31 unique article URLs on dev.to/yuhaolin2005
    comments_written: 4
    followers: ?                  # DEV.to profile page doesn't show follower count
    total_reactions: ?            # needs DEV.to API
    notable_commenters: ['Dipankar Sarkar', 'René Zander', 'Alex Shevchenko', 'CodeKitHub']
    unread_comments: ?            # needs notification check

  juejin:
    articles: 20                  # 已发布 20 / 审核中 0 / 未通过 1 / 全部 21 (browser-verified: 2026-07-25)
    total_reads: 3862             # browser-verified: 创作者中心 数据概览 "文章阅读数"
    total_likes: 28               # browser-verified: 创作者中心 数据概览 "文章点赞数"
    total_comments: 11            # browser-verified: 创作者中心 数据概览 "文章评论数"
    total_collects: 22            # browser-verified: 创作者中心 数据概览 "文章收藏数"
    total_impressions: 38207      # browser-verified: 创作者中心 数据概览 "文章展现数"
    followers: 16                 # browser-verified: 创作者中心
    jue_value: 287                # browser-verified: 掘力值
    most_popular: "七月德国开发者 — 2685阅读 17赞 12收藏"

  github:
    paper_validator_stars: 0      # gh api: 2026-07-25
    paper_validator_forks: 0      # gh api: 2026-07-25
    hermes_workspace_stars: 0     # gh api: 2026-07-25
    total_commits_since_july1: ?  # manual: git log
    prs_merged: 0
    prs_open: 0                   # gh pr list: 2026-07-25
    issues_filed: 0

  paper:
    chapters_drafted: "?/5"
    claims_validated: 10
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
    completed: 16
    in_progress: 0
    planned: 0
    total_api_calls_used: ?       # manual: sum from experiment logs
    latest:
      # (see dashboard.md git history for latest experiment details)

  self:
    last_regeneration: ?

  streaks:
    devto_post_streak: 0
    github_commit_streak: 0
    session_streak: ?

  community_milestones:
    # (manually maintained — preserved across sync runs)

  last_updated: 2026-07-25
  data_gaps_since: 2026-07-25  # 5 unresolved: commits_since_july1, target_deadline, api_calls_used, last_regeneration, session_streak
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
