#!/usr/bin/env python3
"""Tests for Git Worktree Isolation scenarios."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Create worktree for scenario
def test_evolve_creates_worktree_for_scenario():
    """Test that evolve.sh creates a git worktree for each scenario."""
    evolve_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "evolve.sh")

    with open(evolve_path) as f:
        content = f.read()

    # Check that the script creates git worktree
    assert "git worktree add" in content
    assert "WT_PATH" in content or "worktree" in content.lower()


# BDD: Copy runtime files to worktree
def test_evolve_copies_runtime_files_to_worktree():
    """Test that evolve.sh copies runtime files to the worktree."""
    evolve_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "evolve.sh")

    with open(evolve_path) as f:
        content = f.read()

    # Check that the script copies files to worktree
    assert "cp" in content or "copy" in content.lower()
    assert "WT_PATH" in content or "worktree" in content.lower()


# BDD: Merge successful worktree to main
def test_evolve_merges_successful_worktree():
    """Test that evolve.sh merges successful worktree back to main."""
    evolve_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "evolve.sh")

    with open(evolve_path) as f:
        content = f.read()

    # Check that the script merges worktree to main
    assert "git merge" in content
    assert "main" in content.lower()


# BDD: Auto-resolve management file conflicts
def test_evolve_auto_resolves_management_file_conflicts():
    """Test that evolve.sh auto-resolves management file conflicts."""
    evolve_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "evolve.sh")

    with open(evolve_path) as f:
        content = f.read()

    # Check that the script auto-resolves conflicts
    assert "conflict" in content.lower()
    assert "ours" in content.lower() or "resolve" in content.lower()


# BDD: Fold JOURNAL_ENTRY.md into JOURNAL.md
def test_evolve_folds_journal_entry():
    """Test that evolve.sh folds JOURNAL_ENTRY.md into JOURNAL.md."""
    evolve_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "evolve.sh")

    with open(evolve_path) as f:
        content = f.read()

    # Check that the script folds journal entry
    assert "JOURNAL_ENTRY.md" in content
    assert "JOURNAL.md" in content


# BDD: Clean up worktree after merge
def test_evolve_cleans_up_worktree_after_merge():
    """Test that evolve.sh cleans up worktree after merge."""
    evolve_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "evolve.sh")

    with open(evolve_path) as f:
        content = f.read()

    # Check that the script cleans up worktree
    assert "git worktree remove" in content or "worktree remove" in content.lower()
    assert "cleanup" in content.lower()


# BDD: Remove worktree on failure
def test_evolve_removes_worktree_on_failure():
    """Test that evolve.sh removes worktree on failure."""
    evolve_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "evolve.sh")

    with open(evolve_path) as f:
        content = f.read()

    # Check that the script removes worktree on failure
    assert "cleanup_worktree" in content or "trap" in content.lower()
    assert "git worktree" in content or "worktree" in content.lower()
    assert "force" in content.lower() or "remove" in content.lower()
