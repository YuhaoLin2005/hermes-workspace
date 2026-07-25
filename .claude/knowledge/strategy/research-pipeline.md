# 研究管线

> 实验优先级矩阵 + 阻塞关系 + 状态追踪。每次 session 启动回答: "现在该做哪个实验？"

```yaml
pipeline:
  - id: blind-scoring
    claim: claim-8
    description: "P1-2 双人盲评分——解决论文最大方法学局限（无第二评分者 κ=0.00, zero-variance）"
    priority: 1
    impact: "论文实验严谨性 3→7/10；直接堵最弱环节"
    effort: "2-3h × 2人"
    blocks: [paper-submission]
    blocked_by: []
    status: not_started
    next_action: "找第二评分者 + 准备 30 条评分材料（从 P1-2 600 trials 抽样）"

  - id: cross-model-gpt
    claim: claim-9
    description: "跨模型扩展到 GPT-4o——验证 Gateability 二维框架"
    priority: 2
    impact: "3→4 models；Claim 9 generalizeability 强化"
    effort: "~100 API calls, ~2h coding"
    blocks: [cross-model-claude]
    blocked_by: []
    status: not_started
    next_action: "确认 GPT-4o API key 可用 + 读 api_client.py 适配点"

  - id: cross-model-claude
    claim: claim-9
    description: "跨模型扩展到 Claude——完成三模型覆盖"
    priority: 3
    impact: "DS+GPT+Claude→跨架构验证"
    effort: "~100 API calls, ~2h coding"
    blocks: []
    blocked_by: [cross-model-gpt]
    status: not_started

  - id: paper-draft-complete
    description: "完成论文五章完整草稿"
    priority: 4
    impact: "有完整稿件可投"
    effort: "~20h writing"
    blocks: [paper-submission]
    blocked_by: [blind-scoring]
    status: in_progress
    next_action: "§1 Introduction + §5 Discussion + §2 Related Work——非盲评分阻塞部分先起草"
    completed_sections: ["§3.2 L1-Visibility Analysis (Where Format Helps)"]
    section_status: "方法§ 写完了, 引言§ 未写, 讨论§ 未写, 相关工作§ 未写"

  - id: literature-positioning
    description: "系统化 Related Work——Governance/AI-Safety/Agent-Architecture 交叉点"
    priority: 5
    impact: "定位 2→6/10"
    effort: "~8h reading+writing"
    blocks: [paper-submission]
    blocked_by: []
    status: not_started
    next_action: "从 4 个交叉点收集 15-20 篇 key paper + 写对比矩阵"

  - id: github-strategy-execute
    description: "5 repos × ≥1 PR + ≥1 issue"
    priority: 6
    impact: "GitHub profile 0→有实质贡献"
    effort: "~10h"
    blocks: []
    blocked_by: []
    status: not_started

  - id: sart
    claim: claim-11
    description: "SART: Safety Attention Routing Tomography — 测量安全/情感 token 的 attention 路由作为安全训练诊断工具。3家族×3训练深度 token→layer→head routing map + habituation curve + causal ablation validation"
    priority: 5
    impact: "L2神经门细粒度扩展；安全训练解剖刀（非安全评估器）；可独立发表为 workshop/short paper"
    effort: "~2-3天（本地推理，$0成本），RTX 3060 6GB 可跑"
    blocks: []
    blocked_by: [paper-work-resumes]
    status: planned
    spec: "paper/experiments/sart-safety-attention-routing-tomography.md"
    gate_condition: "林宇浩恢复论文工作（开始更新 PAPER.md 或明确说'继续推进论文'）→ session 启动时提醒 SART 可以做"
    next_action: "等待论文工作恢复。arXiv 需要导师推荐才能发预印版，目前论文暂停中。"

critical_path: [blind-scoring → paper-draft-complete → paper-submission]
current_blocker: "盲评分未做——阻塞论文投稿（最大瓶颈）"
total_estimated_effort: "~50h"
```

## 优先级逻辑（三维加权）

1. **阻塞影响**（40%）：在 critical path 上？阻塞多少下游？
2. **边际收益**（35%）：做完后论文/量化指标改善多少？
3. **执行成本**（25%）：时间、金钱、依赖就绪？

双池专家团参与新增实验或重排优先级的评分。

---
*最后更新: 2026-07-19*
*交叉引用: [[../dashboard]] [[content-pipeline]] [[../paper/claims]]*
