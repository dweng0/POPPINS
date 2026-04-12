#!/usr/bin/env python3
"""
BAADD agent — multi-provider AI agent with tool use.
Reads a prompt from stdin, runs the agent loop, prints output.

Usage:
    ANTHROPIC_API_KEY=sk-...  python3 scripts/agent.py < prompt.txt  # Anthropic (priority)
    MOONSHOT_API_KEY=sk-...   python3 scripts/agent.py < prompt.txt  # Kimi
    DASHSCOPE_API_KEY=sk-...  python3 scripts/agent.py < prompt.txt  # Alibaba/Qwen
    OPENAI_API_KEY=sk-...     python3 scripts/agent.py < prompt.txt  # OpenAI
    GROQ_API_KEY=gsk_...      python3 scripts/agent.py < prompt.txt  # Groq
    OLLAMA_HOST=http://...    python3 scripts/agent.py --model llama3 < prompt.txt
    CUSTOM_BASE_URL=http://...  CUSTOM_API_KEY=sk-... CUSTOM_MODEL=mymodel  python3 scripts/agent.py < prompt.txt

Flags:
    --model     Override default model for the detected provider
    --provider  Force a specific provider (anthropic|moonshot|dashscope|openai|groq|ollama|custom)
    --skills    Path to skills directory
    --mode      evolve|bootstrap (affects wrap-up reminder content)

Provider priority (first key found wins):
    ANTHROPIC_API_KEY > MOONSHOT_API_KEY > DASHSCOPE_API_KEY > OPENAI_API_KEY > GROQ_API_KEY > CUSTOM_API_KEY/CUSTOM_BASE_URL > OLLAMA_HOST

Dependencies:
    pip install anthropic openai
"""

import os
import sys
import json
import subprocess
import argparse
import glob as globmod
import time


def load_dotenv(path=".env"):
    """Load .env file into os.environ without overriding existing vars.
    Supports KEY=value, KEY="value", KEY='value', and # comments.
    """
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Strip surrounding quotes
            if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]
            # Only set if not already in environment (explicit env vars take priority)
            if key and key not in os.environ:
                os.environ[key] = value


load_dotenv()

# Import poppins config (lives alongside this script)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_poppins_config import get_config as _get_poppins_config

_POPPINS_CFG = _get_poppins_config().get("agent", {})
MAX_TOKENS = _POPPINS_CFG.get("max_tokens_per_response", 8192)
TOOL_OUTPUT_LIMIT = _POPPINS_CFG.get("tool_output_limit", 12000)
CONTEXT_WINDOW_LIMIT = _POPPINS_CFG.get("context_window_limit", 100000)
MAX_ITERATIONS = _POPPINS_CFG.get("max_iterations", 75)
WRAP_UP_AT = _POPPINS_CFG.get("wrap_up_at", 70)


# Apply poppins.yml provider config as env var defaults (env vars take priority).
# This lets users set provider/base_url/api_key once in poppins.yml.
def _apply_poppins_provider_config(cfg):
    provider = cfg.get("provider", "")
    base_url = cfg.get("base_url")
    api_key = cfg.get("api_key")

    if provider == "ollama" and base_url and not os.environ.get("OLLAMA_HOST"):
        os.environ["OLLAMA_HOST"] = base_url.rstrip("/").removesuffix("/v1")
    elif base_url and not os.environ.get("CUSTOM_BASE_URL"):
        os.environ["CUSTOM_BASE_URL"] = base_url

    if api_key:
        key_env = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "groq": "GROQ_API_KEY",
            "moonshot": "MOONSHOT_API_KEY",
            "dashscope": "DASHSCOPE_API_KEY",
            "custom": "CUSTOM_API_KEY",
        }.get(provider, "CUSTOM_API_KEY")
        if not os.environ.get(key_env):
            os.environ[key_env] = api_key

    if provider == "custom" and not os.environ.get("CUSTOM_MODEL"):
        model = cfg.get("default_model")
        if model:
            os.environ["CUSTOM_MODEL"] = model


_apply_poppins_provider_config(_POPPINS_CFG)

# Detect GitHub Actions for log grouping
IN_CI = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"

