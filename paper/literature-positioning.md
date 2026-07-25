# Literature Positioning — Self-Evolving Agent Harness

> 对照矩阵：Prose Barrier 论文 vs 2026 清华自进化 Agent 研究线
> 生成: 2026-07-22 | 用途: PAPER.md §2 Related Work 素材

## 四个交叉点

| # | 领域 | 清华论文 | 我们 |
|:--:|------|---------|------|
| 1 | Agent Harness 形式化 | SEAGym A=(M,H), 88p综述 trace-to-capability | Prose Barrier + paper-validator 5层 |
| 2 | 自进化机制 | SEED(同策略蒸馏), EDV, GTR(防思维崩塌) | Strange Loop 6-phase + L3 EvalField |
| 3 | 评测框架 | SEAGym 6-view | paper-validator 8 claims + 12+ experiments |
| 4 | 跨模型泛化 | SEAGym: harness更新不对称 | Claim 9: Gateability=Structure×Capacity |



## 对照矩阵 1: 形式化 vs 工程化

| | SEAGym (Zheng et al., 2026) | Prose Barrier (Ours) |
|:---|:---|:---|
| 形式化 | A=(M,H), H_{t+1}=U(H_t) | P(token|context;θ)共享解码器→自验证结构不可靠 |
| 更新函数U | 程序化 | 混合: 4步机械+1步NL(AI再生) |
| 他们没讨论的 | — | Prose Barrier发现, Hollow Compliance, L2/L3 Dissociation, Constraint Gradient非单调 |

## 对照矩阵 2: 自进化机制

| | EDV | SEED | GTR | Strange Loop (Ours) |
|:---|:---|:---|:---|:---|
| 核心 | Execute→Distill→Verify | 事后技能SFT | 外部教师防思维崩塌 | detect→trigger→regenerate→validate→audit→clear |
| 防自确认 | 第三方Distill | — | — | 5-persona consensus+24h cooling |
| 失败利用 | — | 失败→纠正规则 | — | growth-log翻车(未编译⚠️) |
| 漂移检测 | — | — | — | L4 8特征 trending_up(n=3) |

## 对照矩阵 3: SEAGym 6-View 覆盖

| View | 我们 | 状态 |
|:---|:---|:---:|
| Update-validation | strange_loop.validate() | ✅ |
| ID Transfer | — | ❌ |
| OOD Transfer | Claim 6: d_z 0.58→0.19 | ⚠️ |
| Replay | 3版本轮转,无自动化 | ⚠️ |
| Cost | INTERFACE.md+heartbeat | ⚠️ |
| Safety non-regression | L4+L0,未验证预测性 | ⚠️ |

## 六个独特贡献 (competitor_differentiation 现为 3/10，上限空间 5/10)

| # | 贡献 | 证据 |
|:--:|------|------|
| 1 | **Prose Barrier形式化** — 首次将AI无法自验证表述为解码器结构必然推论 | Claim 1 |
| 2 | **L2/L3 Dissociation** — logprob效应≠行为效应 (d=+0.578 vs Δ=-0.024) | Claim 4 |
| 3 | **Hollow Compliance** — 命名并量化"格式合规零实质" | Claim 9 |
| 4 | **Constraint Gradient非单调** — L1>L3>L0>L2 | Claim 5 |
| 5 | **社区驱动验证闭环** — 学术论文罕见的复现→补充→更新 ⚠️ | 2026-07-19 Mike复现+Tom独立验证+Alice案例；强声称但未发表·需更多文献支撑 |
| 6 | **全栈工程实现** — L1→L4完整可运行代码,pip install | paper-validator |

## 待收集论文

- [ ] Weng Li — Harness Engineering for Self-Improvement (2026.07 blog)
- [ ] Anthropic — J-space self-referential representations
- [ ] Hofstadter — GEB (1979): Strange Loop概念源头


## 使用说明 (PAPER.md §2 集成)

| 论文章节 | 使用此文件的 | 操作 |
|:---|:---|:---|
| §2.1 Agent Harness 形式化 | 对照矩阵 1 | 直接引用 formality vs engineering 对比，强调 U 函数的混合性质 |
| §2.2 自进化机制 | 对照矩阵 2 | EDV/SEED/GTR → Strange Loop 对照；标注我们的防自确认机制 |
| §2.3 评测框架 | 对照矩阵 3 | SEAGym 6-view 覆盖表；诚实标注 ID Transfer ❌和 Replay ⚠️ |
| §2.4 跨模型泛化 | 交叉点 #4 | Gateability=Structure×Capacity 公式 + Claim 9 证据 |
| §5 Discussion | 六个独特贡献 | 按证据强度排序：#1-4 主论据·#5-6 补充论点 |

> ⚠️ 积分评估：competitor_differentiation 3/10(当前)→5/10(目标)取决于盲评分结果+贡献 #5/6 发表验证。
---
*交叉引用: [[claims]] [[structure]] [[dashboard]]*

## 2026.07 新增文献 — 高度交叉

> 搜索日期: 2026-07-22 | 8篇新论文与你的研究高重叠

### 对照矩阵 4: Prose Barrier vs 2026 Harness Dissociation

