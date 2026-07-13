# hermes-workspace

> **AI agent 到底有没有在遵守规则？** — 五层验证架构，从机械门到漂移预测
>
> 林宇浩 · FAFU 空间信息与数字技术 2023 级
>
> 📄 [完整论文 (PAPER.md)](PAPER.md) · 📂 [实验数据](paper/experiment/) · 🔧 [独立验证工具 paper-validator](https://github.com/YuhaoLin2005/paper-validator) · 📝 [DEV.to](https://dev.to/yuhaolin2005) · [掘金](https://juejin.cn/user/4250072430682412)

---

## 一句话

**AI agent 长对话中遗忘规则、产出物无验证、自我认知漂移。** 现有方案依赖 AI 自评（不可靠），本文提出脱离模型解码器的机械校验体系——文件时间戳、正则匹配、进程退出码——任何模型、任何厂商均可复现。

---

## 论文三部曲

| Part | 内容 | 状态 | 文件 |
|:--:|------|:--:|------|
| **1** | 机械门：文件系统层校验，绕过 AI 自评偏差 | ✅ 已部署 + 实验 | [PAPER.md](PAPER.md) §3-§5 |
| **2** | 神经门：关键词回响→logprob差分→残差流探针 | 📐 v1 已部署, v2/v3 已设计 | [PAPER.md](PAPER.md) §6 |
| **3** | 因果编码：三段论格式改变注意力路由→推理深度 | 🗺️ 路线图, 初步证据 | [PAPER.md](PAPER.md) §7 |

---

## 实验概览

| 实验 | N | 设计 | 主要发现 | 状态 |
|------|:--:|------|------|:--:|
| Growth-log 回溯 | 34 sessions | 纵向编码 | 机械门接线前 55.9%→接线后 0.7% | ✅ |
| Causal Swap | 30 tasks | Between-subjects, DeepSeek V4 Pro | OR=11.0, p=0.0092 | ⚠️ 单评分者 |
| Format A/B | **150 tasks** | Between-subjects, 6 sessions | 99.3%合规, 天花板效应 | ⚠️ 需 GateGuard-OFF |
| Syllogism 交叉验证 | 4 sessions | 5规则全触发, 零违规 | 格式→推理深度因果链初步 | ⚠️ n 过小 |

> **诚实标注**：所有定量结果由作者单人评分、非盲法。κ=-0.14（盲审信度检查 n=8，未通过）。需独立第二评分者验证。

---

## 三层架构

```
L1 机械门 ✅ 已部署   文件时间戳/正则/exit 2 → 绕过 AI 自评
L2 神经门 📐 设计中  关键词回响→logprob差分→残差流探针
L3 因果编码 🗺️ 路线图 三段论格式→注意力路由→推理深度

核心洞见 (Prose Barrier)：
生成和验证共享同一解码器分布 P(token|context;θ)
→ AI 无法独立验证自身输出 → 机械校验是结构必需，非工程偏好
```

---

---

## DeepSeek V4 成本优化

研究基础设施从 Claude 迁移至 DeepSeek V4 Pro 后，针对 1M 上下文窗口 + 自动前缀缓存特性进行了系统优化：

| 参数 | 优化前 | 优化后 | 逻辑 |
|------|------|------|------|
| Reasoning Effort | max | high | DeepSeek high 足够，省 thinking token |
| autoCompactWindow | 600K | **400K** | 利用 1M 窗口, 减少 compact→保护缓存 |
| subagent model | inherit (pro) | **flash** | cache miss $0.14 vs $0.435 |
| ENABLE_TOOL_SEARCH | auto:5 | **false** | ToolSearch 每次摧毁缓存 (已知 Bug #53132) |
| ENABLE_PROMPT_CACHING_1H | "1" | 已删除 | DeepSeek 自动前缀缓存，不需要标记 |

详见 [DeepSeek 优化文档](paper/experiment/DEEPSEEK_OPTIMIZATION.md)

---

## 诚实局限

1. 单评分者 + 非盲法 — **κ=-0.14**，论文最致命缺陷
2. 无安慰剂对照 — 观测效应可能归因于 token 数量
3. GateGuard 天花板效应 — 验证了 L1 而非 L3
4. 文献检索依赖自主搜索 + AI 辅助
5. 独立完成，无导师指导

---

## 快速导航

| 你要看 | 点这里 |
|------|------|
| 完整论文 | [PAPER.md](PAPER.md) |
| 5 分钟摘要 | [paper/professor-meeting-onepager.md](paper/professor-meeting-onepager.md) |
| 实验数据 | [paper/experiment/](paper/experiment/) |
| 实验配置快照 | [paper/experiment/experiment-config-snapshot.json](paper/experiment/experiment-config-snapshot.json) |
| DeepSeek 优化 | [paper/experiment/DEEPSEEK_OPTIMIZATION.md](paper/experiment/DEEPSEEK_OPTIMIZATION.md) |
| AI 模拟审稿报告 | [paper/reviewer-report-2026-07-11.md](paper/reviewer-report-2026-07-11.md) |
| DEV.to 技术文章 | [dev.to/yuhaolin2005](https://dev.to/yuhaolin2005) |

---

## 许可

MIT
