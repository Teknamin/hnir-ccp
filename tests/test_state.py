"""Tests for ccp.state."""

from datetime import datetime, timedelta

from ccp.config import load_states
from ccp.models import ActionType, ConversationState
from ccp.state.machine import StateMachine
from ccp.state.session import Session
from ccp.state.transitions import check_timeout, is_action_type_allowed, is_valid_transition


class TestSession:
    def test_initial_state(self):
        s = Session()
        assert s.current_state == ConversationState.INTAKE
        assert s.previous_state is None

    def test_transition(self):
        s = Session()
        s.transition_to(ConversationState.TRIAGE)
        assert s.current_state == ConversationState.TRIAGE
        assert s.previous_state == ConversationState.INTAKE
        assert len(s.state_history) == 2

    def test_rollback(self):
        s = Session()
        s.transition_to(ConversationState.TRIAGE)
        assert s.rollback() is True
        assert s.current_state == ConversationState.INTAKE

    def test_rollback_no_previous(self):
        s = Session()
        assert s.rollback() is False

    def test_reset(self):
        s = Session()
        s.transition_to(ConversationState.TRIAGE)
        s.transition_to(ConversationState.RECOMMENDATION)
        s.reset()
        assert s.current_state == ConversationState.INTAKE

    def test_pending_confirmation(self):
        from ccp.models import ProposedAction
        s = Session()
        action = ProposedAction(name="test", action_type=ActionType.DELETE)
        s.set_pending(action)
        assert s.pending_confirmation is not None
        assert s.pending_confirmation.name == "test"
        s.clear_pending()
        assert s.pending_confirmation is None

    def test_transition_clears_pending(self):
        from ccp.models import ProposedAction
        s = Session()
        action = ProposedAction(name="test", action_type=ActionType.DELETE)
        s.set_pending(action)
        s.transition_to(ConversationState.TRIAGE)
        assert s.pending_confirmation is None

    def test_custom_roles(self):
        s = Session(user_roles={"admin", "user"})
        assert "admin" in s.user_roles


class TestTransitions:
    def setup_method(self):
        self.states = load_states().states

    def test_valid_transition(self):
        assert is_valid_transition(
            ConversationState.INTAKE, ConversationState.TRIAGE, self.states
        ) is True

    def test_invalid_transition(self):
        assert is_valid_transition(
            ConversationState.INTAKE, ConversationState.EXECUTION, self.states
        ) is False

    def test_action_type_allowed(self):
        assert is_action_type_allowed(
            ConversationState.TRIAGE, ActionType.WRITE, self.states
        ) is True

    def test_action_type_denied(self):
        assert is_action_type_allowed(
            ConversationState.INTAKE, ActionType.DELETE, self.states
        ) is False

    def test_timeout_not_expired(self):
        now = datetime.utcnow()
        entered = now - timedelta(seconds=10)
        remaining = check_timeout(ConversationState.INTAKE, entered, now, self.states)
        assert remaining is not None
        assert remaining > 0

    def test_timeout_expired(self):
        now = datetime.utcnow()
        entered = now - timedelta(seconds=999)
        remaining = check_timeout(ConversationState.INTAKE, entered, now, self.states)
        assert remaining is not None
        assert remaining < 0

    def test_no_timeout(self):
        now = datetime.utcnow()
        entered = now - timedelta(seconds=10)
        remaining = check_timeout(ConversationState.COMPLETE, entered, now, self.states)
        assert remaining is None


class TestStateMachine:
    def test_validate_transition_allowed(self):
        sm = StateMachine()
        result = sm.validate_transition(ConversationState.INTAKE, ConversationState.TRIAGE)
        assert result.allowed is True

    def test_validate_transition_denied(self):
        sm = StateMachine()
        result = sm.validate_transition(ConversationState.INTAKE, ConversationState.EXECUTION)
        assert result.allowed is False
        assert "INVALID" in result.reason_code

    def test_validate_action_type_allowed(self):
        sm = StateMachine()
        result = sm.validate_action_type(ConversationState.TRIAGE, ActionType.WRITE)
        assert result.allowed is True

    def test_validate_action_type_denied(self):
        sm = StateMachine()
        result = sm.validate_action_type(ConversationState.INTAKE, ActionType.DELETE)
        assert result.allowed is False

    def test_initial_state(self):
        sm = StateMachine()
        assert sm.initial_state == ConversationState.INTAKE
