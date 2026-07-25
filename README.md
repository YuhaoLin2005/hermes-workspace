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

**16 experiments completed.** All with deterministic regex scoring and public data. Pre-registered: P1-1, P1-2, R1/R2, E1/E1b. Full list in [PAPER.md Experiment Overview](PAPER.md).

| # | Experiment | Design | Key result | Where |
|---|-----------|--------|------------|-------|
| 1 | L0 Safety Prompt | 40 probes, within-probe, logprob DV | Accuracy preserved; gains robust (r=+0.949) | [PAPER.md §3.5] |
| 2 | Growth-log Retrospective | 34 sessions, longitudinal coding | 55.9%→0.7% with mechanical gate | [PAPER.md §6.2] |
| 3 | Causal Swap | 30 tasks, between-subjects | OR=11.0, p=0.0092 | [PAPER.md §4] |
| 4 | Logprob Probe V3 | 40 probes, within-probe, API logprob DV | d=+0.578, BF=282k | [PAPER.md §6.11] |
| 5 | Format A/B | 150 tasks, between-subjects, 6 sessions | 99.3% compliance (ceiling effect) | [PAPER.md §6.5] |
| 6 | GateGuard-OFF | 21 probes × 3 conditions | Rules work (+0.38); IMP≈SYL | [PAPER.md §6.12] |
| 7 | Cross-Model Behavioral | 12 probes × 3 models | SYL−IMP ≤ |0.025| across 3 architectures | [PAPER.md §6.13] |
| 8 | Decision-Token L1-Visibility | 40 probes re-analysis (0 API calls) | Format-L1 synergy: d_z=+0.71 vs +0.40 | [PAPER.md §6.14] |
| 9 | P1 Multi-Scene Resilience | 48 calls, multi-scene + controls | Format effects collapse; meta-instruction ~80% driver | [PAPER.md §6.15] |
| 10 | Constraint Gradient | 96 calls, 4 output-constraint levels | Non-monotonic: L1(0.596)>L3(0.297)>L0(0.315)>L2(0.091) | [PAPER.md §6.15] |
| 11 | Cross-Model Constraint Gradient | 192 calls, 2 models | No format effect on 8B/9B; model capacity boundary | [PAPER.md §6.13] |
| 12 | Syllogism Blind CV | 4 sessions | 5/5 rules triggered, zero violations + emergent auditing | [PAPER.md §6.4] |
| 13 | Compaction Decay R1 | 50 calls, 5 rules × 5 compaction levels | Null: default-aligned rules immune to compaction (96%) | [PAPER.md §6.17] |
| 14 | Compaction Decay R2 | 50 calls, 5 adversarial rules × 5 levels | L8→L12 cliff: compliance 80%→20% | [PAPER.md §6.17] |
| 15 | P1-1 Residual Cluster | 200 trials, 5 task types × 40 | L1 100% compliant; violations cluster where gate can't reach | [PAPER.md §6.16] |
| 16 | P1-2 Format×Gate | 240 trials, 2×2 factorial, pre-registered | H1 NOT CONFIRMED; prose→better reasoning regardless of gate | [PAPER.md §6.16] |

Also completed (not in main paper overview): E1a/E1b Persona Decorrelation (30→112 trials, cross-model, Fleiss' κ=0.049) — [paper/experiments/e1-persona-decorrelation.md](paper/experiments/e1-persona-decorrelation.md).

Consistency check: `python scripts/check_experiment_count.py` — verifies PAPER.md, README.md, and dashboard.md agree on experiment count.

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

- **Single rater.** Author-scored. Blind check: κ=0.00 (n=8, zero-variance — protocol never tested). Critical weakness.
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