# Icons for tool types (plain-text, no emoji to keep CI logs clean)
TOOL_ICONS = {
    "bash": "$",
    "read_file": "<-",
    "write_file": "->",
    "edit_file": "~~",
    "list_files": "ls",
    "search_files": "??",
}


class EventLogger:
    """Writes structured JSON Lines to a log file for observability."""

    def __init__(self, path):
        self._path = path
        self._file = None
        self._session_start = time.time()
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        if path:
            self._file = open(path, "a")

    def _write(self, event, **data):
        if not self._file:
            return
        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "elapsed_s": round(time.time() - self._session_start, 2),
            "event": event,
            **data,
        }
        self._file.write(json.dumps(record, default=str) + "\n")
        self._file.flush()

    def session_start(self, provider, model, mode):
        self._write("session_start", provider=provider, model=model, mode=mode)

    def iteration_start(self, iteration, max_iterations):
        self._write(
            "iteration_start", iteration=iteration, max_iterations=max_iterations
        )

    def agent_text(self, text, iteration):
        self._write("agent_text", iteration=iteration, text=text[:500])

    def tool_call(self, name, input_data, iteration):
        preview = {
            k: (v[:200] if isinstance(v, str) and len(v) > 200 else v)
            for k, v in input_data.items()
        }
        self._write("tool_call", iteration=iteration, tool=name, input=preview)

    def tool_result(self, name, result, duration_ms, iteration):
        result_str = str(result)
        self._write(
            "tool_result",
            iteration=iteration,
            tool=name,
            duration_ms=round(duration_ms),
            result_length=len(result_str),
            result_preview=result_str[:300],
        )

    def api_response(self, input_tokens, output_tokens, iteration):
        self._total_input_tokens += input_tokens or 0
        self._total_output_tokens += output_tokens or 0
        self._write(
            "api_response",
            iteration=iteration,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cumulative_input_tokens=self._total_input_tokens,
            cumulative_output_tokens=self._total_output_tokens,
        )

    def wrap_up(self, iteration):
        self._write("wrap_up_injected", iteration=iteration)

    def session_end(self, iterations_used, reason):
        self._write(
            "session_end",
            iterations_used=iterations_used,
            reason=reason,
            total_input_tokens=self._total_input_tokens,
            total_output_tokens=self._total_output_tokens,
        )
        if self._file:
            self._file.close()
            self._file = None


def estimate_tokens(text):
    """Rough token estimate: ~4 chars per token for English/code."""
    return len(str(text)) // 4


def _get_msg_attr(msg, attr, default=None):
    """Get attribute from message - works for both dict and Pydantic objects."""
    if hasattr(msg, attr):
        return getattr(msg, attr, default)
    return msg.get(attr, default)


