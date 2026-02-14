# Phase 1 — Public Repo Skeleton with CCP Architecture (half day)

Goal
- Create a clean, publishable public repository that reflects the control plane architecture.

Primary Deliverable
- Public GitHub repo (hnir-ccp) with CCP module layout, docs, CI, and license.

Inputs
- POSITIONING.md (Phase 0).
- Decision on repo name and license (Apache-2.0 recommended for enterprise credibility).

Outputs
- README.md
- LICENSE (Apache-2.0)
- CONTRIBUTING.md
- COMMUNITY.md
- ETHICS.md
- RISKS.md
- ROADMAP.md
- CODE_OF_CONDUCT.md
- SECURITY.md
- REPRODUCIBILITY.md
- DATA_POLICY.md
- GOVERNANCE.md
- CITATION.cff
- .github/CODEOWNERS
- .github/PULL_REQUEST_TEMPLATE.md (with safety checklist)
- GitHub Actions CI workflow(s)
- Module layout reflecting CCP architecture

Step-by-step
1) Create or rename the public repo
   - Final name: hnir-ccp.
   - Initialize with README and license.

2) Define the CCP module layout
   - This is the core architectural decision. The module structure must reflect the control plane, not an intent router:
   ```
   ccp/
     control/          # Control command handler
       commands.py     # Command definitions (help, cancel, undo, reset, status)
       shortcuts.py    # Fast-path resolution for control signals
     policy/           # Policy enforcement engine
       gate.py         # Action classification + policy evaluation (ALLOW/DENY/CONFIRM)
       rules.py        # Policy rule definitions (YAML-loaded)
       authorization.py # Role/permission checks
     state/            # Conversation state machine
       machine.py      # State definitions + transition rules
       transitions.py  # Transition validation + precondition checks
       session.py      # Session state storage and retrieval
     audit/            # Deterministic observability
       logger.py       # Structured decision logging with reason codes
       trace.py        # Request trace assembly
     integration/      # LLM integration layer
       interceptor.py  # Pre-execution interception of LLM-proposed actions
       fallback.py     # Safe-mode fallback handler
   ```
   - Note: there is no "matching" or "routing" module. The CCP does not classify intent. It intercepts control commands, gates actions, and governs state.

3) Write README.md
   - Structure:
     - Problem statement (why LLM agents need a deterministic control plane)
     - The reframe (not an intent router — a control plane)
     - Architecture diagram (control commands → CCP; LLM-proposed actions → policy gate → state machine → execution)
     - Three capabilities (control shortcuts, policy gate, state machine)
     - Key differentiator (deterministic = not prompt-injectable)
     - Demo (what the v0 runs and what it shows)
     - Roadmap
     - Research Artifacts section pointing to eval/ and paper/
   - Include the Phase 0 positioning paragraph verbatim.

4) Add project governance + reproducibility docs
   - CONTRIBUTING.md with dev setup, lint/test commands, and PR expectations.
   - CODE_OF_CONDUCT.md (standard template).
   - SECURITY.md with reporting instructions.
   - REPRODUCIBILITY.md with pinned versions and one-command eval run.
   - DATA_POLICY.md with data sources and exclusions.
   - GOVERNANCE.md with policy rule approval workflow, safety constraints, and governance model (BDFL: aravindravi-research).
   - CITATION.cff for scholarly reuse.
   - .github/CODEOWNERS to require review on policy/ and state/ changes.
   - .github/PULL_REQUEST_TEMPLATE.md with safety checklist including: "Does this change modify policy rules or state transitions? If yes, has it been reviewed for safety invariant compliance?"

5) Add license
   - Apache-2.0.

6) Add CI
   - Lint (ruff or flake8) and tests (pytest) on push and PR.
   - Required status check for changes to policy/ and state/ directories.

7) Smoke check
   - README renders cleanly.
   - CI passes on first run.
   - Module layout is importable.

Acceptance Criteria
- Repo has all listed docs and CI workflow.
- Module layout reflects CCP architecture (control/, policy/, state/, audit/, integration/).
- README clearly explains the reframe: this is a control plane, not an intent router.
- No "matching" or "routing" modules exist — this is intentional.
- Governance enforced via CODEOWNERS on policy/ and state/ directories.
- CI green on default branch.

Handoff Notes
- Phase 2 will implement the modules.
- The module layout is the architectural commitment — changing it later means the paper's architecture section changes.
