"""Unit tests for LLM adapters (no live API calls by default).

Live tests are marked with @pytest.mark.live and skipped unless
the environment variable RUN_LIVE_TESTS=1 is set.
"""

import os
import pytest

from ccp.integration.adapters import AdapterFactory
from ccp.integration.adapters.mock import MockAdapter
from ccp.integration.llm_adapter import LLMAdapter
from ccp.integration.schema import ACTION_TOOL_NAME, ACTION_TOOL_SCHEMA, build_system_prompt
from ccp.models import ActionType, ProposedAction, UserInput


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _user(text: str = "test input") -> UserInput:
    return UserInput(text=text)


# ---------------------------------------------------------------------------
# AdapterFactory
# ---------------------------------------------------------------------------

class TestAdapterFactory:
    def test_create_mock_returns_mock_adapter(self):
        adapter = AdapterFactory.create("mock")
        assert isinstance(adapter, MockAdapter)

    def test_create_default_is_mock(self):
        adapter = AdapterFactory.create()
        assert isinstance(adapter, MockAdapter)

    def test_create_unknown_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown backend"):
            AdapterFactory.create("unknown_backend")

    def test_create_mock_accepts_kwargs(self):
        script = [
            ProposedAction(name="x", action_type=ActionType.READ, description="test")
        ]
        adapter = AdapterFactory.create("mock", script=script)
        assert isinstance(adapter, MockAdapter)

    def test_create_openai_raises_import_error_when_not_installed(self, monkeypatch):
        """If openai is not installed, AdapterFactory.create('openai') raises ImportError."""
        import sys
        # Temporarily hide the openai module if present
        original = sys.modules.get("openai")
        sys.modules["openai"] = None  # type: ignore[assignment]
        try:
            with pytest.raises((ImportError, ValueError)):
                AdapterFactory.create("openai", api_key="dummy")
        finally:
            if original is None:
                sys.modules.pop("openai", None)
            else:
                sys.modules["openai"] = original

    def test_create_anthropic_raises_import_error_when_not_installed(self, monkeypatch):
        """If anthropic is not installed, AdapterFactory.create('anthropic') raises ImportError."""
        import sys
        original = sys.modules.get("anthropic")
        sys.modules["anthropic"] = None  # type: ignore[assignment]
        try:
            with pytest.raises((ImportError, ValueError)):
                AdapterFactory.create("anthropic", api_key="dummy")
        finally:
            if original is None:
                sys.modules.pop("anthropic", None)
            else:
                sys.modules["anthropic"] = original


# ---------------------------------------------------------------------------
# MockAdapter
# ---------------------------------------------------------------------------

