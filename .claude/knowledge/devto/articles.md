# DEV.to Article Index

> 32 posts published (as of 2026-07-26). 每发新文章后更新。
> `[key]` = /devto-copilot 命令参数。论文实验系列有完整索引，平台工程系列简洁索引。

## 论文实验系列（9篇——有详细索引）

### [audit-ctbv] I Discovered AI Agents Can't Self-Verify. The Real Problem Is Much Bigger.
- **URL**: https://dev.to/yuhaolin2005/i-discovered-ai-agents-cant-self-verify-the-real-problem-is-much-bigger-2jb6
- **Published**: 2026-07-26
- **Tags**: ai, machinelearning, programming, python
- **论文章节**: Full thesis synthesis — Prose Barrier + Three Paths + Gate Audit + CTBV Theory
- **关键数字**: 38 gates, 9 sessions, 339 entries, 87% noise; κ = 0.00; DPO 150 pairs
- **核心发现**: Gate audit revealed 87% noise; working gates check things LLMs physically can't fake; CTBV (Cross-Type Bidirectional Verification) — orthogonal blind spots → joint error = 0
- **关联评论者**: Mike Czerwinski, Dipankar Sarkar, Max Quimby, René Zander

### [cross-model] Your AI Gate Works Perfectly — Until You Switch Models
- **URL**: https://dev.to/yuhaolin2005/your-ai-gate-works-perfectly-until-you-switch-models-4bf0
- **Published**: 2026-07-18
- **Tags**: ai, machinelearning, programming, python
- **论文章节**: Experiment 4 (Multi-Model Scanner Calibration)
- **关键实验**: P1-1 cross-model (200 API calls, 3 models)
- **关键数字**: DS Pro alignment 5/5→2/5; DS Flash 100% checklist=空心合规
- **核心发现**: Gateability = rule_structure × model_capability; compliance=f(mechanizability) for DS Pro
- **关联评论者**: Mike Czerwinski

### [search] Search Didn't Make Your LLM Dumber. Unweighted Context Did.
- **URL**: https://dev.to/yuhaolin2005/your-web-search-is-making-the-model-dumber-4dj9
- **Published**: ~2026-07-03
- **论文章节**: Paper B
- **核心发现**: Search quality drop 源于未加权上下文，非检索本身
- **关联评论者**: Alice (主), Mike Czerwinski

### [150-tasks] I Ran 150 Tasks to Test If AI Agents Follow Rules
- **URL**: https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670
- **Published**: 2026-07-11
- **关键实验**: GateGuard on/off; syllogism vs imperative; 55.9%→0.7%
- **核心发现**: Mechanical gate eliminates format effect; ceiling effect IS the finding
- **关联评论者**: Mike Czerwinski, Dipankar Sarkar, René Zander, Alex Shevchenko, CodeKitHub

### [pre-reg] I Pre-Registered a Hypothesis. 600 API Calls Later, the Data Killed It.
- **URL**: https://dev.to/yuhaolin2005/i-pre-registered-a-hypothesis-600-api-calls-later-the-data-killed-it-1aec
- **Published**: 2026-07-15
- **关键实验**: 2×2 factorial (format × gate), n=600, d=0.605
- **核心发现**: Pre-registered hypothesis killed; SHA256 scheme; tamper-resistance ≠ third-party verifiability
- **关联评论者**: Mike Czerwinski, Dipankar Sarkar, Alex Shevchenko

### [feedback] Your Feedback Made This Better — Here's What Changed
- **URL**: https://dev.to/yuhaolin2005/your-feedback-made-this-better-heres-what-changed-4ol2
- **Published**: 2026-07-13
- **核心发现**: 5 community-driven improvements documented
- **关联评论者**: Mike Czerwinski, Dipankar Sarkar, Alice

### [neural-gate] I Built a Neural Gate for My AI Agent — Layer 2 of Self-Verification
- **URL**: https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2
- **Published**: 2026-07-10
- **核心发现**: Logprob-based L2 gate; decision-token targeting
- **关联评论者**: Mike Czerwinski, René Zander

### [self-verify] AI Agents Can't Self-Verify — And That's a Structural Constraint, Not a Bug
- **URL**: https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l
- **Published**: 2026-07-10
- **核心发现**: Prose Barrier identified; 平行发明(René Zander)
- **关联评论者**: René Zander

### [follow-up] Follow-Up: Decision-Token Measurement, Format-as-Fallback
- **URL**: https://dev.to/yuhaolin2005/follow-up-decision-token-measurement-format-as-fallback-and-what-changed-18jo
- **Published**: 2026-07-13
- **关联评论者**: Dipankar Sarkar, CodeKitHub

---

## 实验方法系列（5篇——logprob/统计/drift/DPO）

