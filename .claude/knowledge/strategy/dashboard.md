# 量化仪表盘

> 单一真相来源。每次 session 启动时读取 → AI 立刻知道"现在在哪里"。
> 做完任何事→更新对应数字。>7天未更新→`_check_kb.py` 警告。

```yaml
dashboard:
  synced_at: 2026-08-12T22:35:00Z  # 2026-08-12 browser-verified (dev.to dashboard/analytics/notifications + juejin creator center); logged-in metrics refreshed

  devto:
    articles: 32  # 2026-08-12 browser-verified (dashboard nav Posts 32)
    comments_written: 45  # 2026-08-12 browser-verified (analytics 32 posts · 45 comments · 54 reactions)
    comments_received: 94  # 2026-08-12 browser-verified (analytics 32 posts · 45 comments · 54 reactions)
    followers: 621  # 2026-08-12 browser-verified (dashboard nav; was 608. analytics "0 of 690" 不同口径, 以 nav 621 为准)
    total_reactions: 29  # 2026-08-12 browser-verified (analytics 32 posts · 45 comments · 54 reactions)
    total_views: 1235  # 2026-08-12 browser-verified (was 1040)
    notable_commenters: ['Dipankar Sarkar', 'Max Quimby', 'René Zander', 'Alex Shevchenko', 'CodeKitHub']
    unread_comments: 4  # 2026-08-14 browser-verified (dev.to 通知中心无未读通知, 但文章页确认 4 条真实未回复: mike/audit-ctbv 7-29, yunetzi/audit-ctbv 7-26, mike/expert-board 7-27, RAD/150-tasks 7-18). ⚠️ 原 2 条 unread 已过期 — 实际 7-23 已回复 (浏览器确认), 已更正 replies.md

  juejin:
    articles: 20
    total_reads: 4672  # 2026-08-12 browser-verified (creator center; was 3691 index sum)
    total_likes: 38  # 2026-08-12 browser-verified (was 29 index sum)
    total_views: 61038  # 2026-08-12 browser-verified (creator center)
    total_bookmarks: 24  # 2026-08-12 browser-verified (creator center)
    most_popular: juejin-rene_2685_reads  # 2026-08-01 from index (was 34_reads — stale)

  github:
    paper_validator_stars: 0  # 2026-08-01 gh api verified
    paper_validator_forks: 0  # 2026-08-01 gh api verified
    hermes_workspace_stars: 1  # 2026-08-05 gh api verified
    total_commits_since_july1: 124  # 2026-08-01 gh api: hermes-workspace(100) + paper-validator(24). fu-complexity/fu-garden repos gone (404)
    prs_merged: 4  # github-strategy.md #1-3 + modelscope/evalscope #1576（2026-08-14 merged，维护者 Yunnglin APPROVED——第一个国内大厂主线仓库合并 PR）。⚠️ 08-12 曾误报 4（#331 被误判 merged），撤回后现在真到 4
    prs_open: 5  # github-strategy.md #4,#6-9 external contributions, browser-verified 2026-07-28
    issues_filed: 3  # github-strategy.md #5,#10,#11 external contributions, browser-verified 2026-07-28

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
    completed: 18
    in_progress: 0
    planned: 0
    total_api_calls_used: ~2600  # +140k tokens E1b-v2 (112 trials, 139,659 tokens)
    latest:
      e1b-v2-drift-probe:
        date: 2026-08-14
        status: "PASS — costumes structural conclusion survives drift: cross-model same-persona 0.57 ≈ within-model diff-persona 0.54 (7-23 was 0.41 vs 0.52). Point estimates version-dependent (κ 0.049→0.175). Mechanism: official V4-Flash is a reasoning model."
        output: "results/e1b_v2_current.json"
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

  data_gaps_since: 2026-08-12  # remaining gap: target_deadline (pending professor response). All platform metrics browser-verified 2026-08-12
  last_updated: 2026-08-14  # E1b-v2 drift probe experiment +18, devto reply drafts browser-verified (voice gate pending); unread_comments 0→4 (真实未回复)
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
*最后更新: 2026-08-12*
*交叉引用: [[../routing]] [[research-pipeline]] [[content-pipeline]] [[github-strategy]]*
