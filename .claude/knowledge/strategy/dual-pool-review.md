# 双池对抗审查方法论 — 研究形式化

> 论文级形式化: dual-pool adversarial review as validated methodology
> 对应: PAPER.md section 3.4 或 section 5 Discussion

## 核心定义

双池审查 = 固定池(数字分身匹配, 收敛) + 随机池(联网搜索, 发散) + 管理员策展编排

## 形式化

Review(R, T, M) = CrossArrange(
  FixedPool(P_fixed, phi_user),
  RandomPool(P_random, search),
  orchestration in {exploit-exploit, exploit-explore, explore-exploit}
)

## 与 Prose Barrier 的关系

Prose Barrier: LLM 自审查不可靠, 因为生成和审查共享同一解码器分布

双池审查回应:
- 固定池通过不同人物角色扮演提供部分解耦
- 随机池通过联网搜索提供外部信息
- 但审查仍由 LLM 执行 -> 仍受 Prose Barrier 限制
- 双池减轻了 Prose Barrier, 但未消除 -> 实证的而非结构的解决方案

## 验证证据

| 证据 | 类型 | 来源 |
|------|------|------|
| R1 McCord: 10 issues | 实证 | PR 866 |
| R2 Catmull: 8 issues | 实证 | PR 866 |
| R3 Spolsky+DuVander: 3 issues | 实证 | PR 866 |
| 固定池找到的随机池找不到 | 架构验证 | PR 866 |
| 随机池找到的固定池想不到 | 架构验证 | PR 866 |
| 6个社区验证者独立复现 | 外部验证 | DEV.to 2026.07 |

## 局限性

1. 审查者仍是 LLM -> 受 Prose Barrier 限制
2. 固定池回声室风险
3. 随机池质量波动
4. token 成本 ~400K (deep模式)
5. 无形式化非散度证明 (vs Ratchet 2026)

## 与 2026 文献

| 方法 | 我们 | 类似工作 |
|------|------|---------|
| 多视角审查 | 固定池+随机池 | Self-Harness |
| 防退化 | 换池换人 | Ratchet |
| 反伪造 | 有源原则+置信度 | 独特 |
| 外部信号 | 搜索+社区 | Accumulated Rules |

---
*最后更新: 2026-07-22*
*交叉引用: [[../devto/warm]] [[content-pipeline]] [[dashboard]]*
