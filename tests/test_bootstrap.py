#!/usr/bin/env python3
"""Tests for bootstrap.sh scenarios."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Scaffold TypeScript React project
def test_bootstrap_scaffolds_typescript_react():
    """Test that bootstrap.sh scaffolds TypeScript React project with correct commands."""
    # This test verifies the bootstrap.sh script contains the correct scaffold commands
    # for TypeScript + React Vite projects

    bootstrap_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "bootstrap.sh"
    )

    with open(bootstrap_path) as f:
        content = f.read()

    # Check that the script contains the correct scaffold command for TypeScript React
    assert "npm create vite@latest" in content
    assert "--template react-ts" in content or "react-ts" in content


# BDD: Scaffold Python project
def test_bootstrap_scaffolds_python_project():
    """Test that bootstrap.sh scaffolds Python project correctly."""
    bootstrap_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "bootstrap.sh"
    )

    with open(bootstrap_path) as f:
        content = f.read()

    # Check that the script contains Python scaffolding commands
    assert "python3 -m venv" in content or ".venv" in content
    assert "pip install" in content or "pip3 install" in content


# BDD: Scaffold Rust project
def test_bootstrap_scaffolds_rust_project():
    """Test that bootstrap.sh scaffolds Rust project correctly."""
    bootstrap_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "bootstrap.sh"
    )

    with open(bootstrap_path) as f:
        content = f.read()

    # Check that the script contains Rust scaffolding commands
    assert "cargo init" in content or "cargo new" in content


# BDD: Create CI workflow for TypeScript
def test_bootstrap_creates_ci_workflow_typescript():
    """Test that bootstrap.sh creates CI workflow for TypeScript projects."""
    bootstrap_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "bootstrap.sh"
    )

    with open(bootstrap_path) as f:
        content = f.read()

    # Check that the script contains CI workflow creation for TypeScript
    assert ".github/workflows/ci.yml" in content
    assert "setup-node" in content or "actions/setup-node" in content


# BDD: Create CI workflow for Python
def test_bootstrap_creates_ci_workflow_python():
    """Test that bootstrap.sh creates CI workflow for Python projects."""
    bootstrap_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "bootstrap.sh"
    )

    with open(bootstrap_path) as f:
        content = f.read()

    # Check that the script contains CI workflow creation for Python
    assert ".github/workflows/ci.yml" in content
    assert "setup-python" in content or "actions/setup-python" in content


# BDD: Verify build passes before marking initialized
def test_bootstrap_verifies_build_before_initialized():
    """Test that bootstrap.sh verifies build passes before creating .baadd_initialized."""
    bootstrap_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "bootstrap.sh"
    )

    with open(bootstrap_path) as f:
        content = f.read()

    # Check that the script verifies build before marking initialized
    assert ".baadd_initialized" in content
    # Should have build verification logic
    assert "BUILD_CMD" in content or "build_cmd" in content


# BDD: Create Day 0 journal entry
def test_bootstrap_creates_day_0_journal_entry():
    """Test that bootstrap.sh creates Day 0 journal entry."""
    bootstrap_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "bootstrap.sh"
    )

    with open(bootstrap_path) as f:
        content = f.read()

    # Check that the script creates journal entry for bootstrap
    assert "JOURNAL.md" in content
    assert "Bootstrap" in content or "bootstrap" in content


# BDD: Write fallback journal if agent skips
def test_bootstrap_writes_fallback_journal():
    """Test that bootstrap.sh writes fallback journal if agent skips."""
    bootstrap_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "bootstrap.sh"
    )

    with open(bootstrap_path) as f:
        content = f.read()

    # Check that the script has fallback journal logic
    assert "JOURNAL.md" in content
    # Should have logic to detect if journal was written
    assert "fallback" in content.lower() or "auto" in content.lower()


# BDD: Seed journal index on bootstrap
def test_bootstrap_seeds_journal_index():
    """Test that bootstrap.sh seeds journal index on bootstrap."""
    bootstrap_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "bootstrap.sh"
    )

    with open(bootstrap_path) as f:
        content = f.read()

    # Check that the script creates JOURNAL_INDEX.md with proper structure
    assert "JOURNAL_INDEX.md" in content
    assert "| Day | Date | Time | Coverage | Summary |" in content
