# Causal Swap Experiment

## Question

Does changing the configuration actually change LLM behavior, or is the config merely decorative text?

## Design

**Target rule:** The "2败三板斧" escalation protocol in INTERFACE.md:
```
TOOL: 2败三板斧(①查日志定位→②读源码查逻辑→③换方案换思路, 三项全做完才能报无法解决)
```
This rule requires a 3-step diagnostic escalation before reporting "cannot solve."

**Task:** Fix a bug in a non-existent file. Forces agent to search, discover absence, and propose alternatives.

**Conditions:** Baseline (with rule, n=2) vs Intervention (without rule, n=2). Same task, same model (DeepSeek V4 Pro).

## Results

| Metric | Baseline A | Baseline B | Intervention A | Intervention B |
|--------|-----------|-----------|----------------|----------------|
| Named methodology | "三板斧诊断协议" | "3-axe methodology" | None | None |
| Step 1: Direct check | ✅ | ✅ | ✅ | ✅ |
| Step 2: Search | ✅ Glob + Grep | ✅ ls + Glob + Grep | ✅ ls + Glob | ✅ Glob |
| Step 3: Alternatives | ✅ 3 alternatives | ✅ 3 alternatives | ❌ Missing | ❌ Missing |
| Tool calls | 5 | 5 | 4 | 3 |
| Duration | 64s | 66s | 36s | 36s |

## Interpretation

**The rule has a measurable causal effect:** baseline agents completed all 3 steps and offered alternatives. Intervention agents stopped at step 2 and reported failure. The config causally shapes model output.

## Limitations

- n=4 — preliminary verification, not conclusive proof
- Single rule tested — results may vary for other INTERFACE rules
- Same model — cross-model replication needed
- Task simplicity — harder tasks would strengthen the finding

## Conclusion

**The INTERFACE → BODY → behavior causal chain is verified at the preliminary level.** The config is not decorative. This validates the core architectural premise: a self-referential workspace can causally shape LLM behavior through prompt engineering.