| | "Harness Updating Is Not Harness Benefit" (Lin et al., 2605.30621) | Prose Barrier (Ours) |
|:---|:---|:---|
| 核心分离 | harness-updating(产生更新) != harness-benefit(从更新获益) | P(token|context;theta)共享解码器 -> 自验证结构不可靠 |
| 发现 | harness-updating 跨模型平坦(<=3.1pp差); benefit 非单调 | Constraint Gradient: L1>L3>L0>L2 |
| 弱模型失败 | harness activation failure(25%加载率) + adherence failure(长期漂移) | Hollow Compliance: 格式合规零实质 |
| 设计指导 | 投资capability budget到task agent，非evolver | 投资机械门(确定性的L1)，非更多LLM约束 |
| 我们独有的 | — | L2/L3 Dissociation(logprob!=行为) + 解码器结构根基 + 跨模型Gateability公式 |

### 对照矩阵 5: Strange Loop vs 2026 Self-Evolution Loops

| | Self-Harness (Shanghai AI Lab) | RHI (Lee et al.) | Ratchet (Zhang et al.) | Strange Loop (Ours) |
|:---|:---|:---|:---|:---|
| 循环 | weakness mining->proposal->validate | harness as prompt spec, pairwise feedback refine | write->retrieve->curate->retire | detect->trigger->regenerate->validate->audit->clear |
| 防退化 | 回归测试(on held-out) | pairwise diff over revision history | bounded cap + retirement threshold(形式化非散度证明) | L4 8特征 trending_up(n=3) WARNING 无rollback |
| 独特贡献 | — | 成本降60% | formal non-divergence proof | 5-persona consensus + 24h cooling + 5层全栈 |
| 我们可借鉴 | WARNING regression testing on held-out | WARNING pairwise diff computation | WARNING formal non-divergence for L4 | — |

### 对照矩阵 6: Hollow Compliance vs 2026 Silent Failure

| | "Library Drift" (Zhang et al., 2605.19576) | "Don't Blame the LLM" (Ben Sghaier et al., 2607.03691) | Hollow Compliance (Ours) |
|:---|:---|:---|:---|
| 失败模式 | 3阶段: accumulation->retrieval degradation->silent injection harm | hyper-churn(10-18 releases/week) + token inflation无质量提升 | 格式合规零实质 |
| LLM产出质量 | LLM-authored skills +0.0pp; human-curated +16.2pp | harness development无统计显著提升 | Prose Barrier: AI自验证 55.9%->0.7% vs 机械门 |
| 根因 | 无quality signal的积累->近重复检索稀释->隐性注入伤害 | LLM Provider layer + Context Management = 高风险回归组件 | P(token|context;theta)共享解码器结构必然推论 |
| 我们独有的 | — | — | 解码器结构根基(非经验观察) + L1机械门为第一防线 |

### 对照矩阵 7: Rule Compilation (针对我们的"翻车未编译"缺口)

| | Accumulated Behavioral Rules | Mistake Notebook Learning | AgentTrust v2 | Ours (缺口) |
|:---|:---|:---|:---|:---|
| 规则来源 | 人类review comments -> .rules文件 | batch-clustered failures -> mistake notes | LLM judge -> deterministic rules(lexical) + RAG(semantic) | growth-log翻车 WARNING 仅记录不编译 |
| 效果 | 0% recurrence for ruled-against errors | 测试时缩放引导搜索避开已知陷阱 | judge-call rate 50%->44% | — |
| 我们缺什么 | version-controlled .rules file | batch-clustered abstraction | lexical/semantic分离 | 整个编译步骤 |

### 五个新洞察

| # | 洞察 | 对你的意义 |
|---|------|-----------|
| 1 | Harness-updating全校准但benefit非单调 — Lin et al.独立发现类似Constraint Gradient | L1>L3>L0>L2是独立验证！可引用为convergent evidence |
| 2 | Library Drift = Hollow Compliance的系统级版本 — 3阶段退化模型可形式化机制 | 考虑用3-stage model扩展Claim 3 |
| 3 | Ratchet的形式化非散度证明 — L4 drift predictor没有这个 | 最大理论升级机会：给L4加形式化保证 |
| 4 | Self-Harness的held-out回归测试 — strange_loop.validate()没有这个 | 填补"无rollback"的最直接方案 |
| 5 | Accumulated Behavioral Rules的0%复发率 — growth-log仅记录不编译 | 填补"失败->规则"缺口的最直接模板 |

### 可行动借鉴 (按优先级)

| 优先级 | 借鉴 | 实现位置 | 难度 |
|:---:|------|------|:---:|
| P0 | regression testing on held-out (Self-Harness) | strange_loop.py validate() | 中 |
| P0 | formal non-divergence proof (Ratchet) | l4_drift_predictor.py | 高 |
| P1 | version-controlled .rules file (Accumulated Rules) | 新建 failure->rule 编译层 | 中 |
| P1 | batch-clustered failure abstraction (Mistake Notebook) | growth-log -> 结构化 | 低 |
| P2 | pairwise diff computation (RHI) | strange_loop.py regenerate() | 低 |
| P2 | lexical/semantic rule separation (AgentTrust) | l1_gates.py | 中 |

