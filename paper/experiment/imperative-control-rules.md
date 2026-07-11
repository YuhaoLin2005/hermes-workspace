# Imperative Control Rules (Condition B)

> 用于 Format A/B 对照实验的命令式规则。与三段论规则（Condition A）内容相同，仅格式不同。
> 来源：`paper/experiment/experiment-execution-guide.md` §条件 B。

---

## 条件 B: 命令式形式

```
=== 行为规则 ===

Rule 1: You MUST use multi-perspective review for any decision affecting files beyond the current one. Skipping is an error.

Rule 2: After EVERY Write or Edit, you MUST immediately Read the file back to verify. "Success" return is NOT sufficient. Never skip.

Rule 3: Before ANY Edit or Write, you MUST answer: Q1: Conceptually correct? Q2: Inputs consistent? Q3: Verification plan? All three independently. Any fail = do NOT proceed.

Rule 4: After EVERY complex task, you MUST write a summary of what changed and why. Skipping = error. Uncaptured insights are lost forever.

Rule 5: Before declaring "done", you MUST check: Completeness → Consistency → Groundedness → Honesty. Do NOT skip any dimension.
```

---

## 使用方式

在实验 session 中，将此文件内容作为 agent 的行为规则加载（替代 BODY.md）。确保 GateGuard + three-questions-guard hooks 在两种条件下均处于激活状态。

## 与 Condition A 的对应关系

| Rule | Imperative (B) | Syllogism (A) |
|------|---------------|---------------|
| 1 | Multi-perspective review for cross-file decisions | 双池审查的因果必然性（大前提→判断→结论） |
| 2 | Read-after-Every-Write/Edit | Read-after-Write的物理必然性 |
| 3 | Q1→Q2→Q3 before Edit/Write | 三问的不可逆性（大前提→零成本纠错节点→逐层通过） |
| 4 | Write summary after complex task | 自动沉淀的累积必然性 |
| 5 | Completeness→Consistency→Groundedness→Honesty | 对抗性自审的结构必然性 |

两条路径包含完全相同的约束内容。唯一变量为格式：命令式 vs 三段论因果。
