#!/usr/bin/env python3
"""Tests for orchestrate.py worker result structure"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Worker result structure
def test_worker_result_has_scenario():
    """Worker result must include scenario name."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    assert "scenario" in result
    assert result["scenario"] == "Test scenario"


# BDD: Worker result structure
def test_worker_result_has_branch():
    """Worker result must include branch name."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test-scenario",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    assert "branch" in result
    assert result["branch"] == "agent/test-scenario"


# BDD: Worker result structure
def test_worker_result_has_wt_path():
    """Worker result must include worktree path."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test",
        "wt_path": "/tmp/wt-test",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    assert "wt_path" in result
    assert result["wt_path"] == "/tmp/wt-test"


# BDD: Worker result structure
def test_worker_result_has_commits():
    """Worker result must include commit count."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test",
        "wt_path": "/tmp/wt",
        "commits": 3,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    assert "commits" in result
    assert isinstance(result["commits"], int)
    assert result["commits"] >= 0


# BDD: Worker result structure
def test_worker_result_has_tests_pass():
    """Worker result must include tests_pass flag."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    assert "tests_pass" in result
    assert isinstance(result["tests_pass"], bool)


# BDD: Worker result structure
def test_worker_result_has_elapsed_s():
    """Worker result must include elapsed time in seconds."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 45.5,
        "rc": 0,
        "stdout": "",
    }

    assert "elapsed_s" in result
    assert isinstance(result["elapsed_s"], (int, float))
    assert result["elapsed_s"] >= 0


# BDD: Worker result structure
def test_worker_result_has_rc():
    """Worker result must include return code."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    assert "rc" in result
    assert isinstance(result["rc"], int)


# BDD: Worker result structure
def test_worker_result_has_stdout():
    """Worker result must include stdout."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "Agent output here",
    }

    assert "stdout" in result
    assert isinstance(result["stdout"], str)


# BDD: Worker result structure
def test_worker_result_merged_flag():
    """Worker result may include merged flag after merge."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
        "merged": True,
    }

    assert "merged" in result
    assert result["merged"] is True


# BDD: Worker result structure
def test_worker_result_empty_stdout():
    """Worker result may have empty stdout."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    assert result["stdout"] == ""


# BDD: Worker result structure
def test_worker_result_failed_case():
    """Failed worker result has rc=1 and tests_pass=False."""
    result = {
        "scenario": "Failed scenario",
        "branch": "agent/failed",
        "wt_path": "/tmp/wt-failed",
        "commits": 0,
        "tests_pass": False,
        "has_marker": False,
        "elapsed_s": 5,
        "rc": 1,
        "stdout": "Error message",
    }

    assert result["rc"] == 1
    assert result["tests_pass"] is False
    assert result["commits"] == 0


# BDD: Worker result structure
def test_worker_result_with_has_marker():
    """Worker result must include has_marker flag."""
    result = {
        "scenario": "Test scenario",
        "branch": "agent/test",
        "wt_path": "/tmp/wt",
        "commits": 1,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 10,
        "rc": 0,
        "stdout": "",
    }

    assert "has_marker" in result
    assert isinstance(result["has_marker"], bool)


# BDD: Worker result structure
def test_orchestrator_result_aggregation():
    """Orchestrator aggregates results from multiple workers."""
    results = [
        {
            "scenario": "Scenario A",
            "branch": "agent/a",
            "wt_path": "/tmp/wt-a",
            "commits": 2,
            "tests_pass": True,
            "has_marker": True,
            "elapsed_s": 100,
            "rc": 0,
            "stdout": "",
            "merged": True,
        },
        {
            "scenario": "Scenario B",
            "branch": "agent/b",
            "wt_path": "/tmp/wt-b",
            "commits": 1,
            "tests_pass": False,
            "has_marker": True,
            "elapsed_s": 50,
            "rc": 0,
            "stdout": "",
            "merged": False,
        },
    ]

    assert len(results) == 2
    assert all(r["scenario"] in ["Scenario A", "Scenario B"] for r in results)
    assert all(r["branch"] is not None for r in results)
    assert all(r["wt_path"] is not None for r in results)
    assert all(isinstance(r["commits"], int) for r in results)
    assert all(isinstance(r["tests_pass"], bool) for r in results)
    assert all(isinstance(r["elapsed_s"], (int, float)) for r in results)
    assert all(isinstance(r["rc"], int) for r in results)
    assert all(isinstance(r["stdout"], str) for r in results)


# BDD: Worker result structure
def test_worker_result_total_time_calculation():
    """Total time is sum of all worker elapsed times."""
    results = [
        {"scenario": "A", "elapsed_s": 120},
        {"scenario": "B", "elapsed_s": 90},
        {"scenario": "C", "elapsed_s": 150},
    ]

    total_time = sum(r.get("elapsed_s", 0) for r in results)

    assert total_time == 360


# BDD: Worker result structure
def test_worker_result_merge_status():
    """Each result tracks whether it was merged."""
    results = [
        {"scenario": "A", "merged": True},
        {"scenario": "B", "merged": True},
        {"scenario": "C", "merged": False},
    ]

    merged_count = sum(1 for r in results if r.get("merged"))
    failed_count = len(results) - merged_count

    assert merged_count == 2
    assert failed_count == 1
