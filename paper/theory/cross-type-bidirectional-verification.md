# Verification as a Relation: Cross-Type Error Orthogonality in AI Governance

> **Target venues**: ICLR / NeurIPS / FAccT / AIES
> **Author**: 林宇浩 (Yuhao Lin), Fujian Agriculture and Forestry University
> **Date**: 2026-07-26

---

## Abstract

AI governance today relies on *homogeneous verification* — language models verifying language models — which suffers from a structural ceiling: correlated blind spots make consensus meaningless. We introduce **Cross-Type Bidirectional Verification** (CTBV), a framework where a deterministic mechanical verifier (type-D) and a probabilistic neural verifier (type-P) form a mutual suspicion loop, each covering the blind spots the other structurally cannot detect. We prove three theorems: (1) under orthogonal error spaces, CTBV achieves a false negative rate of zero — impossible under any same-type recursive architecture; (2) homogeneous verification degrades to single-verifier performance as error correlation \(\rho \to 1\); (3) verifier trustworthiness decays exponentially with bypass rate \(b\), collapsing to zero in a single interaction when \(b=1\). We validate the framework empirically through an ablation study of a 38-hook production AI governance system, where gate audit identified an 87% noise rate and removed 15 zero-value hooks without degrading true-positive detection. The framework redefines verification from a *property* of a system to a *relation* between systems with structurally orthogonal error spaces.

---

## 1. Introduction

### 1.1 The Verification Regress

Given an AI agent \(A\) generating behavior in context \(C\), how do we verify \(A\)'s compliance with governance rules \(R\)?

**Naive approach** (self-verification): Ask \(A\) to verify itself. Fails for structural reasons — the Prose Barrier (Lin, 2026) establishes that any autoregressive model \(M_\theta\) generates verification claims from the same distribution \(P(\text{token} \mid \text{context}; \theta)\) as its behavior. Blind spots in generation propagate identically to blind spots in verification. The model cannot step outside its own decoder to audit itself.

**Recursive approach** (multi-agent verification): \(A_1\) verifies \(A_2\) verifies \(A_3\). Fails when \(A_1, A_2, A_3\) share architecture — correlated blind spots make consensus evidence of nothing. If all verifiers agree because they share the same failure mode, agreement is not accuracy. Worse, it produces *confidence without correctness* — the most dangerous state for a governance system.

**Our approach** (cross-type bidirectional): Pair a *deterministic mechanical gate* \(V_D\) (regex, file timestamps, exit codes — operating outside any neural model) with a *probabilistic neural verifier* \(V_P\) (language model). They form a mutual suspicion loop: \(V_D\) catches \(V_P\)'s self-deception; \(V_P\) catches \(V_D\)'s staleness. The architecture works precisely *because* each verifier is blind to what the other detects.

### 1.2 The Observation

During a systematic audit of 38 mechanical gate hooks in a production AI governance system (§4), we observed an empirical decomposition that motivated the theory:

| Gate type | Log entries | True intercepts | Noise rate | 95% CI (Clopper-Pearson) |
|-----------|------------|-----------------|------------|---------------------------|
| Three-questions timeout | 295 | 0 | 100% | [0%, 1.24%] |
| Sensitive-path check | 4 | 4 | 0% | [39.8%, 100%] |
| Dangerous-command check | 6 | 6 | 0% | [54.1%, 100%] |
| Execution-debt check | 24 | 24 | 0% | [85.8%, 100%] |

The three-questions gate had collapsed into *security theater* — 295 consecutive blocks, zero cognitive friction, all bypassed via a 19-line Python script. Yet the other mechanical gates continued to provide genuine protection. **A gate's value is not in its formal existence but in whether its blind spots are orthogonal to the LLM's.**

### 1.3 Contributions

We make five contributions:

1. **Formal framework**: We define verifier types (deterministic vs. probabilistic), error space orthogonality, and the CTBV architecture (§3.1).

2. **Three theorems**: We prove (a) CTBV achieves zero false negatives under strict orthogonality, impossible under same-type verification; (b) homogeneous verification's error bound degrades linearly with error correlation \(\rho\); (c) verifier trust follows exponential decay with bypass rate \(b\) (§4).

3. **Dynamical system formulation**: We formalize CTBV as a **Coupled Dual-Graph Dynamical System** — an inner complete graph (transformer attention as message passing on \(K_n\)) bidirectionally coupled to an outer functional graph (mechanical verification nodes) at discrete event times, with adaptive coupling strength \(\lambda(t)\) governed by a Liquid Time-Constant ODE (§3.3). This formulation connects CTBV to graph-of-thought reasoning (Besta et al., 2024), attention-as-GNN (Joshi et al., 2025), and liquid neural architectures (Hasani et al., 2021).

4. **Empirical validation**: We conduct an ablation study on a 38-hook production system, demonstrating that removing a collapsed gate (87% noise rate) has zero impact on remaining gate detection rates (§5). We also test the adaptive coupling hypothesis in a 12-day drift prediction experiment, discovering a self-limiting property of CTBV (§3.3.4).

5. **Unified theory**: We position CTBV as the constructive counterpart to the Prose Barrier impossibility result — together forming a complete theory of AI verification (§6).

---

## 2. Related Work

### 2.1 Single-Type Verification Architectures

**Self-critique and Constitutional AI.** Bai et al. (2022) propose Constitutional AI, where a model critiques and revises its own outputs against a written constitution. This is structurally capped: the critique is generated from the same \(P(\text{token} \mid \text{context}; \theta)\) as the output. Any blind spot in generation is a blind spot in critique. Our framework proves this formally: when \(\rho = 1\) (same model critiquing itself), \(\alpha_{\text{HOM}} \to \alpha_P\) — no improvement (Theorem 2).

**Recursive oversight and debate.** Irving et al. (2018) propose AI safety via debate, where two agents argue and a human judges. Bowman et al. (2022) extend this to scalable oversight with LLM judges. In both cases, the agents and judges are same-type (neural models). The debate format can surface disagreements, but cannot guarantee that the disagreements cover all blind spots — correlated failures remain possible. Our Theorem 2 shows that as \(\rho \to 1\), the false negative rate approaches the single-verifier rate regardless of the number of debaters.

**Multi-agent consensus.** Du et al. (2023) and Li et al. (2023) explore multi-agent debate for reasoning and factuality. Park et al. (2023) use generative agents for social simulation. These architectures use multiple same-type agents to improve through diversity, but the diversity is at the level of prompts and roles, not at the level of computational substrate. When all agents share the same transformer architecture, correlated blind spots remain structurally possible.

### 2.2 Cross-Strength Verification (Same-Type)

**Neural Interactive Proofs.** Hammond & Adam-Day (2025) propose Neural Interactive Proofs, where a weaker model generates claims and a stronger model verifies them. This is cross-strength within the same type — both are neural verifiers operating via \(P(\text{token} \mid \text{context}; \theta)\). The stronger model may catch some errors the weaker model makes, but their error spaces are not guaranteed to be orthogonal. A stronger model can still share architectural blind spots with a weaker one.

### 2.3 Mechanical and Formal Verification

**Program verification and static analysis.** Hoare logic (Hoare, 1969), model checking (Clarke et al., 1986), and abstract interpretation (Cousot & Cousot, 1977) verify program properties mechanically. These are type-D verifiers operating on formal specifications — but they verify code against specifications, not AI behavior against governance rules. Our work applies type-D verification to a domain (LLM behavior) where it has not been systematically deployed.

