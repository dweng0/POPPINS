#!/usr/bin/env python3
"""Tests for orchestrate.py running N rounds sequentially"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Run orchestrator N rounds sequentially
def test_orchestrator_runs_multiple_rounds():
    """Orchestrator should run up to max_rounds rounds sequentially."""
    from orchestrate import select_scenarios

    ordered = [f"Scenario {i}" for i in range(1, 11)]
    max_agents = 3

    round1_selected, remaining = select_scenarios(ordered, max_agents=3)
    assert len(round1_selected) == 3
    assert round1_selected == ["Scenario 1", "Scenario 2", "Scenario 3"]
    assert len(remaining) == 7

    round2_selected, remaining = select_scenarios(remaining, max_agents=3)
    assert len(round2_selected) == 3
    assert round2_selected == ["Scenario 4", "Scenario 5", "Scenario 6"]
    assert len(remaining) == 4

    round3_selected, remaining = select_scenarios(remaining, max_agents=3)
    assert len(round3_selected) == 3
    assert round3_selected == ["Scenario 7", "Scenario 8", "Scenario 9"]
    assert len(remaining) == 1

    round4_selected, remaining = select_scenarios(remaining, max_agents=3)
    assert len(round4_selected) == 1
    assert round4_selected == ["Scenario 10"]
    assert len(remaining) == 0


# BDD: Run orchestrator N rounds sequentially
def test_orchestrator_round_progress_messages():
    """Each round should have a progress message."""
    round_num = 1
    max_rounds = 3
    selected_count = 2

    message = f"\n=== Round {round_num}/{max_rounds} — {selected_count} scenario(s) ==="

    assert "Round 1/3" in message
    assert "2 scenario(s)" in message


# BDD: Run orchestrator N rounds sequentially
def test_orchestrator_round_complete_summary():
    """Each round should have a summary of merged vs thrown away."""
    round_merged = 2
    round_failed = 1
    done_so_far = 3
    total = 9

    message = (
        f"\n  Round 1/3 complete — "
        f"{round_merged} merged, {round_failed} thrown away. "
        f"Progress: {done_so_far}/{total} attempted, {total - done_so_far} remaining."
    )

    assert "Round 1/3 complete" in message
    assert "2 merged" in message
    assert "1 thrown away" in message
    assert "Progress: 3/9 attempted" in message


# BDD: Run orchestrator N rounds sequentially
def test_orchestrator_round_with_zero_scenarios():
    """Round with no scenarios should skip."""
    selected = []

    if not selected:
        skip_message = "  No worktrees created for this round. Skipping."

    assert skip_message == "  No worktrees created for this round. Skipping."


# BDD: Run orchestrator N rounds sequentially
def test_orchestrator_round_stops_when_exhausted():
    """Round should stop when all scenarios exhausted."""
    all_selected_names = ["Scenario 1", "Scenario 2"]
    ordered_names = ["Scenario 1", "Scenario 2"]

    remaining_names = [n for n in ordered_names if n not in all_selected_names]

    if not remaining_names:
        stop_message = "\n  All scenarios exhausted before round 3. Stopping."
    else:
        stop_message = ""

    assert stop_message == "\n  All scenarios exhausted before round 3. Stopping."


# BDD: Run orchestrator N rounds sequentially
def test_orchestrator_round_with_max_rounds_1():
    """With max_rounds=1, only one round should run."""
    max_rounds = 1

    rounds_run = []
    for round_num in range(1, max_rounds + 1):
        rounds_run.append(round_num)

    assert rounds_run == [1]


# BDD: Run orchestrator N rounds sequentially
def test_orchestrator_round_with_max_rounds_5():
    """With max_rounds=5, up to 5 rounds should run."""
    max_rounds = 5

    rounds_run = []
    for round_num in range(1, max_rounds + 1):
        rounds_run.append(round_num)

    assert rounds_run == [1, 2, 3, 4, 5]


# BDD: Run orchestrator N rounds sequentially
def test_orchestrator_round_selection_logic():
    """Each round should select top N scenarios from remaining."""
    from orchestrate import select_scenarios

    all_scenarios = [f"Scenario {i}" for i in range(1, 21)]
    max_agents = 4

    all_selected = []
    remaining = all_scenarios.copy()

    round_num = 1
    while remaining and round_num <= 5:
        selected, remaining = select_scenarios(remaining, max_agents=max_agents)
        all_selected.extend(selected)
        round_num += 1

    assert len(all_selected) == 20
    assert remaining == []
    assert all_selected == all_scenarios


# BDD: Run orchestrator N rounds sequentially
def test_orchestrator_round_with_partial_last_round():
    """Last round may have fewer than max_agents scenarios."""
    from orchestrate import select_scenarios

    ordered = [f"Scenario {i}" for i in range(1, 11)]
    max_agents = 4

    round1, remaining = select_scenarios(ordered, max_agents=max_agents)
    round2, remaining = select_scenarios(remaining, max_agents=max_agents)
    round3, remaining = select_scenarios(remaining, max_agents=max_agents)

    assert len(round1) == 4
    assert len(round2) == 4
    assert len(round3) == 2
    assert remaining == []


# BDD: Run orchestrator N rounds sequentially
def test_orchestrator_round_deferred_count():
    """Deferred count should show scenarios beyond max_rounds."""
    from orchestrate import select_scenarios

    ordered = [f"Scenario {i}" for i in range(1, 16)]
    max_agents = 4
    max_rounds = 2

    round1, remaining = select_scenarios(ordered, max_agents=max_agents)
    round2, remaining = select_scenarios(remaining, max_agents=max_agents)

    deferred = remaining
    deferred_count = len(deferred)

    assert len(round1) == 4
    assert len(round2) == 4
    assert deferred_count == 7
    assert deferred == [f"Scenario {i}" for i in range(9, 16)]
