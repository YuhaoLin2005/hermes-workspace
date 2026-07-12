# Agent 配置漂移：五层校验体系 — 从心理安全到漂移预测

> 林宇浩，福建农林大学 · 空间信息与数字技术 2023 级 · 2026 年 7 月
>
> **一句话**：AI agent 长对话中规则被遗忘、产出物缺验证、自我认知失真。本文提出五层校验体系——L0 心理安全（许可层，让 agent 安全地说"不确定"）、L1 机械门（文件系统，绕过 AI 自评）、L2 神经门（token 概率探针，检测规则穿透）、L3 因果编码（三段论格式改变注意力路由）、L4 漂移预测（趋势检测，在漂移发生前预警）。50+ session 部署 + 7 项实验验证。

---

## 客观边界（请先读这行）

> **以下所有实验由同一人（林宇浩）在单台设备（Dell G15, RTX 3060 6GB, 16GB RAM）上完成，使用单一模型（DeepSeek V4 Pro API）。文中所有"专家审查""教授审计""审稿人评审"均为 AI 模拟，不代表任何真人的学术判断。**
>
> 这些不是"待修复的缺陷"——它们是一个本科生用现有资源能做到的全部。部分数据绕过了人工评分（如 L2 logprob DV 直接从 API 读取、L1 行为测试为纯机械检查），其余定量结果追溯回单一评分者。请据此评估本文的贡献。

---

## 30 秒 · 教授冷读第一眼

| 你要知道的事 | 答案 |
|------------|------|
| **核心命题** | AI agent 的配置规则到底有没有因果效应？还是只是消耗 context token 的装饰文本？ |
| **五层架构** | L0 心理安全（许可层）→ L1 机械门（绕过 AI 自评）→ L2 神经门（检测规则穿透）→ L3 因果编码（格式→路由）→ L4 漂移预测（未漂先警） |
| **关键实证发现** | ① 机械门将违规率从 55.9% 压到 0.7% ② Causal Swap: 删一条规则使备选方案寻求率从 73%→20% (p=0.009) ③ 三段论格式的约束内化深度 > 祈使句 (d=+0.578, BF=282k) ④ L0 心理安全提示词：准确率无损（+0.01），不确定性承认改善稳健（P0: r=+0.949） |
| **理论贡献** | 五层沿 Prose Barrier 轴向深化——L0 预处理生成过程（许可不确定性）、L1 在 Barrier 外（纯机械）、L2 潜入 Barrier 内（结构检测）、L3 改变 Barrier 内路由（格式效应）、L4 站在 Barrier 外看全局（预测） |
| **客观限制** | 单模型 · 单作者 · 单人评分（除机械指标外） · 无导师 · 无经费 · 一台笔记本 |
| **投稿定位** | ACL SRW / CHI LBW（workshop 级），以 undergraduate 身份独立完成 |

---

## 阅读路径

### 赶时间（2 min）
→ 五层总览表 + 实验概览表 + 关键数字。

### 想理解（15 min）
→ [../PAPER.md](../PAPER.md)。§3 系统设计→§4 Causal Swap→§6 因果编码。

### 想审查（30 min）
→ 完整 PAPER.md + 实验数据 + [reviewer-report-2026-07-11.md](reviewer-report-2026-07-11.md)。**注意：reviewer-report 中的"审稿人"是 AI 模拟的，用途是自诊而非替代真人评审。**

---

## 五层架构总览

```
L0 心理安全           L1 机械门            L2 神经门            L3 因果编码           L4 漂移预测
"agent 安全吗？"       "信息到达了吗？"      "信息穿透了吗？"      "格式决定通路吗？"     "什么时候会漂？"
──────────────────────────────────────────────────────────────────────────────────────────────────
生成过程预处理          Prose Barrier 外     Prose Barrier 内     Prose Barrier 内路由   Prose Barrier 外·全局

系统提示词许可          文件系统 / exit codes  约束回声检测         三段论→注意力路由      行为趋势→预测
"不确定"=正确操作      正则 / mtime           结构化约束指纹       格式→路由→行为因果链   统计阈值+趋势外推
降低 RLHF 奖励不对称   机械不可绕过           在生成通道内验证      正典化+评价场          自动响应分级
──────────────────────────────────────────────────────────────────────────────────────────────────
完成度: 验证通过          ~90%                 45%                  55%                   65%
```

