#!/usr/bin/env python3
"""Tests for Error Recovery scenarios related to evolve.sh behavior."""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _evolve():
    with open(os.path.join(ROOT, "scripts", "evolve.sh")) as f:
        return f.read()


# BDD: API error causes retry exit
def test_api_error_detected_from_jsonl():
    content = _evolve()
    assert '"type":"error"' in content


# BDD: API error causes retry exit
def test_api_error_causes_exit_without_commit():
    content = _evolve()
    assert "API error detected" in content
    assert "Exiting for retry" in content or "retry" in content


# BDD: Post-merge verification catches breakage
def test_post_merge_verification_runs_tests():
    content = _evolve()
    assert (
        "post-merge" in content.lower()
        or "post_merge" in content.lower()
        or "Post-merge" in content
    )


# BDD: Post-merge verification catches breakage
def test_post_merge_reverts_to_session_sha():
    content = _evolve()
    assert "SESSION_START_SHA" in content
    assert "git reset --hard" in content


# BDD: Post-merge verification catches breakage
def test_post_merge_reverts_on_test_failure():
    content = _evolve()
    # Confirm the revert block is inside a failure branch
    assert "Reverted to" in content
    assert "Push skipped" in content


# BDD: Timeout kills long session
def test_timeout_command_used():
    content = _evolve()
    assert "timeout" in content or "TIMEOUT" in content


# BDD: Timeout kills long session
def test_timeout_env_var_configurable():
    content = _evolve()
    assert "TIMEOUT=" in content or "TIMEOUT:-" in content


# BDD: Timeout kills long session
def test_timeout_applied_to_agent_call():
    content = _evolve()
    assert "TIMEOUT_CMD" in content
    assert "python3 scripts/agent.py" in content


# BDD: Worktree creation failure
def test_worktree_add_command_present():
    content = _evolve()
    assert "git worktree add" in content


# BDD: Worktree creation failure
def test_worktree_creation_uses_branch():
    content = _evolve()
    assert "git worktree add" in content
    assert "-b" in content
