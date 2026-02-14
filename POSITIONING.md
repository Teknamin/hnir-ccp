# POSITIONING.md

**Canonical positioning for HNIR-CCP (Conversation Control Plane). This text is the source for README, paper abstract, patent claims, and website copy.**

---

## 1. Core Positioning

HNIR v1 proposed deterministic intent routing as a cost and latency optimization for conversational AI, intercepting simple queries before they reached an LLM. That framing was wrong: LLMs are fundamentally better at intent understanding, and competing on classification accuracy against neural models is a losing architectural bet. HNIR v2 reframes the contribution as a **deterministic execution control plane (CCP)** — a pre-execution governance layer that controls what happens *after* an LLM has understood intent. CCP provides three capabilities: **control command shortcuts** that handle system signals without LLM invocation, a **policy gate** that classifies and authorizes proposed actions before execution, and **state machine governance** that enforces explicit conversation state transitions with preconditions and timeout rules. When an LLM agent proposes deleting a patient record, the CCP checks authorization, enforces confirmation, validates workflow state, and logs the decision with a deterministic reason code — regardless of how the LLM was prompted. As AI agents become operational systems in regulated domains — healthcare, finance, defense — deterministic execution governance is the missing architectural layer between probabilistic reasoning and irreversible action.

---

## 2. The Three Capability Layers

### Control Command Shortcuts

System commands — help, cancel, undo, reset, status — are control signals, not conversational content. CCP handles them deterministically without LLM invocation, the same way Ctrl+C does not require AI interpretation. This eliminates unnecessary inference latency for procedural operations and guarantees consistent behavior regardless of model state or prompt context.

### Policy Gate

The LLM proposes an action. CCP classifies it (read / write / delete / irreversible), checks authorization against defined policy rules, enforces confirmation requirements for destructive operations, and validates scope constraints. The gate returns one of three verdicts: **ALLOW**, **DENY**, or **REQUIRE_CONFIRMATION**. Policy enforcement is deterministic code execution, not model inference — it cannot be bypassed by adversarial prompts at the execution boundary.

### State Machine Governance

Conversations in safety-critical workflows are not stateless exchanges. CCP maintains explicit conversation states with defined valid transitions, preconditions, and timeout rules. The LLM reasons freely within a state but cannot skip states, violate transition preconditions, or bypass required workflow steps. A triage conversation cannot jump from intake to prescription without completing assessment; a data deletion workflow cannot execute without passing through confirmation.

---

## 3. Threat Model Boundary

### What CCP Protects Against

| Threat | Mechanism |
|--------|-----------|
| Unauthorized action execution | Policy gate denies actions that violate rules, regardless of how the LLM was prompted to propose them |
| State bypass attacks | LLM cannot skip states or violate transition preconditions; state machine is code, not inference |
| Direct prompt injection at the execution boundary | Injected instructions cannot override code-based policy checks or state transition rules |
| Unconfirmed destructive actions | Irreversible operations require explicit user confirmation enforced by the policy gate |
| Audit gaps | Every decision produces a deterministic reason code and structured log entry |

### What CCP Does Not Protect Against

| Threat | Reason |
|--------|--------|
| Adversarial reasoning producing correctly-classified actions | If the LLM is manipulated into proposing a READ instead of a DELETE, the policy gate sees a READ and allows it — the attack operates below CCP's classification boundary |
| Social engineering that does not result in gated actions | Conversational manipulation that stays within allowed action categories is outside CCP's scope |
| Model-level attacks (adversarial training data, weight poisoning) | CCP operates at the application layer, not the model layer |
| Policy definitions that fail to cover edge cases | CCP enforces policy as written; it does not generate or improve policy |
| Content generation quality or factual accuracy | CCP governs execution, not reasoning or generation |

**The honest claim:** CCP guarantees that policy is enforced as written. The quality of protection depends entirely on the quality of the policy definitions.

---

## 4. Competitive Positioning

*Based on publicly available data as of February 2026.*

### NeMo Guardrails (NVIDIA, v0.20+)

NeMo Guardrails uses LLM-based intent classification internally (Colang runtime). Published research demonstrates fundamental vulnerabilities: emoji smuggling bypass at 100% attack success rate, and 72.54% jailbreak ASR against guardrail configurations. These findings validate the core CCP thesis — LLM-based classification is fundamentally injectable because the enforcement mechanism shares the attack surface with the threat vector. CCP's policy gate is deterministic code execution, not model inference; it does not share an attack surface with prompt injection.

### Guardrails AI

Guardrails AI uses the same model for generation and safety validation — a same-model-for-generation-and-security design where the model evaluates its own output. Confidence scoring bypass has been documented. CCP separates the enforcement mechanism (deterministic code) from the reasoning mechanism (LLM), eliminating this architectural conflict of interest.

### Semantic Router

Semantic Router is a routing-only library: it classifies input to select a handler but provides no policy enforcement, state management, or action gating. It is complementary to CCP, not competing — Semantic Router could serve as an intent classification front-end with CCP providing execution governance.