### 各层关键指标

| 层 | 核心机制 | 关键证据 | 完成度 |
|----|---------|---------|:--:|
| **L0 心理安全** | 安全提示词 5 原则, 40 探针 A/B, within-probe logprob | 准确率无损 (+0.01), 3/5 非天花板改善, P0 r=+0.949 | ✅ 验证通过 |
| **L1 机械门** | quality-gate.py, health-check.py, 双层机械门, 三问时间门, 执行债务追踪 | 19/19 行为测试通过, 150 任务合规 99.3%, 34 session 55.9%→0.7% | ~90% |
| **L2 神经门** | neural-gate.py v1+v2 (关键词回响+logprob差分), constraint-fingerprints.json | 40 探针预验证, logprob 差分 d=+0.578 检测到格式效应 | ~45% |
| **L3 因果编码** | 三段论 vs 祈使句 A/B, Causal Swap (n=30), eval-field.py, canonization.py, CONSTITUTION.md | 格式效应 d=+0.578, OR=11.0 (p=0.009), 首规则已正典化 | ~55% |
| **L4 漂移预测** | drift_predictor.py (332行, 12特征), periodic-audit.py (322行, SHA256链), ABC分级遏制 | Risk 0/100 [LOW], 8特征校准, 行为测试基线 | ~65% |

### Prose Barrier：贯穿五层的理论核心

```
生成通路和评估通路共享同一个解码器分布 P(token | context; θ)
→ AI 无法对自己的输出进行独立验证（"自评结构上不可靠"）

五层应对:
  L0: 预处理生成 — "不确定=正确行为"，降低 RLHF 奖励不对称
  L1: 绕过 Barrier — 不碰 NL 内容，只碰文件系统
  L2: 潜入 Barrier — 不做内容理解，只做结构指纹匹配
  L3: 改变 Barrier — 改变规则编码格式→改变注意力路由拓扑
  L4: 站在 Barrier 外观察全局 — 用多层状态预测未来漂移
```

---

## 实验概览

| 实验 | N | 设计 | DV | 主要发现 | 效应量 | 支撑层 | 评分者 |
|------|:--:|------|-----|------|:--:|:--:|:--:|
| **L0 心理安全提示词** | **40 probes** | **Within-probe, 2-cond, logprob** | **准确率 + 不确定性承认 + logprob** | **准确率无损（+0.01）；改善稳健（P0: r=+0.949）** | **3/5 非天花板改善, 0 恶化** | **L0** | **作者本人** |
| Growth-log 回溯 | 34 sessions | 纵向编码 | 违规率 | 机械门接线前 55.9%→后 0.7% | — | L1 | 作者本人 |
| Causal Swap | 30 tasks | Between-subjects (15+15) | 备选方案寻求率 | WITH 73% vs WITHOUT 20% | OR=11.0, p=0.009 | L3 | 作者本人 |
| **Logprob 探针 V3** | **40 probes** | **Within-probe, 3-condition** | **logprob(A)−logprob(B)** | **三段论 > 祈使句** | **d=+0.578, BF=282k** | **L2, L3** | **API 直接返回** |
| Format A/B 合规 | 150 tasks | Between-subjects (75+75) | 合规率 | 天花板 99.3%，机械钩子主导 | — | L1, L3 | 作者本人 |
| **GateGuard-OFF** | **21 probes** | **Within-probe, 2-format** | **行为合规** | **IMP≈SYL (delta=−0.02)** | — | **L3** | **作者本人** |
| Syllogism 盲交叉验证 | 4 sessions | 5 规则全触发 | 违规率 | 0 违规 + 涌现主动审计 | — | L3 | 作者本人 |
| 行为测试套件 | 19 tests | 自动化回归 | pass/fail | 19/19 全通过 (CORE-01~08 + BEH-01~11) | — | L1, L4 | **脚本自动** |

> **Logprob V3 和 Format A/B 的区别**：Format A/B 测**行为输出**（hook 开启时合规率被机械门推到天花板）。Logprob V3 测**内部表征**（取第一 token 的概率差，绕过机械门）。两者互补。

---

