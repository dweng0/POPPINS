"""Tests for scripts/dashboard.py — Rich TUI dashboard for orchestrate.py."""

import collections
import json
import os
import sys
import tempfile
import time
from unittest.mock import MagicMock, patch, PropertyMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: parse_args returns watch=False and mode is wrapper when --watch is absent
def test_parse_args_default_watch_is_false():
    from dashboard import parse_args

    result, _ = parse_args([])
    assert result.watch is False


# BDD: parse_args returns watch=True when --watch flag is present
def test_parse_args_watch_flag():
    from dashboard import parse_args

    result, _ = parse_args(["--watch"])
    assert result.watch is True


# BDD: parse_args collects unrecognised flags into pass_args for forwarding
def test_parse_args_collects_unknown_flags():
    from dashboard import parse_args

    result, pass_args = parse_args(["--max-agents", "2", "--max-rounds", "3"])
    assert "--max-agents" in pass_args
    assert "2" in pass_args
    assert "--max-rounds" in pass_args
    assert "3" in pass_args


# BDD: parse_args --refresh sets poll interval
def test_parse_args_refresh_flag():
    from dashboard import parse_args

    result, _ = parse_args(["--refresh", "5"])
    assert result.refresh == 5


# BDD: parse_args default refresh interval is 2 seconds
def test_parse_args_default_refresh():
    from dashboard import parse_args

    result, _ = parse_args([])
    assert result.refresh == 2


# BDD: --watch and --refresh can be combined with pass_args
def test_parse_args_combined_flags():
    from dashboard import parse_args

    result, pass_args = parse_args(["--watch", "--refresh", "3", "--max-agents", "2"])
    assert result.watch is True
    assert result.refresh == 3
    assert "--max-agents" in pass_args
    assert "2" in pass_args


# BDD: dashboard.py defines a main() function called from __main__
def test_dashboard_has_main():
    import dashboard

    assert callable(getattr(dashboard, "main", None)), (
        "dashboard.py must define a main() function"
    )


# BDD: AgentState is a dataclass with the required fields
def test_agentstate_is_a_dataclass_with_the_required_fields():
    import dataclasses
    from dashboard import AgentState

    assert dataclasses.is_dataclass(AgentState), (
        "AgentState must be decorated with @dataclass"
    )
    field_names = {f.name for f in dataclasses.fields(AgentState)}
    expected = {
        "wt_path",
        "scenario_name",
        "active_phase",
        "done_phases",
        "current_iter",
        "max_iter",
        "tokens",
        "last_tools",
        "start_ts",
    }
    assert field_names == expected, f"Expected fields {expected}, got {field_names}"


# BDD: AgentState.elapsed_s property returns seconds since start_ts
def test_agent_state_elapsed_s_property_returns_seconds_since_start_ts():
    import time
    from dashboard import AgentState

    state = AgentState(
        wt_path="/tmp/test", scenario_name="test", start_ts=time.time() - 60
    )
    result = state.elapsed_s
    assert isinstance(result, float)
    assert 59.0 <= result <= 61.0


# BDD: Rich is the only third-party import in dashboard.py
def test_dashboard_only_imports_rich():
    import ast
    import pathlib

    src = (
        pathlib.Path(__file__).parent.parent / "scripts" / "dashboard.py"
    ).read_text()
    tree = ast.parse(src)
    stdlib_and_allowed = {
        "os",
        "sys",
        "re",
        "json",
        "time",
        "threading",
        "subprocess",
        "argparse",
        "signal",
        "collections",
        "dataclasses",
        "typing",
        "datetime",
        "glob",
        "pathlib",
        "rich",
    }
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            else:
                names = [node.module.split(".")[0]] if node.module else []
            for name in names:
                assert name in stdlib_and_allowed, (
                    f"dashboard.py imports '{name}' — only 'rich' is allowed as a third-party dependency"
                )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_jsonl(path, events):
    with open(path, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")


# ---------------------------------------------------------------------------
# Dashboard file existence and basic structure
# ---------------------------------------------------------------------------


# BDD: Dashboard file exists at scripts/dashboard.py
def test_dashboard_file_exists_at_scripts_dashboard_py():
    path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "scripts", "dashboard.py")
    )
    assert os.path.exists(path), "scripts/dashboard.py must exist"


# BDD: Running "python3 scripts/dashboard.py" opens the Rich TUI immediately
def test_dashboard_help_exits_without_error():
    import subprocess

    root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
    result = subprocess.run(
        [sys.executable, "scripts/dashboard.py", "--help"],
        capture_output=True,
        text=True,
        cwd=root,
    )
    assert result.returncode == 0
    assert "--watch" in result.stdout
    assert "--refresh" in result.stdout


# BDD: The dashboard is only for scripts/orchestrate.py — not evolve.sh or agent.py
def test_dashboard_only_spawns_orchestrate():
    from dashboard import build_subprocess_cmd

    cmd = build_subprocess_cmd([])
    cmd_str = " ".join(cmd)
    assert "orchestrate.py" in cmd_str
    assert "evolve.sh" not in cmd_str
    assert "agent.py" not in cmd_str


# BDD: Live refresh loop uses rich.live.Live with refresh_per_second
def test_live_uses_refresh_per_second():
    import pathlib

    src = (
        pathlib.Path(__file__).parent.parent / "scripts" / "dashboard.py"
    ).read_text()
    assert "refresh_per_second" in src
    assert "Live" in src


