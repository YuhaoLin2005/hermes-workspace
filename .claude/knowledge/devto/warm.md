# DEV.to Warm (≤60d, paper-related, low comments)
> 按需加载标题+finding。回复引用时读全文。

```yaml
articles:
  - slug: logprob-safe
    title: "I Told My AI 'You're Safe to Say I Don't Know.' Then I Measured What Changed"
    url: https://dev.to/yuhaolin2005/i-told-my-ai-youre-safe-to-say-i-dont-know-then-i-measured-what-changed-with-logprobs-986
    date: 2026-07-12
    domain: experiment
    claims: [claim-3]
    commenters: []
    finding: "L0 safety prompt → logprob measurement validation"
    status: active

  - slug: zero-effect
    title: "My Experiment Showed Zero Effect. A Statistician Told Me My Measurement Was Broken."
    url: https://dev.to/yuhaolin2005/my-experiment-showed-zero-effect-a-statistician-told-me-my-measurement-was-broken-4g26
    date: 2026-07-12
    domain: experiment
    claims: [claim-4]
    commenters: []
    finding: "n=21 underpowered for d≤0.3; null result可能是测量问题"
    status: active

  - slug: drift-metric
    title: "My Loss Went Down, But My Model Still Broke — So I Built a Drift Metric"
    url: https://dev.to/yuhaolin2005/my-loss-went-down-but-my-model-still-broke-so-i-built-a-drift-metric-e8f
    date: 2026-07-08
    domain: architecture
    claims: []
    commenters: []
    finding: "L4 drift predictor design rationale; 8-feature 0-100 scorer"
    status: active

  - slug: forget-protocol
    title: "I Open-Sourced the Protocol That Stops AI From Forgetting Who You Are"
    url: https://dev.to/yuhaolin2005/i-open-sourced-the-protocol-that-keeps-my-ai-from-forgetting-who-i-am-4pp
    date: 2026-07-05
    domain: architecture
    claims: []
    finding: "身份持久化协议→自指环前身"
    status: active

  - slug: zero-output
    title: "Your AI Agent's Best Work Produces Zero Output — And That's the Point"
    url: https://dev.to/yuhaolin2005/your-ai-agents-best-work-produces-zero-output-and-thats-the-point-5b3a
    date: 2026-07-04
    domain: architecture
    claims: []
    finding: "零输出=质量信号; 机械门哲学基础"
    status: active

  - slug: self-verifiable
    title: "I Made My AI Rules Self-Verifiable. Now They Catch Their Own Violations."
    url: https://dev.to/yuhaolin2005/i-made-my-ai-rules-self-verifiable-heres-how-19ea
    date: 2026-07-03
    domain: config
    claims: [claim-2]
    finding: "自验证规则→L1 gate前身"
    status: active

  - slug: search
    title: "Search Didn't Make Your LLM Dumber. Unweighted Context Did."
    url: https://dev.to/yuhaolin2005/your-web-search-is-making-the-model-dumber-4dj9
    date: 2026-07-03
    domain: experiment
    claims: []
    commenters: [alice, mike]
    finding: "Search quality drop源于未加权上下文，非检索本身"
    status: active

  - slug: dual-pool
    title: "I Built a Dual-Pool Adversarial Review System for AI Agents — And It Actually Works"
    url: https://dev.to/yuhaolin2005/i-built-a-dual-pool-adversarial-review-system-for-ai-agents-and-it-actually-works-595j
    date: 2026-06-29
    domain: architecture
    finding: "双池对抗审查; 固定池+随机池交叉验证"
    status: active

  - slug: feedback-loop
    title: "How I Built a File-Timestamp-Based Feedback Loop to Enforce AI Output Quality"
    url: https://dev.to/yuhaolin2005/how-i-built-a-file-timestamp-based-feedback-loop-to-enforce-ai-output-quality-1ibc
    date: 2026-07-07
    domain: config
    finding: "文件时间戳→质量门→L1 QualityGate前身"
    status: active

  - slug: starter-kit
    title: "I Packed DeepSeek V4 + Claude Code Into a Starter Kit. Clone It and Ship."
    url: https://dev.to/yuhaolin2005/i-packed-deepseek-v4-claude-code-into-a-starter-kit-clone-it-and-ship-13dn
    date: 2026-07-05
    domain: tutorial
    finding: "一键部署; DeepSeek+Claude Code集成"
    status: active

  - slug: self-healing
    title: "I Built a Closed-Loop Self-Healing System for My AI Config — By Accident"
    url: https://dev.to/yuhaolin2005/i-built-a-closed-loop-self-healing-system-for-my-ai-config-by-accident-51m4
    date: 2026-07-04
    domain: config
    finding: "配置自愈系统→Strange Loop前身"
    status: active

  - slug: single-modal
    title: "Single-Modal LLMs Have a Blind Spot. Here's How to Fix It."
    url: https://dev.to/yuhaolin2005/single-modal-llms-have-a-blind-spot-heres-how-to-fix-it-2ogd
    date: 2026-06-28
    domain: architecture
    finding: "单模态LLM盲点分析"
    status: active

  - slug: open-source-flywheel
    title: "The Open Source Flywheel: How I Turn Personal AI Scripts Into Merged PRs"
    url: https://dev.to/yuhaolin2005/the-open-source-flywheel-how-i-turn-personal-ai-scripts-into-merged-prs-528d
    date: 2026-07-06
    domain: tutorial
    finding: "个人脚本→开源PR的工作流方法论"
    status: active

  - slug: 150-tasks
    title: "I Ran 150 Tasks to Test If AI Agents Follow Rules — The Answer Surprised Me"
    url: https://dev.to/yuhaolin2005/i-ran-150-tasks-to-test-if-ai-agents-follow-rules-the-answer-surprised-me-2670
    date: 2026-07-11
    domain: experiment
    claims: [claim-2, claim-7]
    commenters: [mike, dipankar, rene, alex, codekithub]
    numbers: "55.9%→0.7%; 19/19 behavioral tests; 150 tasks × 2 formats"
    finding: "Mechanical gate eliminates format effect; ceiling effect IS the finding"
    status: active

  - slug: neural-gate
    title: "I Built a Neural Gate for My AI Agent — Layer 2 of Self-Verification"
    url: https://dev.to/yuhaolin2005/i-built-a-neural-gate-for-my-ai-agent-layer-2-of-self-verification-6o2
    date: 2026-07-10
    domain: experiment
    claims: [claim-3, claim-5, claim-7]
    commenters: [mike, rene]
    numbers: "d=+0.578 BF=282k; 32/40 probes favoring syllogistic"
    finding: "Logprob-based L2 gate; decision-token targeting; L1-visibility synergy"
    status: active

  - slug: self-verify
    title: "AI Agents Can't Self-Verify — And That's a Structural Constraint, Not a Bug"
    url: https://dev.to/yuhaolin2005/ai-agents-cant-self-verify-and-thats-a-structural-constraint-not-a-bug-1d7l
    date: 2026-07-10
    domain: architecture
    claims: [claim-1]
    commenters: [rene]
    numbers: "Prose Barrier identified; 平行发明(René Zander/skillgate)"
    finding: "Self-verification is structurally unreliable — shares generation distribution"
    status: active

  - slug: meta-cognition
    title: "Meta-Cognition Is the Future of AI Personalization — A 4-Quadrant Framework to Build It"
    url: https://dev.to/yuhaolin2005/meta-cognition-is-the-future-of-ai-personalization-a-4-quadrant-framework-to-build-it-5fki
    date: 2026-07-09
    domain: architecture
    claims: []
    commenters: []
    numbers: "4-quadrant framework"
    finding: "元认知框架——self-model的理论基础"
    status: active

  - slug: self-referential
    title: "I Built a Self-Referential AI System. Then Anthropic Discovered the Same Architecture in Claude."
    url: https://dev.to/yuhaolin2005/i-built-a-self-referential-ai-system-then-anthropic-discovered-the-same-architecture-in-claude-3m73
    date: 2026-07-07
    domain: architecture
    claims: []
    commenters: []
    numbers: "Strange Loop; 平行发现 Anthropic J-Space"
    finding: "自指环架构——独立发现后被Anthropic论文验证"
    status: active

  - slug: feedback
    title: "Your Feedback Made This Better — Here's What Changed"
    url: https://dev.to/yuhaolin2005/your-feedback-made-this-better-heres-what-changed-4ol2
    date: 2026-07-13
    domain: experiment
    claims: [claim-2, claim-3, claim-4]
    commenters: [mike, dipankar, alice]
    numbers: "5 community-driven improvements"
    finding: "Community feedback→paper improvements documented"
    status: active

  - slug: follow-up
    title: "Follow-Up: Decision-Token Measurement, Format-as-Fallback, and What Changed"
    url: https://dev.to/yuhaolin2005/follow-up-decision-token-measurement-format-as-fallback-and-what-changed-18jo
    date: 2026-07-13
    domain: experiment
    claims: [claim-8]
    commenters: [dipankar, codekithub]
    numbers: "code+gate mech=5.0 reason=4.2; prose+gate reason=4.42"
    finding: "Format×Gate interaction; prose format consistently better for reasoning"
    status: active
```
*tier: warm | count: 20 | 2026-08-14*
