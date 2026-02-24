"""Tests for ccp.models."""

from ccp.models import (
    ActionType,
    AuditEntry,
    CommandDefinition,
    ConversationState,
    ControlResult,
    GateDecision,
    PipelineResult,
    PolicyResult,
    ProposedAction,
    StateResult,
    UserInput,
)


def test_action_type_values():
    assert ActionType.READ.value == "READ"
    assert ActionType.IRREVERSIBLE.value == "IRREVERSIBLE"


def test_gate_decision_values():
    assert GateDecision.ALLOW.value == "ALLOW"
    assert GateDecision.DENY.value == "DENY"
    assert GateDecision.REQUIRE_CONFIRMATION.value == "REQUIRE_CONFIRMATION"


def test_conversation_state_values():
    assert ConversationState.INTAKE.value == "INTAKE"
    assert ConversationState.COMPLETE.value == "COMPLETE"


def test_user_input_defaults():
    inp = UserInput(text="hello")
    assert inp.user_id == "default"
    assert "user" in inp.roles
    assert inp.metadata == {}


def test_proposed_action():
    action = ProposedAction(
        name="read_file",
        action_type=ActionType.READ,
        description="Read a file",
    )
    assert action.name == "read_file"
    assert action.action_type == ActionType.READ
    assert action.target_state is None


def test_control_result():
    cr = ControlResult(intercepted=True, command="help", message="Help text")
    assert cr.intercepted is True
    assert cr.command == "help"


def test_state_result():
    sr = StateResult(allowed=True, reason="ok")
    assert sr.allowed is True
    assert sr.from_state is None


def test_policy_result():
    pr = PolicyResult(decision=GateDecision.ALLOW, reason="ok")
    assert pr.decision == GateDecision.ALLOW


def test_pipeline_result():
    pr = PipelineResult(decision=GateDecision.DENY, layer="policy", reason="denied")
    assert pr.decision == GateDecision.DENY
    assert pr.layer == "policy"


def test_audit_entry_defaults():
    entry = AuditEntry(event="test")
    assert entry.level.value == "INFO"
    assert entry.request_id == ""


def test_command_definition():
    cmd = CommandDefinition(name="help", aliases=["?", "h"], description="Show help")
    assert cmd.name == "help"
    assert "?" in cmd.aliases


def test_enum_str_behavior():
    """Verify enums work as strings (str, Enum) for Python 3.9 compat."""
    assert isinstance(ActionType.READ, str)
    assert isinstance(GateDecision.ALLOW, str)
    assert isinstance(ConversationState.INTAKE, str)
