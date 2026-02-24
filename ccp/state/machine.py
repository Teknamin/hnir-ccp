"""State definitions and transition rules for the conversation state machine."""

from datetime import datetime
from typing import Optional

from ccp.config import load_states
from ccp.models import ActionType, ConversationState, StateResult, StatesConfig
from ccp.state import transitions as tx
from ccp import reason_codes as rc


class StateMachine:
    """Validates state transitions and action types against config."""

    def __init__(self, config: Optional[StatesConfig] = None):
        self._config = config or load_states()

    @property
    def initial_state(self) -> ConversationState:
        return self._config.initial_state

    def validate_transition(
        self, from_state: ConversationState, to_state: ConversationState
    ) -> StateResult:
        """Check if a state transition is valid."""
        if tx.is_valid_transition(from_state, to_state, self._config.states):
            return StateResult(
                allowed=True,
                reason=f"Transition {from_state.value} -> {to_state.value} allowed",
                reason_code=rc.state_transition_allowed(from_state.value, to_state.value),
                from_state=from_state,
                to_state=to_state,
            )
        return StateResult(
            allowed=False,
            reason=f"Transition {from_state.value} -> {to_state.value} not allowed",
            reason_code=rc.state_transition_invalid(from_state.value, to_state.value),
            from_state=from_state,
            to_state=to_state,
        )

    def validate_action_type(
        self, state: ConversationState, action_type: ActionType
    ) -> StateResult:
        """Check if an action type is allowed in the current state."""
        if tx.is_action_type_allowed(state, action_type, self._config.states):
            return StateResult(
                allowed=True,
                reason=f"{action_type.value} allowed in {state.value}",
                reason_code=f"STATE_ACTION_ALLOWED_{action_type.value}_IN_{state.value}",
                from_state=state,
            )
        return StateResult(
            allowed=False,
            reason=f"{action_type.value} not allowed in {state.value}",
            reason_code=rc.state_action_type_denied(state.value, action_type.value),
            from_state=state,
        )

    def check_timeout(
        self, state: ConversationState, entered_at: datetime, now: Optional[datetime] = None
    ) -> Optional[int]:
        """Check timeout for current state. Returns remaining seconds (negative = expired)."""
        now = now or datetime.utcnow()
        return tx.check_timeout(state, entered_at, now, self._config.states)
