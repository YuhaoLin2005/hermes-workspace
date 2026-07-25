# 数字分身路由表

> 我不是 agent。我是一张表——告诉系统"这个任务→加载哪些知识库+哪些规则+哪个 agent"。
> 源仓库更新后，对应 KB 可能过时——检查每个 KB 的 `最后更新` 时间戳。

## 策略决策引擎

> 每次 session 启动时：读 dashboard.md + research-pipeline.md → 生成当前状态 → 双池评估优先级 → 输出"今天做什么"。

```
启动加载: kb-strategy/dashboard.md + kb-strategy/research-pipeline.md + kb-strategy/content-pipeline.md
状态快照: 从 dashboard 提取关键数字 → 报告"当前在哪"
阻塞检查: 从 research-pipeline 提取 critical_path → 找到当前 blocker
双池评估: 4 角色独立评估优先级（每人一句话+理由）→ 共识 top 3
输出格式:
  → 今天做什么：
    1. [P0] <最高优先级任务> — <原因>
    2. [P1] <次优> — <原因>
    3. [P2] <维护项> — <原因>

双池战略评估角色（固定 4 人）:
  - Carmack: 方法论视角——"什么动作能最大提升可信度？"
  - Wardley: 生态视角——"什么动作在价值链上最上游？"
  - Jobs: 叙事视角——"什么动作能让简历最好看？"
  - Cagan: 问题视角——"我们在解决真问题还是绕路？"
```

### 双池设计触发规则

| 用户意图 | 阶段 | 双池角色 | 介入点 |
|---------|------|---------|--------|
| "设计实验验证 X" | 设计评审 | Carmack(方法)+Hickey(简洁)+Schell(叙事) | 方案定稿前 |
| "写一篇关于 X 的文章" | 角度评审 | Jobs(读者在乎吗)+Traynor(前30秒)+Cagan(真问题) | 选题阶段 |
| "选哪个仓库做贡献" | 战略评审 | Wardley(生态定位)+Hickey(可维护性)+Abramov(概念匹配) | commit 前 |
| "这个实验够了吗" | 完整性评审 | Thompson(边界)+Carmack(漏什么)+Brooks(本质复杂度) | 写结论前 |

### 收尾规则

每次 session 做了任何事后，收尾序列：
1. 更新 `dashboard.md` 对应数字
2. 回复了评论 → 更新 `replies.md`
3. 实验完成 → 更新 `research-pipeline.md` → 检查 `content-pipeline.md` depends_on
4. 新文章 → 更新 KB hot/warm/cold + dashboard
5. 新 PR/issue → 更新 `github-strategy.md` + dashboard
6. 跑 `_check_kb.py` 确认无 stale 数据

---

## 路由规则

> **Owner**: 所有路由最终决策者为用户（林宇浩）。系统提供 KB + 双池审查 + 声音门，用户决定采纳/驳回/修改。
> **Format**: YAML schema — 固定字段名 → LLM attention 精确路由。与 `knowledge/_schema.md` 同模式。

```yaml
routes:
  - id: experiment-design
    triggers: ["design experiment", "validate methodology"]
    load_kb: [kb-experiments, kb-paper-claims]
    design_review:
      roles: [Carmack, Hickey, Schell]
      focus: "method + simplicity + narrative fit"

  - id: writing-review
    triggers: ["draft article", "pre-publish review"]
    load_kb: [kb-articles, kb-voice-reference]
    voice_review:
      roles: [Zinsser, Orwell, Graham]
      focus: "clarity + honesty + human voice"

  - id: code-review
    triggers: ["PR ready", "refactor complete"]
    load_kb: [kb-code, kb-security]
    code_review:
      roles: [Thompson, Torvalds, Beck]
      focus: "trust boundaries + taste + testability"

  - id: strategic-decision
    triggers: ["choose direction", "evaluate tradeoff"]
    load_kb: [kb-strategy, kb-market]
    strategy_review:
      roles: [Wardley, Hickey, Cagan]
      focus: "ecosystem position + maintainability + real problem?"
```

