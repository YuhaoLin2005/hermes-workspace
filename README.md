# hermes-workspace

> Dual-layer mechanical gate for AI agent self-configuration. Independent architectural convergence with neural activation spaces.

## The Problem

Individual developers using AI coding agents lack process infrastructure. No review. No CI. No stale-config detection. Developer = coder + reviewer = single point of failure.

## Architecture

Five-layer self-configuration system:
1. **Identity** (SOUL.md) — persona, boundaries
2. **Calibration** (INTERFACE.md) — model-specific tuning
3. **Execution** (BODY.md) — hot-path rules, dual-pool review
4. **Memory** (MEMORY.md + 5 libraries) — HOT/WARM/COLD state
5. **Feedback** (quality-gate.py + health-check.py + self-model regeneration)

Dual-layer gate: soft process monitoring (never blocks) + hard output blocking (exit 2).

## What I Observed (preliminary, single-rater, unblinded)

- 30 programming tasks across 5 domains, with and without the gate system
- Treatment group consistently produced more verifiable deliverables than baseline (same person scored both — take with salt)
- Cross-domain tasks: no clear difference (underpowered to detect)
- QLoRA fine-tuning experiment: loss decreased but behavioral quality collapsed — loss alone doesn't tell you if the system is working
- 12 additional treatment trials: pattern held, but no control comparison (adding treatment-only data biases the comparison — acknowledged)

## Research Question

**Under what conditions can a self-referential AI agent system maintain configuration integrity, and what is the minimum set of mechanical checks required?** Currently exploring: file-system layer (4 gates) + neural layer (3-stage progression). Preliminary. No p-values until someone other than me scores the outputs.

## Related

- [digital-twin-trainer](https://github.com/YuhaoLin2005/digital-twin-trainer)
- [compact-counter](https://github.com/YuhaoLin2005/compact-counter)
- [Juejin: J-space structural convergence](https://juejin.cn/post/7660007537018617883)

## Status

- [x] Five-layer architecture + dual-layer gate
- [x] 30 + 8 trials
- [ ] Double-blind second rater (needed)
- [ ] n≥60 target

## License

MIT
