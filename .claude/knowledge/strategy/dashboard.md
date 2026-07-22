# 量化仪表盘

> 单一真相来源。每次 session 启动时读取 → AI 立刻知道"现在在哪里"。
> 做完任何事→更新对应数字。>7天未更新→`_check_kb.py` 警告。

```yaml
dashboard:
  devto:
    articles: 30
    comments_written: 41
    followers: ?        # DEV.to profile 页未公开显示 follower count
    total_reactions: ?  # 需从 API 或手动统计 29 篇文章
    unread_comments: ?   # 需检查通知页

  juejin:
    articles: 18
    followers: ?
    total_reads: ?
    total_likes: ?
    # 注：掘金评论互动少，平台文化不同——不重点维护评论

  github:
    paper_validator_stars: 0
    paper_validator_forks: 0
    hermes_workspace_stars: ?
    prs_merged: 0
    prs_open: 0
    issues_filed: 0
    issues_resolved: 0

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
    completed: 16
    in_progress: 0
    planned: 1
    total_api_calls_used: ~2000

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

last_updated: 2026-07-21
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
