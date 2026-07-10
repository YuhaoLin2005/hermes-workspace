# Short Paper: Self-Referential Gate Architecture for Agent Configuration Integrity

> Revised 2026-07-10: Academic Researcher + Systems Engineer + Digital Twin + Web Search landscape.
> Target: arXiv → CHI LBW → ACL SRW.
> **Key shift**: Core contribution is NOT "dual-layer gate" — it's the **self-referential closure (strange loop)**.

## Competitive Landscape

- **HyperAgents** (Meta, ICLR 2026): code-layer. We work at config-layer.
- **Ouro Loop / Agentic Engineering**: task gates, no persistent agent identity.
- **ETH Zurich (arXiv 2604)**: validates "mechanical over semantic."
- **Our niche**: self-model regeneration + claimed-vs-evidenced cognition + creation-wiring gap. No existing framework does these.

## Title (Proposed v2 — post professor review)

> **Mechanical Before Semantic: Self-Verifying Configuration Integrity for AI Coding Agents**

(Not "ecosystem" — 4 checks, not an ecosystem. Not "strange loop" — self-referential feedback where gate output triggers self-model regeneration.)

**Core contribution (one sentence):**
Mechanical checks (mtime, regex, exit codes, hook wiring) detect and prevent AI agent configuration drift without relying on AI self-assessment — because the agent cannot reliably judge its own configuration integrity.

> **Dual-Layer Guard Architecture for AI Agent Configuration: Structural Convergence with Neural Activation Spaces**

Alternative: **Structural Isomorphism Across Implementation Layers: A Prompt-Level Guard Architecture and Its Neural Counterpart**

## Abstract (draft, ~150 words)

The dual-layer mechanical gate is an architecture for AI agent configuration that combines soft process monitoring with hard output blocking, deployed entirely at the prompt-engineering layer. We report an independently designed five-layer agent configuration system (identity, calibration, execution, memory, feedback) whose topology exhibits structural isomorphism with cross-layer convergence patterns observed in neural activation spaces. Across 30 controlled trials, Fisher's exact test yields p=0.0092 (odds ratio=11.0) for output quality improvement. Cross-domain behavioral generalization showed no significant result. QLoRA fine-tuning produced catastrophic forgetting—all behavioral metrics degraded despite decreasing loss. We interpret these results not as replication of neural-layer findings but as evidence for structural inevitability: the optimization target may determine architectural topology regardless of implementation substrate.

## Section Outline

### 1. Introduction
- Problem: single-developer AI agent reliability (no review/CI/QA infrastructure)
- Approach: dual-layer mechanical gate (soft process + hard output blocking)
- Surprise: independent convergence to five-layer topology mapping onto J-space
- Hypothesis: structural inevitability — same problem → same architectural shape
- Outline: related work → architecture → experiments → discussion

### 2. Related Work
- 2.1 Global Workspace Theory (Baars 1988, Goyal & Bengio 2022)
- 2.2 Neural Interpretability: J-space (Elhage et al. 2022, Bricken et al. 2023)
- 2.3 Constitutional AI and Guard Architectures (Bai et al. 2022, Kundu et al. 2024)
- 2.4 Prompt Engineering as Design Discipline (White et al. 2023, Zamfirescu-Pereira et al. 2023)
- 2.5 Behavioral Evaluation Beyond Perplexity (Lin et al. 2022 TruthfulQA)

### 3. Architecture
- Five layers: Identity → Calibration → Execution → Memory → Feedback
- Dual-layer gate: soft (config-health) + hard (quality-gate, exit 2)
- Key principles: mechanical over semantic, soft-on-process/hard-on-output, zero-token normal path
- Structural isomorphism with J-space (table)

### 4. Experiments
- 4.1 Controlled comparison: n=30, Fisher exact p=0.0092, OR=11.0
- 4.2 Cross-domain generalization: NULL (all p > 0.05)
- 4.3 QLoRA fine-tuning: NEGATIVE (loss↓ but behavior collapsed)

### 5. Discussion
- 5.1 Structural inevitability hypothesis
- 5.2 What null results mean
- 5.3 Limitations (n=30, single experimenter, single model, no blinding, no inter-rater reliability, qualitative isomorphism claim, no causal intervention)
- 5.4 Ethical considerations

### 6. Conclusion

## Pre-Professor Checklist

### Blockers (do not schedule meeting without)
1. ⬜ Second rater for output classification (Cohen's kappa)
2. ⬜ Reproducible experimental protocol documented
3. ⬜ Fisher exact test independently recomputed
4. ⬜ Clarify 5-category/3-gate classification criteria

### Professor's First Questions (prepare)
5. ⬜ Power analysis (n=30 minimum detectable effect size?)
6. ⬜ Task list for 30 trials (difficulty, randomization, independence)
7. ⬜ J-space comparison formalization criterion
8. ⬜ Coincidence probability estimate

### Nice-to-Have
9. ⬜ Re-run with randomized task order
10. ⬜ Add second model backend (10 trials)
11. ⬜ Pre-registration (OSF/AsPredicted)
12. ⬜ Causal swap experimental design draft

## Meeting Readiness: YES (with conditions)

**Opening line**: "I built something that worked for my own use, noticed it structurally resembles something in published literature, ran initial experiments. Results mixed — one significant, two null. I want your advice on whether worth writing up as workshop paper."

**Professor will question**: (1) J-space citation legitimacy (2) Null hypothesis precision (3) Trial independence (4) PR #778 publication status (5) Whether Anthropic papers were actually read or just blog posts (6) Why convergence isn't just imposed pattern-matching.

**Bottom line**: Enough substance for first conversation. Honest about limitations. Concrete next-steps list.
