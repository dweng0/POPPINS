#!/usr/bin/env python3
"""Integration test agent — runs post-merge tests and fixes failures."""

import os
import sys
import json
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_poppins_config import get_config


def log_event(log_path, event_type, **kwargs):
    """Append an event to the JSONL log."""
    event = {"ts": datetime.now().isoformat(), "event": event_type, **kwargs}
    with open(log_path, "a") as f:
        f.write(json.dumps(event) + "\n")


def run_cmd(cmd, cwd=None, timeout=120):
    """Run a shell command."""
    import subprocess

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "timeout", 1


def run_tests(main_dir):
    """Run all tests and return results."""
    config = get_config()
    test_cmd = config.get("agent", {}).get("test_cmd", "python3 -m pytest tests/ -v")

    # Get test command from BDD.md if available
    bdd_config_path = os.path.join(main_dir, "BDD.md")
    if os.path.exists(bdd_config_path):
        _, _, rc = run_cmd(
            'eval "$(python3 scripts/parse_bdd_config.py BDD.md)" && echo "$TEST_CMD"',
            cwd=main_dir,
            timeout=10,
        )
        if rc == 0:
            test_cmd = os.environ.get("TEST_CMD", "python3 -m pytest tests/ -v")

    stdout, stderr, rc = run_cmd(
        'eval "$(python3 scripts/parse_bdd_config.py BDD.md)" && eval "$TEST_CMD"',
        cwd=main_dir,
        timeout=120,
    )

    return stdout, stderr, rc


def analyze_test_failure(stdout, stderr, rc):
    """Analyze test failure and suggest fixes."""
    suggestions = []

    # Check for syntax errors
    if "SyntaxError" in stdout or "SyntaxError" in stderr:
        suggestions.append("Fix syntax errors in recently modified files")

    # Check for import errors
    if (
        "ImportError" in stdout
        or "ImportError" in stderr
        or "ModuleNotFoundError" in stdout
        or "ModuleNotFoundError" in stderr
    ):
        suggestions.append("Check import statements in modified files")
        suggestions.append("Verify all required modules are imported")

    # Check for assertion errors
    if "AssertionError" in stdout:
        # Extract test name
        m = re.search(r"FAILED.*test_(\w+)", stdout)
        if m:
            suggestions.append(f"Review test_{m.group(1)}() implementation")

    # Check for missing markers
    if "BDD marker" in stdout or "BDD marker" in stderr:
        suggestions.append("Add '# BDD: <scenario>' markers to test functions")

    # Check for merge conflict markers - THIS IS CRITICAL
    if "<<<<<<" in stdout or "<<<<<<" in stderr:
        suggestions.append("Remove merge conflict markers from files")
    if "SyntaxError" in stdout and "<<" in stdout:
        suggestions.append("Remove merge conflict markers from files")

    return suggestions


def fix_test_failure(main_dir, suggestions):
    """Attempt to fix test failures based on suggestions."""
    log_path = os.path.join(main_dir, "integration_test.jsonl")

    fixes_applied = 0

    for suggestion in suggestions:
        # Remove merge conflict markers FIRST - this is critical
        if "merge conflict markers" in suggestion:
            # Find all Python files with conflict markers
            files_with_conflicts, _, _ = run_cmd(
                'grep -rl "<<<<<<" tests/ scripts/ src/ 2>/dev/null || true',
                cwd=main_dir,
                timeout=30,
            )

            for file_path in files_with_conflicts.splitlines():
                file_path = file_path.strip()
                if not file_path:
                    continue

                try:
                    with open(file_path) as f:
                        content = f.read()

                    # Remove conflict markers
                    content = re.sub(r"<<<<<<< HEAD\n", "", content)
                    content = re.sub(r"=======\n", "", content)
                    content = re.sub(r">>>>>>> agent/[^\n]+\n", "", content)
                    content = re.sub(r">>>>>>> [^\n]+\n", "", content)

                    with open(file_path, "w") as f:
                        f.write(content)

                    fixes_applied += 1
                    log_event(log_path, "conflict_markers_removed", file=file_path)
                    print(f"    [FIX] Removed conflict markers from {file_path}")
                except Exception as e:
                    log_event(
                        log_path, "conflict_fix_failed", file=file_path, error=str(e)
                    )

        # Try to fix import issues
        if "import" in suggestion.lower() and fixes_applied == 0:
            # Check for files with syntax errors
            files_out, _, _ = run_cmd(
                "python3 -m py_compile scripts/*.py tests/*.py 2>&1 | grep -oP 'File.*?\\d+' | head -20",
                cwd=main_dir,
                timeout=30,
            )

            for file_line in files_out.splitlines():
                if "SyntaxError" in file_line:
                    # Try to find and fix the issue
                    m = re.search(r'File "([^"]+)"', file_line)
                    if m:
                        file_path = m.group(1)
                        log_event(
                            log_path, "fix_attempt", file=file_path, fix="syntax_check"
                        )

    return fixes_applied > 0


