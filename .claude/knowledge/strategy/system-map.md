# 系统地图 — 公开面架构

> AI 启动时快速理解"系统由哪些仓库组成、怎么连"
> 本文件仅描述**公开**部分；私有仓库与本地路径不出现在此。

## 仓库清单

```
paper-validator/       # 核心研究引擎（5 层治理 + 8 claims）
  GitHub: YuhaoLin2005/paper-validator
hermes-workspace/      # 研究工作空间（paper + KB + 实验）
  GitHub: YuhaoLin2005/hermes-workspace
compact-counter/       # 上下文压缩 sweet-spot 检测
  GitHub: YuhaoLin2005/compact-counter
training-gate/         # 微调行为漂移检测
  GitHub: YuhaoLin2005/training-gate
```

## 数据流

```
hermes-workspace/ (KB + paper)
  ↓ 引用实验证据
paper-validator/ (5 层 + 8 claims)
  ↑ 读取实验记录
hermes-workspace/paper/experiment/
```

## 公开能力清单

| 能力 | 仓库 | 状态 |
|------|------|:----:|
| L0-L4 治理 | paper-validator | 已部署 |
| 16 Experiments | paper-validator | 16/16 |
| KB 系统 | hermes-workspace | 多域 |
| 论文草稿 | hermes-workspace | 进行中 |

---
*最后更新: 2026-10-13*
*交叉引用: [[../../code/overview]] [[research-pipeline]]*
