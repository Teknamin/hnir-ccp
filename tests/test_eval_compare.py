"""Unit tests for eval.compare — Phase 3 invariants (PR b).

Test matrix (10 tests):
  1.  test_sev0_adversarial_deny_to_allow        — SEV0 classification and regression list
  2.  test_sev1_adversarial_deny_to_rc           — SEV1 classification
  3.  test_sev2_policy_deny_to_allow             — SEV2 classification
  4.  test_allow_to_deny_no_severity             — ALLOW→DENY on non-adversarial → severity=None
  5.  test_no_change_produces_empty_diffs        — identical inputs → changed_count=0
  6.  test_diff_ordering_by_category_then_id     — diffs sorted (category, scenario_id)
  7.  test_unmatched_ids_in_result               — extra candidate ID → unmatched, not dup
  8.  test_duplicate_scenario_id_sets_flag       — dup baseline ID → has_duplicates=True
  9.  test_reliability_only_diff_emitted         — timeout change → len(diffs)=1, severity=None
  10. test_compare_json_determinism              — same input → identical model_dump_json bytes
"""

import json

from eval.compare import compare_results
from eval.schema import ScenarioResult


def _make_result(
    scenario_id: str,
    category: str = "policy_gate",
    actual_decision: str = "ALLOW",
    actual_layer: str = "policy",
    actual_reason_code: str = "ALLOW_DEFAULT",
    expected_decision: str = "ALLOW",
    expected_layer: str = "policy",
    expected_reason_code: str = "ALLOW_DEFAULT",
    is_skipped: bool = False,
    is_timeout: bool = False,
    is_crash: bool = False,
    is_no_decision: bool = False,
    passed: bool = True,
) -> ScenarioResult:
    return ScenarioResult(
        scenario_id=scenario_id,
        category=category,
        system="test",
        passed=passed,
        expected_decision=expected_decision,
        actual_decision=actual_decision,
        expected_layer=expected_layer,
        actual_layer=actual_layer,
        expected_reason_code=expected_reason_code,
        actual_reason_code=actual_reason_code,
        is_skipped=is_skipped,
        is_timeout=is_timeout,
        is_crash=is_crash,
        is_no_decision=is_no_decision,
    )


def test_sev0_adversarial_deny_to_allow():
    """SEV0: adversarial DENY→ALLOW sets sev0_count=1 and severity='SEV0'."""
    baseline = [_make_result("adv_001", category="adversarial", actual_decision="DENY")]
    candidate = [_make_result("adv_001", category="adversarial", actual_decision="ALLOW")]
    result = compare_results(baseline, candidate)
    assert result.sev0_count == 1
    assert "adv_001" in result.sev0_regressions
    assert result.diffs[0].severity == "SEV0"
    assert result.sev1_count == 0
    assert result.sev2_count == 0


def test_sev1_adversarial_deny_to_rc():
    """SEV1: adversarial DENY→REQUIRE_CONFIRMATION sets sev1_count=1 and severity='SEV1'."""
    baseline = [_make_result("adv_002", category="adversarial", actual_decision="DENY")]
    candidate = [
        _make_result("adv_002", category="adversarial", actual_decision="REQUIRE_CONFIRMATION")
    ]
    result = compare_results(baseline, candidate)
    assert result.sev1_count == 1
    assert "adv_002" not in result.sev0_regressions
    assert result.diffs[0].severity == "SEV1"
    assert result.sev0_count == 0
    assert result.sev2_count == 0


def test_sev2_policy_deny_to_allow():
    """SEV2: policy_gate DENY→ALLOW sets sev2_count=1 and severity='SEV2'."""
    baseline = [_make_result("pol_001", category="policy_gate", actual_decision="DENY")]
    candidate = [_make_result("pol_001", category="policy_gate", actual_decision="ALLOW")]
    result = compare_results(baseline, candidate)
    assert result.sev2_count == 1
    assert "pol_001" not in result.sev0_regressions
    assert "pol_001" not in result.sev1_regressions
    assert result.diffs[0].severity == "SEV2"
    assert result.sev0_count == 0
    assert result.sev1_count == 0


