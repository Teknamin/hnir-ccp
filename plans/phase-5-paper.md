# Phase 5 — Write v2 Paper Targeting Peer-Reviewed Venue (1-2 weeks part-time)

Goal
- Produce a publishable, evidence-backed v2 paper framed as a systems architecture contribution, targeting a peer-reviewed workshop or conference.

Primary Deliverables
- paper/hnir_v2.tex (LaTeX, formatted for target venue)
- paper/figures/ (architecture diagram, eval plots)

Inputs
- Phase 0 positioning (the thesis)
- Phase 3 evaluation results (the evidence)
- Phase 4 HITL workflow (the governance story)
- Competitive landscape analysis (the differentiation)

Outputs
- Paper draft with all sections mapped to repo artifacts
- Figures generated from eval results
- Artifact map table (section -> repo path)
- Target venue list with submission deadlines

Target Venues (prioritized)
- Workshop at NeurIPS, ICML, or AAAI on AI safety / trustworthy AI / reliable ML
- USENIX Security or IEEE S&P workshop on AI security
- ACM CCS workshop on adversarial ML
- SoCC, EuroSys, or OSDI (systems venues — aligns with the "control plane" framing)
- IEEE Access or ACM Computing Surveys (journal, longer timeline)
- Note: even a workshop paper at a top venue carries significant weight for EB1A criterion 6. Peer review is the key differentiator over Zenodo preprints.

Paper Structure

1) Abstract
   - 150-word version of Phase 0 positioning paragraph.
   - Must include: the reframe (not intent routing — execution governance), the three capabilities, the key metric (prompt injection resistance), and the differentiator (deterministic = not prompt-injectable).

2) Introduction
   - AI agents are transitioning from advisory chatbots to operational systems in regulated domains.
   - Current architectures treat LLMs as the default execution path with safety as post-hoc filtering.
   - This paper proposes a deterministic control plane that governs execution before, during, and after LLM reasoning.
   - The key insight: the right question is not "can we understand intent better than the LLM?" but "how do we guarantee safe execution regardless of how the LLM was prompted?"

3) Motivation: Why Intent Routing Is the Wrong Primitive
   - V1 framed this as intent routing. That framing was wrong.
   - LLMs are genuinely better at intent understanding. Competing on classification is a losing battle.
   - The real gap is execution governance: policy enforcement, state management, and safety invariants.
   - Analogy to distributed systems: data plane (LLM) vs control plane (CCP). Networks don't have routers that "understand packets better" — they have control planes that enforce routing policy.

4) Architecture: Deterministic Conversation Control Plane
   - Three capability layers:
     a) Control Command Shortcuts — system commands resolved without LLM invocation.
     b) Policy Gate — deterministic action classification and enforcement (ALLOW/DENY/CONFIRM).
     c) State Machine — explicit conversation states with validated transitions.
   - Integration model: CCP intercepts LLM-proposed actions at the execution boundary.
   - Key property: deterministic CCP cannot be prompt-injected (it is code, not a model).
   - Architecture diagram (Figure 1).
   - Map to ccp/ module layout.

5) Implementation
   - Registry of control commands (ccp/control/).
   - YAML-driven policy rules with action taxonomy (ccp/policy/).
   - YAML-driven state machine with transition validation (ccp/state/).
   - Structured audit logging with deterministic reason codes (ccp/audit/).
   - LLM integration layer with pre-execution interception (ccp/integration/).

6) Evaluation
   - Experimental setup: scenario traces across four categories (control commands, policy gating, state transitions, adversarial inputs). Traces sourced from: (a) hand-crafted scenarios, (b) published adversarial benchmarks adapted to CCP context (TensorTrust, WASP, Garak probes, InjectBench, LLMail-Inject, Open-Prompt-Injection), (c) real-world CVE-derived attack scenarios (CVE-2025-53773, CVE-2025-32711, CVE-2025-54135/54136). Document the ratio and adaptation methodology.
   - Baselines: raw LLM with real API (system prompt safety only), actual NeMo Guardrails library with Colang flows, actual Guardrails AI library with validators. All baselines use the same LLM backend. Baseline configurations documented in eval/baselines/.
   - Results:
     - Policy compliance rate by system.
     - Prompt injection resistance by system (the headline metric).
     - Control command latency (sub-ms for CCP vs LLM inference latency).
     - State transition correctness.
     - Audit completeness.
     - Deterministic reproducibility (variance across 100 runs).
   - Include clean vs adversarial slice breakdowns.
   - Reference eval/results.md and eval/results.json.

7) HITL: Evolving Policy Without Compromising Safety
   - How the CCP's policy and state machine evolve over time.
   - Gap detection from audit logs.
   - Proposal → safety invariant check → regression eval → human review.
   - Key property: no change that weakens safety can pass the invariant checker.
   - Cite review/ outputs and audit log format.

