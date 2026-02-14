# Phase 7 — Update Lab + Personal Websites (1 day)

Goal
- Update public-facing pages with evidence-backed summaries and links reflecting the control plane reframe.

Primary Deliverables
- Teknamin Labs site (https://www.teknamin.com/): Research entry
- raviaravind.com (https://www.raviaravind.com/): Portfolio item

Inputs
- Zenodo v1 + v2 links
- GitHub repo link: https://github.com/Teknamin/hnir-ccp
- Key metrics from eval/results
- Venue submission status

Outputs
- Research entry on teknamin.com
- Portfolio entry on raviaravind.com

Step-by-step

1) Draft lab site research entry for teknamin.com
   - Title: "HNIR-CCP: A Deterministic Control Plane for LLM-Powered Systems"
   - Key narrative: the evolution from intent routing (v1) to execution governance (v2).
   - 3-5 bullet summary:
     - What CCP does (policy gate, state machine, control commands).
     - Why it matters (prompt injection resistance, regulatory auditability, deterministic guarantees).
     - Key headline metric from eval (e.g., "100% prompt injection resistance at the execution boundary vs X% for LLM-based guardrails").
   - Links: Zenodo v1, Zenodo v2, GitHub Repo, specific release notes.
   - Research artifacts section: link to eval/, paper/, and REPRODUCIBILITY.md.
   - Community section: link to GitHub Discussions.
   - If venue submission is pending, note: "Under review at [venue]."

2) Draft personal site portfolio item for raviaravind.com
   - One paragraph explaining the contribution:
     - "As AI agents move into regulated domains, the missing architectural layer is not better intent understanding but deterministic execution governance. HNIR-CCP provides this layer..."
   - Evidence bullets:
     - Patent pending (U.S. Utility Non-Provisional Application No. 63/950,425).
     - Published research: Zenodo v1 DOI, v2 DOI.
     - Key metrics from eval.
     - Peer review status (if submitted/accepted).
   - Scope statement: one sentence on what CCP does not do.
   - Link to REPRODUCIBILITY.md.

3) Add evidence snippets
   - Use exact numbers from eval/results.
   - Examples: "Sub-millisecond control command resolution vs Xms LLM inference", "100% policy compliance on adversarial traces", "Identical decisions across 100 runs (zero variance)."

4) Publish updates
   - Ensure links resolve correctly.
   - Ensure text is consistent with Phase 0 positioning.
   - Verify no claims exceed what eval/results support.

Acceptance Criteria
- Both sites include links, evidence snippets, and the control plane framing.
- Metrics match eval/results exactly (no new or inflated claims).
- Limitations/non-goals are stated briefly.
- Patent and publication references are accurate.

Handoff Notes
- If metrics change with v2.1 or venue revisions, update the evidence bullets.
- When venue acceptance/rejection is known, update accordingly.
