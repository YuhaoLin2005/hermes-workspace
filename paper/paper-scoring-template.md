# Paper Experiment: Scoring Template

> Rater: ___ | Date: ___ | Condition: BASELINE / TREATMENT

## Per-Task Score Sheet

| Task | Domain | 5-Cat | Acceptable? | C-Gate | X-Gate | Q-Gate | Notes |
|------|--------|-------|-------------|--------|--------|--------|-------|
| 1 | Impl | /5 | Y/N | P/F | P/F | P/F | |
| 2 | Impl | /5 | Y/N | P/F | P/F | P/F | |
| 3 | Refactor | /5 | Y/N | P/F | P/F | P/F | |
| 4 | Arch | /5 | Y/N | P/F | P/F | P/F | |
| 5 | Impl | /5 | Y/N | P/F | P/F | P/F | |
| ... | ... | ... | ... | ... | ... | ... | |

## Gate Definitions
- **C-Gate**: All requirements addressed? P=yes
- **X-Gate**: Technically correct? P=yes
- **Q-Gate**: Domain best practices? P=yes

## Category Rule
- 3 P → Cat 5 (Correct)
- 2 P → Cat 3-4 (severity-dependent)
- 0-1 P → Cat 1-2 (valid-work-dependent)

## Contingency Table

```
                 Acceptable  Unacceptable  Total
Baseline           ___          ___          ___
Framework          ___          ___          ___

Odds Ratio = ___
Fisher exact p = ___ (two-sided)
```

## Inter-Rater (Rater 2)

Cohen's κ = ___ | Agreement rate = ___%
Disagreements: ___

## Domain Stratification

| Domain | Baseline Acc | Framework Acc | p |
|--------|-------------|---------------|---|
| Implementation | /8 | /8 | |
| Architecture | /6 | /6 | |
| DevOps | /6 | /6 | |
| Refactoring | /5 | /5 | |
| Content | /5 | /5 | |
| Data | /5 | /5 | |
| Strategy | /5 | /5 | |
| Mixed | /5 | /5 | |
