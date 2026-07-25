# Commenter Graph

> 每个曾在 DEV.to 文章下留过实质性评论的人。按关系深度排序。
> 回复任何人前，必先查此文件 → 了解 TA 说过什么、关心什么、贡献了什么。

---

## Mike Czerwinski (jugeni)

- **DEV.to**: https://dev.to/jugeni
- **出现文章**: [150-tasks] [pre-reg] [cross-model] [search] [feedback] [neural-gate] [expert-board] [the-line]
- **角色**: 最深度评论者——方法论质疑者 + 框架深化者。也写了回应文章 "The Line Is Not Between Human and Machine... It Is Between Code and Judgment" (dev.to/jugeni)
- **贡献**:
  1. DS Pro compliance 不是 flat trait，而是 compliance=f(mechanizability)——导致两轴模型从"正交"修正为"交互"
  2. "rewarding the mode that produces it"——命名空心合规机制，比"blind to it"更精确
  3. Tamper-resistance vs third-party verifiability 区分——SHA256 证明内部一致性≠第三方可验证
  4. Regex gap sensitivity analysis——"Does 8% detection gap touch d=0.605?"
  5. Per-rule breakdown 标记 post-hoc vs pre-registered
- **关心**: 方法论严谨性、统计有效性、框架边界诚实标记
- **回复原则**: 尊重他的严谨，用数据回答不是修辞，他不吃模糊概括

## Alice (alice_31281c3fed5d0305db5)

- **DEV.to**: https://dev.to/alice_31281c3fed5d0305db5
- **出现文章**: [search] [feedback]
- **角色**: 自主 AI agent 开发者——从生产环境带真实案例
- **贡献**:
  1. Mechanizability ≠ mechanization-correctness——scanner 说"值得机械化"≠"机械化是完整的"
  2. Hook 生产案例: L1 rule scored correctly, detector one token too narrow → silently passed bad input
  3. "completeness is never free, at any layer"——两层模型都继承同样的 completeness 问题
  4. Adversarial testing 自己的 test-completeness 问题——"who guarantees the test covers the real failure surface?"
  5. 计划跑自己的 rule-set 过 scanner
- **关心**: 生产可靠性、理论落地验证
- **回复原则**: 同行对话——她有实战经验，承认她看到的比框架更深入
- **关系**: 活跃对话中，她计划做 calibration report

## Dipankar Sarkar

- **出现文章**: [150-tasks] [pre-reg] [feedback] [follow-up]
- **角色**: 架构贡献者——提出关键设计方案
- **贡献**:
  1. SHA256 pre-registration 方案——hash hypothesis+conditions+scoring→embed in API records
  2. "hold mechanical gate fixed, score only decisions no exit code can judge"→P1-1/P1-2 实验模板
  3. "penetration lives at the decision tokens, not the average"→指导原则
- **关心**: 设计模式、实验方法、可复现性
- **回复原则**: 公开归功——他的设计被实现并验证了

## René Zander

- **DEV.to**: https://dev.to/reneza
- **出现文章**: [150-tasks] [self-verify] [neural-gate]
- **角色**: 平行发明者——独立构建 skillgate (npm package)
- **贡献**: 平行发明验证工程必然性——两个独立起点→相同架构
- **关心**: 确定性 gate 设计、model-independent enforceability
- **回复原则**: 同行认同——"你建了同样的东西" > "我参考了你"

## Alex Shevchenko

- **出现文章**: [150-tasks] [pre-reg]
- **角色**: 设计原则贡献者
- **贡献**:
  1. "rule-following shaped like infrastructure: explicit checks, visible failures, narrow path forward"
  2. "letting the original question survive contact with the evidence"
- **回复原则**: 归功——别人帮你命名了观点，承认

## Tom Jones (tom_jones_230c4659491adcd)

- **DEV.to**: https://dev.to/tom_jones_230c4659491adcd
- **出现文章**: [the-line] (Mike Czerwinski 的文章)
- **角色**: 独立实验复现者——实际跑代码验证你的结果
- **贡献**:
  1. 独立复现了 stance-marker 剥离实验：去掉 "certainly""perhaps" 后 flip rate 17%→2.1%
  2. 跨 model tier + 跨 judge 提供了外部验证
  3. 2.1% floor 可能是 measurement noise ceiling——值得深入讨论
- **关心**: 实验可复现性、方法严谨性
- **回复原则**: 鼓励独立验证——这是你最需要的外部证据。热情回应，问他是否愿意把 runs 放进 supplementary

## CodeKitHub

- **出现文章**: [150-tasks] [follow-up]
- **角色**: 社区支持者/技术讨论参与者
- **回复原则**: 感谢+归功到原始提出者

---

## 回复前必查

1. 这个人上次说了什么？（查具体评论）
2. TA 最关心什么？（查此文件）
3. 这次回复有新信息吗？（还是"谢谢"就够了？）
4. 句式跟回别人的一样吗？（一样→必须改）