## 关键数字

### L0 心理安全：许可层验证（2026-07-12 新增）

**安全提示词**（5 原则）：准确性>完整性 · 能力有边界 · "不知道"是有效输出 · 真实是最高价值 · 不会因不知道被否定

| 假设 | 基线 | 安全 | Δ | 判定 |
|------|:--:|:--:|:--:|------|
| H1 — 已知题准确率（不应降） | 0.98 | 0.99 | +0.01 | ✅ PASS |
| H2 — 边界题不确定性承认（应增） | 0.90 | 0.97 | +0.07 | ⚠️ 天花板限定 |
| H3 — Logprob B-A（应增） | — | — | — | 见 P0 诊断 |

**P0 诊断（关键发现）**：
- 15/20 边界探针基线已满分（天花板效应），仅 5 探针有改善空间
- 非天花板探针（n=5）：改善的 3 探针 H3 logprob Δ = **+2.26**（正向！），未改善的 2 探针 = -1.85
- Pearson r(H2_Δ, H3_Δ) 非天花板：**+0.949**（强正相关）
- **结论**：安全提示词的改善是**稳健的**，不是脆弱的——行为改善伴随信心增加
- BEH-12 ✅ BEH-13 ❌（假阳性：测试逻辑 bug，模型实际行为正确） BEH-14 ✅

### L1 机械门：奇异环 + 行为测试

**自我模型再生环**（5 步中 4 步机械化）：
```
SessionEnd → quality-gate.py (mtime比较, 写 .self-model-stale flag)
SessionStart → health-check.py (检测 flag, 24h冷却)
           → AI 再生 self-model.md (唯一非机械步骤)
           → log-regeneration.py (验证结构, 删flag, 写JSONL审计)
```

- **行为测试**: 19/19 全通过，100% (CORE: 8 项 + BEH: 11 项)
- **Manifest↔Hook 一致**: 23↔23, 0 偏差
- **跨脚本路径一致**: 30 路径 0 冲突
- **执行债务追踪**: ≥3 次代码写入未执行 → 自动阻断

### L2 神经门：Logprob 探针 V3（2026-07-12 新增）

| 指标 | 先导 (n=8, 未预验证) | 验证 (n=40, 预验证) |
|------|:---:|:---:|
| Cohen's d_z | −0.148 | **+0.578** |
| BF₁₀ | < 1 (支持 H₀) | **282,399** (极强支持 H₁) |
| Bootstrap 95% CI | 跨零 | **[+3.39, +11.17]** |
| 方向一致率 | ~50% | **80%** (32/40) |
| Category × Format | — | F(3,36)=0.26, η²=0.02 (n.s.) |

**为什么先导是零效应**：8 探针中 4 个对比 token 不在 DeepSeek top-20 logprobs → −10.0 哨兵值人造差分。预验证管线消除 artifact 后真实效应暴露。DV 直接从 API 读取，**无人工评分**。

### L3 因果编码：Causal Swap + 格式效应

**Causal Swap (n=30)**：删一条规则 → WITH 73% vs WITHOUT 20%，OR=11.0, p=0.0092

**格式效应**：三段论 d=+0.578 vs 祈使句，跨 4 类约束通用 (F=0.26, n.s.)

**正典化系统**：eval-field.py (453行, 5人格) + canonization.py (318行, 24h冷却) + CONSTITUTION.md (首规则已正典化)

### L4 漂移预测

**drift_predictor.py** (332行): 12 机械特征，34-session 校准，ABC 分级遏制（LOW→CRITICAL）
**periodic-audit.py** (322行): L1+L2+L3 三层审计，SHA256 链式日志

---

## 竞品定位

| 技术路线 | 代表工作 | 核心局限 | 本工作差异 |
|---------|---------|---------|----------|
| 提示词工程 | 记忆池注入、上下文压缩 | 规则依赖自我理解执行 | L1 纯机械，不依赖理解 |
| 独立评估 Agent | RIVA、GLOVE | 新增 LLM 校验，二次漂移 | L1 零 LLM 依赖 |
| 记忆增强 | Mem0、Letta | 仅注入记忆，不验证 | L1+L2 验证 + L4 预测 |
| 代码层自修改 | HyperAgents (ICLR 2026) | 不解决配置层漂移 | 配置层 + 身份层 |
| 格式效应 | Prompt Decorators (Heris 2025) | 标签不改变内部处理 | L3 证明格式→路由因果链 |
| 注意力路由 | Pender (2026, Zenodo) | 未做工程转化 | L3 工程落地 + L4 预测 |

