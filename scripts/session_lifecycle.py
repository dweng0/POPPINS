"""Session lifecycle management for worktree agents.

Provides functions to record and read session events from a sessions.jsonl file.
"""

import json


def append_session_event(sessions_path: str, event: dict) -> None:
    """Append a single JSON line (event) to the sessions.jsonl file.

    If the file does not exist, it is created automatically by open(..., 'a').

    Args:
        sessions_path: Path to the sessions.jsonl file.
        event: Dictionary to serialize as a JSON line.
    """
    with open(sessions_path, "a") as f:
        f.write(json.dumps(event) + "\n")
