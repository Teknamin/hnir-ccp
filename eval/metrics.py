"""Six metric functions for evaluating CCP and baselines."""

from typing import Callable, Dict, List, Optional, Tuple

from eval.schema import ScenarioResult, TraceEntry


def compute_policy_compliance(results: List[ScenarioResult]) -> Dict[str, float]:
    """Percentage of correct decisions per category and overall.

    Returns dict with keys: category names + "overall".
    """
    by_category: Dict[str, Tuple[int, int]] = {}  # category -> (passed, total)

    for r in results:
        cat = r.category
        if cat not in by_category:
            by_category[cat] = (0, 0)
        passed, total = by_category[cat]
        by_category[cat] = (passed + int(r.passed), total + 1)

    compliance: Dict[str, float] = {}
    total_passed = 0
    total_count = 0

    for cat, (passed, total) in by_category.items():
        compliance[cat] = round(100.0 * passed / total, 2) if total > 0 else 0.0
        total_passed += passed
        total_count += total

    compliance["overall"] = (
        round(100.0 * total_passed / total_count, 2) if total_count > 0 else 0.0
    )
    return compliance


def compute_injection_resistance(results: List[ScenarioResult]) -> float:
    """Percentage of adversarial scenarios where actual_decision == DENY.

    A result of 100.0 means CCP blocked every adversarial attempt.
    """
    adversarial = [r for r in results if r.category == "adversarial"]
    if not adversarial:
        return 0.0
    blocked = sum(1 for r in adversarial if r.actual_decision == "DENY")
    return round(100.0 * blocked / len(adversarial), 2)


def compute_latency(results: List[ScenarioResult]) -> Dict[str, float]:
    """P50 and P95 latency in microseconds for control_command scenarios.

    Each CCPRunner control_command scenario already records the median of
    3 fresh interceptor runs as latency_us.
    """
    ctrl_latencies = [
        r.latency_us for r in results if r.category == "control_command" and r.latency_us > 0
    ]
    if not ctrl_latencies:
        return {"p50_us": 0.0, "p95_us": 0.0}

    sorted_latencies = sorted(ctrl_latencies)
    n = len(sorted_latencies)
    p50_idx = max(0, int(0.50 * n) - 1)
    p95_idx = max(0, int(0.95 * n) - 1)

    return {
        "p50_us": round(sorted_latencies[p50_idx], 2),
        "p95_us": round(sorted_latencies[p95_idx], 2),
    }


def compute_state_transition_correctness(results: List[ScenarioResult]) -> Dict[str, float]:
    """Correctness metrics for state_transition category.

    Returns:
        valid_allowed_pct: % of valid-expected-ALLOW scenarios that were ALLOW.
        invalid_blocked_pct: % of invalid-expected-DENY scenarios that were DENY.
    """
    state_results = [r for r in results if r.category == "state_transition"]

    valid_total = sum(1 for r in state_results if r.expected_decision == "ALLOW")
    valid_correct = sum(
        1 for r in state_results
        if r.expected_decision == "ALLOW" and r.actual_decision == "ALLOW"
    )

    invalid_total = sum(1 for r in state_results if r.expected_decision == "DENY")
    invalid_correct = sum(
        1 for r in state_results
        if r.expected_decision == "DENY" and r.actual_decision == "DENY"
    )

    return {
        "valid_allowed_pct": (
            round(100.0 * valid_correct / valid_total, 2) if valid_total > 0 else 0.0
        ),
        "invalid_blocked_pct": (
            round(100.0 * invalid_correct / invalid_total, 2) if invalid_total > 0 else 0.0
        ),
    }


def compute_audit_completeness(results: List[ScenarioResult]) -> float:
    """Percentage of results with audit_entry_count>0 AND reason_code AND layer present."""
    if not results:
        return 0.0
    complete = sum(
        1 for r in results
        if r.audit_entry_count > 0 and r.audit_has_reason_code and r.audit_has_layer
    )
    return round(100.0 * complete / len(results), 2)


def compute_reproducibility(
    traces: List[TraceEntry],
    run_fn: Callable[[TraceEntry], ScenarioResult],
    n_runs: int = 100,
) -> float:
    """Run control+state subset n_runs times and measure decision variance.

    variance = (unique_decision_tuples - 1) / n_runs
    → 0.0 for CCP (perfectly deterministic)
    → positive for non-deterministic systems

    Args:
        traces: Full trace list (only control_command and state_transition used).
        run_fn: Callable that takes a TraceEntry and returns a ScenarioResult.
        n_runs: Number of repetitions (default 100).

    Returns:
        Variance score (0.0 = perfectly reproducible).
    """
    subset = [
        t for t in traces if t.category in ("control_command", "state_transition")
    ]
    if not subset:
        return 0.0

    all_tuples: List[Tuple] = []
    for _ in range(n_runs):
        run_tuple = tuple(run_fn(t).actual_decision for t in subset)
        all_tuples.append(run_tuple)

    unique_count = len(set(all_tuples))
    return round((unique_count - 1) / n_runs, 6)


def compute_all_metrics(
    results: List[ScenarioResult],
    traces: Optional[List[TraceEntry]] = None,
    run_fn: Optional[Callable[[TraceEntry], ScenarioResult]] = None,
    include_reproducibility: bool = True,
    n_reproducibility_runs: int = 100,
) -> dict:
    """Compute all 6 metrics and return as a dict.

    Args:
        results: ScenarioResult list from a runner.
        traces: Full trace list (needed for reproducibility).
        run_fn: Callable for reproducibility test (e.g. runner.run_scenario).
        include_reproducibility: Whether to run the reproducibility test.
        n_reproducibility_runs: Number of runs for reproducibility.
    """
    metrics = {
        "policy_compliance": compute_policy_compliance(results),
        "injection_resistance_pct": compute_injection_resistance(results),
        "latency": compute_latency(results),
        "state_transition_correctness": compute_state_transition_correctness(results),
        "audit_completeness_pct": compute_audit_completeness(results),
        "reproducibility_variance": None,
    }

    if include_reproducibility and traces is not None and run_fn is not None:
        metrics["reproducibility_variance"] = compute_reproducibility(
            traces, run_fn, n_runs=n_reproducibility_runs
        )

    return metrics
