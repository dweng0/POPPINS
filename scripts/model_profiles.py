#!/usr/bin/env python3
"""
Named model profiles from poppins.yml.

A profile bundles everything needed to talk to one model endpoint:
model_name, api_type, base_url, api_key, max_tokens, max_context_window.
Several can be defined under `models:`; `active_model` picks the one in use.
When no `models:` map exists, an equivalent profile is built from the legacy
flat `agent:` keys (provider, base_url, api_key, default_model).
"""

import os

API_TYPES = ("openai-completions", "anthropic-messages")

DEFAULT_BASE_URLS = {
    "openai-completions": "https://api.openai.com/v1",
    "anthropic-messages": "https://api.anthropic.com",
}


class ProfileError(Exception):
    pass


def _build(name, raw, source):
    api_type = raw.get("api_type") or "openai-completions"
    if api_type not in API_TYPES:
        raise ProfileError(
            f"Profile '{name}': unknown api_type '{api_type}'. Valid: {', '.join(API_TYPES)}"
        )
    api_key = raw.get("api_key") or None
    key_env = raw.get("api_key_env")
    if key_env and os.environ.get(key_env):
        api_key = os.environ[key_env]
    return {
        "name": name,
        "source": source,
        "model_name": raw.get("model_name"),
        "api_type": api_type,
        "base_url": raw.get("base_url") or DEFAULT_BASE_URLS[api_type],
        "api_key": api_key,
        "max_tokens": raw.get("max_tokens"),
        "max_context_window": raw.get("max_context_window"),
    }


def _legacy(cfg):
    agent = cfg.get("agent", {})
    api_type = (
        "anthropic-messages"
        if agent.get("provider") == "anthropic"
        else "openai-completions"
    )
    profile = _build(
        "legacy",
        {
            "model_name": agent.get("default_model"),
            "api_type": api_type,
            "base_url": agent.get("base_url"),
            "api_key": agent.get("api_key"),
            "max_tokens": agent.get("max_tokens_per_response"),
            "max_context_window": agent.get("context_window_limit"),
        },
        "legacy",
    )
    # legacy configs never defaulted base_url from the api_type
    profile["base_url"] = agent.get("base_url")
    return profile


def resolve_profile(cfg, name=None):
    """Return the profile dict for `name`, else active_model, else the legacy one.

    Raises ProfileError when the requested profile is not defined.
    """
    models = cfg.get("models")
    if not isinstance(models, dict) or not models:
        if name:
            raise ProfileError(f"Unknown model profile '{name}'. Defined: (none)")
        return _legacy(cfg)
    chosen = name or cfg.get("active_model") or next(iter(models))
    if chosen not in models or not isinstance(models[chosen], dict):
        raise ProfileError(
            f"Unknown model profile '{chosen}'. Defined: {', '.join(models)}"
        )
    return _build(chosen, models[chosen], "models")


def resolve_orchestrator_profile(cfg):
    """Profile named by orchestration.model, falling back to the active one."""
    return resolve_profile(cfg, cfg.get("orchestration", {}).get("model") or None)


def profile_to_agent_cfg(profile):
    """Translate a profile into the provider/base_url/api_key/default_model keys agent.py applies."""
    return {
        "provider": "anthropic"
        if profile["api_type"] == "anthropic-messages"
        else "custom",
        "base_url": profile["base_url"],
        "api_key": profile["api_key"],
        "default_model": profile["model_name"],
    }
