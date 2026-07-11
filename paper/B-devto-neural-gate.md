# I Built a Neural Gate for My AI Agent — Layer 2 of Self-Verification

> Published: https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2
> Updated: 2026-07-11

File-system checks ask "did the script run?" Neural gates ask "did the constraint actually change the output?"

## The Problem With File-System Gates

For the past month, I've been building mechanical gates for my Claude Code agent. They check file timestamps, hook registrations, exit codes. They work — they catch real configuration drift. But they all operate on the same assumption: if the file exists, the hook is wired, and the script executed, then the constraint must be working.

This is false. An AI agent can read a behavioral rule, echo it in its self-assessment, generate compliant-looking outputs — and still not be influenced by it. File-system gates check **arrival**. They don't check **penetration**.

## AI Logic ≠ Human Logic

I was using human logic (file timestamps, regex, exit codes) to verify an AI system. But an AI agent's native senses are attention weights, residual stream directions, and logprob distributions. Verification must happen at the level where information actually flows.

## Neural Gate v1: Constraint Echo Detection

`neural-gate.py` (86 lines). Extracts 8 constraint themes from BODY.md, scans output files for keyword echoes. All 8 constraints echoing. Validated across 150-task controlled experiment.

## Neural Gate v2: Logprob Differential (Designed)

Compares token probabilities with/without constraints using DeepSeek `logprobs=True`. Script written (`neural-gate-v2.py`). Needs API key.

## Neural Gate v3: Residual Stream Probes (Roadmap)

On Qwen2.5-1.5B (fits RTX 3060 6GB): train linear probes per transformer layer. Track layer shifts across sessions to detect early decay.

## Three-Layer Architecture

| Layer | Question | Status |
|-------|----------|:------:|
| L1 — Mechanical Gate | Did info arrive? | ✅ Validated (150 tasks) |
| L2 — Neural Gate | Did info penetrate? | v1 deployed, v2/v3 roadmap |
| L3 — Causal Encoding | Does format determine pathway? | ✅ Experiment (see update) |

## Update (July 11, 2026)

150-task controlled experiment: mechanical gate validated — 55.9% violation rate (no gate) → 0.7% (with gate). Full writeup: [I Ran 150 Tasks to Test If AI Agents Follow Rules](https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670)

Also discovered L3: syllogism-form rules (causal chains) vs imperative rules — same compliance rate (ceiling from mechanical gate) but systematically different reasoning depth.

## Honest Status

- v1: deployed, validated across 150 controlled tasks
- v2: written, needs API key
- v3: designed, feasible on RTX 3060 (1.5B models)
- 34 growth-logs: 55.9% violation pre-GateGuard, 0.7% post
- 7 frameworks audited, 0 do neural-layer constraint fidelity
- 2 ECC PRs merged, claude-skills Co-authored-by

---

*👋 林宇浩 — Building verification infrastructure for AI agents. [github.com/YuhaoLin2005](https://github.com/YuhaoLin2005)*
