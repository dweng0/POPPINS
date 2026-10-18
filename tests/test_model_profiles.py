#!/usr/bin/env python3
"""Tests for named model profiles in poppins.yml"""

import os
import subprocess
import sys
import textwrap

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import parse_poppins_config as ppc
from model_profiles import ProfileError, profile_to_agent_cfg, resolve_profile

YML = textwrap.dedent(
    """\
    models:
      fast:
        model_name: gpt-fast
        api_type: openai-completions
        base_url: https://openrouter.ai/api/v1
        api_key: sk-plain
        max_tokens: 4096
        max_context_window: 32000
      smart:
        model_name: claude-smart
        api_type: anthropic-messages
        base_url: https://proxy.example.com
        api_key_env: MY_KEY
        max_tokens: 8000
        max_context_window: 200000
    active_model: smart
    agent:
      max_iterations: 10
    """
)


def _load(tmp_path, text=YML):
    p = tmp_path / "poppins.yml"
    p.write_text(text)
    return ppc.deep_merge(ppc.DEFAULTS, ppc.parse_yaml_simple(str(p)))


# BDD: Load named model profiles from poppins.yml
def test_load_named_model_profiles(tmp_path):
    cfg = _load(tmp_path)
    assert set(cfg["models"]) == {"fast", "smart"}
    fast = cfg["models"]["fast"]
    assert fast["model_name"] == "gpt-fast"
    assert fast["api_type"] == "openai-completions"
    assert fast["base_url"] == "https://openrouter.ai/api/v1"
    assert fast["max_tokens"] == 4096
    assert fast["max_context_window"] == 32000
    assert cfg["active_model"] == "smart"
    assert cfg["agent"]["max_iterations"] == 10


# BDD: Select the active model profile
def test_select_active_profile(tmp_path):
    cfg = _load(tmp_path)
    assert resolve_profile(cfg)["name"] == "smart"
    assert resolve_profile(cfg, "fast")["name"] == "fast"


# BDD: Unknown active model fails clearly
def test_unknown_active_model_fails_clearly(tmp_path):
    cfg = _load(tmp_path, YML.replace("active_model: smart", "active_model: nope"))
    with pytest.raises(ProfileError) as exc:
        resolve_profile(cfg)
    msg = str(exc.value)
    assert "nope" in msg and "fast" in msg and "smart" in msg


# BDD: Default base_url from api_type
def test_default_base_url_from_api_type():
    cfg = {"models": {"m": {"model_name": "x", "api_type": "openai-completions"}}}
    assert resolve_profile(cfg, "m")["base_url"] == "https://api.openai.com/v1"


# BDD: Custom base_url for an OpenAI-compatible endpoint
def test_custom_base_url_openai_client(tmp_path):
    cfg = _load(tmp_path)
    agent_cfg = profile_to_agent_cfg(resolve_profile(cfg, "fast"))
    assert agent_cfg["provider"] == "custom"
    assert agent_cfg["base_url"] == "https://openrouter.ai/api/v1"
    assert agent_cfg["default_model"] == "gpt-fast"


# BDD: Custom base_url for an Anthropic-compatible endpoint
def test_custom_base_url_anthropic_client(tmp_path, monkeypatch):
    cfg = _load(tmp_path)
    agent_cfg = profile_to_agent_cfg(resolve_profile(cfg, "smart"))
    assert agent_cfg["provider"] == "anthropic"
    import types

    seen = {}
    fake = types.SimpleNamespace(
        Anthropic=lambda **kw: seen.update(kw) or (_ for _ in ()).throw(StopIteration)
    )
    monkeypatch.setitem(sys.modules, "anthropic", fake)
    import agent

    with pytest.raises(StopIteration):
        agent.run_anthropic_loop(
            "k", "m", "sys", "p", "evolve", None, base_url=agent_cfg["base_url"]
        )
    assert seen["base_url"] == "https://proxy.example.com"


# BDD: Resolve the API key from an environment variable
def test_api_key_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("MY_KEY", "from-env")
    assert resolve_profile(_load(tmp_path), "smart")["api_key"] == "from-env"


# BDD: Plaintext api_key is used when no environment variable is set
def test_plaintext_api_key(tmp_path):
    assert resolve_profile(_load(tmp_path), "fast")["api_key"] == "sk-plain"


# BDD: Per-profile max_tokens limits the response size
def test_per_profile_max_tokens(tmp_path):
    (tmp_path / "poppins.yml").write_text(
        YML.replace("active_model: smart", "active_model: fast")
    )
    out = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.path.insert(0,'/home/jay/projects/POPPINS/scripts'); import agent; print(agent.MAX_TOKENS)",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert out.stdout.strip().splitlines()[-1] == "4096", out.stderr


# BDD: Per-profile max_context_window triggers context trimming
def test_per_profile_max_context_window(tmp_path):
    (tmp_path / "poppins.yml").write_text(
        YML.replace("active_model: smart", "active_model: fast")
    )
    out = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.path.insert(0,'/home/jay/projects/POPPINS/scripts'); import agent; print(agent.CONTEXT_WINDOW_LIMIT)",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert out.stdout.strip().splitlines()[-1] == "32000", out.stderr


# BDD: Legacy flat config still works
def test_legacy_flat_config():
    cfg = {
        "agent": {
            "provider": "custom",
            "base_url": "http://localhost:1234/v1",
            "default_model": "qwen",
        }
    }
    p = resolve_profile(cfg)
    assert p["model_name"] == "qwen"
    assert p["base_url"] == "http://localhost:1234/v1"
    assert p["api_type"] == "openai-completions"
    assert p["source"] == "legacy"


# BDD: Command-line model overrides the active profile
def test_cli_model_overrides_profile(tmp_path):
    (tmp_path / "poppins.yml").write_text(
        YML.replace("active_model: smart", "active_model: fast")
    )
    code = (
        "import sys; sys.path.insert(0,'/home/jay/projects/POPPINS/scripts');"
        "import os; import agent;"
        "print(os.environ['CUSTOM_BASE_URL'], os.environ['CUSTOM_MODEL'])"
    )
    env = {k: v for k, v in os.environ.items() if not k.startswith("CUSTOM_")}
    out = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
    )
    assert (
        out.stdout.strip().splitlines()[-1] == "https://openrouter.ai/api/v1 gpt-fast"
    ), out.stderr
    # --model wins over CUSTOM_MODEL at resolution time (agent.main uses args.model first)
    src = open("/home/jay/projects/POPPINS/scripts/agent.py").read()
    assert "if args.model:\n        model = args.model" in src


# BDD: Orchestrator uses a configurable model profile
def test_orchestrator_profile(tmp_path):
    from model_profiles import resolve_orchestrator_profile

    cfg = _load(tmp_path)
    assert resolve_orchestrator_profile(cfg)["name"] == "smart"  # falls back to active
    cfg["orchestration"]["model"] = "fast"
    assert resolve_orchestrator_profile(cfg)["name"] == "fast"
