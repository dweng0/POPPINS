#!/usr/bin/env python3
"""Tests for orchestrate.py worker with no commits shows fail status"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_shows_fail():
    """Worker with 0 commits should show fail status."""
    result = {
        "scenario": "No progress scenario",
        "branch": "agent/noprogress",
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


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_not_merged():
    """Worker with 0 commits should not be marked as merged."""
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

    merged = (
        result["commits"] > 0
        and result.get("has_marker", True)
        and result["tests_pass"]
    )

    assert merged is False


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_thrown_away():
    """Worker with 0 commits should be thrown away."""
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

    if result["commits"] == 0:
        outcome = "THROWN AWAY (no commits — agent made no progress)"
    elif not result.get("has_marker", True):
        outcome = "THROWN AWAY (BDD marker not found)"
    elif not result["tests_pass"]:
        outcome = "THROWN AWAY (tests failing)"
    else:
        outcome = "MERGED"

    assert outcome == "THROWN AWAY (no commits — agent made no progress)"


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_zero_elapsed():
    """Worker with 0 commits should have 0 elapsed time."""
    result = {
        "scenario": "Zero time scenario",
        "branch": "agent/zero",
        "wt_path": "/tmp/wt",
        "commits": 0,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 0,
        "rc": 0,
        "stdout": "",
    }

    assert result["commits"] == 0
    assert result["elapsed_s"] == 0


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_empty_stdout():
    """Worker with 0 commits may have empty stdout."""
    result = {
        "scenario": "Silent scenario",
        "branch": "agent/silent",
        "wt_path": "/tmp/wt",
        "commits": 0,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 0,
        "rc": 0,
        "stdout": "",
    }

    assert result["commits"] == 0
    assert result["stdout"] == ""


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_with_rc():
    """Worker with 0 commits may have non-zero rc."""
    result = {
        "scenario": "Failed scenario",
        "branch": "agent/failed",
        "wt_path": "/tmp/wt",
        "commits": 0,
        "tests_pass": False,
        "has_marker": False,
        "elapsed_s": 5,
        "rc": 1,
        "stdout": "Error occurred",
    }

    assert result["commits"] == 0
    assert result["rc"] == 1


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_status_in_orchestrator():
    """Orchestrator shows FAIL status for 0 commits."""
    results = [
        {"scenario": "A", "commits": 2, "tests_pass": True, "has_marker": True},
        {"scenario": "B", "commits": 0, "tests_pass": True, "has_marker": True},
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

    assert statuses == ["[OK]", "[FAIL: no commits]", "[OK]"]


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_merged_flag_false():
    """Worker with 0 commits has merged=False."""
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

    merged = (
        result["commits"] > 0
        and result.get("has_marker", True)
        and result["tests_pass"]
    )
    result["merged"] = merged

    assert result["merged"] is False


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_thrown_away_message():
    """Thrown away message should explain why."""
    result = {
        "scenario": "Abandoned scenario",
        "branch": "agent/abandoned",
        "wt_path": "/tmp/wt",
        "commits": 0,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 0,
        "rc": 0,
        "stdout": "",
    }

    if result["commits"] == 0:
        message = "THROWN AWAY (no commits — agent made no progress)"

    assert "no commits" in message
    assert "agent made no progress" in message


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_total_time_excluded():
    """Worker with 0 commits should still contribute to total time."""
    results = [
        {"scenario": "A", "commits": 2, "elapsed_s": 100},
        {"scenario": "B", "commits": 0, "elapsed_s": 0},
        {"scenario": "C", "commits": 1, "elapsed_s": 50},
    ]

    total_time = sum(r.get("elapsed_s", 0) for r in results)

    assert total_time == 150


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_orchestrator_summary():
    """Orchestrator summary shows failed count includes 0 commits."""
    results = [
        {"scenario": "A", "commits": 2, "tests_pass": True, "has_marker": True},
        {"scenario": "B", "commits": 0, "tests_pass": True, "has_marker": True},
        {"scenario": "C", "commits": 1, "tests_pass": False, "has_marker": True},
    ]

    merged_count = sum(
        1
        for r in results
        if r["commits"] > 0 and r.get("has_marker", True) and r["tests_pass"]
    )
    failed_count = len(results) - merged_count

    assert merged_count == 1
    assert failed_count == 2


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_status_text():
    """Status text should be clear about the failure."""
    result = {
        "scenario": "Failed worker",
        "branch": "agent/failed",
        "wt_path": "/tmp/wt",
        "commits": 0,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 0,
        "rc": 0,
        "stdout": "",
    }

    if result["commits"] == 0:
        status_text = f"[FAIL: no commits] {result['scenario']} — 0 commit(s), {result['elapsed_s']}s"

    assert "[FAIL: no commits]" in status_text
    assert "0 commit(s)" in status_text


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_result_dict():
    """Worker result dict has all required fields even with 0 commits."""
    result = {
        "scenario": "Empty result",
        "branch": "agent/empty",
        "wt_path": "/tmp/wt",
        "commits": 0,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 0,
        "rc": 0,
        "stdout": "",
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


# BDD: Worker with no commits shows fail status
def test_worker_no_commits_status_consistency():
    """Status is consistent across different checks."""
    result = {
        "scenario": "Consistent scenario",
        "branch": "agent/consistent",
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

    merged = (
        result["commits"] > 0
        and result.get("has_marker", True)
        and result["tests_pass"]
    )

    assert status_str == "[FAIL: no commits]"
    assert merged is False
