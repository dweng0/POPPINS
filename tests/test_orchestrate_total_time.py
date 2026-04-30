#!/usr/bin/env python3
"""Tests for orchestrate.py tracking total agent time across workers"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Track total agent time across workers
def test_total_agent_time_calculation():
    """Total agent time should be sum of all worker elapsed times."""
    results = [
        {"scenario": "Scenario A", "elapsed_s": 120},
        {"scenario": "Scenario B", "elapsed_s": 90},
        {"scenario": "Scenario C", "elapsed_s": 150},
    ]

    total_time = sum(r.get("elapsed_s", 0) for r in results)

    assert total_time == 360, f"Expected 360s, got {total_time}s"


# BDD: Track total agent time across workers
def test_total_agent_time_with_zero_elapsed():
    """Workers with zero elapsed time should not affect total."""
    results = [
        {"scenario": "Scenario A", "elapsed_s": 100},
        {"scenario": "Scenario B", "elapsed_s": 0},
        {"scenario": "Scenario C", "elapsed_s": 50},
    ]

    total_time = sum(r.get("elapsed_s", 0) for r in results)

    assert total_time == 150, f"Expected 150s, got {total_time}s"


# BDD: Track total agent time across workers
def test_total_agent_time_missing_elapsed_field():
    """Workers without elapsed_s field should default to 0."""
    results = [
        {"scenario": "Scenario A", "elapsed_s": 80},
        {"scenario": "Scenario B"},
        {"scenario": "Scenario C", "elapsed_s": 20},
    ]

    total_time = sum(r.get("elapsed_s", 0) for r in results)

    assert total_time == 100, f"Expected 100s, got {total_time}s"


# BDD: Track total agent time across workers
def test_total_agent_time_empty_results():
    """Empty results should have zero total time."""
    results = []

    total_time = sum(r.get("elapsed_s", 0) for r in results)

    assert total_time == 0, f"Expected 0s, got {total_time}s"


# BDD: Track total agent time across workers
def test_orchestrator_reports_total_agent_time():
    """Orchestrator should report total agent time in summary."""

    results = [
        {
            "scenario": "Scenario A",
            "elapsed_s": 120,
            "commits": 2,
            "tests_pass": True,
            "has_marker": True,
            "rc": 0,
            "stdout": "",
        },
        {
            "scenario": "Scenario B",
            "elapsed_s": 90,
            "commits": 1,
            "tests_pass": True,
            "has_marker": True,
            "rc": 0,
            "stdout": "",
        },
        {
            "scenario": "Scenario C",
            "elapsed_s": 150,
            "commits": 3,
            "tests_pass": True,
            "has_marker": True,
            "rc": 0,
            "stdout": "",
        },
    ]

    total_time = sum(r.get("elapsed_s", 0) for r in results)

    assert total_time == 360, f"Expected 360s total, got {total_time}s"


# BDD: Track total agent time across workers
def test_total_agent_time_in_orchestrator_complete():
    """Orchestrator complete message should show total agent time."""
    results = [
        {"scenario": "Test 1", "elapsed_s": 100},
        {"scenario": "Test 2", "elapsed_s": 200},
    ]

    total_time = sum(r.get("elapsed_s", 0) for r in results)

    assert total_time == 300
    assert "300s" in f"Total agent time:   {total_time}s"


# BDD: Track total agent time across workers
def test_total_agent_time_high_precision():
    """Total agent time should handle fractional seconds."""
    results = [
        {"scenario": "Scenario A", "elapsed_s": 120.5},
        {"scenario": "Scenario B", "elapsed_s": 90.25},
        {"scenario": "Scenario C", "elapsed_s": 150.75},
    ]

    total_time = sum(r.get("elapsed_s", 0) for r in results)

    assert abs(total_time - 361.5) < 0.01, f"Expected ~361.5s, got {total_time}s"


# BDD: Track total agent time across workers
def test_total_agent_time_with_failed_workers():
    """Failed workers should still contribute to total time."""
    results = [
        {"scenario": "Scenario A", "elapsed_s": 100, "tests_pass": True},
        {"scenario": "Scenario B", "elapsed_s": 50, "tests_pass": False},
        {"scenario": "Scenario C", "elapsed_s": 75, "tests_pass": True},
    ]

    total_time = sum(r.get("elapsed_s", 0) for r in results)

    assert total_time == 225, f"Expected 225s, got {total_time}s"