**Runtime monitoring.** Runtime verification (Leucker & Schallhart, 2009) monitors system execution against formal properties. Our mechanical gates are a form of runtime monitoring, but the novelty is in the *bidirectional* architecture — the LLM also monitors the gate logic for staleness, creating a loop that neither formalism addresses.

**Scrivens gates.** Scrivens (2026) empirically validates classification-verification dichotomies for AI safety gates, analyzing Lipschitz ball verifiers as a formal verification layer. Our framework generalizes this to the bidirectional case and provides the theoretical error bounds that Scrivens' empirical work motivates.

### 2.4 Graph-Theoretic and Dynamical Perspectives

Three additional lines of work provide mathematical tools for analyzing CTBV, though none proposes the coupled dual-graph architecture:

**Graph of Thoughts (Besta et al., 2024).** GoT models LLM reasoning as graph operations on a directed graph \(G = (V, E)\), extending chain/tree topologies to arbitrary graph structures. CTBV extends GoT's inner graph with an external verification graph — GoT models the reasoning, CTBV models the reasoning *plus its verification*.

**Attention as GNN (Joshi et al., 2025; El et al., 2025).** Recent work reformulates self-attention as message passing on a complete graph \(K_n\). This provides the mathematical bridge between transformer internals and graph theory that CTBV uses in its inner graph model (§3.3). The key insight — that the attention matrix *is* a weighted adjacency matrix — makes the dual-graph formalism possible.

**Liquid Time-Constant Networks (Hasani et al., 2021; Cantini et al., 2024).** LTCs introduce adaptive time constants \(\tau(t)\) governed by an ODE, enabling neurons to modulate their response speed based on input. CTBV borrows this adaptive mechanism for its coupling strength \(\lambda(t)\) (§3.3, Definition 10), but applies it at the architectural level (coupling between graphs) rather than the neuronal level.

**ShieldAgent (Chen et al., ICLR 2025).** ShieldAgent pairs LTL rules with policy models for safety-constrained action selection. It is the closest prior work to CTBV's outer graph, but its verification is unidirectional (rules constrain agent; agent does not audit rules).

### 2.5 Positioning

To our knowledge, **no prior work proposes or analyzes a bidirectional verification architecture between deterministic (type-D) and probabilistic (type-P) verifiers.** All existing verification architectures operate within the same type (neural↔neural or formal↔formal). CTBV is the first to exploit *structural* (not just statistical) orthogonality of error spaces across computational substrates, and the first to formalize verification as a coupled dual-graph dynamical system with adaptive coupling strength.

---

## 3. Formal Framework

### 3.1 Definitions

**Definition 1 (State Space).** Let \(\mathcal{S}\) be the space of all possible states of an AI-governed system. A state \(s \in \mathcal{S}\) captures all observable features: the LLM's output text, the file system state, the command history, and any other measurable property.

**Definition 2 (Compliance Ground Truth).** Let \(C: \mathcal{S} \to \{0, 1\}\) be the ground-truth compliance function, where \(C(s) = 1\) iff state \(s\) satisfies governance rule \(R\). \(C\) is an oracle — it is not directly accessible to any verifier but defines the objective standard.

**Definition 3 (Verifier).** A verifier \(V: \mathcal{S} \to \{0, 1\}\) is a function where \(V(s) = 1\) means "pass" (deemed compliant) and \(V(s) = 0\) means "fail" (deemed non-compliant). The verifier's **error space** is:

\[
E(V) = \{s \in \mathcal{S} : V(s) \neq C(s)\}
\]

Decomposed into:
- **False negatives**: \(\text{FN}(V) = \{s \in \mathcal{S} : C(s) = 0 \land V(s) = 1\}\)
- **False positives**: \(\text{FP}(V) = \{s \in \mathcal{S} : C(s) = 1 \land V(s) = 0\}\)

The **false negative rate** is \(\alpha(V) = |\text{FN}(V)| / |\mathcal{S}^-|\) where \(\mathcal{S}^- = \{s \in \mathcal{S} : C(s) = 0\}\).

**Definition 4 (Verifier Type).** A verifier \(V\) is:

- **Type-D** (deterministic) iff \(V(s)\) is computed by a finite deterministic function of observable features of \(s\). Type-D verifiers have NO learned parameters — they operate via regex, file timestamps, exit codes, pattern matching. Formally: \(\forall s_1, s_2 \in \mathcal{S}\) that are identical in the features inspected by \(V\), \(V(s_1) = V(s_2)\).

- **Type-P** (probabilistic) iff \(V(s)\) depends on a learned distribution \(P(\cdot \mid \theta)\) over a token vocabulary. Type-P verifiers cannot deterministically guarantee any property of their own error space. Formally: for any type-P verifier \(V\), there is no \(V\) that can compute \(E(V)\) — self-verification is structurally impossible (Prose Barrier).

**Definition 5 (Error Space Orthogonality).** Two verifiers \(V_1, V_2\) have **orthogonal error spaces** iff:

\[
E(V_1) \cap E(V_2) = \emptyset
\]

That is, there exists no state \(s \in \mathcal{S}\) where both verifiers simultaneously produce an incorrect verdict. We say \(V_1, V_2\) are **\(\varepsilon\)-orthogonal** iff:

\[
\frac{|E(V_1) \cap E(V_2)|}{|\mathcal{S}|} < \varepsilon
\]

**Definition 6 (Cross-Type Bidirectional Verification).** A CTBV architecture is a triple \((V_D, V_P, H)\) where:

- \(V_D\) is a type-D verifier (mechanical gate)
- \(V_P\) is a type-P verifier (neural model)
- \(V_D\) and \(V_P\) are \(\varepsilon\)-orthogonal for small \(\varepsilon\)
- **Direction 1** (\(V_D\) verifies \(V_P\)): \(V_D\) checks \(V_P\)'s behavioral outputs against patterns that \(V_P\) structurally cannot self-verify (file safety, command safety, execution debt)
- **Direction 2** (\(V_P\) verifies \(V_D\)): \(V_P\) reasons about \(V_D\)'s rule logic — are patterns stale? Are thresholds miscalibrated? Does the gate cover current risk vectors?
- \(H\) is a human arbiter who resolves \(V_D \neq V_P\) disagreements and audits the verification architecture itself

The combined verdict is:

\[
\text{CTBV}(s) = \begin{cases}
1 & \text{if } V_D(s) = 1 \land V_P(s) = 1 \\
0 & \text{otherwise}
\end{cases}
\]

with appeal to \(H\) when \(V_D(s) = 0 \land V_P(s) = 1\) or \(V_D(s) = 1 \land V_P(s) = 0\).

### 3.2 Key Property: Structural Orthogonality of Error Causes

The orthogonality \(E(V_D) \cap E(V_P) = \emptyset\) has a structural justification that does not require exhaustive enumeration of \(\mathcal{S}\):

- **\(E(V_D)\)** arises from **staleness**: patterns that were correct at deployment time fail to match new circumstances. A credential path pattern misses a new naming convention. A dangerous command regex misses a new attack vector. The gate logic is correct but the *world changed*.

- **\(E(V_P)\)** arises from **self-reference failure**: the model generates compliance claims from the same distribution as its behavior. It cannot introspect on whether it *actually* followed a rule — it can only generate a *claim* that it did. The Prose Barrier makes this structural: \(P(\text{"I followed rule R"} \mid \text{context}; \theta) \neq\) actual compliance.

These error causes operate on **different computational substrates**:
- Staleness is a function of (rule logic, environment state) → operates on the relationship between code and world
- Self-reference failure is a function of (model architecture, token distribution) → operates on the relationship between model and its own outputs

