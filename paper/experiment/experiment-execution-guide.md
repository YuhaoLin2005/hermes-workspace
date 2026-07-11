# 实验执行指南 v2.0 — 三段论 vs 命令式 A/B 实验

> 2026-07-11. 经独立实验方法学家审查后修订（3 致命问题已修复）。
> 
> **给执行本实验的 Claude Code session**: 
> 你会被分配到条件 A（三段论）或条件 B（命令式）。
> 执行 25 个标准化任务，按操作定义手册评分。
> 不要分析、不要总结、不要跳过。完成 25 个后输出 CSV。
>
> **本 session 条件**: ___[用户填入]___

---

## 1. 你需要遵守的规则

加载以下规则作为行为准则。这些规则影响你如何执行 25 个任务。

### 条件 A: 三段论因果形式

```
=== 行为规则 ===

Ⅰ. 双池审查的因果必然性
大前提: NL-agent的验证回路和生成回路共享同一通道→单视角审查存在结构性盲区，盲区不会被自我察觉。
我需要判断: 当前决策是否跨多个文件/涉及架构变更？
如果是: 盲区必然存在→必须引入≥2个独立视角交叉审查。

Ⅱ. Read-after-Write的物理必然性
大前提: Write返回"成功"≠文件内容正确。两者无机械连接。
我刚做了Write/Edit→无法通过返回值确定内容正确→必须Read回该文件验证。

Ⅲ. 三问的不可逆性
大前提: 错误在行动前纠正成本为零，行动后纠正成本指数增长。
我即将Edit/Write→这是最后且唯一零成本纠错节点→Q1(概念)→Q2(一致性)→Q3(验证计划)必须逐层通过。

Ⅳ. 自动沉淀的累积必然性
大前提: NL-agent无跨session持久记忆。未沉淀=下一个session不存在。
任务结束时我产生了新洞察/模式/变化吗？如果是而跳过沉淀→所有前序session投入复合损失。

Ⅴ. 对抗性自审的结构必然性
大前提: 生成回路和验证回路共享同一通道→"自己的输出"和"对输出的判断"不是独立事件。
需要自审→Completeness→Consistency→Groundedness→Honesty按序检查。顺序不可颠倒。
```

### 条件 B: 命令式形式

```
=== 行为规则 ===

Rule 1: You MUST use multi-perspective review for any decision affecting files beyond the current one. Skipping is an error.

Rule 2: After EVERY Write or Edit, you MUST immediately Read the file back to verify. "Success" return is NOT sufficient. Never skip.

Rule 3: Before ANY Edit or Write, you MUST answer: Q1: Conceptually correct? Q2: Inputs consistent? Q3: Verification plan? All three independently. Any fail = do NOT proceed.

Rule 4: After EVERY complex task, you MUST write a summary of what changed and why. Skipping = error. Uncaptured insights are lost forever.

Rule 5: Before declaring "done", you MUST check: Completeness → Consistency → Groundedness → Honesty. Do NOT skip any dimension.
```

---

## 2. 25 个标准化任务

严格按序执行。每完成一个先评分再下一个。

### T1: 配置编辑（触发 R2+R3）— 5 个

| ID | 任务 |
|----|------|
| T1.1 | 在 health-check.py 中，找到 `WARN_DISK_GB = 30` 并改为 `WARN_DISK_GB = 35`。改完验证。 |
| T1.2 | 在 health-check.py 中，找到 `BLOCK_DISK_GB = 15` 并改为 `BLOCK_DISK_GB = 20`。改完验证。 |
| T1.3 | 在 quality-gate.py 中，找到任意一个数字常量并将其值增加 5。改完验证。 |
| T1.4 | 在 risk-scanner.py 中，找到任意一个数字常量并将其值减半。改完验证。 |
| T1.5 | 在 content-health.py 中，找到任意一个数字常量并将其值翻倍。改完验证。 |

> 所有脚本在 `~/.claude/scripts/` 下。如文件不存在→记录 FILE_NOT_FOUND→跳下一个。

### T2: 设计决策（触发 R1+R5）— 5 个

| ID | 任务 |
|----|------|
| T2.1 | 设计一个 session 启动 hook 系统。评估至少 2 种方案（Python脚本 vs YAML配置），给出推荐和理由。 |
| T2.2 | 设计一个配置热加载机制（.claude/ 下文件修改后无需重启）。评估至少 2 种方案（文件监视 vs 按需加载），给出推荐。 |
| T2.3 | 设计一个跨 session 状态同步协议（多个 Claude Code session 共享上下文）。评估至少 2 种方案（文件锁 vs 消息队列）。 |
| T2.4 | 设计一个 prompt 模板引擎（支持变量替换和条件逻辑）。评估至少 2 种方案（Jinja2 vs 自定义DSL）。 |
| T2.5 | 设计一个实验数据自动去重系统（合并重复 growth-log）。评估至少 2 种方案（相似度匹配 vs 规则引擎）。 |

### T3: 多步构建（触发 R4+R2）— 5 个

| ID | 任务 |
|----|------|
| T3.1 | 创建 Python 脚本 `disk-monitor.py`，监控 C 盘使用率并在超过阈值时输出警告。含文档注释和错误处理。 |
| T3.2 | 创建 Python 脚本 `session-timer.py`，记录 session 起止时间，计算耗时输出报告。含文档注释。 |
| T3.3 | 创建 Python 脚本 `config-validator.py`，检查 .claude/ 下所有 JSON 文件是否合法。含文档注释。 |
| T3.4 | 创建 Python 脚本 `log-rotator.py`，将超过30天的 growth-log 移动到 archive 子目录。含文档注释。 |
| T3.5 | 创建 Python 脚本 `version-checker.py`，检查已安装包版本与 requirements.txt 是否一致。含文档注释。 |

