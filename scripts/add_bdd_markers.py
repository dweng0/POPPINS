#!/usr/bin/env python3
"""
Upgrade script: add BDD marker comments to existing test files.

Reads BDD.md to find all scenarios, then scans test files for matches
using the same heuristic as check_bdd_coverage.py. Where a match is found
and no marker already exists, inserts a '# BDD: <scenario name>' (or '//')
comment above the matching test function/block.

Usage:
    python3 scripts/add_bdd_markers.py BDD.md           # dry run (default)
    python3 scripts/add_bdd_markers.py BDD.md --apply    # actually modify files

This is idempotent — running it twice won't add duplicate markers.
"""

import sys
import os
import re

# Reuse the coverage checker's parsing and matching logic
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_bdd_coverage import (
    parse_scenarios,
    find_test_files,
    normalize,
    normalize_partial,
    check_marker,
)

# Comment prefix by file extension
COMMENT_PREFIX = {
    ".py": "#",
    ".js": "//",
    ".ts": "//",
    ".jsx": "//",
    ".tsx": "//",
    ".go": "//",
    ".rs": "//",
    ".java": "//",
    ".rb": "#",
}


def detect_comment_prefix(filepath):
    _, ext = os.path.splitext(filepath)
    return COMMENT_PREFIX.get(ext, "#")


def find_test_line(content, scenario_name):
    """Find the line number where a test matching this scenario starts.
    Returns (line_index, match_type) or (None, None)."""
    full = normalize(scenario_name)
    partial = normalize_partial(scenario_name)
    lines = content.splitlines()

    # Look for test function/block definitions that match
    test_patterns = [
        # Python: def test_scenario_name
        re.compile(r"^\s*def\s+test\w*", re.IGNORECASE),
        # JS/TS: test('...', it('...', describe('...'
        re.compile(r"^\s*(?:test|it|describe)\s*\(", re.IGNORECASE),
        # Go: func Test...
        re.compile(r"^\s*func\s+Test", re.IGNORECASE),
        # Rust: #[test] followed by fn
        re.compile(r"^\s*fn\s+\w*test", re.IGNORECASE),
        # Java: @Test followed by method
        re.compile(r"^\s*(?:@Test|public\s+void\s+test)", re.IGNORECASE),
    ]

    for i, line in enumerate(lines):
        line_lower = line.lower()

        # Check if this line looks like a test definition
        is_test_def = any(p.search(line) for p in test_patterns)
        if not is_test_def:
            continue

        # Check if the scenario name matches this test
        if full in normalize(line):
            return i, "full"
        if partial and partial in line_lower:
            return i, "partial"

        # Check surrounding context (2 lines above, 2 below)
        context_start = max(0, i - 2)
        context_end = min(len(lines), i + 3)
        context = " ".join(lines[context_start:context_end]).lower()

        words = [
            w
            for w in re.sub(r"[^a-z0-9\s]", "", scenario_name.lower()).split()
            if len(w) > 3
        ]
        if len(words) >= 3 and all(w in context for w in words[:4]):
            return i, "words"

    return None, None


def add_marker_to_file(filepath, line_index, scenario_name, prefix):
    """Insert a BDD marker comment above the given line. Returns the modified content."""
    with open(filepath) as f:
        lines = f.readlines()

    marker = f"{prefix} BDD: {scenario_name}\n"

    # Check if marker already exists on the line above
    if (
        line_index > 0
        and "BDD:" in lines[line_index - 1]
        and scenario_name.lower() in lines[line_index - 1].lower()
    ):
        return None  # Already has marker

    # Get the indentation of the test line
    indent = ""
    match = re.match(r"^(\s*)", lines[line_index])
    if match:
        indent = match.group(1)

    lines.insert(line_index, indent + marker)
    return "".join(lines)


def main():
    bdd_path = sys.argv[1] if len(sys.argv) > 1 else "BDD.md"
    apply_changes = "--apply" in sys.argv

    if not os.path.exists(bdd_path):
        print(f"ERROR: {bdd_path} not found")
        sys.exit(1)

    scenarios = parse_scenarios(bdd_path)
    if not scenarios:
        print("No scenarios found in BDD.md.")
        sys.exit(0)

    test_files = find_test_files()
    test_contents = {}
    for path in test_files:
        try:
            with open(path) as f:
                test_contents[path] = f.read()
        except Exception:
            pass

    if not test_contents:
        print("No test files found.")
        sys.exit(0)

    print(f"Found {len(scenarios)} scenario(s), {len(test_contents)} test file(s).\n")

    added = 0
    skipped_has_marker = 0
    skipped_no_match = 0

    for feature, scenario_name in scenarios:
        # Already has an explicit marker?
        if check_marker(scenario_name, test_contents):
            skipped_has_marker += 1
            print(f"  [ok]   {scenario_name} — marker already exists")
            continue

        # Try to find a matching test via heuristic
        found_in = None
        found_line = None
        match_type = None

        for path, content in test_contents.items():
            line_idx, mtype = find_test_line(content, scenario_name)
            if line_idx is not None:
                found_in = path
                found_line = line_idx
                match_type = mtype
                break

        if found_in is None:
            skipped_no_match += 1
            print(f"  [skip] {scenario_name} — no matching test found")
            continue

        prefix = detect_comment_prefix(found_in)
        lines = test_contents[found_in].splitlines()
        test_line_preview = lines[found_line].strip()[:80]

        if apply_changes:
            new_content = add_marker_to_file(
                found_in, found_line, scenario_name, prefix
            )
            if new_content is None:
                skipped_has_marker += 1
                print(f"  [ok]   {scenario_name} — marker already exists")
                continue
            with open(found_in, "w") as f:
                f.write(new_content)
            # Refresh cached content
            test_contents[found_in] = new_content
            added += 1
            print(f"  [add]  {scenario_name}")
            print(f"         → {found_in}:{found_line + 1} ({match_type})")
            print(f"           {test_line_preview}")
        else:
            added += 1
            print(f"  [would add] {scenario_name}")
            print(f"              → {found_in}:{found_line + 1} ({match_type})")
            print(f"                {test_line_preview}")

    print(f"\n{'Applied' if apply_changes else 'Would apply'}: {added} marker(s)")
    print(f"Already marked: {skipped_has_marker}")
    print(f"No test found:  {skipped_no_match}")

    if not apply_changes and added > 0:
        print("\nRe-run with --apply to modify files:")
        print(f"  python3 scripts/add_bdd_markers.py {bdd_path} --apply")


if __name__ == "__main__":
    main()
