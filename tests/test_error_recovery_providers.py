#!/usr/bin/env python3
"""Tests for Error Recovery scenarios — provider defaults, tool formatting, wrap-up, slug."""

import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))


def _agent_src():
    with open(os.path.join(ROOT, "scripts", "agent.py")) as f:
        return f.read()


def _evolve_src():
    with open(os.path.join(ROOT, "scripts", "evolve.sh")) as f:
        return f.read()


# ── Provider default models ────────────────────────────────────────────────────

# BDD: Moonshot default model
def test_moonshot_default_model():
    import agent
    assert agent.PROVIDER_CONFIGS["moonshot"]["default_model"] == "kimi-latest"


# BDD: Dashscope default model
def test_dashscope_default_model():
    import agent
    assert agent.PROVIDER_CONFIGS["dashscope"]["default_model"] == "qwen-max"


# BDD: Groq default model
def test_groq_default_model():
    import agent
    assert agent.PROVIDER_CONFIGS["groq"]["default_model"] == "llama-3.3-70b-versatile"


# BDD: Ollama default model
def test_ollama_default_model():
    import agent
    assert agent.PROVIDER_CONFIGS["ollama"]["default_model"] == "llama3.2"


# ── API key placeholders ───────────────────────────────────────────────────────

# BDD: Ollama provider uses "ollama" as api_key
def test_ollama_uses_ollama_as_api_key():
    content = _agent_src()
    assert 'api_key = "ollama"' in content


# BDD: Custom provider requires api_key string placeholder
def test_custom_provider_uses_custom_as_api_key():
    content = _agent_src()
    assert 'api_key = "custom"' in content


# ── Tool output formatting ─────────────────────────────────────────────────────

# BDD: Tool output formatting with iteration tag
def test_iteration_tag_format():
    import agent
    # print_tool_call builds iter_tag as "[iter/max] "
    # Verify the format string in source
    content = _agent_src()
    assert '[{iteration}/{max_iterations}]' in content or "f\"[{iteration}/{max_iterations}]" in content


# BDD: Tool output formatting with iteration tag
def test_print_tool_call_includes_iter_tag():
    import agent
    import io
    from unittest.mock import patch
    buf = io.StringIO()
    with patch("builtins.print", side_effect=lambda *a, **kw: buf.write(str(a[0]) + "\n")):
        agent.print_tool_call("bash", {"command": "ls"}, "file.txt", iteration=25, max_iterations=75)
    output = buf.getvalue()
    assert "25/75" in output


# BDD: Tool icons for different tool types
def test_tool_icons_defined():
    import agent
    icons = agent.TOOL_ICONS
    assert icons["bash"] == "$"
    assert icons["read_file"] == "<-"
    assert icons["write_file"] == "->"
    assert icons["edit_file"] == "~~"
    assert icons["search_files"] == "??"


# ── Wrap-up message content ────────────────────────────────────────────────────

# BDD: Mode flag affects wrap-up message content
def test_bootstrap_mode_wrap_up_mentions_initialized():
    import agent
    msg = agent.make_wrap_up_message(70, 100, "bootstrap")
    assert ".baadd_initialized" in msg


# BDD: Mode flag affects wrap-up message content
def test_bootstrap_mode_wrap_up_mentions_journal():
    import agent
    msg = agent.make_wrap_up_message(70, 100, "bootstrap")
    assert "journal" in msg.lower() or "JOURNAL" in msg


# BDD: Mode flag affects wrap-up message content
def test_evolve_mode_wrap_up_differs_from_bootstrap():
    import agent
    bootstrap_msg = agent.make_wrap_up_message(70, 100, "bootstrap")
    evolve_msg = agent.make_wrap_up_message(70, 100, "evolve")
    assert bootstrap_msg != evolve_msg


# ── Scenario slug with special characters ─────────────────────────────────────

# BDD: Handle scenario with special characters in name
def test_scenario_slug_replaces_special_chars():
    r = subprocess.run(
        ["bash", "-c",
         r'''echo "Login with email (user@example.com)" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//' | cut -c1-60'''],
        capture_output=True, text=True, timeout=10
    )
    slug = r.stdout.strip()
    assert slug == "login-with-email-user-example-com"


# BDD: Handle scenario with special characters in name
def test_scenario_slug_logic_in_evolve_sh():
    content = _evolve_src()
    assert "scenario_to_slug" in content
    assert "[^a-z0-9]" in content
    assert "cut -c1-60" in content


# ── Concurrent scenario locks ──────────────────────────────────────────────────

# BDD: Handle concurrent scenario locks
def test_lock_files_use_scenario_slug():
    content = _evolve_src()
    assert "LOCKS_DIR" in content
    assert ".lock" in content
    assert "slug" in content


# BDD: Handle concurrent scenario locks
def test_lock_file_noclobber_prevents_race():
    content = _evolve_src()
    assert "noclobber" in content


# BDD: Handle concurrent scenario locks
def test_each_scenario_has_unique_lock_file():
    # Verify slug derivation produces different locks for different scenarios
    scenarios = [
        "Never modify IDENTITY.md",
        "Never modify scripts/evolve.sh",
        "Never modify .github/workflows/",
    ]
    slugs = set()
    for s in scenarios:
        r = subprocess.run(
            ["bash", "-c",
             rf'''echo "{s}" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//' | cut -c1-60'''],
            capture_output=True, text=True
        )
        slugs.add(r.stdout.strip())
    assert len(slugs) == 3
