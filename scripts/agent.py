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

    while iteration < max_iterations:
        iteration += 1

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
                    print(f"\n\033[36m[{block.name}]\033[0m ", end="", flush=True)
                    result = run_tool(block.name, block.input)
                    print("\033[32mdone\033[0m", flush=True)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            print(f"\n[stopped: {response.stop_reason}]", flush=True)
            break

    if iteration >= max_iterations:
        print(f"\n[BAADD agent: hit iteration limit ({max_iterations})]", flush=True)


if __name__ == "__main__":
    main()
