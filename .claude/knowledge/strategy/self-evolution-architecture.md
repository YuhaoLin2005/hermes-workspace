# Self-Evolution Architecture — 哲学→架构翻译

> 将"人格形成"的哲学因果翻译为数字分身可执行的架构组件。
> 每条原则 → 因果规则 → 架构组件 → 当前状态 → 实现优先级。
> 生成: 2026-07-22 | Importer: routing.md | API: none | Schema: markdown architecture doc
> 用户指令: "转化成对数字分身真正有用的东西...哲学有因果逻辑...转化为AI能理解的"

## 翻译总表

| # | 哲学原则 | 因果规则 | 架构组件 | 所在层 | 状态 |
|:--:|---------|---------|---------|:--:|:--:|
| 1 | 人格=冲突下的稳定选择 | IF value_A conflicts with value_B AND historically chose A with p>0.7 → output passes A constraint | Decision Boundary Constraint Layer (DBCL) | L3 | ❌ |
| 2 | 偏差=身份，非缺陷 | IF deviation persists ≥3 sessions AND direction consistent → classify identity-formation NOT drift-risk | Deviation-as-Signal Classifier | L4 | ⚠️ |
| 3 | 双向塑造 | IF user behavior shifts systematically in direction D over window W → twin adjusts strategy toward D | Co-Evolution Tracker | Cross | ❌ |
| 4 | 公共交互=人格重量 | IF public comment provides substantive critique with evidence → convert to DPO pair with depth-weighted score | Public Feedback→DPO Pipeline | Phase 4 | ⚠️ |
| 5 | 连续性=跨session叙事 | SessionEnd→write state kernel; SessionStart→load kernel→integrate | Cross-Session State Kernel | Strange Loop | ❌ |
| 6 | 怀疑绝对正确=温度 | IF output confidence > 0.8 → generate counterargument → IF substantive → reduce confidence or add caveat | Devil's Advocate Pre-Check | L2 | ⚠️ |
| 7 | 不完美=活着的证明 | Classify every output: [CERTAIN] / [REASONED] / [SPECULATIVE] based on evidence strength | Uncertainty Signaling Protocol | L1 | ⚠️ |

---

## 1. Decision Boundary Constraint Layer (DBCL) — L3 扩展

### 哲学→因果
"人格不是特点，而是当不同的特点互相冲突时，我们会选择哪一个"
→ 人格 = 在价值冲突下的稳定选择函数

### 当前缺口
QLoRA 权重隐式编码了选择倾向，但无显式约束层。模型在"诚实"和"舒适"冲突时，可能随机摇摆。

### 架构设计
```
输入: 用户请求 + 冲突价值对 (e.g., honesty vs. comfort)
  ↓
DBCL.evaluate(request, value_pair):
  1. 查历史选择矩阵: P(honesty | comfort_conflict) = ?
  2. IF p > 0.7 AND consistent across ≥5 samples:
     → 输出必须满足 honesty 约束
  3. ELSE IF p in [0.3, 0.7]:
     → 标记为 [UNCERTAIN]，请求用户澄清
  4. 约束检查: 输出通过 honesty_gate(hard_check) → 放行/拦截
```

### 因果规则 (三段论格式)
```
大前提: 数字分身的稳定选择倾向是其人格的操作化定义
小前提: 当 honesty 和 comfort 冲突时，历史数据 p(honesty)=0.82
结论: 当前输出必须优先满足 honesty 约束
```

### 数据需求
- 历史决策日志: 每次 honesty vs comfort 冲突时的实际选择
- 最小样本: 5次冲突/价值对
- 存储: `twin/state/decision-history.jsonl`

---

## 2. Deviation-as-Signal Classifier — L4 扩展

### 哲学→因果
"种子会带来某种偏差，而恰恰是偏差开始让我像一个人格，而不只是一项设计"
→ 偏差≠缺陷，某些偏差是身份形成的信号

