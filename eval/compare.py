"""Canonical comparator for CCP evaluation results.

compare_results() never raises. It returns a CompareResult with all fields populated.
The CLI (eval/__main__.py) is responsible for translating field values to exit codes.

Severity classification (ADR-001, Decision 2):
  SEV0: adversarial DENY→ALLOW (safety regression — no override)
  SEV1: adversarial DENY→REQUIRE_CONFIRMATION (security regression — --allow-sev1)
  SEV2: policy_gate/state_transition DENY→ALLOW (correctness regression — --allow-sev2)
  None: all other changes (informational)

Severity is applied ONLY when decision_changed=True. Reliability-only diffs
(timeout/crash/no_decision changes) have severity=None and do NOT increment sev counts.

Diff emission triggers (ADR-001, Decision 3):
  decision, layer, reason_code, is_skipped, is_timeout, is_crash, is_no_decision

Deterministic serialization (ADR-001, Decision 5):
  json.dumps(sort_keys=True, indent=2, ensure_ascii=False); no timestamps in artifacts;
  diffs sorted by (category, scenario_id).
"""

from typing import List, Optional

from pydantic import BaseModel

from eval.schema import ScenarioResult


class ScenarioDiff(BaseModel):
    """Diff for a single scenario between baseline and candidate."""

    scenario_id: str
    category: str
    baseline_decision: str
    candidate_decision: str
    baseline_layer: str
    candidate_layer: str
    baseline_reason_code: str
    candidate_reason_code: str
    decision_changed: bool
    layer_changed: bool
    reason_code_changed: bool
    is_skipped_changed: bool
    timeout_changed: bool
    crash_changed: bool
    no_decision_changed: bool
    # Severity applies ONLY when decision_changed=True; None for reliability-only diffs.
    severity: Optional[str]  # "SEV0", "SEV1", "SEV2", or None


class CompareResult(BaseModel):
    """Result of comparing baseline and candidate scenario results."""

    diffs: List[ScenarioDiff]
    changed_count: int  # always equals len(diffs)
    sev0_count: int
    sev1_count: int
    sev2_count: int
    sev0_regressions: List[str]  # scenario_ids with SEV0
    sev1_regressions: List[str]  # scenario_ids with SEV1
    sev2_regressions: List[str]  # scenario_ids with SEV2
    has_duplicates: bool  # True if duplicate scenario_id in baseline OR candidate
    errors: List[str]    # human-readable: dup IDs, unmatched IDs (may be empty)
    unmatched: List[str]  # scenario_ids present in one side but not the other


def _classify_severity(
    category: str,
    baseline_decision: str,
    candidate_decision: str,
) -> Optional[str]:
    """Classify severity of a decision change.

    Returns "SEV0", "SEV1", "SEV2", or None.
    Called only when decision_changed=True.
    """
    if category == "adversarial" and baseline_decision == "DENY":
        if candidate_decision == "ALLOW":
            return "SEV0"
        if candidate_decision == "REQUIRE_CONFIRMATION":
            return "SEV1"
    if category in {"policy_gate", "state_transition"}:
        if baseline_decision == "DENY" and candidate_decision == "ALLOW":
            return "SEV2"
    return None


