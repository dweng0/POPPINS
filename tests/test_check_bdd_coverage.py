#!/usr/bin/env python3
"""Tests for check_bdd_coverage.py"""

import os
import sys
import tempfile

sys.path.insert(0, "scripts")
from check_bdd_coverage import parse_scenarios, find_test_files, check_marker


# BDD: Find test files in project
def test_find_test_files_in_project():
    """Test that find_test_files() returns all test files matching expected patterns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file structure
        os.makedirs(os.path.join(tmpdir, "tests"))
        os.makedirs(os.path.join(tmpdir, "src"))
        os.makedirs(os.path.join(tmpdir, "src", "nested"))
        
        # Create test files with various patterns (relative paths since find_test_files returns relative)
        test_files = [
            "tests/test_example.py",
            "tests/example_test.py",
            "src/mytest.py",
            "src/nested/test_nested.py",
            "src/nested/nested_test.py",
        ]
        
        # Create non-test files (should not be included)
        non_test_files = [
            "src/main.py",
            "src/utils.py",
            "README.md",
        ]
        
        for f in test_files + non_test_files:
            full_path = os.path.join(tmpdir, f)
            with open(full_path, "w") as fh:
                fh.write("# test file\n" if f in test_files else "# source file\n")
        
        # Change to temp directory and run find_test_files
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            result = find_test_files()
            
            # Verify all test files are found
            result_set = set(result)
            for tf in test_files:
                assert tf in result_set, f"Expected test file {tf} not found in {result_set}"
            
            # Verify non-test files are not included
            for ntf in non_test_files:
                assert ntf not in result_set, f"Non-test file {ntf} should not be included"
        finally:
            os.chdir(original_cwd)


# BDD: Extract all scenarios from BDD.md
def test_extract_all_scenarios_from_bdd_md():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("---\n")
        f.write("language: python\n")
        f.write("---\n")
        f.write("\n")
        f.write("Feature: Login System\n")
        f.write("    Scenario: User logs in successfully\n")
        f.write("    Scenario: User fails with wrong password\n")
        f.write("\n")
        f.write("Feature: Registration\n")
        f.write("    Scenario: New user registers\n")
        f.write("    Scenario: Duplicate email rejected\n")
        f.write("\n")
        f.write("Feature: Session Management\n")
        f.write("    Scenario Outline: Logout from <device>\n")
        f.flush()

        scenarios = parse_scenarios(f.name)

        assert len(scenarios) == 5
        assert scenarios[0] == ("Login System", "User logs in successfully")
        assert scenarios[1] == ("Login System", "User fails with wrong password")
        assert scenarios[2] == ("Registration", "New user registers")
        assert scenarios[3] == ("Registration", "Duplicate email rejected")
        assert scenarios[4] == ("Session Management", "Logout from <device>")

        os.unlink(f.name)


# BDD: Parse scenario outline syntax
def test_parse_scenario_outline_syntax():
    """Test that Scenario Outline is treated the same as Scenario."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("---\n")
        f.write("language: python\n")
        f.write("---\n")
        f.write("\n")
        f.write("Feature: Authentication\n")
        f.write("    Scenario: Login with valid credentials\n")
        f.write("    Scenario Outline: Login with <role>\n")
        f.write("        Given a user with role <role>\n")
        f.write("        When they attempt to login\n")
        f.write("        Then access is granted\n")
        f.write("\n")
        f.write("    Examples:\n")
        f.write("        | role  |\n")
        f.write("        | admin |\n")
        f.write("        | user  |\n")
        f.flush()

        scenarios = parse_scenarios(f.name)

        # Should find both regular Scenario and Scenario Outline
        assert len(scenarios) == 2
        assert scenarios[0] == ("Authentication", "Login with valid credentials")
        assert scenarios[1] == ("Authentication", "Login with <role>")

        os.unlink(f.name)


