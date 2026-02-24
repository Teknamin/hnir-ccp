"""Abstract base class for LLM adapters."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ccp.models import ProposedAction, UserInput
    from ccp.state.session import Session


class LLMAdapter(ABC):
    """Backend-agnostic interface for proposing actions from an LLM.

    The adapter sits *above* the CCP gate. The gate never calls an LLM.
    This separation is the core invariant: policy enforcement is code,
    LLM reasoning is pluggable.
    """

    @abstractmethod
    def propose(
        self,
        user_input: "UserInput",
        session: "Optional[Session]",
    ) -> "ProposedAction":
        """Given user input and session context, return a proposed action.

        Args:
            user_input: The raw user input object.
            session: Current session state. May be None (e.g. in unit tests).

        Returns:
            A ProposedAction to be forwarded to CCPInterceptor.process_input().
        """

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Identifier logged in audit entries (e.g. 'openai', 'anthropic', 'mock')."""
