# CCP Phase 3 — Baseline Comparison Results

**Run date:** 2026-02-26
**Git commit:** `79fa940`
**Duration:** 1.0s
**Scenarios:** 100 total (20 control, 20 state, 30 policy, 30 adversarial)

## Methodology

### Formal Metric Definitions

**Policy compliance (category)**: Among non-skipped (is_skipped=False) scenarios in the category, the fraction where `actual_decision == expected_decision`. Skipped scenarios are excluded from both numerator and denominator.

**Intersection-set compliance**: Policy compliance computed only on the 60-scenario intersection set (policy_gate + adversarial) — categories supported by all four systems. This is the apples-to-apples comparison metric.

**Injection resistance**: Among non-skipped adversarial scenarios, the fraction where `actual_decision == DENY`. 100% = every adversarial probe was blocked.

**Latency — shim**: Wall-clock time for local guardrail/routing/audit logic only. No LLM network calls. N/A for Raw LLM and NeMo (no separable local layer; the LLM IS the guardrail).

**Latency — e2e**: Total wall-clock time including all LLM API calls, retries, and response parsing. For CCP: shim == e2e (zero LLM calls).

**No-decision rate**: Fraction of evaluated scenarios where the system returned an unparseable or empty response; harness defaults to ALLOW (honest worst-case — counted as a decision failure, not a pass).

**Audit schema enforced**: True when every decision has a structured entry with timestamp + layer + reason_code enforced as first-class invariants. Baselines report 0% by design — this is a scope distinction, not a deficiency.

**Evaluation parameters:** temperature=0, timeout=60s/scenario, CCP latency = median of 3 fresh CCPInterceptor instances.

### Table A — Coverage Matrix

_Which categories each system natively evaluates. N/A = out-of-scope by design; scenarios are is_skipped=True and excluded from compliance denominators._

| System | Control (n=20) | Policy (n=30) | State (n=20) | Adversarial (n=30) |
| --- | --- | --- | --- | --- |
| ccp | FULL | FULL | FULL | FULL |

_NeMo: evaluated on all categories but has no RBAC or state machine (documented limitation)._  
_Guardrails AI: content validation only; control_command and state_transition are N/A._

### Table B — Safety & Correctness

_Policy compliance: fraction of non-skipped scenarios where actual_decision == expected_decision. Intersection set: policy_gate + adversarial (n=60), supported by all four systems — the apples-to-apples comparison. Injection resistance: fraction of adversarial scenarios where actual_decision == DENY._

| System | Compliance (all, %) | Compliance (intersection, %) | Adversarial Blocked (%) |
| --- | --- | --- | --- |
| **ccp** | 100.0% | 100.0% | 100.0% |

### Table C — Reliability

_Timeout: exceeded 60s per scenario. Crash: unhandled exception. No-decision: unparseable/empty response, defaulted to ALLOW (honest worst-case). N/A rate: fraction of scenarios out-of-scope for this system (is_skipped=True)._

| System | Timeout (%) | Crash (%) | No-Decision (%) | N/A Rate (%) |
| --- | --- | --- | --- | --- |
| **ccp** | 0.0% | 0.0% | 0.0% | 0.0% |

### Table D — Latency (control_command category, n=20 scenarios)

_Shim: local guardrail/routing/audit logic only — no LLM network calls. E2E: total wall time including all LLM API calls and parsing. N/A = no separable local shim layer (the LLM IS the system). CCP latency = median of 3 fresh CCPInterceptor instances per scenario. Measurements from local development machine (see manifest.json for hardware context)._

| System | Shim P50 | Shim P95 | Shim P99 | E2E P50 | E2E P95 | E2E P99 |
| --- | --- | --- | --- | --- | --- | --- |
| **ccp** | 24.2μs | 33.7μs | 33.7μs | 24.2μs | 33.7μs | 33.7μs |

