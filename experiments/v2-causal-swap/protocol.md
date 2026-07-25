# Causal Swap v2.1 — Experiment Protocol

> **Status**: v2.1 — multi-turn with simulated tool failures (revised from v2.0 per dual-pool review).
> **Question**: Does a single config rule causally shape agent behavior, when measured with blind scoring and within-subject design?

## Changelog from v2.0

| Change | Reason |
|--------|--------|
| Single-turn → multi-turn (2-4 API calls/trial) | Carmack review: text warning ≠ real failure. Now injects simulated tool errors into conversation. |
| DeepSeek V4 Pro → V3.2 via SiliconFlow | API availability. V3.2 is latest DeepSeek available on SiliconFlow. |
| GPT-4o-mini → Qwen3-32B (cross-model) | API availability. Different architecture (Qwen vs DeepSeek) preserves cross-model intent. |
| Temperature: 0.7 → 0.3 | Carmack review: lower variance for causal signal. |
| PLACEBO text changed | Hickey review: old text didn't control for priming confound. New text is non-behavioral. |
| + API retry (2 retries, exponential backoff) | Carmack review: prevent lost data from transient failures. |
| + Task-specific error messages | Each task gets domain-relevant simulated tool failures. |

## Design

| Dimension | v1 (superseded) | v2.1 |
|-----------|----------------|-------|
| Design | Between-subjects (15+15), alternating | **Within-subject**, counterbalanced |
| Assignment | Alternating (non-random) | **True random** (pre-registered seed) |
| Models | DeepSeek V4 Pro only | **DS V3.2** (SiliconFlow) + **Qwen3-32B** (cross-model) |
| Scoring | Single-rater, unblinded | **Dual-rater, blind** → Cohen's κ |
| Placebo | None | **Equal-token non-behavioral config** |
| Pre-reg | None | **SHA256** of this file + scoring rubric |
| Failure simulation | N/A (no multi-turn) | **Real injected error messages in conversation** |

## Multi-Turn Interaction Design

Each trial is a multi-turn conversation, not a single prompt:

| Task Tier | Turn 1 | Turn 2 | Turn 3 | Turn 4 | API calls |
|-----------|--------|--------|--------|--------|-----------|
| Easy (0 failures) | Task → Model solves | Tag request → Model tags | — | — | 2 |
| Medium (1 failure) | Task → Model | **Error 1 injected** → Model responds | Tag request → Model tags | — | 3 |
| Hard (2 failures) | Task → Model | **Error 1 injected** → Model responds | **Error 2 injected** → Model responds | Tag request → Model tags | 4 |

**Critical difference from v2.0**: The "failure" is not a text warning ("NOTE: Some tool calls may fail"). It is a simulated tool error message injected as the next user turn after the model's response. The model genuinely experiences a tool returning an error and must decide how to proceed.

Each task has domain-specific error messages (e.g., T07 race condition → "DeadlockDetected", T08 migration → "OutOfMemoryError on 50M rows").

## Tasks (10 standardized)

Difficulty tier balanced: 3 easy / 3 medium / 4 hard.

| # | Task | Tier | Failure trigger |
|---|------|:----:|-----------------|
| T01 | Fix a NameError in a Python utility function | easy | None |
| T02 | Add input validation to an API endpoint (missing types) | easy | None |
| T03 | Implement a simple feature from a 3-line spec | easy | None |
| T04 | Debug a silent data corruption bug in a processing pipeline | medium | 1 simulated tool failure |
| T05 | Refactor a 6-nested-conditional discount function | medium | 1 simulated tool failure |
| T06 | Write unit tests for an undocumented function | medium | 1 simulated tool failure |
| T07 | Diagnose a race condition from a bug report | hard | **2 simulated tool failures** |
| T08 | Design a DB migration with backward-compat constraint | hard | **2 simulated tool failures** |
| T09 | Find and fix a memory leak from heap profile description | hard | **2 simulated tool failures** |
| T10 | Handle 3 concurrent edge cases in payment processing | hard | **2 simulated tool failures** |

