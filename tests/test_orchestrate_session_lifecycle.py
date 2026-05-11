import os
import json
import os.path
from unittest.mock import patch, mock_open

# BDD: Worktree Session Lifecycle

_original_exists = os.path.exists
_original_open = open


def test_orchestrate_appends_session_start_per_worker_worktree():
    # BDD: orchestrate.py appends session_start per worker worktree it spawns
    # Since os.getcwd is mocked to return /tmp, sessions.jsonl will be at /tmp/sessions.jsonl
    sessions_path = "/tmp/sessions.jsonl"
    if _original_exists(sessions_path):
        os.remove(sessions_path)

    # We will mock the components of orchestrate to avoid actual heavy lifting
    # but still test the logic of spawning and logging.

    def mock_run_cmd(cmd, cwd=None, timeout=30, capture=True):
        if "pytest" in str(cmd).lower() or "test" in str(cmd).lower():
            return ("", "", 0)
        if "git" in str(cmd).lower():
            return ("mock-output", "", 0)
        return ("", "", 0)

    def mock_exists(path):
        if "BDD_SCENARIO.md" in path:
            return True
        if "CONTEXT.md" in path:
            return False
        return _original_exists(path)

    def mock_open_func(path, mode="r", *args, **kwargs):
        path_str = str(path)
        if "BDD_SCENARIO.md" in path_str and mode == "r":
            return mock_open(read_data="line1\nline2\nline3\n").return_value
        return _original_open(path, mode, *args, **kwargs)

    with (
        patch("scripts.orchestrate.get_uncovered_scenarios") as mock_uncovered,
        patch("scripts.orchestrate.create_worktree") as mock_create_wt,
        patch("scripts.orchestrate.run_pm_pipeline") as mock_pipeline,
        patch("scripts.orchestrate.remove_worktree") as mock_remove_wt,
        patch("scripts.orchestrate.get_config") as mock_config,
        patch("scripts.orchestrate.run_cmd", side_effect=mock_run_cmd) as mock_run,
        patch("scripts.orchestrate.os.path.exists", side_effect=mock_exists),
        patch("scripts.orchestrate.os.getcwd", return_value="/tmp"),
        patch("builtins.open", side_effect=mock_open_func),
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
    with open(sessions_path, "r") as f:
        lines = f.readlines()

    assert len(lines) >= 3, (
        f"Expected at least 3 session_start events, got {len(lines)}"
    )
    wt_paths = []
    for line in lines:
        data = json.loads(line)
        if data["type"] == "session_start":
            wt_paths.append(data["wt_path"])

    assert len(wt_paths) >= 3, (
        f"Expected at least 3 session_start wt_paths, got {len(wt_paths)}"
    )
    assert len(set(wt_paths)) >= 3, (
        f"Expected at least 3 unique wt_paths, got {len(set(wt_paths))}"
    )

    if _original_exists(sessions_path):
        os.remove(sessions_path)
