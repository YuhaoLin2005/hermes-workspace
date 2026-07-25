# KB Schema v1.0 — L0 Format Standard

> 每个 KB 条目必须遵循此格式。L1 机械门据此验证。
> 设计原则: 固定字段名→LLM attention 精确路由; 一行一事实→不浪费 token 解析散文。

## 文章条目

```yaml
- slug: cross-model              # 唯一标识, kebab-case
  title: "..."                   # 原标题
  url: "..."                     # 完整 URL
  date: 2026-07-18               # ISO 8601
  tier: hot                      # hot|warm|cold
  domain: experiment             # experiment|platform|config|architecture|narrative|tutorial|personal
  claims: [claim-9]             # 关联论文声明 slug 列表, 无则 []
  commenters: [mike]            # 关联评论者 slug 列表, 无则 []
  numbers: "5/5→2/5; 100% hollow"  # 一行关键数字, 无则 ""
  finding: "Gateability = structure × capacity"  # 一行核心发现, 无则 ""
  status: active                 # active|superseded|historical
```

## 评论者条目

```yaml
- slug: mike-czerwinski
  name: "Mike Czerwinski"
  devto: "https://dev.to/jugeni"
  tier: hot
  articles: [cross-model, pre-reg, 150-tasks]
  role: "方法论质疑者+框架深化者"
  contributions:
    - "compliance=f(mechanizability)→两轴模型"
    - "hollow compliance命名"
  interests: "方法论严谨性、统计有效性"
  reply_principle: "尊重严谨, 用数据回答, 不模糊概括"
```

## 实验条目

```yaml
- slug: p1-1-ceiling
  name: "P1-1: Ceiling Effect"
  tier: hot
  script: "experiment_p1_1_residual_cluster.py"
  design: "5 task × 40 trials = 200 calls"
  numbers: "T1/T2=100%, T3=0%, T4=35%, T5=42.5%"
  claims: [claim-2]
  articles: [150-tasks, cross-model]
```

## 论文声明条目

```yaml
- slug: claim-1
  name: "Prose Barrier — 自验证是结构性约束"
  tier: hot
  statement: "LLM无法独立验证自身输出"
  numbers: "55.9%→0.7%; d=+0.578 BF=282k"
  articles: [self-verify, 150-tasks]
  limitations: "单模型、无第二评分者"
```

## 回复条目

```yaml
- article: cross-model              # 文章 slug
  commenter: mike                   # 评论者 slug
  thread: "two-axis-framing"       # 线程标识, kebab-case
  date: 2026-07-18                  # ISO 8601
  status: replied                  # unread|replied
  reply_summary: "核心回复内容摘要" # 20-40 字
  voice_checked: yes                # 过声音门: yes|no
```

## 分层规则 (L3)

| Tier | 条件 | 加载策略 |
|------|------|---------|
| **hot** | ≤14天 + 活跃评论者 + 支撑活跃声明 | 启动全量加载 |
| **warm** | ≤60天 + 有评论但非活跃 | 标题+finding, 按需全文 |
| **cold** | >60天或无评论无引用 | 仅搜索, 不进context |

**自动升降**: 新评论→升hot; hot超30天无评论→降warm; warm超90天→降cold

## 必填字段校验 (L1)

hot 条目必须通过:
- slug: 非空, kebab-case, 唯一
- title/name: 非空
- date: ISO 8601, hot <30天
- tier: hot|warm|cold
- domain: experiment|platform|config|architecture|narrative|tutorial|personal
- claims: 每个 slug 在 paper/claims.md 中存在
- status: active|superseded|historical
