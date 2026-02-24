"""Request trace assembly — constructs full audit traces for CCP decisions."""

from typing import Dict, List

from ccp.models import AuditEntry


class RequestTrace:
    """Groups AuditEntry records by request_id for trace assembly."""

    def __init__(self, entries: List[AuditEntry]):
        self._by_request: Dict[str, List[AuditEntry]] = {}
        for entry in entries:
            self._by_request.setdefault(entry.request_id, []).append(entry)

    def get_trace(self, request_id: str) -> List[AuditEntry]:
        """Get all entries for a request_id, ordered by timestamp."""
        entries = self._by_request.get(request_id, [])
        return sorted(entries, key=lambda e: e.timestamp)

    def all_request_ids(self) -> List[str]:
        """Return all known request IDs."""
        return list(self._by_request.keys())

    def summary(self, request_id: str) -> Dict:
        """Return a summary dict for a request trace."""
        entries = self.get_trace(request_id)
        if not entries:
            return {"request_id": request_id, "entries": 0}
        return {
            "request_id": request_id,
            "entries": len(entries),
            "layers": list(dict.fromkeys(e.layer for e in entries)),
            "levels": list(dict.fromkeys(e.level.value for e in entries)),
            "reason_codes": [e.reason_code for e in entries if e.reason_code],
        }
