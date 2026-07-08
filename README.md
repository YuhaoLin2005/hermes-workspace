# Hermes Workspace

> **Causal swap experiment (n=30): config rules measurably shape LLM agent behavior.**
> WITH rule: 73% alternative-offering rate vs. WITHOUT: 20%. Δ=53pp, OR=11.0, Fisher exact p=0.0092.
> Independently converged on same functional pattern as Anthropic's J-space (July 2026). DeepSeek V4 Pro. MIT.

[![J-space Convergent Evolution](https://img.shields.io/badge/J--space-convergent_evolution-blue)](https://transformer-circuits.pub/2026/j-space)
[![Experiment](https://img.shields.io/badge/experiment-n%3D30%20p%3D0.0092-green)](PAPER.md)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What Problem Does This Solve?

LLM agents drift over time — forgetting negotiated conventions, relaxing quality enforcement, drifting from configured identity. Over 50 coding sessions with DeepSeek V4 Pro, I observed this ~30% of sessions.

**Hermes Workspace wraps the LLM in a mechanical scaffold.** It doesn't change the model. It changes what surrounds the model.

The insight: you can build a compact, attention-routing, self-verifying architecture entirely in prompt engineering. No neural weights touched. No fine-tuning. Just markdown files and Python scripts.

---

## Architecture (30 seconds)

```
self-model.md        ← compact self-representation (~100 lines, single source of truth)
    ↓
INTERFACE.md         ← 9-row neural system table (brain traits → behavioral rules)
    ↓
BODY.md              ← process rules, startup checks, delivery gate
    ↓
mechanical hooks     ← Python scripts (quality-gate, health-check, log-regeneration)
    ↓
causal feedback      ← growth-log → quality-gate → flag → regenerate self-model → behavior change
    ↑_____________________________________________________________↓
```

**Four layers. Five-step closed loop. 3/4 operational steps mechanized (deterministic Python).**

---

## The Causal Swap Experiment (n=30)

**Question:** Do config rules causally shape agent behavior, or are they decorative text?

**Design:** Between-subjects. 15 agents WITH escalation rule, 15 WITHOUT. Model: DeepSeek V4 Pro. Four task types (bug fix, JSON repair, wrong-path forced failures).

### Results

| Round | WITH (alt. rate) | WITHOUT (alt. rate) |
|-------|------------------|---------------------|
| R1 (bug fix) | 0/3 (0%) | 0/3 (0%) |
| R2 (JSON repair) | 1/3 (33%) | 0/3 (0%) |
| R3 (wrong-path) | 3/3 (100%) | 1/3 (33%) |
| R4 (wrong-path ext.) | 6/6 (100%) | 2/6 (33%) |
| **Total** | **11/15 (73%)** | **3/15 (20%)** |

**Risk difference:** 53pp
**Newcombe-Wilson 95% CI:** [18pp, 74pp]
**Odds ratio:** 11.0 (95% CI [2.0, 60.6])
**Fisher's exact (two-sided):** p = 0.0092 (p < 0.01)

**Interpretation:** Effect direction consistently favors WITH condition. CI excludes zero. OR=11.0. The config rule causally increases alternative-offering behavior — statistically significant and task-dependent (strongest under forced failures). **Config rules are not decorative.**

Full paper with limitations, related work, and future directions: [PAPER.md](PAPER.md)
Detailed experiment breakdown: [EXPERIMENT.md](EXPERIMENT.md)

---

## Open Source Impact

Core modules from this system have been validated through open-source contribution:

| Project | Contribution | Status |
|---------|-------------|--------|
| **ECC** (200K+★) | `delivery-gate` quality gating module | ✅ Merged via [PR #2377](https://github.com/affaan-m/ECC/pull/2377) & [#2378](https://github.com/affaan-m/ECC/pull/2378) by maintainer **affaan-m** |
| **ECC** (200K+★) | Zero-config plugin loading proposal | 📝 [PR #2365](https://github.com/affaan-m/ECC/pull/2365) — reviewed by core maintainer |
| **claude-skills** | Adversarial self-audit system | ✅ Co-author credit — concept merged, implementation rewritten by maintainer |
| **Anthropic Skills** | Agent identity drift detection | 📝 [PR submitted](https://github.com/anthropics/skills) — maintainer: "fills a real gap", "The PR is solid"

---

## J-space: Convergent Evolution

After Anthropic published "A Global Workspace in Language Models" (July 2026), I mapped my architecture onto their findings:

| J-space (Anthropic) | Hermes Workspace (this project) |
|---------------------|--------------------------------|
| Compact neural subspace (~25 concepts, <10% activations) | self-model.md (~100 lines) |
| Causal: swap concept → changes answer | Causal: remove rule → changes behavior |
| Emerged from gradient descent | Emerged from iterating on 50 broken sessions |
| Downstream layers attend to J-space | Context window attends to self-model |

**Same functional pattern. Different substrate.** Both are compact, causally-placed, structured, and attended-to — four properties that appear necessary for an intermediate representation to shape agent behavior. This is convergent evolution at the functional level, not homology.

---

## Quick Start

```bash
git clone https://github.com/YuhaoLin2005/hermes-workspace
cd hermes-workspace

# Read the architecture
cat ARCHITECTURE.md

# Read the full paper
cat PAPER.md

# Adapt INTERFACE.md to your LLM
vim workspace/INTERFACE.md

# Wire the hooks
cp workspace/settings.example.json ~/.claude/settings.json
```

**Requirements:** Python 3.10+, any LLM with API access. Tested on DeepSeek V4 Pro.

Example: wire the hooks into your Claude Code config
```bash
cp workspace/settings.example.json ~/.claude/settings.json
# Edit INTERFACE.md to match your workflow
# Run health-check to verify the pipeline
python scripts/health-check.py --check
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for full design rationale and component details.

---

## Related Reading

**English (DEV.to):**
- [I Built a Self-Referential AI System. Then Anthropic Discovered the Same Architecture in Claude.](https://dev.to/yuhaolin2005/i-built-a-self-referential-ai-system-then-anthropic-discovered-the-same-architecture-in-claude-3m73)
- [How I Built a File-Timestamp-Based Feedback Loop to Enforce AI Output Quality](https://dev.to/yuhaolin2005/how-i-built-a-file-timestamp-based-feedback-loop-to-enforce-ai-output-quality-1ibc)

**中文（掘金）:**
- [我删掉了一行配置，AI 的行为变了——n=30 因果实验全记录](https://juejin.cn/post/7659671273129705522)
- [在DeepSeek上复现了Anthropic的J-space架构](https://juejin.cn/post/7659251094817341490)
- [我用三个 Python 脚本，让 AI 学会了"记得自己是谁"](https://juejin.cn/post/7659252393879748617)

---

## Why This Matters

1. **Config rules are causally efficacious.** n=30 experiment with p=0.0092 confirms they're not decorative text.
2. **GWT is an architectural pattern, not a neural phenomenon.** Same topology works on DeepSeek. It works in prompt engineering.
3. **Prompt engineering has an unexplored ceiling.** Prompts can be architecture — compact representations that route attention and causally shape behavior.
4. **You don't need a PhD to build this.** Python + markdown + API access. No ML training. No weight access. No research lab.

---

## Find Me On

- **GitHub:** [YuhaoLin2005](https://github.com/YuhaoLin2005)
- **DEV.to:** [dev.to/yuhaolin2005](https://dev.to/yuhaolin2005)
- **掘金:** [juejin.cn/user/yuhaolin2005](https://juejin.cn/user/4303322289409304)
- **Reddit:** [reddit.com/user/linyuhao2005](https://reddit.com/user/linyuhao2005)

---

## About the Author

Lin Yuhao, third-year student at FAFU (Spatial Information & Digital Technology). Built this system independently before the J-space paper was published. Seeking summer 2026 internship.

**Contact:** lin_yuhao2005@163.com

---

## License

MIT © 2026 YuhaoLin2005
