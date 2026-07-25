# Codebase Overview

> paper-validator 仓库结构、架构分层、执行流程、配置要点。
> 设计实验/查脚本位置/理解引擎怎么跑时查此文件。配合 [[scripts]] 使用。

## 仓库位置

- **主仓库**: `C:\Users\86131\paper-validator` (GitHub: `YuhaoLin2005/paper-validator`)
- **原始实验**: `C:\Users\86131\hermes-workspace\paper\experiment\`
- **补充文档**: `C:\Users\86131\hermes-workspace\paper\supplementary\`
- **数字分身训练**: `C:\Users\86131\Desktop\digital-twin-trainer` (GitHub: `YuhaoLin2005/digital-twin-trainer`) — QLoRA+DPO 4阶段训练管线
- **全局配置**: `C:\Users\86131\.claude` (GitHub: `YuhaoLin2005/agent-self-model`) — SOUL/INTERFACE/BODY + 双池 + 五库 + 自指环

## 目录结构

```
paper-validator/
├── main.py                  # CLI入口: claim/health/interactive
├── mcp_server.py            # MCP stdio server (3 tools)
├── validate.bat             # Windows启动脚本
│
├── config/
│   ├── defaults.py          # ★ 一切常量的单源真相: 模型、规则、探针、权重
│   └── schema.py            # Dataclass模型
│
├── engine/                  # API交互层
│   ├── api_client.py        # urllib→DeepSeek /v1/chat/completions
│   ├── messages.py          # Message dataclasses
│   ├── query.py             # Agent loop: send→receive→tools→repeat
│   └── tools.py             # 4 tools: read_file/write_file/bash/grep
│
├── layers/                  # 五层架构实现
│   ├── l0_constitution.py   # 宪法规则+修订生命周期
│   ├── l1_gates.py          # HealthChecker+QualityGate+WriteGuard+RegenerationValidator
│   ├── l2_neural_gate.py    # Logprob差分约束探针
│   ├── l3_causal_encoding.py# EvalField(5 personas)+CanonizationPipeline
│   ├── l4_drift_predictor.py# 8特征drift risk scorer
│   ├── strange_loop.py      # 6阶段自指再生循环
│   └── mechanizability_scanner.py # 正则规则→层级分类器
│
├── claims/                  # 8个可复现实验
│   ├── base.py              # BaseClaim ABC + TrialResult/ClaimReport
│   ├── runner.py            # 声明注册表+编排器
│   ├── metrics.py           # Cohen's d, bootstrap CI, verdict classifier
│   ├── l0_safety_prompt.py  # Claim 1
│   ├── causal_swap.py       # Claim 2
│   ├── logprob_probe_v3.py  # Claim 3
│   ├── dissociation.py      # Claim 4
│   ├── gateguard_off.py     # Claim 5
│   ├── l1_visibility.py     # Claim 6
│   ├── prose_barrier.py     # Claim 7
│   └── cross_model.py       # Claim 8
│
├── state/                   # 运行时状态
│   ├── store.py             # 线程安全JSON KV store
│   └── flags.py             # Flag enum + FlagManager
│
├── results/                 # 实验输出
│   ├── p1_1_residual_cluster.json
│   └── p1_2_format_gate_cross.json
│
├── experiment_p1_1_residual_cluster.py  # 独立: P1-1 (200 API calls)
├── experiment_p1_2_format_gate_cross.py # 独立: P1-2 (240 API calls)
└── regex_gap_measure.py                # 独立: regex-human gap分析
```

## 执行流程

```
python -m paper_validator claim --claim all --trials 30
  → main.py cmd_claim()
    → claims/runner.py run_all()
      → 每个声明动态import → BaseClaim.run(n=30)
        → engine/api_client.py call_api() → DeepSeek /v1/chat/completions
        → claims/metrics.py → cohens_d, bootstrap_ci, classify_verdict
      → summarize(results)

python -m paper_validator health
  → config/defaults.py (常量) + state/store.py (计数器) + state/flags.py (活跃flags)
```

## 配置要点

| 位置 | 内容 | 注意 |
|------|------|------|
| `config/defaults.py` | 一切常量 | 改任何参数从这里开始 |
| `DEEPSEEK_MODEL` | "deepseek-chat" | temperature=0.0 (确保regex可重复) |
| API key fallback | DEEPSEEK_API_KEY→ANTHROPIC→... | 4层fallback |
| `results/` | JSON输出 | committed, 持久化 |

## 已知坑

1. **Windows硬编码路径**: `l4_drift_predictor.py` 用 `C:/` 检查磁盘
2. **硬编码self-model路径**: `strange_loop.py` → 用户特定路径
3. **API key无提前警告**: 未设→RuntimeError在调用时才抛
4. **无.env支持**: 必须真实环境变量
5. **中文探针/规则**: 隐含语言依赖
6. **Scanner修过bug**: commit `84a775a` → case-sensitive regex + 缺失signal

## 双仓库关系

```
hermes-workspace/paper/experiment/  ← 原始实验(探索性)
    └── logprob-v3/  ← 120 calls, 40 probes, 原始V3

paper-validator/              ← 复现+验证(工程化)
    └── claims/  ← 8个声明用BaseClaim框架复现
```

---

*最后更新: 2026-07-18*
*交叉引用: [[scripts]] [[../paper/claims]] [[../paper/structure]] [[../training/overview]] [[../strategy/system-map]]*