def estimate_messages_tokens(messages):
    """Estimate total tokens across all messages."""
    total = 0
    for msg in messages:
        content = _get_msg_attr(msg, "content", "")
        if isinstance(content, str):
            total += estimate_tokens(content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    total += estimate_tokens(item.get("content", ""))
                    total += estimate_tokens(item.get("text", ""))
                else:
                    total += estimate_tokens(str(item))
        else:
            total += estimate_tokens(str(content) if content else "")
    return total


def trim_context(messages, limit):
    """Trim older tool results when estimated tokens exceed limit.

    Strategy: walk from oldest to newest. For tool result messages older than
    the most recent 6 exchanges, replace long content with a truncated summary.
    Preserves the last 6 message pairs (12 messages) untouched so the agent
    has full context for its current work.
    """
    est = estimate_messages_tokens(messages)
    if est <= limit:
        return messages

    # Keep the first message (initial prompt) and the last 12 messages intact
    protected_tail = 12
    if len(messages) <= protected_tail + 1:
        return messages

    trimmed = 0
    for i in range(1, len(messages) - protected_tail):
        msg = messages[i]
        content = _get_msg_attr(msg, "content", "")

        # Trim tool_result lists (Anthropic format)
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_result":
                    old_content = item.get("content", "")
                    if len(str(old_content)) > 500:
                        item["content"] = (
                            str(old_content)[:200]
                            + "\n[... trimmed by context manager]"
                        )
                        trimmed += 1

        # Trim tool role messages (OpenAI format)
        elif (
            _get_msg_attr(msg, "role") == "tool"
            and isinstance(content, str)
            and len(content) > 500
        ):
            messages[i] = dict(msg) if hasattr(msg, "__dict__") else dict(msg)
            messages[i]["content"] = (
                content[:200] + "\n[... trimmed by context manager]"
            )
            trimmed += 1

    if trimmed > 0:
        new_est = estimate_messages_tokens(messages)
        print(
            f"\033[90m  [context: trimmed {trimmed} old results, ~{est}→~{new_est} tokens]\033[0m",
            flush=True,
        )

    return messages


# Provider detection — ordered by priority
PROVIDER_PRIORITY = [
    ("anthropic", "ANTHROPIC_API_KEY"),
    ("moonshot", "MOONSHOT_API_KEY"),
    ("dashscope", "DASHSCOPE_API_KEY"),
    ("openai", "OPENAI_API_KEY"),
    ("groq", "GROQ_API_KEY"),
    ("custom", "CUSTOM_API_KEY"),
]

PROVIDER_CONFIGS = {
    "anthropic": {
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": None,
        "default_model": "claude-haiku-4-5-20251001",
    },
    "moonshot": {
        "api_key_env": "MOONSHOT_API_KEY",
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "kimi-latest",
    },
    "dashscope": {
        "api_key_env": "DASHSCOPE_API_KEY",
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-max",
    },
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "default_model": "gpt-4o",
    },
    "groq": {
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
    },
    "custom": {
        "api_key_env": "CUSTOM_API_KEY",
        "base_url": None,  # resolved from CUSTOM_BASE_URL at runtime
        "default_model": None,  # resolved from CUSTOM_MODEL at runtime
    },
    "ollama": {
        "api_key_env": None,
        "base_url": None,  # resolved from OLLAMA_HOST at runtime
        "default_model": "llama3.2",
    },
}

# Tool definitions in Anthropic format (converted to OpenAI format where needed)
TOOLS = [
    {
        "name": "bash",
        "description": "Run a shell command and return its output.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"}
            },
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file, creating it if it doesn't exist.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace the first occurrence of old_str with new_str in a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_str": {"type": "string", "description": "Exact string to find"},
                "new_str": {"type": "string", "description": "Replacement string"},
            },
            "required": ["path", "old_str", "new_str"],
        },
    },
    {
        "name": "list_files",
        "description": "List files in a directory recursively.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory to list (default: .)",
                }
            },
        },
    },
    {
        "name": "search_files",
        "description": "Search for a pattern across all files in the project.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Text to search for"},
                "path": {
                    "type": "string",
                    "description": "Directory to search (default: .)",
                },
            },
            "required": ["pattern"],
        },
    },
]

# OpenAI-format version of the same tools
TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"],
        },
    }
    for t in TOOLS
]


def detect_provider():
    """Return provider from env var detection, then poppins.yml config, then ollama probe.
    
    Environment variables take priority over poppins.yml config.
    """
    # Check environment variables first (highest priority)
    for name, env_var in PROVIDER_PRIORITY:
        if os.environ.get(env_var):
            return name
    # Custom: base URL alone is enough (some endpoints need no auth)
    if os.environ.get("CUSTOM_BASE_URL"):
        return "custom"
    # Ollama: check OLLAMA_HOST or probe localhost
    if os.environ.get("OLLAMA_HOST"):
        return "ollama"
    # Fall back to poppins.yml config
    cfg_provider = _POPPINS_CFG.get("provider")
    if cfg_provider:
        return cfg_provider
    # Probe localhost for Ollama
    try:
        import urllib.request

        urllib.request.urlopen("http://localhost:11434", timeout=1)
        return "ollama"
    except Exception:
        pass
    return None


