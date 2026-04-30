import os
from unittest.mock import patch, mock_open
from scripts.orchestrate import main

# BDD: orchestrate.py appends session_end for each worker when it finishes


def test_orchestrate_appends_session_end_for_each_worker_when_it_finishes():
    # BDD: orchestrate.py appends session_end for each worker when it finishes
    sessions_path = "/tmp/test_orchestrate_session_end.jsonl"
    if os.path.exists(sessions_path):
        os.remove(sessions_path)

    wt_paths_created = []

    with (
        patch("scripts.orchestrate.get_uncovered_scenarios") as mock_uncovered,
        patch("scripts.orchestrate.create_worktree") as mock_create_wt,
        patch("scripts.orchestrate.run_pm_pipeline") as mock_pipeline,
        patch("scripts.orchestrate.remove_worktree") as mock_remove_wt,
        patch("scripts.orchestrate.get_config") as mock_config,
        patch("scripts.orchestrate.merge_worker_result") as mock_merge,
        patch("scripts.orchestrate.run_integration_tests") as mock_integration,
        patch("scripts.orchestrate.run_cmd") as mock_cmd,
        patch("scripts.orchestrate.read_file_safe") as mock_read_file,
        patch("scripts.orchestrate.append_session_event") as mock_append_event,
        patch("os.path.exists") as mock_exists,
        patch("os.path.isdir") as mock_isdir,
        patch("builtins.open", create=True),
    ):
        mock_uncovered.return_value = [
            ("Feature", "Scenario 1"),
            ("Feature", "Scenario 2"),
            ("Feature", "Scenario 3"),
        ]

        def side_effect_wt(slug, main_dir):
            path = f"/tmp/baadd-wt-{slug}-{os.getpid()}"
            wt_paths_created.append(path)
            return path, f"branch-{slug}"

        mock_create_wt.side_effect = side_effect_wt

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

        mock_config.return_value = {
            "orchestration": {"max_parallel_agents": 3, "max_rounds": 1},
            "agent": {},
        }

        mock_merge.return_value = False
        mock_integration.return_value = (True, "")

        def cmd_side_effect(cmd, cwd=None, timeout=30, capture=True):
            if "extract_scenario.sh" in cmd:
                return ("Extracted scenario: 30 lines", "", 0)
            elif "git rev-parse HEAD" in cmd:
                return ("abc123", "", 0)
            elif "parse_bdd_config.py" in cmd:
                return ("export TEST_CMD='pytest'", "", 0)
            elif "check_bdd_coverage.py" in cmd:
                return ("- [x] Scenario 1\n- [x] Scenario 2\n- [x] Scenario 3", "", 0)
            return ("", "", 0)

        mock_cmd.side_effect = cmd_side_effect

        mock_read_file.return_value = (
            "# Journal\n\n- [x] Scenario 1\n- [x] Scenario 2\n- [x] Scenario 3"
        )

        def exists_side_effect(path):
            if "BDD_SCENARIO.md" in path or "sessions.jsonl" in path:
                return True
            if path.startswith("/tmp/baadd-wt-"):
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        mock_isdir.return_value = True

        m_open = mock_open()
        with patch("builtins.open", m_open):
            with patch(
                "sys.argv",
                ["scripts/orchestrate.py", "--max-agents", "3", "--max-rounds", "1"],
            ):
                main()

    session_end_calls = [
        c
        for c in mock_append_event.call_args_list
        if c[0][1].get("type") == "session_end"
    ]

    assert len(session_end_calls) == 3

    wt_paths_from_ends = []
    for call_obj in session_end_calls:
        event = call_obj[0][1]
        assert event["type"] == "session_end"
        assert "wt_path" in event
        wt_paths_from_ends.append(event["wt_path"])

    assert set(wt_paths_from_ends) == set(wt_paths_created)

    if os.path.exists(sessions_path):
        os.remove(sessions_path)
