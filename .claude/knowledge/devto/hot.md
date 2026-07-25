# DEV.to Hot Articles (≤14d + active commenters + paper claims)
> 启动加载。格式: YAML-in-Markdown per _schema.md

```yaml
articles:
  - slug: cross-model
    title: "Your AI Gate Works Perfectly — Until You Switch Models"
    url: https://dev.to/yuhaolin2005/your-ai-gate-works-perfectly-until-you-switch-models-4bf0
    date: 2026-07-18
    domain: experiment
    claims: [claim-9]
    commenters: [mike]
    numbers: "DS Pro 5/5→2/5; DS Flash 100% hollow; Qwen T1=40% T5=0%"
    finding: "Gateability = rule_structure × model_capability (2D space)"
    status: active

  - slug: pre-reg
    title: "I Pre-Registered a Hypothesis. 600 API Calls Later, the Data Killed It."
    url: https://dev.to/yuhaolin2005/i-pre-registered-a-hypothesis-600-api-calls-later-the-data-killed-it-1aec
    date: 2026-07-15
    domain: experiment
    claims: [claim-8]
    commenters: [mike, dipankar, alex]
    numbers: "d=0.605; H1 NOT_CONFIRMED; SHA256 pre-reg; tamper≠third-party"
    finding: "Pre-reg killed hypothesis; prose+gate=best combo (4.42/5)"
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

  - slug: search
    title: "Search Didn't Make Your LLM Dumber. Unweighted Context Did."
    url: https://dev.to/yuhaolin2005/your-web-search-is-making-the-model-dumber-4dj9
    date: 2026-07-03
    domain: experiment
    claims: []
    commenters: [alice, mike]
    numbers: ""
    finding: "Search quality drop源于未加权上下文，非检索本身"
    status: active

  - slug: expert-board
    title: "Stop Using Generic AI Review. Build Your Own Board of Experts."
    url: https://dev.to/yuhaolin2005/stop-using-generic-ai-review-build-your-own-board-of-experts-196n
    date: 2026-07-21
    domain: architecture
    claims: []
    commenters: [mike]
    numbers: "33 persona独立幻觉; 跨模型decorrelation测试"
    finding: "33个persona同意≠33个独立判断；命名原则锚定→去关联前提→真独立性需跨模型验证"
    status: active

  - slug: dpo-causal
    title: "I DPO-Trained a Model to Prefer Causal Reasoning. The Base Model Already Did — It Just Couldn't Act On It."
    url: https://dev.to/yuhaolin2005/i-dpo-trained-a-model-to-prefer-causal-reasoning-the-base-model-already-did-it-just-couldnt-act-1kip
    date: 2026-07-24
    domain: experiment
    claims: []
    commenters: []
    numbers: "SYLL=0.941 IMP=0.750 TOKCTRL=0.667 COTCTRL=1.048"
    finding: "Base model already encodes causal reasoning—DPO unlocks action, doesn't teach from scratch; format-control gap reveals DPO selects CoT over token-level"
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
```

*tier: hot | count: 12 | updated: 2026-07-24*
