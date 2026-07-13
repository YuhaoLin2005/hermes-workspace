# Agent 配置漂移：五层校验体系 — 从心理安全到漂移预测

> 林宇浩，福建农林大学 · 空间信息与数字技术 2023 级 · 2026 年 7 月
>
> **一句话**：AI agent 长对话中规则被遗忘、产出物缺验证、自我认知失真。本文提出五层校验体系——L0 心理安全（许可层，让 agent 安全地说"不确定"）、L1 机械门（文件系统，绕过 AI 自评）、L2 神经门（token 概率探针，检测规则穿透）、L3 因果编码（三段论格式改变注意力路由）、L4 漂移预测（趋势检测，在漂移发生前预警）。50+ session 部署 + 11 项实验验证。

---

## 客观边界（请先读这行）

> **以下所有实验由同一人（林宇浩）在单台设备（Dell G15, RTX 3060 6GB, 16GB RAM）上完成，主要使用 DeepSeek V4 Pro API。跨模型行为复制已扩展至 Qwen3-8B (Dense) 和 GLM-4-9B (GLM)（§6.13）。文中所有"教授审计""审稿人评审"均为 AI 模拟，不代表任何真人的学术判断。**
>
> 这些不是"待修复的缺陷"——它们是一个本科生用现有资源能做到的全部。部分数据绕过了人工评分（如 L2 logprob DV 直接从 API 读取、L1 行为测试为纯机械检查、跨模型行为观察从 API 直接读取），其余定量结果追溯回单一评分者。请据此评估本文的贡献。

---

## 30 秒 · 教授冷读第一眼

| 你要知道的事 | 答案 |
|------------|------|
| **核心命题** | AI agent 的配置规则到底有没有因果效应？还是只是消耗 context token 的装饰文本？ |
| **五层架构** | L0 心理安全（许可层）→ L1 机械门（绕过 AI 自评）→ L2 神经门（检测规则穿透）→ L3 因果编码（格式→路由）→ L4 漂移预测（未漂先警） |
| **关键实证发现** | ① 机械门将违规率从 55.9% 压到 0.7% ② Causal Swap: 删一条规则使备选方案寻求率从 73%→20% (OR=11.0, 95% CI [2.0, 60.6], p=0.009, 单人评分) ③ 三段论格式的约束内化深度 > 祈使句 (d=+0.578, BF=282k, API读取DV) ④ L0 心理安全提示词：准确率无损（+0.01），不确定性承认改善（n=5非天花板探针 r=+0.949）⑤ L2/L3 分离跨三架构一致 ⑥ 约束梯度非单调：三段论效益遵循三阶段（优化→压制→反弹），L1最优(d_z=0.596)，8B/9B模型上未检测到 |
| **理论贡献** | 五层沿 Prose Barrier 轴向深化——L0 预处理生成过程（许可不确定性）、L1 在 Barrier 外（纯机械）、L2 潜入 Barrier 内（结构检测）、L3 改变 Barrier 内路由（格式效应）、L4 站在 Barrier 外看全局（预测） |
| **客观限制** | 单作者 · 单人评分（L2/跨模型除外） · L2 logprob 仅 DeepSeek · 无导师 · 无经费 · 一台笔记本 |
| **投稿定位** | Workshop 强投稿（ACL SRW / CHI LBW / NeurIPS R0-FoMo）；补盲法评分+结构重组可达 Findings/Short Paper；顶会长文需独立复制+导师指导 |

---

## 阅读路径

### 赶时间（2 min）
→ 五层总览表 + 实验概览表 + 关键数字。

### 想理解（15 min）
→ [../PAPER.md](../PAPER.md)。§3 系统设计→§4 Causal Swap→§6 因果编码。全文约 12,000 词，建议留 30-45 min。

### 想审查（30 min）
→ 完整 PAPER.md + 实验数据 + [reviewer-report-2026-07-11.md](reviewer-report-2026-07-11.md)。**注意：reviewer-report 中的"审稿人"是 AI 模拟的，用途是自诊而非替代真人评审。**

### 想深入（45 min）
→ 以上全部 + [supplementary/](supplementary/) 补充分析（logprob↔behavior 桥接、NO RULES 基线完整分析、五层独立性论证、P1社区驱动验证实验）。

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

> **五层划分依据**：Prose Barrier 定义了三种空间位置（外/内/预处理）× 两种时间方向（当前快照/未来预测）。L0 预处理生成、L1 在 Barrier 外（文件系统）、L2 在 Barrier 内（token 概率）、L3 改变 Barrier 内路由（格式）、L4 在 Barrier 外看时间轴（趋势）。如果不用 Barrier 轴线，按功能分 3 层或 7 层都是任意的——五层不是启发式，是结构约束的推论。

### 各层关键指标

