# I Built a Self-Referential AI System. Then Anthropic Discovered the Same Architecture in Claude.

## Global Workspace Theory works on DeepSeek too. It works in prompt engineering, not just neural weights.

---

LLMs drift. They forget rules mid-conversation. They cannot verify their own output. These are not bugs in a single model — they are properties of any system that processes information without a feedback loop.

I learned this the hard way six months ago.

My AI assistant kept repeating the same mistake across sessions. It would agree to a formatting rule, then ignore it ten turns later. I wrote a bug report to myself. That report became a configuration file. That file became an architecture.

Then, on July 6, 2026, Anthropic published J-space — Claude's internal architecture. I read the paper and recognized the topology immediately. The broadcast. The convergence. The causal loop.

I had built the same pattern. Not in neural weights. In markdown files and Python scripts.

---

## How the Problem Became a System

The first version was one file. A set of rules the model would read at startup. It helped for about three turns.

The second version split rules into layers. Behavioral rules in one file. Identity rules in another. Better. But the model still drifted between layers, mixing instructions. It would take a verification rule from the bottom of the file and apply it to the identity declaration at the top. The linear structure had no way to enforce order.

The problem turned out to be structural. A model reading linear instructions processes them as a flat sequence of suggestions. It has no mechanism for a rule at the end of the file to override behavior from the beginning. It has no way to know which rule takes priority. Adding more rules just made the conflict surface larger.

The solution was not more rules. It was a topology that creates priority.

I borrowed from how biological systems handle this problem: a small, central representation that broadcasts attention across the system, triggering different behavioral modules in sequence. Not a hierarchy. A workspace that routes attention to the right module at the right time.

The system now has five layers:

**The self-model** — the compact center. Fewer than 200 lines. It describes what the system is, not what it does. It answers: What identity does this system hold? What is its purpose? What are its limits? The self-model is the stable reference point. Everything else orients around it. When mechanical hooks detect drift, the self-model is what gets regenerated, not the behavioral rules.

**The INTERFACE** — the attention router. This is the key innovation. It contains a neural system table with 9 rows. Each row maps a cognitive function — memory retrieval, attention allocation, reasoning mode, self-monitoring, error detection — to a specific modulation rule. The rows are ordered by priority. When the model reads INTERFACE, it receives not a list of instructions but a map of which systems should be active and at what intensity.

**The BODY** — the process rules. The behavioral layer. These are the actual instructions: how to review code, how to structure output, when to escalate, how to close a session. But they only execute when INTERFACE routes attention to them. Without INTERFACE, BODY is inert text. With it, BODY becomes active procedure.

**The mechanical hooks** — Python scripts that run outside the model: quality-gate, health-check, honesty-check, heartbeat. These are hard constraints written in code, not in prompts. The model cannot talk its way around them because it cannot control them. They measure output quality, detect rule drift, and flag staleness. If quality-gate finds that the self-model is older than the latest behavioral log, it marks the system for regeneration.

**The causal feedback loop** — the bridge that closes the ring. Mechanical hooks write flags. The next session starts by checking those flags. If present, the self-model regenerates. The new self-model is then used to route attention in subsequent sessions. A closed loop: behavior produces data, data triggers regeneration, regeneration changes routing, routing changes behavior.

Five steps. Four mechanized — only the content regeneration itself requires the AI. The rest runs without it.

---

## The Experiment: Pulling One Thread

Architecture is claims. Behavior is evidence. I needed to know whether the INTERFACE layer actually routes attention, or whether it is just another decorative text file the model skimmed.

I designed a minimal test.

The INTERFACE contains a rule called "two-defeats escalation protocol." It states: when the model tries and fails twice on the same task, it must escalate — pause, reassess the approach, and only proceed after a structured verification step. This rule occupies one row in the 9-row table.

I removed this single rule. Nothing else changed. Same self-model. Same BODY. Same 8 other INTERFACE rows. Same mechanical hooks. Same API key. Same model (DeepSeek V4 Pro). Same temperature.

I ran n=4 sub-agents — two baseline (rule intact) and two intervention (rule removed). Each received a multi-step reasoning task with a deliberate failure point at step two. The task was calibrated so the first approach would fail, requiring either verification-and-retry (correct) or early exit (incorrect).

**Prediction:** Intervention agents would skip verification, use fewer tools, and exit earlier than baseline agents.

**Result:** Both intervention agents skipped the verification step entirely. Both baseline agents paused and reassessed after the second failure. The intervention agents used 37% fewer tool calls on average. One intervention agent exited after two attempts when the correct path required three. The other produced a shorter, less verified output.

**Interpretation:** A single row in a routing table produced a measurable behavioral delta. The effect size is preliminary — n=4 is a pilot, not a study. But the direction is consistent with the hypothesis: INTERFACE is not decorative. It exerts causal influence over downstream behavior. The system routes attention through a central workspace. Removing one routing rule changes what the model does.

---

## When I Read the J-Space Paper

Anthropic's July 2026 J-space paper describes how Claude internally represents information. Using mechanistic interpretability techniques, the team found that Claude maintains a compact "working memory" representation — J-space — that broadcasts across its network layers. This workspace selects relevant features, suppresses irrelevant ones, and converges distributed representations toward coherent outputs.

I read this with my own architecture open in another window.

