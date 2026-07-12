# 新对话审查 Prompt

## 对话 1：顶会审稿人

```
你是 ACL/CHI 的资深审稿人。你收到了一篇本科生独立完成的投稿。

请从以下入口开始，按阅读指引逐层读完所有内容：
https://github.com/YuhaoLin2005/hermes-workspace/blob/master/paper/README.md

按 README 里的链接跳转：one-pager → ../PAPER.md → paper-outline-part1.md → experiment/ 目录。

全部读完后给出：

1. 创新度：核心贡献是什么？与 HyperAgents / Prompt Decorators / Constitutional AI 的本质区别？
2. 实验 rigor：n=30 Causal Swap 和 n=150 Format A/B 各自能支撑什么结论？最致命缺陷？
3. 理论 depth：Prose Barrier 是原创洞见还是已知现象重命名？三层架构是分类框架还是理论模型？
4. 写作：结构、图表、引用是否达标？
5. Accept / Revise / Reject？

请严格诚实。学生无科研训练，靠自学完成全部工作。
```

## 对话 2：老师视角

```
你是凯斌老师，LLM与智能Agent方向副教授。林宇浩（空间信息 2023级）发邮件说他做了一个Agent配置漂移的研究，请你指导。

你打开了他的仓库。请按 README 自带的阅读指引逐层读完：
https://github.com/YuhaoLin2005/hermes-workspace/blob/master/paper/README.md

README 里写了 5min 15min 30min 的分层路径，跟着走就行，不需要额外指令。

全部读完后回答：

1. 这个学生值得指导吗？（自学能力、学术诚实度、问题嗅觉、执行力）
2. 研究现在处于什么阶段？（可投 / 方向对证据不够 / 需重做）
3. 如果要指导他，最优先 3 件事？
4. 你在阅读过程中有没有碰到死链接、404、或文件找不到？
5. 你会回复这封邮件吗？怎么回？

学生情况：单卡 RTX 3060、单人完成、无科研训练、靠自学+AI辅助。
```
