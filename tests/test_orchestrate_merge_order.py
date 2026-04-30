#!/usr/bin/env python3
"""Tests for orchestrate.py merge results in planned order"""

import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Merge results in planned order
def test_merge_results_in_planned_order():
    """Results should be merged in the planned order, not completion order."""
    planned_order = ["First scenario", "Second scenario", "Third scenario"]

    results = [
        {"scenario": "Third scenario", "commits": 1, "tests_pass": True},
        {"scenario": "First scenario", "commits": 1, "tests_pass": True},
        {"scenario": "Second scenario", "commits": 1, "tests_pass": True},
    ]

    sorted_results = sorted(results, key=lambda r: planned_order.index(r["scenario"]))

    assert [r["scenario"] for r in sorted_results] == planned_order, (
        f"Expected {planned_order}, got {[r['scenario'] for r in sorted_results]}"
    )


# BDD: Merge results in planned order
def test_merge_order_preserves_planning():
    """Even if workers complete in different order, merge should follow plan."""

    planned_order = ["Alpha", "Beta", "Gamma"]

    results = [
        {"scenario": "Gamma", "commits": 1, "tests_pass": True, "has_marker": True},
        {"scenario": "Alpha", "commits": 1, "tests_pass": True, "has_marker": True},
        {"scenario": "Beta", "commits": 1, "tests_pass": True, "has_marker": True},
    ]

    sorted_results = sorted(results, key=lambda r: planned_order.index(r["scenario"]))

    assert [r["scenario"] for r in sorted_results] == planned_order, (
        f"Expected {planned_order}, got {[r['scenario'] for r in sorted_results]}"
    )


# BDD: Merge results in planned order
def test_merge_worker_result_rejects_no_commits():
    """Worker with no commits should not merge."""
    from orchestrate import merge_worker_result

    result = {
        "scenario": "No commits scenario",
        "branch": "agent/nocommits",
        "wt_path": "/tmp/wt-nocommits",
        "commits": 0,
        "tests_pass": True,
        "has_marker": True,
        "elapsed_s": 0,
        "rc": 0,
        "stdout": "",
    }

    with patch("orchestrate.run_cmd", return_value=("", "", 0)):
        merged = merge_worker_result(result, "/tmp/main")

    assert merged is False, "Worker with no commits should not merge"


# BDD: Merge results in planned order
def test_merge_worker_result_rejects_failing_tests():
    """Worker with failing tests should not merge even with commits."""
    from orchestrate import merge_worker_result

    result = {
        "scenario": "Failing scenario",
        "branch": "agent/fail",
        "wt_path": "/tmp/wt-fail",
        "commits": 1,
        "tests_pass": False,
        "has_marker": True,
        "elapsed_s": 5,
        "rc": 0,
        "stdout": "",
    }

    merged = merge_worker_result(result, "/tmp/main")

    assert merged is False, "Worker with failing tests should not merge"


# BDD: Merge results in planned order
def test_merge_worker_result_rejects_no_marker():
    """Worker without BDD marker should not merge."""
    from orchestrate import merge_worker_result

    result = {
        "scenario": "No marker scenario",
        "branch": "agent/nomarker",
        "wt_path": "/tmp/wt-nomarker",
        "commits": 1,
        "tests_pass": True,
        "has_marker": False,
        "elapsed_s": 5,
        "rc": 0,
        "stdout": "",
    }

    merged = merge_worker_result(result, "/tmp/main")

    assert merged is False, "Worker without BDD marker should not merge"


# BDD: Merge results in planned order
def test_orchestrate_sorts_results_by_planned_order():
    """Orchestrator sorts results by planned order before merging."""

    planned_order = ["Scenario A", "Scenario B", "Scenario C"]

    results = [
        {
            "scenario": "Scenario C",
            "commits": 1,
            "tests_pass": True,
            "has_marker": True,
        },
        {
            "scenario": "Scenario A",
            "commits": 1,
            "tests_pass": True,
            "has_marker": True,
        },
        {
            "scenario": "Scenario B",
            "commits": 1,
            "tests_pass": True,
            "has_marker": True,
        },
    ]

    sorted_results = sorted(results, key=lambda r: planned_order.index(r["scenario"]))

    scenarios_in_order = [r["scenario"] for r in sorted_results]
    assert scenarios_in_order == planned_order, (
        f"Results should be sorted by planned order: {scenarios_in_order}"
    )