def run_tool(name, input_data):
    """Execute a tool call and return the string result."""
    try:
        if name == "bash":
            result = subprocess.run(
                input_data["command"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
            output = result.stdout
            if result.stderr:
                output += "\n[stderr]\n" + result.stderr
            if not output.strip():
                output = f"(exit code: {result.returncode})"
            return output[:TOOL_OUTPUT_LIMIT]

        elif name == "read_file":
            path = input_data["path"]
            if not os.path.exists(path):
                return f"ERROR: file not found: {path}"
            with open(path) as f:
                content = f.read()
            if len(content) > TOOL_OUTPUT_LIMIT:
                content = (
                    content[:TOOL_OUTPUT_LIMIT]
                    + f"\n[... truncated at {TOOL_OUTPUT_LIMIT} chars]"
                )
            return content

        elif name == "write_file":
            path = input_data["path"]
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(path, "w") as f:
                f.write(input_data["content"])
            return f"Written: {path}"

        elif name == "edit_file":
            path = input_data["path"]
            if not os.path.exists(path):
                return f"ERROR: file not found: {path}"
            with open(path) as f:
                content = f.read()
            old_str = input_data["old_str"]
            new_str = input_data["new_str"]
            if old_str not in content:
                return f"ERROR: string not found in {path}. Make sure the old_str matches exactly."
            new_content = content.replace(old_str, new_str, 1)
            with open(path, "w") as f:
                f.write(new_content)
            return f"Edited: {path}"

        elif name == "list_files":
            path = input_data.get("path", ".")
            result = subprocess.run(
                [
                    "find",
                    path,
                    "-type",
                    "f",
                    "-not",
                    "-path",
                    "*/.git/*",
                    "-not",
                    "-path",
                    "*/node_modules/*",
                    "-not",
                    "-path",
                    "*/target/*",
                    "-not",
                    "-path",
                    "*/__pycache__/*",
                ],
                capture_output=True,
                text=True,
            )
            output = result.stdout.strip()
            return output[:TOOL_OUTPUT_LIMIT] if output else "(empty)"

        elif name == "search_files":
            pattern = input_data["pattern"]
            path = input_data.get("path", ".")
            result = subprocess.run(
                ["grep", "-r", "--include=*", "-l", pattern, path],
                capture_output=True,
                text=True,
            )
            files = result.stdout.strip()
            if not files:
                return f"No files found containing: {pattern}"
            result2 = subprocess.run(
                ["grep", "-r", "-n", "--include=*", pattern, path],
                capture_output=True,
                text=True,
            )
            return (files + "\n\nMatching lines:\n" + result2.stdout)[
                :TOOL_OUTPUT_LIMIT
            ]

    except subprocess.TimeoutExpired:
        return "ERROR: command timed out after 300s"
    except Exception as e:
        return f"ERROR: {e}"


def _ci_group(title):
    """Start a collapsible group in GitHub Actions logs."""
    if IN_CI:
        print(f"::group::{title}", flush=True)


def _ci_endgroup():
    """End a collapsible group in GitHub Actions logs."""
    if IN_CI:
        print("::endgroup::", flush=True)


def _result_summary(result):
    """Return a short one-line summary of a tool result."""
    preview = str(result).strip()
    if not preview or preview == "(exit code: 0)":
        return ""
    lines = preview.splitlines()
    # For short results (<=3 lines), show inline
    if len(lines) <= 3:
        return " | ".join(l.strip() for l in lines if l.strip())
    # Otherwise just the first line + count
    first = lines[0].strip()[:100]
    return f"{first}  (+{len(lines) - 1} lines)"


def print_tool_call(name, input_data, result, iteration=None, max_iterations=None):
    """Print a structured tool call summary optimised for CI readability."""
    icon = TOOL_ICONS.get(name, ">")
    iter_tag = f"[{iteration}/{max_iterations}] " if iteration else ""

    # Build the one-line header
    if name == "bash":
        cmd = input_data.get("command", "")
        # Multi-line commands: show first line only
        cmd_preview = cmd.split("\n")[0][:120]
        if "\n" in cmd:
            cmd_preview += " ..."
        header = f"{iter_tag}{icon} {cmd_preview}"
    elif name == "write_file":
        path = input_data.get("path", "")
        n = len(input_data.get("content", "").splitlines())
        header = f"{iter_tag}{icon} {path} ({n} lines)"
    elif name == "edit_file":
        path = input_data.get("path", "")
        header = f"{iter_tag}{icon} {path}"
    elif name == "read_file":
        path = input_data.get("path", "")
        n = len(str(result).splitlines()) if result else 0
        header = f"{iter_tag}{icon} {path} ({n} lines)"
    elif name == "search_files":
        pattern = input_data.get("pattern", "")
        header = f"{iter_tag}{icon} search: {pattern}"
    elif name == "list_files":
        path = input_data.get("path", ".")
        header = f"{iter_tag}{icon} {path}"
    else:
        header = f"{iter_tag}{icon} {name}"

    summary = _result_summary(result)

    # Print the header
    print(f"\033[36m  {header}\033[0m", flush=True)

    # For bash commands and search results, show output (collapsible in CI)
    if name in ("bash", "search_files", "list_files") and summary:
        if IN_CI and len(str(result).splitlines()) > 5:
            _ci_group(f"  output: {summary[:80]}")
            print(f"\033[90m{str(result).strip()}\033[0m", flush=True)
            _ci_endgroup()
        else:
            print(f"\033[90m    {summary}\033[0m", flush=True)
    elif name == "edit_file" and result:
        r = str(result).strip()
        if r.startswith("ERROR"):
            print(f"\033[31m    {r}\033[0m", flush=True)
        else:
            print(f"\033[32m    {r}\033[0m", flush=True)
    elif name == "write_file":
        print("\033[32m    Written\033[0m", flush=True)


def make_wrap_up_message(iteration, max_iterations, mode):
    if mode == "bootstrap":
        return (
            f"⚠️ You have used {iteration} of {max_iterations} allowed iterations. "
            "Stop any new work and wrap up the bootstrap:\n"
            "1. Run the build and tests — fix any failures.\n"
            '2. Commit all changes: git add -A && git commit -m "Bootstrap: scaffold complete"\n'
            '3. Create .baadd_initialized: touch .baadd_initialized && git add .baadd_initialized && git commit -m "Bootstrap: mark initialized"\n'
            "4. Write a Day 0 journal entry to JOURNAL.md.\n"
            '5. Commit the journal: git add JOURNAL.md && git commit -m "Bootstrap: journal entry"\n'
            "Do not start implementing any BDD scenarios."
        )
    return (
        f"⚠️ You have used {iteration} of {max_iterations} allowed iterations. "
        "Stop starting new work. Finish only what you are currently doing, then wrap up:\n"
        "1. Run the build and tests — fix any failures before committing.\n"
        "2. Update BDD_STATUS.md with current coverage.\n"
        "3. Write your journal entry to JOURNAL.md. Include: what you completed this session, "
        "which scenarios are still uncovered or failing, and exactly where the next session should pick up.\n"
        "4. Commit everything.\n"
        "Do not start any new scenarios."
    )


def load_skills(skills_dir):
    if not skills_dir or not os.path.isdir(skills_dir):
        return ""
    skill_texts = []
    for skill_file in sorted(
        globmod.glob(os.path.join(skills_dir, "**", "SKILL.md"), recursive=True)
    ):
        try:
            with open(skill_file) as f:
                skill_texts.append(f.read())
        except Exception:
            pass
    return "\n\n---\n\n".join(skill_texts) if skill_texts else ""


def run_anthropic_loop(api_key, model, system_prompt, prompt, mode, event_log):
    try:
        import anthropic
    except ImportError:
        print(
            "ERROR: anthropic package not installed. Run: pip install anthropic",
            file=sys.stderr,
        )
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    messages = [{"role": "user", "content": prompt}]

    iteration = 0
    wrap_up_injected = False

    while iteration < MAX_ITERATIONS:
        iteration += 1
        event_log.iteration_start(iteration, MAX_ITERATIONS)

        if iteration >= WRAP_UP_AT and not wrap_up_injected:
            print(
                f"\n\033[33m[agent: iteration {iteration}/{MAX_ITERATIONS} — injecting wrap-up reminder]\033[0m",
                flush=True,
            )
            messages.append(
                {
                    "role": "user",
                    "content": make_wrap_up_message(iteration, MAX_ITERATIONS, mode),
                }
            )
            wrap_up_injected = True
            event_log.wrap_up(iteration)

        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        # Log token usage from the API response
        input_tokens = getattr(response.usage, "input_tokens", None)
        output_tokens = getattr(response.usage, "output_tokens", None)
        event_log.api_response(input_tokens, output_tokens, iteration)

        # Print agent reasoning text
        has_text = False
        for block in response.content:
            if hasattr(block, "text") and block.text:
                has_text = True
                text = block.text.strip()
                if text:
                    event_log.agent_text(text, iteration)
                    if IN_CI:
                        _ci_group(
                            f"Agent [{iteration}/{MAX_ITERATIONS}]: {text[:80]}..."
                        )
                        print(text, flush=True)
                        _ci_endgroup()
                    else:
                        print(f"\n\033[33m> {text}\033[0m", flush=True)

        if response.stop_reason == "end_turn":
            print(f"\n[BAADD agent done — {iteration} iterations]", flush=True)
            event_log.session_end(iteration, "end_turn")
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    event_log.tool_call(block.name, block.input, iteration)
                    t0 = time.time()
                    result = run_tool(block.name, block.input)
                    duration_ms = (time.time() - t0) * 1000
                    event_log.tool_result(block.name, result, duration_ms, iteration)
                    print_tool_call(
                        block.name, block.input, result, iteration, MAX_ITERATIONS
                    )
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        }
                    )
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            messages = trim_context(messages, CONTEXT_WINDOW_LIMIT)
        else:
            print(f"\n[stopped: {response.stop_reason}]", flush=True)
            event_log.session_end(iteration, response.stop_reason)
            break

    if iteration >= MAX_ITERATIONS:
        print(f"\n[BAADD agent: hit iteration limit ({MAX_ITERATIONS})]", flush=True)
        event_log.session_end(iteration, "iteration_limit")


