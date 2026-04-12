#!/usr/bin/env python3
"""Tests for check_bdd_coverage.py"""

import os
import sys
import tempfile

sys.path.insert(0, "scripts")
from check_bdd_coverage import parse_scenarios, find_test_files


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
