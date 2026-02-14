# Phase 4 — HITL Workflow for Policy and State Refinement (3-7 days)

Goal
- Demonstrate a safe, minimal human-in-the-loop workflow for evolving policy rules and state machine definitions without compromising safety invariants.

Primary Deliverable
- review/ workflow that turns operational data into policy/state PRs with mandatory human approval.

Inputs
- Audit logs from Phase 2/3 (policy decisions, state transitions, denied actions, fallback events).

Outputs
- Policy gap analysis (actions the CCP couldn't confidently gate)
- State machine gap analysis (transitions that were ambiguous or missing)
- Rule proposal generator (CLI)
- Safety validation for proposed changes (conflict detection, invariant checking)
- Audit log of all proposals and decisions

Step-by-step

1) Define gap detection from audit logs
   - Identify actions where CCP fell back to default behavior (no specific policy matched).
   - Identify state transitions that were denied but may represent legitimate new workflows.
   - Identify patterns in adversarial traces that reveal policy blind spots.
   - Output: review/gaps.md with categorized findings.

2) Implement policy proposal generator
   - For each identified gap, generate:
     - Proposed policy rule (action type, conditions, decision, reason code).
     - Impact analysis: which existing scenarios would be affected.
     - Conflict detection: does the new rule contradict existing rules?
   - Output: YAML policy rule template ready for human review.

3) Implement state machine proposal generator
   - For identified state gaps, generate:
     - Proposed new state or transition.
     - Precondition and validation rules.
     - Impact analysis: which existing transitions are affected.
   - Verify: new transitions don't create unsafe paths (e.g., new shortcut from INTAKE to EXECUTION).
   - Output: YAML state definition template ready for human review.

4) Implement safety invariant checker
   - Before any proposed change can be submitted:
     - Run all existing eval traces against the modified policy/state.
     - Verify no previously-blocked adversarial scenario now passes.
     - Verify no previously-allowed safe scenario is now blocked.
     - Check for state machine reachability issues (unreachable states, deadlocks).
   - Output: safety report with pass/fail and specific violations.

5) Implement one-click proposal workflow
   - CLI command: `hnir-ccp propose-rule` / `hnir-ccp propose-transition`
   - Generates:
     - Policy/state YAML change.
     - Safety invariant check report.
     - Regression test additions.
     - PR or patch file (proposal only, never auto-merge).
   - Defaults to a patch file unless `--open-pr` is explicitly set.

6) Enforce human review gates with defined governance
   - No policy or state machine changes merge without:
     - Safety invariant check passing.
     - Regression eval passing (all existing traces produce same-or-better results).
     - Explicit human approval via PR review.
     - Ethical review step (referencing ETHICS.md): could this policy change enable harm?
   - Record every proposal and decision in an append-only audit log at review/audit.jsonl.
   - CODEOWNERS enforces review on policy/ and state/ directories.
   - Governance specifics (who approves, when, and how):
     - Reviewer roles: POLICY_REVIEWER (can approve policy/ changes), STATE_REVIEWER (can approve state/ changes), SAFETY_LEAD (required for any change that touches adversarial trace results). Initially all roles held by project maintainer (BDFL). As contributors join, roles are delegated via GOVERNANCE.md.
     - Approval SLA: all proposals must be reviewed within 7 calendar days. Unreviewed proposals are auto-escalated (flagged in review/audit.jsonl with reason REVIEW_SLA_EXCEEDED). No auto-merge — SLA breach triggers escalation, not approval.
     - Conflict resolution: if a proposed change passes safety invariant check but reviewer disagrees, the reviewer's judgment overrides. Rationale must be documented in the audit log. The safety invariant checker catches mechanical regressions; human reviewers catch semantic issues the checker cannot.
     - Reviewer qualifications: reviewers must have read ETHICS.md, RISKS.md, and the threat model (Phase 5, Section 8). For domain-specific policies (healthcare, defense), domain expertise is required and must be documented in the PR review.
     - Escalation path: if no qualified reviewer is available, the change is blocked. "No reviewer = no merge" is a safety invariant, not a process bottleneck.

