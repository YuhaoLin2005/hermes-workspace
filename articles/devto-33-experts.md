# Stop Using Generic AI Review. Build Your Own Board of Experts.

You finish a piece of work. You ask AI to review it. It says "looks good." You publish.

It wasn't good. You had no way to know.

That's the problem with adversarial review. You tell the AI to "act as a security reviewer" or "play the skeptic." It gives you feedback. Some is useful. Most of it you can't trust — not because the AI is malicious, but because you have no idea *why* it said what it said.

"Your experiment design looks solid." Based on what?

"Consider adding error handling." Which errors? Why here? Is this real analysis, or did the model just pattern-match "code review → suggest error handling"?

When you work alone — no team, no code review, no second set of eyes — this is worse than no review. Generic review gives you **confidence without knowing if you should be confident.** You think you've been reviewed. You haven't.

I hit this wall hard. My work involves measuring whether AI agents follow rules — niche, quantitative, easy to get wrong. Before I built what I'm about to describe, I'd design an experiment, run 200 API calls, discover a design flaw on iteration 3, and redo everything. I wasted approximately 40% of my API calls on rework that could have been caught before iteration 1.

I don't waste those calls anymore. Here's what changed.

---

## Named Experts > Abstract Roles

Instead of asking for "a security reviewer," give the AI a real person's name. A real person with documented, searchable, citeable principles.

**Ken Thompson**, not "security expert." His 1984 Turing Award lecture *Reflections on Trusting Trust* gives you an actual analytical lens — supply chain risks, trust boundaries in third-party code, input validation at trust boundaries. Not a vibe. A documented framework you can go read yourself.

**Don Norman**, not "UX reviewer." *The Design of Everyday Things.* Affordances, signifiers, conceptual models. Chapter 1. Searchable. Verifiable.

**Torvalds** on "good taste" — eliminating special cases rather than handling them. TED 2016. He walks through a linked-list deletion example where the refactored version has zero conditionals. That's not an opinion. That's a specific, citeable criterion you can apply to your own code.

When these people review your work, the feedback anchors to something outside the model's generation loop. Carmack doesn't say "consider optimizing this" — he flags that you're speculating about performance without measurements, because his documented principle is "measure first, optimize second." You can verify that principle. You can decide whether it applies here.

**This is the anti-fabrication discipline.** Every attribution carries a confidence level:

- `high` — I can show you the source. Torvalds' TED talk. Thompson's Turing lecture. The page number.
- `moderate` — consistent with their documented work, but I can't pin the exact quote.
- `low` — my inference. Labeled as such. Treated as a suggestion, not analysis.

The rule: if I can't reach at least `moderate` confidence, I drop the persona. Better fewer real experts than more fabricated ones. The model will happily invent a Carmack quote that sounds plausible. Don't let it.

---

## 33 Experts Is Useless Without a Dispatcher

I built a pool of 33 people across 6 domains. Engineers, product thinkers, designers, writers. Each with documented principles, real sources, confidence levels.

And then I immediately hit the real problem.

Having 33 experts is meaningless if you have to manually decide who reviews what every time. You'll do it twice and stop. The bottleneck isn't the quality of the reviewers — it's the **dispatch system.**

So I built a routing table. Not a chatbot. Not an agent. A single YAML file:

```yaml
routes:
  - id: experiment-design
    triggers: ["design experiment", "validate methodology"]
    load_kb: [kb-experiments, kb-paper-claims]
    design_review:
      roles: [Carmack, Hickey, Schell]
      focus: "method + complexity + clarity"

  - id: writing-review
    triggers: ["draft article", "pre-publish review"]
    load_kb: [kb-articles, kb-voice-reference]
    voice_review:
      roles: [Zinsser, Orwell, Graham]

  - id: code-review
    triggers: ["PR ready", "refactor complete"]
    code_review:
      roles: [Thompson, Torvalds, Beck]
      focus: "trust boundaries + taste + testability"
```

I never manually pick who reviews what. I finish something, the routing table fires, the right experts load with the right context. Zero cognitive overhead.

Before the routing table: I used the expert panel maybe once a week, when I remembered. After: it fires on every finished piece of work, every session, without me thinking about it. That's the difference between "I have a cool idea" and "this is part of how I work."

---

## The Pool Is Two Pools, Not One

The routing table dispatches from two separate pools.

**Fixed pool** — 33 vetted people. Documented principles. Confidence-rated. They give me depth. After 10 reviews with the same expert, they know your patterns. The feedback gets sharper. Hickey on your third experiment design catches things he missed on your first.

**Random pool** — web search for people I've never heard of. Each session, one round: search `"[domain] engineering philosophy"` → find an unfamiliar name → apply their lens to my work. This breaks echo chambers. Once, a random-pool round caught a design flaw both fixed-pool rounds missed. If I only had the fixed pool, I'd never have seen it.

