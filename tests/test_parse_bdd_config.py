#!/usr/bin/env python3
"""Tests for parse_bdd_config.py, parse_poppins_config.py, and orchestrate.py"""

import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from parse_poppins_config import get_config


# BDD: Parse YAML frontmatter from BDD.md
def test_parse_yaml_frontmatter_from_bdd_md():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("---\n")
        f.write("language: python\n")
        f.write("framework: pytest\n")
        f.write("build_cmd: python3 -m py_compile src/*.py\n")
        f.write("test_cmd: python3 -m pytest tests/\n")
        f.write("---\n")
        f.write("\n")
        f.write("Some content\n")
        f.flush()

        result = subprocess.run(
            ["python3", "scripts/parse_bdd_config.py", f.name],
            capture_output=True,
            text=True,
        )

        output = result.stdout
        assert "LANGUAGE='python'" in output
        assert "FRAMEWORK='pytest'" in output
        assert "BUILD_CMD='python3 -m py_compile src/*.py'" in output
        assert "TEST_CMD='python3 -m pytest tests/'" in output

        os.unlink(f.name)


# BDD: Handle missing frontmatter gracefully
def test_handle_missing_frontmatter_gracefully():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("No frontmatter here\n")
        f.write("Just regular content\n")
        f.flush()

        result = subprocess.run(
            ["python3", "scripts/parse_bdd_config.py", f.name],
            capture_output=True,
            text=True,
        )

        output = result.stdout
        assert "LANGUAGE='unknown'" in output
        assert "FRAMEWORK='none'" in output

        os.unlink(f.name)


# BDD: Parse frontmatter with quoted values
def test_parse_frontmatter_with_quoted_values():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("---\n")
        f.write("language: typescript\n")
        f.write('build_cmd: "npm run build"\n')
        f.write("test_cmd: 'npm test'\n")
        f.write("---\n")
        f.flush()

        result = subprocess.run(
            ["python3", "scripts/parse_bdd_config.py", f.name],
            capture_output=True,
            text=True,
        )

        output = result.stdout
        assert "LANGUAGE='typescript'" in output
        assert "BUILD_CMD='npm run build'" in output
        assert "TEST_CMD='npm test'" in output

        os.unlink(f.name)


# BDD: Apply defaults when poppins.yml missing
def test_apply_defaults_when_poppins_yml_missing():
    """Test that default values are applied when no poppins.yml file exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            config = get_config()
        finally:
            os.chdir(orig)
    # Verify agent defaults
    assert config["agent"]["max_iterations"] == 75
    assert config["agent"]["session_timeout"] == 3600


# BDD: Default max_rounds is 1
def test_default_max_rounds_is_1():
    with tempfile.TemporaryDirectory() as tmpdir:
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            config = get_config()
        finally:
            os.chdir(orig)
    assert config["orchestration"]["max_rounds"] == 1


# BDD: Read max_rounds from poppins.yml
def test_read_max_rounds_from_poppins_yml():
    with tempfile.TemporaryDirectory() as tmpdir:
        poppins_path = os.path.join(tmpdir, "poppins.yml")
        with open(poppins_path, "w") as f:
            f.write("orchestration:\n")
            f.write("  max_rounds: 3\n")
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            config = get_config()
        finally:
            os.chdir(orig)
    assert config["orchestration"]["max_rounds"] == 3


# BDD: Search parent directories for poppins.yml
def test_search_parent_directories_for_poppins_yml():
    """Test that find_config() searches parent directories for poppins.yml"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create poppins.yml in the root of tmpdir
        poppins_path = os.path.join(tmpdir, "poppins.yml")
        with open(poppins_path, "w") as f:
            f.write("orchestration:\n")
            f.write("  max_rounds: 5\n")
        
        # Create a subdirectory and change into it
        subdir = os.path.join(tmpdir, "subdir")
        os.makedirs(subdir)
        
        orig = os.getcwd()
        os.chdir(subdir)
        try:
            # poppins.yml is NOT in subdir, but is in parent (tmpdir)
            config_path = None
            # Import here to get fresh find_config
            import importlib
            import scripts.parse_poppins_config as ppm
            importlib.reload(ppm)
            config_path = ppm.find_config()
            
            # Should find poppins.yml in parent directory
            assert config_path is not None, "find_config() should find poppins.yml in parent"
            assert config_path == poppins_path, f"Should find {poppins_path}, got {config_path}"
        finally:
            os.chdir(orig)


# BDD: Get single config value via dot notation
def test_get_single_config_value_via_dot_notation():
    """Test that --get flag retrieves a single config value via dot notation."""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(script_dir, "scripts", "parse_poppins_config.py")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        poppins_path = os.path.join(tmpdir, "poppins.yml")
        with open(poppins_path, "w") as f:
            f.write("agent:\n")
            f.write("  max_iterations: 50\n")
        
        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            result = subprocess.run(
                ["python3", script_path, "--get", "agent.max_iterations"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"Command failed: {result.stderr}"
            assert result.stdout.strip() == "50", f"Expected '50', got '{result.stdout.strip()}'"
        finally:
            os.chdir(orig)

