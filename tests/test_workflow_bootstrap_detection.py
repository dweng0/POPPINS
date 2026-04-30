#!/usr/bin/env python3
"""Tests for bootstrap detection in GitHub Actions workflow."""

import os

WORKFLOWS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows"
)
EVOLVE_YML = os.path.join(WORKFLOWS_DIR, "evolve.yml")


def _read_evolve_yml():
    with open(EVOLVE_YML) as f:
        return f.read()


# BDD: Bootstrap detection in workflow
def test_workflow_checks_baadd_initialized_file():
    """Workflow checks for .baadd_initialized before deciding which script to run."""
    content = _read_evolve_yml()
    assert ".baadd_initialized" in content


# BDD: Bootstrap detection in workflow
def test_workflow_runs_bootstrap_when_marker_missing():
    """When .baadd_initialized is absent, workflow runs bootstrap.sh."""
    content = _read_evolve_yml()
    # The conditional must check absence of marker and call bootstrap.sh
    assert "bootstrap.sh" in content
    assert "! -f .baadd_initialized" in content or "not exist" in content.lower()


# BDD: Bootstrap detection in workflow
def test_workflow_runs_evolve_when_marker_present():
    """When .baadd_initialized is present, workflow runs evolve.sh."""
    content = _read_evolve_yml()
    assert "evolve.sh" in content


# BDD: Bootstrap detection in workflow
def test_workflow_bootstrap_branch_before_evolve_branch():
    """bootstrap.sh branch appears before evolve.sh in the conditional."""
    content = _read_evolve_yml()
    bootstrap_pos = content.find("bootstrap.sh")
    evolve_pos = content.find("evolve.sh")
    assert bootstrap_pos < evolve_pos, (
        "bootstrap.sh should appear before evolve.sh in the conditional block"
    )