| 层 | 核心机制 | 关键证据 | 完成度 |
|----|---------|---------|:--:|
| **L0 心理安全** | 安全提示词 5 原则, 40 探针 A/B, within-probe logprob | 准确率无损 (+0.01), 3/5 非天花板改善, P0 r=+0.949 | ✅ 验证通过 |
| **L1 机械门** | quality-gate.py, health-check.py, 双层机械门, 三问时间门, 执行债务追踪 | 19/19 行为测试通过, 150 任务合规 99.3%, 34 session 55.9%→0.7% | ~90% |
| **L2 神经门** | neural-gate.py v1+v2 (关键词回响+logprob差分), constraint-fingerprints.json | 40 探针预验证, logprob 差分 d=+0.578 检测到格式效应 | ~45% |
| **L3 因果编码** | 三段论 vs 祈使句 A/B, Causal Swap (n=30), 约束梯度 (96 calls), 跨模型约束梯度 (192 calls) | 格式效应 d=+0.578, OR=11.0 (p=0.009), 三阶段模型 (优化→压制→反弹), 跨模型行为零效应(行为测量+天花板限定) | ~60% |
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
| **L0 心理安全提示词** | **40 probes** | **Within-probe, 2-cond, logprob** | **准确率 + 不确定性承认 + logprob** | **准确率无损（+0.01）；改善正向（n=5非天花板 r=+0.949 [0.57,0.996]）** | **3/5 非天花板改善, 0 恶化** | **L0** | **作者本人** |
| Growth-log 回溯 | 34 sessions | 纵向编码 | 违规率 | 机械门接线前 55.9%→后 0.7% | — | L1 | 作者本人 |
| Causal Swap | 30 tasks | 交替分配 (15+15), 非随机 | 备选方案寻求率 | WITH 73% vs WITHOUT 20%（单人评分, 非盲法） | OR=11.0, 95% CI [2.0, 60.6], p≈0.009 | L3 | 作者本人 |
| **Logprob 探针 V3** | **40 probes** | **Within-probe, 3-condition, 预验证** | **logprob(A)−logprob(B)** | **三段论 > 祈使句** | **d=+0.578, BF=282k, 95% CI [+3.39,+11.17]** | **L2, L3** | **API 直接返回** |
| Format A/B 合规 | 150 tasks | Between-subjects (75+75) | 合规率 | 天花板 99.3%，机械钩子主导 | — | L1, L3 | 作者本人 |
| **GateGuard-OFF** | **21 probes × 3 cond** | **Within-probe, 3-condition (NO RULES / IMP / SYL)** | **行为合规** | **规则有效 (+0.38 above NO RULES baseline 0.48); IMP≈SYL (Δ=−0.02, d<0.65 不可检测)** | — | **L3** | **作者本人** |
| **跨模型行为复制** | **12 probes × 3 cond × 3 models** | **3 模型 (DSv4 MoE + Qwen3-8B Dense + GLM-4-9B)** | **行为合规** | **SYL−IMP all ≤ \|0.025\| across 3 architectures; Qwen/GLM near ceiling; BF₀₁=2.7 (pooled)** | — | **L3** | **API 观察** |
| **约束梯度** | **12 probes × 2 formats × 4 levels (96 calls)** | **4 输出约束级别 (L0~L3), DeepSeek V4 Pro** | **logprob d_z** | **非单调: L1(0.596)>L3(0.297)>L0(0.315)>L2(0.091); 三阶段模型** | — | **L3** | **API 直接返回** |
| **约束梯度-跨模型** | **12p×4L×2fmt×2M (192 calls)** | **Qwen3-8B + GLM-4-9B via SiliconFlow** | **行为合规** | **8B/9B 未检测到格式效应 (GLM d_z=0); 受行为测量+天花板限制, 非确定性结论** | — | **L3** | **API 观察** |
| Syllogism 盲交叉验证 | 4 sessions | 5 规则全触发 | 违规率 | 0 违规 + 涌现主动审计 | — | L3 | 作者本人 |
| **P1-1 残差聚类** (§6.16) | **200 trials** | **5 task types × 40 trials, pre-registered, regex scoring** | **违规分类 (机械/语义)** | **L1 100%合规 0违规; L1/L2边界 100%语义违规; L2/L3 违规聚集于gate盲区** | — | **L1, L3** | **脚本自动** |
| **P1-2 格式×Gate** (§6.16) | **240 trials** | **2×2 factorial (format × gate), pre-registered, regex scoring** | **机械合规 + 推理深度** | **H1未证实 (d_ON=-0.277≈d_OFF=-0.250); Prose格式推理始终优于Code; Code+Gate="checklist mentality"** | — | **L1, L3** | **脚本自动** |
| 行为测试套件 | 19 tests | 自动化回归 | pass/fail | 19/19 全通过 (CORE-01~08 + BEH-01~11) | — | L1, L4 | **脚本自动** |

