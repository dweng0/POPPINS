#!/usr/bin/env python3
"""Merge agent — resolves conflicts and merges multiple scenario results."""

import os
import sys
import json
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def log_event(log_path, event_type, **kwargs):
    """Append an event to the JSONL log."""
    event = {"ts": datetime.now().isoformat(), "event": event_type, **kwargs}
    with open(log_path, "a") as f:
        f.write(json.dumps(event) + "\n")


def detect_comment_prefix(filepath):
    """Detect comment prefix based on file extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".py", ".pyi", ".pyx", ".pxd"):
        return "#"
    elif ext in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"):
        return "//"
    elif ext in (".rs", ".go", ".java", ".c", ".cpp", ".h", ".hpp"):
        return "//"
    elif ext in (".rb", ".pl", ".pm", ".t"):
        return "#"
    elif ext in (".php"):
        return "#"
    elif ext in (".sh", ".bash", ".zsh", ".ksh"):
        return "#"
    elif ext in (".sql"):
        return "--"
    elif ext in (".css", ".scss", ".sass", ".less"):
        return "/*"
    return "#"


def has_existing_marker(content, line_index, scenario_name, prefix):
    """Check if a BDD marker already exists above the given line."""
    lines = content.splitlines(True)
    if line_index <= 0:
        return False

    marker_line = line_index - 1
    if marker_line < len(lines):
        line = lines[marker_line].strip()
        expected_marker = f"{prefix} BDD: {scenario_name}"
        return line == expected_marker

    return False


def insert_marker_above_line(content, line_index, scenario_name, prefix):
    """Insert a BDD marker above the specified line."""
    lines = content.splitlines(True)

    if has_existing_marker(content, line_index, scenario_name, prefix):
        return None

    marker = f"{prefix} BDD: {scenario_name}\n"
    lines.insert(line_index, marker)

    return "".join(lines)


def resolve_import_conflict(content_a, content_b, filepath):
    """Resolve import conflicts between two versions of a file."""
    ext = os.path.splitext(filepath)[1].lower()

    # Parse imports from both versions
    imports_a = []
    imports_b = []
    lines_a = content_a.splitlines(True)
    lines_b = content_b.splitlines(True)

    # Find import lines in version A
    for i, line in enumerate(lines_a):
        if line.strip().startswith("from ") or line.strip().startswith("import "):
            # Extract module and items
            m = re.match(r"(from\s+(\S+)\s+import\s+)(.+)", line.strip())
            if m:
                module = m.group(2)
                items = [x.strip() for x in m.group(3).split(",")]
                imports_a.append((module, items, line))
            elif line.strip().startswith("import "):
                items = [
                    x.strip() for x in line.strip().replace("import ", "").split(",")
                ]
                imports_a.append((None, items, line))

    # Find import lines in version B
    for i, line in enumerate(lines_b):
        if line.strip().startswith("from ") or line.strip().startswith("import "):
            m = re.match(r"(from\s+(\S+)\s+import\s+)(.+)", line.strip())
            if m:
                module = m.group(2)
                items = [x.strip() for x in m.group(3).split(",")]
                imports_b.append((module, items, line))
            elif line.strip().startswith("import "):
                items = [
                    x.strip() for x in line.strip().replace("import ", "").split(",")
                ]
                imports_b.append((None, items, line))

    # Merge imports (union of all modules)
    merged_imports = {}
    for module, items, _ in imports_a + imports_b:
        if module is None:
            # Simple import statement
            for item in items:
                if None not in merged_imports:
                    merged_imports[None] = []
                merged_imports[None].append(item)
        else:
            if module not in merged_imports:
                merged_imports[module] = []
            merged_imports[module].extend(items)

    # Build merged import section
    import_lines = []
    # Sort with None at the end
    sorted_modules = sorted([m for m in merged_imports.keys() if m is not None])
    if None in merged_imports:
        sorted_modules.append(None)

    for module in sorted_modules:
        items = merged_imports[module]
        unique_items = sorted(set(items))
        if module is None:
            import_lines.append(f"import {', '.join(unique_items)}\n")
        else:
            import_lines.append(f"from {module} import {', '.join(unique_items)}\n")

    # Replace import lines in version A with merged version
    # Find range of import lines
    first_import_idx = None
    last_import_idx = None
    for i, line in enumerate(lines_a):
        if line.strip().startswith("from ") or line.strip().startswith("import "):
            if first_import_idx is None:
                first_import_idx = i
            last_import_idx = i

    if first_import_idx is not None:
        # Replace import lines with merged imports
        new_lines = (
            lines_a[:first_import_idx] + import_lines + lines_a[last_import_idx + 1 :]
        )
        return "".join(new_lines)

    # No imports found in version A, try version B
    first_import_idx = None
    last_import_idx = None
    for i, line in enumerate(lines_b):
        if line.strip().startswith("from ") or line.strip().startswith("import "):
            if first_import_idx is None:
                first_import_idx = i
            last_import_idx = i

    if first_import_idx is not None:
        new_lines = (
            lines_b[:first_import_idx] + import_lines + lines_b[last_import_idx + 1 :]
        )
        return "".join(new_lines)

    # No imports to merge, return version A
    return content_a


def resolve_file_merge(
    file_path, content_a, content_b, scenario_a, scenario_b, main_dir
):
    """Resolve merge conflict between two file versions using AI when possible."""
    log_path = os.path.join(main_dir, "merge_resolution.jsonl")

    # Check for syntax errors from conflict markers
    if "<<<<<<" in content_a or "======" in content_a or ">>>>>>" in content_a:
        content_a = re.sub(r"<<<<<<< HEAD\n", "", content_a)
        content_a = re.sub(r"=======\n", "", content_a)
        content_a = re.sub(r">>>>>>> agent/[^\n]+\n", "", content_a)
        content_a = re.sub(r">>>>>>> [^\n]+\n", "", content_a)
        log_event(log_path, "conflict_marker_removed", file=file_path, version="A")

    if "<<<<<<" in content_b or "======" in content_b or ">>>>>>" in content_b:
        content_b = re.sub(r"<<<<<<< HEAD\n", "", content_b)
        content_b = re.sub(r"=======\n", "", content_b)
        content_b = re.sub(r">>>>>>> agent/[^\n]+\n", "", content_b)
        content_b = re.sub(r">>>>>>> [^\n]+\n", "", content_b)
        log_event(log_path, "conflict_marker_removed", file=file_path, version="B")

    # Check if files are identical
    if content_a == content_b:
        return content_a, "identical"

    # Try to use AI merge if anthropic is available
    try:
        import anthropic

        return _resolve_file_merge_with_ai(
            file_path, content_a, content_b, scenario_a, scenario_b, main_dir
        )
    except ImportError:
        pass

    # Fallback: check for import conflicts
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".py",):
        # Try to detect and merge import statements
        has_imports_a = any(
            line.strip().startswith(("from ", "import "))
            for line in content_a.splitlines()
        )
        has_imports_b = any(
            line.strip().startswith(("from ", "import "))
            for line in content_b.splitlines()
        )

        if has_imports_a or has_imports_b:
            merged = resolve_import_conflict(content_a, content_b, file_path)
            if merged != content_a and merged != content_b:
                log_event(
                    log_path,
                    "import_merge",
                    file=file_path,
                    scenario_a=scenario_a,
                    scenario_b=scenario_b,
                )
                return merged, "import_merged"

    # Check for test function additions (common case)
    lines_a = content_a.splitlines(True)
    lines_b = content_b.splitlines(True)

    # Find test functions in both
    test_funcs_a = {}
    test_funcs_b = {}

    for i, line in enumerate(lines_a):
        if "def test_" in line:
            m = re.search(r"def (test_\w+)", line)
            if m:
                test_funcs_a[m.group(1)] = i

    for i, line in enumerate(lines_b):
        if "def test_" in line:
            m = re.search(r"def (test_\w+)", line)
            if m:
                test_funcs_b[m.group(1)] = i

    # Merge test functions from B into A if not present
    merged_lines = list(lines_a)
    offset = 0

    for func_name, line_idx in test_funcs_b.items():
        if func_name not in test_funcs_a:
            # Find corresponding test in B and copy it
            func_lines = []
            j = line_idx
            while j < len(lines_b):
                func_lines.append(lines_b[j])
                # Check if next line is indented (part of function)
                if j + 1 < len(lines_b):
                    next_line = lines_b[j + 1]
                    if next_line.strip() == "" or (
                        next_line.startswith("    ") or next_line.startswith("\t")
                    ):
                        j += 1
                        continue
                break

            # Insert at end of file (after last test or at end)
            insert_idx = len(merged_lines)
            for idx, line in enumerate(merged_lines):
                if "def test_" in line:
                    insert_idx = idx + 1

            merged_lines = (
                merged_lines[:insert_idx] + func_lines + merged_lines[insert_idx:]
            )
            offset += len(func_lines)
            log_event(
                log_path,
                "test_function_added",
                file=file_path,
                function=func_name,
                scenario=scenario_b,
            )

    # Check for marker additions
    for i, line in enumerate(lines_b):
        if f"# BDD: {scenario_b}" in line:
            # Check if marker exists in A
            found = False
            for j, aline in enumerate(lines_a):
                if f"# BDD: {scenario_b}" in aline:
                    found = True
                    break
            if not found:
                # Insert marker above corresponding test in A
                for j, aline in enumerate(lines_a):
                    if (
                        "def test_" in aline
                        and scenario_b.lower().replace(" ", "_") in aline.lower()
                    ):
                        marker_line = f"# BDD: {scenario_b}\n"
                        merged_lines.insert(j, marker_line)
                        log_event(
                            log_path,
                            "marker_added",
                            file=file_path,
                            scenario=scenario_b,
                            line=j,
                        )
                        break

    return "".join(merged_lines), "merged"


def _resolve_file_merge_with_ai(
    file_path, content_a, content_b, scenario_a, scenario_b, main_dir
):
    """Use AI to intelligently merge conflicting file versions."""
    import anthropic

    log_path = os.path.join(main_dir, "merge_resolution.jsonl")

    # Use AI to intelligently merge the two versions
    client = anthropic.Anthropic()

    prompt = f"""You are a merge conflict resolver. You need to merge two versions of a Python test file.

