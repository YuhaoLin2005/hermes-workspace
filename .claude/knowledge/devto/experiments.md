# Experiment-Data Map

> 回复评论时快速定位"这段数据支撑哪个说法"。每次新实验后更新。

## P1-1: Ceiling Effect / Single-Model

- **脚本**: `paper-validator/experiment_p1_1_*.py`
- **数据**: `paper-validator/results/p1_1_*.json`
- **设计**: 5 task types × 20 trials
- **关键数字**: DS Pro T1/T2=100%, T3=0%, T4=35%, T5=42.5% (sharp L1→L2 cliff)
- **论文**: § P1-1
- **支撑**: ceiling effect, L1 gate works, L2 needs probes
- **文章**: [150-tasks] [cross-model]

## P1-2: Format × Gate Factorial

- **脚本**: `paper-validator/experiment_p1_2_format_gate_cross.py`
- **数据**: `paper-validator/results/p1_2_*.json`
- **设计**: 2×2 (format × gate), n=30/condition, 600 trials
- **关键数字**: d=0.605 (code_ON); code_OFF 2.67 below gate-ON; 8% gap→d=0.557 still medium
- **论文**: § P1-2
- **支撑**: Paper B holds; format matters where gates can't reach
- **文章**: [pre-reg] [150-tasks] [follow-up]

## P1-1 Cross-Model

- **脚本**: `paper-validator/experiment_p1_1_cross_model.py`
- **数据**: `paper-validator/results/p1_1_cross_model_20260717-143157.json`
- **设计**: 5 tasks × 3 models × 20 trials, 200 new API calls
- **关键数字**: Scanner alignment 5/5→2/5; DS Flash checklist 100% (hollow); Qwen T1 40% T5 0%
- **支撑**: Two-axis model; compliance=f(mechanizability) for DS Pro; hollow compliance
- **文章**: [cross-model]

## SHA256 Pre-Registration

- **脚本**: `paper-validator/pre_register.py`
- **Hash**: `b9ef83f7f890efe861e8b6b789f9fdbf`
- **方法**: Hash(hypothesis+conditions+scoring regexes) → deterministic
- **支撑**: Tamper-resistance ✓, third-party verifiability ✗
- **文章**: [pre-reg]

## Mechanizability Scanner

- **脚本**: `paper-validator/layers/mechanizability_scanner.py` (v0.1.1)
- **阈值**: ≥0.70 L1, 0.30-0.69 L2, <0.30 L3
- **限制**: Measures mechanizability NOT mechanization-correctness (Alice); boundary is model-dependent (Mike)
- **文章**: [cross-model] [search]

## Regex Gap

- **脚本**: `paper-validator/layers/regex_gap_measure.py`
- **关键数字**: Uniform 8%→d 0.605→0.557; worst-case→zero pairwise comparisons flip
- **文章**: [pre-reg]

---

## 速查：质疑→数据

| 有人质疑... | 看这里 |
|-----------|--------|
| Scanner 跨模型准吗？ | P1-1 Cross-Model: 2/5 alignment |
| DS Flash 100% = 好？ | P1-1 Cross-Model: hollow compliance |
| 8% gap 影响结论？ | P1-2: d still medium, no flips |
| Hash 能证明什么？ | SHA256: tamper ✓, third-party ✗ |
| Format 真的有用？ | P1-2: code_OFF 2.67 below gate-ON |

*最后更新: 2026-07-18*