### [logprob-safe] I Told My AI "You're Safe to Say I Don't Know." Then I Measured What Changed — With Logprobs.
- **URL**: https://dev.to/yuhaolin2005/i-told-my-ai-youre-safe-to-say-i-dont-know-then-i-measured-what-changed-with-logprobs-986
- **Published**: 2026-07-12
- **主题**: L0 safety prompt → logprob measurement

### [zero-effect] My Experiment Showed Zero Effect. A Statistician Told Me My Measurement Was Broken.
- **URL**: https://dev.to/yuhaolin2005/my-experiment-showed-zero-effect-a-statistician-told-me-my-measurement-was-broken-4g26
- **Published**: 2026-07-12
- **主题**: 统计功效、测量有效性、null result 解读

### [drift-metric] My Loss Went Down, But My Model Still Broke — So I Built a Drift Metric
- **URL**: https://dev.to/yuhaolin2005/my-loss-went-down-but-my-model-still-broke-so-i-built-a-drift-metric-e8f
- **Published**: 2026-07-08
- **主题**: L4 drift predictor 设计

### [compact-dumber] Your LLM Gets Dumber Every Time You Compact Context — And Nobody Is Measuring It
- **URL**: https://dev.to/yuhaolin2005/has-anyone-measured-how-llm-output-quality-degrades-across-multiple-compactions-1dad
- **Published**: 2026-06-27
- **主题**: Context compaction → quality degradation (第一篇 DEV.to)

### [dpo-causal] I DPO-Trained a Model to Prefer Causal Reasoning. The Base Model Already Did — It Just Couldn't Act On It.
- **URL**: https://dev.to/yuhaolin2005/i-dpo-trained-a-model-to-prefer-causal-reasoning-the-base-model-already-did-it-just-couldnt-act-1kip
- **Published**: 2026-07-24
- **Tags**: ai, machinelearning, python, deeplearning
- **论文章节**: Experiment 5 (DPO Causal Internalization)
- **关键实验**: Qwen2.5-1.5B QLoRA → DPO preference training; base model already encodes causal reasoning
- **关键数字**: SYLL=0.941, IMP=0.750, TOKCTRL=0.667, COTCTRL=1.048 (4-dimension causal format scoring)
- **核心发现**: Base model already has causal reasoning capability — DPO unlocks action, doesn't teach from scratch; format-control gap (TOKCTRL 0.667 vs COTCTRL 1.048) reveals DPO selects for CoT-style reasoning over token-level control
- **关联评论者**: (new, no comments yet)

---

## 架构/设计哲学系列（6篇）

### [meta-cognition] Meta-Cognition Is the Future of AI Personalization — A 4-Quadrant Framework to Build It
- **URL**: https://dev.to/yuhaolin2005/meta-cognition-is-the-future-of-ai-personalization-a-4-quadrant-framework-to-build-it-5fki
- **Published**: 2026-07-09
- **主题**: 4象限元认知框架

### [self-referential] I Built a Self-Referential AI System. Then Anthropic Discovered the Same Architecture in Claude.
- **URL**: https://dev.to/yuhaolin2005/i-built-a-self-referential-ai-system-then-anthropic-discovered-the-same-architecture-in-claude-3m73
- **Published**: 2026-07-07
- **主题**: 自指环 / Strange Loop — Anthropic 平行发现

### [dual-pool] I Built a Dual-Pool Adversarial Review System for AI Agents — And It Actually Works
- **URL**: https://dev.to/yuhaolin2005/i-built-a-dual-pool-adversarial-review-system-for-ai-agents-and-it-actually-works-595j
- **Published**: ~2026-06-29
- **主题**: 双池对抗审查系统

### [single-modal] Single-Modal LLMs Have a Blind Spot. Here's How to Fix It.
- **URL**: https://dev.to/yuhaolin2005/single-modal-llms-have-a-blind-spot-heres-how-to-fix-it-2ogd
- **Published**: ~2026-06-28
- **主题**: 单模态 LLM 盲点

### [expert-board] Stop Using Generic AI Review. Build Your Own Board of Experts.
- **URL**: https://dev.to/yuhaolin2005/stop-using-generic-ai-review-build-your-own-board-of-experts-196n
- **Published**: 2026-07-21
- **Tags**: ai, programming, productivity, codequality
- **主题**: 命名原则锚定→去关联前提→33 persona独立幻觉
- **核心发现**: 33个persona同意≠33个独立判断；跨模型decorrelation测试才能验证专家团是否真独立
- **关联评论者**: Mike Czerwinski


### [zero-output] Your AI Agent's Best Work Produces Zero Output — And That's the Point
- **URL**: https://dev.to/yuhaolin2005/your-ai-agents-best-work-produces-zero-output-and-thats-the-point-5b3a
- **Published**: ~2026-07-04
- **主题**: 零输出作为质量信号

---

## 配置/协议工程系列（7篇）