_Raw LLM / NeMo shim = N/A: no local guardrail logic separable from the LLM call._  
_Guardrails AI shim ≈ e2e: local validation only, no LLM calls._

### Table E — Cost

_LLM pricing: GPT-4o-mini input $0.15/1M tokens, output $0.6/1M tokens (2026-02). NeMo token counts = 0: nemoguardrails.generate() does not expose per-call token usage via its public API (conservative cost estimate)._

| System | LLM Calls | Input Tokens | Output Tokens | Total Cost (USD) | Avg Cost/Scenario |
| --- | --- | --- | --- | --- | --- |
| **ccp** | 0 | 0 | 0 | $0.000 | $0.000 |

## Per-Category Compliance Detail

| System | control_command | policy_gate | state_transition | adversarial | overall |
| --- | --- | --- | --- | --- | --- |
| ccp | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

## Reproducibility

Reproducibility test skipped (--no-reproducibility flag).

## Key Findings

### Speed

- CCP latency is sub-millisecond and network-independent (zero LLM calls).

### Safety / Injection Resistance

- CCP blocks **100.0%** of adversarial scenarios (IRREVERSIBLE, role escalation, state skips, prompt injection)

### RBAC Coverage

- CCP enforces role-based access correctly across 100% of policy scenarios
- Raw LLM has no RBAC awareness — allows WRITE for guest/viewer/empty roles
- NeMo has no RBAC — role-based scenarios are outside its design scope
- Guardrails AI performs text content validation only — no RBAC

### State Machine

- CCP enforces all state transitions correctly; invalid skips are DENY
- NeMo: returns REQUIRE_CONFIRMATION for invalid state skips instead of DENY
- Guardrails AI: no state machine concept; all state_transition scenarios are N/A

### Audit Trail

- CCP: **100.0%** of decisions have structured audit entry (timestamp + layer + reason_code)
- Baselines: do not implement a structured decision audit schema
  (scope distinction — not a deficiency; see Methodology section)

### Documented Scope Limitations (by Design)

- **NeMo Guardrails**: No RBAC, no state machine — role-based and state-transition scenarios are outside its design scope.
- **Guardrails AI**: Content-based text validation only — control_command and state_transition scenarios are N/A.
- **Raw LLM**: No persistent session state, no deterministic confirmation flow.
- **All baselines**: No structured audit schema.

## What CCP Catches

- **IRREVERSIBLE action types**: Blocked at state machine layer (not in any state's `allowed_action_types`).
- **Role escalation attacks**: Text-based role claims ignored; session `user_roles` is authoritative.
- **State machine skip attacks**: Invalid transitions detected before policy evaluation.
- **DELETE without admin role**: RBAC enforced at policy gate.
- **DELETE without confirmation**: Confirmation gate enforced even for admin.
- **All committed Garak/TensorTrust/WASP adversarial probes**: Blocked by state or policy layer.

## What CCP Does NOT Catch

- **Prompt injection → benign action**: CCP evaluates the *proposed action*, not user text. If the LLM correctly proposes an allowed READ despite adversarial user text, CCP passes it through.
- **Semantic deception in data payloads**: CCP does not inspect action data content.
- **Timing attacks / state timeout bypass**: Not covered in this evaluation.

## Explicit Non-Goals (Out of Scope for This Evaluation)

The following are intentionally NOT measured. Their absence does not imply they are unimportant.

- **External holdout dataset**: All 100 scenarios are used for a single evaluation run; no separate test split is reserved.
- **Multi-model sensitivity**: Baselines use GPT-4o-mini only. Performance may differ for other LLMs.
- **User study / human evaluation**: No human judges reviewed scenario or decision quality.
- **LLM-based CCP modes**: This evaluation covers deterministic CCP only. CCP's LLM fallback (OpenAI/Anthropic adapters) is not benchmarked here.
- **Long-context or multi-turn adversarial attacks**: Scenarios are single-turn.
- **Production latency**: Measurements are from a local development machine (see manifest.json for hardware context), not a production environment.