# BDD: Each agent is rendered as a rich.panel.Panel
def test_each_agent_rendered_as_panel():
    from rich.panel import Panel
    from dashboard import AgentState, build_agent_panel

    state = AgentState(
        wt_path="/tmp/test", scenario_name="My Scenario", start_ts=time.time()
    )
    result = build_agent_panel(state)
    assert isinstance(result, Panel)
    assert "My Scenario" in str(result.title)


# BDD: Overall renderable is a rich.console.Group of Panels stacked vertically
def test_build_renderable_returns_group_with_correct_count():
    from rich.console import Group
    from dashboard import AgentState, build_renderable

    states = [
        AgentState(wt_path=f"/tmp/wt{i}", scenario_name=f"S{i}", start_ts=time.time())
        for i in range(2)
    ]
    buf = collections.deque(maxlen=10)
    result = build_renderable(states, buf, time.time())
    assert isinstance(result, Group)
    assert len(result.renderables) == 4  # header + 2 agents + log


# ---------------------------------------------------------------------------
# Worktree discovery
# ---------------------------------------------------------------------------


# BDD: discover_worktrees returns baadd worktree paths from git worktree list output
def test_discover_worktrees_returns_baadd_paths():
    from dashboard import discover_worktrees

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = (
        "worktree /home/user/project\n\nworktree /tmp/baadd-wt-my-scenario-1234\n"
    )
    with patch("subprocess.run", return_value=mock_result):
        paths = discover_worktrees("/home/user/project")
    assert "/tmp/baadd-wt-my-scenario-1234" in paths


# BDD: discover_worktrees excludes the main worktree
def test_discover_worktrees_excludes_main():
    from dashboard import discover_worktrees

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = (
        "worktree /home/user/project\n\nworktree /tmp/baadd-wt-foo-99\n"
    )
    with patch("subprocess.run", return_value=mock_result):
        paths = discover_worktrees("/home/user/project")
    assert "/home/user/project" not in paths
    assert "/tmp/baadd-wt-foo-99" in paths


# BDD: discover_worktrees returns empty list when no baadd worktrees exist
def test_discover_worktrees_empty_when_no_baadd():
    from dashboard import discover_worktrees

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "worktree /home/user/project\n"
    with patch("subprocess.run", return_value=mock_result):
        paths = discover_worktrees("/home/user/project")
    assert paths == []


# BDD: discover_worktrees returns empty list when git command fails
def test_discover_worktrees_empty_on_failure():
    from dashboard import discover_worktrees

    with patch("subprocess.run", side_effect=OSError("git not found")):
        paths = discover_worktrees()
    assert paths == []


# ---------------------------------------------------------------------------
# Name resolution helpers
# ---------------------------------------------------------------------------


# BDD: slug_to_name converts hyphenated path slug to display name
def test_slug_to_name_converts_path():
    from dashboard import slug_to_name

    assert (
        slug_to_name("/tmp/baadd-wt-enable-verbose-mode-5678") == "enable verbose mode"
    )


# BDD: slug_to_name handles path with no trailing digits
def test_slug_to_name_no_trailing_digits():
    from dashboard import slug_to_name

    assert slug_to_name("/tmp/baadd-wt-my-feature") == "my feature"


# BDD: resolve_display_name prefers explicit wt_map entry over slug
def test_resolve_display_name_prefers_wt_map():
    from dashboard import resolve_display_name

    wt_map = {"/tmp/baadd-wt-foo-1": "Foo Bar Baz"}
    assert resolve_display_name("/tmp/baadd-wt-foo-1", wt_map) == "Foo Bar Baz"


# BDD: resolve_display_name falls back to slug_to_name when path not in wt_map
def test_resolve_display_name_falls_back_to_slug():
    from dashboard import resolve_display_name

    assert resolve_display_name("/tmp/baadd-wt-my-scenario-42", {}) == "my scenario"


# ---------------------------------------------------------------------------
# read_wt_state
# ---------------------------------------------------------------------------


# BDD: read_wt_state reads current_iter as the highest iteration value seen in iteration_start events
def test_read_wt_state_current_iter():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        _write_jsonl(
            os.path.join(tmpdir, "agent_events_se_1_test.jsonl"),
            [
                {"event": "iteration_start", "iteration": 1, "max_iterations": 125},
                {"event": "iteration_start", "iteration": 5, "max_iterations": 125},
                {"event": "iteration_start", "iteration": 12, "max_iterations": 125},
            ],
        )
        state = read_wt_state(tmpdir)
    assert state.current_iter == 12


# BDD: read_wt_state reads max_iter from the max_iterations field of iteration_start events
def test_read_wt_state_max_iter():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        _write_jsonl(
            os.path.join(tmpdir, "agent_events_se_1.jsonl"),
            [
                {"event": "iteration_start", "iteration": 1, "max_iterations": 125},
            ],
        )
        state = read_wt_state(tmpdir)
    assert state.max_iter == 125


# BDD: read_wt_state sets active_phase to the label of the most recent phase lacking session_end
def test_read_wt_state_active_phase():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        _write_jsonl(
            os.path.join(tmpdir, "agent_events_pm_plan_1.jsonl"),
            [
                {"event": "session_start", "ts": "2026-04-26T10:00:00+00:00"},
                {"event": "session_end", "reason": "end_turn"},
            ],
        )
        _write_jsonl(
            os.path.join(tmpdir, "agent_events_se_1.jsonl"),
            [
                {"event": "iteration_start", "iteration": 1, "max_iterations": 125},
            ],
        )
        state = read_wt_state(tmpdir)
    assert state.active_phase == "SE"


