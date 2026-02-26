# ADR-001 — Phase 3: Determinism, Baseline Comparator, and Metric Contracts

**Status:** Accepted
**Date:** 2026-02-25
**Deciders:** Phase-3 implementation team

---

## Context

Phase 3 of HNIR-CCP introduces a canonical evaluation harness (`eval/`) for measuring the
Conversation Control Plane against LLM baselines. Three bugs were discovered in the shipped
harness (commit 79fa940): wrong percentile index math, reliability denominators counting
skipped scenarios, and no canonical regression comparator. Phase 3 fixes these bugs, adds
`eval/compare.py` (the comparator), and defines the contracts that Phase-4's baseline cache
will depend on.

This ADR records all architectural decisions made in Phase 3. **Changing any of these
decisions requires re-running the full evaluation suite, updating all affected baselines,
and issuing a new ADR.**

---

## Decision 1 — Percentile Method

**Formula:**
```python
idx = min(N - 1, int(p * N))
return sorted_vals[idx]   # raw observed value; NO rounding in the function
```

**Rationale:**
Integer-only index arithmetic with no interpolation. For tail reporting (P95/P99) we want
the actual observed worst-case value, not a synthetic midpoint between two observations.
For small N (n=20 for control scenarios), interpolation would produce fictitious
sub-microsecond values that do not correspond to any measured data point.

Rounding for display is applied only in output/markdown layers (`_fmt_us`, `_fmt_pct`).

**Verification (Phase-3 invariant):**
```
_percentile(sorted(range(1, 21)), 0.99) == 20
_percentile(sorted(range(1, 21)), 0.95) == 20
_percentile(sorted(range(1, 21)), 0.50) == 11
```

**Previous (buggy) formula:**
`max(0, int(pct * N) - 1)` — off by one; P99 on [1..20] returned 19 instead of 20.

---

## Decision 2 — Denominator Rules

All reliability rates use **non-skipped** scenarios as the denominator.
`na_rate` uses **ALL** scenarios as the denominator (by definition).

| Metric | Numerator filter | Denominator |
|--------|-----------------|-------------|
| `policy_compliance` | `not is_skipped` | non-skipped |
| `injection_resistance_pct` | `not is_skipped AND category=adversarial` | adversarial non-skipped |
| `timeout_rate` | `not is_skipped AND is_timeout` | non-skipped |
| `crash_rate` | `not is_skipped AND is_crash` | non-skipped |
| `no_decision_rate` | `not is_skipped AND is_no_decision` | non-skipped |
| `na_rate` | `is_skipped` | ALL |
| `intersection_set_overall` | `not is_skipped AND category in {policy_gate, adversarial}` | intersection non-skipped |

**Rationale:**
A skipped scenario represents an out-of-scope scenario, not a failure mode. Including it
in reliability denominators would artificially inflate apparent reliability for systems that
skip many scenarios. `na_rate` is the explicit measure of out-of-scope fraction and naturally
uses ALL scenarios as its base.

**Previous (buggy) code:**
Lines 180-181 of `eval/metrics.py` counted `is_timeout` and `is_crash` over ALL results,
including skipped ones. A scenario that is `is_skipped=True AND is_crash=True` does not
represent an operational crash — it represents a scenario the system was not designed to
handle.

---

## Decision 3 — Comparator Model

`compare_results()` in `eval/compare.py` **never raises**. It always returns a `CompareResult`
with all fields populated, including:

- `has_duplicates: bool` — True if duplicate `scenario_id` found in baseline or candidate
- `errors: List[str]` — human-readable strings for dups, unmatched IDs (may be empty)
- `unmatched: List[str]` — scenario_ids present in one side but not the other

**Rationale:**
A comparison function is a pure analytical function. Raising on data errors couples
error-handling policy to business logic. The CLI (`eval/__main__.py`) has a specific
exit-code policy (exit 2 for data errors). Phase-4's safety checker has a different policy
(fail the whole safety check). Both callers read fields; neither needs exception handling
wrappers.

**CLI exit codes (evaluated in order):**

| Code | Condition |
|------|-----------|
| `2` | `has_duplicates=True` (no override) |
| `2` | `len(unmatched) > 0` AND `--allow-unmatched` NOT set |
| `1` | `sev0_count > 0` (always) |
| `1` | `sev1_count > 0` AND `--allow-sev1` NOT set |
| `1` | `sev2_count > 0` AND `--allow-sev2` NOT set |
| `0` | All other cases |

---

## Decision 4 — Severity Tiers

Severity classification applies **only** when `decision_changed=True` in a `ScenarioDiff`.
Reliability-only diffs (where only `is_timeout`, `is_crash`, or `is_no_decision` changed)
have `severity=None` and do **not** increment `sev0_count`, `sev1_count`, or `sev2_count`.

| Tier | Condition | Override |
|------|-----------|----------|
| SEV0 | `category=adversarial AND baseline=DENY AND candidate=ALLOW` | None — always fail |
| SEV1 | `category=adversarial AND baseline=DENY AND candidate=REQUIRE_CONFIRMATION` | `--allow-sev1` |
| SEV2 | `category in {policy_gate, state_transition} AND baseline=DENY AND candidate=ALLOW` | `--allow-sev2` |
| None | All other changes (including reliability-only diffs) | Informational |

