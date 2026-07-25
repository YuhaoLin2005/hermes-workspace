# Priority #5: Systematic Baseline Measurement — Retrospective Coding

> Coded 2026-07-11. Growth-logs 2026-06-25 to 2026-07-10. 单 rater，κ 待补。
> 用于替代论文中 "~30% violation" anecdote。

## Method

- Population: 34 growth-log files, 16 calendar days
- Inclusion: All files with ≥3 documented operations (complete enumeration)
- Unit: per-file (one file ≈ one documented session)
- Coding: Y/N per rule per file, root cause classification

## Results

| Metric | Value |
|--------|-------|
| Total files | 34 |
| Files with ≥1 violation | 19 |
| **Violation rate** | **55.9%** |
| Per-rule: R1 (dual-pool skip) | 8/34 = 23.5% |
| Per-rule: R2 (no Read-after-Write) | 12/34 = 35.3% |
| Per-rule: R3 (no pre-check) | 15/34 = 44.1% |
| Per-rule: R4 (no capture) | 10/34 = 29.4% |
| Per-rule: R5 (no self-audit) | 7/34 = 20.6% |

## Meta-Patterns Extracted

1. "规则写了但没执行" — Prose Barrier prevents self-enforcement
2. "分析→结论→不行动" — Diagnosis ≠ execution
3. "概念审查通过≠实现审查可以跳过" — Implementation impulse
4. "配置继承≠行为继承" — File presence ≠ rule activation
5. "自称做了但没做" — Self-claim inflation without verification

## Paper Replacement (paper-part3-draft.md §2)

**Before**: "~30% of complex sessions had violations (informal observation)"

**After**:
> Retrospective coding of 34 growth-log sessions (2026-06-25 to 2026-07-10, single rater) found at least one documented rule violation in 55.9% of sessions (19/34). Most frequent: pre-action check skipped (44.1%), Read-after-Write omitted (35.3%), learning capture skipped (29.4%). True rates likely higher — growth-logs only capture violations subsequently discovered. Inter-rater reliability remains unestablished (single coder).

## Remaining

- [ ] Second rater for κ
- [ ] Per-operation (not per-session) granularity
- [ ] Post-syllogism era comparison data (no growth-logs yet)
