# 系统地图 — 全量仓库+管线+能力清单

> AI 启动时快速理解"我有什么、在哪、怎么连"
> 加载: MEMORY.md WARM trigger "论文对比/研究方向" 或 "系统架构"

## 仓库清单

```
C:/Users/86131/
├── paper-validator/               # 核心研究引擎 (5层+8 claims+MCP)
│   GitHub: YuhaoLin2005/paper-validator
├── Desktop/digital-twin-trainer/  # 数字分身训练 (MergeKit→QLoRA→DPO)
│   GitHub: YuhaoLin2005/digital-twin-trainer
├── hermes-workspace/              # 研究工作空间 (paper+KB+草稿)
│   GitHub: YuhaoLin2005/hermes-workspace
├── .claude/                       # 全局配置+身份 (SOUL/INTERFACE/BODY)
│   GitHub: YuhaoLin2005/agent-self-model
└── .claude/projects/.../memory/   # 记忆系统 (self-model+双池+五库)
```

## 数据流

```
.claude/ (SOUL/INTERFACE/BODY)
  ↓ 启动加载
hermes-workspace/ (KB+paper)
  ↓ 引用实验证据
paper-validator/ (5层+8 claims)
  ↕ 待连接
digital-twin-trainer/ (4阶段训练)
  ↑ 读取 .claude/ (Phase2数据提取)
  ↑ 读取 .claude/memory/ (self-model+growth-log)
```

## 跨仓库依赖缺口

1. paper-validator ↔ digital-twin-trainer: 无代码级连接
2. strange_loop: 无 diff 计算、无 rollback
3. 失败→规则编译: 未实现 (vs SEED)
4. 盲评分: 未做 (阻塞投稿)

## 能力清单

| 能力 | 仓库 | 状态 |
|------|------|:----:|
| L0-L4 治理 | paper-validator | ✅ |
| 16 Experiments | paper-validator | ✅ 16/16 |
| 模型融合 | digital-twin-trainer | ✅ |
| QLoRA | digital-twin-trainer | ✅ (loss 8.11→0.77) |
| DPO | digital-twin-trainer | ❌ (下一阶段) |
| KB 系统 | hermes-workspace | ✅ 5→6 domains |
| 双池审查 | .claude/memory | ✅ v3.0 |
| 论文草稿 | hermes-workspace | ⚠️ |

---
*最后更新: 2026-07-22*
*交叉引用: [[../code/overview]] [[../training/overview]] [[dashboard]] [[research-pipeline]]*
