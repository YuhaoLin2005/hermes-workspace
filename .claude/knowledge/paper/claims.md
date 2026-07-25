# Paper Claims Database

> 每个声明的支撑实验、数据路径、关键数字。设计实验/回复质疑/写文章时查此文件。
> 交叉引用: [[kb-code/scripts]] [[kb-devto/experiments]] [[kb-devto/articles]]

## 声明清单

### Claim 1: Prose Barrier — 自验证是结构性约束
- **slug**: claim-1
- **声明**: LLM 无法独立验证自身输出——生成与验证共享同一解码器 P(token|context; θ)，自验证在结构上不可靠
- **支撑实验**: Logprob V3, Prose vs Code format, 34-session retrospective
- **关键数字**: 55.9% violation rate (无gate) → 0.7% (有gate); d=+0.578 (三段论格式优势)
- **数据**: `paper/experiment/logprob-v3/` (原始), `paper-validator/results/` (复现)
- **论文章节**: §2 The Prose Barrier
- **DEV.to**: [self-verify] [150-tasks]
- **局限**: 单模型(DeepSeek V4 Pro)、无第二评分者、无跨模型logprob复现

### Claim 2: L1 Mechanical Gate — 近乎完美的合规
- **slug**: claim-2
- **声明**: 机械门(文件系统检查、正则评分)将违规率从55.9%降至0.7%
- **支撑实验**: 34-session retrospective, Format A/B (150 tasks), 19 behavioral tests
- **关键数字**: 55.9%→0.7%; 19/19 behavioral tests pass; 跨3模型均显示规则改善合规
- **数据**: `paper-validator/state/store.py` (growth-log counter), P1-1 results
- **论文章节**: §2 L1, §3.2 L1-Visibility
- **DEV.to**: [150-tasks] [self-verify] [neural-gate]
- **局限**: 历史回顾非RCT、规则集特定于此项目

### Claim 3: L2 Logprob Probes — 检测约束穿透
- **slug**: claim-3
- **声明**: Logprob差分(d=+0.578, BF=282k)可检测格式对内部表征的影响，无需解读内容
- **支撑实验**: Logprob Probe V3 (40 probes, 4 categories, 120 API calls)
- **关键数字**: d=+0.578, BF=282k, 95% CI [+3.39, +11.17], 32/40 probes favoring syllogistic
- **DV**: API-read logprob (客观，非人类评分)
- **数据**: `paper/experiment/logprob-v3/experiment_v3.py`, `paper-validator/claims/logprob_probe_v3.py`
- **论文章节**: §3.1 Logprob V3
- **DEV.to**: [neural-gate] [feedback]
- **局限**: 仅DeepSeek V4 Pro、40个探针非独立采样

### Claim 4: L2/L3 Dissociation — 格式改变内部处理不改变行为
- **slug**: claim-4
- **声明**: 三段论格式改变token级表征(L2)，但不改变行为合规(L3)——IMP≈SYL behaviorally
- **支撑实验**: GateGuard-OFF (21 probes×3 conditions), Cross-Model Behavioral
- **关键数字**: L2 d=+0.578 vs L3 Δ=-0.024; IMP-SYL behavioral gap ≤0.025 across 3 models
- **数据**: `paper/experiment/logprob-v3/gateguard_off.py`, `paper-validator/claims/dissociation.py`
- **论文章节**: §3.4, supplementary/bridge-logprob-to-behavior.md
- **DEV.to**: [feedback] [follow-up]
- **局限**: n=21 underpowered for d≤0.3 behavioral effect (need n≥90)

### Claim 5: Constraint Gradient — 非单调三阶段
- **slug**: claim-5
- **声明**: 约束梯度呈非单调: L1最高(d_z=0.596) > L3(0.297) > L0(0.315) > L2最低(0.091)
- **支撑实验**: Constraint Gradient (12 tasks×2 formats×4 levels=96 API calls)
- **关键数字**: L0→L1 optimization (0.315→0.596), L1→L2 suppression (→0.091), L2→L3 rebound (→0.297)
- **数据**: `paper/experiment/logprob-v3/constraint_gradient.py` + cross_model variants
- **论文章节**: §3.3 Constraint Gradient
- **DEV.to**: [neural-gate]
- **局限**: 单模型API-read、未预注册、4级非连续

### Claim 6: Format Effects Are Context-Fragile
- **slug**: claim-6
- **声明**: 单场景格式效应(d=+0.578)在"一个session执行多个不同任务"后坍塌至d_z=0.19
- **支撑实验**: P1 Multi-Position (24 calls), P1 Controls (48 calls)
- **关键数字**: d_z 0.58→0.19; r=-0.65 with V3; meta-instruction drives ~80% collapse
- **数据**: `paper/experiment/logprob-v3/p1_multi_position.py`, `p1_controls.py`
- **论文章节**: supplementary/p1-followup-experiments.md
- **DEV.to**: [feedback]
- **局限**: 小样本、单模型

