# Phase 8 — Ongoing Cadence, Peer Review Credentials, and Evidence Trail (continuous)

Goal
- Maintain a visible, credible research trajectory while building the supplementary evidence that strengthens both the research contribution and the dual-track legal strategy (EB2-NIW near-term + EB1-A long-term).

Primary Deliverable
- A consistent public trail of milestones, publications, peer review activity, and community engagement.
- HNIR-CCP patent application with empirical evidence package (separate from HNIR v1 patent).

Inputs
- Active repo, issue tracker, and evaluation harness.
- Venue submission status and reviewer feedback.

Outputs
- Regular GitHub milestones closed
- Short lab notes documenting evolution
- Peer review credentials (reviewer for conferences/journals)
- Independent expert engagement
- Optional Zenodo v2.x updates
- Up-to-date ROADMAP.md

Step-by-step

1) Maintain and Evolve the CCP
   - Define and maintain ROADMAP.md with the vision beyond v2:
     - Real LLM integration (replace mock with actual LLM agent).
     - Multi-agent CCP (policy enforcement across collaborating agents).
     - Domain-specific policy templates (healthcare, defense, finance).
     - Formal verification of state machines.
     - CFG-based control command matching (from v1 roadmap, now scoped correctly as control commands only).
   - Use community feedback from GitHub Discussions to inform the roadmap.

2) Set a 2-4 Week Development Cadence
   - Close one GitHub milestone per cycle.
   - Publish one short lab note with changes + results.
   - Milestone types:
     - Policy gate improvements (new action types, authorization models).
     - State machine enhancements (new workflow patterns, formal verification).
     - Eval expansion (new adversarial scenarios, real-world trace integration).
     - Integration work (actual LLM backends, framework integrations).
   - Re-run eval after meaningful changes. Record result deltas.
   - Do not publish claims without a fresh eval run.

3) Build Peer Review Credentials (EB1A Criterion 4)
   - Sign up as a reviewer for relevant venues:
     - Conferences: NeurIPS, ICML, ICLR (via OpenReview), AAAI, ACL.
     - Journals: IEEE Access, ACM Computing Surveys, IEEE Transactions on AI.
     - Workshops: AI safety workshops at top venues.
   - Target: 20+ reviews over 12 months.
   - Document every review with confirmation emails or reviewer portal screenshots.
   - Seek area chair or program committee roles as credibility grows.

4) Cultivate Independent Expert Engagement (EB1A Criterion 5 evidence)
   - Present HNIR-CCP at:
     - Meetups and local AI safety groups.
     - Conference poster sessions or lightning talks.
     - Online seminars or podcast appearances.
   - Goal: build relationships with independent researchers who can later provide expert letters attesting to the contribution's significance.
   - Target: senior researchers at institutions working on AI safety, LLM orchestration, or dialogue systems who have no prior collaboration with you.

5) Seek Media and Community Visibility (EB1A Criterion 3 evidence)
   - Write a technical blog post explaining the "control plane, not intent router" reframe.
   - Target publications: IEEE Spectrum, The Gradient, Towards Data Science, or AI safety-focused outlets.
   - If venue paper is accepted, write a non-technical summary for broader distribution.
   - Document any coverage of your work in professional/trade publications.

6) Track Citation and Adoption Metrics
   - Monitor Google Scholar profile (create one if not existing).
   - Track: citations of v1 and v2, h-index, GitHub stars/forks/dependents.
   - Document independent usage: if anyone references, cites, or builds on HNIR-CCP, record it.
   - These metrics directly support EB1A criterion 5 (original contributions of major significance).

7) Submit to Additional Venues
   - If first venue submission is rejected, incorporate feedback and resubmit.
   - Consider submitting to multiple non-overlapping venues (a workshop paper and a journal article can coexist).
   - Each accepted publication strengthens EB1A criterion 6.

8) Publish Minor Zenodo Updates (optional)
   - Only when substantial additions justify v2.1, v2.2, etc.
   - Each version maintains the DOI chain and demonstrates sustained contribution.

