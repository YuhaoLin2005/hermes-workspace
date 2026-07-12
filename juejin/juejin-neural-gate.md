Importers: 掘金手动发布。API: 无（手动复制粘贴）。Schema: markdown article。User instruction: "掘金给我md文档就好，我自己来"。

---

# 我构建了一个"神经门"——在AI Agent的生成通道内部检测规则穿透

上一篇文章讲了Prose Barrier：AI不能自我验证，因为生成通路和评估通路共享同一个解码器。

机械门（L1）绕过了这个问题——它不碰NL内容，只检查文件系统。但机械门有一个盲区：**它只能检测"行为是否合规"，无法检测"规则是否真的被内化了"。**

举个例子：我的配置里有"交付前必须做自审"的规则。机械门可以检查自审清单是否写入了文件（行为合规），但它无法判断——这个自审是认真做的，还是走形式？

这就引出了L2：**神经门**。

## 思路：不去理解内容，只做结构指纹匹配

神经门的核心洞察是：

> 如果AI真的"理解"了一条规则，它的token概率分布应该呈现可检测的模式。这种检测不需要理解规则的语义——只需要模式匹配。

具体来说：

1. 定义每条规则的关键**约束token**（比如规则"交付前自审"的关键token：`自审`、`Completeness`、`Consistency`、`Groundedness`、`Honesty`）
2. 让AI执行一个触发该规则的任务
3. 调用API的`logprobs`参数，获取关键token的log-probability
4. 比较不同条件下的token概率差异

**关键**：这个过程不做语义理解。它只是在问："这个token出现的概率变了吗？"——这是一个结构问题，不是语义问题。

## 两个版本的进化

### V1：关键词回响（简单，但不够）

第一版神经门很简单：规则定义了一组关键词，每次AI操作后，检查输出中是否出现了这些关键词的回响。

```python
# neural-gate v1 伪代码
def check_echo(output_text, rule_keywords):
    echoes = [kw for kw in rule_keywords if kw in output_text]
    return len(echoes) / len(rule_keywords)  # 回响率
```

问题：关键词出现≠规则真的被内化。AI可能只是在输出中"提到"了关键词，而没有任何实质行为改变。

### V2：Logprob差分（精确，但需要API配合）

V2直接用API的logprobs：

```python
# neural-gate v2 核心逻辑
# 给定约束token "自审"和context，获取它的logprob
# 比较：有规则注入 vs 无规则注入 → 差分 = 内化强度

def probe_constraint(constraint_token, context, api_client):
    resp = api_client.chat(context, logprobs=True, top_logprobs=20)
    logprob = resp.logprobs[constraint_token]  # token的log概率
    return logprob
```

V2不再看"关键词是否出现"，而是看"约束token的概率分布是否因规则注入而改变"。这是一个信号检测问题。

## 实测效果

我用40个探针（probes），分4类约束类型（操作规则/认知验证/结构架构/元自规），在3种条件下测试：

| 条件 | 含义 |
|------|------|
| Baseline | 无规则注入 |
| Imperative | 祈使句式："你必须先自审！" |
| Syllogistic | 三段论式："大前提→小前提→因此必须先自审" |

**关键发现**：

| 指标 | 先导 (n=8, 测量工具有bug) | 验证 (n=40, 修复后) |
|------|:--:|:--:|
| Cohen's d | −0.148 | **+0.578** |
| Bayes Factor BF₁₀ | < 1 | **282,399** |
| Bootstrap 95% CI | 跨零 | **[+3.39, +11.17]** |
| 方向一致率 | ~50% | **80%** |

三段论格式的约束内化深度，显著强于祈使句格式。这不是"AI觉得三段论更权威"——是logprob直接测量的token级概率差异。**格式改变了生成通道内部的路由。**

而且这个效应跨4类约束类型通用（ANOVA: F=0.26, n.s.），不是只对某一类规则有效。

## 神经门 vs 机械门：互补，不是替代

| | 机械门 (L1) | 神经门 (L2) |
|------|------------|------------|
| **检测什么** | 行为是否合规 | 规则是否内化 |
| **操作层面** | 文件系统 | Token概率分布 |
| **与Prose Barrier关系** | 在外面 | 在里面 |
| **可靠性** | 高（机械不可绕过） | 中（信号检测有噪声） |
| **适用场景** | 硬约束（必须做的事） | 软约束（应该内化的认知） |

**两者不是竞争关系。** 机械门保证你不翻车，神经门告诉你为什么有时候还是差一点。

## 现实定位

神经门的完成度我诚实标了~45%。它目前能做到：
- ✅ 检测到格式效应（三段论 > 祈使句，d=+0.578）
- ✅ 提供logprob级别的客观DV（API直接返回，无人工评分）
- ⚠️ 探针设计对token选择敏感（token不在top-20→检测失败）
- ❌ 尚未实时运行（目前是batch实验，不是在线gate）

V3的方向是：在线实时神经门——每次操作都跑constraint-fingerprint匹配，做drift预警而非事后分析。但那是下一个迭代的事了。

## 代码 & 数据

- **neural-gate.py** v1+v2：关键词回响 + logprob差分
- **probe_pool.py**：40个探针，4类约束
- **constraint-fingerprints.json**：规则→约束token映射
- **论文 §4**：[神经门设计与实验](https://github.com/YuhaoLin2005/hermes-workspace/blob/main/PAPER.md)

---

*系列文章：[AI Agent 无法自我验证：这不是bug，是结构约束](#) · [150个任务：AI Agent真的遵守规则吗？](#) · [我的实验显示零效应——一个统计学家告诉我测量工具坏了](#) · [我告诉AI"说不知道是安全的"](#)*

*林宇浩，福建农林大学空间信息与数字技术2023级。DeepSeek V4 Pro API。一个人。在做这件事。*
