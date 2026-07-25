# 内容管线

> 实验→文章→评论→实验 闭环。双池在设计阶段参与角度评审。

```yaml
content_queue:
  - slug: blind-scoring-article
    trigger: "blind-scoring 实验完成后"
    platform: devto
    angle_candidates:
      - "我们找了第二个人来评分——盲评结果证明/推翻了什么"
      - "为什么论文最薄弱的一环是'只有一个人评的'——怎么修的"
    claims: [claim-8]
    priority: 1
    status: waiting_for_experiment
    depends_on:
      experiment: blind-scoring          # research-pipeline.md id
      claim: claim-8                      # claims.md slug
    dual_pool_design: [Jobs, Traynor, Cagan]  # 角度评审

  - slug: gateability-framework
    trigger: "cross-model-gpt + cross-model-claude 完成后"
    platform: devto
    angle_candidates:
      - "Gateability 二维框架：三个模型验证后的完整故事"
      - "不同模型对同一个规则的反应完全不同——这意味着什么"
    claims: [claim-9]
    priority: 2
    status: waiting_for_experiment
    depends_on:
      experiment: cross-model-gpt        # research-pipeline.md id
      claim: claim-9                      # claims.md slug
    dual_pool_design: [Wardley, Carmack, Jobs]

  - slug: paper-journey
    trigger: "论文投稿后"
    platform: devto
    angle_candidates:
      - "从 0 到投稿：一个本科生怎么用 AI 自指环做研究"
      - "我投稿了——这 3 个月里学到的 5 件事"
    claims: [claim-1, claim-2, claim-3]
    priority: 3
    status: waiting_for_event
    depends_on:
      milestone: paper-submission         # future event, not yet in research-pipeline
    dual_pool_design: [Schell, Jobs, Cagan]

  - slug: juejin-mirror
    trigger: "每篇 DEV.to 发布后 3-5 天"
    platform: juejin
    priority: 4
    status: recurring
    note: "中文改编——不同平台不同声音。掘金加更多技术细节，DEV.to 重叙事"
```

## 触发规则

| 事件 | 动作 |
|------|------|
| 实验完成 → claims.md 更新 | `_check_kb.py` 检测新数据 → content_queue 中 depends_on 满足 → 提醒"有新数据，建议写 [slug]" |
| 新评论提到新问题 | 评估是否值得写文章 → 加队列 或 设计实验 |
| 论文投稿 | paper-journey 从 waiting → ready |

## 双池角度评审流程

动笔前（不是写完审，是写前设计）：
1. Jobs 审角度："这个题目读者在乎吗？核心问题是什么？"
2. Traynor 审开头："前 30 秒能抓住人吗？hook 是什么？"
3. Cagan 审问题焦点："核心问题是真问题吗？还是换个说法？"
4. 输出：2-3 个选题角度 + 每个角度的 hook → 用户选

---
*最后更新: 2026-07-24*
*交叉引用: [[../dashboard]] [[research-pipeline]] [[../devto/hot]]*
