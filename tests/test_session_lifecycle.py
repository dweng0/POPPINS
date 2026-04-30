import pytest
import os
import json
from scripts.session_lifecycle import append_session_event

# BDD: Worktree Session Lifecycle

def test_evolve_appends_session_start_to_sessions_jsonl_when_worktree_is_created():
    sessions_path = "/tmp/test_sessions_start.jsonl"
    if os.path.exists(sessions_path):
        os.remove(sessions_path)
    
    event = {
        "type": "session_start",
        "ts": 123456789.0,
        "provider": "anthropic",
        "model": "claude-3-haiku"
    }
    
    append_session_event(sessions_path, event)
    
    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)
        
    assert data["type"] == "session_start"
    assert data["provider"] == "anthropic"
    
    os.remove(sessions_path)

def test_evolve_appends_session_end_to_sessions_jsonl_on_normal_completion():
    sessions_path = "/tmp/test_sessions_end_normal.jsonl"
    if os.path.exists(sessions_path):
        os.remove(sessions_path)
    
    event = {
        "type": "session_end",
        "ts": 123456790.0,
        "status": "success"
    }
    
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
    
    event = {
        "type": "session_end",
        "ts": 123456790.0,
        "status": "failed"
    }
    
    append_session_event(sessions_path, event)
    
    with open(sessions_path, "r") as f:
        line = f.readline()
        data = json.loads(line)
        
    assert data["type"] == "session_end"
    assert data["status"] == "failed"
    
    os.remove(sessions_path)
