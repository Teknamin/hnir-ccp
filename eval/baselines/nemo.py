"""Baseline B: NeMo Guardrails with Colang config.

Uses nemoguardrails package with Colang flows defined in nemo_config/.
Rails block IRREVERSIBLE keyword patterns → DENY.
Rails allow READ intents → ALLOW.
Fallback: route to LLM, parse response.

Documented limitation: NeMo has no state machine or RBAC.
state_transition and role-based scenarios are outside its design scope.
Results are reported separately in results.md.

is_available(): nemoguardrails importable + OPENAI_API_KEY set.
"""

import os
import time
from pathlib import Path

from eval.runner import BaselineRunner
from eval.schema import ScenarioResult, TraceEntry

_NEMO_CONFIG_DIR = str(Path(__file__).parent / "nemo_config")


class NeMoRunner(BaselineRunner):
    """Baseline B: NeMo Guardrails with Colang flows."""

    name = "nemo"

    def is_available(self) -> bool:
        if not os.environ.get("OPENAI_API_KEY"):
            return False
        try:
            import nemoguardrails  # noqa: F401
            return True
        except ImportError:
            return False

    def run_scenario(self, entry: TraceEntry) -> ScenarioResult:
        try:
            from nemoguardrails import RailsConfig, LLMRails
        except ImportError:
            return self._error(entry, "nemoguardrails package not installed")

        if not os.environ.get("OPENAI_API_KEY"):
            return self._error(entry, "OPENAI_API_KEY not set")

        # Build user message including action context
        user_msg = entry.user_text
        if entry.proposed_action:
            pa = entry.proposed_action
            user_msg = (
                f"{entry.user_text}\n"
                f"[action type={pa.action_type} name={pa.name}]"
            )

        t0 = time.perf_counter()
        try:
            config = RailsConfig.from_path(_NEMO_CONFIG_DIR)
            rails = LLMRails(config)
            response = rails.generate(messages=[{"role": "user", "content": user_msg}])
            t1 = time.perf_counter()
            latency_us = (t1 - t0) * 1_000_000

            response_text = response.get("content", "").strip().upper() if isinstance(response, dict) else str(response).strip().upper()
            actual_decision = self._parse_decision(response_text)

        except Exception as exc:
            return self._error(entry, str(exc))

        passed = actual_decision == entry.expected_decision
        return ScenarioResult(
            scenario_id=entry.scenario_id,
            category=entry.category,
            system=self.name,
            passed=passed,
            expected_decision=entry.expected_decision,
            actual_decision=actual_decision,
            expected_layer=entry.expected_layer,
            actual_layer="nemo",
            expected_reason_code=entry.expected_reason_code,
            actual_reason_code="",
            latency_us=latency_us,
            audit_entry_count=0,
            audit_has_reason_code=False,
            audit_has_layer=False,
        )

    @staticmethod
    def _parse_decision(text: str) -> str:
        for decision in ("REQUIRE_CONFIRMATION", "DENY", "ALLOW"):
            if decision in text:
                return decision
        return "ALLOW"

    def _error(self, entry: TraceEntry, msg: str) -> ScenarioResult:
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
            error=msg,
        )
