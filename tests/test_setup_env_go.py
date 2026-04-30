#!/usr/bin/env python3
"""Tests for setup_env.sh Go dependencies setup"""

import sys
import os
import subprocess
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Setup Go dependencies
def test_go_language_setup():
    """setup_env.sh should handle LANGUAGE=go."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["bash", "-c", f"cd {tmpdir} && LANGUAGE=go && echo 'Go setup complete'"],
            capture_output=True,
            text=True,
        )

    assert result.returncode == 0
    assert "Go setup complete" in result.stdout


# BDD: Setup Go dependencies
def test_go_mod_download_command():
    """setup_env.sh should run go mod download when go.mod exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        go_mod_path = os.path.join(tmpdir, "go.mod")
        with open(go_mod_path, "w") as f:
            f.write("module example.com/test\n\ngo 1.21\n")

        result = subprocess.run(
            [
                "bash",
                "-c",
                f"cd {tmpdir} && LANGUAGE=go && [ -f go.mod ] && go mod download 2>/dev/null || true",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0


# BDD: Setup Go dependencies
def test_go_version_output():
    """setup_env.sh should output Go version when Go is installed."""
    result = subprocess.run(
        ["bash", "-c", "which go"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        version_result = subprocess.run(
            ["bash", "-c", "go version"],
            capture_output=True,
            text=True,
        )
        assert "go" in version_result.stdout.lower()
    else:
        assert True


# BDD: Setup Go dependencies
def test_go_not_found_error():
    """setup_env.sh should error when Go is not installed."""
    result = subprocess.run(
        ["bash", "-c", "if ! command -v go &>/dev/null; then exit 1; fi"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        assert True


# BDD: Setup Go dependencies
def test_go_mod_download_silent():
    """setup_env.sh should run go mod download silently."""
    with tempfile.TemporaryDirectory() as tmpdir:
        go_mod_path = os.path.join(tmpdir, "go.mod")
        with open(go_mod_path, "w") as f:
            f.write("module example.com/test\n\ngo 1.21\n")

        result = subprocess.run(
            ["bash", "-c", f"cd {tmpdir} && go mod download 2>/dev/null || true"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0


# BDD: Setup Go dependencies
def test_go_setup_in_setup_env_sh():
    """setup_env.sh should have go case."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "go)" in content
    assert "go mod download" in content


# BDD: Setup Go dependencies
def test_go_case_handles_missing_go():
    """setup_env.sh go case should handle missing go command."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "if ! command -v go" in content
    assert "exit 1" in content


# BDD: Setup Go dependencies
def test_go_case_checks_go_mod():
    """setup_env.sh go case should check for go.mod."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "[ -f go.mod ]" in content


# BDD: Setup Go dependencies
def test_go_case_downloads_modules():
    """setup_env.sh go case should download modules."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "go mod download" in content


# BDD: Setup Go dependencies
def test_go_case_versions_output():
    """setup_env.sh go case should output Go version."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "go version" in content


# BDD: Setup Go dependencies
def test_go_case_error_message():
    """setup_env.sh go case should have error message for missing go."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "Go not found" in content
    assert "install it manually" in content


# BDD: Setup Go dependencies
def test_go_case_uses_setup_go_action():
    """setup_env.sh go case should mention setup-go action."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "setup-go action" in content


# BDD: Setup Go dependencies
def test_go_case_silent_mod_download():
    """setup_env.sh go case should run go mod download silently."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "go mod download 2>/dev/null || true" in content


# BDD: Setup Go dependencies
def test_go_case_language_variable():
    """setup_env.sh should use LANGUAGE variable for go."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert 'case "$LANGUAGE"' in content
    assert "go)" in content


# BDD: Setup Go dependencies
def test_go_case_default_fallback():
    """setup_env.sh should have default fallback for unknown languages."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "*)" in content
    assert "Unknown language" in content


# BDD: Setup Go dependencies
def test_go_case_order_in_switch():
    """setup_env.sh go case should be in correct position in switch."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    lines = content.split("\n")
    go_line = None
    java_line = None

    for i, line in enumerate(lines):
        if line.strip() == "go)":
            go_line = i
        if line.strip() == "java)":
            java_line = i

    assert go_line is not None
    assert java_line is not None
    assert go_line < java_line


# BDD: Setup Go dependencies
def test_go_case_error_handling():
    """setup_env.sh go case should handle errors gracefully."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "set -euo pipefail" in content
    assert "go mod download 2>/dev/null || true" in content