### Claim 7: Format-L1 Synergy (Not Compensation)
- **slug**: claim-7
- **声明**: 格式效应在L1已覆盖区域更强(d_z=0.71)，在L1未覆盖区域更弱(d_z=0.40)——格式放大结构锚点，非弥补缺失执行
- **支撑实验**: L1-Visibility Analysis (40 probes)
- **关键数字**: d_z=0.71 (L1-visible) vs 0.40 (L1-invisible)
- **数据**: `paper-validator/claims/l1_visibility.py`
- **论文章节**: §3.2 L1-Visibility Analysis
- **DEV.to**: [neural-gate]
- **局限**: 单模型、API-read、分类器非独立

### Claim 8: P1-2 — Prose Format Improves Reasoning
- **slug**: claim-8
- **声明**: Prose+Gate=最佳推理(4.42/5), Code+Gate=完美机械(5.0)；**预注册H1被证伪(NOT_CONFIRMED)**——格式对推理的效应不依赖GateGuard状态；格式对机械任务的效应在GateON下巨大(d=2.96)在GateOFF下为零(0.0)
- **支撑实验**: P1-2 Format×Gate Factorial (240 trials: 4 conditions×2 tasks×30); P1-1 Residual Cluster (200 trials: 5 tasks×40)
- **关键数字**: d=0.605 (prose>code reasoning); code+Gate=完美机械(5.0)但最差推理(4.2); prose+Gate=最佳推理(4.42)
- **数据**: `paper-validator/results/p1_2_format_gate_cross.json`, `paper/experiment/experiment_mike_prose_gate.py`
- **论文章节**: §P1-2, supplementary/p1-followup-experiments.md
- **DEV.to**: [pre-reg] [150-tasks] [follow-up]
- **局限**: 双DV均regex评分(非人类)、pre-registered hypothesis被证伪(诚实报告)

### Claim 9: Cross-Model — Gateability = Structure × Capacity
- **slug**: claim-9
- **声明**: 合规性 = 规则结构 × 模型能力(二维空间)，非仅规则结构
- **支撑实验**: P1-1 Cross-Model (200 API calls: 5 tasks×3 models×20 trials)
- **关键数字**: DS Pro scanner alignment 5/5→2/5跨模型; DS Flash checklist 100%(空心合规); Qwen T1=40% T5=0%
- **数据**: `paper-validator/results/p1_1_cross_model_*.json`, community-experiments §4
- **论文章节**: Experiment 4 (Multi-Model Scanner Calibration)
- **DEV.to**: [cross-model] [search]
- **局限**: 仅3个模型、扫描器未经独立验证



### Claim 10: GateGuard Ceiling — 机械门创造近乎完美的合规天花板
- **slug**: claim-10
- **声明**: GateGuard + three-questions-guard hooks 机械阻断所有未验证操作，创造 99.3% 零违规天花板——与规则格式(三段论/祈使句)无���
- **支撑实验**: Syllogism vs Imperative A/B (6 sessions, 150 tasks, DeepSeek V4 Pro)
- **关键数字**: 149/150 (99.3%) zero violations; 唯一的1次违规被三段论agent自审发现
- **格式差异**: 祈使句 = 程序化合规 ("Q1/Q2/Q3 checklist"); 三段论 = 因果嵌入 ("大前提: Write不可逆...")
- **数据**: `paper/experiment/experiment-results-2026-07-11.md`
- **论文章节**: §6.5 (完整6-session数据见 PAPER.md)
- **局限**: GateGuard ceiling 使格式效应无法分离——需要 GateGuard=off 来隔离
- **下一步**: Replicate with ECC_GATEGUARD=off

---

## 声明→数据速查

| 有人质疑... | 查声明 | 看数据 |
|-----------|--------|--------|
| "自验证真的不可靠?" | Claim 1 | 34-session retrospective: 55.9%→0.7% |
| "机械门能覆盖所有规则?" | Claim 2 | P1-1: L1 tasks 100%, T3 0% |
| "logprob效应是真的?" | Claim 3 | d=+0.578, BF=282k, CI不跨0 |
| "内部变化影响行为吗?" | Claim 4 | IMP≈SYL, Δ=-0.024 |
| "约束越多越好?" | Claim 5 | 非单调——L2抑制L1的效应 |
| "格式效应稳定吗?" | Claim 6 | 单场景→多场景坍塌80% |
| "格式和门是替代关系?" | Claim 7 | 协同非补偿——d_z 0.71 vs 0.40 |
| "代码格式比散文好?" | Claim 8 | Prose推理更好(d=0.605)，Code机械更好 |
| "换个模型还成立吗?" | Claim 9 | 依赖模型能力——两维空间 |
| "门本身有天花板吗?" | Claim 10 | 99.3%零违规——机械门近完美天花板 |

## 诚实局限（论文公开承认）

- 无第二评分者(kappa=-0.14 for single rater)
- 无跨模型logprob复现(API限制)
- 无预注册(除P1-2)
- 单模型logprob实验(仅DeepSeek V4 Pro)
- 小样本(多分析n<50)
- 单机实现(非分布式)
- 无placebo control
- L4 drift prediction 未预测性验证

---

*最后更新: 2026-07-18*
*交叉引用: [[structure]] [[../code/scripts]] [[../devto/experiments]]*
