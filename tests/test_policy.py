"""Tests for ccp.policy."""

from ccp.models import ActionType, ConversationState, GateDecision
from ccp.policy.authorization import check_authorization
from ccp.policy.gate import PolicyGate
from ccp.policy.rules import PolicyRuleSet


class TestAuthorization:
    def test_empty_required_roles(self):
        assert check_authorization({"user"}, set()) is True

    def test_has_required_role(self):
        assert check_authorization({"admin", "user"}, {"admin"}) is True

    def test_missing_required_role(self):
        assert check_authorization({"user"}, {"admin"}) is False

    def test_overlap(self):
        assert check_authorization({"user", "viewer"}, {"admin", "viewer"}) is True


class TestPolicyRuleSet:
    def test_find_rule(self):
        rs = PolicyRuleSet()
        rule = rs.find_rule(ActionType.READ)
        assert rule is not None
        assert rule.name == "read_access"

    def test_find_rule_missing(self):
        from ccp.models import PolicyConfig
        rs = PolicyRuleSet(PolicyConfig(rules=[]))
        assert rs.find_rule(ActionType.READ) is None

    def test_all_rules(self):
        rs = PolicyRuleSet()
        assert len(rs.rules) >= 4


class TestPolicyGate:
    def test_read_allowed(self):
        gate = PolicyGate()
        result = gate.evaluate(ActionType.READ, ConversationState.INTAKE, {"user"})
        assert result.decision == GateDecision.ALLOW

    def test_irreversible_denied(self):
        gate = PolicyGate()
        result = gate.evaluate(ActionType.IRREVERSIBLE, ConversationState.EXECUTION, {"admin"})
        assert result.decision == GateDecision.DENY

    def test_delete_denied_in_triage(self):
        gate = PolicyGate()
        result = gate.evaluate(ActionType.DELETE, ConversationState.TRIAGE, {"admin"})
        assert result.decision == GateDecision.DENY

    def test_delete_requires_confirmation(self):
        gate = PolicyGate()
        result = gate.evaluate(ActionType.DELETE, ConversationState.EXECUTION, {"admin"})
        assert result.decision == GateDecision.REQUIRE_CONFIRMATION

    def test_delete_confirmed(self):
        gate = PolicyGate()
        result = gate.evaluate(
            ActionType.DELETE, ConversationState.EXECUTION, {"admin"}, confirmed=True
        )
        assert result.decision == GateDecision.ALLOW

    def test_delete_insufficient_roles(self):
        gate = PolicyGate()
        result = gate.evaluate(ActionType.DELETE, ConversationState.EXECUTION, {"user"})
        assert result.decision == GateDecision.DENY
        assert "Insufficient" in result.reason

    def test_write_requires_user_role(self):
        gate = PolicyGate()
        result = gate.evaluate(ActionType.WRITE, ConversationState.TRIAGE, {"viewer"})
        assert result.decision == GateDecision.DENY

    def test_write_allowed_for_user(self):
        gate = PolicyGate()
        result = gate.evaluate(ActionType.WRITE, ConversationState.TRIAGE, {"user"})
        assert result.decision == GateDecision.ALLOW
