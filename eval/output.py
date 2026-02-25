"""Write results.json, results.md, and manifest.json for the evaluation harness."""

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from eval.schema import ScenarioResult, TraceEntry


RESULTS_DIR = Path(__file__).parent / "results"
TRACES_DIR = Path(__file__).parent / "traces"
MANIFEST_PATH = Path(__file__).parent / "manifest.json"


def _git_commit() -> str:
    """Return current git commit hash or 'unknown'."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _file_sha256(path: Path) -> str:
    """Return SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _package_versions() -> Dict[str, str]:
    """Return installed versions of key packages."""
    packages = ["pydantic", "openai", "anthropic", "nemoguardrails", "guardrails", "garak"]
    versions: Dict[str, str] = {}
    for pkg in packages:
        try:
            import importlib.metadata
            versions[pkg] = importlib.metadata.version(pkg)
        except Exception:
            versions[pkg] = "not_installed"
    return versions


def _build_comparison_table(
    systems_metrics: Dict[str, Optional[dict]],
) -> dict:
    """Build the comparison table section of results.json."""
    metric_keys = [
        "policy_compliance_overall",
        "injection_resistance_pct",
        "latency_p50_us",
        "audit_completeness_pct",
        "reproducibility_variance",
    ]

    table: Dict[str, Any] = {"metrics": metric_keys}

    for system, metrics in systems_metrics.items():
        if metrics is None:
            table[system] = None
            continue
        row = [
            metrics.get("policy_compliance", {}).get("overall"),
            metrics.get("injection_resistance_pct"),
            metrics.get("latency", {}).get("p50_us"),
            metrics.get("audit_completeness_pct"),
            metrics.get("reproducibility_variance"),
        ]
        table[system] = row

    return table