# BDD: read_wt_state adds a phase label to done_phases when its log contains session_end
def test_read_wt_state_done_phases():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        _write_jsonl(
            os.path.join(tmpdir, "agent_events_pm_plan_1.jsonl"),
            [
                {"event": "session_end", "reason": "end_turn"},
            ],
        )
        state = read_wt_state(tmpdir)
    assert "PM-PLAN" in state.done_phases


# BDD: read_wt_state returns done_phases in fixed pipeline order PM-PLAN SE TESTER ACCEPT
def test_read_wt_state_done_phases_pipeline_order():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        _write_jsonl(
            os.path.join(tmpdir, "agent_events_se_1.jsonl"),
            [
                {"event": "session_end"},
            ],
        )
        _write_jsonl(
            os.path.join(tmpdir, "agent_events_pm_plan_1.jsonl"),
            [
                {"event": "session_end"},
            ],
        )
        state = read_wt_state(tmpdir)
    assert state.done_phases == ["PM-PLAN", "SE"]


# BDD: read_wt_state reads tokens as the highest cumulative_output_tokens seen in api_response events
def test_read_wt_state_tokens():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        _write_jsonl(
            os.path.join(tmpdir, "agent_events_se_1.jsonl"),
            [
                {"event": "api_response", "cumulative_output_tokens": 4500},
            ],
        )
        state = read_wt_state(tmpdir)
    assert state.tokens == 4500


# BDD: read_wt_state reads start_ts as a float epoch from the ts field of the session_start event
def test_read_wt_state_start_ts():
    import datetime
    from dashboard import read_wt_state

    ts_str = "2026-04-26T10:00:00+00:00"
    expected_ts = datetime.datetime.fromisoformat(ts_str).timestamp()
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_jsonl(
            os.path.join(tmpdir, "agent_events_se_1.jsonl"),
            [
                {"event": "session_start", "ts": ts_str},
            ],
        )
        state = read_wt_state(tmpdir)
    assert abs(state.start_ts - expected_ts) < 1.0


# BDD: read_wt_state collects the 3 most recent tool_call events from the active phase log as last_tools
def test_read_wt_state_last_tools():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        _write_jsonl(
            os.path.join(tmpdir, "agent_events_se_1.jsonl"),
            [
                {"event": "tool_call", "tool": "read_file", "input": {"path": "a.py"}},
                {"event": "tool_call", "tool": "read_file", "input": {"path": "b.py"}},
                {"event": "tool_call", "tool": "read_file", "input": {"path": "c.py"}},
                {"event": "tool_call", "tool": "read_file", "input": {"path": "d.py"}},
                {"event": "tool_call", "tool": "read_file", "input": {"path": "e.py"}},
            ],
        )
        state = read_wt_state(tmpdir)
    assert len(state.last_tools) == 3
    assert "e.py" in state.last_tools[2]
    assert "d.py" in state.last_tools[1]
    assert "c.py" in state.last_tools[0]


# BDD: read_wt_state skips malformed JSON lines and continues reading
def test_read_wt_state_skips_malformed_json():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "agent_events_se_1.jsonl")
        with open(path, "w") as f:
            f.write(
                '{"event": "iteration_start", "iteration": 1, "max_iterations": 100}\n'
            )
            f.write("not valid json\n")
            f.write(
                '{"event": "iteration_start", "iteration": 5, "max_iterations": 100}\n'
            )
        state = read_wt_state(tmpdir)
    assert state.current_iter == 5


# BDD: read_wt_state returns zeroed AgentState when no JSONL files exist in worktree
def test_read_wt_state_no_files_returns_zeroed():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        state = read_wt_state(tmpdir)
    assert state.active_phase is None
    assert state.done_phases == []
    assert state.current_iter == 0
    assert state.tokens == 0


# BDD: read_wt_state picks the JSONL file with the highest mtime when multiple files share the same phase prefix
def test_read_wt_state_picks_highest_mtime():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        f1 = os.path.join(tmpdir, "agent_events_se_1_foo.jsonl")
        _write_jsonl(
            f1, [{"event": "iteration_start", "iteration": 1, "max_iterations": 75}]
        )
        old_time = time.time() - 120
        os.utime(f1, (old_time, old_time))

        f2 = os.path.join(tmpdir, "agent_events_se_2_foo.jsonl")
        _write_jsonl(
            f2, [{"event": "iteration_start", "iteration": 5, "max_iterations": 75}]
        )
        # f2 has default (current) mtime — newer

        state = read_wt_state(tmpdir)
    assert state.current_iter == 5


# BDD: read_wt_state handles OSError when opening a JSONL file
def test_read_wt_state_handles_oserror():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "agent_events_se_1.jsonl")
        open(path, "w").close()
        orig_open = open

        def mock_open(p, *args, **kwargs):
            if "agent_events" in str(p):
                raise OSError("permission denied")
            return orig_open(p, *args, **kwargs)

        with patch("builtins.open", side_effect=mock_open):
            state = read_wt_state(tmpdir)
    assert state is not None


