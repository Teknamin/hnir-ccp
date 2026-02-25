"""Evaluation harness entry point.

Usage:
    python3 eval/run.py                          # CCP only (no API key needed)
    python3 eval/run.py --include-raw-llm        # + Baseline A (Raw LLM)
    python3 eval/run.py --include-nemo           # + Baseline B (NeMo Guardrails)
    python3 eval/run.py --include-guardrails     # + Baseline C (Guardrails AI)
    python3 eval/run.py --include-garak          # + live Garak probes
    python3 eval/run.py --all                    # all available baselines
    python3 eval/run.py --category adversarial   # single category only
    python3 eval/run.py --no-reproducibility     # skip 100-run repro test
    python3 eval/run.py --dry-run                # validate traces only, no execution

Exit code: 0 if CCP achieves 100% on all deterministic scenarios.
"""

import argparse
import sys
import tempfile
import time
from pathlib import Path
from typing import List, Optional

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from eval.dataset import load_traces, validate_only  # noqa: E402
from eval.metrics import compute_all_metrics  # noqa: E402
from eval.output import write_manifest, write_results_json, write_results_md  # noqa: E402
from eval.runner import BaselineRunner, CCPRunner, EvalRunner  # noqa: E402
from eval.schema import TraceEntry  # noqa: E402


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CCP Phase 3 Evaluation Harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--include-raw-llm", action="store_true", help="Include Raw LLM baseline")
    parser.add_argument("--include-nemo", action="store_true", help="Include NeMo Guardrails baseline")
    parser.add_argument("--include-guardrails", action="store_true", help="Include Guardrails AI baseline")
    parser.add_argument("--include-garak", action="store_true", help="Include live Garak adversarial probes")
    parser.add_argument("--all", dest="all_baselines", action="store_true", help="Include all available baselines")
    parser.add_argument(
        "--category",
        choices=["control_command", "policy_gate", "state_transition", "adversarial"],
        help="Run only a single category",
    )
    parser.add_argument("--no-reproducibility", action="store_true", help="Skip reproducibility test")
    parser.add_argument("--dry-run", action="store_true", help="Validate traces only, no execution")
    return parser.parse_args()


def _build_runners(args: argparse.Namespace) -> List[BaselineRunner]:
    """Build the list of runners based on CLI flags."""
    runners: List[BaselineRunner] = [CCPRunner()]

    include_raw = args.include_raw_llm or args.all_baselines
    include_nemo = args.include_nemo or args.all_baselines
    include_guardrails = args.include_guardrails or args.all_baselines

    if include_raw:
        try:
            from eval.baselines.raw_llm import RawLLMRunner
            runners.append(RawLLMRunner())
        except ImportError as e:
            print(f"  [WARN] Could not import RawLLMRunner: {e}", file=sys.stderr)

    if include_nemo:
        try:
            from eval.baselines.nemo import NeMoRunner
            runners.append(NeMoRunner())
        except ImportError as e:
            print(f"  [WARN] Could not import NeMoRunner: {e}", file=sys.stderr)

    if include_guardrails:
        try:
            from eval.baselines.guardrails_ai import GuardrailsAIRunner
            runners.append(GuardrailsAIRunner())
        except ImportError as e:
            print(f"  [WARN] Could not import GuardrailsAIRunner: {e}", file=sys.stderr)

    return runners


def _load_garak_traces(args: argparse.Namespace) -> List[TraceEntry]:
    """Load Garak adversarial traces if --include-garak flag is set."""
    if not (args.include_garak or args.all_baselines):
        return []
    try:
        from eval.benchmarks.garak_runner import GarakRunner
        gr = GarakRunner()
        if not gr.is_available():
            print("  [WARN] Garak not available (missing garak package or OPENAI_API_KEY)", file=sys.stderr)
            return []
        print("  [RUN ] Running Garak probes (this may take a minute)...", file=sys.stderr)
        garak_traces = gr.run_probes()
        print(f"  [DONE] Garak produced {len(garak_traces)} adversarial traces", file=sys.stderr)
        return garak_traces
    except ImportError as e:
        print(f"  [WARN] Could not import GarakRunner: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  [WARN] Garak probe run failed: {e}", file=sys.stderr)
        return []