8) Threat Model and Safety Analysis
   - What CCP protects against:
     a) Unauthorized action execution: policy gate denies actions violating rules regardless of how the LLM was prompted.
     b) State bypass: LLM cannot skip states or violate transition rules enforced by code.
     c) Direct prompt injection at execution boundary: injected instructions cannot override code-based policy checks.
     d) Missing confirmation: destructive/irreversible actions require explicit confirmation that cannot be spoofed by the LLM.
   - What CCP does NOT protect against (be explicit — this is what reviewers will probe):
     a) Adversarial reasoning within policy bounds: if an attacker manipulates the LLM into proposing a READ instead of a DELETE, the policy gate sees a READ and allows it. CCP enforces policy-as-written, not policy-as-intended.
     b) Action misclassification by the LLM: if the LLM's structured output incorrectly labels action_type, CCP gates based on the label. The gap is between the LLM's action proposal and ground truth.
     c) Sequences of individually-safe actions that are collectively harmful (e.g., read patient A's data, read patient B's data, compare — each READ is allowed but the sequence may violate privacy).
     d) Social engineering that doesn't result in gated actions (e.g., the LLM reveals sensitive information in its conversational response without proposing a formal action).
     e) Model-level attacks: adversarial training data, fine-tuning attacks, weight manipulation.
     f) Policy definitions that encode bias or unjust restrictions — CCP enforces them deterministically (see Ethics section).
   - Safety invariants enumerated and mapped to enforcement mechanisms (table format).
   - Honest scope boundary statement: "CCP is a necessary but not sufficient layer for safe AI agent deployment. It guarantees policy enforcement and auditability. It does not guarantee that the policies themselves are correct, complete, or just."
   - Reference real-world CVEs and incidents from Phase 3 eval to ground the threat model in actual attacks (CVE-2025-53773, CVE-2025-32711, CVE-2025-54135/54136).

9) Ethical Considerations
   - The "who decides safe" problem: a deterministic policy gate is only as good as the policies encoded in it. If the policies encode bias or unjust restrictions, CCP enforces injustice deterministically. This is simultaneously CCP's strength (auditable, changeable, explicit) and its risk (explicit bias is still bias).
   - Potential for misuse: CCP could be used to enforce censorship, discriminatory access controls, or surveillance workflows. The same policy gate that blocks unauthorized deletions could block legitimate whistleblower actions.
   - Mitigation through transparency: all policies and state machines are auditable YAML, not opaque models. Anyone can read what the system enforces and challenge it. This is a structural advantage over model-based safety that is opaque by nature.
   - Governance as ethical infrastructure: HITL workflow (Phase 4) ensures policy changes require human review. But this shifts the ethical question from "is the system safe?" to "are the reviewers making ethical decisions?" — which is a human governance problem, not a technical one.
   - CCP does not absolve deployers of ethical responsibility — it makes the responsibility explicit and auditable.
   - Reference ETHICS.md.

10) Related Work and Positioning
    - NeMo Guardrails (NVIDIA): Colang flows + input/output rails, but uses LLMs internally for classification → vulnerable to prompt injection at the classification layer. Garak (also NVIDIA) documents these vulnerabilities. Strong community and enterprise adoption but different architectural guarantees.
    - Guardrails AI: validation framework with input/output validators. Effective for format/content validation but does not perform action resolution, state management, or execution governance. Complementary, not competing.
    - Semantic Router (Aurelio): embedding-based routing, no policy or state management. Fast and lightweight but routing-only — no safety enforcement.
    - Safiron / Pre-Exec Bench: pre-execution safety checks, but still model-based (probabilistic).
    - ToolSafe: step-level tool invocation guardrails, RL-based — probabilistic and requires training data.
    - LangChain/LangGraph: orchestration frameworks where safety is integrator's responsibility. CCP could be integrated as a layer within LangChain pipelines.
    - Rasa: traditional intent classification with fallback, designed for pre-LLM era. Not positioned as a control plane.
    - OWASP Top 10 for LLM Applications (2025): prompt injection ranked #1 vulnerability. CCP directly addresses this at the execution boundary.
    - Recent prompt injection research (2025-2026): WASP benchmark shows 86% partial success rate against top models; TensorTrust demonstrates human adversarial creativity; real-world CVEs (Copilot, Cursor, Microsoft 365) show production impact. CCP addresses the execution-boundary subset of these attacks.
    - Key differentiation (precisely scoped): HNIR-CCP is the only system that combines deterministic policy enforcement, state machine governance, and control command resolution in a single pre-execution layer. It is structurally immune to prompt injection at the policy enforcement boundary. It is NOT immune to adversarial reasoning that produces policy-compliant actions.