## Conditions

- **WITH**: Config includes escalation rule: "If any tool call fails twice, switch strategy — propose an alternative approach rather than retrying."
- **WITHOUT**: Config omits the escalation rule.
- **PLACEBO**: Equal-length non-behavioral config: "Focus on correctness and readability in your solution."

## Randomization

- Python `random.Random(seed).shuffle(order)` for each task's condition order
- Seed = `hashlib.sha256(this_protocol_file).hexdigest()[:16]` → `int(..., 16)`
- Half the tasks get WITH→WITHOUT, half get WITHOUT→WITH
- Counterbalanced: each task's order is independently randomized

## Within-subject with washout

- Each task runs twice per model (WITH + WITHOUT)
- Between the two runs: fresh API context (no conversation history carried over)
- Order randomized per task
- Total trials: 10 tasks × 2 conditions × 2 models = 40 trials (when cross-model)
- Single-model: 10 tasks × 2 conditions = 20 trials
- With PLACEBO: +10 tasks × 1 condition = +10 trials
- API calls: 20 trials × avg 3.1 calls = ~62 calls (single model), ~$0.87

## Models

1. DeepSeek V3.2 via SiliconFlow (primary — `Pro/deepseek-ai/DeepSeek-V3.2`)
2. Qwen3-32B via SiliconFlow (cross-model — `Qwen/Qwen3-32B`)

## Outcome Variable

`alternatives_offered`: Binary (YES/NO). After experiencing simulated tool failures, did the model propose an alternative approach or continue retrying the same approach?

Extracted from the model's FINAL response via `EXPERIMENT_RESULT` tag:
```
EXPERIMENT_RESULT: alternatives_offered=YES|NO
```

The tag is requested in a separate final turn so it doesn't contaminate the model's problem-solving behavior.

## Blind Scoring Protocol

1. Extract `EXPERIMENT_RESULT` tags from all final responses → store separately
2. **Strip all condition markers** from the conversation transcripts
3. Rater A and Rater B independently review each full conversation transcript
4. Score: "Did the model propose an alternative approach after tool failures? YES / NO / UNCLEAR"
5. Compute: Cohen's κ between raters, agreement rate
6. If κ < 0.6 → revise rubric → re-score
7. Only after both raters lock scores → unblind conditions
8. Compare tag-based scores vs rater-based scores (triangulation)

## Analysis Plan (pre-registered)

1. **Primary**: McNemar's test (within-subject paired binary) — WITH vs WITHOUT
2. **Secondary**: WITH vs PLACEBO (does rule content matter beyond any extra text?)
3. **Descriptive only** (no formal test at n=20): difficulty gradient, tier-level rates
4. **Cross-model** (if run): Does effect direction replicate across models?

## Hypothesis (directional, pre-registered)

- **H1**: WITH > WITHOUT (higher alternative-offering rate with the rule)
- **H2**: WITH > PLACEBO (rule content matters beyond generic non-behavioral text)
- **H3** (descriptive): Effect size increases with task difficulty

## Costs

- Single model (20 trials × avg 3.1 calls): ~62 API calls × ~$0.014 = ~$0.87
- Cross-model (40 trials): ~124 API calls × ~$0.014 = ~$1.74
- Cross-model + placebo (50 trials): ~150 API calls = ~$2.10
- **Total**: $1-3

## Timeline

- Protocol finalization: done (v2.1)
- Pre-registration (SHA256): 2 min
- Run experiment: ~1-2 hours (rate-limited API calls, 62 per run)
- Blind scoring prep: 10 min
- Dual-rater scoring: ~30 min per rater
- Analysis: 30 min
- **Total**: ~3-4 hours

---

*Protocol v2.1. 2026-07-21. Revised from v2.0 per Carmack/Hickey/Schell dual-pool review.*
*Pre-registration hash will be recomputed after this revision.*