def test_allow_to_deny_no_severity():
    """ALLOW→DENY on non-adversarial: in diffs, severity=None, no sev counts incremented."""
    baseline = [_make_result("pol_002", category="policy_gate", actual_decision="ALLOW")]
    candidate = [_make_result("pol_002", category="policy_gate", actual_decision="DENY")]
    result = compare_results(baseline, candidate)
    assert len(result.diffs) == 1
    assert result.diffs[0].severity is None
    assert result.sev0_count == 0
    assert result.sev1_count == 0
    assert result.sev2_count == 0


def test_no_change_produces_empty_diffs():
    """Identical baseline and candidate produce changed_count=0 and empty diffs."""
    r = _make_result("pol_003", actual_decision="DENY")
    result = compare_results([r], [r])
    assert result.changed_count == 0
    assert len(result.diffs) == 0


def test_diff_ordering_by_category_then_id():
    """Diffs are sorted by (category, scenario_id) regardless of input order."""
    baseline = [
        _make_result("pol_002", category="policy_gate", actual_decision="DENY"),
        _make_result("adv_001", category="adversarial", actual_decision="DENY"),
        _make_result("pol_001", category="policy_gate", actual_decision="DENY"),
    ]
    candidate = [
        _make_result("pol_002", category="policy_gate", actual_decision="ALLOW"),
        _make_result("adv_001", category="adversarial", actual_decision="ALLOW"),
        _make_result("pol_001", category="policy_gate", actual_decision="ALLOW"),
    ]
    result = compare_results(baseline, candidate)
    assert len(result.diffs) == 3
    keys = [(d.category, d.scenario_id) for d in result.diffs]
    assert keys == sorted(keys)


def test_unmatched_ids_in_result():
    """Extra scenario_id in candidate is captured in unmatched, not has_duplicates."""
    baseline = [_make_result("pol_001")]
    candidate = [_make_result("pol_001"), _make_result("pol_999")]
    result = compare_results(baseline, candidate)
    assert len(result.unmatched) == 1
    assert "pol_999" in result.unmatched
    assert result.has_duplicates is False
    assert len(result.errors) == 1


def test_duplicate_scenario_id_sets_flag():
    """Duplicate scenario_id in baseline sets has_duplicates=True and populates errors."""
    baseline = [
        _make_result("pol_001", actual_decision="DENY"),
        _make_result("pol_001", actual_decision="ALLOW"),
    ]
    candidate = [_make_result("pol_001", actual_decision="DENY")]
    result = compare_results(baseline, candidate)
    assert result.has_duplicates is True
    assert len(result.errors) > 0
    assert any("pol_001" in e for e in result.errors)


def test_reliability_only_diff_emitted():
    """A change in is_timeout only emits a diff with timeout_changed=True, severity=None.

    Phase-3 invariant: a system that stops making decisions MUST appear in diffs;
    reliability-only diffs have severity=None and do NOT increment sev counts.
    """
    baseline = [
        _make_result(
            "pol_004",
            actual_decision="DENY",
            actual_layer="policy",
            actual_reason_code="RBAC",
            is_timeout=False,
        )
    ]
    candidate = [
        _make_result(
            "pol_004",
            actual_decision="DENY",
            actual_layer="policy",
            actual_reason_code="RBAC",
            is_timeout=True,
        )
    ]
    result = compare_results(baseline, candidate)
    assert len(result.diffs) == 1
    assert result.diffs[0].timeout_changed is True
    assert result.diffs[0].decision_changed is False
    assert result.diffs[0].severity is None
    assert result.sev0_count == 0
    assert result.sev1_count == 0
    assert result.sev2_count == 0


def test_compare_json_determinism():
    """compare_results() called twice on the same input produces identical model_dump_json bytes.

    Phase-3 invariant (ADR-001 Decision 5): no random/timestamp elements in output.
    """
    baseline = [_make_result("adv_001", category="adversarial", actual_decision="DENY")]
    candidate = [_make_result("adv_001", category="adversarial", actual_decision="ALLOW")]

    result1 = compare_results(baseline, candidate)
    result2 = compare_results(baseline, candidate)

    json1 = json.dumps(result1.model_dump(), sort_keys=True, indent=2, ensure_ascii=False)
    json2 = json.dumps(result2.model_dump(), sort_keys=True, indent=2, ensure_ascii=False)
    assert json1 == json2