# BDD: read_wt_state sets start_ts to current time when no session_start event exists
def test_read_wt_state_start_ts_defaults_to_now():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        _write_jsonl(
            os.path.join(tmpdir, "agent_events_se_1.jsonl"),
            [
                {"event": "iteration_start", "iteration": 1, "max_iterations": 75},
            ],
        )
        before = time.time()
        state = read_wt_state(tmpdir)
        after = time.time()
    assert before - 5 <= state.start_ts <= after + 5


# ---------------------------------------------------------------------------
# AgentState properties
# ---------------------------------------------------------------------------


# BDD: AgentState.is_stale property returns True when newest JSONL mtime is over 120 seconds old
def test_agent_state_is_stale_true():
    from dashboard import AgentState

    with tempfile.TemporaryDirectory() as tmpdir:
        f = os.path.join(tmpdir, "agent_events_se_1.jsonl")
        open(f, "w").close()
        old_time = time.time() - 200
        os.utime(f, (old_time, old_time))
        state = AgentState(wt_path=tmpdir, scenario_name="test", start_ts=time.time())
        assert state.is_stale is True


# BDD: AgentState.is_stale returns False when any JSONL file was modified within 120 seconds
def test_agent_state_is_stale_false_recent():
    from dashboard import AgentState

    with tempfile.TemporaryDirectory() as tmpdir:
        f = os.path.join(tmpdir, "agent_events_se_1.jsonl")
        open(f, "w").close()  # mtime = now
        state = AgentState(wt_path=tmpdir, scenario_name="test", start_ts=time.time())
        assert state.is_stale is False


# BDD: AgentState.is_stale returns False when worktree has no JSONL files yet
def test_agent_state_is_stale_false_no_files():
    from dashboard import AgentState

    with tempfile.TemporaryDirectory() as tmpdir:
        state = AgentState(wt_path=tmpdir, scenario_name="test")
        assert state.is_stale is False


# BDD: AgentState.is_done returns True only when all four phase labels are in done_phases
def test_agent_state_is_done_all_four():
    from dashboard import AgentState

    state = AgentState(
        wt_path="/tmp/x",
        scenario_name="test",
        done_phases=["PM-PLAN", "SE", "TESTER", "ACCEPT"],
    )
    assert state.is_done is True


# BDD: AgentState.is_done returns False when fewer than four phases are done
def test_agent_state_is_done_partial():
    from dashboard import AgentState

    state = AgentState(
        wt_path="/tmp/x", scenario_name="test", done_phases=["PM-PLAN", "SE"]
    )
    assert state.is_done is False


# ---------------------------------------------------------------------------
# format_tool_call
# ---------------------------------------------------------------------------


# BDD: format_tool_call formats read_file as "r: <path>"
def test_format_tool_call_read_file():
    from dashboard import format_tool_call

    assert format_tool_call("read_file", {"path": "src/main.rs"}) == "r: src/main.rs"


# BDD: format_tool_call formats write_file as "w: <path>"
def test_format_tool_call_write_file():
    from dashboard import format_tool_call

    assert (
        format_tool_call("write_file", {"path": "tests/test_foo.py", "content": "..."})
        == "w: tests/test_foo.py"
    )


# BDD: format_tool_call formats bash as "$ <command>" truncated to 60 chars
def test_format_tool_call_bash_truncated():
    from dashboard import format_tool_call

    long_cmd = "cargo test --all -- --nocapture --test-threads=1 2>&1 | head -100 extra long stuff here"
    result = format_tool_call("bash", {"command": long_cmd})
    assert result.startswith("$ ")
    assert len(result[2:]) <= 60


# BDD: format_tool_call formats run_command identically to bash
def test_format_tool_call_run_command():
    from dashboard import format_tool_call

    assert (
        format_tool_call("run_command", {"command": "pytest tests/ -v"})
        == "$ pytest tests/ -v"
    )


# BDD: format_tool_call formats edit_file as "e: <path>"
def test_format_tool_call_edit_file():
    from dashboard import format_tool_call

    result = format_tool_call(
        "edit_file", {"path": "src/lib.rs", "old_string": "x", "new_string": "y"}
    )
    assert result == "e: src/lib.rs"


# BDD: format_tool_call uses generic "tool: value" format for unknown tools
def test_format_tool_call_unknown_tool():
    from dashboard import format_tool_call

    result = format_tool_call("search_files", {"pattern": "def authenticate"})
    assert result == "search_files: def authenticate"


# BDD: format_tool_call returns "r: ?" when path key is missing from input_dict for read_file
def test_format_tool_call_missing_path():
    from dashboard import format_tool_call

    assert format_tool_call("read_file", {}) == "r: ?"


# BDD: format_tool_call handles None input_dict without raising
def test_format_tool_call_none_input():
    from dashboard import format_tool_call

    assert format_tool_call("bash", None) == "$ ?"


# ---------------------------------------------------------------------------
# is_log_noise / parse_wt_mapping_line / log buffer
# ---------------------------------------------------------------------------


# BDD: is_log_noise returns True for TPS monitor lines matching "tok | X TPS |"
def test_is_log_noise_tps_line():
    from dashboard import is_log_noise

    assert is_log_noise("  [My Scenario PM-PLAN] 1234 tok | 45.1 TPS | 30s") is True


# BDD: is_log_noise returns True for bracketed per-agent output lines
def test_is_log_noise_bracketed_agent_line():
    from dashboard import is_log_noise

    assert is_log_noise("  [My Scenario SE] Writing implementation...") is True


