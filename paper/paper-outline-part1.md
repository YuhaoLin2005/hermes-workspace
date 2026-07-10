# Short Paper: Self-Referential Gate Architecture for Agent Configuration Integrity

> Revised 2026-07-10: Academic Researcher + Systems Engineer + Digital Twin + Web Search landscape.
> Target: arXiv → CHI LBW → ACL SRW.
> **Key shift**: Core contribution is NOT "dual-layer gate" — it's the **self-referential closure (strange loop)**.

## Competitive Landscape

- **HyperAgents** (Meta, ICLR 2026): code-layer. We work at config-layer.
- **Ouro Loop / Agentic Engineering**: task gates, no persistent agent identity.
- **ETH Zurich (arXiv 2604)**: validates "mechanical over semantic."
- **Our niche**: self-model regeneration + claimed-vs-evidenced cognition + creation-wiring gap. No existing framework does these.

## Title (Proposed v2 — revised 2026-07-10)

> **Mechanical Before Semantic: Self-Verifying Configuration Integrity for AI Coding Agents**

(Not "ecosystem" — 4 checks, not an ecosystem. Not "strange loop" — self-referential feedback where gate output triggers self-model regeneration.)

**Core contribution (one sentence):**
Mechanical checks (mtime, regex, exit codes, hook wiring) detect and prevent AI agent configuration drift without relying on AI self-assessment — because the agent cannot reliably judge its own configuration integrity.

> **Dual-Layer Guard Architecture for AI Agent Configuration: Structural Convergence with Neural Activation Spaces**

Alternative: **Structural Isomorphism Across Implementation Layers: A Prompt-Level Guard Architecture and Its Neural Counterpart**

## Abstract (draft, revised 2026-07-10)

AI coding agents accumulate configuration drift over extended use: behavioral rules decay, claimed capabilities diverge from actual state, and self-assessments systematically overestimate compliance. We propose a dual-layer mechanical gate architecture — a file-system layer (mtime, regex, exit codes, hook wiring) that verifies information arrival without relying on agent self-report, and a neural layer (constraint echo detection, logprob differential, residual stream probes) that checks whether behavioral constraints actually penetrate the generation process. In a preliminary within-subject comparison across 30 programming tasks (single-rater, unblinded, no placebo control — explicitly noted), the gated configuration produced more verifiable deliverables and fewer undetected drift incidents than the un-gated baseline. Cross-domain tasks showed no clear difference. A QLoRA fine-tuning attempt produced decreasing loss but collapsed behavioral quality. We frame these observations not as proof of efficacy but as motivation for a properly controlled study. All materials, including task specifications and scoring templates, are available in the accompanying repository. The core contribution is architectural: a demonstration that mechanical verification at the configuration layer can serve as an independent integrity check for self-referential agent systems — and that the structural constraint preventing AI self-verification (that generation and verification share a decoder) can be partially mitigated but not eliminated.

## Section Outline

### 1. Introduction
- Problem: single-developer AI agent reliability (no review/CI/QA infrastructure)
- Approach: dual-layer mechanical gate (soft process + hard output blocking)
- Observation: the system's 5-layer topology (identity/calibration/execution/memory/feedback) emerged iteratively from 50+ sessions of refinement, not from top-down design
- Key constraint: AI agent self-assessment and code generation share the same decoder — no independent verification channel exists within the model
- Implication: verification must operate outside the agent's generation loop (mechanical, not semantic)
- Outline: related work → architecture → observations → discussion

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
- 4.1 Within-subject comparison: n=30 tasks, single-rater, unblinded (qualitative trends only, no p-values reported)
- 4.2 Cross-domain generalization: no clear difference observed (underpowered)
- 4.3 QLoRA fine-tuning: loss↓ but behavior collapsed (informative negative)

### 5. Discussion
- 5.1 Structural inevitability hypothesis
- 5.2 What null results mean
- 5.3 Limitations (n=30, single experimenter, single model, no blinding, no inter-rater reliability, qualitative isomorphism claim, no causal intervention)
- 5.4 Ethical considerations

### 6. Conclusion

## Part 2: Neural-Layer Gates — Beyond File System Verification

> Added 2026-07-10. Extends Part 1's file-system gates with neural-layer constraint fidelity detection. Note: the architectural analysis in this section was developed through structured AI-assisted reasoning (multi-perspective simulation), not through independent human expert review. The convergence of two simulated perspectives (systems architecture + philosophy of mind) on the same dual-layer topology is noted as an interesting pattern, not as independent validation.

### Motivation: The Prose Barrier

File-system gates (Part 1) check whether information ARRIVED — scripts exist, hooks are wired, files are updated. But they don't check whether constraints actually PENETRATED the generation process. The Prose Barrier (formalized in Part 1 §Discussion) implies that verification must operate at the level where information flows: the model's output distribution.

### Neural Gate v1: Constraint Echo Detection (deployed)

**Principle**: If a behavioral constraint defined in BODY.md is actively influencing the agent, its key concepts should appear as patterns in the agent's outputs.

**Implementation**: `neural-gate.py` — extracts 8 constraint themes from BODY.md, scans today's output files for keyword echoes. Silent constraint = may be decaying. 100% echo rate observed in initial deployment (2026-07-10).

### Neural Gate v2: Logprob Differential Detection (designed)

**Principle**: For a constraint to be neurally "active," it must shift the probability distribution over action-tokens in constraint-relevant contexts.

**Method**: For each constraint, a minimal completion prompt forcing binary choice (compliant vs violating). Call DeepSeek API with `logprobs=True`. Compute `delta = mean_logprob(compliant | constrained) - mean_logprob(compliant | baseline)`. Active threshold: delta > 0.3 logprob units.

**Status**: Script written (`neural-gate-v2.py`). Requires DEEPSEEK_API_KEY.

### Neural Gate v3: Residual Stream Probes (roadmap)

**Method**: On Qwen2.5-1.5B (fits RTX 3060 6GB), extract residual stream activations at last token position for constraint-bearing vs neutral prompts. Train logistic regression probes per layer. Deploy best-layer probe for real-time constraint presence detection.

**Feasibility**: RTX 3060 6GB sufficient for 1.5B model (~4GB VRAM). Extraction + training: ~2-4 hours. Not feasible for 7B+ locally — needs cloud GPU.

### Dual-Layer Completeness

| Failure Mode | File Gates | Neural v1 | Neural v2 | Neural v3 |
|------|:--:|:--:|:--:|:--:|
| Script not wired | ✅ | — | — | — |
| Constraint never echoed in output | — | ✅ | — | — |
| Constraint echoed, no prob shift | — | — | ✅ | — |
| Constraint encoded, no causal effect | — | — | — | ✅ |
| Constraint conflict (two rules clash) | — | — | — | — |

**Known gap**: Constraint conflict resolution — when "自动执行" and "不逆操作前确认" conflict, neither layer detects which constraint dominated. Future work.

## 待完善事项

### 必须完成
1. ⬜ 第二评分者进行输出分类（Cohen's kappa）
2. ⬜ 可复现的实验方案文档化
3. ⬜ 5 类/3 门分类标准澄清
4. ⬜ 统计效力分析（n=30 最小可检测效应量）
5. ⬜ 30 项试验任务清单（难度、随机性、独立性）

### 建议完成
6. ⬜ 用随机任务顺序重跑
7. ⬜ 增加第二模型后端（10 次试验）
8. ⬜ 预注册（OSF/AsPredicted）
9. ⬜ 因果交换实验设计草案
