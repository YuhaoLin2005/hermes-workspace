# Navigation Map

> **"我从 DEV.to 来，现在看什么？"** — 每条阅读路径都从这里开始。

## Quick Jumps（5 秒定位）

| 你刚读完... | 来这里 |
|------------|--------|
| "I Ran 150 Tasks..." | [PAPER.md §6.5](PAPER.md) Format A/B + `paper-validator claim l1-visibility` |
| "I Built a Neural Gate" | [PAPER.md §6.11](PAPER.md) Logprob V3 + `paper-validator claim logprob-probe-v3` |
| "AI Agents Can't Self-Verify" | [PAPER.md §3](PAPER.md) Prose Barrier + `paper-validator claim prose-barrier` |
| "Measurement Was Broken" | [PAPER.md §6.11](PAPER.md) Logprob V3 + `paper-validator claim logprob-probe-v3` |
| "Psychological Safety for AI" | [PAPER.md §3.5](PAPER.md) L0 Safety + `paper-validator claim l0-safety-prompt` |
| "Follow-Up: Decision-Token..." | [PAPER.md §6.14](PAPER.md) L1-Visibility + `paper-validator claim logprob-probe-v3` |
| "I Pre-Registered a Hypothesis" | [PAPER.md §6.16](PAPER.md) P1-2 + `paper-validator claim gateguard-off` |
| "Your Feedback Made This Better" | [PAPER.md §6.16](PAPER.md) P1-1, P1-2 + [supplementary/p1-followup-experiments.md](paper/supplementary/p1-followup-experiments.md) |
| "I Built a Self-Referential AI" | [PAPER.md §3.4](PAPER.md) Strange Loop + `paper-validator/layers/strange_loop.py` |
| "Search Didn't Make Your LLM Dumber" | [PAPER.md §3.1](PAPER.md) Context Engineering |
| "The Line Is Not Between..." | [PAPER.md §6](PAPER.md) Discussion (cross-layer synthesis) |

---

## 完整映射：DEV.to → 论文 → 代码

