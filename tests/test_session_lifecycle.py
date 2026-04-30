"""Tests for scripts/session_lifecycle.py — session lifecycle management."""

import json
import os
import tempfile

from scripts.session_lifecycle import append_session_event


# BDD: sessions.jsonl is created if it does not exist
def test_sessions_jsonl_is_created_if_it_does_not_exist():
    """Append a session event to a sessions.jsonl file that does not yet exist.

    The file should be created automatically by Python's open(..., 'a') mode,
    and the event dict should be written as a single JSON line.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        sessions_path = os.path.join(tmpdir, "sessions.jsonl")

        # Precondition: file does not exist
        assert not os.path.exists(sessions_path), "sessions.jsonl should not exist yet"

        # Action: append a session event
        event = {
            "type": "session_start",
            "scenario": "test",
            "pid": 1,
            "wt_path": "/tmp/fake",
            "ts": 1700000000.0,
        }

        # No exception should be raised
        append_session_event(sessions_path, event)

        # Assertion 1: file now exists
        assert os.path.exists(sessions_path), "sessions.jsonl should have been created"

        # Assertion 2: file contains exactly one line
        with open(sessions_path, "r") as f:
            lines = f.readlines()
        assert len(lines) == 1, f"Expected 1 line, got {len(lines)}"

        # Assertion 3: that line is valid JSON matching the event dict
        parsed = json.loads(lines[0].strip())
        assert parsed == event, f"Expected {event}, got {parsed}"