> **Logprob V3 和 Format A/B 的区别**：Format A/B 测**行为输出**（hook 开启时合规率被机械门推到天花板）。Logprob V3 测**内部表征**（取第一 token 的概率差，绕过机械门）。两者互补。
>
> **Logprob 先导 d=−0.148 → V3 d=+0.578 不是 p-hacking。** 先导 8 探针中 4 个 token 不在 DeepSeek top-20 → −10.0 哨兵值制造噪声。V3 是修复测量工具后的新实验：probe_validator.py 机械过滤 + 探针格式统一 + 预注册 confirmatory 设计。这是"测量工具从坏变好"，不是同一样本量游戏。

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
- Pearson r(H2_Δ, H3_Δ) 非天花板：**+0.949**，95% CI **[0.57, 0.996]**（n=5，事后选择 delta>0 子集，CI 宽——兼容中等至强正相关）
- **结论**：安全提示词的改善呈正向趋势，行为改善伴随信心增加。n=5 限制结论强度，需更大样本验证
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
- **P1-1 残差聚类** (n=200, 2026-07-13): 验证 Mike Czerwinski 的追问——可机械化任务 100%合规零违规；L1/L2 边界 100%语义违规（gate 检测格式但检测不了内容）；不可机械化任务 57%语义违规。**违规聚集在 gate 无法检测的语义空间。**
- **设计哲学**: L1 使用 Shell 脚本、文件 mtime、exit code 是**刻意设计**——Prose Barrier 的推论是任何经过 NL 通道的检查都不可靠，因此 L1 只用 AI 够不着的底层机制。当前实现仅适用于单机（非 K8s/分布式），扩展需要状态持久化层，这是工程化工作而非架构缺陷。

### L2 神经门：Logprob 探针 V3（2026-07-12 新增）

| 指标 | 先导 (n=8, 未预验证) | 验证 (n=40, 预验证) |
|------|:---:|:---:|
| Cohen's d_z | −0.148 | **+0.578** |
| BF₁₀ | < 1 (支持 H₀) | **282,399** (极强支持 H₁) |
| Bootstrap 95% CI | 跨零 | **[+3.39, +11.17]** |
| 方向一致率 | ~50% | **80%** (32/40) |
| Category × Format | — | F(3,36)=0.26, η²=0.02 (n.s.) |

**为什么先导是零效应**：8 探针中 4 个对比 token 不在 DeepSeek top-20 logprobs → −10.0 哨兵值人造差分。预验证管线消除 artifact 后真实效应暴露。DV 直接从 API 读取，**无人工评分**。

### L3 因果编码：Causal Swap + 格式效应 + 约束梯度

**Causal Swap (n=30)**：删一条规则 → WITH 73% vs WITHOUT 20%，OR=11.0, 95% CI [2.0, 60.6], p≈0.009。⚠️ 交替分配非随机（Fisher 检验假设被违反，p 值为近似），单人评分非盲法

**格式效应**：三段论内部表征深度 > 祈使句 (d=+0.578, BF=282k, API 读取 DV)。但行为合规层面 IMP≈SYL（Δ=−0.02）——格式影响内部处理，不影响行为输出。跨三架构（MoE/Dense/GLM）一致：SYL−IMP ≤ |0.025|。

**P1 多场景弹性**（§6.15）：格式效应在多场景提示词下崩溃（d_z 0.58→0.19），控制实验确定元指令（"只输出A或B"）是 ~80% 主因——Prose Barrier of Measurement：测量工具抑制了被测量的机制。

**约束梯度**（96 calls, §6.15）：4 级输出约束（L0: 无 / L1: 仅输出AB / L2: 不要解释 / L3: 禁止任何非AB字符）。**非单调模式**：d_z L1(0.596) > L3(0.297) > L0(0.315) > L2(0.091)。三阶段模型：优化→压制→反弹。L1-visibility 模式从 synergy→compensation 转变，与 P1 多场景独立收敛。

**跨模型约束梯度**（192 calls, Qwen3-8B + GLM-4-9B）：**8B/9B 模型上未检测到格式效益**（GLM d_z=0 全级别，但受行为测量和天花板效应限制）。提示处理深度梯度，但 logprob 级跨模型验证仍待 API 支持。

**L3 升级**：`格式效应 = f(因果链长度, 处理阶段)` where 阶段 ∈ {优化, 压制, 反弹}。边界条件：处理深度（认知负载 + 输出约束） + 模型容量。

