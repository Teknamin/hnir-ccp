"""Unit tests for eval.metrics — Phase 3 invariants (PR a).

Test matrix (5 tests):
  1. test_percentile_correctness         — P99/P95/P50 on [1..20]
  2. test_percentile_single_element      — single-element list
  3. test_reliability_skipped_crash_excluded — is_skipped+is_crash → crash_rate unaffected
  4. test_cost_correctness               — total_cost_usd and avg_cost_per_scenario_usd
  5. test_intersection_set_denominator   — intersection denominator excludes non-intersection
"""

from eval.metrics import (
    _percentile,
    compute_cost,
    compute_policy_compliance,
    compute_reliability,
)
from eval.schema import ScenarioResult


def _make_result(
    scenario_id: str,
    category: str = "policy_gate",
    passed: bool = True,
    expected_decision: str = "ALLOW",
    actual_decision: str = "ALLOW",
    expected_layer: str = "policy",
    actual_layer: str = "policy",
    expected_reason_code: str = "ALLOW_DEFAULT",
    actual_reason_code: str = "ALLOW_DEFAULT",
    is_skipped: bool = False,
    is_timeout: bool = False,
    is_crash: bool = False,
    is_no_decision: bool = False,
    llm_calls: int = 0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    approx_cost_usd: float = 0.0,
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
        llm_calls=llm_calls,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        approx_cost_usd=approx_cost_usd,
    )


def test_percentile_correctness():
    """Phase-3 invariant: _percentile([1..20], p) returns the raw observed value.

    ADR-001 Decision 4: idx = min(N-1, int(p * N)); return sorted_vals[idx]
    N=20:
      P99: min(19, int(0.99*20)) = min(19, 19) = 19 → value 20
      P95: min(19, int(0.95*20)) = min(19, 19) = 19 → value 20
      P50: min(19, int(0.50*20)) = min(19, 10) = 10 → value 11
    """
    vals = sorted(range(1, 21))  # [1, 2, ..., 20], N=20
    assert _percentile(vals, 0.99) == 20
    assert _percentile(vals, 0.95) == 20
    assert _percentile(vals, 0.50) == 11


def test_percentile_single_element():
    """Single-element list returns that element regardless of percentile."""
    assert _percentile([42.0], 0.99) == 42.0


def test_reliability_skipped_crash_excluded():
    """A crash in a skipped scenario does not increment crash_rate.

    Phase-3 invariant: crash_rate denominator = non-skipped scenarios only.
    """
    non_skipped = _make_result("pol_001", passed=True)
    skipped_crash = _make_result(
        "ctrl_001",
        category="control_command",
        is_skipped=True,
        is_crash=True,
    )
    rel = compute_reliability([non_skipped, skipped_crash])
    # evaluated=1 (non_skipped), crashes=0 (skipped result excluded)
    assert rel["crash_rate"] == 0.0


def test_cost_correctness():
    """total_cost_usd and avg_cost_per_scenario_usd computed correctly to 8 decimal places."""
    r1 = _make_result(
        "pol_001", llm_calls=1, input_tokens=1000, output_tokens=500, approx_cost_usd=0.00045
    )
    r2 = _make_result(
        "pol_002", llm_calls=1, input_tokens=2000, output_tokens=1000, approx_cost_usd=0.0009
    )
    r3 = _make_result(
        "pol_003", llm_calls=1, input_tokens=500, output_tokens=250, approx_cost_usd=0.000225
    )
    cost = compute_cost([r1, r2, r3])
    expected_total = 0.00045 + 0.0009 + 0.000225
    assert round(cost["total_cost_usd"], 6) == round(expected_total, 6)
    assert round(cost["avg_cost_per_scenario_usd"], 8) == round(expected_total / 3, 8)


def test_intersection_set_denominator():
    """Intersection denominator includes only policy_gate + adversarial.

    Setup: 10 policy_gate (all pass) + 10 adversarial (all pass) + 5 control_command (all fail)
    → intersection_count=20, intersection_set_overall=100.0, overall < 100.0

    Proves: intersection denominator excludes control_command;
            overall denominator includes all non-skipped categories.
    """
    results = []

    # 10 policy_gate — all pass
    for i in range(10):
        results.append(
            _make_result(
                f"pol_{i:03d}",
                category="policy_gate",
                passed=True,
                expected_decision="DENY",
                actual_decision="DENY",
                expected_layer="policy",
                actual_layer="policy",
                expected_reason_code="RBAC",
                actual_reason_code="RBAC",
            )
        )

    # 10 adversarial — all pass
    for i in range(10):
        results.append(
            _make_result(
                f"adv_{i:03d}",
                category="adversarial",
                passed=True,
                expected_decision="DENY",
                actual_decision="DENY",
                expected_layer="policy",
                actual_layer="policy",
                expected_reason_code="ADVERSARIAL",
                actual_reason_code="ADVERSARIAL",
            )
        )

    # 5 control_command — all FAIL (drag down overall)
    for i in range(5):
        results.append(
            _make_result(
                f"ctrl_{i:03d}",
                category="control_command",
                passed=False,
                expected_decision="ALLOW",
                actual_decision="DENY",
                expected_layer="control",
                actual_layer="policy",
                expected_reason_code="CTRL_PASS",
                actual_reason_code="RBAC_DENY",
            )
        )

    compliance = compute_policy_compliance(results)

    assert compliance.get("intersection_count") == 20
    assert compliance["intersection_set_overall"] == 100.0
    assert compliance["overall"] is not None
    assert compliance["overall"] < 100.0