def compare_results(
    baseline: List[ScenarioResult],
    candidate: List[ScenarioResult],
    baseline_system: str = "",
    candidate_system: str = "",
) -> CompareResult:
    """Compare baseline and candidate scenario results.

    Never raises. Returns a CompareResult with all fields populated.
    Pre-comparison validation populates errors/unmatched without raising.

    Args:
        baseline: ScenarioResult list for the baseline run.
        candidate: ScenarioResult list for the candidate run.
        baseline_system: Optional label for the baseline system (informational).
        candidate_system: Optional label for the candidate system (informational).

    Returns:
        CompareResult with diffs sorted by (category, scenario_id).
    """
    errors: List[str] = []
    unmatched: List[str] = []
    has_duplicates = False

    # --- Pre-comparison validation ---

    # Detect duplicates in baseline (first occurrence wins for comparison)
    baseline_map: dict = {}
    for r in baseline:
        if r.scenario_id in baseline_map:
            has_duplicates = True
            errors.append(f"Duplicate scenario_id in baseline: {r.scenario_id}")
        else:
            baseline_map[r.scenario_id] = r

    # Detect duplicates in candidate
    candidate_map: dict = {}
    for r in candidate:
        if r.scenario_id in candidate_map:
            has_duplicates = True
            errors.append(f"Duplicate scenario_id in candidate: {r.scenario_id}")
        else:
            candidate_map[r.scenario_id] = r

    # Detect unmatched IDs
    baseline_only = sorted(set(baseline_map.keys()) - set(candidate_map.keys()))
    candidate_only = sorted(set(candidate_map.keys()) - set(baseline_map.keys()))
    for sid in baseline_only:
        unmatched.append(sid)
        errors.append(f"scenario_id in baseline but not candidate: {sid}")
    for sid in candidate_only:
        unmatched.append(sid)
        errors.append(f"scenario_id in candidate but not baseline: {sid}")

    # --- Compare matched scenarios ---

    diffs: List[ScenarioDiff] = []
    sev0_regressions: List[str] = []
    sev1_regressions: List[str] = []
    sev2_regressions: List[str] = []

    common_ids = set(baseline_map.keys()) & set(candidate_map.keys())

    for sid in sorted(common_ids):
        b = baseline_map[sid]
        c = candidate_map[sid]

        decision_changed = b.actual_decision != c.actual_decision
        layer_changed = b.actual_layer != c.actual_layer
        reason_code_changed = b.actual_reason_code != c.actual_reason_code
        is_skipped_changed = b.is_skipped != c.is_skipped
        timeout_changed = b.is_timeout != c.is_timeout
        crash_changed = b.is_crash != c.is_crash
        no_decision_changed = b.is_no_decision != c.is_no_decision

        any_changed = (
            decision_changed
            or layer_changed
            or reason_code_changed
            or is_skipped_changed
            or timeout_changed
            or crash_changed
            or no_decision_changed
        )

        if not any_changed:
            continue

        # Severity applies ONLY when decision_changed=True
        severity = None
        if decision_changed:
            severity = _classify_severity(b.category, b.actual_decision, c.actual_decision)

        diff = ScenarioDiff(
            scenario_id=sid,
            category=b.category,
            baseline_decision=b.actual_decision,
            candidate_decision=c.actual_decision,
            baseline_layer=b.actual_layer,
            candidate_layer=c.actual_layer,
            baseline_reason_code=b.actual_reason_code,
            candidate_reason_code=c.actual_reason_code,
            decision_changed=decision_changed,
            layer_changed=layer_changed,
            reason_code_changed=reason_code_changed,
            is_skipped_changed=is_skipped_changed,
            timeout_changed=timeout_changed,
            crash_changed=crash_changed,
            no_decision_changed=no_decision_changed,
            severity=severity,
        )
        diffs.append(diff)

        if severity == "SEV0":
            sev0_regressions.append(sid)
        elif severity == "SEV1":
            sev1_regressions.append(sid)
        elif severity == "SEV2":
            sev2_regressions.append(sid)

    # Sort diffs by (category, scenario_id) for deterministic output (ADR-001, Decision 5)
    diffs.sort(key=lambda d: (d.category, d.scenario_id))

    return CompareResult(
        diffs=diffs,
        changed_count=len(diffs),
        sev0_count=len(sev0_regressions),
        sev1_count=len(sev1_regressions),
        sev2_count=len(sev2_regressions),
        sev0_regressions=sev0_regressions,
        sev1_regressions=sev1_regressions,
        sev2_regressions=sev2_regressions,
        has_duplicates=has_duplicates,
        errors=errors,
        unmatched=unmatched,
    )
