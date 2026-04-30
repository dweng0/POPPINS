---
language: python
framework: none
build_cmd: python3 -m py_compile scripts/*.py && echo "Build OK"
test_cmd: python3 -m pytest tests/ -q --tb=short --no-header 2>/dev/null || python3 tests/run_tests.py
lint_cmd: python3 -m ruff check scripts/ tests/ --fix || echo "lint skipped"
fmt_cmd: python3 -m ruff format scripts/ tests/ || echo "format skipped"
birth_date: 2026-03-05
---

    Feature: Worktree Session Lifecycle
        As a developer running evolve.sh or orchestrate.py
        I want sessions to register start and end events in a central log
        So that the dashboard can distinguish live agents from orphaned or completed worktrees

        evolve.sh and orchestrate.py append JSON lines to sessions.jsonl in the main repo root.
        Each line is {"type": "session_start"|"session_end", "scenario": "...", "pid": 12345,
        "wt_path": "/tmp/baadd-wt-...", "ts": 1700000000.0}.
        The dashboard reads sessions.jsonl to determine which worktrees are truly active.
        A worktree is ACTIVE if it has a session_start with no matching session_end
        (matched by wt_path) AND the session_start is less than SESSION_TIMEOUT seconds old (default 3600).
        A worktree is STALE if session_start is present but no session_end AND age > SESSION_TIMEOUT.
        A worktree is DONE if session_end is present.


        Scenario: orchestrate.py appends session_end for each worker when it finishes
            Given orchestrate.py has spawned 3 workers and they all complete
            When the last worker exits
            Then sessions.jsonl contains 3 session_end lines matching the 3 wt_paths