def run_integration_tests(scenario_results, main_dir):
    """Run integration tests after merging scenarios."""
    log_path = os.path.join(main_dir, "integration_test.jsonl")

    # Run initial tests
    stdout, stderr, rc = run_tests(main_dir)

    # Log initial results
    test_results = {
        "ts": datetime.now().isoformat(),
        "event": "integration_test_run",
        "scenario_results": [r["scenario"] for r in scenario_results],
        "rc": rc,
        "stdout_preview": stdout[:500] if stdout else "",
        "stderr_preview": stderr[:500] if stderr else "",
    }

    # Count tests
    passed = len(re.findall(r"PASSED", stdout))
    failed = len(re.findall(r"FAILED", stdout))
    test_results["passed"] = passed
    test_results["failed"] = failed

    log_event(log_path, "initial_test_results", **test_results)

    if rc == 0:
        print(f"[OK] All tests passing ({passed} passed, {failed} failed)")
        return True, test_results

    print(f"[FAIL] {failed} tests failed")

    # Analyze failures
    suggestions = analyze_test_failure(stdout, stderr, rc)
    print(f"Suggested fixes: {suggestions}")

    # Attempt fix (one attempt only)
    if suggestions:
        print("Attempting to fix failures...")
        fixes_applied = fix_test_failure(main_dir, suggestions)

        if fixes_applied:
            # Re-run tests
            stdout2, stderr2, rc2 = run_tests(main_dir)

            test_results["retry"] = {
                "rc": rc2,
                "stdout_preview": stdout2[:500] if stdout2 else "",
                "stderr_preview": stderr2[:500] if stderr2 else "",
            }

            passed2 = len(re.findall(r"PASSED", stdout2))
            failed2 = len(re.findall(r"FAILED", stdout2))
            test_results["retry"]["passed"] = passed2
            test_results["retry"]["failed"] = failed2

            log_event(log_path, "retry_test_results", **test_results)

            if rc2 == 0:
                print(
                    f"[OK] Tests now passing after fix ({passed2} passed, {failed2} failed)"
                )
                return True, test_results

    # Persistent failure
    print("[FAIL] Persistent test failure after fix attempt")
    log_event(log_path, "integration_test_failed", **test_results)

    return False, test_results


def main():
    """Main entry point for integration test agent."""
    parser = argparse.ArgumentParser(description="BAADD Integration Test Agent")
    parser.add_argument("--main-dir", default=".", help="Main repository directory")
    parser.add_argument("--results-file", help="JSON file with scenario results")
    parser.add_argument(
        "--max-fix-attempts", type=int, default=1, help="Max fix attempts"
    )
    args = parser.parse_args()

    # Load scenario results
    scenario_results = []
    if args.results_file and os.path.exists(args.results_file):
        with open(args.results_file) as f:
            scenario_results = json.load(f)

    success, results = run_integration_tests(scenario_results, args.main_dir)

    if success:
        print("Integration tests: PASSED")
        sys.exit(0)
    else:
        print("Integration tests: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    main()