def run_openai_loop(client, model, system_prompt, prompt, mode, event_log):
    """Agent loop for any OpenAI-compatible provider (Kimi, Alibaba, Groq, OpenAI, Ollama)."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    iteration = 0
    wrap_up_injected = False

    while iteration < MAX_ITERATIONS:
        iteration += 1
        event_log.iteration_start(iteration, MAX_ITERATIONS)

        if iteration >= WRAP_UP_AT and not wrap_up_injected:
            print(
                f"\n\033[33m[agent: iteration {iteration}/{MAX_ITERATIONS} — injecting wrap-up reminder]\033[0m",
                flush=True,
            )
            messages.append(
                {
                    "role": "user",
                    "content": make_wrap_up_message(iteration, MAX_ITERATIONS, mode),
                }
            )
            wrap_up_injected = True
            event_log.wrap_up(iteration)

        response = client.chat.completions.create(
            model=model,
            max_tokens=MAX_TOKENS,
            messages=messages,
            tools=TOOLS_OPENAI,
            tool_choice="auto",
        )

        choice = response.choices[0]
        msg = choice.message

        # Log token usage (OpenAI-compatible APIs report usage at the response level)
        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "prompt_tokens", None) if usage else None
        output_tokens = getattr(usage, "completion_tokens", None) if usage else None
        event_log.api_response(input_tokens, output_tokens, iteration)

        # Print agent reasoning text
        if msg.content:
            text = msg.content.strip()
            if text:
                event_log.agent_text(text, iteration)
                if IN_CI:
                    _ci_group(f"Agent [{iteration}/{max_iterations}]: {text[:80]}...")
                    print(text, flush=True)
                    _ci_endgroup()
                else:
                    print(f"\n\033[33m> {text}\033[0m", flush=True)

        if choice.finish_reason == "stop":
            print(f"\n[BAADD agent done — {iteration} iterations]", flush=True)
            event_log.session_end(iteration, "stop")
            break

        if choice.finish_reason == "tool_calls":
            # Append assistant message (includes tool_calls metadata)
            messages.append(msg)

            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                try:
                    input_data = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    input_data = {}
                event_log.tool_call(name, input_data, iteration)
                t0 = time.time()
                result = run_tool(name, input_data)
                duration_ms = (time.time() - t0) * 1000
                event_log.tool_result(name, result, duration_ms, iteration)
                print_tool_call(name, input_data, result, iteration, MAX_ITERATIONS)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    }
                )
            messages = trim_context(messages, CONTEXT_WINDOW_LIMIT)
        else:
            print(f"\n[stopped: {choice.finish_reason}]", flush=True)
            event_log.session_end(iteration, choice.finish_reason)
            break

    if iteration >= MAX_ITERATIONS:
        print(f"\n[BAADD agent: hit iteration limit ({MAX_ITERATIONS})]", flush=True)
        event_log.session_end(iteration, "iteration_limit")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", default=None, help="Override default model for the detected provider"
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="Force provider: anthropic|moonshot|dashscope|openai|groq|ollama",
    )
    parser.add_argument("--skills", default=None)
    parser.add_argument("--mode", default="evolve", choices=["evolve", "bootstrap"])
    parser.add_argument(
        "--event-log",
        default=None,
        help="Path for JSON Lines event log (default: agent_events.jsonl)",
    )
    args = parser.parse_args()

    provider = args.provider or detect_provider()
    if not provider:
        print(
            "ERROR: No API key found. Set one of:\n"
            "  ANTHROPIC_API_KEY  — Anthropic Claude (priority)\n"
            "  MOONSHOT_API_KEY   — Kimi\n"
            "  DASHSCOPE_API_KEY  — Alibaba/Qwen\n"
            "  OPENAI_API_KEY     — OpenAI\n"
            "  GROQ_API_KEY       — Groq\n"
            "  CUSTOM_API_KEY + CUSTOM_BASE_URL + CUSTOM_MODEL — any OpenAI-compatible endpoint\n"
            "  OLLAMA_HOST        — Ollama (local)",
            file=sys.stderr,
        )
        sys.exit(1)

    if provider not in PROVIDER_CONFIGS:
        print(
            f"ERROR: Unknown provider '{provider}'. Valid: {', '.join(PROVIDER_CONFIGS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    config = PROVIDER_CONFIGS[provider]

    # Resolve model: --model flag > CUSTOM_MODEL env (for custom provider) > provider default
    if args.model:
        model = args.model
    elif provider == "custom":
        model = os.environ.get("CUSTOM_MODEL") or config["default_model"]
        if not model:
            print(
                "ERROR: CUSTOM_MODEL not set. Provide a model name via CUSTOM_MODEL or --model.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        model = config["default_model"]

    api_key = None
    if config["api_key_env"]:
        api_key = os.environ.get(config["api_key_env"])
        if not api_key and provider != "custom":
            print(f"ERROR: {config['api_key_env']} not set", file=sys.stderr)
            sys.exit(1)

    prompt = sys.stdin.read().strip()
    if not prompt:
        print("ERROR: no prompt provided on stdin", file=sys.stderr)
        sys.exit(1)

    skills_text = load_skills(args.skills)
    system_prompt = (
        "You are an expert software developer. You build software strictly according to BDD specifications.\n\n"
        "CRITICAL RULE — TDD cycle:\n"
        "  1. Write the test.\n"
        "  2. Run it — confirm it fails (do NOT commit yet).\n"
        "  3. Write the implementation that makes it pass.\n"
        "  4. Run all tests — confirm they ALL pass.\n"
        "  5. Only now commit.\n\n"
        "NEVER commit a failing test. A failing test commit is broken code, not a 'red phase checkpoint'.\n"
        "NEVER write tests without also writing the implementation in the same session.\n"
        "If you add a test file, you MUST also add or modify the source file(s) it tests."
    )
    if skills_text:
        system_prompt += "\n\n" + skills_text

    event_log_path = args.event_log if args.event_log else "agent_events.jsonl"
    event_log = EventLogger(event_log_path)

    print(
        f"[BAADD agent starting — provider: {provider}, model: {model}, event log: {event_log_path}]",
        flush=True,
    )
    event_log.session_start(provider, model, args.mode)

    if provider == "anthropic":
        run_anthropic_loop(api_key, model, system_prompt, prompt, args.mode, event_log)
        return

    # All other providers use the OpenAI-compatible client
    try:
        from openai import OpenAI
    except ImportError:
        print(
            "ERROR: openai package not installed. Run: pip install openai",
            file=sys.stderr,
        )
        sys.exit(1)

    base_url = config["base_url"]
    if provider == "ollama":
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        base_url = host.rstrip("/") + "/v1"
        api_key = "ollama"  # OpenAI client requires a non-empty string
    elif provider == "custom":
        base_url = os.environ.get("CUSTOM_BASE_URL")
        if not base_url:
            print(
                "ERROR: CUSTOM_BASE_URL not set. Provide the API base URL via CUSTOM_BASE_URL.",
                file=sys.stderr,
            )
            sys.exit(1)
        if not api_key:
            api_key = "custom"  # OpenAI client requires a non-empty string

    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    client = OpenAI(**client_kwargs)
    run_openai_loop(client, model, system_prompt, prompt, args.mode, event_log)


if __name__ == "__main__":
    main()
