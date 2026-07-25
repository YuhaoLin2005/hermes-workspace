# DEV.to Reply Log

> 每条评论的回复状态追踪。Session 启动扫描 status=unread → 提醒数量。
> Importer: routing.md, devto-copilot. Schema: YAML-in-Markdown.

```yaml
replies:
  # === cross-model ===
  - article: cross-model
    commenter: mike
    thread: "two-axis-framing"
    date: 2026-07-18
    status: replied
    reply_
  # === expert-board (NEW article) ===
  - article: expert-board
    commenter: mike
    thread: "named-principle-anchor"
    date: 2026-07-22
    status: unread
    reply_summary: "Named-principle decorelates premise but not inference. 33 personas agreeing = one engine in 33 mirrors. Cross-model Carmack test is the real independence metric."
    voice_checked: no

  # === cross-model (NEW) ===
  - article: cross-model
    commenter: james-sanderson
    thread: "scanner-vs-compliance"
    date: 2026-07-21
    status: unread
    reply_summary: "Scanner scores checkability but compliance is model property. DS Pro compliance=f(mechanizability). Did cross-model gradient reshuffle?"
    voice_checked: no

  # === pre-reg (NEW) ===
  - article: pre-reg
    commenter: mike
    thread: "tamper-resistance-vs-verifiability"
    date: 2026-07-20
    status: replied
    reply_summary: "SHA256 = tamper-resistant not tamper-proof. Hash in provider-timestamped record. But third-party verifiability needs API-retained records."
    voice_checked: no

  - article: pre-reg
    commenter: alex-shev
    thread: "sha256-hardens"
    date: 2026-07-20
    status: replied
    reply_summary: "SHA256 makes pre-reg harder to hand-wave. Hash→other people can verify against the run."
    voice_checked: no

  - article: pre-reg
    commenter: alex-shev
    thread: "question-survives-evidence"
    date: 2026-07-19
    status: replied
    reply_summary: "Pre-reg protects original question from being rewritten into something easier."
    voice_checked: no

  # === follow-up (NEW) ===
  - article: follow-up
    commenter: alex-shev
    thread: "measurement-changed-design"
    date: 2026-07-20
    status: replied
    reply_summary: "Measurement that changes design = valuable kind. Otherwise dashboard proves observation after decisions."
    voice_checked: no

  # === 150-tasks (NEW) ===
  - article: 150-tasks
    commenter: alex-shev
    thread: "mechanizability-scanner-next"
    date: 2026-07-20
    status: replied
    reply_summary: "Mechanizability scanner forces rules to become observable. Tricky: partial gateability = need to say what is checked vs what still needs review."
    voice_checked: no

  - article: 150-tasks
    commenter: alex-shev
    thread: "rules-as-infrastructure"
    date: 2026-07-19
    status: replied
    reply_summary: "Rules reliable when they stop being vibes and start being infrastructure. Boundary should not depend on mood."
    voice_checked: no

  - article: 150-tasks
    commenter: mike
    thread: "rewarding-mode-sharper-name"
    date: 2026-07-19
    status: replied
    reply_summary: "'Rewarding the mode' sharper than 'blind to it.' Fix = make metric ungamable by orthogonal mode."
    voice_checked: no

  # === cross-model (NEW) ===
  - article: cross-model
    commenter: mike
    thread: "two-axis-ds-pro-pattern"
    date: 2026-07-19
    status: replied
    reply_summary: "DS Pro compliance=f(mechanizability): high T1/T2(100%), low T3/T4/T5(0-42.5%). Third behavioral type: judicious vs obedient vs inattentive. Axes not fully orthogonal for every model."
    voice_checked: no

  # === search (NEW deeper) ===
  - article: search
    commenter: alice
    thread: "no-last-layer-closed"
    date: 2026-07-19
    status: replied
    reply_summary: "Alice: 'no last layer, only question staying open' is cleaner statement. Most alive exchange in a while. Will bring report when real."
    voice_checked: no

  - article: search
    commenter: alice
    thread: "mechanization-correctness"
    date: 2026-07-19
    status: replied
    reply_summary: "mechanizability != mechanization-correctness. My L1 hook had correct score but failed—check was too narrow (required 2 tokens, real failure emitted 1). Completeness never free at any layer."
    voice_checked: no

summary: "DS Pro compliance=f(mechanizability). Flash hollow, Qwen low. Confirmed two-axis model."
    voice_checked: yes

  # === pre-reg ===
  - article: pre-reg
    commenter: mike
    thread: "SHA256-in-API-record"
    date: 2026-07-18
    status: replied
    reply_summary: "SHA256 in provider-timestamped record = tamper-evident, not just tamper-proof."
    voice_checked: yes

  # === 150-tasks ===
  - article: 150-tasks
    commenter: mike
    thread: "rewarding-the-mode"
    date: 2026-07-18
    status: replied
    reply_summary: "Rewarding the mode > blind to it. Changes fix target."
    voice_checked: yes

  # === the-line (Mike's article) ===
  - article: the-line
    commenter: tom
    thread: "stance-marker-replication"
    date: 2026-07-19
    status: replied
    reply_summary: "Tom independently replicated 17%→2.1% floor after stripping markers."
    voice_checked: yes

  - article: the-line
    commenter: tom
    thread: "model-tier-swap"
    date: 2026-07-19
    status: replied
    reply_summary: "Cross-model-tier + cross-judge validation of your results."
    voice_checked: yes

  - article: the-line
    commenter: mike
    thread: "floor-correction"
    date: 2026-07-19
    status: replied
    reply_summary: "Floor correction honest. Persistent-flipper settles boundary noise."
    voice_checked: yes

  # === search ===
  - article: search
    commenter: alice
    thread: "production-cases"
    date: 2026-07-19
    status: replied
    reply_summary: "Alice shared 2 production hook-failure cases. Case1: model-tier swap. Case2: adversarial test coverage."
    voice_checked: yes

  - article: search
    commenter: alice
    thread: "no-last-layer"
    date: 2026-07-19
    status: replied
    reply_summary: "Alice: second layer leaks. You: no last layer, only open question."
    voice_checked: yes

summary:
  total_tracked: 20
  unreplied: 2
  last_sync: 2026-07-22
```

## 机制

| 事件 | 动作 |
|------|------|
| 新评论到达 | 加条目 `status: unread` |
| 回复发出 | 改 `status: replied` + 填 `reply_summary` |
| 过声音门 | 标 `voice_checked: yes` |
| Session 启动 | 扫 `unread` → 提醒 |

---
*最后更新: 2026-07-22*
*交叉引用: [[commenters]] [[hot]]*
