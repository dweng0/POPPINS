#!/usr/bin/env python3
"""Scenario locking utilities for parallel agent execution."""

import os
import re


def scenario_to_slug(scenario_name: str) -> str:
    """Convert a scenario name to a URL-safe slug.

    Args:
        scenario_name: The scenario name (e.g., "Login with valid credentials")

    Returns:
        A lowercase slug with alphanumeric characters and hyphens only,
        truncated to 60 characters (e.g., "login-with-valid-credentials")
    """
    # Convert to lowercase
    slug = scenario_name.lower()

    # Replace any non-alphanumeric character (except hyphens) with a hyphen
    slug = re.sub(r"[^a-z0-9-]", "-", slug)

    # Replace multiple consecutive hyphens with a single hyphen
    slug = re.sub(r"-+", "-", slug)

    # Strip leading and trailing hyphens
    slug = slug.strip("-")

    # Truncate to 60 characters
    slug = slug[:60]

    return slug


def is_pid_alive(pid: int) -> bool:
    """Return True if a process with the given PID is currently running."""
    try:
        return os.path.exists(f"/proc/{pid}")
    except (ValueError, TypeError):
        return False


def check_and_remove_stale_lock(lock_path: str) -> bool:
    """Check if a lock file is stale (dead PID) and remove it if so.

    Returns True if the lock was stale and removed, False if the lock is live.
    """
    try:
        with open(lock_path) as f:
            content = f.read()
    except OSError:
        return True

    pid = None
    for line in content.splitlines():
        if line.startswith("PID="):
            try:
                pid = int(line.split("=", 1)[1].strip())
            except (ValueError, IndexError):
                pass
            break

    if pid is None or not is_pid_alive(pid):
        try:
            os.remove(lock_path)
        except OSError:
            pass
        return True

    return False


def release_lock(locks_dir: str, slug: str) -> None:
    """Delete the lock file for the given slug, if it exists."""
    lock_path = os.path.join(locks_dir, f"{slug}.lock")
    try:
        os.remove(lock_path)
    except OSError:
        pass
