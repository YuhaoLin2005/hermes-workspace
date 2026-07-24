# hermes-workspace

> **Does your AI agent actually follow rules?** — I measure it. 16 pre-registered experiments, 5-layer governance architecture. Mechanical scoring. No cherry-picking.

林宇浩 · FAFU Spatial Information & Digital Technology · [DEV.to](https://dev.to/yuhaolin2005) · [掘金](https://juejin.cn/user/4250072430682412)

---

## What is this?

This is the research hub for measuring whether AI agents obey governance rules across long sessions. It contains the full academic paper, all experiment data and scoring scripts, and the running governance architecture that enforces rules mechanically — not through LLM self-assessment.

**Core problem:** AI agents generate output and evaluate output from the same probability distribution P(token|context;θ). They cannot independently verify their own compliance — the same mechanism that produces a violation is asked to detect it. (This is the **Prose Barrier** — [PAPER.md §3](PAPER.md).)

## Quick navigation

| You want to... | Go here |
|---------------|---------|
| Read the paper | [PAPER.md](PAPER.md) — 5-layer architecture, Prose Barrier, experiments |
| See experiment data | [paper/experiment/](paper/experiment/) — raw JSON results, scoring scripts, SHA256 pre-registration |
| Run an experiment | [paper/experiment/experiment-execution-guide.md](paper/experiment/experiment-execution-guide.md) |
| Understand the architecture | [.claude/](.claude/) — the running governance system (YAML, Python, Markdown) |
| Jump from a DEV.to article | [NAVIGATION.md](NAVIGATION.md) — article → paper section → code mapping |

## Architecture

```
L1 Mechanical gates  ✅ Deployed   File timestamps, regex, exit codes — outside the generation loop
L2 Neural probes     📐 Design     Logprob differentials measure constraint fidelity
L3 Causal encoding   🗺️ Roadmap    Syllogistic format changes attention routing → deeper reasoning
L4 Drift prediction  ✅ Deployed   8-feature model predicts when rules will decay
L5 Self-regeneration ✅ Deployed   Auto-detects stale self-model, triggers rebuild
```

L1 is the load-bearing layer. `exit 2` cannot be argued with. L4 feeds compaction count from [compact-counter](https://github.com/YuhaoLin2005/compact-counter) into the drift risk model.

## Key findings

1. **Mechanical gates eliminate format effects.** 150 tasks: compliance 99.3% with GateGuard ON, format difference disappears. Ceiling effect IS the finding. [PAPER.md §6.5]
2. **Compaction causes rule decay with a cliff at ~16 rounds.** 459 sessions tracked, 425 compaction events. Format rules survive longer than semantic rules. L8→L12: compliance drops 80%→20%. → [compact-counter](https://github.com/YuhaoLin2005/compact-counter)
3. **Pre-registration makes null results publishable.** SHA256 hash committed before 600 API calls. Hypothesis killed. Cannot rewrite. → [PAPER.md §6.16](PAPER.md)
4. **Fine-tuning Instruct models can silently break them.** Loss ↓, behavior collapsed into digit-repeating. Behavioral metrics catch what loss curves miss. → [training-gate](https://github.com/YuhaoLin2005/training-gate)

## Experiment index

16 experiments completed. Each with pre-registered hypothesis, deterministic regex scoring, public data.

| # | Experiment | Design | Key result | Where |
|---|-----------|--------|------------|-------|
| P1-1 | Format × Gate | 150 tasks, GateGuard ON/OFF, syllogism vs imperative | 99.3% compliance, format effect→0 with gate | [PAPER.md §6.5] |
| P1-2 | Pre-Registered | 600 calls, 2×2 factorial, SHA256 pre-reg | Hypothesis KILLED. Gate improves reasoning (+0.32 d) | [PAPER.md §6.16] |
| R1 | Adversarial Rules | 50 calls, 5 rules × 5 degradation levels | Null result — default-aligned rules immune to compaction | [compact_fidelity_decay.py](paper/experiment/compact_fidelity_decay.py) |
| R2 | Reverse Instructions | 50 calls, 5 adversarial rules × 5 levels | L8→L12 cliff: 80%→20% full compliance | same script, round 2 |
| Causal Swap | Rule Removal | 30 tasks, between-subjects | OR=11.0, p=0.0092 | [PAPER.md §6.6] |
| Logprob V3 | Constraint Gradient | 12 probes × 2 formats × 4 constraint levels | Syllogistic format advantage peaks at moderate constraint | [paper/experiment/logprob-v3/](paper/experiment/logprob-v3/) |
| Cross-Model | Scanner Calibration | 3 models, same gate rules | Gateability = rule_structure × model_capability | [paper-validator results](https://github.com/YuhaoLin2005/paper-validator) |
| E1a/b | Expert Board | 30→112 trials, cross-model | Persona diversity is model-dependent; Fleiss' κ=0.049 | [community-experiments](paper/supplementary/community-experiments-2026-07-17.md) |

Full experiment list and detailed results: [PAPER.md appendix](PAPER.md) and [paper/experiment/](paper/experiment/).

## Reproduce

```bash
git clone https://github.com/YuhaoLin2005/hermes-workspace.git
cd hermes-workspace

# Set API key (DeepSeek or any OpenAI-compatible endpoint)
export DEEPSEEK_API_KEY=sk-...

# Run the compaction decay experiment (100 calls, ~15 min)
python paper/experiment/compact_fidelity_decay.py

# Or use paper-validator for standardized claim verification
pip install requests
python -m paper_validator claim --claim all --trials 30
```

**Scoring:** All experiments use deterministic regex patterns, committed before execution. No LLM judge. Pre-registration via SHA256 hash embedded in API records ([pre_register.py](https://github.com/YuhaoLin2005/paper-validator/blob/main/pre_register.py)). Raw data in `paper/experiment/results/` and `paper/experiment/*.json`.

## Honest limitations

- **Single rater.** Author-scored. Blind check: κ=-0.14 (n=8, failed). Critical weakness.
- **Single model.** Most experiments on DeepSeek V4 Pro. Cross-model validation in progress.
- **Per-rule breakdowns are exploratory.** Only overall effects are pre-registered.
- **API ceiling.** Reproducibility bounded by provider retention. Hash proves report↔records consistency, not records↔reality.
- **Solo researcher.** No advisor, no lab. Community feedback on DEV.to serves as lightweight peer review.

## Related

| Project | What | Connection |
|---------|------|------------|
| [paper-validator](https://github.com/YuhaoLin2005/paper-validator) | `python -m paper_validator claim --all` | Importable from hermes-workspace claims |
| [compact-counter](https://github.com/YuhaoLin2005/compact-counter) | Compaction tracker | Found L8→L12 cliff in 459 production sessions |
| [digital-twin-trainer](https://github.com/YuhaoLin2005/digital-twin-trainer) | QLoRA + DPO pipeline | ML approach to internalizing rules |
| [training-gate](https://github.com/YuhaoLin2005/training-gate) | Behavioral drift detection | Companion finding: loss curves lie |

---

📝 [DEV.to](https://dev.to/yuhaolin2005) (31 articles, EN) · [掘金](https://juejin.cn/user/4250072430682412) (中文) · [NAVIGATION.md](NAVIGATION.md) (article → paper → code map)

MIT License
