"""OpenAI adapter — function calling via chat.completions.create()."""

import json
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

# OpenAI tool schema wraps ACTION_TOOL_SCHEMA in the expected format
_OPENAI_TOOL = {
    "type": "function",
    "function": ACTION_TOOL_SCHEMA,
}


class OpenAIAdapter(LLMAdapter):
    """LLM adapter backed by OpenAI chat completions with function calling."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
    ) -> None:
        try:
            import openai  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "openai package is required for OpenAIAdapter. "
                "Install it with: pip install hnir-ccp[openai]"
            ) from exc

        resolved_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key= to OpenAIAdapter()."
            )

        import openai as _openai
        self._client = _openai.OpenAI(api_key=resolved_key)
        self._model = model

    def propose(
        self,
        user_input: "UserInput",
        session: "Optional[Session]",
    ) -> ProposedAction:
        """Call OpenAI with tool_choice='required' and parse the tool call."""
        system_prompt = build_system_prompt(session)
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input.text},
                ],
                tools=[_OPENAI_TOOL],
                tool_choice="required",
            )
            tool_calls = response.choices[0].message.tool_calls
            if not tool_calls:
                logger.warning("OpenAI returned no tool calls; using fallback READ action")
                return _FALLBACK_ACTION

            args_raw = tool_calls[0].function.arguments
            return _parse_action(args_raw)

        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("OpenAIAdapter.propose failed: %s; using fallback READ action", exc)
            return _FALLBACK_ACTION

    @property
    def backend_name(self) -> str:
        return "openai"


def _parse_action(args_raw: str) -> ProposedAction:
    """Parse JSON tool-call arguments into a ProposedAction, falling back on error."""
    try:
        data = json.loads(args_raw)
        return ProposedAction(
            name=data["name"],
            action_type=ActionType(data["action_type"]),
            description=data.get("description", ""),
            target_state=data.get("target_state"),
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Failed to parse OpenAI tool call arguments: %s", exc)
        return _FALLBACK_ACTION
