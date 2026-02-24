"""Tests for ccp.config."""

from ccp.config import load_commands, load_policies, load_states
from ccp.models import ActionType, ConversationState, GateDecision


def test_load_policies():
    config = load_policies()
    assert len(config.rules) >= 4
    names = [r.name for r in config.rules]
    assert "read_access" in names
    assert "irreversible_block" in names


def test_load_policies_action_types():
    config = load_policies()
    types = {r.action_type for r in config.rules}
    assert ActionType.READ in types
    assert ActionType.IRREVERSIBLE in types


def test_load_policies_irreversible_denied():
    config = load_policies()
    irr = [r for r in config.rules if r.action_type == ActionType.IRREVERSIBLE][0]
    assert irr.decision == GateDecision.DENY


def test_load_states():
    config = load_states()
    assert config.initial_state == ConversationState.INTAKE
    assert len(config.states) == 6
    names = [s.name for s in config.states]
    assert ConversationState.INTAKE in names
    assert ConversationState.COMPLETE in names


def test_load_states_transitions():
    config = load_states()
    intake = [s for s in config.states if s.name == ConversationState.INTAKE][0]
    assert ConversationState.TRIAGE in intake.allowed_transitions


def test_load_states_action_types():
    config = load_states()
    execution = [s for s in config.states if s.name == ConversationState.EXECUTION][0]
    assert ActionType.DELETE in execution.allowed_action_types


def test_load_commands():
    config = load_commands()
    assert len(config.commands) >= 9
    names = [c.name for c in config.commands]
    assert "help" in names
    assert "confirm" in names
    assert "deny" in names


def test_load_commands_aliases():
    config = load_commands()
    help_cmd = [c for c in config.commands if c.name == "help"][0]
    assert "?" in help_cmd.aliases