### [self-verifiable] I Made My AI Rules Self-Verifiable. Now They Catch Their Own Violations.
- **URL**: https://dev.to/yuhaolin2005/i-made-my-ai-rules-self-verifiable-heres-how-19ea
- **Published**: ~2026-07-03
- **主题**: 自验证规则 → L1 gate 前身

### [config-fighting] Your AI Config Files Are Fighting Each Other
- **URL**: https://dev.to/yuhaolin2005/your-ai-config-files-are-fighting-each-other-13c7
- **Published**: ~2026-07-01
- **主题**: 多配置文件冲突

### [config-parse] Your AI Agent Burns 30% of Its Context Parsing Your Config. Fix It in 5 Minutes.
- **URL**: https://dev.to/yuhaolin2005/your-ai-agent-burns-30-of-its-context-parsing-your-config-fix-it-in-5-minutes-5ejo
- **Published**: 2026-07-06
- **主题**: 配置瘦身 → BODY.md 37% 精简的前身

### [context-engineering] Context Engineering Isn't Just for Prompts — It's for Config Files Too
- **URL**: https://dev.to/yuhaolin2005/context-engineering-isnt-just-for-prompts-its-for-config-files-too-11m7
- **Published**: ~2026-07-02
- **主题**: Context engineering 应用于配置

### [token-burning] Your AI Agent Is Burning Tokens. Do You Know How Many?
- **URL**: https://dev.to/yuhaolin2005/your-ai-agent-is-burning-tokens-do-you-know-how-many-2fhf
- **Published**: ~2026-07-01
- **主题**: Token 消耗审计

### [deepseek-swap] I Run DeepSeek on Claude Code — How I Swap Models by Changing Only One File
- **URL**: https://dev.to/yuhaolin2005/i-run-deepseek-on-claude-code-how-i-swap-models-by-changing-only-one-file-3ee5
- **Published**: ~2026-06-30
- **主题**: DeepSeek + Claude Code 集成

### [forget-protocol] I Open-Sourced the Protocol That Stops AI From Forgetting Who You Are
- **URL**: https://dev.to/yuhaolin2005/i-open-sourced-the-protocol-that-keeps-my-ai-from-forgetting-who-i-am-4pp
- **Published**: ~2026-07-05
- **主题**: 身份持久化协议 → 自指环前身

---

## 工具/效率系列（5篇）

### [feedback-loop] How I Built a File-Timestamp-Based Feedback Loop to Enforce AI Output Quality
- **URL**: https://dev.to/yuhaolin2005/how-i-built-a-file-timestamp-based-feedback-loop-to-enforce-ai-output-quality-1ibc
- **Published**: 2026-07-07
- **主题**: 文件时间戳 → 质量门

### [open-source-flywheel] The Open Source Flywheel: How I Turn Personal AI Scripts Into Merged PRs
- **URL**: https://dev.to/yuhaolin2005/the-open-source-flywheel-how-i-turn-personal-ai-scripts-into-merged-prs-528d
- **Published**: 2026-07-06
- **主题**: 个人脚本→开源 PR 的工作流

### [starter-kit] I Packed DeepSeek V4 + Claude Code Into a Starter Kit. Clone It and Ship.
- **URL**: https://dev.to/yuhaolin2005/i-packed-deepseek-v4-claude-code-into-a-starter-kit-clone-it-and-ship-13dn
- **Published**: ~2026-07-05
- **主题**: 一键部署 starter kit

### [self-healing] I Built a Closed-Loop Self-Healing System for My AI Config — By Accident
- **URL**: https://dev.to/yuhaolin2005/i-built-a-closed-loop-self-healing-system-for-my-ai-config-by-accident-51m4
- **Published**: ~2026-07-04
- **主题**: 配置自愈系统

### [skill-filter] I Installed 50 AI Agent Skills Blindly. Here's the 3-Question Filter I Use Now.
- **URL**: https://dev.to/yuhaolin2005/i-stopped-installing-ai-agent-skills-blindly-heres-what-i-do-instead-2f3o
- **Published**: ~2026-07-02
- **主题**: Agent skill 评估过滤器

---

## 论文章节→文章速查

| 章节 | DEV.to 文章 |
|------|------------|
| Prose Barrier | [self-verify] [config-fighting] [self-verifiable] |
| L1 Gate | [150-tasks] [self-verify] [feedback-loop] |
| L2 Neural Gate | [neural-gate] [logprob-safe] |
| Format-Gate | [150-tasks] [pre-reg] [follow-up] |
| Search Weight | [search] |
| Cross-Model | [cross-model] |
| SHA256 Pre-reg | [pre-reg] |
| Drift/L4 | [drift-metric] [compact-dumber] |
| DPO Internalization | [dpo-causal] |
| Self-Referential | [self-referential] [forget-protocol] [self-healing] |
| Dual-Pool Review | [dual-pool] |
| Expert Board/Persona | [expert-board] |
| Community Docs | [feedback] + community-experiments-2026-07-17.md |

---

*最后更新: 2026-07-24 — 31/31**
