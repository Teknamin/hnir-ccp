"""Structured decision logging with reason codes for every CCP decision."""

from pathlib import Path
from typing import List, Optional, Union

from ccp.models import AuditEntry, AuditLevel


class AuditLogger:
    """Appends structured JSON audit entries to a JSONL file and keeps in-memory list."""

    def __init__(self, log_path: Union[str, Path, None] = None):
        self._entries: List[AuditEntry] = []
        self._log_path: Optional[Path] = Path(log_path) if log_path else None
        if self._log_path:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        request_id: str,
        layer: str,
        event: str,
        reason_code: str = "",
        level: AuditLevel = AuditLevel.INFO,
        **details,
    ) -> AuditEntry:
        """Create and store an audit entry."""
        entry = AuditEntry(
            request_id=request_id,
            layer=layer,
            level=level,
            event=event,
            reason_code=reason_code,
            details=details,
        )
        self._entries.append(entry)
        if self._log_path:
            with open(self._log_path, "a") as f:
                f.write(entry.model_dump_json() + "\n")
        return entry

    @property
    def entries(self) -> List[AuditEntry]:
        """Return all in-memory audit entries."""
        return list(self._entries)

    def entries_for_request(self, request_id: str) -> List[AuditEntry]:
        """Return entries for a specific request."""
        return [e for e in self._entries if e.request_id == request_id]

    def clear(self) -> None:
        """Clear in-memory entries."""
        self._entries.clear()
