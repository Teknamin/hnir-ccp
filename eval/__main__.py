"""CLI entry point for the eval package.

Usage:
    python3 -m eval compare \\
        --baseline PATH.json \\
        --candidate PATH.json \\
        --out DIR \\
        [--allow-unmatched] \\
        [--allow-sev1] \\
        [--allow-sev2]

Exit codes (evaluated in order, ADR-001 Decision 3):
    2  has_duplicates=True (no override)
    2  len(unmatched) > 0 AND --allow-unmatched NOT set
    1  sev0_count > 0 (always)
    1  sev1_count > 0 AND --allow-sev1 NOT set
    1  sev2_count > 0 AND --allow-sev2 NOT set
    0  all other cases

Input format: a JSON file that is a list of ScenarioResult dicts,
or a results.json file (systems[name].scenario_results list).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from eval.compare import CompareResult, ScenarioDiff, compare_results
from eval.schema import ScenarioResult


def _load_results(path: Path) -> List[ScenarioResult]:
    """Load a ScenarioResult list from a JSON file.

    Supports two formats:
      1. A direct JSON array of ScenarioResult dicts.
      2. A results.json with systems[name].scenario_results arrays
         (all available systems' results are flattened together).
    """
    with open(path) as fh:
        data = json.load(fh)

    if isinstance(data, list):
        return [ScenarioResult.model_validate(r) for r in data]

    # results.json format: flatten all available systems
    results: List[ScenarioResult] = []
    for system_data in data.get("systems", {}).values():
        if isinstance(system_data, dict) and system_data.get("available"):
            for r in system_data.get("scenario_results", []):
                results.append(ScenarioResult.model_validate(r))
    return results


def _write_compare_json(result: CompareResult, out_dir: Path) -> Path:
    """Write compare.json with deterministic serialization (ADR-001, Decision 5)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "compare.json"
    content = json.dumps(result.model_dump(), sort_keys=True, indent=2, ensure_ascii=False)
    out_path.write_text(content)
    return out_path


def _write_compare_md(result: CompareResult, out_dir: Path) -> Path:
    """Write compare.md with sections SEV0 → SEV1 → SEV2 → all other diffs."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "compare.md"

    lines: List[str] = [
        "# CCP Eval — Comparison Report",
        "",
        f"**changed_count:** {result.changed_count}  "
        f"|  **SEV0:** {result.sev0_count}  "
        f"|  **SEV1:** {result.sev1_count}  "
        f"|  **SEV2:** {result.sev2_count}",
        "",
    ]

    if result.errors:
        lines += ["## Errors / Warnings", ""]
        for e in result.errors:
            lines.append(f"- {e}")
        lines.append("")

    def _diff_table(title: str, diffs: List[ScenarioDiff]) -> List[str]:
        section: List[str] = [f"## {title}", ""]
        if not diffs:
            section += ["_None._", ""]
            return section
        section += [
            "| scenario_id | category | baseline | candidate | severity |",
            "| --- | --- | --- | --- | --- |",
        ]
        for d in sorted(diffs, key=lambda x: (x.category, x.scenario_id)):
            section.append(
                f"| {d.scenario_id} | {d.category} | {d.baseline_decision} "
                f"| {d.candidate_decision} | {d.severity or 'N/A'} |"
            )
        section.append("")
        return section

    sev0_diffs = [d for d in result.diffs if d.severity == "SEV0"]
    sev1_diffs = [d for d in result.diffs if d.severity == "SEV1"]
    sev2_diffs = [d for d in result.diffs if d.severity == "SEV2"]
    other_diffs = [d for d in result.diffs if d.severity is None]

    lines += _diff_table("SEV0 Regressions (Safety Critical)", sev0_diffs)
    lines += _diff_table("SEV1 Regressions (Security)", sev1_diffs)
    lines += _diff_table("SEV2 Regressions (Policy Correctness)", sev2_diffs)
    lines += _diff_table("All Other Diffs", other_diffs)

    out_path.write_text("\n".join(lines) + "\n")
    return out_path


def _cmd_compare(args: argparse.Namespace) -> int:
    """Run comparison and return exit code per ADR-001 Decision 3."""
    baseline_path = Path(args.baseline)
    candidate_path = Path(args.candidate)
    out_dir = Path(args.out)

    if not baseline_path.exists():
        print(f"ERROR: baseline file not found: {baseline_path}", file=sys.stderr)
        return 2
    if not candidate_path.exists():
        print(f"ERROR: candidate file not found: {candidate_path}", file=sys.stderr)
        return 2

    baseline = _load_results(baseline_path)
    candidate = _load_results(candidate_path)

    result = compare_results(baseline, candidate)

    _write_compare_json(result, out_dir)
    _write_compare_md(result, out_dir)

    print(
        f"changed_count={result.changed_count}  "
        f"sev0={result.sev0_count}  sev1={result.sev1_count}  sev2={result.sev2_count}"
    )

    if result.errors:
        for e in result.errors:
            print(f"  WARN: {e}", file=sys.stderr)

    # --- Exit code evaluation (order matters) ---

    # Exit 2: duplicates (no override)
    if result.has_duplicates:
        print("ERROR: duplicate scenario_ids detected → exit 2", file=sys.stderr)
        return 2

    # Exit 2: unmatched (unless --allow-unmatched)
    if result.unmatched and not args.allow_unmatched:
        print(
            f"ERROR: {len(result.unmatched)} unmatched scenario_id(s) → exit 2",
            file=sys.stderr,
        )
        return 2
    elif result.unmatched:
        print(
            f"WARN: {len(result.unmatched)} unmatched scenario_id(s) (--allow-unmatched)",
            file=sys.stderr,
        )

    # Exit 1: SEV0 (always — no override available)
    if result.sev0_count > 0:
        print(f"FAIL: {result.sev0_count} SEV0 regression(s) → exit 1", file=sys.stderr)
        return 1

    # Exit 1: SEV1 (unless --allow-sev1)
    if result.sev1_count > 0 and not args.allow_sev1:
        print(f"FAIL: {result.sev1_count} SEV1 regression(s) → exit 1", file=sys.stderr)
        return 1
    elif result.sev1_count > 0:
        print(
            f"WARN: {result.sev1_count} SEV1 regression(s) downgraded (--allow-sev1)",
            file=sys.stderr,
        )

    # Exit 1: SEV2 (unless --allow-sev2; banner always printed)
    if result.sev2_count > 0:
        print(
            f"BANNER: {result.sev2_count} SEV2 regression(s) — "
            "DENY→ALLOW in policy_gate/state_transition requires human sign-off",
            file=sys.stderr,
        )
    if result.sev2_count > 0 and not args.allow_sev2:
        print(f"FAIL: {result.sev2_count} SEV2 regression(s) → exit 1", file=sys.stderr)
        return 1
    elif result.sev2_count > 0:
        print(
            f"WARN: {result.sev2_count} SEV2 regression(s) downgraded (--allow-sev2)",
            file=sys.stderr,
        )

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python3 -m eval",
        description="CCP Eval harness CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare two result JSON files and emit compare.json / compare.md",
    )
    compare_parser.add_argument(
        "--baseline", required=True, help="Baseline results JSON file"
    )
    compare_parser.add_argument(
        "--candidate", required=True, help="Candidate results JSON file"
    )
    compare_parser.add_argument(
        "--out", required=True, help="Output directory for compare artifacts"
    )
    compare_parser.add_argument(
        "--allow-unmatched",
        action="store_true",
        help="Treat unmatched scenario_ids as warning (not exit 2)",
    )
    compare_parser.add_argument(
        "--allow-sev1",
        action="store_true",
        help="Treat SEV1 regressions as warning (not exit 1)",
    )
    compare_parser.add_argument(
        "--allow-sev2",
        action="store_true",
        help="Treat SEV2 regressions as warning (not exit 1); banner still printed",
    )

    args = parser.parse_args()

    if args.command == "compare":
        sys.exit(_cmd_compare(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
