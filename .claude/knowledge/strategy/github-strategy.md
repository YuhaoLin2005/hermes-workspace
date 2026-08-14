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
| 1 | affaan-m/ECC | PR | [#2377](https://github.com/affaan-m/ECC/pull/2377) growth-log skill | ✅ merged | 2026-07 |
| 2 | affaan-m/ECC | PR | [#2378](https://github.com/affaan-m/ECC/pull/2378) delivery-gate skill | ✅ merged | 2026-07 |
| 3 | alirezarezvani/claude-skills | PR | [#867](https://github.com/alirezarezvani/claude-skills/pull/867) persona-review | ✅ merged (Co-authored-by) | 2026-07 |
| 4 | affaan-m/ECC | PR | [#2496](https://github.com/affaan-m/ECC/pull/2496) config-health skill | 🔄 open (approved by daltino) | 2026-07 |
| 5 | crewAIInc/crewAI | Issue | [#6428](https://github.com/crewAIInc/crewAI/issues/6428) lang-aware prompt routing | 🔄 open → PR [#6491](https://github.com/crewAIInc/crewAI/pull/6491) by ashusnapx | 2026-07 |
| 6 | anthropics/skills | PR | [#1420](https://github.com/anthropics/skills/pull/1420) persona-review skill | 🔄 open (0 reviews) | 2026-07 |
| 7 | anthropics/skills | PR | [#1422](https://github.com/anthropics/skills/pull/1422) pre-task-calibration | 🔄 open (0 reviews) | 2026-07 |
| 8 | anthropics/skills | PR | [#1423](https://github.com/anthropics/skills/pull/1423) delivery-verification | 🔄 open (0 reviews) | 2026-07 |
| 9 | anthropics/skills | PR | [#1424](https://github.com/anthropics/skills/pull/1424) neural-gate | 🔄 open (0 reviews) | 2026-07 |
| 10 | dair-ai/Prompt-Engineering-Guide | Issue | [#787](https://github.com/dair-ai/Prompt-Engineering-Guide/issues/787) mechanical guards proposal | 🔄 open (0 responses) | 2026-07 |
| 11 | langchain-ai/langchain | Issue | [#39073](https://github.com/langchain-ai/langchain/issues/39073) process verification pattern | ❌ closed (bot, no template) | 2026-07 |
| 12 | addyosmani/agent-skills | PR | [#331](https://github.com/addyosmani/agent-skills/pull/331) session-quality-gate | ❌ closed 未合并（内容并入 #429 repository-memory log tier） | 2026-07 |
| 13 | modelscope/evalscope | PR | [#1576](https://github.com/modelscope/evalscope/pull/1576) fix(judge): LLM-judge fail-close [ERROR] guard + NaN | ✅ merged（维护者 Yunnglin APPROVED + 亲自推 1 commit 修 NaN/yapf） | 2026-08-14 |
| 14 | modelscope/evalscope | Issue | [#1575](https://github.com/modelscope/evalscope/issues/1575) LLM-judge 静默错分审计 | ✅ 被确认 + 并入维护者 LLM-judge 重构计划（失败降级 point 3 由其实现） | 2026-08-13 |

**Verification notes (2026-07-28, browser-verified; #12 added 2026-08-12):**
- #1-3: Confirmed merged via GitHub PR pages and profile README update
- #12: ⚠️ 修正 2026-08-12 —— **未合并**。event-29091130062 = addyosmani 关闭，横幅 "Closed with unmerged commits"。此前误报 merged 的教训：`3336107` 是分支 commit（后被 force-push 换为 `0436976`），非 merge；badge 是 Closed。addyosmani 明示内容并入 #429（repository-memory）log tier → 贡献机会在 #429，不在 #331（这正好印证：合并没有发生，之前"第 4 个合并贡献"的说法作废）
- #4: Open, daltino approved, coderabbitai reviewed, merge conflicts pending
- #5: 4 participants, PR #6491 built by ashusnapx with 96 tests passing, 2 commits ref the issue — strongest non-merged item
- #6-9: 0 maintainer reviews as of verification date
- #10: 0 human responses in 2 weeks
- #11: Auto-closed by langchain-oss-automated-triage bot, labeled "external"

---
*最后更新: 2026-08-12*
*交叉引用: [[../dashboard]] [[../github/notifications]] [[research-pipeline]] [[content-pipeline]]*
