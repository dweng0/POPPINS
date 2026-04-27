#!/usr/bin/env python3
"""Tests for evolve.sh script"""

import os
import subprocess
import tempfile


# BDD: Load BDD config before session
def test_load_bdd_config_before_session():
    """Test that evolve.sh loads BDD config and sets environment variables."""
    # Create a temporary BDD.md with known config values
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("---\n")
        f.write("language: python\n")
        f.write("framework: pytest\n")
        f.write("build_cmd: python3 -m py_compile src/*.py\n")
        f.write("test_cmd: python3 -m pytest tests/\n")
        f.write("lint_cmd: python3 -m ruff check .\n")
        f.write("fmt_cmd: python3 -m ruff format .\n")
        f.write("birth_date: 2026-01-01\n")
        f.write("---\n")
        f.write("\n")
        f.write("Some content\n")
        bdd_path = f.name

    try:
        # Simulate what evolve.sh does: eval the output of parse_bdd_config.py
        result = subprocess.run(
            ["python3", "scripts/parse_bdd_config.py", bdd_path],
            capture_output=True,
            text=True,
        )

        # The output should be shell variable assignments
        output = result.stdout
        
        # Verify the key environment variables are set
        assert "export LANGUAGE=" in output, "LANGUAGE should be exported"
        assert "export BUILD_CMD=" in output, "BUILD_CMD should be exported"
        assert "export TEST_CMD=" in output, "TEST_CMD should be exported"
        
        # Verify the values are correct
        assert "LANGUAGE='python'" in output
        assert "BUILD_CMD='python3 -m py_compile src/*.py'" in output
        assert "TEST_CMD='python3 -m pytest tests/'" in output
        
        # Now simulate sourcing these in a shell and verify they're set
        shell_result = subprocess.run(
            ["bash", "-c", f"eval \"$(python3 scripts/parse_bdd_config.py {bdd_path})\" && echo LANGUAGE=$LANGUAGE && echo BUILD_CMD=$BUILD_CMD && echo TEST_CMD=$TEST_CMD"],
            capture_output=True,
            text=True,
        )
        
        assert "LANGUAGE=python" in shell_result.stdout
        assert "BUILD_CMD=python3 -m py_compile" in shell_result.stdout
        assert "TEST_CMD=python3 -m pytest tests/" in shell_result.stdout
        
    finally:
        os.unlink(bdd_path)
