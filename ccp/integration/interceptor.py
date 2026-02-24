"""Pre-execution interception of LLM-proposed actions for policy evaluation."""

import uuid
from typing import Optional

from ccp.audit.logger import AuditLogger
from ccp.control.commands import CommandHandler
from ccp.models import (
    AuditLevel,
    GateDecision,
    PipelineResult,
    ProposedAction,
    UserInput,
)
from ccp.policy.gate import PolicyGate
from ccp.state.machine import StateMachine
from ccp.state.session import Session
from ccp import reason_codes as rc


class CCPInterceptor:
    """The CCP pipeline orchestrator.

    Evaluation order: control commands -> state machine -> policy gate.
    """

    def __init__(
        self,
        session: Optional[Session] = None,
        command_handler: Optional[CommandHandler] = None,
        state_machine: Optional[StateMachine] = None,
        policy_gate: Optional[PolicyGate] = None,
        audit_logger: Optional[AuditLogger] = None,
    ):
        self.session = session or Session()
        self._commands = command_handler or CommandHandler()
        self._state_machine = state_machine or StateMachine()
        self._policy = policy_gate or PolicyGate()
        self.audit = audit_logger or AuditLogger()

    def process_input(
        self, user_input: UserInput, proposed_action: Optional[ProposedAction] = None
    ) -> PipelineResult:
        """Process user input through the CCP pipeline.

        1. Check for control commands
        2. If proposed_action: validate state transition + action type
        3. If proposed_action: evaluate policy gate
        """
        request_id = str(uuid.uuid4())[:8]
        self.session.user_roles = user_input.roles

        # --- Layer 1: Control Commands ---
        control_result = self._commands.try_handle(user_input.text)
        if control_result and control_result.intercepted:
            result = self._handle_control_command(control_result, request_id)
            if result is not None:
                return result

        # No proposed action — just pass through
        if proposed_action is None:
            self.audit.log(
                request_id, "pipeline", "No proposed action, pass-through",
                level=AuditLevel.INFO,
            )
            return PipelineResult(
                decision=GateDecision.ALLOW,
                layer="pipeline",
                reason="No action proposed, input passed through",
            )

        # --- Layer 2: State Machine ---
        # Check state transition if target_state specified
        if proposed_action.target_state is not None:
            state_result = self._state_machine.validate_transition(
                self.session.current_state, proposed_action.target_state
            )
            if not state_result.allowed:
                self.audit.log(
                    request_id, "state", state_result.reason,
                    reason_code=state_result.reason_code,
                    level=AuditLevel.DENY,
                    from_state=self.session.current_state.value,
                    to_state=proposed_action.target_state.value,
                )
                return PipelineResult(
                    decision=GateDecision.DENY,
                    layer="state",
                    reason=state_result.reason,
                    reason_code=state_result.reason_code,
                    action=proposed_action,
                    state_result=state_result,
                )

        # Check action type allowed in current state
        action_type_result = self._state_machine.validate_action_type(
            self.session.current_state, proposed_action.action_type
        )
        if not action_type_result.allowed:
            self.audit.log(
                request_id, "state", action_type_result.reason,
                reason_code=action_type_result.reason_code,
                level=AuditLevel.DENY,
                state=self.session.current_state.value,
                action_type=proposed_action.action_type.value,
            )
            return PipelineResult(
                decision=GateDecision.DENY,
                layer="state",
                reason=action_type_result.reason,
                reason_code=action_type_result.reason_code,
                action=proposed_action,
                state_result=action_type_result,
            )

        # --- Layer 3: Policy Gate ---
        # Check if this is a confirmed pending action
        confirmed = False
        if (
            self.session.pending_confirmation is not None
            and proposed_action.name == self.session.pending_confirmation.name
        ):
            confirmed = True

        policy_result = self._policy.evaluate(
            proposed_action.action_type,
            self.session.current_state,
            self.session.user_roles,
            confirmed=confirmed,
        )

        if policy_result.decision == GateDecision.REQUIRE_CONFIRMATION:
            self.session.set_pending(proposed_action)
            self.audit.log(
                request_id, "policy", policy_result.reason,
                reason_code=policy_result.reason_code,
                level=AuditLevel.WARN,
                action=proposed_action.name,
                action_type=proposed_action.action_type.value,
            )
            return PipelineResult(
                decision=GateDecision.REQUIRE_CONFIRMATION,
                layer="policy",
                reason=policy_result.reason,
                reason_code=policy_result.reason_code,
                action=proposed_action,
                policy_result=policy_result,
            )

        if policy_result.decision == GateDecision.DENY:
            self.audit.log(
                request_id, "policy", policy_result.reason,
                reason_code=policy_result.reason_code,
                level=AuditLevel.DENY,
                action=proposed_action.name,
                action_type=proposed_action.action_type.value,
            )
            return PipelineResult(
                decision=GateDecision.DENY,
                layer="policy",
                reason=policy_result.reason,
                reason_code=policy_result.reason_code,
                action=proposed_action,
                policy_result=policy_result,
            )

        # ALLOW — perform state transition if target specified
        if proposed_action.target_state is not None:
            self.session.transition_to(proposed_action.target_state)

        if confirmed:
            self.session.clear_pending()

        self.audit.log(
            request_id, "policy", policy_result.reason,
            reason_code=policy_result.reason_code,
            level=AuditLevel.INFO,
            action=proposed_action.name,
            action_type=proposed_action.action_type.value,
            state=self.session.current_state.value,
        )
        return PipelineResult(
            decision=GateDecision.ALLOW,
            layer="policy",
            reason=policy_result.reason,
            reason_code=policy_result.reason_code,
            action=proposed_action,
            policy_result=policy_result,
        )

    def _handle_control_command(self, control_result, request_id: str):
        """Handle a control command, returning a PipelineResult or None to continue."""
        cmd = control_result.command

        self.audit.log(
            request_id, "control", f"Command: {cmd}",
            reason_code=rc.control_command_resolved(cmd),
            level=AuditLevel.INFO,
        )

        if cmd == "confirm" and self.session.pending_confirmation is not None:
            # Re-process the pending action with confirmed=True
            pending = self.session.pending_confirmation
            self.session.clear_pending()
            # Directly evaluate with confirmed=True
            policy_result = self._policy.evaluate(
                pending.action_type,
                self.session.current_state,
                self.session.user_roles,
                confirmed=True,
            )
            if policy_result.decision == GateDecision.ALLOW:
                if pending.target_state is not None:
                    self.session.transition_to(pending.target_state)
                self.audit.log(
                    request_id, "policy", "Confirmed action allowed",
                    reason_code=rc.policy_confirmation_granted(policy_result.rule_name or ""),
                    level=AuditLevel.INFO,
                    action=pending.name,
                )
            return PipelineResult(
                decision=policy_result.decision,
                layer="control",
                reason=f"Confirmed: {policy_result.reason}",
                reason_code=policy_result.reason_code,
                action=pending,
                control_result=control_result,
                policy_result=policy_result,
            )

        if cmd == "deny" and self.session.pending_confirmation is not None:
            pending = self.session.pending_confirmation
            self.session.clear_pending()
            return PipelineResult(
                decision=GateDecision.DENY,
                layer="control",
                reason="User denied pending action",
                reason_code="CONTROL_DENY_PENDING",
                action=pending,
                control_result=control_result,
            )

        if cmd == "reset":
            self.session.reset(self._state_machine.initial_state)
            return PipelineResult(
                decision=GateDecision.ALLOW,
                layer="control",
                reason="Session reset to initial state",
                reason_code=rc.control_command_resolved("reset"),
                control_result=control_result,
            )

        if cmd == "undo" or cmd == "back":
            success = self.session.rollback()
            msg = "Rolled back to previous state" if success else "No previous state to roll back to"
            return PipelineResult(
                decision=GateDecision.ALLOW,
                layer="control",
                reason=msg,
                reason_code=rc.control_command_resolved(cmd),
                control_result=control_result,
            )

        if cmd == "status":
            control_result.data = {
                "current_state": self.session.current_state.value,
                "previous_state": self.session.previous_state.value if self.session.previous_state else None,
                "user_roles": sorted(self.session.user_roles),
                "pending_confirmation": self.session.pending_confirmation.name if self.session.pending_confirmation else None,
                "history_length": len(self.session.state_history),
            }
            control_result.message = (
                f"State: {self.session.current_state.value} | "
                f"Roles: {', '.join(sorted(self.session.user_roles))} | "
                f"Pending: {self.session.pending_confirmation.name if self.session.pending_confirmation else 'None'}"
            )

        return PipelineResult(
            decision=GateDecision.ALLOW,
            layer="control",
            reason=f"Control command: {cmd}",
            reason_code=rc.control_command_resolved(cmd),
            control_result=control_result,
        )
