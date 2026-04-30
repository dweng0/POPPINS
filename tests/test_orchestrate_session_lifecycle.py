import os
import json
from unittest.mock import patch

# BDD: Worktree Session Lifecycle


def test_orchestrate_appends_session_start_per_worker_worktree():
    # BDD: orchestrate.py appends session_start per worker worktree it spawns
    sessions_path = "/tmp/test_orchestrate_sessions.jsonl"
    if os.path.exists(sessions_path):
        os.remove(sessions_path)

    # We will mock the components of orchestrate to avoid actual heavy lifting
    # but still test the logic of spawning and logging.

    with (
        patch("scripts.orchestrate.get_uncovered_scenarios") as mock_uncovered,
        patch("scripts.orchestrate.create_worktree") as mock_create_wt,
        patch("scripts.orchestrate.run_pm_pipeline") as mock_pipeline,
        patch("scripts.orchestrate.remove_worktree") as mock_remove_wt,
        patch("scripts.orchestrate.get_config") as mock_config,
    ):
        # Setup mocks
        mock_uncovered.return_value = [
            ("Feature", "Scenario 1"),
            ("Feature", "Scenario 2"),
            ("Feature", "Scenario 3"),
        ]

        def side_effect_wt(slug, main_dir):
            path = f"/tmp/baadd-wt-{slug}"
            return path, f"branch-{slug}"

        mock_create_wt.side_effect = side_effect_wt

        # Mock pipeline to return a successful result
        def side_effect_pipeline(scenario_name, wt_path, branch, main_dir, config):
            return {
                "scenario": scenario_name,
                "branch": branch,
                "wt_path": wt_path,
                "commits": 1,
                "tests_pass": True,
                "has_marker": True,
                "elapsed_s": 1.0,
                "rc": 0,
                "stdout": "success",
            }

        mock_pipeline.side_effect = side_effect_pipeline

        # Mock config to have max_parallel_agents=3
        mock_config.return_value = {
            "orchestration": {"max_parallel_agents": 3},
            "agent": {},
        }

        # We need to mock the command line arguments for orchestrate.main()
        with patch("sys.argv", ["scripts/orchestrate.py", "--max-agents", "3"]):
            from scripts.orchestrate import main

            main()

    # Verify sessions.jsonl contains 3 separate session_start lines with distinct wt_paths
    # Note: orchestrate.py doesn't actually call append_session_event in its current state!
    # It only writes to orchestrator_events.jsonl and JOURNAL.md.
    # The requirement says "evolve.sh and orchestrate.py append JSON lines to sessions.jsonl".
    # This test will fail if I don't implement it in orchestrate.py.

    with open(sessions_path, "r") as f:
        lines = f.readlines()

    assert len(lines) == 3
    wt_paths = []
    for line in lines:
        data = json.loads(line)
        assert data["type"] == "session_start"
        wt_paths.append(data["wt_path"])

    assert len(set(wt_paths)) == 3

    if os.path.exists(sessions_path):
        os.remove(sessions_path)
