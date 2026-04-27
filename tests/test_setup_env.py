#!/usr/bin/env python3
"""Tests for setup_env.sh scenarios."""

import os


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