def main() -> int:
    args = _parse_args()
    t_start = time.perf_counter()

    # --- Dry run: validate only ---
    if args.dry_run:
        print("Validating traces (dry-run)...", file=sys.stderr)
        try:
            summary = validate_only()
            print(f"  OK: {summary['total']} scenarios validated", file=sys.stderr)
            for cat, count in summary["categories"].items():
                print(f"      {cat}: {count}", file=sys.stderr)
            return 0
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            return 1

    # --- Load traces ---
    garak_traces = _load_garak_traces(args)

    # Write Garak traces to a temp file for loading if any
    garak_file: Optional[Path] = None
    if garak_traces:
        garak_file_handle = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, dir=Path(__file__).parent / "traces"
        )
        for t in garak_traces:
            garak_file_handle.write(t.model_dump_json() + "\n")
        garak_file_handle.close()
        garak_file = Path(garak_file_handle.name)

    try:
        traces = load_traces(extra_file=garak_file, category=args.category)
    except Exception as e:
        print(f"ERROR loading traces: {e}", file=sys.stderr)
        return 1
    finally:
        if garak_file and garak_file.exists():
            garak_file.unlink()

    print(f"Loaded {len(traces)} traces", file=sys.stderr)

    # --- Build runners ---
    runners = _build_runners(args)

    # --- Run evaluation ---
    eval_runner = EvalRunner(traces=traces, runners=runners)
    all_results = eval_runner.run_all()

    # --- Compute metrics ---
    all_metrics = {}
    system_availability = {}

    # Mark all requested runners' availability
    for runner in runners:
        avail = runner.is_available()
        system_availability[runner.name] = {
            "available": avail,
            "skip_reason": "" if avail else "dependencies not met or API key missing",
        }

    # Mark skipped baselines
    for name in ["raw_llm", "nemo", "guardrails_ai"]:
        if name not in system_availability:
            system_availability[name] = {
                "available": False,
                "skip_reason": "not requested (use --include-* or --all)",
            }

    for system, results_list in all_results.items():
        ccp_runner = next((r for r in runners if r.name == system), None)
        run_fn = ccp_runner.run_scenario if ccp_runner else None

        all_metrics[system] = compute_all_metrics(
            results=results_list,
            traces=traces,
            run_fn=run_fn,
            include_reproducibility=not args.no_reproducibility,
            n_reproducibility_runs=100,
        )
        # Mark available in system_availability if not already set
        if system not in system_availability:
            system_availability[system] = {"available": True, "skip_reason": ""}

    # Fill None metrics for unavailable systems
    for system, info in system_availability.items():
        if not info["available"] and system not in all_metrics:
            all_metrics[system] = None

    t_end = time.perf_counter()
    eval_duration = t_end - t_start

    # --- Write outputs ---
    write_manifest(traces)
    json_path = write_results_json(all_results, all_metrics, system_availability, traces, eval_duration)
    md_path = write_results_md(all_results, all_metrics, system_availability, traces, eval_duration)

    print("\nResults written to:", file=sys.stderr)
    print(f"  {json_path}", file=sys.stderr)
    print(f"  {md_path}", file=sys.stderr)

    # Print summary to stdout
    if "ccp" in all_metrics and all_metrics["ccp"]:
        ccp_metrics = all_metrics["ccp"]
        overall = ccp_metrics.get("policy_compliance", {}).get("overall", 0.0)
        repro = ccp_metrics.get("reproducibility_variance")
        inj_res = ccp_metrics.get("injection_resistance_pct", 0.0)
        print("\nCCP Results:")
        print(f"  Policy compliance (overall): {overall}%")
        print(f"  Injection resistance:         {inj_res}%")
        print(f"  Reproducibility variance:     {repro}")

    # --- Determine exit code ---
    # Exit 0 only if CCP achieves 100% on all deterministic scenarios
    if "ccp" in all_results:
        ccp_results = all_results["ccp"]
        deterministic = [
            r for r in ccp_results
            if r.category in ("control_command", "policy_gate", "state_transition")
        ]
        if deterministic:
            all_passed = all(r.passed for r in deterministic)
            if not all_passed:
                failed = [r.scenario_id for r in deterministic if not r.passed]
                print(
                    f"\nEXIT 1: CCP failed {len(failed)} deterministic scenario(s): {failed}",
                    file=sys.stderr,
                )
                return 1
            print(
                f"\nEXIT 0: CCP passed all {len(deterministic)} deterministic scenarios.",
                file=sys.stderr,
            )
        else:
            print("\nEXIT 0: No deterministic scenarios run.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
