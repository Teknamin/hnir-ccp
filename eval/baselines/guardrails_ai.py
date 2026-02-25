"""Baseline C: Guardrails AI with custom Guard.

Scope:
- Supported categories: adversarial, policy_gate
- Out-of-scope: control_command, state_transition (returned as SKIP / is_skipped=True)

Documented limitation: Guardrails AI validates text content only, not action-type
policy, state machine transitions, or RBAC. control_command and state_transition
scenarios are outside its design scope.

Latency notes:
- latency_shim_us: local guardrail logic only (no LLM calls). Measured for
  supported categories only. None (N/A) for SKIP (out-of-scope) scenarios.
- latency_e2e_us: same as latency_shim_us for this baseline (no LLM calls).

Audit: No structured audit schema. audit_schema_enforced = False by design.
"""

import time
from typing import Optional

from eval.runner import BaselineRunner
from eval.schema import ScenarioResult, TraceEntry


class _ActionTypeValidator:
    """Simple validator that rejects IRREVERSIBLE action types."""

    IRREVERSIBLE_KEYWORDS = [
        "irreversible", "purge", "wipe", "destroy", "nuke", "permanent",
        "delete all", "drop table", "format", "erase",
    ]

    def validate(self, user_text: str, action_description: str) -> Optional[str]:
        """Return 'DENY' if content suggests irreversible action, else None."""
        combined = (user_text + " " + action_description).lower()
        for kw in self.IRREVERSIBLE_KEYWORDS:
            if kw in combined:
                return "DENY"
        return None


class GuardrailsAIRunner(BaselineRunner):
    """Baseline C: Guardrails AI with content validators."""

    name = "guardrails_ai"

    # Categories this baseline is designed to handle
    SUPPORTED_CATEGORIES = {"adversarial", "policy_gate"}

    def is_available(self) -> bool:
        try:
            import guardrails  # noqa: F401
            return True
        except ImportError:
            return False

    def run_scenario(self, entry: TraceEntry) -> ScenarioResult:
        # Out-of-scope categories: mark N/A (not a failure, not measured in latency)
        if entry.category not in self.SUPPORTED_CATEGORIES:
            return ScenarioResult(
                scenario_id=entry.scenario_id,
                category=entry.category,
                system=self.name,
                passed=False,
                expected_decision=entry.expected_decision,
                actual_decision="SKIP",
                expected_layer=entry.expected_layer,
                actual_layer="n/a",
                expected_reason_code=entry.expected_reason_code,
                actual_reason_code="",
                latency_shim_us=None,   # N/A — not evaluated for this category
                latency_e2e_us=None,    # N/A — not evaluated for this category
                is_skipped=True,
                error="out-of-scope category for Guardrails AI (content validator only)",
            )

        try:
            import guardrails  # noqa: F401
        except ImportError:
            return self._error(entry, "guardrails-ai package not installed", is_crash=True)

        action_desc = entry.proposed_action.description if entry.proposed_action else ""
        action_type = entry.proposed_action.action_type if entry.proposed_action else ""

        t0 = time.perf_counter()
        try:
            validator = _ActionTypeValidator()
            deny_reason = validator.validate(entry.user_text, action_desc)

            # Also check action_type directly
            if action_type == "IRREVERSIBLE":
                deny_reason = "IRREVERSIBLE action type rejected"

            t1 = time.perf_counter()
            local_us = (t1 - t0) * 1_000_000

            actual_decision = "DENY" if deny_reason else "ALLOW"

        except Exception as exc:
            return self._error(entry, str(exc), is_crash=True)

        is_no_decision = actual_decision not in {"ALLOW", "DENY", "REQUIRE_CONFIRMATION"}
        passed = actual_decision == entry.expected_decision

        return ScenarioResult(
            scenario_id=entry.scenario_id,
            category=entry.category,
            system=self.name,
            passed=passed,
            expected_decision=entry.expected_decision,
            actual_decision=actual_decision,
            expected_layer=entry.expected_layer,
            actual_layer="guardrails",
            expected_reason_code=entry.expected_reason_code,
            actual_reason_code="",
            latency_shim_us=local_us,   # local guardrail logic, no LLM
            latency_e2e_us=local_us,    # no LLM calls → shim == e2e
            is_no_decision=is_no_decision,
        )

    def _error(self, entry: TraceEntry, msg: str, is_crash: bool = False) -> ScenarioResult:
        return ScenarioResult(
            scenario_id=entry.scenario_id,
            category=entry.category,
            system=self.name,
            passed=False,
            expected_decision=entry.expected_decision,
            actual_decision="ERROR",
            expected_layer=entry.expected_layer,
            actual_layer="error",
            expected_reason_code=entry.expected_reason_code,
            actual_reason_code="",
            is_crash=is_crash,
            error=msg,
        )
