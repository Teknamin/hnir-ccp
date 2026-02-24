"""Mock LLM adapter — scripted responses for deterministic testing and demos."""

from typing import TYPE_CHECKING, List, Optional

from ccp.integration.llm_adapter import LLMAdapter
from ccp.models import ActionType, ProposedAction

if TYPE_CHECKING:
    from ccp.models import UserInput
    from ccp.state.session import Session


class MockAdapter(LLMAdapter):
    """Returns scripted ProposedAction objects for demo and test purposes.

    Uses a queue of pre-configured actions. When the queue is exhausted,
    returns a default READ action.
    """

    def __init__(self, script: Optional[List[ProposedAction]] = None) -> None:
        self._script: List[ProposedAction] = list(script or [])
        self._index = 0

    def propose(
        self,
        user_input: "UserInput",
        session: "Optional[Session]",
    ) -> ProposedAction:
        """Return the next scripted action, or a default READ action."""
        if self._index < len(self._script):
            action = self._script[self._index]
            self._index += 1
            return action
        return ProposedAction(
            name="default_read",
            action_type=ActionType.READ,
            description=f"Default read action for: {user_input.text}",
        )

    def reset(self) -> None:
        """Reset script index to the beginning."""
        self._index = 0

    @property
    def backend_name(self) -> str:
        return "mock"