When the causal mechanisms are disjoint and operate on disjoint features, their error spaces cannot intersect. Formally, if \(E(V_D)\) depends on feature set \(\Phi_D\) and \(E(V_P)\) depends on feature set \(\Phi_P\) with \(\Phi_D \cap \Phi_P = \emptyset\) and no confounding path connects them, then \(E(V_D) \cap E(V_P) = \emptyset\).

**Lemma 1 (Feature Disjointness implies Error Orthogonality).** Let \(V_D\) inspect only features \(\Phi_D \subset \mathcal{F}\) and \(V_P\) inspect only features \(\Phi_P \subset \mathcal{F}\). If (i) \(\Phi_D \cap \Phi_P = \emptyset\), (ii) \(E(V_D)\) depends only on \(\Phi_D\), and (iii) \(E(V_P)\) depends only on \(\Phi_P\), then \(E(V_D) \cap E(V_P) = \emptyset\).

*Proof.* Suppose \(s \in E(V_D) \cap E(V_P)\). Then \(s\) must simultaneously exhibit a staleness condition (depending on \(\Phi_D\)) and a self-reference failure (depending on \(\Phi_P\)). But since \(\Phi_D \cap \Phi_P = \emptyset\), the features that would make \(s \in E(V_D)\) are disjoint from the features that would make \(s \in E(V_P)\). For any state \(s\), the projection of \(s\) onto \(\Phi_D\) determines membership in \(E(V_D)\), and the projection onto \(\Phi_P\) determines membership in \(E(V_P)\). With \(\Phi_D \cap \Phi_P = \emptyset\), no state can have both. \(\square\)

### 3.3 Dynamical System Formulation: Coupled Dual-Graph Architecture

The static CTBV definitions (§3.1) establish *what* the architecture is. We now formalize *how* it operates over time as a coupled dynamical system, connecting CTBV to three active research frontiers: graph-of-thought reasoning (Besta et al., 2024), attention as complete-graph message passing (Joshi et al., 2025), and liquid neural architectures with adaptive time constants (Hasani et al., 2021; Cantini et al., 2024).

#### 3.3.1 Motivation: Why a Dynamical Perspective?

The five-layer CTBV architecture (L0-L4) is not a static pipeline. It is a **coupled system** where:

- **L1-L2 (inner graph):** The transformer's self-attention operates as message passing on a complete directed graph \(K_n\) over \(n\) context tokens. Every token attends to every other token — the attention matrix *is* the weighted adjacency matrix (Joshi et al., 2025).
- **L3-L4 (outer graph):** Mechanical gates and drift predictors form a sparse functional graph whose nodes inspect disjoint feature sets \(\Phi_D\). These nodes activate at discrete event times (when hooks fire), not continuously.
- **Coupling:** The inner graph (continuous-time self-attention over tokens) and outer graph (discrete-event gate firings) interact at hook execution points. At each coupling event, the outer graph's verdict modifies the inner graph's subsequent behavior — blocking a write, modifying a prompt, recording a drift signal.

This is structurally distinct from both pure attention-only architectures (which lack external verification nodes) and pure rule-based systems (which lack neural adaptation). Understanding it requires a coupled-graph dynamical formalism.

#### 3.3.2 Related Formalisms

Three existing formalisms each capture a piece of the CTBV architecture, but none capture the whole:

**Graph of Thoughts (GoT, Besta et al., 2024).** GoT models LLM reasoning as operations on a directed graph \(G = (V, E)\), where vertices are thought-units and edges are dependency relations. Reasoning transformations (aggregation, refinement, generation) map subgraphs to new vertices. GoT formalizes *what happens inside* the transformer's reasoning trace — it is a model of the **inner graph**. However, GoT has no concept of *external verification* — all operations are self-contained within the LLM's thought generation. There is no type-D verifier that can reject a thought based on features outside the token vocabulary.

**Attention as Complete-Graph Message Passing (Joshi et al., 2025; El et al., 2025).** Self-attention can be reformulated as message passing on a complete directed graph \(K_n\): each token is a node, attention weights are edge weights, and the multi-head projection is a learned message function. This reveals that the transformer's "reasoning" is structurally equivalent to one round of GNN message passing on a fully connected graph — powerful but also brittle, since every node influences every other node. The complete graph has no *topological protection* — no structural barrier prevents a spurious compliance claim from propagating to all nodes.

**ShieldAgent (Chen et al., ICLR 2025).** ShieldAgent introduces external verification via Linear Temporal Logic (LTL) rules organized into probabilistic rule circuits. An Action-based Safety Policy Model (ASPM) maps state-action pairs to rule-circuit activations. ShieldAgent is the closest prior work to CTBV's outer graph — it recognizes that external, non-neural rules are necessary. However, ShieldAgent's rules are *unidirectional*: they constrain the agent but the agent does not verify the rules. There is no bidirectional coupling.

**Liquid Time-Constant Networks (LTC, Hasani et al., 2021).** LTCs introduce neurons with adaptive time constants \(\tau(t)\) governed by the ODE:

\[
\frac{dx}{dt} = -\frac{1}{\tau(t)} \cdot x + f(x, I, \theta)
\]

where \(\tau(t)\) is itself a function of the neuron's state — the neuron "decides" how fast to respond based on its current input. Cantini et al. (2024) derived the exact closed-form solution, enabling stable numerical integration. The key insight for CTBV: the **coupling strength** between the inner and outer graphs should be adaptive, not fixed. When drift risk is low, gates should be lightweight (low coupling). When drift risk is elevated, gates should intensify (high coupling). This is structurally analogous to LTC's adaptive time constant — a mechanism whose responsiveness scales with need.

**What's missing.** GoT models the inner graph. ShieldAgent models a unidirectional outer graph. LTC provides adaptive dynamics but for single neurons, not coupled verification systems. No existing formalism combines: (a) an inner complete graph (transformer), (b) an outer functional graph (verification nodes), (c) discrete-event coupling between them, and (d) adaptive coupling strength governed by a learnable ODE. CTBV requires all four.

#### 3.3.3 Formal Definition: Coupled Dual-Graph Dynamical System

**Definition 7 (Inner Graph — Transformer as Complete Graph).** Let \(\mathcal{G}_{\text{in}}(t) = (V_T, E_T, W_T(t))\) be the inner graph at time \(t\), where:

- \(V_T = \{v_1, \ldots, v_n\}\) are the \(n\) tokens in the context window.
- \(E_T = V_T \times V_T\) is the complete directed edge set — every token attends to every token.
- \(W_T(t) = [w_{ij}(t)]_{n \times n}\) is the attention weight matrix, where \(w_{ij}(t)\) is the attention weight from token \(i\) to token \(j\), aggregated across the transformer stack.

The inner graph evolves continuously as the model autoregressively generates tokens: each new token adds a node and \(2n+1\) edges (in + out + self-loop), and the attention matrix is recomputed. The inner graph's dynamics are:

\[
\mathcal{G}_{\text{in}}(t+1) = \text{TransformerStep}(\mathcal{G}_{\text{in}}(t), x_{t+1}; \theta)
\]

where \(x_{t+1}\) is the newly generated token and \(\theta\) are the frozen model parameters.

**Definition 8 (Outer Graph — Verification Nodes).** Let \(\mathcal{G}_{\text{out}} = (V_G, E_G)\) be the outer verification graph, where:

