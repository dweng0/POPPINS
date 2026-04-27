#!/usr/bin/env python3
"""Tests for setup_env.sh scenarios."""

import os


# BDD: Setup Python dependencies
def test_setup_python_dependencies():
    """Test that setup_env.sh installs Python dependencies from requirements.txt."""
    setup_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "setup_env.sh"
    )

    with open(setup_path) as f:
        content = f.read()

    # Check that the script contains a python) case in the case statement
    assert "python)" in content, "Missing python) case in setup_env.sh"

    # Check that the Python case contains a requirements.txt existence check
    assert "[ -f requirements.txt ]" in content, (
        "Missing [ -f requirements.txt ] guard in Python case"
    )

    # Check that the Python case contains the pip install command
    assert "pip install -r requirements.txt" in content, (
        "Missing pip install -r requirements.txt in Python case"
    )
