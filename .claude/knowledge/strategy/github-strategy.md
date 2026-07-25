# GitHub 贡献策略

> 目标：GitHub profile 从"只有自己项目"→"高星仓库有实质贡献"。
> Importer: routing.md, CLAUDE.md. Schema: YAML-in-Markdown.

```yaml
target_repos:
  - repo: "continuedev/continue"
    stars: "20k+"
    language: "TypeScript"
    relevance: "AI agent IDE 工具——你的自指环研究是差异化视角"
    first_action: "找 good first issue → 修 bug 或加测试"
    contribution_angle: "贡献 agent governance 相关的 issue/PR"

  - repo: "langchain-ai/langchain"
    stars: "100k+"
    language: "Python"
    relevance: "最主流 Agent 框架——五层架构可贡献为 cookbook"
    first_action: "找 documentation 标签 → 写 tutorial/cookbook"
    contribution_angle: "用 paper claims 写 tutorial——贡献 + 文章素材"

  - repo: "microsoft/autogen"
    stars: "40k+"
    language: "Python"
    relevance: "Multi-agent 框架——双池专家团是差异化视角"
    first_action: "提 issue 讨论 multi-agent adversarial review"
    contribution_angle: "issue→discussion→potential PR"

  - repo: "anthropics/claude-code"
    stars: "?"
    language: "TypeScript"
    relevance: "研究直接基于 Claude Code——自然延伸"
    first_action: "找 bug/feature request → 复现+PR"

contributions:
  # 格式: {repo, type, url, status, date}
  # 目标: 5 repos × (≥1 PR merged + ≥1 issue filed) = ≥10 contributions

strategy_notes: |
  顺序：
  1. 先提 issue（低成本，建立存在感）→ 观察 maintainer 响应
  2. 再 good first issue（建立信任）→ 第一次 PR 尽量小
  3. 然后贡献与你的研究相关的 feature/cookbook（展示深度）
  4. 每次贡献 → 更新此处 + dashboard + 考虑写 DEV.to 文章
  
  一个 20k-star PR = "我修了高星项目" 远 > "我写了自己的小项目"
```

## 贡献记录

| # | 仓库 | 类型 | URL | 状态 | 日期 |
|---|------|------|-----|------|------|
| - | - | - | - | - | - |

---
*最后更新: 2026-07-19*
*交叉引用: [[../dashboard]] [[research-pipeline]] [[content-pipeline]]*