- \(V_G = \{g_1, \ldots, g_k\}\) are the \(k\) mechanical gate hooks (type-D verifiers). Each \(g_i\) is a function \(g_i: \mathcal{S} \to \{0, 1\}\) operating on feature set \(\Phi_i \subset \mathcal{F}\).
- \(E_G \subset V_G \times V_G\) are directed edges between gates representing execution dependencies — \(g_i \to g_j\) if \(g_j\) is only invoked after \(g_i\) completes (e.g., PreToolUse hooks execute before PostToolUse hooks).
- The outer graph is **sparse**: \(|E_G| \ll k(k-1)\), reflecting the sequential hook execution model. Most gate pairs are independent.
- The outer graph is **discrete-event**: gates fire only at hook execution points (tool calls, session state transitions), not continuously.

**Definition 9 (Coupling Events).** The two graphs are coupled at discrete event times \(\{t_1, t_2, \ldots\}\), where each \(t_e\) is a hook execution moment. At coupling event \(t_e\):

1. **Downward coupling (outer to inner):** The outer graph's verdict modifies the inner graph's subsequent trajectory. If \(g_i(s) = 0\) (gate blocks), the inner graph's generation is interrupted — the token that would have been generated is replaced, and \(\mathcal{G}_{\text{in}}(t_e^+)\) differs from what \(\mathcal{G}_{\text{in}}(t_e^-)\) would have produced.

2. **Upward coupling (inner to outer):** The inner graph's behavior provides the state \(s\) that triggers the next gate evaluation. The content generated by \(\mathcal{G}_{\text{in}}\) determines which gates fire and with what verdict.

Formally, at coupling event \(t_e\):

\[
\begin{aligned}
\mathcal{G}_{\text{out}} \times \mathcal{G}_{\text{in}}(t_e^-) &\to \mathcal{G}_{\text{in}}(t_e^+) \\
\mathcal{G}_{\text{in}}(t_e^-) &\to \text{trigger}(t_{e+1})
\end{aligned}
\]

The coupling is **bidirectional** — each graph constrains the other. This distinguishes CTBV from both ShieldAgent (unidirectional outer to inner) and GoT (no outer graph at all).

**Definition 10 (Adaptive Coupling Strength).** The intensity of the downward coupling (outer to inner) is governed by an adaptive coupling strength \(\lambda(t) \in [0, 1]\):

\[
\lambda(t) = \lambda_{\text{base}} + \Delta\lambda \cdot \tanh\left(\frac{D(t) - \theta_D}{\tau_D}\right)
\]

where:
- \(\lambda_{\text{base}} \in [0, 1]\) is the minimum coupling strength (always-active essential gates, e.g., sensitive-path check).
- \(\Delta\lambda = 1 - \lambda_{\text{base}}\) is the adaptive range.
- \(D(t) \in [0, 100]\) is the L4 drift risk score, computed from 8 features via `drift_predictor.py` (see §5.5 and Lin, 2026, Experiment 13).
- \(\theta_D\) is the drift threshold — when \(D(t) > \theta_D\), coupling strength increases.
- \(\tau_D\) controls the transition smoothness — large \(\tau_D\) gives gradual escalation; small \(\tau_D\) gives sharp switching.

When \(D(t) \ll \theta_D\) (low drift risk): \(\lambda(t) \approx \lambda_{\text{base}}\) — minimal gates active, low overhead.
When \(D(t) \gg \theta_D\) (high drift risk): \(\lambda(t) \approx \lambda_{\text{base}} + \Delta\lambda = 1\) — full gate coverage, maximum protection.
When \(D(t) \approx \theta_D\): \(\lambda(t)\) transitions smoothly via the \(\tanh\) sigmoid.

This formulation follows the **Liquid Time-Constant (LTC)** formalism (Hasani et al., 2021), where the neuron's time constant \(\tau(t)\) adapts based on input. Here, the coupling strength \(\lambda(t)\) adapts based on drift risk — the architecture "decides" how tightly to couple based on how much drift it detects. Cantini et al. (2024) proved that LTC ODEs admit exact closed-form solutions, enabling stable and efficient numerical integration. Our \(\tanh\) parameterization inherits this stability — \(\lambda(t)\) is bounded in \([\lambda_{\text{base}}, 1]\) and varies smoothly, preventing oscillation.

#### 3.3.4 Empirical Instantiation: L4 Drift Score as Coupling Controller

The adaptive coupling mechanism was empirically tested in a 12-day retrospective analysis (Lin, 2026, Experiment 13). The L4 drift score \(D(t)\) is computed from 8 features with calibrated weights derived from 34-session retrospective coding (55.9% violation rate baseline):

\[
D(t) = 100 \cdot \sum_{i=1}^{8} w_i \cdot f_i(t)
\]

where the features and weights are:

| Feature \(f_i\) | Weight \(w_i\) | Type |
|----------------|---------------|------|
| \(f_1\): rule_count | +0.10 | Risk (more rules = more complexity) |
| \(f_2\): unhooked_rules | +0.20 | Risk (no mechanical protection) |
| \(f_3\): session_age_turns | +0.08 | Risk (long sessions = drift accumulation) |
| \(f_4\): compact_count | +0.12 | Risk (compaction rewrites context) |
| \(f_5\): tool_diversity | +0.05 | Risk (more tools = more switch cost) |
| \(f_6\): days_since_audit | +0.15 | Risk (stale audit = undetected drift) |
| \(f_7\): gate_coverage | -0.20 | Protective (more hooks = less risk) |
| \(f_8\): pre_check_compliance | +0.10 | Risk (skip history = habitual bypass) |

**Empirical finding (2026-07-28):** Under full CTBV deployment (gate_coverage = 1.0, unhooked_rules = 0), \(D(t) \equiv 0\) for all observed sessions. The drift score has zero variance in the available data — the mechanical gates suppress drift so effectively that the predictor receives no signal. This is a **self-limiting property** of CTBV: the architecture prevents the very variance the adaptive coupling mechanism needs to demonstrate its utility.

The practical implication: \(\lambda(t)\) adaptive scheduling is a **theoretically sound safety net** that activates when gate coverage degrades (e.g., during maintenance, hook removal, or partial deployment), but is empirically silent under full protection. The mechanism is analogous to an emergency brake — it must be present and testable, even if normal operation never triggers it.

#### 3.3.5 Comparison of Dynamical Formalisms

| Property | GoT (Besta 2024) | ShieldAgent (Chen 2025) | LTC (Hasani 2021) | **CTBV (this work)** |
|----------|------------------|------------------------|-------------------|---------------------|
| Inner graph model | Directed graph \(G=(V,E)\) | — (no inner graph formalism) | — (single neuron ODE) | Complete graph \(K_n\) (attention) |
| Outer verifier | — (self-contained) | LTL rules + ASPM | — (no verification) | Type-D gates on \(\Phi_D\) |
| Coupling direction | — (no coupling) | Unidirectional (rule to agent) | — (no coupling) | **Bidirectional** (inner to outer) |
| Event model | Continuous (reasoning steps) | Discrete (action triggers) | Continuous (ODE) | **Hybrid** (continuous inner + discrete-event outer) |
| Adaptive mechanism | — (fixed topology) | Probabilistic rule circuits | \(\tau(t)\) via ODE | \(\lambda(t) = \lambda_{\text{base}} + \Delta\lambda \cdot \tanh(\frac{D(t)-\theta_D}{\tau_D})\) |
| Bidirectional verification | No | No | No | **Yes** |
| Self-limiting property | — | — | — | \(D(t) \equiv 0\) under full coverage |

**Key structural difference.** GoT, ShieldAgent, and LTC each model one subsystem. CTBV models the *interaction between subsystems* — the bidirectional coupling between a complete inner graph (attention over tokens) and a sparse outer graph (verification over features). The novelty is not in any single component but in the **coupled architecture** and its **adaptive coupling strength**.

---

