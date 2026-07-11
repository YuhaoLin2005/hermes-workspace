# DeepSeek V4 Pro 成本优化实录

> 2026-07-11 · 林宇浩
>
> 研究计算基础设施从 Claude API 迁移至 DeepSeek V4 Pro 后的系统性参数调优。

---

## 背景

hermes-workspace 的 150 任务对照实验使用 DeepSeek V4 Pro（通过 Anthropic 兼容端点 `api.deepseek.com/anthropic`）。迁移后发现：(1) token 成本居高不下，(2) 缓存命中率极低。

根因分析识别了 **5 个成本放大器**，逐项修复。

---

## DeepSeek V4 Pro 关键特性

| 特性 | 数值 | 影响 |
|------|:--:|------|
| 上下文窗口 | **1M tokens** | 远大于 Claude 200K，不应过早压缩 |
| 最大输出 | 384K tokens | 限制输出 = 自废武功 |
| 缓存机制 | **自动前缀匹配**（非 Anthropic cache_control） | 前缀稳定 = 命中率高 |
| 缓存命中价 | $0.0036/M input（vs miss $0.435/M） | **120x 差价** |
| Flash 模型 | $0.14/M input（vs Pro $0.435/M） | 子任务 3x 便宜 |
| Thinking 模式 | 始终开启, reasoning_effort 可控 | high vs max 有显著 token 差异 |

---

## 优化历程

### 第 1 轮：止血（-50% 立即生效）

| 参数 | 旧值 | 新值 | 逻辑 |
|------|------|------|------|
| `CLAUDE_CODE_EFFORT_LEVEL` | max | high | max 产生 40-60% 额外 thinking token；DeepSeek high 推理质量足够 |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 32000 | 16000 | 减少输出缓冲区浪费 |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | 500000 | 200000 | 提前触发压缩，控制上下文膨胀 |

**Bug 发现**：env 变量 `AUTO_COMPACT_WINDOW` 被 top-level `autoCompactWindow: 600000` 覆盖——env 改动未生效。

### 第 2 轮：DeepSeek 能力匹配（匹配模型真实特性）

问题：第 1 轮优化基于 Claude 模型假设（200K 窗口、显式 cache_control）。DeepSeek 完全不同。

| 参数 | 第 1 轮值 | 第 2 轮值 | 逻辑 |
|------|------|------|------|
| `MAX_OUTPUT_TOKENS` | 16000 | **28000** | 释放 DeepSeek 384K 输出能力；多用 12K ≈ $0.01/请求 |
| `autoCompactWindow` | 200000 | **400000** | 利用 1M 窗口；减少 compact→前缀更稳定→缓存命中更高 |
| `SUBAGENT_MODEL` | inherit (pro) | **deepseek-v4-flash** | 子 agent 90% 是 grep/读文件，flash 完全够；cache miss 3x 便宜 |

### 第 3 轮：缓存命中率攻坚（根本原因修复）

**问题**：`ENABLE_TOOL_SEARCH: "auto:5"` → 每轮可能加载新工具 schema → 工具列表变化 → 前缀不匹配 → **整个缓存作废**。这是 GitHub Issue [#53132](https://github.com/anthropics/claude-code/issues/53132) 确认的 Bug。

**实测**：ToolSearch 解锁工具后，下一轮 `cache_read` 从 67K 暴跌到 15K，`cache_creation` 从 2K 暴涨到 62K。

| 参数 | 旧值 | 新值 | 逻辑 |
|------|------|------|------|
| `ENABLE_TOOL_SEARCH` | auto:5 | **false** | 全量加载工具 schema，前缀稳定→缓存可持续命中 |
| `ENABLE_PROMPT_CACHING_1H` | "1" | **删除** | DeepSeek 自动前缀缓存，cache_control 标记无效且干扰前缀匹配 |
| `CLAUDE_CODE_ATTRIBUTION_HEADER` | - | **"0"** | 屏蔽每请求变化的 billing header（已验证） |

### 其他修复

- **compact-counter 去重**：同一脚本在 SessionStart + PreCompact + PostCompact 三处触发 → 保留 SessionStart，删除重复
- **实验配置快照**：将优化前配置保存至 `experiment-config-snapshot.json`，确保补充实验可复现

---

## 最终配置

```
MODEL:        deepseek-v4-pro[1m]
EFFORT:       high
OUTPUT:       28K
COMPACT:      400K（可用对话空间 ~300K）
SUBAGENT:     deepseek-v4-flash
TOOL_SEARCH:  false（全量加载，不延迟）
CACHING:      自动前缀（无需标记）
BILLING:      已屏蔽动态头
```

---

## 关键洞察

1. **不要把 DeepSeek 当 Claude 用。** 1M 窗口 → compact 阈值应该更高而非更低；自动前缀缓存 → 稳定前缀比小 prompt 更重要。

2. **ToolSearch 是 DeepSeek 用户的隐形杀手。** 每解锁一个工具 → 下一轮缓存清零。`auto:5` 看似智能，实际在长 session 中不断触发缓存重建。

3. **缓存经济学**：cache hit $0.0036/M vs miss $0.435/M = 120x。优化方向不是减少 token 数，而是提高前缀稳定性。首轮多花 50K 加载工具，后续 50 轮全部命中 = 净赚。

4. **Flash 是 DeepSeek 的独特优势。** Claude 没有等价物。子 agent 用 Flash，主对话用 Pro——分层路由是免费的省钱方案。

---

## 后续

- [ ] 实测缓存命中率（需 API 响应中的 `cache_hit_tokens` 字段）
- [ ] 评估 `permafrost` 插件（确定性工具排序，适合 MCP 重用户）
- [ ] 持续监控 cost/session，建立基线
