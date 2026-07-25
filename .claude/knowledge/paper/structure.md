# Paper Architecture

> 论文的五层架构、章节结构、关键术语、研究方向。
> 写论文章节或设计新实验时查此文件。配合 [[claims]] 使用。

## 论文概览

- **标题**: The Prose Barrier: Structural Limits of Agent Self-Verification and a Five-Layer Configuration Integrity Architecture
- **格式**: ACL (4页, 双盲)
- **源文件**: `paper/acl-submission/main.tex`, `main.pdf`
- **状态**: 投稿准备中

## 五层架构

```
L0: Psychological Safety (pre-barrier)
    └── 宪法规则 + 修订生命周期(提议→辩论→共识→冷却→入典)

L1: Mechanical Gate (outside barrier — filesystem checks)
    └── HealthChecker + QualityGate + WriteGuard + RegenerationValidator
    └── 正则评分、文件存在检查、路径模式匹配——完全确定性

L2: Neural Gate (inside barrier — logprob probes)
    └── 配对API调用(with/without constraint) → logprob差分
    └── 阈值≥0.3 = "active" constraint. API-read, 客观DV.

L3: Causal Encoding (through barrier — syllogistic format)
    └── 三段论格式重新路由注意力——格式改变token概率分布
    └── EvalField(5 personas) + CanonizationPipeline(3/5共识+24h冷却)

L4: Drift Prediction (outside barrier, temporal axis)
    └── 8特征评分→0-100 risk score + temporal trend tracking
    └── 已建未验证预测性
```

## 论文章节

| 章节 | 内容 | 主要声明 |
|------|------|---------|
| §1 Introduction | 问题定义、三个核心声明 | — |
| §2 The Prose Barrier | 结构性约束定义、五层响应 | Claim 1, 2 |
| §3.1 Logprob V3 | 格式对内部表征的影响 | Claim 3 |
| §3.2 L1-Visibility | 格式-机械门协同 | Claim 7 |
| §3.3 Constraint Gradient | 非单调三阶段 | Claim 5 |
| §3.4 Behavioral Replication | 跨架构行为复现 | Claim 4, 9 |
| §P1-1 | 残留违规聚类(200 trials) | Claim 2 |
| §P1-2 | Format×Gate 2×2 Factorial(600 trials) | Claim 8 |
| §6.5 GateGuard Ceiling | 三段论 vs 祈使句 A/B (150 tasks) | Claim 10 |
| §Digital Twin | QLoRA+D PO 4阶段训练管线 (253 samples) | — |
| §Experiment 4 | 多模型扫描器校准(200 API calls) | Claim 9 |
| §Discussion | 是什么/不是什么、相关工作、实践意义 | — |
| §Limitations | 8条诚实局限 | — |

## 关键术语

| 术语 | 定义 |
|------|------|
| **Prose Barrier** | 自回归解码器结构使自验证共享生成分布→结构不可靠 |
| **Mechanizability** | 规则能否被正则/文件检查等确定性手段验证(0-1 score) |
| **Hollow Compliance** | 格式合规但内容无实质——如DS Flash checklist 100%但无真信息 |
| **Receipt-of-Action vs Receipt-of-Diligence** | 机械检查收据(格式)vs实质努力(内容)——T3 0% compliant的根因 |
| **L2/L3 Dissociation** | Logprob效应(d=+0.578)≠行为效应(Δ=-0.024)——两层测不同东西 |
| **Two-Axis Gateability** | 合规=f(规则结构, 模型能力)——二维空间，非单维 |
| **Format-L1 Synergy** | 格式效应在L1已覆盖处更强——格式放大锚点，非弥补缺失 |

## 补充材料索引

| 文件 | 内容 | 何时读 |
|------|------|--------|
| `paper/supplementary/bridge-logprob-to-behavior.md` | L2/L3 dissociation三解释 | 被问"logprob效应有什么用" |
| `paper/supplementary/gateguard-off-analysis.md` | NO RULES/IMP/SYL三条件全量 | 被问"三段论真的有用吗" |
| `paper/supplementary/layer-independence-argument.md` | 每层独立性和交叉检测矩阵 | 被问"层之间会不会混淆" |
| `paper/supplementary/verified-by-dimension.md` | Alice的执行vs解读分类维度 | 被问"两个维度什么关系" |
| `paper/supplementary/community-experiments-2026-07-17.md` | 4个社区驱动实验 | 被问"社区贡献了哪些" |
| `paper/supplementary/p1-followup-experiments.md` | P1-1 + P1-2 全量分析 | 被问"P1实验细节" |
| `../../training/overview.md` | 数字分身训练管线：MergeKit→QLoRA→DPO，Phase 3完成 | 被问"数字分身训练到什么程度"

## 开放问题 / 下一步

1. **跨模型logprob复现**: 在Claude/GPT-4o上复现d=+0.578(成本~$5)
2. **独立盲评**: 两个评分者, blinded, Cohen's kappa>0.7
3. **预注册约束梯度测试**: 正式非单调性测试(留出探针)
4. **数字分身 Phase 3 完成**: QLoRA训练完成(253 samples, gate_passed=true), 待Phase 4 DPO
5. **L1-visibility第二分类器**: 独立分类+一致性报告
6. **L4预测性验证**: 追踪20+ session检验drift predictor预测力
7. **混合效应模型**: 替代配对t检验, 更稳健的推断

---

*最后更新: 2026-07-22**
*交叉引用: [[claims]] [[../code/overview]] [[../devto/articles]]*
