#!/usr/bin/env python3
"""Tests for retry after second attempt failure in GitHub Actions workflow."""

import os

WORKFLOWS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows"
)
EVOLVE_YML = os.path.join(WORKFLOWS_DIR, "evolve.yml")


def _read_evolve_yml():
    with open(EVOLVE_YML) as f:
        return f.read()


# BDD: Retry after second attempt failure
def test_workflow_has_third_attempt_step():
    """Workflow has a step that runs when both attempt1 and attempt2 fail."""
    content = _read_evolve_yml()
    # Must condition on both previous attempts failing
    assert "attempt2" in content, "Workflow should reference attempt2 outcome"
    assert "attempt1" in content and "attempt2" in content


# BDD: Retry after second attempt failure
def test_workflow_third_attempt_requires_both_failures():
    """Third retry step is only triggered when attempt1 AND attempt2 both fail."""
    content = _read_evolve_yml()
    # The condition must check both attempt1 failure AND attempt2 failure
    assert (
        "attempt1.outcome == 'failure'" in content
        and "attempt2.outcome == 'failure'" in content
    ) or (
        'attempt1.outcome == "failure"' in content
        and 'attempt2.outcome == "failure"' in content
    ), "Third retry should require both attempt1 and attempt2 to have failed"


# BDD: Retry after second attempt failure
def test_workflow_third_attempt_waits_45_minutes():
    """Third retry waits 45 minutes (sleep 2700) before running."""
    content = _read_evolve_yml()
    assert "sleep 2700" in content or "45 min" in content.lower(), (
        "Third retry should wait 45 minutes (sleep 2700)"
    )


# BDD: Retry after second attempt failure
def test_workflow_third_attempt_runs_session():
    """Third retry attempt actually runs bootstrap or evolve."""
    content = _read_evolve_yml()
    # After waiting, it must run a session script
    # Find the third occurrence of bootstrap.sh / evolve.sh after 2700
    sleep_pos = content.find("sleep 2700")
    assert sleep_pos != -1, "sleep 2700 not found"
    after_sleep = content[sleep_pos:]
    assert "bootstrap.sh" in after_sleep or "evolve.sh" in after_sleep, (
        "Third retry should run a session script after the wait"
    )
