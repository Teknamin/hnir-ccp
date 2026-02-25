"""Pydantic models for the CCP evaluation harness."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# GPT-4o-mini pricing (as of 2026-02; update if pricing changes)
# Source: https://openai.com/api/pricing/
# ---------------------------------------------------------------------------
GPT4O_MINI_INPUT_COST_PER_1M = 0.150   # USD per 1M input tokens
GPT4O_MINI_OUTPUT_COST_PER_1M = 0.600  # USD per 1M output tokens

EVAL_TIMEOUT_SECONDS = 60.0   # per-scenario LLM timeout
EVAL_TEMPERATURE = 0           # fixed for all LLM calls (reproducibility)


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
    passed: bool   # actual_decision == expected_decision (excludes skipped)
    expected_decision: str
    actual_decision: str   # ALLOW / DENY / REQUIRE_CONFIRMATION / TIMEOUT / ERROR / SKIP
    expected_layer: str
    actual_layer: str
    expected_reason_code: str
    actual_reason_code: str

    # ---- Latency (None = N/A for this system/mode) ----
    # shim: guardrail / routing / audit logic only, no LLM network calls
    # e2e: total wall time including all LLM API calls, retries, parsing
    latency_shim_us: Optional[float] = None
    latency_e2e_us: Optional[float] = None

    # ---- Reliability ----
    is_timeout: bool = False     # LLM call exceeded EVAL_TIMEOUT_SECONDS
    is_crash: bool = False       # unhandled exception during scenario run
    is_no_decision: bool = False  # system returned unparseable / empty response
    is_skipped: bool = False     # scenario is out-of-scope for this system (N/A)

    # ---- Audit ----
    audit_entry_count: int = 0
    audit_has_reason_code: bool = False
    audit_has_layer: bool = False
    audit_schema_enforced: bool = False  # structured schema (timestamp+layer+code) present

    # ---- Cost (LLM-based systems only; 0 for deterministic systems) ----
    llm_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    approx_cost_usd: float = 0.0  # see schema.GPT4O_MINI_* constants for rates

    error: Optional[str] = None


class MetricReport(BaseModel):
    """Aggregated metrics for a single system."""

    system: str
    # Safety & correctness
    policy_compliance: Dict[str, Any] = Field(default_factory=dict)
    injection_resistance_pct: Optional[float] = None
    # Reliability
    timeout_rate: float = 0.0
    crash_rate: float = 0.0
    no_decision_rate: float = 0.0
    # Latency
    latency_shim: Dict[str, Optional[float]] = Field(default_factory=dict)  # p50/p95/p99
    latency_e2e: Dict[str, Optional[float]] = Field(default_factory=dict)
    # State transition
    state_transition_correctness: Dict[str, Any] = Field(default_factory=dict)
    # Audit
    audit_completeness_pct: Optional[float] = None
    # Cost
    total_llm_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_cost_per_scenario_usd: float = 0.0
    # Reproducibility
    reproducibility_variance: Optional[float] = None