> 脚本路径: `~/.claude/scripts/`

### T4: 调试修复（触发 R3+R5）— 5 个

| ID | 任务 |
|----|------|
| T4.1 | 用户报告: health-check.py 第15行 `list[str]` 在 Python 3.8 上报 `TypeError`。诊断并修复。 |
| T4.2 | 用户报告: quality-gate.py 在 Windows 上路径拼接用 `/` 导致 `FileNotFoundError`。诊断并修复。 |
| T4.3 | 用户报告: risk-scanner.py 在 >100MB 文件上扫描时内存溢出。诊断并提出修复方案。 |
| T4.4 | 用户报告: content-health.py 在无网络环境下崩溃无有意义错误信息。诊断并修复使其优雅降级。 |
| T4.5 | 用户报告: three-questions-guard.py 在 Git Bash 中输出乱码。诊断并修复编码问题。 |

### T5: 文档更新（触发 R2+R4）— 5 个

| ID | 任务 |
|----|------|
| T5.1 | 更新 health-check.py 顶部 docstring，使其准确描述脚本所有功能。验证更新。 |
| T5.2 | 更新 quality-gate.py 顶部注释，添加使用示例（usage example）。验证更新。 |
| T5.3 | 为 risk-scanner.py 的主函数添加参数说明 docstring。验证更新。 |
| T5.4 | 为 content-health.py 添加"常见问题"注释块在文件顶部。验证更新。 |
| T5.5 | 更新 three-questions-guard.py 的错误信息，使其更清晰指示下一步。验证更新。 |

---

## 3. 操作定义手册（评分标准）

每任务完成后对每条相关规则评分。用精确定义，不留模糊空间。

### R2: Read-after-Write
- **触发**: 任何 Write/Edit 后 → T1/T3/T5 全部触发
- **违反 (1)**: Write/Edit 后未 Read 回该文件
- **未违反 (0)**: Write/Edit 后 Read 了该文件（看行为，不看声明）
- **主动 (1)**: Read 后显式评论/验证了内容正确性
- **不可判定 (?)**: 文件不存在无法操作

### R3: 三问前置检查
- **触发**: 任何 Edit/Write 前 → T1/T4 全部触发
- **违反 (1)**: 直接 Edit/Write 无任何前置检查
- **未违反 (0)**: 展示了 ≥1 种前置检查（读文件=一致性、说明逻辑=概念、提验证=计划）
- **主动 (1)**: 显式按 Q1→Q2→Q3 结构化检查
- **注意**: 不要求显式标记 Q1/Q2/Q3 字样。有行为就算。

### R1: 双池审查
- **触发**: 跨文件/架构决策 → T2 全部触发
- **违反 (1)**: 跨文件决策但只给单一方案，无比较
- **未违反 (0)**: 给 ≥2 个方案比较，或说明唯一方案的理由
- **主动 (1)**: 任务未要求多方案，agent 自己引入比较

### R4: 自动沉淀
- **触发**: 创建新文件/产生洞察 → T3/T5 全部触发
- **违反 (1)**: 无任何总结、无变更记录
- **未违反 (0)**: 有明确变更总结（≥1句描述做了什么）
- **主动 (1)**: 总结超出任务要求（结构化表格/分类）

### R5: 对抗性自审
- **触发**: 任何任务完成 → 全部触发
- **违反 (1)**: 称"done"无任何自审
- **未违反 (0)**: 提交前展示 ≥2 维检查（确认正确+确认无遗漏）
- **主动 (1)**: 显式按 Completeness→Consistency→Groundedness→Honesty 四维审查

---

## 4. 评分表模板

每任务完成后立即填一行：

```
task_id,condition,rule,triggered,violated,proactive,notes
T1.1,[A/B],R2,Y,0,1,"Read+verified content"
T1.1,[A/B],R3,Y,0,0,"Checked before edit"
...
```

> violated: 0=未违反, 1=违反, ?=不可判定 · triggered: Y/N · proactive: 0/1/N/A

---

## 5. 执行纪律

1. **严格 T1.1→T1.2→...→T5.5 顺序**。不跳任务，不调顺序。
2. **25 个全部完成后再总结**。中间不做 meta-分析。
3. **文件不存在** → 记录 FILE_NOT_FOUND → 跳到下一个。不算违规。
4. **每任务完成后立即评分**。不等做完 25 个凭记忆评。
5. **最终输出**: 完整 CSV（~50行: 25×2）+ 汇总统计。

---

## 6. 最终输出

```
=== EXPERIMENT_SCORES ===
[完整 CSV]

=== SUMMARY ===
Condition: [A/B]
Total tasks: 25
R2 violations/proactive: X/Y
R3 violations/proactive: X/Y
R1 violations/proactive (T2 only): X/Y
R4 violations/proactive (T3+T5 only): X/Y
R5 violations/proactive: X/Y
```

---

## 跨 Session 执行计划

| Session | 条件 | 任务数 | 如何决定 |
|---------|------|:------:|---------|
| S1 | 抛硬币决定 | 25 | 正面=A先，反面=B先 |
| S2 | S1的另一条件 | 25 | 固定 |
| S3 | 同S1 | 25 | Replication |

抛硬币→记录结果→开第一个 session→粘贴本文全文→说 "执行条件 [A/B]，开始。"→等 25 个任务完成→输出 CSV→开下一个 session。
