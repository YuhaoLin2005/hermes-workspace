# Architecture: Hermes Workspace

## Design Principles

Six principles extracted from the system's own evolution:

| # | Principle | What It Means |
|---|-----------|---------------|
| P1 | **Self-Reference** | A system that modifies itself must have a causal representation of itself |
| P2 | **Mechanical Enforcement** | Rules relying on AI memory will be forgotten; critical rules need hooks |
| P3 | **Compact Representation** | Working memory is finite; what doesn't fit in the attention window is noise |
| P4 | **Identity Stability** | A self-modifying system needs an invariant core, or it drifts into meaninglessness |
| P5 | **Causal Verification** | A representation's value is its causal impact on behavior, not its self-description |
| P6 | **Failure-Driven** | System structure is shaped by real failures, not hypothetical threats |

## The Four Layers

### Layer 1: Self-Model (Compact Center)
`self-model.md` — ~100 lines. Single source of truth for identity, capabilities, goals, and warnings. This is the "global workspace" — whatever enters here broadcasts to all downstream behavior.

### Layer 2: Interface (Attention Router)
`INTERFACE.md` — 9-row neural system table. Each row maps a brain trait to a behavioral regulation:

| Brain Trait | Behavioral Rule |
|-------------|----------------|
| Long conversations → drift | Double self-audit frequency |
| Tool precision < Claude | Verification steps non-negotiable |
| Output tends to be too long | >500 words → force split |
| 1M context, ~70% effective attention | Compact at 70% |
| Chinese output > English | Technical docs in Chinese first |
| Creative > Consistent | Fixed pool weight > random pool |
| Tends to say "can't solve" early | 3-step escalation before giving up |
| Complex decisions need long reasoning | Allow extended thinking |

### Layer 3: Body (Process Rules)
`BODY.md` — Startup checks, delivery gate, degradation chain. Maps INTERFACE traits to concrete procedures. Includes a source-mapping table so every BODY rule traces back to an INTERFACE row.

### Layer 4: Mechanical Hooks (Enforcement)
Python scripts that run at session boundaries:

| Script | Hook | Function |
|--------|------|----------|
| `health-check.py` | SessionStart | Detect stale self-model, trigger regeneration |
| `three-questions-guard.py` | PreToolUse | Block edits without concept review |
| `quality-gate.py` | Stop | Check freshness, write regeneration flag |
| `honesty-check.py` | Stop | Regex-based honesty signature detection |
| `heartbeat.py` | Stop | Session metrics logging (no LLM introspection) |
| `log-regeneration.py` | Stop | Write machine-auditable regeneration log |
| `precompact-guard.py` | PreCompact | Protect context window from premature compaction |

## The Strange Loop (Causal Feedback)

```
growth-log entry → quality-gate detects staleness → writes .self-model-stale flag
    ↓
next session: health-check detects flag → AI regenerates self-model
    ↓
log-regeneration.py writes audit trail → behavior changes → new growth-log
    ↑_____________________________________________________________↓
```

**5 steps. 4 mechanized (write flag, detect flag, delete flag, audit log). 1 requires AI (content regeneration).**

## Config Degradation Chain

What happens when a core file is missing:

| Missing File | Severity | Behavior |
|-------------|----------|----------|
| `INTERFACE.md` | **Fatal** | Stop. Enter query-only mode. |
| `BODY.md` | **Serious** | Skip dual-pool review + delivery gate. Mark output "unverified." |
| `SOUL.md` | **Medium** | Work as generic assistant. Skip personal-goal judgments. |
| `self-model.md` | **Mild** | Use cached self-model. Regenerate from persona+ratings if stale flag exists. |
| `assumption.md` | **Mild** | Work with default posture. Remind user to create/repair. |

## Why This Architecture Works

The system doesn't make the LLM smarter. It makes the LLM's **environment** smarter. The LLM is an attention engine. The workspace routes that attention through a compact, self-verifying scaffold.

The key insight from J-space: a small set of privileged representations, with dense connections to downstream behavior, creates coherent identity across time. The same principle works whether the representations are neural activations (J-space) or markdown files (Hermes Workspace).
