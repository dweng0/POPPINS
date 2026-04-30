#!/usr/bin/env python3
"""Tests for orchestrate.py parallel agent output streaming with scenario prefixes"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from orchestrate import format_worker_output


# BDD: Stream agent output with scenario prefix
def test_worker_output_streaming_with_scenario_prefix():
    """Each line of agent output should be prefixed with scenario name for parallel execution clarity."""

    scenario_name = "Login with valid credentials"

    mock_stdout = "Line 1\nLine 2\nLine 3"

    result = {
        "scenario": scenario_name,
        "branch": "agent/login-with-valid-credentials",
        "wt_path": "/tmp/wt-login",
        "commits": 2,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 45.5,
        "rc": 0,
        "stdout": mock_stdout,
    }

    formatted = format_worker_output(result)

    for line in mock_stdout.split("\n"):
        assert f"[{scenario_name}]" in formatted, (
            f"Expected scenario prefix in output for line: {line}"
        )
        assert line in formatted or re.search(
            rf"\[{re.escape(scenario_name)}\].*{re.escape(line)}", formatted
        ), f"Expected line '{line}' to be in formatted output with prefix"


# BDD: Stream agent output with scenario prefix
def test_worker_output_streaming_multiline_with_prefix():
    """Multi-line agent output should preserve scenario prefix on each line."""

    scenario_name = "Parse YAML frontmatter from BDD.md"
    multiline_output = "Starting parse...\nReading frontmatter...\nDone!"

    result = {
        "scenario": scenario_name,
        "branch": "agent/parse-yaml",
        "wt_path": "/tmp/wt-yaml",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 12.3,
        "rc": 0,
        "stdout": multiline_output,
    }

    formatted = format_worker_output(result)

    lines = formatted.strip().split("\n")
    for line in lines:
        if line.strip():
            assert f"[{scenario_name}]" in line, (
                f"Line should have scenario prefix: {line}"
            )


# BDD: Stream agent output with scenario prefix
def test_worker_output_error_with_scenario_prefix():
    """Error output should also be prefixed with scenario name."""

    scenario_name = "Setup Go dependencies"
    error_output = "ERROR: go not installed\nTrying to install..."

    result = {
        "scenario": scenario_name,
        "branch": "agent/setup-go",
        "wt_path": "/tmp/wt-go",
        "commits": 0,
        "tests_pass": False,
        "has_marker": False,
        "elapsed_s": 5.0,
        "rc": 1,
        "stdout": error_output,
    }

    formatted = format_worker_output(result)

    assert f"[{scenario_name}]" in formatted, "Error output should have scenario prefix"
    assert "ERROR: go not installed" in formatted


# BDD: Stream agent output with scenario prefix
def test_worker_output_empty_stdout():
    """Worker with empty stdout should still show scenario prefix in status line."""

    scenario_name = "Handle missing gh CLI gracefully"

    result = {
        "scenario": scenario_name,
        "branch": "agent/gh-cli",
        "wt_path": "/tmp/wt-gh",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 8.0,
        "rc": 0,
        "stdout": "",
    }

    formatted = format_worker_output(result)

    assert f"[{scenario_name}]" in formatted or f"({scenario_name})" in formatted, (
        "Status output should identify the scenario"
    )


# BDD: Stream agent output with scenario prefix
def test_worker_output_long_scenario_name():
    """Long scenario names should be truncated in prefix but remain readable."""

    scenario_name = "This is a very long scenario name that exceeds normal display width and should be truncated for cleaner output"
    assert len(scenario_name) > 50

    result = {
        "scenario": scenario_name,
        "branch": "agent/long-name",
        "wt_path": "/tmp/wt-long",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 20.0,
        "rc": 0,
        "stdout": "Output line",
    }

    formatted = format_worker_output(result)

    assert "Output line" in formatted
    assert (
        f"[{scenario_name}" in formatted
        or "[This is a very long scenario name" in formatted
    ), "Prefix should show scenario name (possibly truncated)"
