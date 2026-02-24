"""Transition validation and precondition checks for state changes."""

from datetime import datetime
from typing import List, Optional

from ccp.models import ActionType, ConversationState, StateDefinition


def is_valid_transition(
    from_state: ConversationState,
    to_state: ConversationState,
    state_defs: List[StateDefinition],
) -> bool:
    """Check if a transition from from_state to to_state is allowed."""
    for sd in state_defs:
        if sd.name == from_state:
            return to_state in sd.allowed_transitions
    return False


def is_action_type_allowed(
    state: ConversationState,
    action_type: ActionType,
    state_defs: List[StateDefinition],
) -> bool:
    """Check if an action type is allowed in the given state."""
    for sd in state_defs:
        if sd.name == state:
            return action_type in sd.allowed_action_types
    return False


def check_timeout(
    state: ConversationState,
    entered_at: datetime,
    now: datetime,
    state_defs: List[StateDefinition],
) -> Optional[int]:
    """Check if the state has timed out. Returns remaining seconds or None if no timeout.

    Returns negative value if timed out.
    """
    for sd in state_defs:
        if sd.name == state:
            if sd.timeout_seconds is None:
                return None
            elapsed = (now - entered_at).total_seconds()
            return int(sd.timeout_seconds - elapsed)
    return None
