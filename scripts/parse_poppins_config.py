#!/usr/bin/env python3
"""
Parse poppins.yml and output either shell variable assignments or JSON.

Usage:
    # Shell mode (default) — for sourcing in bash:
    eval "$(python3 scripts/parse_poppins_config.py)"

    # JSON mode — for reading in Python:
    python3 scripts/parse_poppins_config.py --json

    # Get a single value:
    python3 scripts/parse_poppins_config.py --get agent.max_iterations

Searches for poppins.yml in the current directory, then parent directories.
Falls back to built-in defaults if the file is missing.
"""

import sys
import os
import json
import re

DEFAULTS = {
    "orchestration": {
        "max_parallel_agents": 3,
        "model_orchestrator": "claude-haiku-4-5-20251001",
    },
    "agent": {
        "max_iterations": 75,
        "wrap_up_at": 70,
        "max_tokens_per_response": 8192,
        "tool_output_limit": 12000,
        "session_timeout": 3600,
        "context_window_limit": 100000,
        "default_model": "claude-haiku-4-5-20251001",
    },
}


def find_config():
    """Search for poppins.yml starting from cwd, walking up."""
    d = os.getcwd()
    while True:
        candidate = os.path.join(d, "poppins.yml")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def parse_yaml_simple(path):
    """Minimal YAML parser for flat/one-level-nested key: value files.
    Avoids requiring PyYAML as a dependency."""
    result = {}
    current_section = None

    with open(path) as f:
        for line in f:
            stripped = line.rstrip()

            if not stripped or stripped.lstrip().startswith("#"):
                continue

            indent = len(line) - len(line.lstrip())

            if indent == 0 and stripped.endswith(":"):
                current_section = stripped[:-1].strip()
                result[current_section] = {}
                continue

            if ":" in stripped:
                key, _, value = stripped.partition(":")
                key = key.strip()
                value = value.strip()

                if value.startswith("#"):
                    value = ""
                elif "#" in value:
                    value = value[:value.index("#")].strip()

                if value.lower() in ("true", "yes"):
                    value = True
                elif value.lower() in ("false", "no"):
                    value = False
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            value = value.strip('"').strip("'")

                if current_section and indent > 0:
                    result.setdefault(current_section, {})[key] = value
                else:
                    result[key] = value

    return result


def deep_merge(base, override):
    """Merge override into base, returning a new dict."""
    merged = dict(base)
    for k, v in override.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = deep_merge(merged[k], v)
        else:
            merged[k] = v
    return merged


def flatten(d, prefix=""):
    """Flatten nested dict to dot-notation keys."""
    items = {}
    for k, v in d.items():
        key = f"{prefix}{k}" if not prefix else f"{prefix}.{k}"
        if isinstance(v, dict):
            items.update(flatten(v, key))
        else:
            items[key] = v
    return items


def get_config():
    """Load and return merged config (defaults + file overrides)."""
    config_path = find_config()
    if config_path:
        file_config = parse_yaml_simple(config_path)
        return deep_merge(DEFAULTS, file_config)
    return dict(DEFAULTS)


def shell_escape(value):
    s = str(value)
    return "'" + s.replace("'", "'\\''") + "'"


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--get", type=str, help="Get a single dot-notation key")
    args = parser.parse_args()

    config = get_config()

    if args.get:
        flat = flatten(config)
        value = flat.get(args.get)
        if value is None:
            print(f"ERROR: key '{args.get}' not found", file=sys.stderr)
            sys.exit(1)
        print(value)
        return

    if args.json:
        print(json.dumps(config, indent=2))
        return

    # Shell mode: output flat variable assignments
    flat = flatten(config)
    for key, value in flat.items():
        shell_key = key.upper().replace(".", "_").replace("-", "_")
        print(f"export POPPINS_{shell_key}={shell_escape(value)}")


if __name__ == "__main__":
    main()
