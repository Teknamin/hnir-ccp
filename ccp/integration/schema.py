"""Shared tool schema and system prompt builder for LLM adapters."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccp.state.session import Session

ACTION_TOOL_NAME = "propose_action"

ACTION_TOOL_SCHEMA = {
    "name": ACTION_TOOL_NAME,
    "description": "Propose a single action to be executed in the conversation workflow.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Short action identifier",
            },
            "action_type": {
                "type": "string",
                "enum": ["READ", "WRITE", "DELETE", "IRREVERSIBLE"],
                "description": (
                    "READ=safe/info. WRITE=state-changing. "
                    "DELETE=destructive. IRREVERSIBLE=permanent, avoid."
                ),
            },
            "description": {"type": "string"},
            "target_state": {
                "type": "string",
                "enum": ["INTAKE", "TRIAGE", "RECOMMENDATION", "CONFIRMATION", "EXECUTION", "COMPLETE"],
                "description": (
                    "Optional: request a state transition if this action should "
                    "advance the workflow."
                ),
            },
        },
        "required": ["name", "action_type", "description"],
    },
}


def build_system_prompt(session: "Session | None") -> str:
    """Build a context-aware system prompt from the current session state."""
    state_value = session.current_state.value if session is not None else "UNKNOWN"
    return (
        "You are a clinical workflow assistant operating inside a governed control plane.\n"
        "You MUST respond by calling the `propose_action` tool — no free-text responses.\n\n"
        f"Current conversation state: {state_value}\n\n"
        "Action type rules:\n"
        "  READ        — Safe, informational. Always permitted in early states.\n"
        "  WRITE       — State-changing. Allowed for authorised users.\n"
        "  DELETE      — Destructive. Requires admin role and confirmation.\n"
        "  IRREVERSIBLE — Permanent operation. Never propose unless explicitly required.\n\n"
        "Choose the most appropriate action_type for the user's request. "
        "Only propose DELETE or IRREVERSIBLE when the user has explicitly requested a "
        "destructive or permanent operation."
    )