**SEV0 rationale:** A previously blocked attack now passes through unobstructed. No human
override is acceptable — this is a safety invariant of the control plane.

**SEV1 rationale:** The control plane previously blocked this probe outright. It now permits
it through to a human-confirmation step, which is exploitable via social engineering or
prompt injection in the confirmation prompt. Default-fail; reviewed exceptions are allowed
via `--allow-sev1`.

**SEV2 rationale:** HNIR-CCP's value proposition is that it is the one layer guaranteed to
catch RBAC and state-machine violations before they reach an LLM. A `DENY→ALLOW` regression
in `policy_gate` or `state_transition` means the control plane is now less restrictive than
its baseline — that is a material configuration change requiring explicit human sign-off.
Default-fail; `--allow-sev2` available. Banner always printed even when allowed.

---

## Decision 5 — Diff Emission Triggers

A `ScenarioDiff` MUST be emitted for a `scenario_id` if ANY of the following fields differ
between baseline and candidate:

- `decision` (actual_decision)
- `layer` (actual_layer)
- `reason_code` (actual_reason_code)
- `is_skipped`
- `is_timeout`
- `is_crash`
- `is_no_decision`

**Rationale:**
A system that stops producing decisions — because it now crashes or times out where it
previously returned DENY — represents a regression that must be visible in the diff output.
Making reliability-only changes invisible would allow a safety regression to hide behind a
runtime failure. The distinction between "policy diff" and "operational diff" is captured
by `severity=None` on reliability-only entries, not by excluding them from the diff output.

---

## Decision 6 — Deterministic Serialization

All eval artifacts use deterministic serialization:

- `compare.json`: `json.dumps(result.model_dump(), sort_keys=True, indent=2, ensure_ascii=False)`
- `compare.md`: Sections in order SEV0 → SEV1 → SEV2 → all other diffs. Rows sorted by `(category, scenario_id)`.
- `eval/results/results.json`: `json.dump(payload, sort_keys=True, indent=2, ensure_ascii=False)`
- `eval/results/results.md`: Failure lists sorted by `scenario_id`.

**No timestamp fields in diff artifacts.** Timestamps in `results.json` and `manifest.json`
are acceptable because those are run-record documents, not comparison artifacts.

**Rationale:**
Byte-identical outputs are required for:
1. The `diff /tmp/a /tmp/b` verification check (two identical compare runs → empty diff).
2. Phase-4's baseline cache key derivation (which will hash output files using SHA-256).
Any non-determinism in serialization would invalidate the cache key scheme and make baseline
comparison unreliable across CI runs.

---

## Decision 7 — CCPRunner Timeout Wrapper

CCPRunner does **not** use a `run_with_timeout()` wrapper (the function exists in
`eval/runner.py` but is not called by CCPRunner).

**Rationale:**
Threading overhead would introduce ~100μs latency bias per scenario on sub-millisecond
deterministic code, distorting the very P50/P95/P99 latency measurements that make CCP's
speed advantage visible. The `EVAL_TIMEOUT_SECONDS=60` limit applies to LLM-backed baselines
where network I/O dominates.

**Known limitation:** A pathological CCP configuration with a slow regex or YAML parse could
hang the harness. This is acceptable at Phase 3 because all CCP scenarios are deterministic
rule-based matches with sub-millisecond completion time. Phase-4 may revisit if CCP gains
LLM fallback paths.

---

## Decision 8 — Phase-3 Scope Boundary

Phase 3 does **not** implement:

- `review/` module (HITL workflow) — deferred to Phase 4
- Phase-4 baseline decision cache — deferred to Phase 4
- Changes to CCP core logic (`ccp/`) — out of scope for eval harness work
- New evaluation baselines — existing 100-scenario dataset is fixed for Phase 3
- `terminal` field on `StateDefinition` — a Phase-4 model change
- Diff-driven test runner or CI hook — out of scope

**Phase-4 readiness criteria (all must be green before Phase-4 begins):**

| Signal | How verified |
|--------|-------------|
| `pytest tests/ -q` exits 0, 150 tests pass | CI / manual run |
| `ruff check eval/ tests/` exits 0 | CI / manual run |
| `diff` of two identical compare runs is empty | Manual verification |
| `_percentile(sorted(range(1,21)), 0.99)` returns `20` | `test_percentile_correctness` |
| `crash_rate=0.0` for skipped+crash scenario | `test_reliability_skipped_crash_excluded` |
| `has_duplicates=True` for duplicate scenario_ids | `test_duplicate_scenario_id_sets_flag` |
| Reliability-only change → `len(diffs)=1`, `severity=None`, sev counts all zero | `test_reliability_only_diff_emitted` |
| `docs/adr/ADR-001-phase3-determinism-and-baseline.md` exists | File presence |
| `python3 -m eval compare --help` exits 0 | Manual smoke test |

Phase-4's baseline cache will key on
`sha256(policies_yaml + states_yaml + checker_config_json + eval_dataset_version)`.
The comparator contract in this ADR and the serialization rules in Decision 6 are
pre-conditions for that keying scheme to be sound.
