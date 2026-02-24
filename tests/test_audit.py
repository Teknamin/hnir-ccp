"""Tests for ccp.audit."""

import json
import tempfile
from pathlib import Path

from ccp.audit.logger import AuditLogger
from ccp.audit.trace import RequestTrace
from ccp.models import AuditLevel


class TestAuditLogger:
    def test_log_in_memory(self):
        logger = AuditLogger()
        logger.log("req-1", "control", "test event")
        assert len(logger.entries) == 1
        assert logger.entries[0].request_id == "req-1"

    def test_log_to_file(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            path = f.name
        try:
            logger = AuditLogger(log_path=path)
            logger.log("req-1", "control", "event1", level=AuditLevel.INFO)
            logger.log("req-2", "policy", "event2", level=AuditLevel.DENY)

            lines = Path(path).read_text().strip().split("\n")
            assert len(lines) == 2
            data = json.loads(lines[0])
            assert data["request_id"] == "req-1"
            assert data["layer"] == "control"
        finally:
            Path(path).unlink(missing_ok=True)

    def test_entries_for_request(self):
        logger = AuditLogger()
        logger.log("req-1", "control", "event1")
        logger.log("req-2", "policy", "event2")
        logger.log("req-1", "state", "event3")
        entries = logger.entries_for_request("req-1")
        assert len(entries) == 2

    def test_clear(self):
        logger = AuditLogger()
        logger.log("req-1", "control", "event")
        logger.clear()
        assert len(logger.entries) == 0


class TestRequestTrace:
    def test_get_trace(self):
        logger = AuditLogger()
        logger.log("req-1", "control", "event1")
        logger.log("req-1", "state", "event2")
        logger.log("req-2", "policy", "event3")

        trace = RequestTrace(logger.entries)
        entries = trace.get_trace("req-1")
        assert len(entries) == 2

    def test_all_request_ids(self):
        logger = AuditLogger()
        logger.log("req-1", "control", "event1")
        logger.log("req-2", "policy", "event2")
        trace = RequestTrace(logger.entries)
        ids = trace.all_request_ids()
        assert "req-1" in ids
        assert "req-2" in ids

    def test_summary(self):
        logger = AuditLogger()
        logger.log("req-1", "control", "event1", reason_code="CODE_1")
        logger.log("req-1", "policy", "event2", reason_code="CODE_2", level=AuditLevel.DENY)
        trace = RequestTrace(logger.entries)
        s = trace.summary("req-1")
        assert s["entries"] == 2
        assert "control" in s["layers"]
        assert "CODE_1" in s["reason_codes"]

    def test_summary_empty(self):
        trace = RequestTrace([])
        s = trace.summary("nonexistent")
        assert s["entries"] == 0
