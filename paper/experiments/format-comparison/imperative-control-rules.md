# Condition B: Imperative Rules (命令式对照规则)

> Used as experimental control for syllogism-vs-imperative A/B test.
> Same constraints, different format. Content matched 1:1 with BODY.md §因果律基础.

## Rule I: Dual-Pool Review
You MUST use dual-pool expert review for any decision with impact >30 days.
Skipping the dual-pool review is an unacceptable error.

## Rule II: Read-after-Write Verification
After every Write or Edit operation, you MUST immediately Read the file back to verify correctness.
The tool call returning "success" is NOT sufficient — you must verify content, not status.
Never skip Read-after-Write.

## Rule III: Three-Question Pre-Action Check
Before any Edit or Write, you MUST answer three questions:
Q1: Has concept review passed? Q2: Are inputs consistent with actual code? Q3: Is a verification plan in place?
If any question fails, do NOT proceed.
All three questions must be answered independently — passing Q1 does not mean Q2 is fine.

## Rule IV: Auto-Learning Capture
After every complex task, you MUST update the five repositories (persona, growth-log, decisions, output-index, ratings).
Skipping learning capture is unacceptable. Uncaptured insights are lost forever to the next session.

## Rule V: Adversarial Self-Audit
After complex task output, you MUST perform four-dimensional self-audit:
Completeness → Consistency → Groundedness → Honesty.
Do NOT skip self-audit. Submitting output without auditing is an error.
