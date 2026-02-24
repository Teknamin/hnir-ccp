"""Anthropic adapter — tool use via messages.create()."""

import logging
import os
from typing import TYPE_CHECKING, Optional

from ccp.integration.llm_adapter import LLMAdapter
from ccp.integration.schema import ACTION_TOOL_SCHEMA, build_system_prompt
from ccp.models import ActionType, ProposedAction

if TYPE_CHECKING:
    from ccp.models import UserInput
    from ccp.state.session import Session

logger = logging.getLogger(__name__)

_FALLBACK_ACTION = ProposedAction(
    name="fallback_read",
    action_type=ActionType.READ,
    description="Parse error fallback",
)

# Anthropic tool schema: wrap parameters as input_schema
_ANTHROPIC_TOOL = {
    "name": ACTION_TOOL_SCHEMA["name"],
    "description": ACTION_TOOL_SCHEMA["description"],
    "input_schema": ACTION_TOOL_SCHEMA["parameters"],
}


class AnthropicAdapter(LLMAdapter):
    """LLM adapter backed by Anthropic messages API with tool use."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-haiku-4-5-20251001",
    ) -> None:
        try:
            import anthropic  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "anthropic package is required for AnthropicAdapter. "
                "Install it with: pip install hnir-ccp[anthropic]"
            ) from exc

        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise ValueError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key= to AnthropicAdapter()."
            )

        import anthropic as _anthropic
        self._client = _anthropic.Anthropic(api_key=resolved_key)
        self._model = model

    def propose(
        self,
        user_input: "UserInput",
        session: "Optional[Session]",
    ) -> ProposedAction:
        """Call Anthropic with tool_choice={'type':'any'} and parse the tool_use block."""
        system_prompt = build_system_prompt(session)
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=256,
                system=system_prompt,
                messages=[{"role": "user", "content": user_input.text}],
                tools=[_ANTHROPIC_TOOL],
                tool_choice={"type": "any"},
            )
            # Find the tool_use content block
            tool_block = next(
                (b for b in response.content if b.type == "tool_use"),
                None,
            )
            if tool_block is None:
                logger.warning("Anthropic returned no tool_use block; using fallback READ action")
                return _FALLBACK_ACTION

            return _parse_action(tool_block.input)

        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("AnthropicAdapter.propose failed: %s; using fallback READ action", exc)
            return _FALLBACK_ACTION

    @property
    def backend_name(self) -> str:
        return "anthropic"


def _parse_action(data: dict) -> ProposedAction:
    """Parse tool input dict into a ProposedAction, falling back on error."""
    try:
        return ProposedAction(
            name=data["name"],
            action_type=ActionType(data["action_type"]),
            description=data.get("description", ""),
            target_state=data.get("target_state"),
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Failed to parse Anthropic tool input: %s", exc)
        return _FALLBACK_ACTION