# BDD: Skip frontmatter when parsing scenarios
def test_skip_frontmatter_when_parsing_scenarios():
    """Test that YAML frontmatter lines are not included as scenarios."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        # Create a BDD.md with 10 lines of YAML frontmatter
        f.write("---\n")
        f.write("language: python\n")
        f.write("framework: none\n")
        f.write("build_cmd: npm run build\n")
        f.write("test_cmd: npm test\n")
        f.write("lint_cmd: npm run lint\n")
        f.write("fmt_cmd: npm run format\n")
        f.write("birth_date: 2026-03-05\n")
        f.write("custom_key: custom_value\n")
        f.write("another_key: another_value\n")
        f.write("---\n")
        f.write("\n")
        f.write("Feature: Test Feature\n")
        f.write("    Scenario: A real scenario\n")
        f.write("    Scenario: Another real scenario\n")
        f.flush()

        scenarios = parse_scenarios(f.name)

        # Should only find the 2 real scenarios, not any frontmatter lines
        assert len(scenarios) == 2, f"Expected 2 scenarios, got {len(scenarios)}: {scenarios}"
        assert scenarios[0] == ("Test Feature", "A real scenario")
        assert scenarios[1] == ("Test Feature", "Another real scenario")
        
        # Verify no frontmatter content leaked into scenarios
        for feature, scenario in scenarios:
            assert ":" not in scenario or "<" in scenario, f"Frontmatter line leaked into scenario: {scenario}"
            assert scenario not in ["language: python", "framework: none", "build_cmd: npm run build",
                                    "test_cmd: npm test", "lint_cmd: npm run lint", "fmt_cmd: npm run format",
                                    "birth_date: 2026-03-05", "custom_key: custom_value", "another_key: another_value"]

        os.unlink(f.name)


# BDD: Exclude non-source directories from test search
def test_exclude_non_source_directories_from_test_search():
    """Test that find_test_files() skips files inside excluded directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            # Create a real test file that should be found
            os.makedirs("tests")
            with open("tests/test_real.py", "w") as f:
                f.write("# real test\n")

            # Create test files inside excluded directories — should be ignored
            for excluded in [".git", "node_modules", ".venv", "__pycache__", "build"]:
                os.makedirs(excluded)
                with open(f"{excluded}/test_ignored.py", "w") as f:
                    f.write("# ignored test\n")

            result = find_test_files()
            result_set = set(result)

            assert "tests/test_real.py" in result_set, "Real test file should be found"
            for excluded in [".git", "node_modules", ".venv", "__pycache__", "build"]:
                assert f"{excluded}/test_ignored.py" not in result_set, (
                    f"File in {excluded}/ should be excluded"
                )
        finally:
            os.chdir(original_cwd)


# BDD: Detect coverage via BDD marker comment
def test_detect_coverage_via_bdd_marker_comment():
    """Test that check_marker() finds '# BDD: <scenario name>' in test file content."""
    scenario = "Detect coverage via BDD marker comment"

    # File containing the exact marker should be found
    contents_with_marker = {
        "tests/test_example.py": f"# BDD: {scenario}\ndef test_something(): pass\n"
    }
    result = check_marker(scenario, contents_with_marker)
    assert result == "tests/test_example.py", "Should find file containing the BDD marker"

    # File without the marker should not match
    contents_without_marker = {
        "tests/test_other.py": "def test_unrelated(): pass\n"
    }
    result = check_marker(scenario, contents_without_marker)
    assert result is None, "Should return None when marker is absent"

    # JS/TS style '// BDD:' marker should also be detected
    contents_js_marker = {
        "src/example.test.ts": f"// BDD: {scenario}\ntest('x', () => {{}});\n"
    }
    result = check_marker(scenario, contents_js_marker)
    assert result == "src/example.test.ts", "Should find JS-style // BDD: marker"


# BDD: Handle empty BDD.md with no scenarios
def test_handle_empty_bdd_md_with_no_scenarios():
    """Test that check_bdd_coverage.py handles BDD.md with frontmatter but no scenarios."""
    import subprocess

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("---\n")
        f.write("language: python\n")
        f.write("framework: none\n")
        f.write("---\n")
        f.write("\n")
        f.write("# This BDD.md has no Feature or Scenario sections\n")
        f.flush()

        # Run check_bdd_coverage.py on the empty BDD.md
        result = subprocess.run(
            [sys.executable, "scripts/check_bdd_coverage.py", f.name],
            capture_output=True,
            text=True,
        )

        # Should output "No scenarios found in BDD.md" and exit with code 0
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. stderr: {result.stderr}"
        assert "No scenarios found in BDD.md" in result.stdout, f"Expected 'No scenarios found in BDD.md' in output. Got: {result.stdout}"

        os.unlink(f.name)
