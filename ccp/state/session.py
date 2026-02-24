"""Session state storage and retrieval."""

from datetime import datetime
from typing import List, Optional, Set, Tuple

from ccp.models import ConversationState, ProposedAction


class Session:
    """Tracks conversation state, history, user roles, and pending confirmations."""

    def __init__(
        self,
        initial_state: ConversationState = ConversationState.INTAKE,
        user_roles: Optional[Set[str]] = None,
    ):
        self.current_state: ConversationState = initial_state
        self.previous_state: Optional[ConversationState] = None
        self.state_history: List[Tuple[ConversationState, datetime]] = [
            (initial_state, datetime.utcnow())
        ]
        self.user_roles: Set[str] = user_roles or {"user"}
        self.pending_confirmation: Optional[ProposedAction] = None
        self._state_entered_at: datetime = datetime.utcnow()

    @property
    def state_entered_at(self) -> datetime:
        """When the current state was entered."""
        return self._state_entered_at

    def transition_to(self, new_state: ConversationState) -> None:
        """Transition to a new state, updating history."""
        self.previous_state = self.current_state
        self.current_state = new_state
        self._state_entered_at = datetime.utcnow()
        self.state_history.append((new_state, self._state_entered_at))
        self.pending_confirmation = None

    def rollback(self) -> bool:
        """Roll back to the previous state. Returns True if successful."""
        if self.previous_state is None:
            return False
        self.current_state = self.previous_state
        self.previous_state = None
        self._state_entered_at = datetime.utcnow()
        self.state_history.append((self.current_state, self._state_entered_at))
        self.pending_confirmation = None
        return True

    def reset(self, initial_state: ConversationState = ConversationState.INTAKE) -> None:
        """Reset session to initial state."""
        self.previous_state = self.current_state
        self.current_state = initial_state
        self._state_entered_at = datetime.utcnow()
        self.state_history.append((initial_state, self._state_entered_at))
        self.pending_confirmation = None

    def set_pending(self, action: ProposedAction) -> None:
        """Store an action awaiting confirmation."""
        self.pending_confirmation = action

    def clear_pending(self) -> None:
        """Clear any pending confirmation."""
        self.pending_confirmation = None
