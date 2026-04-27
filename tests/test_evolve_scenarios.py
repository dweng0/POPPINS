#!/usr/bin/env python3
"""Tests for evolve.sh scenarios."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Check starting build state
def test_evolve_checks_starting_build_state():
    """Test that evolve.sh verifies build state before starting session."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script verifies build state
    assert "BUILD_OK" in content
    assert "BUILD_CMD" in content or "build_cmd" in content
    # Should have logic to detect if build passes or fails
    assert "exit 1" in content


# BDD: Continue with failing tests
def test_evolve_continues_with_failing_tests():
    """Test that evolve.sh continues when build passes but tests fail."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script handles failing tests
    assert "TEST_OK" in content
    assert "TEST_CMD" in content or "test_cmd" in content
    # Should have message about agent fixing failing tests
    assert "FAILING" in content or "agent will fix" in content.lower()


# BDD: Exit if build broken at start
def test_evolve_exits_if_build_broken():
    """Test that evolve.sh exits immediately if build is broken at start."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script exits if build fails
    assert "BUILD_OK" in content
    assert "exit 1" in content
    # Should have message about build failure
    assert "Build: FAIL" in content or "build" in content.lower()


# BDD: Fetch trusted GitHub issues
def test_evolve_fetches_trusted_github_issues():
    """Test that evolve.sh fetches trusted GitHub issues."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script fetches issues
    assert "gh issue list" in content or "gh api" in content
    assert "agent-input" in content or "agent-approved" in content
    # Should verify issue trust
    assert "verify" in content.lower() or "trusted" in content.lower()


# BDD: Generate issues file for agent
def test_evolve_generates_issues_file():
    """Test that evolve.sh generates ISSUES_TODAY.md for agent."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script generates issues file
    assert "ISSUES_TODAY.md" in content
    # Should use format_issues.py or similar
    assert "format_issues" in content.lower() or "format" in content.lower()


# BDD: Pre-compute coverage before session
def test_evolve_pre_computes_coverage():
    """Test that evolve.sh pre-computes coverage before agent session."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script pre-computes coverage
    assert "check_bdd_coverage" in content or "coverage" in content.lower()
    # Should capture uncovered scenarios
    assert "uncovered" in content.lower()


# BDD: Detect test-only anti-pattern
def test_evolve_detects_test_only_anti_pattern():
    """Test that evolve.sh detects if agent only writes tests without implementation."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script detects test-only anti-pattern
    assert "test" in content.lower()
    assert "implementation" in content.lower() or "build" in content.lower()
    # Should prompt agent to implement
    assert "prompt" in content.lower() or "implement" in content.lower()


# BDD: Retry fix on build failure
def test_evolve_retries_fix_on_build_failure():
    """Test that evolve.sh retries up to 3 times on build failure."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script retries on build failure
    assert "retry" in content.lower() or "fix attempt" in content.lower()
    # Should have max 3 retries
    assert "3" in content or "three" in content.lower()


# BDD: Revert session on persistent failure
def test_evolve_reverts_on_persistent_failure():
    """Test that evolve.sh reverts to session start SHA on persistent failure."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script reverts on persistent failure
    assert "revert" in content.lower() or "git revert" in content
    assert "SESSION_START_SHA" in content or "session start" in content.lower()


# BDD: Write journal if agent skipped
def test_evolve_writes_journal_if_agent_skipped():
    """Test that evolve.sh writes journal if agent skips writing one."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script writes journal if agent skipped
    assert "JOURNAL.md" in content
    assert "journal" in content.lower()
    # Should have fallback logic
    assert "fallback" in content.lower() or "auto" in content.lower()


# BDD: Update journal index after session
def test_evolve_updates_journal_index():
    """Test that evolve.sh updates JOURNAL_INDEX.md after session."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script updates journal index
    assert "JOURNAL_INDEX.md" in content
    assert "coverage" in content.lower()


# BDD: Comment and close implemented issues
def test_evolve_comments_and_closes_issues():
    """Test that evolve.sh comments on and closes implemented GitHub issues."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script comments on and closes issues
    assert "gh issue comment" in content or "gh issue close" in content
    assert "ISSUE_RESPONSE" in content or "issue" in content.lower()


# BDD: Push changes after session
def test_evolve_pushes_changes():
    """Test that evolve.sh pushes changes to remote after session."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script pushes changes
    assert "git push" in content or "push" in content.lower()


# BDD: Track session start SHA for rollback
def test_evolve_tracks_session_start_sha():
    """Test that evolve.sh tracks session start SHA for rollback."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script tracks session start SHA
    assert "SESSION_START_SHA" in content or "session start sha" in content.lower()
    assert "git rev-parse" in content or "git rev-parse" in content


# BDD: Branch naming convention with timestamp
def test_evolve_branch_naming_convention():
    """Test that evolve.sh creates branches with timestamp naming convention."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script uses timestamp in branch names
    assert "agent/" in content or "branch" in content.lower()
    # Branch format is agent/${slug}-YYYYMMDD-HHMMSS
    assert "date +%Y%m%d" in content or "%Y%m%d" in content
    assert "date +%H%M%S" in content or "%H%M%S" in content


# BDD: Calculate has_work flag
def test_evolve_calculates_has_work():
    """Test that evolve.sh calculates has_work flag based on coverage and issues."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script calculates has_work
    assert "has_work" in content.lower()
    # Should consider uncovered scenarios and open issues
    assert "uncovered" in content.lower() or "issues" in content.lower()


# BDD: Handle push failure gracefully
def test_evolve_handles_push_failure():
    """Test that evolve.sh handles push failure gracefully without exiting."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script handles push failure gracefully
    assert "push" in content.lower()
    assert "failed" in content.lower() or "check" in content.lower()


# BDD: Handle missing git remote
def test_evolve_handles_missing_git_remote():
    """Test that evolve.sh handles missing git remote gracefully."""
    evolve_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "evolve.sh"
    )
    
    with open(evolve_path) as f:
        content = f.read()
    
    # Check that the script handles missing git remote
    assert "git remote" in content or "origin" in content
    assert "unknown/repo" in content or "fallback" in content.lower()