## KB 清单

| KB | 位置 | 层级 | 最后更新 |
|-----|------|------|---------|
| kb-strategy | `.claude/knowledge/strategy/` | dashboard+pipeline×3+github | 2026-07-19 |
| kb-devto | `.claude/knowledge/devto/` | hot(12)+warm(12)+cold(7)+commenters+experiments+replies | 2026-07-24 |
| kb-juejin | `.claude/knowledge/juejin/` | hot(7)+warm(11)+cold(2) | 2026-07-24 |
| kb-paper | `.claude/knowledge/paper/` | claims+structure | 2026-07-19 |
| kb-code | `.claude/knowledge/code/` | overview+scripts | 2026-07-19 |
| persona-principles | `~/.claude/.../memory/persona-principles.md` | 全场景人物原则+来源+置信度 | 2026-07-11 |
| persona-pool | `~/.claude/.../memory/persona-pool.md` | 工程双池详细配置(管理员+工人+随机池) | 2026-07-11 |
| kb-voice | `~/.claude/.../memory/voice-reference.md` | 1 | 用户维护 |
| L1 gate | `.claude/knowledge/_check_kb.py` | validator | 2026-07-19 |

## KB 新鲜度

| 源仓库 | 对应 KB | 过时条件 |
|--------|---------|---------|
| DEV.to (文章/评论) | kb-devto | 新文章发后 24h 未更新 |
| 掘金 (文章) | kb-juejin | 新文章发后 24h 未更新 |
| paper/ (论文/补充) | kb-paper | 论文结构或声明变更 |
| paper-validator/ (代码) | kb-code | 新脚本/新实验/目录变化 |
| strategy/ (策略) | kb-strategy | dashboard >7d 未更新 |
| paper/experiment/ | kb-code, kb-strategy | 新原始实验 → pipeline + dashboard 均需更新 |
| persona-principles.md | persona-principles KB | 新增人物或原则变更 |
| persona-pool.md | persona-pool KB | 管理员/工人/角色/随机池规则变更 |

**数字分身职责**: 每次 session 启动时检查 KB 最后更新时间 vs 源仓库最后修改时间 → 若 KB 更旧 → 提醒"XX KB 可能过时，需要更新"。

## Agent 清单

| Agent | 文件 | 用途 |
|-------|------|------|
| devto-copilot | `agents/devto-copilot.md` | DEV.to 评论+文章+实验建议 |
| juejin-writer | `agents/juejin-writer.md` | 掘金叙事弧引导+voice审查+发布适配 |
| experiment-runner | 待建 | 实验执行+数据分析 |
| paper-builder | 待建 | 论文写作辅助 |

---

*最后更新: 2026-07-24*
*这就是数字分身——一张表。不需要 agent，不需要新架构。*

## Session 启动序列

每次 session 启动时，按以下顺序加载（P0 联动架构 v1.0）：

1. **机械同步**（0 token，Python 脚本）：
   - `python knowledge/_signals.py` — 5条管线→dashboard 自动更新（每字段带 synced_at）
   - `python knowledge/_verify.py` — depends_on/claim/slug 引用完整性检查
2. **策略层**（一页纸全貌，~800 token）：
   - `knowledge/strategy/dashboard.md` — 量化数据快照（synced_at 证明新鲜度）
   - `knowledge/strategy/research-pipeline.md` — 当前阻塞 + 关键路径
3. **知识层**（按需加载，路由表已有规则）：
   - `knowledge/devto/hot.md` — 12 篇核心文章
   - `knowledge/devto/commenters.md` — 7 位评论者
4. **规则层**：
   - `~/.claude/projects/.../memory/voice-reference.md` — 声音校准
5. **输出**：策略引擎生成"今天做什么"（见 §策略决策引擎）

> **设计原则**：_signals.py 和 _verify.py 是机械层——不烧 token、不依赖 AI 判断。
> 它们回答"数字对吗？引用断了吗？"——AI 回答"今天做什么？"
