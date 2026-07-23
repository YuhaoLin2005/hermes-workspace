# E1: Persona Decorrelation — Expert Board Independence Validation

> 来源：Mike Czerwinski DEV.to 评论质疑 → 实验设计 → E1a(天花板) → E1b(证伪)
> 实验脚本：`paper-validator/experiment_e1_persona_decorrelation.py` (E1a), `experiment_e1b_snippet_pretest.py` + `experiment_e1b_cross_model.py` (E1b)
> 结果数据：`paper-validator/results/e1_persona_decorrelation.json`, `results/e1b_snippet_pretest.json`, `results/e1b_cross_model.json`
> 完整记录：`growth-log/2026-07-23-e1-persona-decorrelation.md`, `growth-log/2026-07-23-e1b-cross-model.md`

## 背景

论文使用 3-persona expert board (Carmack/Torvalds/Knuth) 做代码审查。Mike Czerwinski 在 [DEV.to 评论](https://dev.to/jugeni/comment/3bi5c) 中质疑：board 的 diversity 是真正的 persona 独立性还是 "costume diversity"——同一 base model 穿 33 件外衣自我点头。

他的建议：**decompose the variance**。跨模型测试——如果 Claude-Carmack 与 Claude-Thompson 一致但与 GPT-Carmack 不一致，diversity 是 costume。如果同一 persona 跨模型一致，board 是真实的。

## E1a: 初始实验（天花板效应）

### 设计

- 3 personas (Carmack/Torvalds/Knuth) × 2 models (DS V4 Pro + Kimi K2.7 Code) × **5 snippets** = 30 trials
- Pre-reg: `eebe2a31fb290860`

### 结果

| 条件 | 一致率 | N |
|------|--------|---|
| Cross-model same-persona | **1.000** | 15 |
| Within-model diff-persona | **0.867** | 30 |

**初步结论**: Persona drives judgment (1.00 > 0.87)

### 问题

专家团审查（Mike/Dipankar/James）指出：**4/5 snippets unanimous（天花板效应）**。只有 `error_silent` 区分了 persona。Wilson 95% CI 大幅重叠。1.00 = 实验设计失败，非方法学成功。

## E1b: 重构实验（证伪 E1a）

### 设计

按专家团建议全面重设计：

- **预筛选**: 30 snippets → 14 discriminating items (agreement 0.00-0.33, all 14 show genuine disagreement)
- **主实验**: 14 snippets × 3 personas × 2 models = 84 trials
- **Control**: 14 snippets × no-persona × 2 models = 28 trials
- **总计**: 112 trials
- **指标**: Fleiss' κ (chance-corrected) + 95% bootstrap CI
- Pre-reg: `9c80bad72382d8c4`

### 核心结果

#### Fleiss' κ（概率修正一致率）

| 条件 | κ | 95% CI | 解释 |
|------|-----|--------|------|
| All 6 persona-raters | **0.049** | [-0.046, 0.111] | **不可区分于随机** |
| DS V4 Pro 3 personas | **-0.201** | [-0.334, -0.081] | **负一致——persona分歧>随机** |
| Kimi K2.7 Code 3 personas | **0.460** | [0.142, 0.724] | 中等一致 |
| Control (no persona) | **-0.292** | [-0.495, -0.167] | 模型自身分歧>随机 |

#### 原始一致率

| 条件 | 一致率 | vs E1a |
|------|--------|--------|
| Cross-model same-persona (avg) | **~0.405** | E1a: 1.000 |
| Within-model diff-persona (DS) | 0.405 | — |
| Within-model diff-persona (Kimi) | 0.643 | — |

#### Manipulation Check

Persona vs control score deltas 平均 ~ -0.11（clarity/correctness/efficiency/maintainability）—— persona 未系统性改变评分。

### 关键发现

1. **整体 κ ≈ 0**：aggregated across all persona-raters，一致率不可区分于随机
2. **Model × Persona 交互**：DS κ=-0.201 vs Kimi κ=0.460——同一实验操作在不同模型上产生**相反效果**
3. **Persona 效果是 model-dependent 的**：不泛化
4. **Control 条件 κ=-0.292**：剥离 persona 后，模型之间仍然分歧——证明 E1a 的"diversity"实际上是模型异质性，非 persona 多样性

### 专家团共识

| 问题 | 共识 |
|------|------|
| E1b 支持 E1a "persona drives judgment" 吗？ | 否。κ=0.049≈随机 |
| DS vs Kimi 分裂意味什么？ | Persona 效果是 model-dependent |
| 是 costume diversity 吗？ | 是。表面 persona 着色，无系统性判断差异 |
| 论文 impact？ | 从 "persona-driven expert diversity" 降级为 "multi-model ensemble with cosmetic personas" |

## 对论文的影响

### 方法学修正

- **Expert board 框架需要重写**。不能说"3 个独立专家视角"——应该说"3 个 LLM persona，其 diversity 受 base model 显著影响，整体效应量接近零"
- **Named-principle anchor 仍然有效**：premise decorrelation + source-checkable citations 是真实贡献。Persona 本身不是
- **报告 model-specific κ 值**：DS κ=-0.201, Kimi κ=0.460——承认效果不泛化

### 方法论贡献

E1b 本身是一个 **methodologically sound 的 negative result**：
- Pre-registration + chance-corrected metric + bootstrap CI + manipulation check + control condition
- 诚实报告 negative result 比 E1a 的"完美 1.00"科学质量高得多
- 论文可引用 E1b 作为"自我证伪"的证据——证明方法论严谨性

### 推荐下一步

1. 第三模型 (GPT-4o/Claude Opus) 测试可复现性
2. Ablation: model vs persona 方差分量量化
3. 下游任务：persona 分歧是否改善最终决策质量

## 执行数据

| 实验 | Trials | Errors | Tokens | Pre-reg | 结论 |
|------|--------|--------|--------|---------|------|
| E1a | 30 | 0 | 21,853 | `eebe2a31fb290860` | 天花板效应，结论无效 |
| E1b pretest | 90 | 0 | 39,404 | `429b32cc1774589c` | 筛选14个discriminating snippets |
| E1b main | 112 | 0 | 81,717 | `9c80bad72382d8c4` | κ=0.049, persona=costume diversity |
| **Total** | **232** | **0** | **142,974** | | |

## 文件清单

```
paper-validator/
├── experiment_e1_persona_decorrelation.py     # E1a 脚本
├── experiment_e1b_snippet_pretest.py          # E1b 预筛选脚本
├── experiment_e1b_cross_model.py              # E1b 主实验脚本
└── results/
    ├── e1_persona_decorrelation.json          # E1a 结果 (30 trials)
    ├── e1b_snippet_pretest.json              # E1b 预筛选结果 (90 trials)
    └── e1b_cross_model.json                  # E1b 主实验结果 (112 trials)
```
