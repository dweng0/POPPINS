#!/usr/bin/env python3
"""
BAADD agent — calls Claude with tool use capabilities.
Reads a prompt from stdin, runs the agent loop, prints output.

Usage:
    ANTHROPIC_API_KEY=sk-... python3 scripts/agent.py --model claude-opus-4-6 --skills ./skills < prompt.txt

Dependencies:
    pip install anthropic
"""

import os
import sys
import subprocess
import argparse
import glob as globmod

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)

MAX_TOKENS = 8192
TOOL_OUTPUT_LIMIT = 12000

TOOLS = [
    {
        "name": "bash",
        "description": "Run a shell command and return its output.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file, creating it if it doesn't exist.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "edit_file",
        "description": "Replace the first occurrence of old_str with new_str in a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_str": {"type": "string", "description": "Exact string to find"},
                "new_str": {"type": "string", "description": "Replacement string"}
            },
            "required": ["path", "old_str", "new_str"]
        }
    },
    {
        "name": "list_files",
        "description": "List files in a directory recursively.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory to list (default: .)"}
            }
        }
    },
    {
        "name": "search_files",
        "description": "Search for a pattern across all files in the project.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Text to search for"},
                "path": {"type": "string", "description": "Directory to search (default: .)"}
            },
            "required": ["pattern"]
        }
    }
]


def run_tool(name, input_data):
    try:
        if name == "bash":
            result = subprocess.run(
                input_data["command"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
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
                content = content[:TOOL_OUTPUT_LIMIT] + f"\n[... truncated at {TOOL_OUTPUT_LIMIT} chars]"
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
                ["find", path, "-type", "f",
                 "-not", "-path", "*/.git/*",
                 "-not", "-path", "*/node_modules/*",
                 "-not", "-path", "*/target/*",
                 "-not", "-path", "*/__pycache__/*"],
                capture_output=True, text=True
            )
            output = result.stdout.strip()
            return output[:TOOL_OUTPUT_LIMIT] if output else "(empty)"

        elif name == "search_files":
            pattern = input_data["pattern"]
            path = input_data.get("path", ".")
            result = subprocess.run(
                ["grep", "-r", "--include=*", "-l", pattern, path],
                capture_output=True, text=True
            )
            files = result.stdout.strip()
            if not files:
                return f"No files found containing: {pattern}"
            # Show matching lines too
            result2 = subprocess.run(
                ["grep", "-r", "-n", "--include=*", pattern, path],
                capture_output=True, text=True
            )
            return (files + "\n\nMatching lines:\n" + result2.stdout)[:TOOL_OUTPUT_LIMIT]

    except subprocess.TimeoutExpired:
        return "ERROR: command timed out after 300s"
    except Exception as e:
        return f"ERROR: {e}"


def prune_old_tool_results(messages, keep_last=3):
    """Replace content of old tool_result messages with [pruned] to limit context growth."""
    # Find all user messages that contain tool_results
    tool_result_indices = [
        i for i, m in enumerate(messages)
        if m["role"] == "user" and isinstance(m["content"], list)
        and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in m["content"])
    ]
    # Prune all but the last `keep_last`
    to_prune = tool_result_indices[:-keep_last] if len(tool_result_indices) > keep_last else []
    pruned = 0
    for i in to_prune:
        new_content = []
        for block in messages[i]["content"]:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                if block.get("content") != "[pruned]":
                    block = {**block, "content": "[pruned]"}
                    pruned += 1
            new_content.append(block)
        messages[i]["content"] = new_content
    if pruned:
        print(f"  \033[90m[context: pruned {pruned} old tool result(s)]\033[0m", flush=True)


