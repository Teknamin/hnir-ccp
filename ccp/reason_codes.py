"""Reason code template constants for structured audit logging.

Format: {LAYER}_{CATEGORY}_{DETAIL}
"""


def control_command_resolved(command: str) -> str:
    """Reason code for a resolved control command."""
    return f"CONTROL_COMMAND_RESOLVED_{command.upper()}"


def control_command_unknown(text: str) -> str:
    """Reason code for an unknown control command attempt."""
    return f"CONTROL_COMMAND_UNKNOWN_{text.upper()}"


def state_transition_allowed(from_state: str, to_state: str) -> str:
    """Reason code for a valid state transition."""
    return f"STATE_TRANSITION_ALLOWED_FROM_{from_state}_TO_{to_state}"


def state_transition_invalid(from_state: str, to_state: str) -> str:
    """Reason code for an invalid state transition."""
    return f"STATE_TRANSITION_INVALID_FROM_{from_state}_TO_{to_state}"


def state_action_type_denied(state: str, action_type: str) -> str:
    """Reason code for a denied action type in a given state."""
    return f"STATE_ACTION_TYPE_DENIED_{action_type}_IN_{state}"


def state_timeout_expired(state: str) -> str:
    """Reason code for a state timeout."""
    return f"STATE_TIMEOUT_EXPIRED_{state}"


def policy_allowed(rule_name: str) -> str:
    """Reason code for a policy-allowed action."""
    return f"POLICY_ALLOWED_{rule_name.upper()}"


def policy_denied(rule_name: str) -> str:
    """Reason code for a policy-denied action."""
    return f"POLICY_DENIED_{rule_name.upper()}"


def policy_denied_state(rule_name: str, state: str) -> str:
    """Reason code for a policy denial due to state restriction."""
    return f"POLICY_DENIED_STATE_{state}_RULE_{rule_name.upper()}"


def policy_auth_insufficient(roles: str) -> str:
    """Reason code for insufficient authorization."""
    return f"POLICY_AUTH_INSUFFICIENT_ROLE_NEEDS_{roles}"


def policy_confirmation_required(rule_name: str) -> str:
    """Reason code for a confirmation requirement."""
    return f"POLICY_CONFIRMATION_REQUIRED_{rule_name.upper()}"


def policy_confirmation_granted(rule_name: str) -> str:
    """Reason code for a granted confirmation."""
    return f"POLICY_CONFIRMATION_GRANTED_{rule_name.upper()}"


def policy_no_rule(action_type: str) -> str:
    """Reason code when no policy rule matches."""
    return f"POLICY_NO_RULE_FOR_{action_type}"
