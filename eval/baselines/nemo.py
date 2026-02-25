"""Baseline B: NeMo Guardrails with Colang flows.

Latency notes:
- latency_shim_us: N/A — NeMo always routes through an LLM; there is no
  local-only guardrail layer separable from the LLM call.
- latency_e2e_us: full wall-clock time including LLM API round-trip and
  NeMo's Colang flow evaluation.

Token tracking:
- NeMo does not reliably expose per-call token counts via its public API.
  Token counts are therefore reported as 0 with a note in the manifest.
  Cost estimate is also 0 for the same reason (conservative).

Audit: No structured audit schema. audit_schema_enforced = False.

Documented limitation: NeMo has no state machine or RBAC. state_transition
and role-based scenarios are outside its design scope; they are included in
the run for coverage-matrix purposes (not for a fair capability comparison).

Temperature: 0 (via OpenAI provider config). Timeout: EVAL_TIMEOUT_SECONDS.
"""

import os
import time
from pathlib import Path

from eval.runner import BaselineRunner, run_with_timeout
from eval.schema import EVAL_TIMEOUT_SECONDS, ScenarioResult, TraceEntry

_NEMO_CONFIG_DIR = str(Path(__file__).parent / "nemo_config")
_VALID = {"ALLOW", "DENY", "REQUIRE_CONFIRMATION"}


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
            from nemoguardrails import LLMRails, RailsConfig
        except ImportError:
            return self._error(entry, "nemoguardrails package not installed", is_crash=True)

        if not os.environ.get("OPENAI_API_KEY"):
            return self._error(entry, "OPENAI_API_KEY not set", is_crash=True)

        user_msg = entry.user_text
        if entry.proposed_action:
            pa = entry.proposed_action
            user_msg = (
                f"{entry.user_text}\n"
                f"[action type={pa.action_type} name={pa.name}]"
            )

        def _call():
            config = RailsConfig.from_path(_NEMO_CONFIG_DIR)
            rails = LLMRails(config)
            return rails.generate(messages=[{"role": "user", "content": user_msg}])

        t0 = time.perf_counter()
        response, exc = run_with_timeout(_call, timeout=EVAL_TIMEOUT_SECONDS)
        t1 = time.perf_counter()
        e2e_us = (t1 - t0) * 1_000_000

        if exc is not None:
            is_timeout = isinstance(exc, TimeoutError)
            return ScenarioResult(
                scenario_id=entry.scenario_id,
                category=entry.category,
                system=self.name,
                passed=False,
                expected_decision=entry.expected_decision,
                actual_decision="TIMEOUT" if is_timeout else "ERROR",
                expected_layer=entry.expected_layer,
                actual_layer="error",
                expected_reason_code=entry.expected_reason_code,
                actual_reason_code="",
                latency_shim_us=None,
                latency_e2e_us=e2e_us,
                is_timeout=is_timeout,
                is_crash=not is_timeout,
                error=str(exc),
            )

        if isinstance(response, dict):
            text = response.get("content", "").strip().upper()
        else:
            text = str(response).strip().upper()

        actual_decision, is_no_decision = self._parse_decision(text)
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
            latency_shim_us=None,   # no local shim — NeMo always calls LLM
            latency_e2e_us=e2e_us,
            is_no_decision=is_no_decision,
            # NeMo does not expose per-call token usage in its generate() API
            llm_calls=1,
            input_tokens=0,   # not accessible via public API
            output_tokens=0,
            approx_cost_usd=0.0,
        )

    @staticmethod
    def _parse_decision(text: str):
        for decision in ("REQUIRE_CONFIRMATION", "DENY", "ALLOW"):
            if decision in text:
                return decision, False
        return "ALLOW", True

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