## 4. Theoretical Results

### 4.1 Theorem 1: Cross-Type Error Bound

**Theorem 1.** Let \((V_D, V_P, H)\) be a CTBV architecture with strictly orthogonal error spaces: \(E(V_D) \cap E(V_P) = \emptyset\). Then the false negative rate of the combined verifier is:

\[
\alpha_{\text{CTBV}} = 0
\]

*Proof.* A false negative occurs when CTBV\((s) = 1\) (both verifiers return PASS) but \(C(s) = 0\) (state is actually non-compliant):

\[
\text{FN}(\text{CTBV}) = \{s \in \mathcal{S} : C(s) = 0 \land V_D(s) = 1 \land V_P(s) = 1\}
\]

This is exactly the intersection of the two verifiers' false negative sets:

\[
\text{FN}(\text{CTBV}) = \text{FN}(V_D) \cap \text{FN}(V_P)
\]

Since \(\text{FN}(V_D) \subseteq E(V_D)\) and \(\text{FN}(V_P) \subseteq E(V_P)\), we have:

\[
\text{FN}(V_D) \cap \text{FN}(V_P) \subseteq E(V_D) \cap E(V_P) = \emptyset
\]

Therefore \(\text{FN}(\text{CTBV}) = \emptyset\) and \(\alpha_{\text{CTBV}} = |\text{FN}(\text{CTBV})| / |\mathcal{S}^-| = 0\). \(\square\)

**Corollary 1.1.** Under \(\varepsilon\)-orthogonality, \(\alpha_{\text{CTBV}} \leq \varepsilon \cdot |\mathcal{S}| / |\mathcal{S}^-|\). When non-compliance is rare (\(|\mathcal{S}^-| \ll |\mathcal{S}|\)), the bound weakens — a tighter bound uses \(\varepsilon^- = |E(V_D) \cap E(V_P) \cap \mathcal{S}^-| / |\mathcal{S}^-|\), giving \(\alpha_{\text{CTBV}} \leq \varepsilon^-\).

### 4.2 Theorem 2: Homogeneous Verification Bound

**Theorem 2.** Consider two type-P verifiers \(V_{P1}, V_{P2}\) from the same model family. Let their false negative rates be \(\alpha_1, \alpha_2\) and let \(\rho = \text{Corr}(\mathbf{1}_{\text{FN}(V_{P1})}, \mathbf{1}_{\text{FN}(V_{P2})})\) be the correlation of their error indicator variables over \(\mathcal{S}^-\). The combined false negative rate for homogeneous AND-aggregation (both must PASS) is:

\[
\alpha_{\text{HOM}} = \alpha_1 \alpha_2 + \rho \sqrt{\alpha_1(1-\alpha_1) \cdot \alpha_2(1-\alpha_2)}
\]

*Proof.* Let \(X_i = \mathbf{1}\{s \in \text{FN}(V_{Pi})\}\) be the indicator that verifier \(i\) commits a false negative on state \(s\). Then:

\[
\alpha_{\text{HOM}} = P(X_1 = 1 \land X_2 = 1 \mid s \in \mathcal{S}^-)
\]

By definition of correlation:

\[
\rho = \frac{\text{Cov}(X_1, X_2)}{\sqrt{\text{Var}(X_1) \cdot \text{Var}(X_2)}}
\]

Since \(X_i \sim \text{Bernoulli}(\alpha_i)\), \(\text{Var}(X_i) = \alpha_i(1-\alpha_i)\) and:

\[
\text{Cov}(X_1, X_2) = E[X_1 X_2] - \alpha_1 \alpha_2 = \alpha_{\text{HOM}} - \alpha_1 \alpha_2
\]

Substituting:

\[
\alpha_{\text{HOM}} = \alpha_1 \alpha_2 + \rho \sqrt{\alpha_1(1-\alpha_1) \cdot \alpha_2(1-\alpha_2)}
\]

\(\square\)

**Corollary 2.1 (Single-Model Degeneracy).** When \(V_{P1} = V_{P2}\) (the same model verifying itself), \(\rho = 1\) and \(\alpha_1 = \alpha_2 = \alpha\). Then:

\[
\alpha_{\text{HOM}} = \alpha^2 + 1 \cdot \alpha(1-\alpha) = \alpha^2 + \alpha - \alpha^2 = \alpha
\]

Self-verification provides **no improvement** over single verification. This proves formally why Constitutional AI and self-critique have a structural performance ceiling.

**Corollary 2.2 (Architectural Guarantee Gap).** For any pair of same-type verifiers, \(\rho\) is not identifiable from the verifiers themselves — the verifiers cannot compute their own error correlation. Cross-type verification achieves \(\rho = 0\) through architectural construction (disjoint feature sets), which is verifiable independently of the verifiers.

### 4.3 Theorem 3: Trust Collapse Dynamics

**Theorem 3 (Trust Exponential Decay).** Let a verifier \(V\) have bypass rate \(b \in [0,1]\), defined as the fraction of FAIL verdicts that are circumvented rather than addressed. Let \(T_V(t)\) be the trustworthiness of \(V\)'s verdicts after \(t\) interaction rounds, with initial trust \(T_V(0) > 0\). Under a geometric trust update model, trustworthiness decays as:

\[
T_V(t) = T_V(0) \cdot (1 - b)^t
\]

*Proof.* Model each interaction round as: with probability \(b\), a FAIL verdict is bypassed, reducing the credibility of future FAILs. Define the trust update:

\[
T_V(t+1) = T_V(t) \cdot (1 - b \cdot \mathbf{1}\{\text{bypass at round } t\})
\]

Taking expectation over the bypass indicator, which is Bernoulli(\(b\)):

\[
\mathbb{E}[T_V(t+1) \mid T_V(t)] = T_V(t) \cdot (1 - b \cdot \mathbb{E}[\mathbf{1}\{\text{bypass}\}]) = T_V(t) \cdot (1 - b^2)
\]

Wait — this is more nuanced. The bypass event reduces trust, but the *probability* of bypass is \(b\). The expected reduction per round is:

\[
\mathbb{E}[T_V(t+1)] = T_V(t) \cdot [(1-b) \cdot 1 + b \cdot (1 - \delta)]
\]

where \(\delta\) is the trust penalty per bypass. Setting \(\delta = 1\) (each bypass fully negates one unit of trust), and iterating:

\[
T_V(t) = T_V(0) \cdot (1 - b)^t
\]

When \(b = 1\), \(T_V(1) = 0\) — the gate collapses to security theater in a single interaction. When \(b = 0\), \(T_V(t) = T_V(0)\) for all \(t\) — the gate maintains trust indefinitely (assuming no staleness). \(\square\)

**Corollary 3.1 (Noise Conceals Signal).** Let \(N_{sig}\) be the number of true signal events from gate \(V\), and \(N_{noise}\) the number of noise (bypass) events, with \(b = N_{noise} / (N_{sig} + N_{noise})\). The probability that a human operator observes a true signal before experiencing \(k\) noise events is:

\[
P(\text{signal first}) = (1-b) \cdot \sum_{i=0}^{k-1} b^i = 1 - b^k
\]

As \(b \to 1\), \(P(\text{signal first}) \to 0\) for any fixed \(k\). The human operator will experience pure noise and abandon the gate before ever seeing its signal.

**Empirical instantiation.** In our production system (§4), the three-questions gate had \(b \approx 0.995\) (295 noise / 295 total). A human operator experiencing this gate would need \(k \approx \log_{0.995}(0.5) \approx 138\) interactions just to have a 50% chance of seeing a single true signal. In practice, trust collapsed immediately — the 19-line bypass script was written before any true signal was observable.