9) HNIR-CCP Patent Filing (Separate from HNIR v1 Patent)
   - HNIR v1 utility non-provisional (No. 63/950,425) is already filed and under examination. Track examination status; respond to office actions promptly.
   - HNIR-CCP is a distinct invention: deterministic policy gate + state machine governance + audit trail — architecturally different from v1 intent routing. The CCP patent must stand on its own merits with its own evidence.
   - CRITICAL: Do NOT file CCP patent with synthetic-only evidence. The patent must include:
     a) Empirical results from Phase 3 evaluation with real LLM integration (not mock)
     b) Results against published adversarial benchmarks (TensorTrust, WASP, Garak probes, etc.)
     c) Results against real-world CVE-derived attack scenarios (CVE-2025-53773, CVE-2025-32711, etc.)
     d) Comparison against actual NeMo Guardrails and Guardrails AI libraries (not simplified mocks)
     e) Reproducible evaluation artifacts with manifest hashes
   - Candidate patent claims (to be refined with patent attorney):
     Claim 1: A method for deterministic pre-execution policy enforcement of LLM-proposed actions, comprising: receiving a structured action proposal from a language model, classifying the action by type (READ/WRITE/DELETE/IRREVERSIBLE), evaluating the classified action against a set of YAML-defined policy rules, and producing a deterministic decision (ALLOW/DENY/REQUIRE_CONFIRMATION) with a structured reason code — wherein the policy evaluation is performed by code execution, not by model inference.
     Claim 2: A system for deterministic state machine governance of conversational AI workflows, comprising: a set of defined conversation states with explicit transition rules, preconditions, timeout rules, and action type restrictions — wherein state transitions are validated by code execution and invalid transitions are blocked with deterministic reason codes.
     Claim 3: A method for safely evolving deterministic policy configurations in conversational AI systems, comprising: detecting policy gaps from structured audit logs, generating policy/state proposals, validating proposals against a safety invariant checker that runs all existing evaluation traces against the candidate configuration, and requiring human approval before any change is applied.
     Claim 4: A structured audit system for conversational AI execution governance, producing deterministic, reproducible decision logs with reason codes, policy references, state context, and latency measurements for every gated action.
   - Timeline: file after Phase 3 evaluation is complete with real LLM data and published benchmark results. Estimated: 2-4 months after Phase 0 start.
   - Budget: self-filing a utility non-provisional costs ~$800-1,600 (micro entity). Patent attorney review adds $3,000-8,000. Consider self-filing with attorney review of claims only to manage cost.
   - A granted CCP patent (distinct from v1) demonstrates two separate inventions from the same research program — strong evidence of sustained original contribution for both EB1-A and EB2-NIW.

10) Dual-Track Legal Strategy: EB2-NIW + EB1-A
    - EB2-NIW (near-term, lower bar):
      - "National Interest" argument: deterministic safety infrastructure for AI agents in healthcare, defense, and regulated domains serves U.S. national interest by reducing systemic AI risk.
      - Evidence: HNIR v1 patent (filed), HNIR-CCP patent (forthcoming), peer-reviewed publication, problem statement addressing HIPAA/defense/mental-health safety gaps.
      - Prong 1 (substantial merit and national importance): AI safety for regulated systems. Reference OWASP Top 10 for LLM (2025) ranking prompt injection as #1 vulnerability.
      - Prong 2 (well-positioned to advance): patent portfolio, published research, working prototype with evaluation results.
      - Prong 3 (on balance beneficial to waive job offer requirement): independent researcher advancing open-source safety infrastructure that benefits the field broadly.
      - Timeline: can file once v2 paper is submitted and CCP patent is filed. Estimated 4-6 months from Phase 0 start.
    - EB1-A (long-term, higher bar):
      - Requires evidence across 3+ of the 10 criteria (see checklist below).
      - HNIR-CCP alone is necessary but not sufficient — needs peer review credentials, expert letters, media coverage, and adoption metrics built over 12+ months.
      - Do NOT file EB1-A prematurely with thin evidence. Build the portfolio methodically.
      - Timeline: 12-18 months from Phase 0 start to filing readiness.
    - Sequencing: file EB2-NIW first (lower risk, establishes baseline), continue building EB1-A portfolio, file EB1-A when evidence is strong across 3+ criteria.
    - Engage immigration attorney early — at minimum for a case assessment before either filing. Budget $500-1,000 for initial consultation.

Evidence Checklist (Dual-Track: EB2-NIW + EB1-A)

EB2-NIW Evidence (file first, ~4-6 months):
- [ ] HNIR v1 utility non-provisional patent (No. 63/950,425) — filed, track examination
- [ ] HNIR-CCP patent filed with empirical proofs (not synthetic-only)
- [ ] v2 paper submitted to peer-reviewed venue
- [ ] Problem statement and positioning docs establishing national importance (AI safety for healthcare, defense, regulated domains)
- [ ] Working prototype with reproducible evaluation results
- [ ] Reference OWASP 2025 LLM Top 10 and real-world CVEs to ground the "national interest" argument
- [ ] Immigration attorney consultation completed

EB1-A Evidence (file when strong across 3+ criteria, ~12-18 months):

Criterion 4 — Judging:
- [ ] Reviewer for 2+ conferences or journals
- [ ] 20+ documented peer reviews (with confirmation emails/screenshots)
- [ ] Area chair or PC role at 1+ venue