| DEV.to Article | 论文章节 | paper-validator claim | 实验数据/脚本 |
|---------------|---------|----------------------|-------------|
| [AI Agents Can't Self-Verify](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) | [PAPER.md §3](PAPER.md) Prose Barrier | `prose-barrier` | [paper/A-devto-prose-barrier.md](paper/A-devto-prose-barrier.md) (原稿) |
| [I Built a Neural Gate](https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2) | [PAPER.md §6.11](PAPER.md) Logprob V3 + §6.7 L2 | `logprob-probe-v3` | [paper/B-devto-neural-gate.md](paper/B-devto-neural-gate.md) (原稿) |
| [I Ran 150 Tasks](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) | [PAPER.md §6.5](PAPER.md) Format A/B + §6.12 GateGuard-OFF | `l1-visibility`, `gateguard-off` | [paper/C-devto-experiment.md](paper/C-devto-experiment.md) (原稿) |
| [Measurement Was Broken](https://dev.to/yuhaolin2005/my-experiment-showed-zero-effect-a-statistician-told-me-my-measurement-was-broken-4g26) | [PAPER.md §6.11](PAPER.md) Logprob V3 (pilot→V3 story) | `logprob-probe-v3` | [experiment/logprob-v3/](experiment/logprob-v3/) |
| [Psychological Safety for AI](https://dev.to/yuhaolin2005/i-told-my-ai-youre-safe-to-say-i-dont-know-then-i-measured-what-changed-with-logprobs-986) | [PAPER.md §3.5](PAPER.md) L0 Safety | `l0-safety-prompt` | [devto/devto-safety-prompt-l0.md](devto/devto-safety-prompt-l0.md) |
| [Follow-Up: Decision-Token](https://dev.to/yuhaolin2005/follow-up-decision-token-measurement-format-as-fallback-and-what-changed-18jo) | [PAPER.md §6.14](PAPER.md) L1-Visibility | `logprob-probe-v3`, `dissociation` | re-analysis of V3 data |
| [I Pre-Registered a Hypothesis](https://dev.to/yuhaolin2005/i-pre-registered-a-hypothesis-600-api-calls-later-the-data-killed-it-1aec) | [PAPER.md §6.16](PAPER.md) P1-2 (600 trials) | `gateguard-off` | [experiment/experiment_mike_prose_gate.py](experiment/experiment_mike_prose_gate.py) |
| [Your Feedback Made This Better](https://dev.to/yuhaolin2005/your-feedback-made-this-better-heres-what-changed-4ol2) | [PAPER.md §6.16](PAPER.md) P1-1, P1-2 | `gateguard-off`, `l1-visibility` | [supplementary/p1-followup-experiments.md](paper/supplementary/p1-followup-experiments.md) |
| [I Built a Self-Referential AI](https://dev.to/yuhaolin2005/i-built-a-self-referential-ai-system-then-anthropic-discovered-the-same-architecture-in-claude-3m73) | [PAPER.md §3.4](PAPER.md) Strange Loop | `strange_loop` module | [layers/strange_loop.py](https://github.com/YuhaoLin2005/paper-validator/blob/main/layers/strange_loop.py) |
| Search Didn't Make Your LLM Dumber | [PAPER.md §3.1](PAPER.md) Context Engineering | — | — |
| The Line Is Not Between Human and Machine | [PAPER.md §6](PAPER.md) Discussion | 全量 claims | [paper/self-model.md](paper/self-model.md) |

**中国读者**: [掘金主页](https://juejin.cn/user/4250072430682412) — 5 篇中文深度解读

---

## 三条阅读路径

### 🏃 2 分钟：看实验结论
1. 打开 [paper/README.md](paper/README.md) → "At a Glance" + "Per-Layer Status" 表格
2. 找到感兴趣的数字 → 点进对应 PAPER.md 章节

### 📖 15 分钟：读懂论文核心
1. [PAPER.md](PAPER.md) → §3 (System Design) → §4 (Causal Swap) → §6.11 (Logprob V3)
2. 回到 [paper/README.md](paper/README.md) 实验对照表

### 🔬 深入：复现 + 扩展
1. Clone [paper-validator](https://github.com/YuhaoLin2005/paper-validator)
2. `python -m paper_validator claim --list` → 查看 8 个可复现 claim
3. `python -m paper_validator claim --claim <name> --trials 30` → 跑单个实验
4. `from paper_validator.layers import L1Gates, L2NeuralGate` → 嵌入你自己的 agent

---

## paper-validator：8 Claims 速查

| # | Claim | 验证什么 | 对应文章 | 命令 |
|---|-------|---------|---------|------|
| 1 | `l0-safety-prompt` | 安全提示词是否改变输出 | [Psychological Safety for AI](https://dev.to/yuhaolin2005/i-told-my-ai-youre-safe-to-say-i-dont-know-then-i-measured-what-changed-with-logprobs-986) | `python -m paper_validator claim --claim l0-safety-prompt --trials 30` |
| 2 | `causal-swap` | 删除规则后行为是否逆转 | [I Ran 150 Tasks](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) | `python -m paper_validator claim --claim causal-swap --trials 30` |
| 3 | `logprob-probe-v3` | logprob 差分是否测量约束保真度 | [I Built a Neural Gate](https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2) + [Measurement Was Broken](https://dev.to/yuhaolin2005/my-experiment-showed-zero-effect-a-statistician-told-me-my-measurement-was-broken-4g26) | `python -m paper_validator claim --claim logprob-probe-v3 --trials 30` |
| 4 | `dissociation` | L2/L3 是否测量不同信号 | [Follow-Up: Decision-Token](https://dev.to/yuhaolin2005/follow-up-decision-token-measurement-format-as-fallback-and-what-changed-18jo) | `python -m paper_validator claim --claim dissociation --trials 30` |
| 5 | `gateguard-off` | 规则移除后合规是否退化 | [I Pre-Registered a Hypothesis](https://dev.to/yuhaolin2005/i-pre-registered-a-hypothesis-600-api-calls-later-the-data-killed-it-1aec) + [Your Feedback](https://dev.to/yuhaolin2005/your-feedback-made-this-better-heres-what-changed-4ol2) | `python -m paper_validator claim --claim gateguard-off --trials 30` |
| 6 | `l1-visibility` | 机械门是否产生可测量差异 | [I Ran 150 Tasks](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670) | `python -m paper_validator claim --claim l1-visibility --trials 30` |
| 7 | `prose-barrier` | 代码格式规则是否优于散文格式 | [AI Agents Can't Self-Verify](https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l) | `python -m paper_validator claim --claim prose-barrier --trials 30` |
| 8 | `cross-model` | 治理效应是否跨模型泛化 | — | `python -m paper_validator claim --claim cross-model --trials 30` |

---

## 社区驱动的实验

以下实验由 DEV.to 读者评论直接推动：

| 实验 | 触发者 | 核心问题 | 数据 |
|------|--------|---------|------|
| **P1-1** (n=200) | Mike Czerwinski | "0.7% 残余违规聚类在门无法检测的任务上吗？" | [supplementary/p1-followup-experiments.md](paper/supplementary/p1-followup-experiments.md) |
| **P1-2** (n=600) | Mike Czerwinski | "Prose rules + 机械门 = 两全其美？" | [data](experiment/mike_full_n30_trials.json) [script](experiment/experiment_mike_prose_gate.py) |
| **Deterministic scoring** | Dipankar Sarkar | "不用 LLM 判官——用 regex" | 所有后续实验采用 |
| **Pre-registration** | Dipankar Sarkar | "Git commit → SHA256 + provider timestamp 升级方案" | 待实现 |
| **skillgate 收敛** | René Zander | 独立构建了相同架构 | [paper/README.md §Real Feedback](paper/README.md) |
| **Mechanizability boundary** | Max Quimby | "门在哪一步从可门控变成只能轻推？" | mechanizability-scanner 待构建 |

---

## 运行 & 配置

```bash
# Clone paper-validator
git clone https://github.com/YuhaoLin2005/paper-validator.git
cd paper-validator
pip install requests
export DEEPSEEK_API_KEY=<your-key>

# 跑单个 claim
python -m paper_validator claim --claim causal-swap --trials 30

# 跑全部
python -m paper_validator claim --claim all --trials 30
```

**自定义 self-model 路径**（可选）：
```bash
export ECC_SELF_MODEL_PATH=~/.claude/projects/<your-project>/memory/self-model.md
```

---

*最后更新: 2026-07-17 · 反馈? → [GitHub Issue](https://github.com/YuhaoLin2005/hermes-workspace/issues)*
