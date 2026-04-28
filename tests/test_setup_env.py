#!/usr/bin/env python3
"""Tests for setup_env.sh scenarios."""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


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


# BDD: Setup Node dependencies
def test_setup_node_dependencies():
    """Test that setup_env.sh contains correct node|javascript) case with npm install logic."""
    setup_env_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "setup_env.sh"
    )

    with open(setup_env_path) as f:
        content = f.read()

    # 1. Verify the node|javascript) case block exists
    assert "node|javascript)" in content, "setup_env.sh must contain a node|javascript) case block"

    # 2. Extract the node|javascript) case block and verify it checks for package.json
    #    The case block ends at the next ;; pattern
    node_block_match = re.search(
        r"node\|javascript\)(.*?)\n\s*;;",
        content,
        re.DOTALL,
    )
    assert node_block_match is not None, "Could not find node|javascript) case block"
    node_block = node_block_match.group(1)

    assert "[ -f package.json ]" in node_block, (
        "node|javascript) case must check for package.json existence"
    )

    # 3. Verify it runs npm install inside that block
    assert "npm install" in node_block, (
        "node|javascript) case must run npm install when package.json exists"
    )


# BDD: Setup Rust toolchain
def test_setup_rust_toolchain():
    """Test that setup_env.sh installs Rust via rustup when LANGUAGE=rust and cargo is not installed."""
    setup_env_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "setup_env.sh"
    )

    with open(setup_env_path) as f:
        content = f.read()

    # Verify the script has a rust case
    assert "rust)" in content, "setup_env.sh should have a 'rust' case in its case statement"

    # Verify it checks for cargo not being installed
    assert "command -v cargo" in content, "setup_env.sh should check if cargo is installed"

    # Verify it installs Rust via rustup
    assert "rustup" in content, "setup_env.sh should install Rust via rustup"
    assert "sh.rustup.rs" in content, "setup_env.sh should use sh.rustup.rs for rustup installation"


# BDD: Skip unknown language gracefully
def test_skip_unknown_language_gracefully() -> None:
    """Test that setup_env.sh handles unknown languages gracefully with a default case."""
    setup_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "setup_env.sh"
    )

    with open(setup_path) as f:
        content = f.read()

    # 1. Verify the *) default case exists in the case statement
    assert "*)" in content, (
        "setup_env.sh must contain a *) default case in its case statement"
    )

    # 2. Extract the *) case block (from *) to the next ;;)
    default_block_match = re.search(
        r"\*\)(.*?)\n\s*;;",
        content,
        re.DOTALL,
    )
    assert default_block_match is not None, "Could not find *) default case block"
    default_block = default_block_match.group(1)

    # 3. Verify the default case prints a warning about unknown language
    assert "Unknown language" in default_block or "unknown" in default_block.lower(), (
        "Default case must warn about unknown language"
    )

    # 4. Verify the default case indicates it skips toolchain setup
    assert "skip" in default_block.lower(), (
        "Default case must indicate it skips toolchain setup"
    )

    # 5. Verify the default case does NOT exit with error (must continue, not fail)
    assert "exit 1" not in default_block, (
        "Default case must not contain 'exit 1' — it should skip, not fail"
    )