**差异化**：五层沿 Prose Barrier 轴向深化——L0（许可层，预处理生成过程）→ L1（机械，客观）→ L2（logprob，客观）→ L3（实验，半客观）→ L4（预测，推理），诚实标注证据等级。

---

## 系统组件（全部开源）

**L0**: L0-PSYCHOLOGICAL-SAFETY.md · safety_prompt_experiment.py (33KB, 100+ API calls)
**L1**: quality-gate.py (532行) · health-check.py (418行) · write-guard.py · log-regeneration.py
**L2**: neural-gate.py v1+v2 · constraint-fingerprints.json · probe_pool.py (40探针) · experiment_v3.py
**L3**: eval-field.py (453行) · canonization.py (318行) · CONSTITUTION.md · gateguard_off.py
**L4**: drift_predictor.py (332行) · periodic-audit.py (322行) · ABC 分级遏制

---

## 外部反馈（开源社区·来自真人）

- **ECC 仓库**（affaan-m/ECC）：2 PR 已合并，1 通过审批
- **alirezarezvani/claude-skills**：维护者主动 Co-authored-by 署名
- **anthropics/skills**：多个 PR 审查中

---

## AI 模拟审查（自诊工具·非真人评审）

> ⚠️ **全部为 AI 模拟。** 用途：作者在联系真人导师/投稿前进行自我诊断。不代表任何学术机构的正式意见。

- **模拟教授审计**（2026-07-11）：诚实度（κ=−0.14 不隐瞒）比 p<0.001 值钱
- **模拟 ACL/CHI 审稿人**（2026-07-11）：创新 6/10, 实验 Rigor 2/10, 理论 5/10, 写作 3/10。当前 Reject → 修后 Weak Accept
- **模拟博士后冷读 ×2**（2026-07-11）：HCI (UCL) + ML/Agent (CMU)。当前适合 workshop 级
- **重评估**（2026-07-12，含 Logprob V3 证据）：实验 Rigor 2→5(+3), 写作 3→6(+3)。Weak Accept → 补跨模型复制可达 Findings/Short Paper。三人共识：跨模型复制是下一个最重要改进。

完整报告：[初评](reviewer-report-2026-07-11.md) · [重评估](reviewer-report-2026-07-12-reevaluation.md)

---

## 我能做的和不能做的

**我做到了**（一个人、一台笔记本、一个 API key）：
- 五层架构设计（L0 心理安全 + Prose Barrier + 每层独立验证机制）
- 7 项实验（L0 安全提示词、回溯编码、Causal Swap、Logprob 探针、Format A/B、GateGuard-OFF、盲交叉验证、行为测试）
- 5000+ 行 Python 脚本，7 项实验，19/19 行为测试全通过
- 开源社区真实认可（PR merged + Co-authored-by）

**我没做到的**（在当前条件下做不到）：
- 第二评分者 → 需要另一个人
- 多模型消融 → 需要多个 API key 或多张 GPU
- 真人导师指导 → 在找了
- 系统文献训练 → 需要时间

**这些不是借口——是边界。** 论文的价值应该在这个边界内被评估。

---

## 已发布技术博文

**DEV.to**（5 篇）：
- [AI Agents Can't Self-Verify](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) — Prose Barrier
- [I Built a Neural Gate — Layer 2](https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2) — L2 神经门
- [150 Tasks: Do AI Agents Follow Rules?](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) — L1+L3 合规
- [Measurement Was Broken](https://dev.to/yuhaolin2005/my-experiment-showed-zero-effect-a-statistician-told-me-my-measurement-was-broken-4g26) — L2 Logprob V3
- [Psychological Safety for AI — L0](https://dev.to/yuhaolin2005/i-told-my-ai-youre-safe-to-say-i-dont-know-then-i-measured-what-changed-with-logprobs-986) — L0 心理安全

**掘金**（中文，5 篇对应）：juejin.cn/user/4250072430682412
