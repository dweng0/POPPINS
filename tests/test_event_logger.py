import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath("scripts"))
from agent import EventLogger


def _read_events(path):
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


# BDD: Log session start with provider and model
def test_log_session_start_with_provider_and_model():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = f.name
    try:
        logger = EventLogger(path)
        logger.session_start("anthropic", "claude-haiku", "evolve")
        events = _read_events(path)
        assert len(events) == 1
        e = events[0]
        assert e["event"] == "session_start"
        assert e["provider"] == "anthropic"
        assert e["model"] == "claude-haiku"
    finally:
        os.unlink(path)


# BDD: Log tool call with input preview
def test_log_tool_call_with_input_preview():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = f.name
    try:
        logger = EventLogger(path)
        long_cmd = "git status " + "x" * 300
        logger.tool_call("bash", {"command": long_cmd}, iteration=1)
        events = _read_events(path)
        e = events[0]
        assert e["event"] == "tool_call"
        assert e["tool"] == "bash"
        assert len(e["input"]["command"]) <= 200
    finally:
        os.unlink(path)


# BDD: Log tool result with duration
def test_log_tool_result_with_duration():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = f.name
    try:
        logger = EventLogger(path)
        logger.tool_result("bash", "output", duration_ms=1500, iteration=1)
        events = _read_events(path)
        e = events[0]
        assert e["event"] == "tool_result"
        assert e["duration_ms"] == 1500
    finally:
        os.unlink(path)


# BDD: Log token usage per API response
def test_log_token_usage_per_api_response():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = f.name
    try:
        logger = EventLogger(path)
        logger.api_response(500, 200, iteration=1)
        events = _read_events(path)
        e = events[0]
        assert e["event"] == "api_response"
        assert e["input_tokens"] == 500
        assert e["output_tokens"] == 200
        assert e["cumulative_input_tokens"] == 500
        assert e["cumulative_output_tokens"] == 200
    finally:
        os.unlink(path)


# BDD: Log session end with reason
def test_log_session_end_with_reason():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = f.name
    try:
        logger = EventLogger(path)
        logger.api_response(100, 50, iteration=1)
        logger.session_end(iterations_used=50, reason="end_turn")
        events = _read_events(path)
        end_event = next(e for e in events if e["event"] == "session_end")
        assert end_event["reason"] == "end_turn"
        assert end_event["iterations_used"] == 50
        assert end_event["total_input_tokens"] == 100
        assert end_event["total_output_tokens"] == 50
    finally:
        os.unlink(path)