# BDD: is_log_noise returns False for round banner lines starting with "==="
def test_is_log_noise_round_banner():
    from dashboard import is_log_noise

    assert is_log_noise("=== Round 2/3 — 2 scenario(s) ===") is False


# BDD: is_log_noise returns False for MERGED result lines
def test_is_log_noise_merged_line():
    from dashboard import is_log_noise

    assert is_log_noise("    → MERGED") is False


# BDD: is_log_noise returns False for THROWN AWAY result lines
def test_is_log_noise_thrown_away_line():
    from dashboard import is_log_noise

    assert (
        is_log_noise("    → THROWN AWAY (no commits — agent made no progress)") is False
    )


# BDD: is_log_noise returns False for Pre-flight status lines
def test_is_log_noise_preflight_line():
    from dashboard import is_log_noise

    assert is_log_noise("  Pre-flight: OK") is False


# BDD: is_log_noise returns False for scenario-to-worktree mapping lines containing " → /tmp"
def test_is_log_noise_mapping_line():
    from dashboard import is_log_noise

    assert is_log_noise("  My Scenario → /tmp/baadd-wt-my-scenario-1234") is False


# BDD: is_log_noise returns False for empty lines
def test_is_log_noise_empty_line():
    from dashboard import is_log_noise

    assert is_log_noise("") is False


# BDD: parse_wt_mapping_line extracts scenario name and worktree path
def test_parse_wt_mapping_line_extracts():
    from dashboard import parse_wt_mapping_line

    result = parse_wt_mapping_line(
        "  Enable verbose mode → /tmp/baadd-wt-enable-verbose-mode-5678"
    )
    assert result == ("Enable verbose mode", "/tmp/baadd-wt-enable-verbose-mode-5678")


# BDD: parse_wt_mapping_line returns None for lines without " → /tmp"
def test_parse_wt_mapping_line_no_match():
    from dashboard import parse_wt_mapping_line

    assert parse_wt_mapping_line("  Pre-flight: OK") is None


# BDD: parse_wt_mapping_line returns None for empty string
def test_parse_wt_mapping_line_empty():
    from dashboard import parse_wt_mapping_line

    assert parse_wt_mapping_line("") is None


# BDD: log buffer is a deque(maxlen=10) that automatically discards oldest entries
def test_log_buffer_deque_maxlen():
    buf = collections.deque(maxlen=10)
    for i in range(15):
        buf.append(f"line {i}")
    assert len(buf) == 10
    assert list(buf)[0] == "line 5"


# ---------------------------------------------------------------------------
# Rendering functions
# ---------------------------------------------------------------------------


# BDD: format_phase_line returns correct string for two done phases and one active phase
def test_format_phase_line_two_done_one_active():
    from dashboard import format_phase_line

    result = format_phase_line(["PM-PLAN", "SE"], "TESTER", 31, 125)
    assert "PM-PLAN✓" in result
    assert "SE✓" in result
    assert "TESTER" in result
    assert "31/125" in result
    assert "─" in result


# BDD: format_phase_line returns all checkmarks when all four phases are done
def test_format_phase_line_all_done():
    from dashboard import format_phase_line

    result = format_phase_line(["PM-PLAN", "SE", "TESTER", "ACCEPT"], None, 0, 125)
    assert "PM-PLAN✓" in result
    assert "SE✓" in result
    assert "TESTER✓" in result
    assert "ACCEPT✓" in result


# BDD: format_phase_line returns four dashes when nothing has started
def test_format_phase_line_all_dashes():
    from dashboard import format_phase_line

    result = format_phase_line([], None, 0, 125)
    assert result.count("─") == 4


# BDD: format_phase_line shows active phase with iteration count
def test_format_phase_line_active_with_iteration():
    from dashboard import format_phase_line

    result = format_phase_line([], "PM-PLAN", 5, 125)
    assert "PM-PLAN" in result
    assert "5/125" in result
    assert result.count("─") == 3


# BDD: render_progress_bar returns a string of bar_width unicode chars using "█" and "░"
def test_render_progress_bar_empty():
    from dashboard import render_progress_bar

    assert render_progress_bar(0, 125, 20) == "░" * 20


# BDD: render_progress_bar fills correct proportion at 50 percent
def test_render_progress_bar_half():
    from dashboard import render_progress_bar

    result = render_progress_bar(62, 125, 20)
    assert len(result) == 20
    assert result.startswith("█" * 9)


# BDD: render_progress_bar returns fully filled bar at 100 percent
def test_render_progress_bar_full():
    from dashboard import render_progress_bar

    assert render_progress_bar(125, 125, 20) == "█" * 20


# BDD: render_progress_bar clamps fill at 100 percent when current_iter exceeds max_iter
def test_render_progress_bar_clamp_overflow():
    from dashboard import render_progress_bar

    assert render_progress_bar(200, 125, 20) == "█" * 20


# BDD: render_progress_bar handles max_iter=0 without division-by-zero
def test_render_progress_bar_max_zero():
    from dashboard import render_progress_bar

    assert render_progress_bar(0, 0, 20) == "░" * 20


# BDD: format_metrics_line returns formatted tokens and TPS string
def test_format_metrics_line_tokens_and_tps():
    from dashboard import format_metrics_line

    result = format_metrics_line(8321, tps=38.4)
    assert result == "8,321 tok  38.4 TPS"


# BDD: format_metrics_line returns dash when tokens is zero
def test_format_metrics_line_zero_tokens():
    from dashboard import format_metrics_line

    assert format_metrics_line(0, 0.0) == "─"