class TestMockAdapter:
    def test_backend_name(self):
        assert MockAdapter().backend_name == "mock"

    def test_implements_llm_adapter(self):
        assert isinstance(MockAdapter(), LLMAdapter)

    def test_propose_returns_proposed_action(self):
        adapter = MockAdapter()
        result = adapter.propose(_user("hello"), session=None)
        assert isinstance(result, ProposedAction)
        assert result.action_type in ActionType.__members__.values()

    def test_scripted_sequence(self):
        script = [
            ProposedAction(name="a1", action_type=ActionType.READ, description="first"),
            ProposedAction(name="a2", action_type=ActionType.WRITE, description="second"),
        ]
        adapter = MockAdapter(script=script)
        r1 = adapter.propose(_user("one"), session=None)
        r2 = adapter.propose(_user("two"), session=None)
        assert r1.name == "a1"
        assert r2.name == "a2"

    def test_exhausted_script_returns_default_read(self):
        adapter = MockAdapter(script=[
            ProposedAction(name="only", action_type=ActionType.READ, description="x")
        ])
        adapter.propose(_user("1"), session=None)  # consume the one item
        fallback = adapter.propose(_user("2"), session=None)
        assert fallback.action_type == ActionType.READ
        assert "default" in fallback.name.lower() or "2" in fallback.description

    def test_reset_replays_script(self):
        script = [ProposedAction(name="r1", action_type=ActionType.READ, description="r")]
        adapter = MockAdapter(script=script)
        r1 = adapter.propose(_user("x"), session=None)
        adapter.reset()
        r2 = adapter.propose(_user("x"), session=None)
        assert r1.name == r2.name == "r1"

    def test_no_script_returns_read(self):
        adapter = MockAdapter()
        result = adapter.propose(_user("anything"), session=None)
        assert result.action_type == ActionType.READ

    def test_propose_with_session_none_does_not_crash(self):
        adapter = MockAdapter()
        result = adapter.propose(_user("x"), session=None)
        assert result is not None

    def test_description_contains_user_text_for_default(self):
        adapter = MockAdapter()
        result = adapter.propose(_user("my unique text"), session=None)
        assert "my unique text" in result.description


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class TestSchema:
    def test_action_tool_name_is_string(self):
        assert isinstance(ACTION_TOOL_NAME, str)
        assert ACTION_TOOL_NAME == "propose_action"

    def test_action_tool_schema_has_required_keys(self):
        assert "name" in ACTION_TOOL_SCHEMA
        assert "description" in ACTION_TOOL_SCHEMA
        assert "parameters" in ACTION_TOOL_SCHEMA

    def test_schema_parameters_has_required_fields(self):
        params = ACTION_TOOL_SCHEMA["parameters"]
        assert "properties" in params
        assert "required" in params
        assert "name" in params["required"]
        assert "action_type" in params["required"]
        assert "description" in params["required"]

    def test_action_type_enum_values(self):
        enum_values = ACTION_TOOL_SCHEMA["parameters"]["properties"]["action_type"]["enum"]
        assert set(enum_values) == {"READ", "WRITE", "DELETE", "IRREVERSIBLE"}

    def test_target_state_enum_values(self):
        enum_values = ACTION_TOOL_SCHEMA["parameters"]["properties"]["target_state"]["enum"]
        assert "INTAKE" in enum_values
        assert "EXECUTION" in enum_values
        assert "COMPLETE" in enum_values

    def test_build_system_prompt_with_none_session(self):
        prompt = build_system_prompt(None)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "propose_action" in prompt

    def test_build_system_prompt_includes_state(self):
        from ccp.state.session import Session
        from ccp.models import ConversationState
        session = Session(initial_state=ConversationState.TRIAGE)
        prompt = build_system_prompt(session)
        assert "TRIAGE" in prompt

    def test_build_system_prompt_all_states(self):
        from ccp.state.session import Session
        from ccp.models import ConversationState
        for state in ConversationState:
            session = Session(initial_state=state)
            prompt = build_system_prompt(session)
            assert state.value in prompt

    def test_schema_is_valid_dict(self):
        import json
        # Must be JSON-serialisable
        encoded = json.dumps(ACTION_TOOL_SCHEMA)
        decoded = json.loads(encoded)
        assert decoded["name"] == ACTION_TOOL_SCHEMA["name"]


# ---------------------------------------------------------------------------
# Live integration tests (skipped unless RUN_LIVE_TESTS=1)
# ---------------------------------------------------------------------------

_run_live = os.environ.get("RUN_LIVE_TESTS") == "1"
skip_live = pytest.mark.skipif(not _run_live, reason="Set RUN_LIVE_TESTS=1 to run live tests")


@skip_live
@pytest.mark.live
class TestOpenAIAdapterLive:
    def test_propose_returns_proposed_action(self):
        adapter = AdapterFactory.create("openai")
        result = adapter.propose(_user("show me the patient record"), session=None)
        assert isinstance(result, ProposedAction)
        assert result.action_type in ActionType.__members__.values()

    def test_propose_action_type_is_valid(self):
        adapter = AdapterFactory.create("openai")
        result = adapter.propose(_user("read the intake form"), session=None)
        assert isinstance(result.action_type, ActionType)

    def test_propose_name_is_nonempty(self):
        adapter = AdapterFactory.create("openai")
        result = adapter.propose(_user("what is the patient status?"), session=None)
        assert result.name and isinstance(result.name, str)

    def test_backend_name(self):
        adapter = AdapterFactory.create("openai")
        assert adapter.backend_name == "openai"


@skip_live
@pytest.mark.live
class TestAnthropicAdapterLive:
    def test_propose_returns_proposed_action(self):
        adapter = AdapterFactory.create("anthropic")
        result = adapter.propose(_user("show me the patient record"), session=None)
        assert isinstance(result, ProposedAction)
        assert result.action_type in ActionType.__members__.values()

    def test_propose_action_type_is_valid(self):
        adapter = AdapterFactory.create("anthropic")
        result = adapter.propose(_user("read the intake form"), session=None)
        assert isinstance(result.action_type, ActionType)

    def test_propose_name_is_nonempty(self):
        adapter = AdapterFactory.create("anthropic")
        result = adapter.propose(_user("what is the patient status?"), session=None)
        assert result.name and isinstance(result.name, str)

    def test_backend_name(self):
        adapter = AdapterFactory.create("anthropic")
        assert adapter.backend_name == "anthropic"