The rule is simple: fixed pool guarantees the floor. Random pool raises the ceiling. They're orchestrated, not alternatives.

---

## The Mechanical Gate: Don't Trust AI to Remember Rules

You can build the most beautiful routing table in the world. It won't matter if three weeks later, your knowledge base is stale, your routing rules have rotted, and nobody noticed.

I don't trust AI to remember what to enforce. I trust code.

A Python script (`_check_kb.py`) runs at the end of every session. Knowledge base older than its source? Hard fail. Routing rule unused for 30+ days? Flagged. Session ended without updating the dashboard? Blocked.

This sounds small. It's not. Before the mechanical gate, I'd discover stale KB entries weeks after they went bad — usually when an expert gave feedback based on outdated context and I didn't realize until I'd already acted on it. That doesn't happen anymore.

**Code enforces rules. AI follows them. Never let AI enforce rules on itself.**

---

## Does This Actually Work?

In June 2026, I submitted a pull request to `alirezarezvani/claude-skills`. The concept was named-persona adversarial review. The PR had structural issues — wrong directory, missing anti-fabrication discipline. It got closed.

The maintainer didn't just close it. He wrote: **"The concept is yours."** Then he opened PR #867, hardened the implementation — added `persona_principles.md` with citeable sources and confidence levels for every persona — and merged it with `Co-authored-by: YuhaoLin2005`.

Someone with no reason to credit me, crediting me.

That's the external validation I have. Not a benchmark score. Not a p-value. One real person looked at the idea, decided it was worth building, and put my name on it.

I haven't run a controlled experiment comparing named-expert review against generic prompts. The Prose Barrier makes self-scoring unreliable — the same model generating the review can't also be the one grading it. A proper within-subject double-blind design needs more care than I've given it so far. I'm working on it. When I have data, I'll report back — whether it confirms the hypothesis or kills it.

---

## Build Yours. One Hour.

**Step 1: Let the AI learn your context first.**

Don't name anyone yet. Run a few real sessions. Let the system see your stack, your projects, your recurring decisions. A knowledge base without context is just a famous name attached to generic feedback.

**Step 2: Find your people. Search, don't remember.**

Open a search engine. Type: `"[your domain] engineering philosophy principles"` or `"[your field] design thinking framework."` Read the actual sources — talks, books, papers. Don't trust AI summaries.

Here's a real example. I searched `"software architecture simplicity principles"` and found Rich Hickey's "Simple Made Easy" (Strange Loop 2011). In that talk, he distinguishes *simple* (objective — one braid, one responsibility) from *easy* (subjective — familiar, within reach). That distinction became my lens for reviewing whether complexity in my code was essential or accidental.

One person. One principle. One source.

Then: confidence-level it. Can I verify Hickey said this? Yes — Strange Loop 2011 keynote, transcribed. `high`. Write that down.

Can't verify? Drop them. Keep going until you have 5-10 people across the domains you work in.

**Step 3: Route them.**

```yaml
my-design-review: [your-edge-case-person, your-simplicity-person]
my-writing-review: [your-clarity-person, your-style-person]
my-code-review: [your-correctness-person, your-architecture-person]
```

Three scenarios. Two experts each. Five lines.

Add a check script — verify your KB hasn't gone stale. Three lines of Python. Run it when you finish a session.

That's it. One file for the pool. One file for routing. One script for the gate.

---

## What Will Go Wrong

**Hallucinations still happen.** Named principles reduce fabrication significantly — but don't eliminate it. Confidence levels exist for a reason. `low` = suggestion only. Label it or drop it.

**You'll pick wrong people.** Someone sounds right on paper, gives shallow feedback in practice. Swap them. The pool is alive. Revisit it monthly.

**Maintenance is real.** Knowledge bases go stale. Work directions change. The mechanical gate catches staleness — it doesn't fix content. That's still you.

**The real risk: outsourcing judgment.** An expert panel tells you what Torvalds or Norman or Carmack would flag. Only you can decide whether that flag matters for your codebase, your users, your constraints. If you stop thinking and start blindly trusting — you've built a system that's better at producing confident-sounding wrong answers than a generic prompt. That's worse, not better.

The best thing this system does isn't giving you answers. It's making you harder to fool.

---
## Start Now

1. `expert-pool.md`. One person. One principle. One source. Confidence level next to it.
2. Three scenarios you hit every week. Two experts each.
3. One script that checks your KB isn't stale. Run it at session end.

My routing table, expert pool, and mechanical gate are at [github.com/YuhaoLin2005/hermes-workspace](https://github.com/YuhaoLin2005/hermes-workspace). Everything described in this article is there — YAML, Python, markdown. No demo, no mockup.

---

*Who's going on your board — and which of their principles do you keep coming back to?*
