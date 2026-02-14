# Phase 0 — Lock the Control Plane Narrative (1-2 hours)

Goal
- Produce a single-paragraph positioning statement that anchors all downstream docs.
- Clearly articulate the architectural reframe from intent router to control plane.

Primary Deliverable
- POSITIONING.md (in repo root; reused on websites and in paper).

Inputs
- Zenodo v1 record for HNIR: https://zenodo.org/records/18110920
- ProblemStatement.md (CCP for safety-critical AI systems).
- Competitive landscape analysis (NeMo Guardrails, Semantic Router, Guardrails AI, Lakera, etc.).

Outputs
- POSITIONING.md with six components:
  1) What v1 said (deterministic intent routing to reduce LLM cost/latency)
  2) Why that framing was wrong (LLMs are better at intent understanding; competing on classification is a losing battle)
  3) What v2 actually is (a deterministic execution control plane that governs what happens after intent is understood)
  4) The three capabilities (control command shortcuts, policy-gated action execution, state machine governance)
  5) What you will measure (policy compliance rate, prompt injection resistance, control command latency, state transition correctness, audit completeness)
  6) Why this matters (as AI agents become operational systems in regulated domains, deterministic execution governance is the missing architectural layer)
- Explicit scope boundary: what CCP does NOT do (it does not understand intent better than LLMs, does not replace LLMs, does not do content generation).
- The key differentiator sentence (precisely scoped): "A deterministic CCP cannot be prompt-injected at the execution boundary because policy enforcement is code, not a model. However, CCP does not prevent adversarial reasoning within the LLM — if an attacker manipulates the LLM into proposing an action that is correctly classified as safe by the policy gate, CCP will allow it. CCP guarantees that policy is enforced as written; it does not guarantee that the policy covers all adversarial scenarios."
- A "Threat Model Boundary" note (what CCP protects against vs. what it does not).
- A short "Limits" note (3-5 bullets).

Step-by-step
1) Articulate the v1-to-v2 reframe
   - v1 thesis: "Route simple intents deterministically to save cost."
   - v2 thesis: "Govern execution deterministically because LLMs cannot provide safety guarantees."
   - The shift is from cost optimization to safety architecture.

2) Define the three capability layers
   - Control Command Shortcuts: system commands (help, cancel, undo, reset, status) handled without LLM invocation — not because CCP understands them better, but because they are control signals, not conversational content (like Ctrl+C doesn't need AI interpretation).
   - Policy Gate: LLM proposes an action → CCP classifies it (read/write/delete/irreversible) → checks authorization, enforces confirmation requirements, validates scope → ALLOW / DENY / REQUIRE_CONFIRMATION.
   - State Machine: explicit conversation states with valid transitions, preconditions, and timeout rules. LLM reasons freely within a state but cannot skip states or violate transitions.

3) Define the competitive positioning
   - vs NeMo Guardrails: NeMo uses LLMs internally for intent classification → prompt-injectable. CCP is fully deterministic → not prompt-injectable.
   - vs Guardrails AI / Lakera / Arthur: these are input/output filters (binary allow/block). CCP can resolve requests, enforce state, and gate execution — not just filter.
   - vs Semantic Router: routing-only library with no response generation, policy, or state management.
   - vs LangChain/LangGraph: orchestration frameworks where safety is a bolt-on, not architectural.

4) Define measurable claims
   - Policy compliance rate (% of actions correctly gated).
   - Prompt injection resistance (% of adversarial inputs that bypass CCP vs bypass NeMo Guardrails).
   - Control command latency (sub-ms for deterministic path vs LLM inference latency).
   - State transition correctness (% of invalid transitions blocked).
   - Audit completeness (% of decisions with deterministic reason codes).

5) Draft the single paragraph
   - 5-7 sentences max.
   - Must include all six components.
   - Include one concrete example (e.g., "When an LLM agent proposes deleting a patient record, the CCP checks authorization, enforces confirmation, and logs the decision with a deterministic reason code — regardless of how the LLM was prompted.").

6) Add threat model boundary
   - CCP DOES protect against: unauthorized action execution (policy gate denies actions that violate rules regardless of how the LLM was prompted), state bypass (LLM cannot skip states or violate transition rules), and direct prompt injection at the execution boundary (injected instructions cannot override code-based policy checks).
   - CCP DOES NOT protect against: adversarial reasoning that produces correctly-classified actions (if the LLM is manipulated into proposing a READ instead of a DELETE, the policy gate sees a READ and allows it), social engineering that doesn't result in gated actions, adversarial training data or model-level attacks, or policy definitions that fail to cover edge cases.
   - The honest claim: "CCP guarantees that policy is enforced as written. The quality of protection depends entirely on the quality of the policy definitions."

7) Add scope boundaries and limits
   - CCP does not replace LLMs for open-ended reasoning or generation.
   - CCP does not claim to understand intent better than LLMs.
   - CCP effectiveness depends on correct policy and state machine configuration — a misconfigured policy gate is a false sense of security.
   - Edge cases at the boundary between control commands and conversational content require careful design.
   - State machine complexity scales with workflow complexity; YAML-based definitions may not scale to 50+ state workflows without tooling support.
   - Regulatory compliance claims (HIPAA, GDPR, SOC2) require domain-specific validation with compliance professionals — CCP provides the audit infrastructure but does not itself constitute compliance.

7) Stress-test the paragraph
   - Remove hype; keep scope bounded and falsifiable.
   - Ensure it reads as a systems architecture contribution, not AI hype.
   - Verify every claim maps to something measurable or demonstrable.

8) Save to POSITIONING.md
   - Place at repo root.
   - This file becomes the canonical source for README, paper abstract, and website text.

Acceptance Criteria
- POSITIONING.md is one paragraph (5-7 sentences) plus limits.
- All six components are present and explicit.
- The v1-to-v2 reframe is clearly stated (intent router -> control plane).
- The three capability layers are named and distinguished.
- The prompt injection resistance differentiator is stated.
- Claims are bounded and tied to metrics.
- Scope boundaries and non-goals are explicit.

Known Gaps and Mitigations
- GAP: "Prompt injection immunity" is easy to overstate. MITIGATION: Every mention of this claim must include the scope boundary (execution boundary only, policy-as-written only). The paper's threat model section (Phase 5, Section 8) must make this distinction explicitly.
- GAP: Competitive positioning against NeMo Guardrails risks being unfair if based on a simplified mock. MITIGATION: Phase 3 must use the actual NeMo Guardrails library, not a simplified reimplementation.
- GAP: Regulatory compliance claims (HIPAA, defense) are theoretical without domain validation. MITIGATION: All regulatory language must be framed as "CCP provides the audit infrastructure for" not "CCP ensures compliance with." Seek domain expert review before publication.

Handoff Notes
- Downstream docs must reuse this paragraph verbatim or as the base text.
- The competitive positioning informs the Related Work section in Phase 5.
- If any later phase conflicts, return to Phase 0 and reconcile.
