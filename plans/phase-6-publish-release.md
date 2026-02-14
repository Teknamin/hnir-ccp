# Phase 6 — Publish + Release Artifacts (same day)

Goal
- Create a clean public release with Zenodo DOI and all artifacts, establishing priority for the v2 contribution.

Primary Deliverables
- GitHub Release (v2.0)
- Zenodo v2 record linking to release + paper
- Submission to target peer-reviewed venue (from Phase 5)

Inputs
- Completed repo with CCP demo, eval, paper.
- Target venue submission deadline (from Phase 5).

Outputs
- GitHub release tag (v2.0)
- Zenodo DOI record with paper PDF + results
- Release artifact manifest (hashes + file list)
- Venue submission confirmation

Step-by-step

1) Connect GitHub repo to Zenodo
   - Use the GitHub-Zenodo integration.
   - Ensure metadata is correct (title, author, description, keywords).
   - Keywords should include: conversation control plane, deterministic execution governance, AI safety, policy enforcement, prompt injection resistance, LLM orchestration.

2) Prepare release artifacts
   - Paper PDF (generated from paper/hnir_v2.tex)
   - eval/results.md
   - eval/results.json
   - eval/manifest.json
   - eval/traces.jsonl (full trace dataset)
   - Artifact manifest with SHA-256 hashes

3) Create GitHub release
   - Tag: v2.0
   - Release notes:
     - The reframe: HNIR-CCP is a deterministic control plane, not an intent router.
     - Three capabilities: control command shortcuts, policy-gated execution, state machine governance.
     - Key results: prompt injection resistance (CCP vs baselines), control command latency, policy compliance rate.
     - Known limitations (from paper's Limits section).
   - Attach the artifact manifest to the release.
   - Keep release notes factual and tied to eval outputs.

4) Mint Zenodo DOI
   - Zenodo should auto-archive the release.
   - Attach paper PDF and supplementary results.
   - Link to v1 record (https://zenodo.org/records/18110920) as "is new version of."

5) Submit to peer-reviewed venue
   - Submit paper to the target venue identified in Phase 5.
   - Include Zenodo DOI as supplementary material link.
   - Note: Zenodo preprint establishes priority date; venue publication establishes peer review credibility.

6) Verify the record
   - Check DOI resolves and links to GitHub release.
   - Ensure metadata is accurate.
   - Verify artifacts match the manifest hashes.
   - Verify v1 → v2 version chain on Zenodo.

Acceptance Criteria
- GitHub release exists with v2.0 tag.
- Zenodo v2 record links to release and includes paper + results.
- Release artifacts are verifiable via the manifest.
- v1 → v2 version chain is visible on Zenodo.
- Paper is submitted to at least one peer-reviewed venue.

Known Gaps and Mitigations
- GAP: Publishing evaluation results publicly before filing CCP patent could create prior art issues. MITIGATION: Zenodo publication establishes your priority date. However, consult patent attorney on timing: in the U.S., you have a 12-month grace period from public disclosure to file a patent application. File CCP patent (Phase 6.5) within 12 months of the Zenodo v2 publication date. Ideally, file the patent before or simultaneously with publication.
- GAP: Zenodo auto-archive from GitHub may include incomplete or draft files. MITIGATION: Create a clean release branch, verify all artifacts, then tag. Don't auto-archive from main branch if it contains work-in-progress.

Handoff Notes
- Phase 6.5 (CCP patent filing) should be executed concurrently with or immediately after Phase 6.
- Phase 7 will reference the DOI and release links on websites.
- Keep release notes factual and aligned with measured claims.
- Track venue review timeline — reviewer feedback may inform v2.1 improvements.
- PATENT TIMING: Note the 12-month grace period from public disclosure. Coordinate patent filing with Zenodo publication.
