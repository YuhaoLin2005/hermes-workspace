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
| 3 | alirezarezvani/claude-skills | PR | [#867](https://github.com/alirezarezvani/claude-skills/pull/867) persona-review | ✅ merged (Co-authored-by — 概念来自 #866) | 2026-07 |
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
| 15 | TencentCloud/TencentDB-Agent-Memory | PR | [#977](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/977) conversation-delete isolation 对齐 L1 atomic delete | 🔄 open（8/15 侦察：已 CONFLICTING，upstream 8/14 commit 6382e8a v2.0.1-beta.1 抢合同功能→pivot 只补回归测试，24-48h 内承认+pivot，勿 rebase 重复 diff） | 2026-08-13 → 08-15 |
| 16 | coze-dev/coze-loop | PR | [#617](https://github.com/coze-dev/coze-loop/pull/617) strategy-4 score 正则键锚定（修 reason 泄漏） | 🔄 open（8/15 侦察：MERGEABLE, CI 2/2 绿, 单 commit, 1-behind, 零冲突；唯一阻塞=无人 review→issue#257 温和引导 lsy357，勿连环催审） | 2026-08-13 → 08-15 |
| 17 | agentscope-ai/agentscope | Discussion | [#2306](https://github.com/agentscope-ai/agentscope/discussions/2306) AgenticMemoryMiddleware recency marker | 🔄 open（Ideas 类目, 等维护者裁决 opt-in 表面） | 2026-08-13 |
| 18 | TencentCloud/TencentDB-Agent-Memory | Comment | [#918/#872](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/918) 盲区审查评论（native-hybrid 短路路径 + sessionId 默认脚枪根因） | ✅ 已发（验证他人 PR 正确性 = 最高价值贡献） | 2026-08-13 |
| 19 | SWE-bench/SWE-bench | Issue | [#626](https://github.com/SWE-bench/SWE-bench/issues/626) test_pass≠human_annotation 分歧分析提案 | ❌ closed 2026-08-14（john-b-yang: 无核心维护容量但开放 PR）→ 礼貌收尾（comment 5295456187），分歧分析改走独立公开写稿 | 2026-07-26 → 08-14 |
| 20 | agentscope-ai/agentscope | PR | [#2325](https://github.com/agentscope-ai/agentscope/pull/2325) fix(app): interrupt assembling chat run via local registry check (#2320) | 🔄 open（**iamroylim APPROVED** 2026-08-16 05:25Z「25 passed, No blocking issue」；作者回复已发 comment 5306009742；等合并后独立 PR 做 direction #2——合成 INTERRUPTED 终端事件） | 2026-08-16 |
| 21 | huggingface/evaluate | PR | [#778](https://github.com/huggingface/evaluate/pull/778) behavioral_drift output integrity metric | 🔄 open（**用户原创设计+实现**，147 行零依赖；= lm-eval #3968 的移植源） | 2026-07 |
| 22 | EleutherAI/lm-evaluation-harness | Issue | [#3924](https://github.com/EleutherAI/lm-evaluation-harness/issues/3924) behavioral_drift proposal | 🔄 open（用户提案，6 轮 Qwen fine-tune 实证） | 2026-07 |
| 23 | anthropics/skills | PR | [#1367](https://github.com/anthropics/skills/pull/1367) self-audit skill（机械验证 + 四维推理质量门 v1.3.0） | 🔄 open（MERGEABLE，REVIEW_REQUIRED，停滞 ~2 月；**#1360/#1361/#1365 三个早期草稿的成活版**） | 2026-06-28 |
| 24 | open-compass/opencompass | PR | [#2598](https://github.com/open-compass/opencompass/pull/2598) fix(datasets): anchored grade extraction + surface judge failures in generic llmjudge | 🔄 open（MERGEABLE，REVIEW_REQUIRED，零 review；与 evalscope #1576 同 bug 类=静默错分） | 2026-08-15 |
| 25 | NextFrontierBuilds/agent-best-practices | PR | [#1](https://github.com/NextFrontierBuilds/agent-best-practices/pull/1) format consistency anti-pattern（混合配置风格解析税） | 🔄 open（MERGEABLE，无 review，停滞 ~2 月） | 2026-06-28 |
| 26 | Aider-AI/aider | Issue | [#5496](https://github.com/Aider-AI/aider/issues/5496) verification pattern for instruction compliance | 🔄 open（0 回应） | 2026-07-26 |
| 27 | affaan-m/ECC | Issue | [#2389](https://github.com/affaan-m/ECC/issues/2389) Semantic verb system for cross-harness skill portability（10 verbs + `requires` frontmatter） | 🔄 open（0 回应） | 2026-06-29 |
| 28 | agentskills/agentskills | Issue | [#440](https://github.com/agentskills/agentskills/issues/440) 可选 `requires` 字段实现 runtime-agnostic skill 移植 | ❌ closed（作者追加 5 点论证 comment 后被关） | 2026-06-29 |
| 29 | anthropics/skills | Issue | [#1385](https://github.com/anthropics/skills/issues/1385) **[Proposal] Reasoning Quality Gate Pipeline**（pre-task calibration → adversarial review → delivery verification） | 🔄 open（4 评论；外部 tonydzi 2026-08-01 提问**已于 2026-10-09 回复**，comment 6081412364） | 2026-07-03 |
| 30 | shaneliuyx/self-improving-agents-curriculum | Issue | [#1](https://github.com/shaneliuyx/self-improving-agents-curriculum/issues/1) L0-L3 数据驱动决策阈值用于 agent 成本追踪 | 🔄 open（0 回应） | 2026-06-29 |

**Verification notes (2026-07-28, browser-verified; #12 added 2026-08-12; #3 深度核实 2026-08-15):**
- #3 ⚠️ **深度核实 2026-08-15（gh api）**：claude-skills **#866（named-persona，作者=我）未合并**；维护者 alirezarezvani 把 #866 概念吸收进**他自己开的 #867**（标题 "hardened from #866"，commit message 明写 "Concept contributed by @YuhaoLin2005 in PR #866"，commit author=Claude）+ 保留 `Co-authored-by: YuhaoLin2005` 后合并。**首页写 claude-skills 应指 #867（共作），不是 #866**
- #1-3: Confirmed merged via GitHub PR pages and profile README update
- #12: ⚠️ 修正 2026-08-12 —— **未合并**。event-29091130062 = addyosmani 关闭，横幅 "Closed with unmerged commits"。此前误报 merged 的教训：`3336107` 是分支 commit（后被 force-push 换为 `0436976`），非 merge；badge 是 Closed。addyosmani 明示内容并入 #429（repository-memory）log tier → 贡献机会在 #429，不在 #331（这正好印证：合并没有发生，之前"第 4 个合并贡献"的说法作废）
- #4: Open, daltino approved, coderabbitai reviewed, merge conflicts pending
- #5: 4 participants, PR #6491 built by ashusnapx with 96 tests passing, 2 commits ref the issue — strongest non-merged item
- #6-9: 0 maintainer reviews as of verification date
- #10: 0 human responses in 2 weeks
- #11: Auto-closed by langchain-oss-automated-triage bot, labeled "external"
- #21/22 ⚠️ **核实 2026-08-17（gh api）**：lm-eval **#3968 作者=Kelvinz-89757（非用户）**——第三方移植用户 huggingface/evaluate **#778**（原创 behavioral_drift，147 行零依赖）+ lm-eval issue **#3924**（提案，6 轮 Qwen 实证）设计，PR body 署名 @YuhaoLin2005。简历/对外只能写「被 lm-eval 列移植候选」（=社区认领我的设计，反而更硬），**禁暗示「我的 PR 合入」**——点开 #3968 显示作者非用户

**Verification notes (2026-09-17, `gh search prs --author YuhaoLin2005` 全量重核):**
- ⚠️ **全生命周期 32 个 PR = open 12 + merged 5 + closed 15**。本表原 22 行**漏记 3 个 open PR**，已补 #23-#25。
  open 实数 **12**（dashboard `prs_open` 已同步 10→12）。漏记根因：此前用**逐条 `gh pr view` 手工比对**，
  没做全量 `search`——漏掉的正好是"没想到要去查"的那几个仓库。**教训：贡献表核验必须用全量 search 打底，不能靠想起来查谁。**
- **13 个 closed 未合并 PR 不入表（点名 + 说明理由）**：anthropics/skills #1360/#1361/#1365、
  ECC #2365/#2375/#2376/#2404/#2407、claude-skills #884/#887、hermes-agent #54631/#54880、
  daymade/claude-code-skills #118。它们绝大多数是 **#1367 / #2377 / #2378 / #867 的上位条早期草稿或重复提交**
  （如 #1360→#1361→#1367 同一 self-audit skill 三次迭代），单列成行只会虚增行数、不增信息
- ⚠️ **7 条 fork CI 失败通知 = 基础设施噪音，非代码失败**：`gh run list` 耗时 `720h1m3s`（正好 30 天）
  → fork 上的 job 排队 30 天后超时。PR 层 check 汇总 0 failing，分支确实存在于两个 fork。
  **看到 fork CI 红不要改代码**——先看 duration 是不是 720h
- ⚠️ **#4（ECC #2496）与 #20（agentscope #2325）实测 CONFLICTING**：#4 与本表既有记述一致（line 80「merge conflicts pending」）；
  #20 是 8/16 获 APPROVED **之后新出现**的冲突——**APPROVED ≠ 可合并**，需 rebase 后再推
- ✅ **#3 共作口径复核通过**：`gh api repos/alirezarezvani/claude-skills/pulls/867/commits` 取到 commit `f7a9a7b2`，
  message 内含 `Co-authored-by: YuhaoLin2005 <278400118+YuhaoLin2005@users.noreply.github.com>`
  与 `Concept contributed by @YuhaoLin2005 in PR #866`。**#867 author=alirezarezvani（非用户）**——
  merged=4 外部口径（3 直连 + 1 共作）成立，但对外仍**禁写「我合并了 #867」**，与 lm-eval #3968 同一条纪律
- ✅ **3 个直连 merged 作者复核**：ECC #2377（2026-06-30T02:22:52Z）、ECC #2378（2026-06-30T02:22:55Z）、
  evalscope #1576（2026-08-14T06:49:07Z），author 全部 = YuhaoLin2005
- ⚠️ **同一条纪律对 issue 也成立 —— `issues_filed` 从 4 严重漏记到 11**：全量
  `gh search issues --author YuhaoLin2005` = **21 = 外部 11 + 自仓 10**。已补 #26-#30
  （aider #5496 / ECC #2389 / agentskills #440 / anthropics/skills #1385 / self-improving-agents-curriculum #1）。
  自仓 10 个（YuhaoLin2005/imprint#1 + gategrow/checkgrow #1-5 + gategrow/delivery-gate #1-4）不计入，口径同 merged。
  **我这次差点又犯同一个错**：刚写下「必须全量 search 打底」，却只对 PR 做了 search —— 对 PR 打全量、对 issue 靠想，等于没打
- ✅ **#29（anthropics/skills #1385）的实质提问（2026-08-01，外部 tonydzi）已于 2026-10-09 回复**（comment 6081412364；本行原写作「未回」，见下行注）：
  tonydzi 主动提出愿关掉自己竞争的 #1460 让位给用户的分模块方案，并问了一个**直击本 session 主题**的问题——
  「你的门有没有记录**它上次真的拦下东西是什么时候**，而不只是**它上次运行是什么时候**？
  一个跑了但没人看输出的门 = 毫无意义的绿灯，而且它**静默劣化**，比直接失败更糟。」
  这正是 `POOL_EVOLVE` 被退役的原因，也正是 `_signals.py` 假红的病因。**⛔ 此处曾标「未回，我不代拟」—— 已于 2026-10-09 回复（comment 6081412364），详见页脚 2026-10-09 条**

---
*最后更新: 2026-10-09*
*2026-10-09 已回（结案 9/17 挂的「#29 未回，我不代拟」）：anthropics/skills **#1385** 回复 tonydzi 2026-08-01 的 standing offer（comment 6081412364）。他要的是「你的模块有没有记录**最后一次真正拦下**什么，而不只是它上次运行是什么时候」。回复给了实测数（源：`session-gate-log.jsonl` 1244 条事件 / 6 个门 / 2026-07-17→今）：`voice-compliance` **26 块 / 68 事件 (38%)**，最后拦下 **2026-10-09**；`writing-workflow` **34 块 / 43 事件 (79%)**，最后拦下 **2026-09-24**。另四个门**答不了这个问题**：`write_guard`(963 条) 与 `evidence-gate`(164 条) 是**结构性单边**——唯一调用点（`write-guard.py:809`、`evidence-gate.py:238`）event 字面量恒为 `blocked` ⇒ `blocked/total` 对**任何**输入恒 **100%**，是记账口径不是门的行为（同 memory/gate-logging-only-negatives-always-reads-100pct）；`voice_guard`(5 条)/`stage5-review`(1 条) 走 `content-guard.py`（:575 `warned` / :583 `blocked`，结构上双边），**样本太小，明确声明不下结构性结论**。收口结论=修法在**补双边日志**（warned/allowed 也记），不在改门。点名接下 **#1423 delivery-verification** 的 review（tonydzi 已自行关闭其对比 PR #1460，兑现了他「维护者偏好模块化我就关」的承诺）。**口径不变**：回复非新 PR/issue，`prs_open` 12 / `prs_merged` 4 / `issues_filed` 11 均不动。证据：`oss-pr-work/anthropics-skills/{reply-1385.md, evidence-gate-stats-20261009.txt}`；追踪条目 `KB/devto/replies.md` = `github-anthropics-skills-1385`。⚠️ **顺带发现（非本次产生）**：`replies.md` 的 yaml 块自首版提交 `9c73d5f` 起即无法解析（悬空 `reply_` 已修；顶格 `summary:` 截断列表一处**待用户裁决**）*
*2026-09-17 全量重核: `gh search prs --author YuhaoLin2005` 全生命周期 **32 PR（open 12 / merged 5 / closed 15）**
*2026-09-17 全量重核: `gh search prs --author YuhaoLin2005` 全生命周期 **32 PR（open 12 / merged 5 / closed 15）**，补记 3 个漏掉的 open PR（#23 anthropics/skills #1367、#24 open-compass #2598、#25 NextFrontierBuilds #1），dashboard `prs_open` 10→12 同步更正。merged 仍 = 4（外部口径）：#867 共作 trailer 已验实（commit f7a9a7b2 含 `Co-authored-by: YuhaoLin2005` + `Concept contributed by @YuhaoLin2005 in PR #866`），3 个直连 merged（ECC #2377/#2378、evalscope #1576）author 全部=用户。#2325 由 APPROVED **转 CONFLICTING**（新），#2496 维持 CONFLICTING。7 条 fork CI 红 = `720h1m3s` 排队超时，非代码问题。13 个 closed 未合并 PR 点名不入表（多为上位条早期草稿）。**issue 同法全量重核：21 = 外部 11 + 自仓 10，补记 #26-#30，dashboard `issues_filed` 4→11**（旧值只记了表内 4 条）。⚠️ #29 anthropics/skills #1385 有外部 tonydzi 2026-08-01 实质提问——问的是「门有没有记录它上次真拦下东西是什么时候」，直击 POOL_EVOLVE 退役 / `_signals.py` 假红的同一命题。**该条已于 2026-10-09 回复（comment 6081412364），见下方 2026-10-09 条，本条「未回」结论已作废** *
*交叉引用: [[../dashboard]] [[../github/notifications]] [[research-pipeline]] [[content-pipeline]]*
*2026-08-17 追加: 新增贡献 #21 evaluate #778 + #22 lm-eval #3924（均为用户原创 behavioral_drift，route-table 核证时发现此前漏记）。⚠️ lm-eval #3968=Kelvinz 移植用户设计（第三方 port，非用户 PR）——简历「列移植候选」措辞准确，禁暗示合入。详见 [[../../../../.claude/projects/C--Users-86131/memory/job-asset-route-table]]*
*2026-08-16 追加: agentscope **#2325 获 iamroylim APPROVED**（2026-08-16 05:25Z，review 4945471700「25 passed, No blocking issue」）——assembly 窗口 interrupt 竞态修复（#2320 保守版，构造器注入 ChatRunRegistry）。作者致谢回复已发（comment 5306009742），边界与 follow-up（cross-replica marker + INTERRUPTED 终端事件）双方对齐。⚠️ 发布踩坑：gh api -f body=@file 在 Windows 下发成路径字面量（`@C:/...`），用户删除后改 Python JSON + `--input` 重发成功——外部发送一律用 `--input` 并拉回核验（[[../../../../.claude/projects/C--Users-86131/memory/growth-log/2026-08-16-gh-atfile-pitfall]]）。下一步：等 #2325 合并 → direction #2 独立 PR*
*2026-08-14 追加: profile README 已更新（evalscope merged, Zenodo DOI, commits 131+）。深化方向: ①evalscope 1 PR→持续贡献者（跟语义问题+下个 issue）②3 个 open PR 提合并率 ③"静默失败"案例研究文章。详见 [[../resume-assets-2026-08]]*
*2026-08-15 追加: **合并数口径 = 仅外部仓库**。全量核实（gh api pulls/authored + 逐 PR merged 字段）：外部 merged = evalscope#1576 + ECC#2377/#2378 + claude-skills#867（共作）= 4；**自仓 merged（YuhaoLin2005/claude-skills#1、deepseek-claude-code-starter#1）不计入含金量**。首页按用户要求只写合并（删 "3 open"），open 记录仍在本表保留供 8/20 复查。详见 [[../resume-assets-2026-08]]*
*2026-08-15 深化路线: P0-A evalscope bullet / P0-B 静默失败案例文章 / P0-C E1b-v2 方法论 / P1 合并率——执行细节见 [[../deepening-roadmap-2026-08]]*
*2026-08-15 夜追加: 方向锁定=AI 应用评测/验证（方向+验证角色）；PR 叙事诚实重构（AI 辅助实现→「定位问题/定义修复方向与验证标准/本地验证/协作 merge」是真实贡献，简历/文章/面试口径统一）；P1 merges 下一动作=career/p1-merges-prep-2026-08-15（用户批准后执行，8/20 复查）；**两条消息已草稿待批=career/p1-message-drafts-2026-08-15（A: #257 引导 lsy357 看 #617 · B: #977 承认 upstream 已修+pivot 测试-only）***
*2026-08-15 深夜侦察（gh 只读）· evalscope 下一步机会: #1575 仍 open，Yunnglin 确认 4 缺口 + LLM-judge 重构计划（position swapping / repeated scoring / multi-judge aggregation / disagreement stats / offline re-scoring / **failure degradation=用户 point 3**）；「refactor design 写好后会在此跟进」。另：维护者往 #1576 分支推过 NaN 修复 commit（main 上 NaN 静默变 1.0 → 改后 fail closed 到 clamp_min）。**新 issue #1578（AUTHENSOR, 8/14, 0 评论）**：AIME 判定被 "Yes" 一词触发 + AIR-Bench 取最后两个裸数字——与 coze-loop #617 同 bug 类（子串/位置启发式）。**推荐下一动作（待用户批准）**：在 #1578 评论锚定 key-position 方法论先例 + offer 审计，作为 #1576 合并后的旗舰仓库续作。详见 career/eval-next-move-2026-08-15*
*2026-08-16 追加: **交付物清洁度纪律**（用户纠正，memory=facing-content-no-audit-traces）：简历/防御包/PR 描述等面向人内容一律纯人话——不写「登录态 dashboard 实测」「公开 API 已移除」「608→621」「gh: 」等内部核证痕迹（读者会读成不专业/此地无银，且暴露数字曾倒退）。核证细节只留内部审计文档（简历链接验证报告 / plan / 本文件 verification notes）。已应用：eval-lapiscv.html/-full.html 注释区 + interview-defense-eval-general.md 正文清理，两版 PDF 重导出 2 页 OCR 通过*