Criterion 5 — Original Contributions:
- [ ] HNIR v1 patent — under examination / granted
- [ ] HNIR-CCP patent — filed with empirical proofs / under examination / granted
- [ ] Two distinct patents from same research program = sustained original contribution
- [ ] Independent expert letters (6-10, at least half from researchers with no prior collaboration)
- [ ] GitHub adoption metrics (stars >100, forks >20, external dependents)
- [ ] Citations from independent researchers (Google Scholar)
- [ ] Documentation of industry interest or adoption (emails, integration requests, enterprise inquiries)

Criterion 6 — Scholarly Articles:
- [ ] Zenodo v1 preprint (done — Dec 2025)
- [ ] Zenodo v2 preprint with empirical results
- [ ] 1+ peer-reviewed workshop or conference paper accepted
- [ ] Optional: journal article (IEEE Access, ACM Computing Surveys)

Criterion 3 — Published Material About You:
- [ ] Technical blog post in a recognized publication (IEEE Spectrum, The Gradient, Towards Data Science)
- [ ] Media coverage or interviews about HNIR-CCP
- [ ] Conference presentation documentation (poster, lightning talk, invited talk)

Criterion 9 — High Salary (if applicable):
- [ ] Document total compensation exceeding 90th percentile for BLS job code
- [ ] Include equity if applicable

Evidence Quality Standards:
- Every checklist item must be backed by verifiable documentation (not self-reported claims).
- Patent evidence: include application number, filing date, claims summary, examination status.
- Publication evidence: include DOI, venue name, acceptance notification, reviewer comments if available.
- Expert letters: must come from people who can speak to the specific contribution, not generic character references. At least 3 letters should reference the CCP architecture specifically.
- Adoption metrics: document with screenshots and timestamps, not just current numbers (show growth trajectory).

Acceptance Criteria
- At least one public artifact every 2-4 weeks.
- Evidence trail stays consistent and auditable.
- Each milestone reports at least one measured delta or baseline comparison.
- Peer review credentials actively growing.
- Patent timeline tracked and on schedule.

Known Gaps and Mitigations
- GAP: Single-author bottleneck — Phase 8 acknowledges this but recruitment plan is vague. MITIGATION: Set a concrete target: recruit 1 contributor by end of Phase 4 (offer co-authorship on v2 paper as incentive). Post in AI safety communities (Alignment Forum, EA Forum, AI safety Slack groups). Even 1 external contributor who reviews policies or adds eval traces significantly strengthens the project's credibility.
- GAP: 20+ peer reviews in 12 months is ambitious for someone not yet established in the review community. MITIGATION: Start with workshop reviews (lower bar for entry), then build toward main conference reviews. OpenReview makes it relatively easy to volunteer for ICLR/NeurIPS workshops. Target 8-10 reviews in first 6 months, scaling to 20+ by month 12.
- GAP: Expert letters require relationships that take months to build. MITIGATION: Start attending AI safety meetups and presenting HNIR-CCP immediately (Phase 0 is enough material for a 5-minute lightning talk). Don't wait until the paper is published to start building relationships.
- GAP: EB2-NIW "national interest" argument for AI safety is relatively novel — not as established as arguments for STEM researchers in medicine or engineering. MITIGATION: Reference executive orders on AI safety, NIST AI Risk Management Framework, OWASP LLM Top 10, and the growing regulatory landscape (EU AI Act) to ground the national interest claim.
- GAP: Patent costs may be prohibitive (attorney review $3K-8K). MITIGATION: Self-file with attorney review of claims only (~$1K-2K total). Some patent clinics at law schools offer reduced-cost assistance for independent inventors. Google Patent offers free prior art search to strengthen claims before filing.

Handoff Notes
- This phase runs indefinitely. The cadence maintains momentum and builds the sustained evidence trail.
- Every artifact produced should serve dual purpose: advancing the research AND strengthening the legal strategy.
- Timeline targets:
  - Month 0-2: Phase 0-2.5 (positioning, skeleton, demo, real LLM integration)
  - Month 2-4: Phase 3-4 (evaluation with real data + published benchmarks, HITL workflow)
  - Month 4-6: Phase 5-6.5 (paper submission, Zenodo release, CCP patent filing with proofs)
  - Month 4-6: EB2-NIW filing (concurrent with Phase 5-6)
  - Month 6-8: Phase 7 (website updates, blog posts, community engagement)
  - Month 8-18: Phase 8 ongoing (peer reviews, expert letters, adoption metrics, venue resubmissions)
  - Month 12-18: EB1-A filing readiness assessment — file only when evidence is strong across 3+ criteria
- CRITICAL: Do not rush EB1-A filing. A weak filing that gets denied is worse than waiting 6 more months to build stronger evidence. EB2-NIW is the safety net.