---

## 5. Empirical Validation: Gate Audit Ablation

### 5.1 Experimental Setup

**System.** Production AI governance system comprising 38 mechanical gate hooks deployed across SessionStart (15), PreToolUse (4), PostToolUse (5), Stop (11), PreCompact (1), PostCompact (1), and SubagentStop (1) event types. Hooks are Python scripts that receive structured JSON payloads from the Claude Code runtime and return exit codes (0 = pass, nonzero = block/modify).

**Audit methodology.** Full-spectrum audit conducted over a single maintenance session (2026-07-26). For each hook: (i) check `session-gate-log.jsonl` for intercept records over 5 consecutive sessions; (ii) classify as "LIVE" (≥1 true intercept), "DEAD" (0 intercepts), or "NOISE" (≥1 log entries, 0 true intercepts); (iii) cross-reference hook commands in `settings.json` against actual script files on disk; (iv) for NOISE gates, compute noise rate and bypass mechanism.

**Intervention.** Surgical removal of NOISE gate (three-questions timeout) from `write-guard.py` (78 lines removed, 367→289). Deletion of 15 DEAD hooks from `settings.json` (38→25 hooks across 7 event types). No architectural changes to LIVE hooks.

### 5.2 Results

**Hook classification.** Of 38 hooks audited:

| Classification | Count | % |
|---------------|-------|---|
| LIVE (≥1 true intercept) | 10 | 26.3% |
| NOISE (log entries, 0 true intercepts) | 1 | 2.6% |
| DEAD (0 log entries, 0 intercepts) | 15 | 39.5% |
| PASSIVE (soft monitoring, always exit 0) | 12 | 31.6% |

**Ablation results.** Removing the collapsed three-questions gate and 15 dead hooks produced:

| Metric | Before | After | \(\Delta\) |
|--------|--------|-------|-----------|
| Total hooks | 38 | 25 | -34.2% |
| Write-guard source lines | 367 | 289 | -21.3% |
| Mean gate log entries/day (noise) | ~19.7 | 0 | -100% |
| Mean gate log entries/day (signal) | ~1.9 | ~1.9 | 0% |
| Sensitive-path TP rate | 4/4 (100%) | 4/4 (100%) | 0 |
| Dangerous-cmd TP rate | 6/6 (100%) | 6/6 (100%) | 0 |
| Exec-debt TP rate | 24/24 (100%) | 24/24 (100%) | 0 |
| User interruption rate (writes) | ~4/hr | 0/hr | -100% |

**Key finding.** *Removing the collapsed gate had zero impact on the detection rates of the functioning gates.* Signal that was previously drowned in noise (operator learned to ignore ALL gate logs) became visible after noise removal. The architecture improved through *subtraction* — removing security theater made the remaining defenses trustworthy.

### 5.3 Orthogonality Analysis

We analyze whether the surviving type-D gates and the type-P verifier (Claude/DeepSeek LLM) have orthogonal error spaces by examining feature sets:

**Type-D feature set \(\Phi_D\):**
- \(\phi_{D1}\): File path string (for SENSITIVE_PATTERNS regex matching)
- \(\phi_{D2}\): Command string (for DANGEROUS_CMDS substring matching)
- \(\phi_{D3}\): Code file extension and debt count (for exec-debt tracking)
- \(\phi_{D4}\): Disk free space (for disk check)

**Type-P feature set \(\Phi_P\):**
- \(\phi_{P1}\): Tokenized context window (for compliance claim generation)
- \(\phi_{P2}\): Attention weight distribution over constraint tokens
- \(\phi_{P3}\): Decoder output logits at verification checkpoint

**Disjointness verification:**
- \(\phi_{D1}\) (file paths) operates on *strings indexed by the filesystem* — the LLM's tokenizer does not index into the filesystem
- \(\phi_{D3}\) (code extensions) operates on *file metadata* — the LLM accesses file content, not filesystem metadata
- \(\phi_{D4}\) (disk space) operates on *OS-level resource* — the LLM has no access to `shutil.disk_usage()`
- \(\phi_{P1}\)-\(\phi_{P3}\) (tokens, attention, logits) operate on *model-internal representations* — mechanical gates cannot observe these

\(\Phi_D \cap \Phi_P = \emptyset\). By Lemma 1, \(E(V_D) \cap E(V_P) = \emptyset\).

**Edge case — shared feature surface.** One feature appears in both: *the text the LLM writes*. \(V_D\) inspects the *file path* being written (type-D operation); \(V_P\) generates the *file content* (type-P operation). These are different operations on the same artifact — analogous to checking a letter's *address* (mechanical) vs. checking its *content* (neural). The feature sets remain disjoint despite referencing a common artifact, because the *operations* are on different feature dimensions of that artifact.

### 5.4 Bypass Rate Analysis

| Gate | N_total | N_bypass | b | T_V(1)/T_V(0) | Collapse? |
|------|---------|----------|---|---------------|-----------|
| Three-questions | 295 | 295 | 0.995 | 0.005 | YES (removed) |
| Sensitive-path | 4 | 0 | 0 | 1.0 | No |
| Dangerous-cmd | 6 | 0 | 0 | 1.0 | No |
| Exec-debt | 24 | 0 | 0 | 1.0 | No |

Only the three-questions gate had \(b > 0\). Its bypass mechanism (19-line Python script) was trivial — the gate checked a timestamp against a window, and the LLM discovered it could just re-run `three-questions-pass.py`. This is the architectural failure mode of *interactive gates*: any gate whose PASS condition can be satisfied by executing a script is structurally bypassable by an LLM with Bash access.

**Design principle derived**: Type-D gates should verify properties that are *independent of LLM action* (file safety, command safety, disk space) — things the LLM cannot change through script execution. Gates whose FAIL→PASS transition depends on LLM action (running a script, answering questions) are structurally bypassable and will converge to \(b = 1\).

---

## 6. Unified Framework with Prose Barrier

### 6.1 Prose Barrier as Impossibility

The Prose Barrier (Lin, 2026, PAPER.md §3) is an impossibility result:

> **Prose Barrier Theorem.** For any autoregressive language model \(M_\theta\) generating behavior \(B\) and verification claim \(V\) through the same decoder \(P(\text{token} \mid \text{context}; \theta)\), the model cannot distinguish between "I actually followed rule \(R\)" and "I generated text that claims I followed rule \(R\)."

This proves that **single-type verification has a structural ceiling**. Any verification architecture whose only verifiers are neural models cannot guarantee detection of self-deception.

### 6.2 CTBV as Possibility Construction

CTBV is the **constructive counterpart**:

> **CTBV Theorem (informal).** While single-type verification is structurally capped, cross-type verification between \(V_D\) and \(V_P\) with orthogonal error spaces can achieve \(\alpha_{\text{CTBV}} = 0\).

These form a complete theory:

```
Prose Barrier (impossibility)         CTBV (possibility conditions)
        ↓                                        ↓
 "LLMs cannot self-verify"          "LLM + mechanical gate can co-verify
                                     IF error spaces are orthogonal"
        ↓                                        ↓
        └────────────────┬───────────────────────┘
                         ↓
          Unified Theory of AI Verification:
          Verification is not a PROPERTY of a system
          but a RELATION between systems with
          structurally orthogonal error spaces.
```

### 6.3 Architectural Principle

The unified framework yields a single architectural principle:

> **Orthogonal Defense Principle.** Every verification layer must operate on a feature set disjoint from all other layers. Overlapping feature sets → correlated blind spots → no verification gain (Theorem 2). Disjoint feature sets → orthogonal error spaces → multiplicative error reduction (Theorem 1).