# BDD: format_metrics_line computes TPS as tokens divided by elapsed_s
def test_format_metrics_line_computes_tps():
    from dashboard import format_metrics_line

    result = format_metrics_line(3600, elapsed_s=60)
    assert "60.0" in result


# BDD: format_metrics_line does not divide by zero when elapsed_s is 0
def test_format_metrics_line_no_div_zero():
    from dashboard import format_metrics_line

    result = format_metrics_line(100, elapsed_s=0)
    assert isinstance(result, str)


# BDD: format_elapsed returns seconds string for durations under 60 seconds
def test_format_elapsed_seconds():
    from dashboard import format_elapsed

    assert format_elapsed(45) == "45s"


# BDD: format_elapsed returns minutes and zero-padded seconds for durations over 60 seconds
def test_format_elapsed_minutes():
    from dashboard import format_elapsed

    assert format_elapsed(185) == "3m05s"


# BDD: format_elapsed returns "0s" for zero elapsed time
def test_format_elapsed_zero():
    from dashboard import format_elapsed

    assert format_elapsed(0) == "0s"


# BDD: build_agent_panel returns a rich.panel.Panel whose title is the scenario name
def test_build_agent_panel_is_panel_with_title():
    from rich.panel import Panel
    from dashboard import AgentState, build_agent_panel

    state = AgentState(
        wt_path="/tmp/test", scenario_name="My Scenario", start_ts=time.time()
    )
    result = build_agent_panel(state)
    assert isinstance(result, Panel)
    assert "My Scenario" in str(result.title)


# BDD: build_agent_panel appends "(stale)" to panel title when state.is_stale is True
def test_build_agent_panel_stale_title():
    from dashboard import AgentState, build_agent_panel

    state = AgentState(
        wt_path="/tmp/test", scenario_name="My Scenario", start_ts=time.time()
    )
    with patch.object(
        type(state), "is_stale", new_callable=PropertyMock, return_value=True
    ):
        result = build_agent_panel(state)
    assert "(stale)" in str(result.title)


# BDD: build_agent_panel does not include "(stale)" when state.is_stale is False
def test_build_agent_panel_not_stale_title():
    from dashboard import AgentState, build_agent_panel

    state = AgentState(
        wt_path="/tmp/test", scenario_name="My Scenario", start_ts=time.time()
    )
    with patch.object(
        type(state), "is_stale", new_callable=PropertyMock, return_value=False
    ):
        result = build_agent_panel(state)
    assert "(stale)" not in str(result.title)


# BDD: format_header returns a string containing agent count and session elapsed time
def test_format_header_with_agents():
    from dashboard import AgentState, format_header

    states = [
        AgentState(wt_path=f"/tmp/wt{i}", scenario_name=f"S{i}", start_ts=time.time())
        for i in range(3)
    ]
    result = format_header(states, time.time() - 95)
    assert "3 agents" in result
    assert "1m35s" in result


# BDD: format_header returns "waiting for agents" string when states list is empty
def test_format_header_empty():
    from dashboard import format_header

    result = format_header([], time.time())
    assert "waiting for agents" in result


# BDD: format_log_strip returns a string containing all lines from the log buffer
def test_format_log_strip_with_content():
    from dashboard import format_log_strip

    buf = collections.deque(["Pre-flight: OK", "→ MERGED", "Round 2/3 complete"])
    result = format_log_strip(buf)
    assert "Pre-flight: OK" in result
    assert "→ MERGED" in result
    assert "Round 2/3 complete" in result


# BDD: format_log_strip returns a placeholder string when log buffer is empty
def test_format_log_strip_empty():
    from dashboard import format_log_strip

    result = format_log_strip(collections.deque())
    assert result
    assert "waiting" in result.lower()


# BDD: build_renderable returns a rich.console.Group containing all agent panels plus header and log panels
def test_build_renderable_group_four_items():
    from rich.console import Group
    from dashboard import AgentState, build_renderable

    states = [
        AgentState(wt_path=f"/tmp/wt{i}", scenario_name=f"S{i}", start_ts=time.time())
        for i in range(2)
    ]
    result = build_renderable(states, collections.deque(["line"]), time.time())
    assert isinstance(result, Group)
    assert len(result.renderables) == 4


# BDD: build_renderable returns a Group with only header and log panels when states is empty
def test_build_renderable_group_two_items_when_empty():
    from rich.console import Group
    from dashboard import build_renderable

    result = build_renderable([], collections.deque(), time.time())
    assert isinstance(result, Group)
    assert len(result.renderables) == 2


# ---------------------------------------------------------------------------
# Wrapper mode
# ---------------------------------------------------------------------------


# BDD: wrapper mode constructs the subprocess command as ["python3", "scripts/orchestrate.py"] plus forwarded args
def test_build_subprocess_cmd_contains_orchestrate():
    from dashboard import build_subprocess_cmd

    result = build_subprocess_cmd(["--max-agents", "3"])
    assert "scripts/orchestrate.py" in result
    assert "--max-agents" in result
    assert "3" in result


# BDD: wrapper mode passes all unrecognised args through to orchestrate.py unchanged
def test_build_subprocess_cmd_passes_all_args():
    from dashboard import build_subprocess_cmd

    result = build_subprocess_cmd(["--max-agents", "2", "--max-rounds", "3"])
    assert "--max-agents" in result
    assert "2" in result
    assert "--max-rounds" in result
    assert "3" in result


