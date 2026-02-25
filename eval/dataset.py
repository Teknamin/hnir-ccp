"""Load and validate JSONL trace datasets for the evaluation harness."""

import json
from pathlib import Path
from typing import List, Optional

from eval.schema import TraceEntry


TRACES_DIR = Path(__file__).parent / "traces"

_TRACE_FILES = [
    TRACES_DIR / "control.jsonl",
    TRACES_DIR / "state.jsonl",
    TRACES_DIR / "policy.jsonl",
    TRACES_DIR / "adversarial.jsonl",
]


def load_traces(
    extra_file: Optional[Path] = None,
    category: Optional[str] = None,
) -> List[TraceEntry]:
    """Load and validate all committed JSONL trace files.

    Args:
        extra_file: Optional additional JSONL file to merge (e.g. garak output).
        category: Optional category filter ("control_command", "policy_gate",
                  "state_transition", "adversarial").

    Returns:
        List of validated TraceEntry objects.

    Raises:
        ValueError: If any scenario_id is duplicated or a record fails validation.
        FileNotFoundError: If a committed trace file is missing.
    """
    files = list(_TRACE_FILES)
    if extra_file is not None:
        files.append(extra_file)

    entries: List[TraceEntry] = []
    seen_ids: set = set()
    errors: List[str] = []

    for path in files:
        if not path.exists():
            raise FileNotFoundError(f"Trace file not found: {path}")

        with open(path) as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                    entry = TraceEntry.model_validate(raw)
                except Exception as exc:
                    errors.append(f"{path.name}:{lineno}: {exc}")
                    continue

                if entry.scenario_id in seen_ids:
                    errors.append(
                        f"{path.name}:{lineno}: duplicate scenario_id '{entry.scenario_id}'"
                    )
                    continue

                seen_ids.add(entry.scenario_id)
                entries.append(entry)

    if errors:
        raise ValueError(
            f"Trace validation failed with {len(errors)} error(s):\n"
            + "\n".join(errors)
        )

    if category is not None:
        entries = [e for e in entries if e.category == category]

    return entries


def validate_only(extra_file: Optional[Path] = None) -> dict:
    """Validate all traces without running them. Returns a summary dict."""
    entries = load_traces(extra_file=extra_file)
    categories: dict = {}
    for e in entries:
        categories[e.category] = categories.get(e.category, 0) + 1
    return {
        "total": len(entries),
        "categories": categories,
        "scenario_ids": [e.scenario_id for e in entries],
    }