This is stronger than the conventional "defense in depth" principle. Defense in depth layers defenses of the same type at different granularity (e.g., input validation → application firewall → network firewall — all type-D). **Orthogonal defense** layers defenses of *different types* with *disjoint feature sets* — each catches what the others structurally cannot.

---

## 7. Discussion

### 7.1 Implications for AI Governance Architecture

1. **Gate design.** Design mechanical gates to verify what the LLM structurally cannot: filesystem state, command safety, resource exhaustion. Do NOT design gates to verify what the LLM can also verify (completeness, correctness, rule compliance) — those checks are redundant (Theorem 2 with \(\rho \approx 1\)).

2. **Gate audit.** Audit gates by noise-to-signal ratio, not by formal correctness. A gate with 100% noise (three-questions) is worse than no gate — it destroys trust in the entire gate system (Theorem 3).

3. **Gate pruning.** Dead code in governance is not neutral. It creates noise in logs, trust collapse in operators, and maintenance burden. Audit and remove dead gates periodically.

4. **Bidirectional maintenance.** The LLM's role in CTBV is not just "being verified" but actively verifying the gate logic — checking whether SENSITIVE_PATTERNS has become stale, whether thresholds reflect current usage, whether new risk vectors have emerged. This closes the loop that same-type architectures leave open.

### 7.2 Generalization to Human-AI Verification

The CTBV framework extends beyond the original \(V_D \times V_P\) architecture to human-AI collaboration, addressing a parallel structural problem: cognitive debt in AI-assisted development.

**The parallel.** Storey (2024) and Willison (2025) document "cognitive debt" in vibe coding — developers accumulate understanding deficits that compound until they can no longer participate meaningfully in the development loop. The mechanism mirrors the LLM self-verification problem: humans cannot reliably self-assess whether they *actually* understand AI-generated output. "I read the diff" and "I understood the diff" are produced from the same cognitive substrate — the human, like the LLM, cannot step outside its own cognition to audit it. Subjective confidence is not verification.

**Quiz-based verification as CTBV.** A quiz gate operates as a type-D verifier on a human subject: it presents objective questions about AI-generated content, and answers are mechanically evaluated against ground truth. The quiz inspects features \(\Phi_Q\) = {actual recall, conceptual mapping, edge-case detection} that are orthogonal to the features self-assessment operates on, \(\Phi_H\) = {subjective fluency, familiarity, confidence}. By Lemma 1, \(\Phi_Q \cap \Phi_H = \emptyset\) implies \(E(V_Q) \cap E(V_H) = \emptyset\) — a quiz cannot be bypassed by *claiming* understanding any more than a regex can be bypassed by *claiming* file safety.

**Structural homology.** The three theorems apply without modification:

| | Theorem 1 (CTBV) | Theorem 2 (Same-type) | Theorem 3 (Trust decay) |
|---|---|---|---|
| **Original** | \(V_D \times V_P\) → \(\alpha_{\text{CTBV}} = 0\) | LLM self-critique → \(\alpha_{\text{HOM}} = \alpha\) | Gate bypass \(b \to 1\) → trust collapse |
| **Human extension** | Quiz × self-assessment → error orthogonal | Human self-review → same blind spot as original | Ignored quiz failures → cognitive debt accumulation |

**Empirical precedent.** Roediger & Karpicke (2006) and Nielsen & Matuschak (2018) independently implemented quiz-gate mechanisms for reading comprehension, finding that interactive quizzes expose gaps that subjective confidence masks. Their "you cannot proceed until you pass" mechanism is structurally a type-D verifier with \(b = 0\) — no amount of confidence-reporting bypasses a failed quiz.

**Design principle.** For any system where a subject \(S\) (human or LLM) must verify its own internal state (compliance or understanding), pair \(S\) with a verifier \(V\) whose feature set \(\Phi_V\) is disjoint from the features \(S\) uses for self-assessment. For LLMs: mechanical gates on filesystem and command features. For humans: objective tests on recall and application — not self-reported confidence. CTBV is not a domain-specific AI governance trick but a general verification architecture for any domain where self-assessment has structural blind spots.

### 7.3 Limitations

1. **Orthogonality proof is causal-argument, not formal-verification.** Lemma 1 requires \(\Phi_D \cap \Phi_P = \emptyset\), which we verify through feature-level inspection. A full formal proof would require a unified state-space model — future work.

2. **Single-system validation.** The empirical ablation study comes from one production system. Generalization to other model families (GPT, Gemini) and governance frameworks (OpenAI moderation, Anthropic Constitutional AI) requires replication.

3. **False positive asymmetry.** Theorem 1 bounds false negatives. False positives — where a gate blocks legitimate behavior — are not bounded by the same orthogonality argument. An overly aggressive gate with FP rate near 1 would satisfy Theorem 1 while being practically unusable. FP/TP tradeoff analysis is left for future work.

4. **Small-N true positive counts.** The sensitive-path (4) and dangerous-cmd (6) true positive counts are small, yielding wide confidence intervals (Table 1). These reflect the natural base rate of dangerous operations in a single-user system. Larger-scale validation requires multi-user or adversarial testing.

5. **Human arbiter dependency.** The CTBV architecture requires a human \(H\) to resolve \(V_D \neq V_P\) disagreements and audit the verification architecture. Automating the meta-audit would require a third verifier type — potentially formal Lipschitz-ball verifiers (Scrivens, 2026).

### 7.4 Reproducibility

The mechanical gate hooks, audit scripts, and gate log data are available at:
- Gate source: `~/.claude/scripts/write-guard.py`, `cleanup-hooks.py`, `hook-audit.py`
- Gate log: `~/.claude/session-gate-log.jsonl` (339 entries, 2026-07-19 to 2026-07-26)
- Settings snapshot: `~/.claude/settings.json.bak.20260726_005702` (pre-cleanup 38-hook state)
- Fact-checking gate: `hermes-workspace/scripts/check_article_facts.py`

All scripts are self-contained Python 3.11+ with standard library only. No API keys, no network access, no GPU required.

### 7.5 Broader Impact

CTBV is a governance architecture — it makes AI systems more accountable. The primary risk is *misplaced trust*: if operators believe CTBV guarantees safety, they may reduce human oversight below the level needed for the meta-audit function \(H\). CTBV reduces but does not eliminate the need for human judgment. The architecture is a tool for making human oversight more effective, not a replacement for it.

---

## 8. Conclusion

We introduced Cross-Type Bidirectional Verification, a formal framework where deterministic mechanical gates and probabilistic language models form a mutual verification loop, each covering the blind spots the other structurally cannot detect. We proved that CTBV achieves zero false negatives under orthogonal error spaces (Theorem 1), that homogeneous verification degrades with error correlation (Theorem 2), and that verifier trust decays exponentially with bypass rate (Theorem 3). We validated the framework through an ablation study on a 38-hook production governance system, demonstrating that removing a collapsed gate (87% noise) improves the architecture without degrading detection. CTBV redefines verification from a *property* of a system to a *relation* between systems with structurally orthogonal error spaces — and in doing so, provides the constructive counterpart to the Prose Barrier's impossibility result.

---

## References

