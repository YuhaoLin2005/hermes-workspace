# 找老师讨论——一页现状报告

> 林宇浩，大三，FAFU 空间信息。2026-07-10。

## 我做了什么

搭建了一个 AI agent 自配置系统——让 Claude Code 能检测自己的配置是否过期、脚本是否未接线、产出是否未验证，并在检测到问题时自动阻断或再生自我模型。

核心结构：五层架构（身份→校准→执行→记忆→反馈）+ 四道机械门（execution-gate, hook-audit, quality-gate, claim-gate）+ 自指闭包（gate 间互相守护，系统能诊断自己架构缺口）。

初步实验：原始 30 任务（alternating baseline/treatment）+ 本 session 8 个 treatment trial。原始数据 Fisher p=0.0092。**诚实说：单人评分、未盲法、无 Placebo Control——p 值不可信。** 数据只够说明"值得做一个严格对照实验"，不够说明"架构有效"。

## 联网搜索

两路独立搜索对标 7 个开源框架，0 个做"系统自我模型再生"。"声称型 vs 证据型认知"分离、"脚本创建了但没接线"检测——目前没有竞品做这些。HyperAgents（Meta, ICLR 2026）在代码层做自修改，我们在配置层。

## 我的限制（诚实）

- 单张 RTX 3060 6GB——跑不动大模型对比实验
- 单人——自己跑自己评，没有第二评分者，没有 Cohen's kappa
- 没有 Placebo Control——无法排除"token 量效果"
- 大三本科——文献、统计、写作都自学的，肯定有漏洞
- 没有导师——方向是自己摸出来的

## 我弥补了什么

- 所有数据公开（github.com/YuhaoLin2005）
- 所有文章机械 fact-check（API 验证，不靠记忆）
- 33 篇 growth-log（完整研发记录，从 June 到 July）
- 联网搜索确认不是自嗨
- 论文不藏 limitations

## 想问您的问题

1. 这个方向值得写吗？
2. 如果值得——投哪里？（CHI LBW / ACL SRW / arXiv）
3. 我现在最需要补什么？
4. 您愿意指导吗？或能帮我找适合的指导老师吗？

## 附：支撑材料索引

> 所有文件在 `memory/` 下。按阅读顺序排列。

**快速了解（5 分钟）**
- `professor-questions-prepared.md` — 18 个预期问题+诚实回答
- `paper-outline-part1.md` — 论文大纲 + 竞品对比（HyperAgents/Ouro Loop/ETH Zurich）

**技术细节（如需深入了解）**
- `paper-methods-draft.md` — Methods 草稿：五层架构+实验设计+统计
- `paper-experiment-expansion.md` — 实验扩展：power analysis, n=60 target, causal swap
- `paper-trial-results.md` — 初步数据：8 treatment trial
- `paper-task-specs.md` — 30 个任务完整规范
- `paper-scoring-template.md` — 评分模板（5-cat + 3-gate）
- `paper-revision-plan-v2.md` — 完整论文修订方案（今天专家审查）

**研发记录（证明不是一次性的）**
- `self-model.md` — 系统自我模型 v0.9.1
- `growth-log/` — 33 篇日志，2026-06-25 到 2026-07-10
- `emerging-patterns.md` — 从翻车中沉淀的通用模式

**GitHub 仓库**
- `github.com/YuhaoLin2005/hermes-workspace` — 架构+实验
- `github.com/YuhaoLin2005/digital-twin-trainer` — QLoRA 微调管线
- `github.com/YuhaoLin2005/compact-counter` — 压缩计数器
