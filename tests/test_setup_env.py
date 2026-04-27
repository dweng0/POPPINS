#!/usr/bin/env python3
"""Tests for setup_env.sh scenarios."""

import os
<<<<<<< HEAD


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
=======
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


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
>>>>>>> agent/setup-node-dependencies-20260427-213902
    )
