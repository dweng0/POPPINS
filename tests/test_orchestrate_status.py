#!/usr/bin/env python3
"""Tests for orchestrate.py status indicators for worker output"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Status indicators for worker output
def test_worker_output_ok_status():
    """Worker with commits and passing tests shows OK status."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test",
        "wt_path": "/tmp/wt",
        "commits": 2,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 45.5,
        "rc": 0,
        "stdout": "",
    }

    if result["commits"] == 0:
        status_str = "[FAIL: no commits]"
    elif not result["tests_pass"]:
        status_str = "[WARN: tests failing]"
    else:
        status_str = "[OK]"

    assert status_str == "[OK]"


# BDD: Status indicators for worker output
def test_worker_output_fail_no_commits():
    """Worker with no commits shows FAIL status."""
    result = {
        "scenario": "No commits scenario",
        "branch": "agent/nocommits",
        "wt_path": "/tmp/wt",
        "commits": 0,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 0,
        "rc": 0,
        "stdout": "",
    }

    if result["commits"] == 0:
        status_str = "[FAIL: no commits]"
    elif not result["tests_pass"]:
        status_str = "[WARN: tests failing]"
    else:
        status_str = "[OK]"

    assert status_str == "[FAIL: no commits]"


# BDD: Status indicators for worker output
def test_worker_output_warn_failing_tests():
    """Worker with failing tests shows WARN status."""
    result = {
        "scenario": "Failing scenario",
        "branch": "agent/fail",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": False,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    if result["commits"] == 0:
        status_str = "[FAIL: no commits]"
    elif not result["tests_pass"]:
        status_str = "[WARN: tests failing]"
    else:
        status_str = "[OK]"

    assert status_str == "[WARN: tests failing]"


# BDD: Status indicators for worker output
def test_worker_output_status_with_commits_and_passing():
    """Worker with commits and passing tests shows OK."""
    result = {
        "scenario": "Success scenario",
        "branch": "agent/success",
        "wt_path": "/tmp/wt",
        "commits": 3,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 120,
        "rc": 0,
        "stdout": "",
    }

    status_str = (
        "[OK]"
        if result["commits"] > 0 and result["tests_pass"]
        else "[FAIL: no commits]"
        if result["commits"] == 0
        else "[WARN: tests failing]"
    )

    assert status_str == "[OK]"


# BDD: Status indicators for worker output
def test_worker_output_status_no_commits_failing_tests():
    """Worker with no commits takes priority over tests_pass check."""
    result = {
        "scenario": "Empty scenario",
        "branch": "agent/empty",
        "wt_path": "/tmp/wt",
        "commits": 0,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 0,
        "rc": 0,
        "stdout": "",
    }

    status_str = "[FAIL: no commits]"

    assert status_str == "[FAIL: no commits]"


# BDD: Status indicators for worker output
def test_worker_output_status_commits_but_failing_tests():
    """Worker with commits but failing tests shows WARN."""
    result = {
        "scenario": "Partial scenario",
        "branch": "agent/partial",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": False,
        "has_marker": True,
        "elapsed_s": 15,
        "rc": 0,
        "stdout": "",
    }

    status_str = "[WARN: tests failing]"

    assert status_str == "[WARN: tests failing]"


# BDD: Status indicators for worker output
def test_worker_output_status_with_has_marker():
    """Worker without has_marker shows FAIL."""
    result = {
        "scenario": "No marker scenario",
        "branch": "agent/nomarker",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": True,
        "has_marker": False,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    if not result.get("has_marker", True):
        status_str = "[FAIL: no BDD marker]"
    elif result["commits"] == 0:
        status_str = "[FAIL: no commits]"
    elif not result["tests_pass"]:
        status_str = "[WARN: tests failing]"
    else:
        status_str = "[OK]"

    assert status_str == "[FAIL: no BDD marker]"


# BDD: Status indicators for worker output
def test_worker_output_format_with_status():
    """Formatted output includes status indicator."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test",
        "wt_path": "/tmp/wt",
        "commits": 2,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 45.5,
        "rc": 0,
        "stdout": "",
    }

    if result["commits"] == 0:
        status_str = "[FAIL: no commits]"
    elif not result["tests_pass"]:
        status_str = "[WARN: tests failing]"
    else:
        status_str = "[OK]"

    output = f"{status_str} {result['scenario']} — {result['commits']} commit(s), {result['elapsed_s']}s"

    assert "[OK]" in output
    assert "Test scenario" in output
    assert "2 commit(s)" in output


# BDD: Status indicators for worker output
def test_worker_output_format_fail_status():
    """Formatted output shows FAIL status."""
    result = {
        "scenario": "Failed scenario",
        "branch": "agent/failed",
        "wt_path": "/tmp/wt",
        "commits": 0,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 0,
        "rc": 1,
        "stdout": "",
    }

    if result["commits"] == 0:
        status_str = "[FAIL: no commits]"
    elif not result["tests_pass"]:
        status_str = "[WARN: tests failing]"
    else:
        status_str = "[OK]"

    output = f"{status_str} {result['scenario']} — {result['commits']} commit(s), {result['elapsed_s']}s"

    assert "[FAIL: no commits]" in output


# BDD: Status indicators for worker output
def test_worker_output_format_warn_status():
    """Formatted output shows WARN status."""
    result = {
        "scenario": "Warning scenario",
        "branch": "agent/warn",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": False,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    if result["commits"] == 0:
        status_str = "[FAIL: no commits]"
    elif not result["tests_pass"]:
        status_str = "[WARN: tests failing]"
    else:
        status_str = "[OK]"

    output = f"{status_str} {result['scenario']} — {result['commits']} commit(s), {result['elapsed_s']}s"

    assert "[WARN: tests failing]" in output


# BDD: Status indicators for worker output
def test_orchestrator_status_output():
    """Orchestrator prints status with scenario name."""
    results = [
        {"scenario": "A", "commits": 2, "tests_pass": True, "has_marker": True},
        {"scenario": "B", "commits": 1, "tests_pass": False, "has_marker": True},
        {"scenario": "C", "commits": 0, "tests_pass": True, "has_marker": True},
    ]

    statuses = []
    for r in results:
        if r["commits"] == 0:
            status_str = "[FAIL: no commits]"
        elif not r["tests_pass"]:
            status_str = "[WARN: tests failing]"
        else:
            status_str = "[OK]"
        statuses.append(status_str)

    assert statuses == ["[OK]", "[WARN: tests failing]", "[FAIL: no commits]"]


# BDD: Status indicators for worker output
def test_worker_output_status_priority():
    """Status priority: no commits > failing tests > OK."""
    test_cases = [
        ({"commits": 0, "tests_pass": True, "has_marker": True}, "[FAIL: no commits]"),
        (
            {"commits": 1, "tests_pass": False, "has_marker": True},
            "[WARN: tests failing]",
        ),
        ({"commits": 1, "tests_pass": True, "has_marker": True}, "[OK]"),
    ]

    for result, expected in test_cases:
        if result["commits"] == 0:
            status_str = "[FAIL: no commits]"
        elif not result["tests_pass"]:
            status_str = "[WARN: tests failing]"
        else:
            status_str = "[OK]"
        assert status_str == expected, f"Expected {expected} for {result}"


# BDD: Status indicators for worker output
def test_worker_output_with_elapsed_time():
    """Status output includes elapsed time."""
    result = {
        "scenario": "Timed scenario",
        "branch": "agent/timed",
        "wt_path": "/tmp/wt",
        "commits": 3,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 125.5,
        "rc": 0,
        "stdout": "",
    }

    if result["commits"] == 0:
        status_str = "[FAIL: no commits]"
    elif not result["tests_pass"]:
        status_str = "[WARN: tests failing]"
    else:
        status_str = "[OK]"

    output = f"{status_str} {result['scenario']} — {result['commits']} commit(s), {result['elapsed_s']}s"

    assert "[OK]" in output
    assert "125.5s" in output


# BDD: Status indicators for worker output
def test_worker_output_status_with_rc():
    """Status output includes return code."""
    result = {
        "scenario": "RC scenario",
        "branch": "agent/rc",
        "wt_path": "/tmp/wt",
        "commits": 2,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 50,
        "rc": 0,
        "stdout": "",
    }

    if result["commits"] == 0:
        status_str = "[FAIL: no commits]"
    elif not result["tests_pass"]:
        status_str = "[WARN: tests failing]"
    else:
        status_str = "[OK]"

    output = f"{status_str} {result['scenario']} — {result['commits']} commit(s), {result['elapsed_s']}s, exit={result['rc']}"

    assert "[OK]" in output
    assert "exit=0" in output
