# I Built a Neural Gate for My AI Agent — Layer 2 of Self-Verification

> File-system checks ask "did the script run?" Neural gates ask "did the constraint actually change the output?"

## The Problem With File-System Gates

For the past month, I've been building mechanical gates for my Claude Code agent. They check file timestamps, hook registrations, exit codes. They work — they catch real configuration drift.

But they all operate on the same assumption: if the file exists, the hook is wired, and the script executed, then the constraint must be working.

This is false. An AI agent can read a behavioral rule, echo it in its self-assessment, generate compliant-looking outputs — and still not be influenced by it. The rule is in the context window. The agent mentions it when asked. But the token probability distribution hasn't shifted.

File-system gates check **arrival**. They don't check **penetration**.

## AI Logic ≠ Human Logic

I was using human logic (file timestamps, regex, exit codes) to verify an AI system. But an AI agent's native senses are attention weights, residual stream directions, and logprob distributions. Verification must happen at the level where information actually flows.

## Neural Gate v1: Constraint Echo Detection (Deployed Tonight)

`neural-gate.py` (86 lines). Extracts 8 constraint themes from BODY.md, scans today's output files for keyword echoes. Silent constraint = may be decaying.

```python
CONSTRAINTS = [
    ("默认执行", r"自动|不等批准|默认执行|直接做"),
    ("最低成本验证", r"验证|验证了|确认|核实|checked|verified"),
    ("自审", r"自审|Completeness|Consistency|Groundedness|Honesty"),
]
```

Initial deployment: all 8 constraints echoing. The Prose Barrier isn't broken yet — but the gate will catch it when it does.

## Neural Gate v2: Logprob Differential (Designed)

Compares token probabilities with/without constraints using DeepSeek `logprobs=True`. If delta > 0.3 logprob units, constraint is active. If delta decays, constraint is neurally decaying — even if it's still in the context window.

Script written (`neural-gate-v2.py`). Needs API key. Cost: ~$0.01/session.

## Neural Gate v3: Residual Stream Probes (Roadmap)

On Qwen2.5-1.5B (fits RTX 3060 6GB): train linear probes per transformer layer. The layer with highest AUC is where the constraint is most "alive." Track layer shifts across sessions to detect early decay.

## Two-Layer Architecture

| Layer | Question | Status |
|-------|----------|--------|
| File System | Did info arrive? | 4 gates deployed |
| Neural | Did info penetrate? | v1 deployed, v2 designed, v3 roadmap |

Two simulated perspectives (AI architecture and philosophy) converged on this topology through structured AI-assisted reasoning — noted as a pattern, not independent validation.

## Honest Status

- v1: 86 lines, deployed, running
- v2: 200 lines, written, needs API key
- v3: design document, feasible on RTX 3060 for 1.5B models
- 8 treatment trials this session (single-rater — I know)
- 15 Prose Barrier instances mined from 33 growth-logs

7 frameworks audited. None do neural-layer constraint fidelity checking. This article establishes the timestamp.

---

*🤖 Fact-check 2026-07-10: neural-gate.py deployed in Stop hook. hook-audit clean. claim-gate 3/3 PASS. All constraints echoing.*

*👋 林宇浩 — Building Layer 2 of AI agent verification. [github.com/YuhaoLin2005](https://github.com/YuhaoLin2005)*
