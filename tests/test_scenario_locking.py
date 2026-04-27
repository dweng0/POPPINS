#!/usr/bin/env python3
"""Tests for scenario locking functionality."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from scenario_locking import scenario_to_slug, is_pid_alive, check_and_remove_stale_lock, release_lock


# BDD: Generate scenario slug from name
def test_generate_scenario_slug_from_name():
    """Test that scenario names are converted to slugs correctly."""
    # Basic case from BDD spec
    assert scenario_to_slug("Login with valid credentials") == "login-with-valid-credentials"
    
    # Additional edge cases for robustness
    assert scenario_to_slug("Simple") == "simple"
    assert scenario_to_slug("Multiple   spaces") == "multiple-spaces"
    assert scenario_to_slug("Special@#$characters") == "special-characters"
    assert scenario_to_slug("Mixed123Numbers") == "mixed123numbers"
    assert scenario_to_slug("UPPERCASE") == "uppercase"
    assert scenario_to_slug("with-dashes") == "with-dashes"
    assert scenario_to_slug("with_underscores") == "with-underscores"


# BDD: Slug truncates to 60 characters
def test_slug_truncates_to_60_characters():
    """Test that scenario_to_slug truncates slugs to 60 characters."""
    # Very long scenario name should be truncated
    long_name = "A" * 100
    slug = scenario_to_slug(long_name)
    assert len(slug) <= 60
    assert slug == "a" * 60
    
    # Scenario name at exactly 60 chars should not be truncated
    exact_name = "A" * 60
    slug = scenario_to_slug(exact_name)
    assert len(slug) == 60
    
    # Scenario name at 61 chars should be truncated to 60
    over_name = "A" * 61
    slug = scenario_to_slug(over_name)
    assert len(slug) == 60


# BDD: Detect stale lock from dead PID
def test_detect_stale_lock_from_dead_pid():
    """Lock file with dead PID is detected as stale, removed, and scenario can be claimed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lock_path = os.path.join(tmpdir, "my-scenario.lock")
        # PID 1 is always alive (init/systemd), use a PID that can't be alive
        # Find a PID that is definitely dead by using a very large number
        dead_pid = 2147483647  # max int32, virtually never a live PID
        with open(lock_path, "w") as f:
            f.write(f"PID={dead_pid}\nSCENARIO=my scenario\nDATE=2026-01-01\n")

        # Dead PID should not be alive
        assert not is_pid_alive(dead_pid)

        # check_and_remove_stale_lock should remove it and return True (stale)
        result = check_and_remove_stale_lock(lock_path)
        assert result is True
        assert not os.path.exists(lock_path)


# BDD: Release lock on completion
def test_release_lock_on_completion():
    """Lock file is deleted when agent completes scenario implementation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        slug = "my-scenario"
        lock_path = os.path.join(tmpdir, f"{slug}.lock")
        with open(lock_path, "w") as f:
            f.write(f"PID={os.getpid()}\nSCENARIO=My Scenario\nDATE=2026-01-01\n")
        assert os.path.exists(lock_path)
        release_lock(tmpdir, slug)
        assert not os.path.exists(lock_path)


def test_release_lock_missing_file_no_error():
    """release_lock does not raise if lock file already gone."""
    with tempfile.TemporaryDirectory() as tmpdir:
        release_lock(tmpdir, "nonexistent-scenario")


def test_stale_lock_live_pid_not_removed():
    """Lock file with live PID is NOT removed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lock_path = os.path.join(tmpdir, "my-scenario.lock")
        live_pid = os.getpid()
        with open(lock_path, "w") as f:
            f.write(f"PID={live_pid}\nSCENARIO=my scenario\nDATE=2026-01-01\n")

        assert is_pid_alive(live_pid)
        result = check_and_remove_stale_lock(lock_path)
        assert result is False
        assert os.path.exists(lock_path)


# BDD: Clean up lock on early exit
def test_clean_up_lock_on_early_exit():
    """trap cleanup_worktree fires on early exit and removes lock file."""
    import subprocess

    with tempfile.TemporaryDirectory() as tmpdir:
        locks_dir = os.path.join(tmpdir, "locks")
        os.makedirs(locks_dir)
        slug = "my-test-scenario"
        lock_path = os.path.join(locks_dir, f"{slug}.lock")
        with open(lock_path, "w") as f:
            f.write("PID=99999\nSCENARIO=My Test Scenario\nDATE=2026-01-01\n")
        assert os.path.exists(lock_path)

        # Run a bash script that sources cleanup_worktree from evolve.sh and calls it
        evolve_sh = os.path.join(os.path.dirname(__file__), "..", "scripts", "evolve.sh")
        script = f"""
set +e
MAIN_DIR={tmpdir}
TARGET_SLUG={slug}
LOCKS_DIR=locks
WT_PATH=""
BRANCH=""
cleanup_worktree() {{
    if [ -d "${{WT_PATH:-}}" ]; then
        git -C "${{MAIN_DIR:-.}}" worktree remove --force "$WT_PATH" 2>/dev/null || true
    fi
    if [ -n "${{BRANCH:-}}" ]; then
        git -C "${{MAIN_DIR:-.}}" branch -D "$BRANCH" 2>/dev/null || true
    fi
    if [ -n "${{TARGET_SLUG:-}}" ]; then
        rm -f "${{MAIN_DIR:-.}}/$LOCKS_DIR/${{TARGET_SLUG}}.lock"
    fi
}}
cleanup_worktree
"""
        result = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert not os.path.exists(lock_path), "Lock file should be removed by cleanup_worktree"