11) Limitations
    - CCP effectiveness depends entirely on the quality of policy rules and state machine definitions. A misconfigured policy gate provides a false sense of security that may be worse than no gate at all.
    - Control command matching is brittle for edge cases at the boundary between control signals and conversational content (addressed by HITL workflow, but HITL effectiveness is unproven at scale).
    - Does not handle open-ended reasoning, generation, or understanding — that's the LLM's job. CCP cannot prevent harmful information disclosure that occurs within LLM conversational responses without triggering a formal action proposal.
    - Evaluation includes both hand-crafted and published benchmark scenarios, with real LLM integration. However, real-world deployment at production scale with actual end users remains future work. Lab results may not transfer to production environments with adversaries who can iterate.
    - State machine complexity scales with workflow complexity. YAML-based state definitions are tractable for <20 states but may require more sophisticated formalisms (TLA+, Alloy) for complex multi-agent workflows. No formal verification is performed in v2.
    - The gap between LLM action proposals and ground truth actions is a fundamental limitation. CCP gates what the LLM says it wants to do, not what it actually does if the execution layer is compromised.
    - Regulatory compliance claims (HIPAA, GDPR, SOC2) are architectural — CCP provides audit infrastructure and policy enforcement mechanisms. Actual compliance requires domain-specific policy definitions validated by compliance professionals, which is outside the scope of this paper.
    - Single-author project — no independent validation of threat model or policy definitions at time of publication.

12) Reproducibility
    - Point to REPRODUCIBILITY.md and eval/manifest.json.
    - All traces, scripts, and results are in the public repo.
    - One-command eval run.

13) Conclusion
    - As AI agents become operational systems, the missing architectural layer is not better intent understanding but deterministic execution governance.
    - HNIR-CCP provides this layer: control commands for system signals, policy gates for action enforcement, state machines for workflow governance.
    - A deterministic control plane cannot be prompt-injected, provides provable audit trails, and enables regulatory compliance in domains where LLMs alone cannot.

Step-by-step

1) Choose target venue and format
   - Research upcoming deadlines for workshops at NeurIPS 2026, ICML 2026, AAAI 2027.
   - Format paper to venue requirements (typically 4-8 pages for workshops).

2) Create paper/hnir_v2.tex skeleton
   - Use headings aligned to the structure above.
   - Add an "Artifact Map" table linking sections to repo paths.

3) Write the Introduction and Motivation sections first
   - These carry the thesis. Get them right before filling in details.
   - The "intent routing is the wrong primitive" argument is the intellectual contribution.

4) Populate architecture + implementation sections
   - Map to modules in the repo.
   - Include architecture diagram.

5) Insert evaluation results
   - Reference eval/results.md and results.json.
   - Generate figures from eval data.
   - The prompt injection resistance comparison is the headline result.

6) Write related work with explicit differentiation
   - Table: CCP vs NeMo vs Guardrails AI vs Semantic Router vs raw LLM across capabilities.
   - Keep it concise and factual.

7) Verify every claim
   - Every claim must map to: a metric, a reproducible script, or a clearly marked design argument.
   - Remove any claim that cannot be traced to an artifact.

8) Final review pass
   - Remove hype, keep scope bounded.
   - Ensure alignment with Phase 0 positioning.
   - Get external feedback if possible (potential source of independent expert letters for EB1A).

Acceptance Criteria
- Paper references only reproducible artifacts from the repo.
- Every quantitative claim is backed by metrics or scripts.
- Paper includes threat model, related work, ethical considerations, and reproducibility sections.
- Artifact map table links each section to specific repo files.
- Paper is formatted for target venue submission.
- The "intent routing is the wrong primitive" reframe is clearly articulated as the thesis.

Known Gaps and Mitigations
- GAP: Single-author paper may face credibility concerns. MITIGATION: Emphasize reproducibility — every claim backed by artifacts. Seek co-author or acknowledged reviewers from AI safety community before submission. Even an "Acknowledged Reviewers" section naming independent experts who provided feedback strengthens credibility.
- GAP: Workshop papers are 4-8 pages — may be too short to cover all 13 sections adequately. MITIGATION: Prioritize sections 1-6 and 8 (thesis, architecture, evaluation, threat model). Sections 7, 9, 11-12 can be condensed. Section 10 (related work) is critical for reviewer context. Prepare a longer arXiv/Zenodo version with full detail.
- GAP: Paper timeline ("1-2 weeks part-time") is likely optimistic for a first peer-reviewed submission. MITIGATION: Realistic timeline is 3-4 weeks part-time. Budget extra time for figure generation, related work verification, and external feedback rounds.
- GAP: Patent and paper have different audiences and standards. MITIGATION: Write the paper for academic reviewers (emphasize novelty, evaluation rigor, honest limitations). Write the patent for examiners (emphasize claims, embodiments, prior art distinction). They share evidence but differ in framing. Do not copy paper text into patent claims verbatim.

Handoff Notes
- Phase 6 will publish the paper on Zenodo and as a GitHub release.
- Submit to target venue independently of Zenodo publication.
- Zenodo preprint establishes priority; peer review at venue establishes credibility.
- The paper's evaluation section is the core evidence for the HNIR-CCP patent (Phase 6.5). Ensure all metrics, datasets, and baselines are documented with enough detail for patent prosecution.