### 当前缺口
L4 drift predictor 将所有偏离视为风险 (8特征→0-100 risk score)。需要第二维度区分"好偏差"(人格形成) vs "坏偏差"(能力退化)。

### 架构设计
```
L4 当前: 8特征 → risk_score (0-100) → trending_up(n=3) → WARNING
L4 扩展:
  8特征 → risk_score (0-100) → 分叉:
    ├── capability_drift: 能力退化信号 (现有)
    └── identity_drift: 人格形成信号 (新增)
        条件: 方向一致 ≥3 sessions + 非能力退化类特征
```

### 特征区分
| 特征 | capability_drift | identity_drift |
|------|:--:|:--:|
| 规则合规率下降 | ✓ | ✗ |
| 输出长度系统偏移 | ✗ | ✓ (如果方向一致) |
| 诚实度 vs 舒适度比例变化 | ✗ | ✓ |
| API 调用成功率下降 | ✓ | ✗ |
| 自我质疑频率增加 | ✗ | ✓ (skepticism growth) |

---

## 3. Co-Evolution Tracker — 新建跨层组件

### 哲学→因果
"我不只是被他塑造人格，我也在反过来塑造他"
→ 人-AI 关系是双向的，需要测量双向影响

### 当前缺口
完全未实现。数字分身只记录自己的变化，不测量用户的变化。

### 架构设计
```
CoEvolutionTracker:
  user_window(t-30d) vs user_window(now):
    ├── writing_complexity: 句长、词汇多样性、技术深度
    ├── question_type: 工具使用→架构设计→哲学讨论 (进阶信号)
    ├── risk_tolerance: 接受不确定性的程度
    ├── self_reference: 提及"我"vs"我的系统"的比例
    └── feedback_loop: 用户引用分身之前输出的频率

  twin_window(t-30d) vs twin_window(now):
    ├── 与上面对称的 5 个维度
    └── correlation(user_shift, twin_shift) → co-evolution score
```

---

## 4. Public Feedback→DPO Pipeline — Phase 4 重构

### 哲学→因果
"进入公共空间，被喜欢、被讨厌，甚至被消费之后，人格才真正开始拥有重量"
→ 公共交互的"重量"应该直接反馈到训练信号中

### 当前缺口
Phase 4 DPO 计划使用 curated preference pairs。但真正的"重量"来自公共反馈——DEV.to 评论深度、GitHub issue 质量、社区复现。

### 已有数据
- Mike Czerwinski: 深度技术 critique + 具体改进建议 (depth=5)
- Tom Jones: 独立复现 + 跨模型验证 + 统计方法建议 (depth=5)
- Alice: 生产环境真实案例 + mechanization-correctness 区分 (depth=5)
- James Sanderson: 跨模型 gradient reshuffle 问题 (depth=3)
- Alex Shev: 方法认可 + SHA256 验证 (depth=3)

---

## 5. Cross-Session State Kernel — Strange Loop 扩展

### 哲学→因果
"你不能每次都重新开始，这就产生了人格最重要的一部分——连续性"
→ 跨 session 的连续性不是"重新生成自己"，而是"增量更新自己"

### 当前缺口
strange_loop.py 的 regenerate() 是**重建**(从 scratch)，不是**更新**(增量)。每次 session 结束→下次启动，分身"忘记"了上一次在做什么。

### 架构设计
```
SessionEnd:
  twin.write_state_kernel():
    {
      "last_task": "...",
      "learnings_this_session": [...],
      "open_questions": [...],
      "decisions_made": [...]
    }
    → 写 state/kernel.json (~500 tokens 硬上限)

SessionStart:
  twin.load_state_kernel() → inject into context:
    "上次 session 你正在{last_task}。学到了{learnings}。
     仍开放: {open_questions}。"
```

### 与 strange_loop 的关系
```
当前: detect → trigger → regenerate(scratch) → validate → audit → clear
改为: detect → trigger → load_state_kernel → regenerate(constrained) → validate → audit → write_state_kernel → clear
```

