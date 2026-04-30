#!/usr/bin/env python3
"""Tests for CI environment detection in agent.py"""

import os
import sys
import subprocess
import textwrap

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
AGENT_PATH = os.path.join(SCRIPTS_DIR, "agent.py")


def _run_in_ci_env(env_vars: dict) -> bool:
    """Load agent module with given env vars and return IN_CI value."""
    env_str = "\n".join(f"os.environ[{k!r}] = {v!r}" for k, v in env_vars.items())
    script = textwrap.dedent(f"""
        import sys, os
        sys.path.insert(0, {SCRIPTS_DIR!r})
        for k in ["CI", "GITHUB_ACTIONS", "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
                  "GROQ_API_KEY", "CUSTOM_API_KEY", "CUSTOM_BASE_URL"]:
            os.environ.pop(k, None)
        {env_str}
        import importlib.util
        spec = importlib.util.spec_from_file_location("agent", {AGENT_PATH!r})
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print("true" if mod.IN_CI else "false")
    """)
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr!r}"
    return result.stdout.strip() == "true"


# BDD: Detect CI environment
def test_in_ci_set_when_ci_true():
    """IN_CI is True when CI=true is set."""
    assert _run_in_ci_env({"CI": "true"}) is True


# BDD: Detect CI environment
def test_in_ci_set_when_github_actions_true():
    """IN_CI is True when GITHUB_ACTIONS=true is set."""
    assert _run_in_ci_env({"GITHUB_ACTIONS": "true"}) is True


# BDD: Detect CI environment
def test_in_ci_false_when_neither_set():
    """IN_CI is False when neither CI nor GITHUB_ACTIONS is set."""
    assert _run_in_ci_env({}) is False


# BDD: Detect CI environment
def test_in_ci_uses_ci_optimized_output():
    """Agent uses CI-optimized output format (::group::) when IN_CI is True."""
    script = textwrap.dedent(f"""
        import sys, os, io
        sys.path.insert(0, {SCRIPTS_DIR!r})
        for k in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY",
                  "CUSTOM_API_KEY", "CUSTOM_BASE_URL"]:
            os.environ.pop(k, None)
        os.environ["CI"] = "true"

        import importlib.util
        spec = importlib.util.spec_from_file_location("agent", {AGENT_PATH!r})
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        assert mod.IN_CI is True, f"IN_CI should be True"

        long_output = "\\n".join(f"line {{i}}" for i in range(10))
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            mod.print_tool_call("bash", {{"command": "ls"}}, long_output)
        finally:
            sys.stdout = old

        out = buf.getvalue()
        assert "::group::" in out, f"Expected CI log group annotation, got: {{out!r}}"
        print("OK")
    """)
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True
    )
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    assert "OK" in result.stdout