def load_skills(skills_dir):
    """Load skill files and return as system prompt additions."""
    if not skills_dir or not os.path.isdir(skills_dir):
        return ""

    skill_texts = []
    for skill_file in sorted(globmod.glob(os.path.join(skills_dir, "**", "SKILL.md"), recursive=True)):
        try:
            with open(skill_file) as f:
                skill_texts.append(f.read())
        except Exception:
            pass

    if skill_texts:
        return "\n\n---\n\n".join(skill_texts)
    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="claude-opus-4-6")
    parser.add_argument("--skills", default=None)
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    prompt = sys.stdin.read().strip()
    if not prompt:
        print("ERROR: no prompt provided on stdin", file=sys.stderr)
        sys.exit(1)

    skills_text = load_skills(args.skills)
    system_prompt = "You are an expert software developer. You build software strictly according to BDD specifications."
    if skills_text:
        system_prompt += "\n\n" + skills_text

    client = anthropic.Anthropic(api_key=api_key)
    messages = [{"role": "user", "content": prompt}]

    print(f"[BAADD agent starting — model: {args.model}]", flush=True)

    iteration = 0
    max_iterations = 50  # safety limit
    wrap_up_at = 45
    wrap_up_injected = False

    while iteration < max_iterations:
        iteration += 1

        if iteration >= wrap_up_at and not wrap_up_injected:
            print(f"\n\033[33m[agent: iteration {iteration}/{max_iterations} — injecting wrap-up reminder]\033[0m", flush=True)
            messages.append({
                "role": "user",
                "content": (
                    f"⚠️ You have used {iteration} of {max_iterations} allowed iterations. "
                    "Stop starting new work. Finish only what you are currently doing, then wrap up:\n"
                    "1. Run the build and tests — fix any failures before committing.\n"
                    "2. Update BDD_STATUS.md with current coverage.\n"
                    "3. Write your journal entry to JOURNAL.md. Include: what you completed this session, "
                    "which scenarios are still uncovered or failing, and exactly where the next session should pick up. "
                    "The next session's agent will read this journal to orient itself — make the handoff clear.\n"
                    "4. Commit everything.\n"
                    "Do not start any new scenarios."
                )
            })
            wrap_up_injected = True

        response = client.messages.create(
            model=args.model,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        # Print text content
        for block in response.content:
            if hasattr(block, "text") and block.text:
                print(block.text, end="", flush=True)

        if response.stop_reason == "end_turn":
            print("\n[BAADD agent done]", flush=True)
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    # Show tool name + key input detail
                    if block.name == "bash":
                        cmd_preview = block.input.get("command", "")[:120]
                        print(f"\n\033[36m[{block.name}]\033[0m \033[90m$ {cmd_preview}\033[0m", flush=True)
                    elif block.name == "write_file":
                        path = block.input.get('path', '')
                        content = block.input.get('content', '')
                        lines = content.splitlines()
                        print(f"\n\033[36m[{block.name}]\033[0m \033[90m{path} ({len(lines)} lines)\033[0m", flush=True)
                        preview_lines = lines[:4]
                        shown = "\n  ".join(preview_lines)
                        suffix = f"\n  ... ({len(lines) - 4} more lines)" if len(lines) > 4 else ""
                        print(f"  \033[90m{shown}{suffix}\033[0m", flush=True)
                    elif block.name in ("read_file", "edit_file"):
                        print(f"\n\033[36m[{block.name}]\033[0m \033[90m{block.input.get('path', '')}\033[0m", flush=True)
                    else:
                        print(f"\n\033[36m[{block.name}]\033[0m", flush=True)
                    result = run_tool(block.name, block.input)
                    # Show a short output preview
                    preview = str(result).strip()
                    if preview and preview != f"(exit code: 0)":
                        lines = preview.splitlines()
                        shown = "\n  ".join(lines[:5])
                        suffix = f"\n  ... ({len(lines) - 5} more lines)" if len(lines) > 5 else ""
                        print(f"  \033[90m{shown}{suffix}\033[0m", flush=True)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            prune_old_tool_results(messages)
        else:
            print(f"\n[stopped: {response.stop_reason}]", flush=True)
            break

    if iteration >= max_iterations:
        print(f"\n[BAADD agent: hit iteration limit ({max_iterations})]", flush=True)


if __name__ == "__main__":
    main()