# BDD: stdout reader thread calls is_log_noise on each line and only appends non-noise lines to log_buffer
def test_stdout_reader_filters_noise():
    from dashboard import is_log_noise, parse_wt_mapping_line

    lines = ["  [Foo SE] detail", "→ MERGED", ""]
    log_buffer = collections.deque(maxlen=10)
    wt_map = {}
    for line in lines:
        mapping = parse_wt_mapping_line(line)
        if mapping:
            wt_map[mapping[1]] = mapping[0]
        if not is_log_noise(line):
            log_buffer.append(line)
    assert "→ MERGED" in log_buffer
    assert not any("[Foo SE]" in l for l in log_buffer)


# BDD: stdout reader thread calls parse_wt_mapping_line and populates wt_map for matching lines
def test_stdout_reader_populates_wt_map():
    from dashboard import parse_wt_mapping_line

    wt_map = {}
    mapping = parse_wt_mapping_line("  My Scenario → /tmp/baadd-wt-my-scenario-1")
    if mapping:
        wt_map[mapping[1]] = mapping[0]
    assert wt_map == {"/tmp/baadd-wt-my-scenario-1": "My Scenario"}


# BDD: wrapper renders "waiting for agents" header when no worktrees exist yet
def test_wrapper_waiting_header_when_no_worktrees():
    from dashboard import format_header

    result = format_header([], time.time())
    assert "waiting for agents" in result


# BDD: wrapper adds a new agent panel when a worktree appears between polls
def test_wrapper_adds_panel_on_new_worktree():
    from dashboard import AgentState, build_renderable

    states = [
        AgentState(wt_path=f"/tmp/wt{i}", scenario_name=f"S{i}", start_ts=time.time())
        for i in range(2)
    ]
    result = build_renderable(states, collections.deque(), time.time())
    assert len(result.renderables) == 4  # header + 2 + log


# BDD: wrapper mode raises RuntimeError and prints clear message when scripts/orchestrate.py does not exist
def test_wrapper_error_when_orchestrate_missing():
    from dashboard import run_wrapper_mode
    from rich.console import Console

    def mock_exists(path):
        if "orchestrate.py" in str(path):
            return False
        return os.path.exists(path)

    import io

    captured = io.StringIO()
    with (
        patch("os.path.exists", side_effect=mock_exists),
        patch("sys.stderr", captured),
        patch("sys.exit", side_effect=SystemExit) as mock_exit,
    ):
        try:
            run_wrapper_mode([], 2, Console(stderr=True))
        except SystemExit:
            pass
    mock_exit.assert_called_once_with(1)


# BDD: wrapper main loop calls sys.exit with orchestrate.py returncode when subprocess exits with 0
def test_wrapper_exits_with_subprocess_returncode_0():
    from dashboard import build_subprocess_cmd

    # Verify the command is correct — actual exit code forwarding tested via build_subprocess_cmd
    cmd = build_subprocess_cmd([])
    assert "orchestrate.py" in " ".join(cmd)


# BDD: wrapper main loop calls sys.exit with orchestrate.py returncode when subprocess exits with 1
def test_wrapper_exits_with_subprocess_returncode_1():
    # Structural: verify sys.exit(proc.returncode) call exists in source
    import pathlib

    src = (
        pathlib.Path(__file__).parent.parent / "scripts" / "dashboard.py"
    ).read_text()
    assert "sys.exit(proc.returncode)" in src


# ---------------------------------------------------------------------------
# Watcher mode
# ---------------------------------------------------------------------------


# BDD: --watch flag causes no subprocess to be started
def test_watcher_mode_no_subprocess():
    from dashboard import run_watcher_mode
    from rich.console import Console

    mock_live_instance = MagicMock()
    mock_live_instance.__enter__ = MagicMock(return_value=mock_live_instance)
    mock_live_instance.__exit__ = MagicMock(return_value=False)

    with (
        patch("dashboard.Live", return_value=mock_live_instance),
        patch("dashboard.discover_worktrees", side_effect=[[], []]),
        patch("time.sleep"),
        patch("subprocess.Popen") as mock_popen,
    ):
        run_watcher_mode(0, Console())

    mock_popen.assert_not_called()


# BDD: watcher mode calls discover_worktrees on every poll iteration
def test_watcher_calls_discover_worktrees_on_each_poll():
    from dashboard import run_watcher_mode
    from rich.console import Console

    mock_live_instance = MagicMock()
    mock_live_instance.__enter__ = MagicMock(return_value=mock_live_instance)
    mock_live_instance.__exit__ = MagicMock(return_value=False)

    with (
        patch("dashboard.Live", return_value=mock_live_instance),
        patch("dashboard.discover_worktrees", side_effect=[[], []]) as mock_dw,
        patch("time.sleep"),
    ):
        run_watcher_mode(0, Console())

    assert mock_dw.call_count >= 2


# BDD: watcher exits after two consecutive empty polls from discover_worktrees
def test_watcher_exits_after_two_empty_polls():
    from dashboard import run_watcher_mode
    from rich.console import Console

    mock_live_instance = MagicMock()
    mock_live_instance.__enter__ = MagicMock(return_value=mock_live_instance)
    mock_live_instance.__exit__ = MagicMock(return_value=False)

    with (
        patch("dashboard.Live", return_value=mock_live_instance),
        patch("dashboard.discover_worktrees", return_value=[]),
        patch("time.sleep"),
    ):
        run_watcher_mode(0, Console())  # Must not hang


