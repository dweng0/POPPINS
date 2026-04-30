#!/usr/bin/env python3
"""Tests for git bot identity configuration in GitHub Actions workflow."""

import os

WORKFLOWS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows"
)
EVOLVE_YML = os.path.join(WORKFLOWS_DIR, "evolve.yml")


def _read_evolve_yml():
    with open(EVOLVE_YML) as f:
        return f.read()


# BDD: Configure git bot identity
def test_git_bot_name_is_baadd_agent():
    """Workflow sets git user.name to baadd-agent[bot]."""
    content = _read_evolve_yml()
    assert 'git config user.name "baadd-agent[bot]"' in content


# BDD: Configure git bot identity
def test_git_bot_email_is_noreply_address():
    """Workflow sets git user.email to baadd-agent[bot]@users.noreply.github.com."""
    content = _read_evolve_yml()
    assert (
        'git config user.email "baadd-agent[bot]@users.noreply.github.com"' in content
    )
