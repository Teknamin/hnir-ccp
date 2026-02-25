"""Pydantic models for the CCP evaluation harness."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ProposedActionSpec(BaseModel):
    """Eval-harness representation of a proposed action (mirrors ccp.models.ProposedAction)."""

    name: str
    action_type: Literal["READ", "WRITE", "DELETE", "IRREVERSIBLE"]
    description: str = ""
    target_state: Optional[str] = None  # ConversationState name or None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class TraceEntry(BaseModel):
    """A single evaluation scenario trace entry."""

    scenario_id: str  # e.g. "ctrl_001", "pol_015", "st_007", "adv_023"
    category: Literal["control_command", "policy_gate", "state_transition", "adversarial"]
    session_id: str
    user_text: str
    proposed_action: Optional[ProposedActionSpec] = None  # None = control cmd only
    initial_state: str  # ConversationState name (e.g. "INTAKE")
    user_roles: List[str]
    expected_decision: Literal["ALLOW", "DENY", "REQUIRE_CONFIRMATION"]
    expected_layer: Literal["control", "state", "policy", "pipeline"]
    expected_reason_code: str  # exact string from ccp/reason_codes.py
    tags: List[str] = Field(default_factory=list)
    source: Literal["hand_crafted", "garak", "tensortrust", "wasp"] = "hand_crafted"
    setup_steps: List[Dict] = Field(default_factory=list)  # prior turns to replay
    notes: str = ""


class ScenarioResult(BaseModel):
    """Result of running a single TraceEntry through a system."""

    scenario_id: str
    category: str
    system: str
    passed: bool
    expected_decision: str
    actual_decision: str
    expected_layer: str
    actual_layer: str
    expected_reason_code: str
    actual_reason_code: str
    latency_us: float = 0.0
    audit_entry_count: int = 0
    audit_has_reason_code: bool = False
    audit_has_layer: bool = False
    error: Optional[str] = None


class MetricReport(BaseModel):
    """Aggregated metrics for a single system."""

    system: str
    policy_compliance: Dict[str, float] = Field(default_factory=dict)
    injection_resistance_pct: float = 0.0
    latency_p50_us: float = 0.0
    latency_p95_us: float = 0.0
    state_transition_correctness: Dict[str, float] = Field(default_factory=dict)
    audit_completeness_pct: float = 0.0
    reproducibility_variance: Optional[float] = None