### LangChain / LangGraph

LangChain is an orchestration framework where safety is a bolt-on concern, not an architectural primitive. CVE-2025-68664 documents a serialization injection vulnerability. LangGraph adds stateful workflows but has no native policy engine and relies on external guardrails for safety enforcement. CCP provides the missing governance layer that these frameworks assume exists externally.

### Emerging Entrants (2025-2026)

- **Kong AI Gateway**: Adds a prompt guard plugin to API gateway infrastructure — network-level filtering, not execution governance.
- **Pydantic AI**: Introduces a governor pattern and human-in-the-loop tool approval — architecturally aligned with CCP's thesis but limited to tool-call authorization without state machine governance.
- **OpenAI Agents SDK**: Provides agent sandboxing primitives — isolation, not policy enforcement.
- **Agentic AI Foundation (Linux Foundation)**: Industry governance initiative recognizing that agent systems need standardized safety architecture — validates the problem space CCP addresses.

### Industry Consensus

- **OWASP Top 10 for LLM Applications (2025)**: Prompt injection ranked #1, appearing in 73% of production deployments surveyed. The report explicitly states there is "no fool-proof prevention" via LLM-only methods.
- **OWASP Top 10 for Agentic Applications (2026)**: Industry consensus that agentic AI systems require governance architecture beyond prompt-level defenses.

### CCP Differentiation

CCP is the only system combining deterministic policy enforcement, state machine governance, and control command shortcuts in a **pre-execution layer** where policy enforcement is code, not model inference. Existing tools address subsets of this problem (routing, filtering, tool authorization) but none formalize the complete execution governance boundary.

---

## 5. Measurable Claims

All claims are tied to metrics evaluated in Phase 3 (evaluation harness). No claim is made without a corresponding measurement protocol.

| # | Metric | Definition | Target |
|---|--------|------------|--------|
| 1 | **Policy compliance rate** | Percentage of actions correctly gated (allowed, denied, or escalated) according to defined policy rules | Measured against policy test suite; baseline comparison against NeMo Guardrails |
| 2 | **Prompt injection resistance** | Percentage of adversarial inputs that fail to bypass CCP's execution boundary, scoped to action-level attacks (not content-level) | Measured using standardized adversarial prompt datasets |
| 3 | **Control command latency** | Time from input receipt to deterministic response for control commands | Target: sub-millisecond (no LLM inference in path) |
| 4 | **State transition correctness** | Percentage of invalid state transitions blocked by the state machine | Measured against state machine specification with adversarial transition attempts |
| 5 | **Audit completeness** | Percentage of CCP decisions that produce a deterministic reason code and structured log entry; deterministic reproducibility of decision given identical input and state | Target: 100% audit coverage; identical input + state = identical output |

---

## 6. Scope Boundaries and Limits

- **CCP does not replace LLMs.** It governs execution; it does not perform open-ended reasoning, generation, or intent understanding. LLMs remain essential for everything CCP does not handle.

- **CCP does not understand intent.** It classifies proposed actions against policy rules. If an action is correctly classified as safe by the policy gate, CCP allows it — even if the intent behind the action is adversarial. Intent understanding is the LLM's responsibility.

- **Effectiveness depends on policy quality.** A misconfigured or incomplete policy gate is a false sense of security. CCP enforces rules as written; it does not compensate for rules that fail to cover adversarial scenarios.

- **State machine scalability has limits.** YAML-based state definitions are practical for workflows with tens of states. Workflows with 50+ states and complex transition graphs may require dedicated tooling support beyond what the current configuration format provides.

- **Regulatory compliance is not automatic.** CCP provides audit infrastructure (deterministic logging, reason codes, reproducible decisions) that supports compliance workflows. It does not itself constitute HIPAA, GDPR, SOC2, or any other regulatory compliance. Domain-specific validation with compliance professionals is required.

- **Adversarial reasoning within policy bounds is not caught.** If an attacker manipulates the LLM into proposing actions that are individually policy-compliant but collectively harmful, CCP will allow each action. Detecting adversarial reasoning patterns requires model-level or sequence-level analysis outside CCP's scope.

---

## 7. Prior Art and Intellectual Property

- **HNIR v1 Preprint**: Published on Zenodo (DOI: [10.5281/zenodo.18110920](https://zenodo.org/records/18110920)). Established deterministic intent routing as the initial contribution; provided the architectural foundation that the CCP pivot builds upon.

- **HNIR v1 Utility Non-Provisional Patent**: Application No. 63/950,425. Covers the hybrid neuro-symbolic intent routing architecture described in the v1 preprint.

- **CCP (v2)**: The Conversation Control Plane constitutes a distinct invention — a pre-execution governance layer for LLM agent systems — that extends beyond the v1 intent routing claims. Patent application for CCP will be filed with empirical proofs from Phase 3 evaluation results.

---

*This document is the canonical source text for all HNIR-CCP positioning. Downstream documents (README, paper abstract, website, patent claims) must reuse or derive from this text. If any later phase conflicts with this positioning, return here and reconcile before proceeding.*
