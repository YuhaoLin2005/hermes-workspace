# Hermes Workspace

## 基于全局工作空间理论的AI自指配置系统 —— 在提示词工程中实现，而非神经网络权重

> 与Anthropic 2026年7月发布的J-space论文结构平行收敛（独立发现，非衍生）。
> 运行于DeepSeek V4 Pro。因果干预实验已验证（n=4）。

⚠️ 本项目由一名大三学生独立构建，非研究实验室产出。架构设计早于J-space论文发表。

---

## What Problem Does This Solve?

LLMs drift. They forget their own rules. They can't verify their own outputs. Chain-of-thought helps, but it's still text — the model can write one thing and think another.

**Hermes Workspace wraps the LLM in a mechanical scaffold.** It doesn't change the model. It changes what surrounds the model.

The insight: you can build a Global Workspace — a compact, attention-routing, self-verifying architecture — entirely in prompt engineering. No neural weights touched. No fine-tuning. Just markdown files and Python scripts.

---

## Architecture (30 seconds)

```
self-model.md        ← compact self-representation (~100 lines, single source of truth)
    ↓
INTERFACE.md         ← 9-row neural system table (brain traits → behavioral rules)
    ↓
BODY.md              ← process rules, startup checks, delivery gate
    ↓
mechanical hooks     ← Python scripts (quality-gate, health-check, honesty-check, heartbeat)
    ↓
causal feedback      ← growth-log → quality-gate → flag → regenerate self-model → behavior change
    ↑_____________________________________________________________↓
```

**Four layers. Five-step closed loop. 4/5 steps mechanized.**

---

## The Causal Swap Experiment

**Question:** Does changing the config actually change behavior, or is it decorative text?

**Method:**
- Removed ONE rule from INTERFACE.md ("2败三板斧" escalation protocol for handling errors)
- Ran n=4 sub-agents: 2 baseline (with rule), 2 intervention (without rule)
- Same task, same model (DeepSeek V4 Pro)

**Result:**
| Condition | Avg Tool Calls | Steps Completed | Offered Alternatives |
|-----------|---------------|-----------------|---------------------|
| With rule (n=2) | 5.0 | 3/3 | Yes |
| Without rule (n=2) | 3.5 | 2/3 | No |

Intervention group: fewer tools, earlier give-up, no alternative solutions. **Measurable behavioral delta. The config causally shapes model output.**

Full experiment: [EXPERIMENT.md](EXPERIMENT.md)

---

## J-space Mapping

After Anthropic published "A Global Workspace in Language Models" (July 6, 2026), I realized my architecture shared the same topology:

| J-space (Anthropic) | Hermes Workspace (this project) |
|---------------------|--------------------------------|
| Compact neural activation workspace (~几十个 concepts) | self-model.md (~100 lines) |
| Broadcast to downstream tasks | INTERFACE → BODY → behavior |
| Jacobian lens reads internal state | quality-gate.py + health-check.py |
| Causal: swap concept changes answer | Causal: remove rule changes behavior |
| Emerged from training | Emerged from iterating on failures |

**Same architecture. Different substrate.** Anthropic found it in neural activations. I built it with markdown and Python.

---

## Quick Start

```bash
git clone https://github.com/YuhaoLin2005/hermes-workspace
cd hermes-workspace

# Read the architecture
cat ARCHITECTURE.md

# Adapt INTERFACE.md to your LLM
vim workspace/INTERFACE.md

# Wire the hooks
cp workspace/settings.example.json ~/.claude/settings.json
```

**Requirements:** Python 3.10+, any LLM with API access. Tested on DeepSeek V4 Pro.

---

## Why This Matters

### 1. GWT is an architectural pattern, not a neural phenomenon
The same topology works on DeepSeek. It works in prompt engineering. It might work on any autoregressive LLM. Global Workspace dynamics may emerge from the architecture of attention itself.

### 2. Prompt engineering has an unexplored ceiling
Most prompts are instructions. This project shows prompts can be **architecture** — compact representations that route attention and causally shape behavior. The difference between "be helpful" and a self-referential workspace is the difference between a note and a program.

### 3. You don't need a PhD to build this
Python + markdown + API access. No ML training. No weight access. No research lab. The tools are already in your terminal.

---

## Who Should Care

- **AI builders** who need models with persistent identity across sessions
- **Prompt engineers** exploring the frontier between prompting and programming
- **Students** exploring AI systems — this is a weekend project, not a research program
- **Product thinkers** who want to understand what "AI-native architecture" looks like

---

## 关于作者 / About the Author

林宇浩，FAFU空间信息与数字技术大三学生。独立构建此系统，早于J-space论文发表。2026暑期产品/用研实习寻找中。

**Contact:** [GitHub Issues](https://github.com/YuhaoLin2005/hermes-workspace/issues)

---

## License

MIT © 2026 YuhaoLin2005