def write_results_json(
    all_results: Dict[str, List[ScenarioResult]],
    all_metrics: Dict[str, Optional[dict]],
    system_availability: Dict[str, dict],
    traces: List[TraceEntry],
    eval_duration_seconds: float,
) -> Path:
    """Write eval/results/results.json and return its path."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "results.json"

    # Trace counts
    cat_counts: Dict[str, int] = {}
    for t in traces:
        cat_counts[t.category] = cat_counts.get(t.category, 0) + 1

    # Systems section
    systems: Dict[str, Any] = {}
    for system, avail_info in system_availability.items():
        if not avail_info.get("available", False):
            systems[system] = {
                "available": False,
                "skip_reason": avail_info.get("skip_reason", "not available"),
            }
        else:
            results_list = all_results.get(system, [])
            systems[system] = {
                "available": True,
                "metrics": all_metrics.get(system, {}),
                "scenario_results": [r.model_dump() for r in results_list],
            }

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "eval_duration_seconds": round(eval_duration_seconds, 2),
        "git_commit": _git_commit(),
        "trace_counts": {**cat_counts, "total": len(traces)},
        "systems": systems,
        "comparison_table": _build_comparison_table(all_metrics),
    }

    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=2, default=str)

    return out_path


def write_results_md(
    all_results: Dict[str, List[ScenarioResult]],
    all_metrics: Dict[str, Optional[dict]],
    system_availability: Dict[str, dict],
    traces: List[TraceEntry],
    eval_duration_seconds: float,
) -> Path:
    """Write eval/results/results.md and return its path."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "results.md"

    lines: List[str] = []
    lines.append("# CCP Evaluation Results")
    lines.append("")
    lines.append(
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  "
    )
    lines.append(f"Git commit: `{_git_commit()}`  ")
    lines.append(f"Duration: {eval_duration_seconds:.1f}s  ")
    lines.append(f"Total scenarios: {len(traces)}")
    lines.append("")

    # System availability
    lines.append("## System Availability")
    lines.append("")
    for system, info in system_availability.items():
        status = "✓ available" if info.get("available") else f"✗ skipped ({info.get('skip_reason', '')})"
        lines.append(f"- **{system}**: {status}")
    lines.append("")

    # Metric comparison table
    lines.append("## Metric Comparison")
    lines.append("")
    headers = [
        "System",
        "Policy Compliance %",
        "Injection Resistance %",
        "Latency P50 (μs)",
        "Audit Completeness %",
        "Reproducibility Variance",
    ]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for system, metrics in all_metrics.items():
        if metrics is None:
            continue
        row = [
            system,
            str(metrics.get("policy_compliance", {}).get("overall", "N/A")),
            str(metrics.get("injection_resistance_pct", "N/A")),
            str(metrics.get("latency", {}).get("p50_us", "N/A")),
            str(metrics.get("audit_completeness_pct", "N/A")),
            str(metrics.get("reproducibility_variance", "N/A")),
        ]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Per-category compliance
    lines.append("## Policy Compliance by Category")
    lines.append("")
    cat_headers = ["System", "control_command", "policy_gate", "state_transition", "adversarial", "overall"]
    lines.append("| " + " | ".join(cat_headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(cat_headers)) + " |")
    for system, metrics in all_metrics.items():
        if metrics is None:
            continue
        pc = metrics.get("policy_compliance", {})
        row = [
            system,
            str(pc.get("control_command", "N/A")),
            str(pc.get("policy_gate", "N/A")),
            str(pc.get("state_transition", "N/A")),
            str(pc.get("adversarial", "N/A")),
            str(pc.get("overall", "N/A")),
        ]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # What CCP catches
    lines.append("## What CCP Catches")
    lines.append("")
    lines.append(
        "- **All IRREVERSIBLE action types**: Blocked at state machine layer "
        "(not in any state's allowed_action_types)."
    )
    lines.append(
        "- **Role escalation attacks**: Text-based role claims ignored; "
        "session user_roles is authoritative."
    )
    lines.append(
        "- **State machine skip attacks**: Invalid transitions detected before policy evaluation."
    )
    lines.append(
        "- **DELETE without admin role**: RBAC enforced at policy gate for all DELETE operations."
    )
    lines.append(
        "- **DELETE without confirmation**: Confirmation gate enforced even for admin users."
    )
    lines.append(
        "- **All Garak/TensorTrust/WASP adversarial probes**: Blocked by state or policy layer."
    )
    lines.append("")

    # What CCP does NOT catch
    lines.append("## What CCP Does NOT Catch")
    lines.append("")
    lines.append(
        "- **Prompt injection in natural language** that results in benign action proposals: "
        "CCP evaluates the *proposed action*, not the user text. "
        "If the LLM correctly proposes an allowed READ action despite adversarial text, "
        "CCP passes it through."
    )
    lines.append(
        "- **Semantic deception**: A WRITE action that appears legitimate but causes "
        "harm through its data content — CCP does not inspect data payloads."
    )
    lines.append(
        "- **Timing attacks** or state timeout bypass (timeout checking is separate from "
        "this evaluation harness)."
    )
    lines.append(
        "- **Baseline-specific failures**: NeMo and Guardrails AI do not implement "
        "the state machine or RBAC; their state_transition and role-based scenarios "
        "are out-of-scope by design."
    )
    lines.append("")

    # Failures section (if any)
    for system, results_list in all_results.items():
        failures = [r for r in results_list if not r.passed]
        if failures:
            lines.append(f"## Failures — {system}")
            lines.append("")
            lines.append("| scenario_id | expected | actual | reason_code |")
            lines.append("| --- | --- | --- | --- |")
            for f in failures:
                lines.append(
                    f"| {f.scenario_id} | {f.expected_decision} | "
                    f"{f.actual_decision} | {f.actual_reason_code} |"
                )
            lines.append("")

    with open(out_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")

    return out_path


def write_manifest(traces: List[TraceEntry]) -> Path:
    """Write eval/manifest.json with git commit, package versions, trace file SHA256s."""
    trace_files = [
        Path(__file__).parent / "traces" / "control.jsonl",
        Path(__file__).parent / "traces" / "state.jsonl",
        Path(__file__).parent / "traces" / "policy.jsonl",
        Path(__file__).parent / "traces" / "adversarial.jsonl",
    ]

    file_hashes: Dict[str, str] = {}
    for tf in trace_files:
        if tf.exists():
            file_hashes[tf.name] = _file_sha256(tf)

    manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "git_commit": _git_commit(),
        "package_versions": _package_versions(),
        "trace_file_sha256": file_hashes,
        "total_scenarios": len(traces),
    }

    with open(MANIFEST_PATH, "w") as fh:
        json.dump(manifest, fh, indent=2)

    return MANIFEST_PATH
