"""Tests for scripts/dashboard.py — Rich TUI dashboard for orchestrate.py."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


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
    assert callable(getattr(dashboard, "main", None)), "dashboard.py must define a main() function"


# BDD: AgentState is a dataclass with the required fields
def test_agentstate_is_a_dataclass_with_the_required_fields():
    import dataclasses
    from dashboard import AgentState
    assert dataclasses.is_dataclass(AgentState), "AgentState must be decorated with @dataclass"
    field_names = {f.name for f in dataclasses.fields(AgentState)}
    expected = {"wt_path", "scenario_name", "active_phase", "done_phases", "current_iter", "max_iter", "tokens", "last_tools", "start_ts"}
    assert field_names == expected, f"Expected fields {expected}, got {field_names}"


# BDD: Rich is the only third-party import in dashboard.py
def test_dashboard_only_imports_rich():
    import ast, pathlib
    src = (pathlib.Path(__file__).parent.parent / "scripts" / "dashboard.py").read_text()
    tree = ast.parse(src)
    stdlib_and_allowed = {
        "os", "sys", "re", "json", "time", "threading", "subprocess",
        "argparse", "signal", "collections", "dataclasses", "typing",
        "datetime", "glob", "pathlib", "rich",
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
