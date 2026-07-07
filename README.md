> 🆕 **July 2026**: Independently converged with [Anthropic J-space](https://www.anthropic.com/research/global-workspace) — compact causal bottlenecks shape agent behavior at BOTH the neural layer (J-space) and the config layer (this project). [📄 Paper](PAPER.md)

# Hermes Workspace

> I ran 50 AI coding sessions and noticed: after ~20 turns, the model drifts. So I built a system that detects staleness, triggers regeneration, and keeps behavior consistent — then tested whether it actually works.
>
> **The finding**: Anthropic found a workspace inside neurons. I built one in config files. Same functional pattern — compact intermediate representations that causally shape behavior — emerged independently at two different abstraction layers.

## The Architecture (30 seconds)

```
self-model.md (~100 lines) → INTERFACE.md → BODY.md → hooks → behavior
    ↑                                                              ↓
    └────────── growth-log → quality-gate → flag → regenerate ←─────┘
```

Four layers. Five steps. 3/4 operational steps mechanized (Python). One step (content synthesis) runs through the LLM. Honest about which is which.

## The Causal Swap Experiment (n=30)

**Question**: Does deleting ONE config rule measurably change agent behavior?

| Condition | Alternative-offering rate | 95% CI |
|-----------|--------------------------|--------|
| WITH rule (n=15) | 73% | [48%, 89%] |
| WITHOUT rule (n=15) | 20% | [7%, 45%] |
| **Difference** | **53pp** | **[25pp, 73pp]** |

Odds ratio: 11.0 [2.1, 57.8]. Fisher exact p=0.0034. Effect consistent across 4 task rounds. Strongest under forced failures (R3/R4). Limitations: single model, single rule, no blinding.

## Why This Matters for J-space

Anthropic proved compact internal representations (J-space) causally shape model behavior — inside neural activations. This project demonstrates the **same functional pattern at the config layer** — outside the model. The convergence suggests a design principle: **compact, causally-placed intermediate representations improve agent reliability, whether emergent or engineered.**

## Quick Start

```bash
git clone https://github.com/YuhaoLin2005/hermes-workspace
cd hermes-workspace
python scripts/health-check.py --check
```

Zero dependencies. Python stdlib + markdown + file system. MIT.

## Read More

- 📄 [Full paper: Agent Identity Drift](PAPER.md)
- 🌐 [DEV.to (18 posts)](https://dev.to/yuhaolin2005)
- 🇨🇳 [掘金](https://juejin.cn/user/4250072430682412)
- 🔴 [Reddit](https://reddit.com/user/linyuhao2005)

## Author

Lin Yuhao, third-year undergrad at FAFU. Seeking summer 2026 internship. lin_yuhao2005@163.com

MIT © 2026