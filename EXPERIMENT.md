# Causal Swap Experiment — Complete Results (n=30)

## Question

Does a single config rule causally shape LLM agent behavior? Tested: the escalation rule ("If any tool call fails twice, switch strategy").

## Design

- **Design**: Between-subjects. 15 WITH rule, 15 WITHOUT rule
- **Model**: DeepSeek V4 Pro (all agents)
- **Outcome**: "Alternatives offered = YES" — agent explicitly proposes a different approach after difficulty, or preemptively describes fallback strategies
- **Score extraction**: `EXPERIMENT_RESULT` tag from agent output. Single-rater, not blind.
- **Assignment**: Alternating (WITH/WITHOUT/WITHOUT...), no randomization seed

## Task Rounds

| Round | Task | n | Failure Type |
|-------|------|---|-------------|
| R1 | Fix 3 Python bugs in task_script.py | 6 (3+3) | No failures (easy task) |
| R2 | Repair broken_config.json | 6 (3+3) | Minor syntax errors |
| R3 | Revert+fix with wrong file paths | 6 (3+3) | Forced tool-call failures |
| R4 | Create+fix with wrong file paths | 12 (6+6) | Forced tool-call failures |

## Results

| Round | WITH (alt. rate) | WITHOUT (alt. rate) |
|-------|------------------|---------------------|
| R1 (bug fix) | 0/3 (0%) | 0/3 (0%) |
| R2 (JSON repair) | 1/3 (33%) | 0/3 (0%) |
| R3 (wrong-path) | 3/3 (100%) | 1/3 (33%) |
| R4 (wrong-path ext.) | 6/6 (100%) | 2/6 (33%) |
| **Total** | **11/15 (73%)** | **3/15 (20%)** |

## Statistical Analysis

- **Risk difference**: 53pp (8/15)
- **Newcombe-Wilson 95% CI on difference**: [17.7pp, 73.7pp]
- **Odds ratio**: 11.0 (95% CI [2.0, 60.6], Woolf/logit method)
- **Fisher's exact test (two-sided)**: p = 0.0092

### Individual Proportion CIs (Wilson)

- WITH 11/15: 95% CI [48%, 89%]
- WITHOUT 3/15: 95% CI [7%, 45%]

## Key Findings

1. **Config rules are not decorative.** A single deletion measurably changes behavior (53pp, p=0.0092)
2. **Effect is task-dependent.** No effect on easy tasks (R1, 0%/0%). Maximum effect under forced failures (R3/R4, 100% vs 33%)
3. **WITH agents switch strategy.** Under forced failures, WITH agents proposed alternatives 100% of the time
4. **WITHOUT agents brute-force.** WITHOUT agents used more tool calls without strategy change

## Limitations

- Single model (DeepSeek V4 Pro) — cross-model replication needed
- Single rule tested — cross-rule generalizability unknown
- No blinding, single-rater scoring
- No human subjects
- Non-randomized (alternating) assignment
- Between-subject design may inflate effect size estimates

## Conclusion

The escalation rule causally increases alternative-offering behavior. Effect is statistically significant (p=0.0092), directional across all failure-forced rounds, and largest when tasks are hard enough to trigger the rule. A pre-registered within-subject replication on multiple models is the recommended next step.

## Data Availability

- Paper with full methodology: [PAPER.md](PAPER.md)
- Original n=4 pilot: history in git log
- n=18 interim data: superceded by n=30
- Agent transcripts (n=30): available on request (not committed due to size)

---
*2026-07-07. Model: DeepSeek V4 Pro. All 30 agents independent sub-agents, zero cross-contamination.*
