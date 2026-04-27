#!/usr/bin/env python3
"""Tests for parse_poppins_config.py"""

import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Parse poppins.yml with agent section
def test_parse_poppins_yml_with_agent_section():
    """Test that poppins.yml with agent.max_iterations: 50 outputs POPPINS_AGENT_MAX_ITERATIONS='50'"""
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
                ["python3", script_path],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"Command failed: {result.stderr}"
            assert "POPPINS_AGENT_MAX_ITERATIONS='50'" in result.stdout, \
                f"Expected POPPINS_AGENT_MAX_ITERATIONS='50' in output, got: {result.stdout}"
        finally:
            os.chdir(orig)


# BDD: Deep merge file config with defaults
def test_deep_merge_file_config_with_defaults():
    import importlib.util
    import os
    import tempfile

    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(script_dir, "scripts", "parse_poppins_config.py")

    spec = importlib.util.spec_from_file_location("parse_poppins_config", config_path)
    mod = importlib.util.module_from_spec(spec)

    with tempfile.TemporaryDirectory() as tmpdir:
        poppins_path = os.path.join(tmpdir, "poppins.yml")
        with open(poppins_path, "w") as f:
            f.write("orchestration:\n  max_parallel_agents: 5\n")

        orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            # Re-load module from tmpdir so it finds poppins.yml
            spec.loader.exec_module(mod)
            config = mod.get_config()
            assert config["orchestration"]["max_parallel_agents"] == 5
            # Agent defaults should remain
            assert "max_iterations" in config["agent"]
        finally:
            os.chdir(orig)