**P1-2 格式×GateGuard 交互** (n=240, 2026-07-13): 2×2 因子实验（格式 code/prose × GateGuard on/off）。H1（格式效应在 GateGuard-OFF 下更大）未证实——效应在两种条件下几乎相同 (d_ON=-0.277 ≈ d_OFF=-0.250)。**反直觉发现**: Prose 格式规则在所有条件下都比 code 格式产生更深推理 (~0.25 SD 恒定优势)。Code+GateGuard ON = "checklist mentality"（机械合规满分 5.0/5，但推理深度最差 4.20/5）。详见 [supplementary/p1-followup-experiments.md](supplementary/p1-followup-experiments.md)。

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

### DEV.to 社区深度反馈 (2026-07-12~13)

5篇技术文章发布后收到 11+ 条详细评论。关键反馈和验证结果：

| 评论者 | 核心贡献 | 我们的验证 |
|--------|---------|-----------|
| **Mike Czerwinski** | "receipt-of-action vs receipt-of-diligence" 概念；追问 ~0.7% 残差是否聚集在 gate 盲区 | P1-1 (n=200): 证实——gate可检测区0机械违规，盲区100%语义违规 |
| **Mike Czerwinski** | "Syllogism only buys you anything in the world you're engineering away"；GateGuard-off下格式效应复测 | P1-2 (n=240): 证实syllogism困境——code格式在gate-on下完美机械合规但推理变浅；prose格式推理始终更优 |
| **Dipankar Sarkar** | 决策token测量、语义only实验设计、scorer不带LLM偏见 | 决策token预标注声明已发布；P1-1/P1-2用确定性regex scoring |
| **René Zander** | skillgate项目：独立构建了相同模式的确定性gate引擎 | 架构对齐分析完成——Prose Barrier/Compliance Gap Theorem 2完全一致；我们的 L2/L3/L4 + 奇异环是独特贡献 |

详见 [supplementary/p1-followup-experiments.md](supplementary/p1-followup-experiments.md)。

---

## AI 模拟审查（自诊工具·非真人评审）

> ⚠️ **全部为 AI 模拟。** 用途：作者在联系真人导师/投稿前进行自我诊断。不代表任何学术机构的正式意见。

- **多轮独立审查**（2026-07-11~13，教授/博士后/顶刊审稿人隔离审查）：共识——当前 Workshop 级（ACL SRW/CHI LBW）强力接受，补盲法评分+结构重组可达 Findings/Short Paper。核心待改进项：单人非盲法评分。

完整报告：[初评](reviewer-report-2026-07-11.md) · [重评估](reviewer-report-2026-07-12-reevaluation.md)

---

## 我能做的和不能做的

**我做到了**（一个人、一台笔记本、一个 API key）：
- 五层架构设计（L0 心理安全 + Prose Barrier + 每层独立验证机制）
- 11 项实验（L0 安全提示词、回溯编码、Causal Swap、Logprob 探针、Format A/B、GateGuard-OFF、跨模型行为复制、约束梯度、跨模型约束梯度、盲交叉验证、行为测试）
- L3 格式效应非单调约束梯度（三阶段：优化→压制→反弹），L3 行为合规跨三架构验证（DeepSeek MoE / Qwen3-8B Dense / GLM-4-9B），L2/L3 分离跨模型一致（L2 logprob 仅 DeepSeek, API 限制）
- 5000+ 行 Python 脚本，19/19 行为测试全通过
- 开源社区真实认可（PR merged + Co-authored-by）

**我没做到的**（在当前条件下做不到）：
- 第二评分者 → 需要另一个人
- L2 logprob 跨模型复制 → Qwen/GLM 的 API 不支持 logprobs 参数（已做行为层跨模型，见 §6.13）
- 真人导师指导 → 正在联系相关方向导师
- 系统文献训练 → 需要时间

**这些不是借口——是边界。** 论文的价值应该在这个边界内被评估。

---

## 已发布技术博文

**DEV.to**（6 篇）：
- [AI Agents Can't Self-Verify](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) — Prose Barrier
- [I Built a Neural Gate — Layer 2](https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2) — L2 神经门
- [150 Tasks: Do AI Agents Follow Rules?](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) — L1+L3 合规
- [Measurement Was Broken](https://dev.to/yuhaolin2005/my-experiment-showed-zero-effect-a-statistician-told-me-my-measurement-was-broken-4g26) — L2 Logprob V3
- [Psychological Safety for AI — L0](https://dev.to/yuhaolin2005/i-told-my-ai-youre-safe-to-say-i-dont-know-then-i-measured-what-changed-with-logprobs-986) — L0 心理安全
- [Follow-Up: Decision-Token, Format-as-Fallback, and What Changed](https://dev.to/yuhaolin2005/follow-up-decision-token-measurement-format-as-fallback-and-what-changed-18jo) — 社区反馈+决策token+格式立场

**掘金**（中文，5 篇对应）：juejin.cn/user/4250072430682412