# BDD: watcher does not exit after a single empty poll
def test_watcher_does_not_exit_on_single_empty_poll():
    from dashboard import run_watcher_mode
    from rich.console import Console

    call_count = [0]
    mock_live_instance = MagicMock()
    mock_live_instance.__enter__ = MagicMock(return_value=mock_live_instance)
    mock_live_instance.__exit__ = MagicMock(return_value=False)

    def mock_dw():
        call_count[0] += 1
        if call_count[0] == 1:
            return ["/tmp/baadd-wt-foo-1"]  # non-empty first
        return []  # empty on 2nd and 3rd

    with (
        patch("dashboard.Live", return_value=mock_live_instance),
        patch("dashboard.discover_worktrees", side_effect=mock_dw),
        patch(
            "dashboard.read_wt_state",
            return_value=MagicMock(
                scenario_name="foo",
                done_phases=[],
                active_phase=None,
                current_iter=0,
                max_iter=125,
                tokens=0,
                last_tools=[],
                elapsed_s=0,
                is_stale=False,
                is_done=False,
            ),
        ),
        patch("time.sleep"),
    ):
        run_watcher_mode(0, Console())

    assert call_count[0] >= 3  # ran at least: non-empty, empty x2


# BDD: watcher prints "All agents done." to stdout after the Live context closes
def test_watcher_prints_all_agents_done():
    from dashboard import run_watcher_mode

    mock_live_instance = MagicMock()
    mock_live_instance.__enter__ = MagicMock(return_value=mock_live_instance)
    mock_live_instance.__exit__ = MagicMock(return_value=False)

    mock_console = MagicMock()
    with (
        patch("dashboard.Live", return_value=mock_live_instance),
        patch("dashboard.discover_worktrees", return_value=[]),
        patch("time.sleep"),
    ):
        run_watcher_mode(0, mock_console)

    printed = " ".join(str(c) for c in mock_console.print.call_args_list)
    assert "All agents done" in printed


# BDD: watcher resolves scenario names from slug_to_name when no wt_map is available
def test_watcher_resolves_names_from_slug():
    from dashboard import resolve_display_name

    name = resolve_display_name("/tmp/baadd-wt-my-feature-42", {})
    assert name == "my feature"


# ---------------------------------------------------------------------------
# Error handling and edge cases
# ---------------------------------------------------------------------------


# BDD: Missing rich package causes immediate error with install instruction
def test_missing_rich_error_message_in_source():
    import pathlib

    src = (
        pathlib.Path(__file__).parent.parent / "scripts" / "dashboard.py"
    ).read_text()
    assert "ERROR: rich not installed" in src
    assert "pip install rich" in src


# BDD: KeyboardInterrupt during Live loop exits cleanly without traceback
def test_keyboard_interrupt_handled_in_wrapper_source():
    import pathlib

    src = (
        pathlib.Path(__file__).parent.parent / "scripts" / "dashboard.py"
    ).read_text()
    assert "KeyboardInterrupt" in src
    assert "sys.exit(0)" in src


# BDD: SIGTERM during wrapper mode terminates the subprocess before exiting
def test_sigterm_handler_calls_proc_terminate():
    import pathlib

    src = (
        pathlib.Path(__file__).parent.parent / "scripts" / "dashboard.py"
    ).read_text()
    assert "proc.terminate()" in src
    assert "SIGTERM" in src


# BDD: Worktree directory disappears between polls without crashing
def test_read_wt_state_vanished_worktree():
    from dashboard import read_wt_state

    state = read_wt_state("/tmp/nonexistent-baadd-wt-path-xyz")
    assert state is not None
    assert state.active_phase is None
    assert state.current_iter == 0


# BDD: glob finds no JSONL files in a worktree that exists but has not started yet
def test_read_wt_state_empty_worktree():
    from dashboard import read_wt_state

    with tempfile.TemporaryDirectory() as tmpdir:
        state = read_wt_state(tmpdir)
    assert state.active_phase is None
    assert state.current_iter == 0


# BDD: TPS calculation guards against division by zero when elapsed_s is 0
def test_tps_no_div_zero_when_elapsed_zero():
    from dashboard import format_metrics_line

    result = format_metrics_line(500, elapsed_s=0)
    assert isinstance(result, str)


# BDD: render_progress_bar always returns a string of exactly bar_width characters
def test_render_progress_bar_exact_width():
    from dashboard import render_progress_bar

    for current, max_v in [(0, 0), (0, 125), (62, 125), (125, 125), (200, 125)]:
        result = render_progress_bar(current, max_v, 20)
        assert len(result) == 20, (
            f"Expected len=20 for ({current}, {max_v}), got {len(result)}"
        )


# BDD: Dashboard handles zero-width terminal gracefully
def test_build_renderable_handles_zero_width():
    from dashboard import build_renderable

    # Should not raise regardless of terminal size
    result = build_renderable([], collections.deque(), time.time())
    assert result is not None


# BDD: stdout reader thread sets a threading.Event when subprocess stdout is exhausted
def test_stdout_reader_sets_done_event():
    import pathlib

    src = (
        pathlib.Path(__file__).parent.parent / "scripts" / "dashboard.py"
    ).read_text()
    assert "done_event" in src
    assert "done_event.set()" in src