Scenario A (first branch): {scenario_a}
Scenario B (second branch): {scenario_b}

File: {file_path}

--- VERSION A (HEAD) ---
{content_a}

--- VERSION B (branch) ---
{content_b}

Please intelligently merge these two versions:
1. Keep both versions of test functions if they test different things
2. Merge import statements from both versions
3. Keep BDD markers from both scenarios if they exist
4. Ensure the merged file has valid Python syntax
5. Return ONLY the merged file content, no explanations

Return the merged file content."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )

        merged_content = response.content[0].text.strip()

        # Clean up any markdown formatting
        if merged_content.startswith("```python"):
            merged_content = (
                merged_content.replace("```python", "").replace("```", "").strip()
            )
        elif merged_content.startswith("```"):
            merged_content = merged_content.replace("```", "").strip()

        log_event(
            log_path,
            "ai_merge_success",
            file=file_path,
            scenario_a=scenario_a,
            scenario_b=scenario_b,
        )

        return merged_content, "ai_merged"

    except Exception as e:
        log_event(log_path, "ai_merge_failed", file=file_path, error=str(e))
        # Fallback to simple resolution
        return resolve_file_merge(
            file_path, content_a, content_b, scenario_a, scenario_b, main_dir
        )


def merge_results(scenario_results, main_dir):
    """Merge multiple scenario results into main branch."""
    log_path = os.path.join(main_dir, "merge_resolution.jsonl")

    if len(scenario_results) == 0:
        return True, "No results to merge"

    if len(scenario_results) == 1:
        # Single result, just merge normally
        result = scenario_results[0]
        branch = result["branch"]
        scenario = result["scenario"]

        stdout, stderr, rc = run_cmd(
            f'git merge --no-ff "{branch}" -m "Merge {scenario}"',
            cwd=main_dir,
            timeout=30,
        )

        if rc != 0:
            log_event(log_path, "merge_failed", scenario=scenario, error=stderr)
            return False, f"Merge failed: {stderr}"

        return True, f"Merged {scenario}"

    # Multiple results - need to merge them in order
    merged = []
    for i, result in enumerate(scenario_results):
        branch = result["branch"]
        scenario = result["scenario"]

        # Check if this branch has already been merged
        check_branch, _, rc = run_cmd(
            f'git branch --contains {branch} | grep -q "^*\\?$" || echo "not_merged"',
            cwd=main_dir,
            timeout=10,
        )

        if rc == 0:
            # Already merged, skip
            log_event(log_path, "already_merged", scenario=scenario)
            continue

        # Merge this branch
        stdout, stderr, rc = run_cmd(
            f'git merge --no-ff "{branch}" -m "Merge {scenario}"',
            cwd=main_dir,
            timeout=30,
        )

        if rc != 0:
            # Conflict detected - resolve it
            log_event(log_path, "conflict_detected", scenario=scenario, error=stderr)

            # Get the conflicting files
            files_out, _, _ = run_cmd(
                "git diff --name-only --diff-filter=U",
                cwd=main_dir,
                timeout=10,
            )
            conflict_files = [f for f in files_out.splitlines() if f.strip()]

            # Resolve conflicts in each file
            for conflict_file in conflict_files:
                file_path = os.path.join(main_dir, conflict_file)

                if not os.path.exists(file_path):
                    continue

                # Read the file with conflicts
                with open(file_path) as f:
                    content = f.read()

                # Remove conflict markers
                content = re.sub(r"<<<<<<< HEAD\n", "", content)
                content = re.sub(r"=======\n", "", content)
                content = re.sub(r">>>>>>> agent/[^\n]+\n", "", content)
                content = re.sub(r">>>>>>> [^\n]+\n", "", content)

                # Write resolved content
                with open(file_path, "w") as f:
                    f.write(content)

                # Add to staging
                run_cmd(f'git add "{conflict_file}"', cwd=main_dir, timeout=10)

                log_event(
                    log_path, "conflict_resolved", file=conflict_file, scenario=scenario
                )

            # Try to complete the merge
            commit_msg = f"Merge {scenario} (auto-resolved)"
            stdout, stderr, rc = run_cmd(
                f'git commit -m "{commit_msg}"',
                cwd=main_dir,
                timeout=15,
            )

            if rc != 0:
                log_event(
                    log_path, "merge_commit_failed", scenario=scenario, error=stderr
                )
                run_cmd("git merge --abort", cwd=main_dir, timeout=10)
                return False, f"Failed to commit merge for {scenario}: {stderr}"

        merged.append(scenario)
        log_event(log_path, "merge_success", scenario=scenario)

    return True, f"Merged {len(merged)} scenarios: {', '.join(merged)}"


def run_cmd(cmd, cwd=None, timeout=30):
    """Run a shell command."""
    import subprocess

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "timeout", 1


def main():
    """Main entry point for merge agent."""
    parser = argparse.ArgumentParser(description="BAADD Merge Agent")
    parser.add_argument("--main-dir", default=".", help="Main repository directory")
    parser.add_argument("--results-file", help="JSON file with scenario results")
    args = parser.parse_args()

    # Load scenario results
    if args.results_file and os.path.exists(args.results_file):
        with open(args.results_file) as f:
            results = json.load(f)
    else:
        # Get results from current git state
        results = []

    success, message = merge_results(results, args.main_dir)
    print(message)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    main()