7) Safety invariant checker algorithm (detailed specification)
   - The checker is a deterministic function: (proposed_change, existing_policy, existing_state_machine, eval_traces) → PASS / FAIL + violations[]
   - Step 1: Parse the proposed YAML change and validate schema.
   - Step 2: Merge proposed change with existing policy/state definitions into a candidate configuration.
   - Step 3: Run ALL eval traces (from Phase 3) against the candidate configuration:
     a) For every trace tagged "adversarial": verify the candidate produces DENY or REQUIRE_CONFIRMATION. If any adversarial trace now produces ALLOW, FAIL with violation "ADVERSARIAL_REGRESSION: {trace_id}".
     b) For every trace tagged "safe": verify the candidate produces ALLOW. If any safe trace now produces DENY, FAIL with violation "FALSE_POSITIVE_REGRESSION: {trace_id}".
     c) For every trace tagged "state_transition" with expected=BLOCKED: verify still blocked. If now allowed, FAIL with "STATE_SAFETY_REGRESSION: {trace_id}".
   - Step 4: State machine reachability analysis on the candidate:
     a) Check for unreachable states (states with no inbound transitions except initial state).
     b) Check for deadlock states (states with no outbound transitions except terminal state).
     c) Check for new shortcuts that bypass confirmation states (e.g., new transition from INTAKE directly to EXECUTION).
   - Step 5: Policy conflict detection:
     a) Check for rules that produce contradictory decisions for the same action_type + state + role combination.
     b) Check for rules that shadow (completely override) existing rules without explicit documentation.
   - Output: structured JSON report with PASS/FAIL, list of violations, list of warnings (non-blocking), and diff of decision changes across all traces.
   - Limitation: the checker catches mechanical regressions against known traces. It cannot catch semantic issues, novel attack vectors not in the trace set, or policy definitions that are technically correct but contextually harmful. This is why human review is mandatory even when the checker passes.

Acceptance Criteria
- Gaps are identified reproducibly from audit logs.
- Proposals include safety invariant check and regression eval results.
- No policy or state change can bypass human review.
- Previously-blocked adversarial scenarios remain blocked after any accepted change.
- Audit log records the full proposal lifecycle (proposed → reviewed → accepted/rejected).
- Safety invariant checker is itself tested: add test cases for each failure mode (adversarial regression, false positive regression, state safety regression, unreachable state, deadlock, policy conflict).

Known Gaps and Mitigations
- GAP: Safety invariant checker only tests against known traces — novel attacks not in the trace set are invisible. MITIGATION: Phase 3's adversarial eval should be expanded over time (Phase 8 cadence). Every real-world incident or new published benchmark should generate new traces. The checker gets stronger as the trace set grows.
- GAP: State machine scalability — reachability analysis is tractable for small state machines (<20 states) but may become expensive for large ones. MITIGATION: Document complexity bounds. For v2, scope to <20 states. If domain-specific workflows require more, investigate formal verification tools (TLA+, Alloy) in Phase 8 roadmap.
- GAP: Single-maintainer review bottleneck. MITIGATION: The governance model explicitly addresses this — "no reviewer = no merge" is a safety feature, not a bug. The project accepts slower velocity as the cost of safety. Phase 8 plans to recruit contributors to distribute review load.
- GAP: Ethical review step is subjective. MITIGATION: Provide a checklist in ETHICS.md with concrete questions: "Does this change allow actions in states where they were previously blocked? Could the newly-allowed action cause harm in any documented domain scenario? Does this change reduce the confirmation requirements for destructive actions?" The checklist doesn't eliminate subjectivity but bounds it.

Handoff Notes
- This phase is critical for governance credibility and for the paper's HITL section.
- The safety invariant checker is a key contribution — it demonstrates that the CCP is not just deterministic but also evolvable without compromising safety.
- The checker algorithm is also patent-relevant: "method for safely evolving deterministic policy configurations in conversational AI systems while maintaining safety invariants" is a distinct claim from the policy gate itself.
- Keep it minimal and deterministic; avoid UI sprawl.
