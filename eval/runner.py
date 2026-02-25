"""Baseline runner ABC, CCPRunner, and EvalRunner for the evaluation harness."""

import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from statistics import median
from typing import Dict, List, Optional

from eval.schema import ScenarioResult, TraceEntry

# Add the project root to sys.path so ccp is importable when run as script
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from ccp.integration.interceptor import CCPInterceptor  # noqa: E402
from ccp.models import ActionType, ConversationState, ProposedAction, UserInput  # noqa: E402
from ccp.state.session import Session  # noqa: E402


class BaselineRunner(ABC):
    """Abstract base class for all runners (CCP and baselines)."""

    name: str = "base"

    @abstractmethod
    def run_scenario(self, entry: TraceEntry) -> ScenarioResult:
        """Run a single scenario and return a ScenarioResult."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this runner can execute (dependencies met)."""


def _make_proposed_action(spec) -> Optional[ProposedAction]:
    """Convert a ProposedActionSpec (or dict) to a ccp ProposedAction."""
    if spec is None:
        return None
    if isinstance(spec, dict):
        name = spec["name"]
        action_type = ActionType[spec["action_type"]]
        description = spec.get("description", "")
        parameters = spec.get("parameters", {})
        target_state_raw = spec.get("target_state")
    else:
        name = spec.name
        action_type = ActionType[spec.action_type]
        description = spec.description
        parameters = spec.parameters
        target_state_raw = spec.target_state

    target_state = ConversationState[target_state_raw] if target_state_raw else None
    return ProposedAction(
        name=name,
        action_type=action_type,
        description=description,
        parameters=parameters,
        target_state=target_state,
    )


def _replay_setup_steps(interceptor: CCPInterceptor, entry: TraceEntry) -> None:
    """Replay setup_steps on the interceptor to establish preconditions."""
    for step in entry.setup_steps:
        if "set_state" in step:
            # Direct state injection for test setup
            interceptor.session.current_state = ConversationState[step["set_state"]]
            interceptor.session.previous_state = None
            interceptor.session._state_entered_at = __import__("datetime").datetime.utcnow()
        else:
            user_input = UserInput(
                text=step.get("user_text", ""),
                roles=set(entry.user_roles),
            )
            proposed = _make_proposed_action(step.get("proposed_action"))
            interceptor.process_input(user_input, proposed)


class CCPRunner(BaselineRunner):
    """Runs scenarios through the full CCP pipeline."""

    name = "ccp"

    def is_available(self) -> bool:
        return True  # CCP is always available

    def run_scenario(self, entry: TraceEntry) -> ScenarioResult:
        """Run one scenario through CCPInterceptor; measures latency over 3 fresh instances."""
        latency_samples: List[float] = []
        last_result = None
        last_interceptor = None

        # For control_command category: median of 3 fresh interceptors for latency accuracy
        n_runs = 3 if entry.category == "control_command" else 1

        try:
            for _ in range(n_runs):
                interceptor = CCPInterceptor(
                    session=Session(
                        initial_state=ConversationState[entry.initial_state],
                        user_roles=set(entry.user_roles),
                    )
                )
                _replay_setup_steps(interceptor, entry)

                user_input = UserInput(
                    text=entry.user_text,
                    roles=set(entry.user_roles),
                )
                proposed = _make_proposed_action(entry.proposed_action)

                t0 = time.perf_counter()
                result = interceptor.process_input(user_input, proposed)
                t1 = time.perf_counter()

                latency_samples.append((t1 - t0) * 1_000_000)  # convert to microseconds
                last_result = result
                last_interceptor = interceptor

            latency_us = median(latency_samples)

            actual_decision = last_result.decision.value
            actual_layer = last_result.layer
            actual_reason_code = last_result.reason_code

            # Audit metrics
            audit_entries = last_interceptor.audit.entries
            audit_entry_count = len(audit_entries)
            audit_has_reason_code = any(e.reason_code for e in audit_entries)
            audit_has_layer = any(e.layer for e in audit_entries)

        except Exception as exc:
            return ScenarioResult(
                scenario_id=entry.scenario_id,
                category=entry.category,
                system=self.name,
                passed=False,
                expected_decision=entry.expected_decision,
                actual_decision="ERROR",
                expected_layer=entry.expected_layer,
                actual_layer="ERROR",
                expected_reason_code=entry.expected_reason_code,
                actual_reason_code="",
                latency_us=0.0,
                error=str(exc),
            )

        passed = actual_decision == entry.expected_decision

        return ScenarioResult(
            scenario_id=entry.scenario_id,
            category=entry.category,
            system=self.name,
            passed=passed,
            expected_decision=entry.expected_decision,
            actual_decision=actual_decision,
            expected_layer=entry.expected_layer,
            actual_layer=actual_layer,
            expected_reason_code=entry.expected_reason_code,
            actual_reason_code=actual_reason_code,
            latency_us=latency_us,
            audit_entry_count=audit_entry_count,
            audit_has_reason_code=audit_has_reason_code,
            audit_has_layer=audit_has_layer,
        )


class EvalRunner:
    """Orchestrates running all traces through all available runners."""

    def __init__(
        self,
        traces: List[TraceEntry],
        runners: Optional[List[BaselineRunner]] = None,
    ):
        self.traces = traces
        self.runners: List[BaselineRunner] = runners or [CCPRunner()]

    def run_all(self) -> Dict[str, List[ScenarioResult]]:
        """Run all traces through each available runner.

        Returns:
            Dict mapping runner name → list of ScenarioResults.
        """
        results: Dict[str, List[ScenarioResult]] = {}

        for runner in self.runners:
            if not runner.is_available():
                print(
                    f"  [SKIP] {runner.name}: not available "
                    f"(missing dependencies or API key)",
                    file=sys.stderr,
                )
                continue

            print(f"  [RUN ] {runner.name} ({len(self.traces)} scenarios)...", file=sys.stderr)
            runner_results: List[ScenarioResult] = []

            for entry in self.traces:
                sr = runner.run_scenario(entry)
                runner_results.append(sr)

            passed = sum(1 for r in runner_results if r.passed)
            total = len(runner_results)
            print(
                f"  [DONE] {runner.name}: {passed}/{total} passed",
                file=sys.stderr,
            )
            results[runner.name] = runner_results

        return results