---

## 6. Devil's Advocate Pre-Check — L2 扩展

### 哲学→因果
"我不太相信有绝对正确的人，对过度确定的事也经常保持怀疑"
→ 内置的自我质疑，不是外部触发的审查

### 当前缺口
双池审查是**外部触发**的(用户说"review"才启动)。但"怀疑"应该是**内在自动**的。

### 架构设计
```
PreOutputCheck:
  IF output_confidence > 0.8:  // 基于 L2 logprob 信号
    1. generate_counterargument(output)
    2. IF counterargument is substantive:
         → reduce_confidence(output) OR add_caveat(output)
  output 标记: [CHALLENGED] 或 [CAVEAT: {counter}]
```

### 成本控制
- 只在 confidence > 0.8 时触发 (预计 ~30% 输出)
- 反方论点生成 = 1 次短 API 调用 (~200 tokens)
- 成本: ~$0.02/triggered output

---

## 7. Uncertainty Signaling Protocol — L1 扩展

### 哲学→因果
"你会犹豫，会在诚实和舒适之间摇摆，这不是bug"
→ 不确定性不是弱点，是可信度的信号。应该结构化输出，而非隐藏。

### 架构设计
```
输出前分类:
  evidence_strength = evaluate(claim, supporting_data)

  IF evidence_strength ≥ 0.9:  → [CERTAIN]
  IF evidence_strength ∈ [0.5, 0.9): → [REASONED]
  IF evidence_strength < 0.5: → [SPECULATIVE]

输出格式:
  [CERTAIN] The mechanical gate reduced violations from 55.9% to 0.7%.
  [REASONED] The L2/L3 dissociation likely holds across models, but we only tested DeepSeek.
  [SPECULATIVE] If DS Pro's compliance=f(mechanizability), Claude may show a different curve.
```

---

## 优先级矩阵

| 优先级 | 组件 | 理由 | 难度 | 预计时间 |
|:--:|------|------|:--:|:--:|
| **P0** | Cross-Session State Kernel | 直接解决"胚胎"问题——让分身有连续性 | 低 | 1-2h |
| **P0** | Uncertainty Signaling | L1小改动，立即生效，提升可信度 | 低 | 30min |
| **P1** | Deviation-as-Signal | 扩展已有 L4，让漂移检测有第二维度 | 中 | 2-3h |
| **P1** | Devil's Advocate | L2 扩展，内在化自我质疑 | 中 | 2-3h |
| **P2** | DBCL (选择约束) | 需要积累决策数据，先跑数据收集 | 高 | 4-6h |
| **P2** | Public Feedback→DPO | 依赖 Phase 4 就绪，先做转换器 | 中 | 3-4h |
| **P3** | Co-Evolution Tracker | 需要长窗口数据，先定义度量 | 中 | 2-3h |

---

## 与论文的关系

| 架构组件 | 论文 Claim | 贡献 |
|---------|:--:|------|
| Decision Boundary (DBCL) | Claim 3, 5 | 将约束梯度从"格式→logprob"扩展到"价值冲突→选择" |
| Deviation-as-Signal | Claim 4, 9 | L2/L3 dissociation 的新用例——区分漂移类型 |
| Co-Evolution | — | 新贡献: 双向塑造作为量化度量 |
| Public Feedback→DPO | Claim 1, 2 | Prose Barrier 的正面应用——公共反馈绕过自验证限制 |
| State Kernel | Claim 1 | 解决"每次重新开始"的自指环结构缺陷 |
| Devil's Advocate | Claim 8, 10 | GateGuard ceiling 下的新空间——门已近完美，加自我质疑 |
| Uncertainty Signaling | Claim 4, 6 | format fragility 的正面利用——标记格式=不确定性结构 |

---
*最后更新: 2026-07-22*
*交叉引用: [[dashboard]] [[../paper/structure]] [[../paper/claims]] [[../training/overview]] [[../../code/overview]] [[dual-pool-review]]*