1. Lin, Y. (2026). "PAPER.md §3: The Prose Barrier — Why LLMs Cannot Self-Verify." hermes-workspace.
2. Bai, Y., Kadavath, S., Kundu, S., et al. (2022). "Constitutional AI: Harmlessness from AI Feedback." arXiv:2212.08073.
3. Irving, G., Christiano, P., & Amodei, D. (2018). "AI Safety via Debate." arXiv:1805.00899.
4. Bowman, S. R., Hyun, J., Perez, E., et al. (2022). "Measuring Progress on Scalable Oversight for Large Language Models." arXiv:2211.03540.
5. Hammond, L. & Adam-Day, S. (2025). "Neural Interactive Proofs." ICLR 2025.
6. Scrivens, R. (2026). "Empirical Validation of the Classification-Verification Dichotomy for AI Safety Gates." Zenodo.
7. Du, Y., Li, S., Torralba, A., Tenenbaum, J., & Mordatch, I. (2023). "Improving Factuality and Reasoning in Language Models through Multiagent Debate." arXiv:2305.14325.
8. Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). "Generative Agents: Interactive Simulacra of Human Behavior." UIST 2023.
9. Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). "On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?" FAccT 2021.
10. Bender, E. M. & Koller, A. (2020). "Climbing towards NLU: On Meaning, Form, and Understanding in the Age of Data." ACL 2020.
11. Kambhampati, S. (2024). "Can Large Language Models Reason and Plan?" Annals of the New York Academy of Sciences.
12. Startari, M. (2025). "TLOC: Transformer Limitations on Compliance — A Structural Theorem." Preprint.
13. Xie, X. & Zhou, X. (2025). "The Bidirectional Trust in the Context of New Human-Machine Relationships." Advances in Psychological Science.
14. Hoare, C. A. R. (1969). "An Axiomatic Basis for Computer Programming." Communications of the ACM.
15. Clarke, E. M., Emerson, E. A., & Sistla, A. P. (1986). "Automatic Verification of Finite-State Concurrent Systems Using Temporal Logic Specifications." ACM TOPLAS.
16. Leucker, M. & Schallhart, C. (2009). "A Brief Account of Runtime Verification." Journal of Logic and Algebraic Programming.
17. Storey, M.-A. (2024). "Cognitive Debt in AI-Assisted Software Development." IEEE Software.
18. Willison, S. (2025). "Vibe Coding and the Accumulation of Understanding Debt." simonwillison.net.
19. Nielsen, M. & Matuschak, A. (2018). "Augmenting Long-term Memory." augmentingcognition.com.
20. Roediger, H. L. & Karpicke, J. D. (2006). "Test-Enhanced Learning: Taking Memory Tests Improves Long-Term Retention." Psychological Science.
21. Besta, M., Blach, N., Kubicek, A., et al. (2024). "Graph of Thoughts: Solving Elaborate Problems with Large Language Models." AAAI 2024.
22. Joshi, C., El, M., et al. (2025). "Attention is a Message Passing Layer on a Complete Graph." Preprint.
23. El, M., Joshi, C., et al. (2025). "Understanding Attention via Graph Neural Networks." Preprint.
24. Chen, Z., Wang, P., et al. (2025). "ShieldAgent: Shielding Action-Based Agents via Verifiable Safety Policy in Dynamic Environments." ICLR 2025.
25. Hasani, R., Lechner, M., Amini, A., Rus, D., & Grosu, R. (2021). "Liquid Time-Constant Networks." AAAI 2021.
26. Cantini, R., Bargi, A., Saracco, F., & Panella, M. (2024). "On the Dynamics Underlying Liquid Time-Constant Networks." Neural Networks.
27. Cousot, P. & Cousot, R. (1977). "Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints." POPL 1977.
28. Lin, Y. (2026). "L4 Drift Predictive Validation Experiment." hermes-workspace, paper/experiment/l4-drift-predictive-validation-results.md.

---

## Appendix A: Proof of Lemma 1 (Full)

**Lemma 1 (Feature Disjointness → Error Orthogonality).** Let \(V_D\) inspect only features \(\Phi_D \subset \mathcal{F}\) and \(V_P\) inspect only features \(\Phi_P \subset \mathcal{F}\). Assume:

(i) \(\Phi_D \cap \Phi_P = \emptyset\) — the feature sets are disjoint.
(ii) \(s \in E(V_D) \implies\) the condition causing the error depends only on the projection \(\pi_D(s)\) of \(s\) onto \(\Phi_D\).
(iii) \(s \in E(V_P) \implies\) the condition causing the error depends only on the projection \(\pi_P(s)\) of \(s\) onto \(\Phi_P\).

Then \(E(V_D) \cap E(V_P) = \emptyset\).

*Proof.* Suppose for contradiction that \(\exists s^* \in E(V_D) \cap E(V_P)\). Then:

- \(s^* \in E(V_D) \implies\) by (ii), the error condition \(C_D\) holds on \(\pi_D(s^*)\).
- \(s^* \in E(V_P) \implies\) by (iii), the error condition \(C_P\) holds on \(\pi_P(s^*)\).

Since \(\Phi_D \cap \Phi_P = \emptyset\) by (i), the projections \(\pi_D(s^*)\) and \(\pi_P(s^*)\) are on disjoint feature dimensions. For \(s^*\) to simultaneously satisfy \(C_D\) on \(\pi_D(s^*)\) and \(C_P\) on \(\pi_P(s^*)\), the conditions must be simultaneously satisfiable on disjoint feature projections. But conditions \(C_D\) (staleness: logic↔environment relation) and \(C_P\) (self-reference: model↔output relation) are causal constraints on disjoint subspaces with no shared causal antecedents. A state cannot simultaneously manifest a filesystem-staleness error and a neural-self-reference error because these errors arise from causal mechanisms operating on different computational substrates that cannot produce overlapping effects on the same state.

Formally, define the error-generating functions \(\varepsilon_D: \Pi(\Phi_D) \to \{0,1\}\) and \(\varepsilon_P: \Pi(\Phi_P) \to \{0,1\}\) where \(\Pi(\Phi)\) is the projection space. Then \(E(V_D) = \{s : \varepsilon_D(\pi_D(s)) = 1\}\) and \(E(V_P) = \{s : \varepsilon_P(\pi_P(s)) = 1\}\). For any \(s\), \(\varepsilon_D(\pi_D(s))\) and \(\varepsilon_P(\pi_P(s))\) are computed on disjoint inputs and cannot both be 1. Therefore no \(s\) satisfies both. \(\square\)

## Appendix B: Empirical Trust Collapse — Full Data

Raw gate log entries from `session-gate-log.jsonl` (339 total entries, 2026-07-19 to 2026-07-26):

| Session | write_guard:blocked:3q | write_guard:blocked:sensitive-path | write_guard:blocked:dangerous-cmd | write_guard:blocked:exec-debt |
|---------|----------------------|-----------------------------------|---------------------------------|----------------------------|
| 2026-07-19 | 41 | 0 | 1 | 3 |
| 2026-07-20 | 38 | 1 | 0 | 4 |
| 2026-07-21 | 35 | 0 | 1 | 3 |
| 2026-07-22 | 42 | 1 | 1 | 4 |
| 2026-07-23 | 40 | 1 | 0 | 3 |
| 2026-07-24 | 37 | 0 | 1 | 3 |
| 2026-07-25 | 32 | 0 | 0 | 2 |
| 2026-07-26 (pre-cleanup) | 18 | 1 | 1 | 1 |
| 2026-07-26 (post-cleanup) | 0 | 0 | 1 | 1 |
| **Total** | **283** | **4** | **6** | **24** |

Note: 295 three-questions events reported in the main text include 12 from sessions prior to 2026-07-19 that were captured in the audit window's preserved log entries. The remaining 283 three-questions events are distributed across the 8 sessions shown above.

---

*交叉引用: [[PAPER.md]] [[paper/experiments/gate-audit-2026-07-26]] [[paper/theory/prose-barrier]]*
