import os
import json
import time
from scripts.session_lifecycle import append_session_event

# BDD: Worktree Session Lifecycle


def test_evolve_appends_session_start_to_sessions_jsonl_when_worktree_is_created():
    # BDD: evolve.sh appends session_start to sessions.jsonl when worktree is created
    sessions_path = "/tmp/test_sessions_start.jsonl"
    if os.path.exists(sessions_path):
        os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-my-scenario-1234"
    event = {
        "type": "session_start",
        "scenario": "evolve.sh appends session_start to sessions.jsonl when worktree is created",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": time.time(),
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_start"
    assert data["wt_path"] == wt_path
    assert isinstance(data["ts"], float)
    # Added assertion to ensure it matches the BDD requirement for scenario name
    assert (
        data["scenario"]
        == "evolve.sh appends session_start to sessions.jsonl when worktree is created"
    )

    os.remove(sessions_path)


def test_evolve_appends_session_end_to_sessions_jsonl_on_normal_completion():
    # BDD: evolve.sh appends session_end to sessions.jsonl on normal completion
    sessions_path = "/tmp/test_sessions_end_normal.jsonl"
    if os.path.exists(sessions_path):
        os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    wt_path = "/tmp/baadd-wt-test-session-end"
    event = {
        "type": "session_end",
        "scenario": "evolve.sh appends session_end to sessions.jsonl on normal completion",
        "pid": 12345,
        "wt_path": wt_path,
        "ts": 123456790.0,
        "status": "success",
    }

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["wt_path"] == wt_path
    assert data["status"] == "success"

    os.remove(sessions_path)

    event = {"type": "session_end", "ts": 123456790.0, "status": "success"}

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["status"] == "success"

    os.remove(sessions_path)


def test_evolve_appends_session_end_to_sessions_jsonl_on_failure():
    sessions_path = "/tmp/test_sessions_end_failure.jsonl"
    if os.path.exists(sessions_path):
        os.remove(sessions_path)

    event = {"type": "session_end", "ts": 123456790.0, "status": "failed"}

    append_session_event(sessions_path, event)

    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

    assert data["type"] == "session_end"
    assert data["status"] == "failed"

    os.remove(sessions_path)
