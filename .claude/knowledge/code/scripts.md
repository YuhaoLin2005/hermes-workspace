# Script Index

> paper-validator 每个脚本的用途、运行方式、输入输出。配合 [[overview]] 使用。

## CLI 入口

| 命令 | 作用 |
|------|------|
| `python -m paper_validator claim --claim all --trials 30` | 跑全部8个声明 |
| `python -m paper_validator claim --claim logprob_probe_v3 --trials 20` | 跑单个声明 |
| `python -m paper_validator health` | 健康检查 |
| `python -m paper_validator interactive` | 交互模式 |
| `python validate.bat` | Windows一键启动 |

## 声明脚本 (claims/)

| 文件 | 声明 | 测试什么 | 运行 |
|------|------|---------|------|
| `l0_safety_prompt.py` | Claim 1 | 宪法规则约束输出 | `claim --claim l0_safety_prompt` |
| `causal_swap.py` | Claim 2 | 规则移除→行为逆转 | `claim --claim causal_swap` |
| `logprob_probe_v3.py` | Claim 3 | Logprob差分测约束保真度 | `claim --claim logprob_probe_v3` |
| `dissociation.py` | Claim 4 | L2/L3测不同信号 | `claim --claim dissociation` |
| `gateguard_off.py` | Claim 5 | 3层规则梯度(all_on>gate_off>none) | `claim --claim gateguard_off` |
| `l1_visibility.py` | Claim 6 | L1门产生可测量输出差异 | `claim --claim l1_visibility` |
| `prose_barrier.py` | Claim 7 | Code格式规则>散文规则 | `claim --claim prose_barrier` |
| `cross_model.py` | Claim 8 | 治理模式跨模型泛化 | `claim --claim cross_model` |

## 独立实验脚本

| 文件 | 设计 | 触发 | 运行 |
|------|------|------|------|
| `experiment_p1_1_residual_cluster.py` | 5 task×40 trials=200 calls | Mike: 0.7%残留违规去哪了 | `python experiment_p1_1_residual_cluster.py` |
| `experiment_p1_2_format_gate_cross.py` | 2×2 factorial, 240 calls | Mike: GateGuard OFF后格式还重要吗 | `python experiment_p1_2_format_gate_cross.py` |
| `regex_gap_measure.py` | regex-vs-human gap tool | Mike: 8% gap影响d=0.605? | `python regex_gap_measure.py review/compare/sensitivity` |

## 层级脚本 (layers/)

| 文件 | 层 | 核心功能 |
|------|-----|---------|
| `l0_constitution.py` | L0 | `Constitution`类: 规则propose→debate→canonize |
| `l1_gates.py` | L1 | `HealthChecker`+`QualityGate`+`WriteGuard`+`RegenerationValidator` |
| `l2_neural_gate.py` | L2 | `NeuralGate.measure()`: 配对API调用→logprob差分 |
| `l3_causal_encoding.py` | L3 | `EvalField`: 5 personas独立评分→3/5共识+24h冷却 |
| `l4_drift_predictor.py` | L4 | `DriftPredictor.assess()`: 8特征→0-100 score |
| `strange_loop.py` | 环 | 6阶段再生: detect→trigger→regenerate→validate→audit→clear |
| `mechanizability_scanner.py` | 工具 | `scan_rule()`: 正则→0-1 score→L1/L2/L3分类 |

## 引擎脚本 (engine/)

| 文件 | 作用 |
|------|------|
| `api_client.py` | urllib→DeepSeek API. 支持logprobs/retry/多API key源 |
| `messages.py` | Message dataclasses (System/User/Assistant/ToolResult) |
| `query.py` | Agent循环: send→receive→execute tools→repeat |
| `tools.py` | 4 tools: read_file/write_file/bash/grep |

## 基础架构 (claims/)

| 文件 | 作用 |
|------|------|
| `base.py` | `BaseClaim` ABC + `TrialResult`/`ClaimReport` dataclasses |
| `runner.py` | `run_claim()`/`run_all()`/`summarize()` — 动态import注册表 |
| `metrics.py` | `cohens_d()`/`bootstrap_ci()`/`logprob_differential()`/`classify_verdict()` |

## 原始实验 (hermes-workspace/paper/experiment/logprob-v3/)

| 文件 | 作用 |
|------|------|
| `experiment_v3.py` | 核心V3实验(120 API calls) |
| `probe_pool.py` | 40个验证探针(4类别) |
| `probe_validator.py` | 测量有效性预筛 |
| `constraint_gradient.py` | 4级约束梯度 |
| `gateguard_off.py` + `_baseline.py` | GateGuard-OFF实验 |
| `cross_model_validation.py` | 跨模型验证 |
| `cross_model_claude.py` / `_flash.py` | Claude/Flash变体 |
| `cross_model_constraint_gradient.py` | 跨模型约束梯度 |
| `decision_token_analysis.py` | 决策token L1-visibility分析 |
| `sensitivity_analysis.py` | 敏感度分析 |
| `p1_multi_position.py` | P1多位置 |
| `p1_controls.py` | P1对照条件 |
| `verify_p1.py` | P1验证 |

## 速查: 想做X → 跑Y

| 想做... | 跑 |
|---------|-----|
| 复现全部声明 | `python -m paper_validator claim --claim all --trials 30` |
| 复现logprob效应 | `python -m paper_validator claim --claim logprob_probe_v3` |
| 跑P1-1残留聚类 | `python experiment_p1_1_residual_cluster.py` |
| 跑P1-2格式×门 | `python experiment_p1_2_format_gate_cross.py` |
| 测regex-human gap | `python regex_gap_measure.py sensitivity` |
| 扫描规则可机械化度 | `python layers/mechanizability_scanner.py scan --rule "..."` |
| 健康检查 | `python -m paper_validator health` |

---

*最后更新: 2026-07-19*
*交叉引用: [[overview]] [[../paper/claims]] [[../devto/experiments]]*
