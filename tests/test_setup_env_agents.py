#!/usr/bin/env python3
"""Tests for setup_env.sh always install agent dependencies"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Always install agent dependencies
def test_always_install_anthropic():
    """setup_env.sh should always ensure anthropic package is installed."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "import anthropic" in content
    assert "anthropic" in content


# BDD: Always install agent dependencies
def test_always_install_openai():
    """setup_env.sh should always ensure openai package is installed."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "import openai" in content
    assert "openai" in content


# BDD: Always install agent dependencies
def test_always_install_uv_or_pip():
    """setup_env.sh should use uv or pip for package installation."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "uv pip install" in content or "python3 -m pip install" in content


# BDD: Always install agent dependencies
def test_always_install_silent():
    """setup_env.sh should install packages silently."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "--quiet" in content


# BDD: Always install agent dependencies
def test_always_install_error_handling():
    """setup_env.sh should handle missing packages gracefully."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "if ! python3 -c" in content


# BDD: Always install agent dependencies
def test_always_install_order():
    """setup_env.sh should install agent dependencies after language setup."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    lines = content.split("\n")

    go_line = None
    anthropic_line = None

    for i, line in enumerate(lines):
        if "go)" in line:
            go_line = i
        if "anthropic" in line:
            anthropic_line = i

    assert go_line is not None
    assert anthropic_line is not None
    assert anthropic_line > go_line


# BDD: Always install agent dependencies
def test_always_install_message():
    """setup_env.sh should print installation message."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "Installing anthropic" in content
    assert "Installing openai" in content


# BDD: Always install agent dependencies
def test_always_install_anthropic_package():
    """setup_env.sh should install anthropic package."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "anthropic" in content
    assert "pip install" in content


# BDD: Always install agent dependencies
def test_always_install_openai_package():
    """setup_env.sh should install openai package."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "openai" in content
    assert "pip install" in content


# BDD: Always install agent dependencies
def test_always_install_conditional():
    """setup_env.sh should only install if package not already installed."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "if ! python3 -c" in content


# BDD: Always install agent dependencies
def test_always_install_both_packages():
    """setup_env.sh should install both anthropic and openai."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "anthropic" in content
    assert "openai" in content


# BDD: Always install agent dependencies
def test_always_install_final_message():
    """setup_env.sh should print environment ready message."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "Environment ready" in content


# BDD: Always install agent dependencies
def test_always_install_no_duplicate_installs():
    """setup_env.sh should not reinstall if package exists."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "if ! python3 -c" in content
    assert "import anthropic" in content


# BDD: Always install agent dependencies
def test_always_install_uv_priority():
    """setup_env.sh should prefer uv over pip."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    lines = content.split("\n")

    uv_line = None
    pip_line = None

    for i, line in enumerate(lines):
        if "uv pip install" in line:
            uv_line = i
        if "python3 -m pip install" in line:
            pip_line = i

    assert uv_line is not None
    assert pip_line is not None
    assert uv_line < pip_line


# BDD: Always install agent dependencies
def test_always_install_language_independent():
    """setup_env.sh should install agent dependencies regardless of language."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "anthropic" in content
    assert "openai" in content


# BDD: Always install agent dependencies
def test_always_install_error_message():
    """setup_env.sh should print error message during installation."""
    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    setup_env_path = scripts_dir + "/setup_env.sh"

    with open(setup_env_path) as f:
        content = f.read()

    assert "Installing anthropic Python package" in content
    assert "Installing openai Python package" in content
