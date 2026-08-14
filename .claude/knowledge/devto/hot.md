# DEV.to Hot Articles (≤14d + active commenters + paper claims)
> 启动加载。格式: YAML-in-Markdown per _schema.md

```yaml
articles:
  - slug: audit-ctbv
    title: "I Discovered AI Agents Can't Self-Verify. The Real Problem Is Much Bigger."
    url: https://dev.to/yuhaolin2005/i-discovered-ai-agents-cant-self-verify-the-real-problem-is-much-bigger-2jb6
    date: 2026-07-26
    domain: experiment
    claims: [claim-1, claim-2, claim-3, claim-4, claim-5, claim-8, claim-9]
    commenters: [mike, dipankar, max, rene]
    numbers: "38 gates, 9 sessions, 339 entries, 87% noise; κ = 0.00; DPO 150 pairs"
    finding: "CTBV: orthogonal blind spots → joint error = 0; working gates check what LLMs can't fake"
    status: active

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

```

*tier: hot | count: 5 | updated: 2026-08-14 | expert-board/cross-model 回复草稿已备（reply-drafts-2026-08-14.md），待 voice gate*
