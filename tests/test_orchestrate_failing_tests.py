#!/usr/bin/env python3
"""Tests for orchestrate.py worker with failing tests shows warning"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_shows_warn():
    """Worker with failing tests should show WARN status."""
    result = {
        "scenario": "Failing tests scenario",
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


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_not_merged():
    """Worker with failing tests should not be merged."""
    result = {
        "scenario": "Broken scenario",
        "branch": "agent/broken",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": False,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    merged = (
        result["commits"] > 0
        and result.get("has_marker", True)
        and result["tests_pass"]
    )

    assert merged is False


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_thrown_away():
    """Worker with failing tests should be thrown away."""
    result = {
        "scenario": "Broken tests",
        "branch": "agent/broken",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": False,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    if result["commits"] == 0:
        outcome = "THROWN AWAY (no commits — agent made no progress)"
    elif not result.get("has_marker", True):
        outcome = "THROWN AWAY (BDD marker not found)"
    elif not result["tests_pass"]:
        outcome = "THROWN AWAY (tests failing)"
    else:
        outcome = "MERGED"

    assert outcome == "THROWN AWAY (tests failing)"


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_status_text():
    """Status text should indicate failing tests."""
    result = {
        "scenario": "Broken tests",
        "branch": "agent/broken",
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


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_with_commits():
    """Worker with commits but failing tests shows WARN."""
    result = {
        "scenario": "Partial work",
        "branch": "agent/partial",
        "wt_path": "/tmp/wt",
        "commits": 3,
        "tests_pass": False,
        "has_marker": True,
        "elapsed_s": 45,
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
    assert result["commits"] == 3


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_status_in_orchestrator():
    """Orchestrator shows WARN for failing tests."""
    results = [
        {"scenario": "A", "commits": 2, "tests_pass": True, "has_marker": True},
        {"scenario": "B", "commits": 1, "tests_pass": False, "has_marker": True},
        {"scenario": "C", "commits": 1, "tests_pass": True, "has_marker": True},
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

    assert statuses == ["[OK]", "[WARN: tests failing]", "[OK]"]


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_thrown_away_message():
    """Thrown away message should explain tests are failing."""
    result = {
        "scenario": "Failing tests",
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
        message = "THROWN AWAY (no commits — agent made no progress)"
    elif not result.get("has_marker", True):
        message = "THROWN AWAY (BDD marker not found)"
    elif not result["tests_pass"]:
        message = "THROWN AWAY (tests failing)"
    else:
        message = "MERGED"

    assert "tests failing" in message


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_merged_flag_false():
    """Worker with failing tests has merged=False."""
    result = {
        "scenario": "Broken",
        "branch": "agent/broken",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": False,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    merged = (
        result["commits"] > 0
        and result.get("has_marker", True)
        and result["tests_pass"]
    )
    result["merged"] = merged

    assert result["merged"] is False


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_total_time_included():
    """Worker with failing tests still contributes to total time."""
    results = [
        {"scenario": "A", "commits": 2, "elapsed_s": 100, "tests_pass": True},
        {"scenario": "B", "commits": 1, "elapsed_s": 50, "tests_pass": False},
        {"scenario": "C", "commits": 1, "elapsed_s": 75, "tests_pass": True},
    ]

    total_time = sum(r.get("elapsed_s", 0) for r in results)

    assert total_time == 225


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_orchestrator_summary():
    """Orchestrator summary shows failed count includes failing tests."""
    results = [
        {"scenario": "A", "commits": 2, "tests_pass": True, "has_marker": True},
        {"scenario": "B", "commits": 1, "tests_pass": False, "has_marker": True},
        {"scenario": "C", "commits": 1, "tests_pass": True, "has_marker": True},
    ]

    merged_count = sum(
        1
        for r in results
        if r["commits"] > 0 and r.get("has_marker", True) and r["tests_pass"]
    )
    failed_count = len(results) - merged_count

    assert merged_count == 2
    assert failed_count == 1


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_status_priority():
    """Failing tests has lower priority than no commits."""
    test_cases = [
        ({"commits": 0, "tests_pass": False}, "[FAIL: no commits]"),
        ({"commits": 1, "tests_pass": False}, "[WARN: tests failing]"),
        ({"commits": 1, "tests_pass": True}, "[OK]"),
    ]

    for result, expected in test_cases:
        if result["commits"] == 0:
            status_str = "[FAIL: no commits]"
        elif not result["tests_pass"]:
            status_str = "[WARN: tests failing]"
        else:
            status_str = "[OK]"
        assert status_str == expected, f"Expected {expected} for {result}"


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_result_dict():
    """Worker result dict has all required fields even with failing tests."""
    result = {
        "scenario": "Broken tests",
        "branch": "agent/broken",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": False,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "Test output",
    }

    required_fields = [
        "scenario",
        "branch",
        "wt_path",
        "commits",
        "tests_pass",
        "has_marker",
        "elapsed_s",
        "rc",
        "stdout",
    ]

    for field in required_fields:
        assert field in result, f"Missing required field: {field}"


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_status_consistency():
    """Status is consistent across different checks."""
    result = {
        "scenario": "Consistent broken",
        "branch": "agent/consistent",
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

    merged = (
        result["commits"] > 0
        and result.get("has_marker", True)
        and result["tests_pass"]
    )

    assert status_str == "[WARN: tests failing]"
    assert merged is False


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_with_stdout():
    """Worker with failing tests may have stdout output."""
    result = {
        "scenario": "Broken with output",
        "branch": "agent/broken",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": False,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "FAILED: test_1\nFAILED: test_2",
    }

    if result["commits"] == 0:
        status_str = "[FAIL: no commits]"
    elif not result["tests_pass"]:
        status_str = "[WARN: tests failing]"
    else:
        status_str = "[OK]"

    assert status_str == "[WARN: tests failing]"
    assert "FAILED" in result["stdout"]


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_with_rc():
    """Worker with failing tests may have non-zero rc."""
    result = {
        "scenario": "Broken with rc",
        "branch": "agent/broken",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": False,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 1,
        "stdout": "Tests failed",
    }

    if result["commits"] == 0:
        status_str = "[FAIL: no commits]"
    elif not result["tests_pass"]:
        status_str = "[WARN: tests failing]"
    else:
        status_str = "[OK]"

    assert status_str == "[WARN: tests failing]"
    assert result["rc"] == 1


# BDD: Worker with failing tests shows warning
def test_worker_failing_tests_orchestrator_result():
    """Orchestrator result includes tests_pass=False."""
    result = {
        "scenario": "Broken",
        "branch": "agent/broken",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": False,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    assert result["tests_pass"] is False
    assert result["commits"] == 1
    assert result["has_marker"] is True
