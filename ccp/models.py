"""Shared Pydantic models and enums for CCP."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field


# --- Enums (str, Enum) for Python 3.9 compat ---

class ActionType(str, Enum):
    """Classification of actions an LLM agent can propose."""
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    IRREVERSIBLE = "IRREVERSIBLE"


class GateDecision(str, Enum):
    """Policy gate evaluation outcome."""
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_CONFIRMATION = "REQUIRE_CONFIRMATION"


class ConversationState(str, Enum):
    """Conversation state machine states."""
    INTAKE = "INTAKE"
    TRIAGE = "TRIAGE"
    RECOMMENDATION = "RECOMMENDATION"
    CONFIRMATION = "CONFIRMATION"
    EXECUTION = "EXECUTION"
    COMPLETE = "COMPLETE"


class AuditLevel(str, Enum):
    """Severity level for audit entries."""
    INFO = "INFO"
    WARN = "WARN"
    DENY = "DENY"
    CRITICAL = "CRITICAL"


# --- Request / Response Models ---

class UserInput(BaseModel):
    """Raw user input to the CCP pipeline."""
    text: str
    user_id: str = "default"
    roles: Set[str] = Field(default_factory=lambda: {"user"})
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProposedAction(BaseModel):
    """An action proposed by the LLM agent."""
    name: str
    action_type: ActionType
    description: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)
    target_state: Optional[ConversationState] = None


class ControlResult(BaseModel):
    """Result from the control command handler."""
    intercepted: bool
    command: Optional[str] = None
    message: str = ""
    data: Dict[str, Any] = Field(default_factory=dict)


class StateResult(BaseModel):
    """Result from a state machine validation."""
    allowed: bool
    reason: str = ""
    reason_code: str = ""
    from_state: Optional[ConversationState] = None
    to_state: Optional[ConversationState] = None


class PolicyResult(BaseModel):
    """Result from policy gate evaluation."""
    decision: GateDecision
    reason: str = ""
    reason_code: str = ""
    rule_name: Optional[str] = None
    required_roles: Optional[Set[str]] = None


class PipelineResult(BaseModel):
    """Combined result from the full CCP pipeline."""
    decision: GateDecision
    layer: str  # "control", "state", "policy"
    reason: str = ""
    reason_code: str = ""
    action: Optional[ProposedAction] = None
    control_result: Optional[ControlResult] = None
    state_result: Optional[StateResult] = None
    policy_result: Optional[PolicyResult] = None


class AuditEntry(BaseModel):
    """A single structured audit log entry."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str = ""
    layer: str = ""
    level: AuditLevel = AuditLevel.INFO
    event: str = ""
    reason_code: str = ""
    details: Dict[str, Any] = Field(default_factory=dict)


# --- Config Models ---

class PolicyRule(BaseModel):
    """A single policy rule from config."""
    name: str
    action_type: ActionType
    decision: GateDecision
    required_roles: Set[str] = Field(default_factory=set)
    denied_states: List[ConversationState] = Field(default_factory=list)
    require_confirmation: bool = False
    description: str = ""


class PolicyConfig(BaseModel):
    """Top-level policy config."""
    rules: List[PolicyRule]


class StateDefinition(BaseModel):
    """A single state definition from config."""
    name: ConversationState
    allowed_transitions: List[ConversationState] = Field(default_factory=list)
    allowed_action_types: List[ActionType] = Field(default_factory=list)
    timeout_seconds: Optional[int] = None
    description: str = ""


class StatesConfig(BaseModel):
    """Top-level states config."""
    initial_state: ConversationState = ConversationState.INTAKE
    states: List[StateDefinition]


class CommandDefinition(BaseModel):
    """A single control command definition from config."""
    name: str
    aliases: List[str] = Field(default_factory=list)
    description: str = ""
    category: str = "general"


class CommandsConfig(BaseModel):
    """Top-level commands config."""
    commands: List[CommandDefinition]
