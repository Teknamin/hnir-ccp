# HNIR v2 Publication Plan Index

Purpose: This folder breaks the multi-day plan into phase-specific, step-by-step files so an AI agent can implement one phase at a time.

Core Reframe (v1 -> v2): HNIR v1 was positioned as an intent router that competes with LLMs on understanding user intent. v2 abandons this framing. LLMs are better at understanding intent. HNIR-CCP is a deterministic control plane that governs what happens after intent is understood — enforcing policy, gating execution, managing state transitions, and handling control commands that don't need probabilistic reasoning. The LLM is the brain; the CCP is the spinal cord and autonomic nervous system.

Prior Art and IP Context:
- HNIR v1 preprint: https://zenodo.org/records/18110920 (Zenodo, Dec 2025)
- HNIR patent pending: U.S. Utility Non-Provisional Application No. 63/950,425 (covers deterministic intent routing architecture from v1). This is a full patent filing under examination, not a provisional placeholder.
- HNIR-CCP patent: NOT YET FILED. The CCP architecture (policy gate + state machine + audit) is a distinct invention from v1 intent routing. A separate patent application for HNIR-CCP must be filed with empirical proofs from the evaluation harness — not synthetic data alone. Phase 3 evaluation with real LLM integration and published adversarial benchmarks provides the evidentiary basis for CCP patent claims.

Legal Strategy Context:
- Primary track: EB2-NIW (National Interest Waiver) — AI safety for regulated domains is a strong "national interest" argument. Lower bar, more realistic near-term.
- Aspirational track: EB1-A (Extraordinary Ability) — requires sustained evidence across 3+ criteria. HNIR-CCP contributes to: original contributions (criterion 5), scholarly articles (criterion 6), judging (criterion 4), and published material (criterion 3). 12-month evidence-building horizon.
- The CCP patent with empirical proofs is dual-purpose: strengthens both patent quality and EB1-A criterion 5.
- All claims in publications, websites, and patent filings must be traceable to reproducible evaluation artifacts. No synthetic-only claims in patent applications.

How to use:
- Start at Phase 0 and proceed sequentially unless a dependency is explicitly marked optional.
- Each phase includes: goal, inputs, outputs, steps, acceptance criteria, and handoff notes.
- Treat each phase file as a self-contained task spec.
- GAP TRACKING: Each phase now includes a "Known Gaps and Mitigations" section documenting identified weaknesses and how they are addressed.

Phases
- Phase 0: Lock the control plane narrative
- Phase 1: Public repo skeleton with CCP architecture
- Phase 2: Working control plane demo (policy gate + state machine + control commands)
- Phase 2.5: Real LLM integration (replace mock with actual LLM backend — required before Phase 3)
- Phase 3: Evaluation harness (CCP vs actual NeMo Guardrails vs real LLM baseline)
- Phase 4: HITL workflow for policy and state machine refinement
- Phase 5: Write v2 paper targeting peer-reviewed venue
- Phase 6: Publish + release artifacts with Zenodo DOI
- Phase 6.5: File HNIR-CCP patent application with empirical evidence package
- Phase 7: Update lab + personal websites
- Phase 8: Ongoing cadence, peer review credentials, and evidence trail

Files
- plans/hnir_v2/phase-0-positioning.md
- plans/hnir_v2/phase-1-repo-skeleton.md
- plans/hnir_v2/phase-2-v0-demo.md
- plans/hnir_v2/phase-3-eval-harness.md
- plans/hnir_v2/phase-4-hitl-workflow.md
- plans/hnir_v2/phase-5-paper.md
- plans/hnir_v2/phase-6-publish-release.md
- plans/hnir_v2/phase-7-web-updates.md
- plans/hnir_v2/phase-8-cadence.md