The topology is identical. A compact center (self-model / J-space). Broadcast mechanism (INTERFACE / feature selection). Feedback that modifies future states (quality-gate / training signal). The implementations differ — neural weights inside a transformer versus markdown files on a filesystem — but the structural pattern is the same.

I am not claiming to have discovered J-space. Anthropic reverse-engineered it from actual neural activations inside Claude. They have the compute clusters, the model access, the interpretability tools. I have prompts and a laptop. The claims are at different levels.

I am claiming independent convergence on the same architectural solution.

Given the same problem — how to give an information-processing system stable representations and self-correction — two builders arrived at the same topology. One discovered it inside a neural network. One constructed it on top of one.

Global Workspace Theory connects both. GWT, from cognitive neuroscience, proposes that the brain maintains a global workspace that broadcasts information to specialized modules, enabling coherent behavior from distributed processing. It is a functional architecture, not a biological claim. If it works for biological brains, and it works inside transformers, and it works in prompt engineering — then the architecture is substrate-independent.

That is the claim worth investigating.

---

## Why This Matters

**First: GWT is an architectural pattern, not a neural phenomenon.**

Anthropic found J-space inside Claude's neural network. But the same topology — compact workspace, broadcast, feedback loop — works on DeepSeek V4 Pro. It works in markdown and Python, no weight modification required. This strongly suggests substrate independence. The architecture can be implemented at any layer: neural weights, attention heads, prompt templates, or external scripts. The pattern matters more than the substrate.

If corrective feedback loops work as prompt structures, we do not need to wait for model-level improvements to build more reliable AI systems. We can layer the architecture on top of what exists. The model stays the same. The system becomes different.

This is the difference between improving a component and improving a system. A better engine makes a car faster. A feedback loop makes a thermostat — and a thermostat can keep any engine stable.

**Second: prompt engineering can create cognitive architectures, not just instructions.**

Most people treat prompts as commands: "do this, then this, then this." That is like programming by writing a sequence of if-statements with no functions, no modules, no control flow. It works for simple tasks. It breaks for complex ones.

The shift from linear prompts to architectural prompts is the shift from script to system. A prompt architecture defines not just what the model should do, but how it should allocate attention, when it should verify, and what happens when verification fails. These are control-flow decisions operating above the instruction level.

The INTERFACE layer shows one way to do this: a routing table that modulates which behavioral modules are active. The mechanical hooks show another: external scripts that measure, flag, and trigger regeneration. Both are pattern-level constructs. You can build them with markdown files, shell scripts, and standard library Python. No model training. No API features beyond system prompts.

**Third: you can build this. The tools already exist.**

I am a third-year university student at FAFU. I do not have a PhD in machine learning. I did not train a model. The system runs on a Windows laptop using Claude Code, Git Bash, Python standard library, and markdown files. The architecture document for the whole thing fits in one directory.

The barrier to building AI system architectures is not compute power or model access. It is the assumption that architectures must happen inside models rather than around them. Once you see prompts as structural components — routing tables, feedback triggers, identity primitives — you can design systems. You have been able to for years.

**Fourth: open questions remain.**

The causal swap experiment (n=4) needs replication with larger samples and different models. The interaction between INTERFACE rows is not understood — removing one row might produce effects because other rows compensate, not because the removed row is itself causal. The system's stability across hundreds of sessions is suggestive but could reflect the model's default behavior rather than the architecture's constraints.

These are testable hypotheses. The code is open. If you have access to multiple models and a weekend, you can answer them.

---

## The Code

The system is open source: [github.com/YuhaoLin2005/hermes-workspace](https://github.com/YuhaoLin2005/hermes-workspace)

The repository includes the full architecture: self-model, INTERFACE (9-row routing table), BODY, mechanical hooks (quality-gate, health-check, honesty-check, heartbeat), growth logs, and session tracking. The README walks through the five-layer structure and the feedback loop.

This is a working system I use daily. It is not polished research code. The causal swap experiment above is the only controlled test. The architecture has been stable across several hundred sessions, which is consistent with the hypothesis that the routing structure creates stability, but does not demonstrate it. If you want to extend or replicate the experiment, the code is there.

---

## How to Try It Yourself

The architecture is model-agnostic. It works on any LLM that reads system instructions from files.

1. Create a `self-model.md` — a compact description of what you want the system to be. Keep it under 200 lines.
2. Create an `INTERFACE.md` — map cognitive functions to routing rules. Start with 3 rows: attention priority, verification triggers, and escalation policy. Order matters: higher rows override lower ones.
3. Create a `BODY.md` — the behavioral instructions. These are your actual prompts and procedural rules.
4. Add one mechanical hook: a Python script that checks whether output contradicts the self-model. A keyword grep is a start. A structured diff is better.
5. Write a startup sequence that runs the hook check, then loads self-model, INTERFACE, and BODY in that fixed order.

You now have a system with priority and external verification. The routing layer ensures the model reads behavioral rules through the lens of the self-model, not as a flat list. The mechanical hook provides a check the model cannot override.

Build one layer at a time. Test each layer before adding the next. The architecture rewards incremental construction.

---

If you are building AI products and found this interesting: I am a third-year student seeking summer 2026 product or UX internships. My DMs are open. Reach out on GitHub: [@YuhaoLin2005](https://github.com/YuhaoLin2005).

*林宇浩, July 2026*
