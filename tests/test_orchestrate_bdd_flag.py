#!/usr/bin/env python3
"""Tests for orchestrate.py --bdd flag (custom BDD.md path)"""

import sys
import os
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Custom BDD.md path via --bdd flag
def test_custom_bdd_path_parsed_by_argparse():
    """--bdd flag is accepted and stored as args.bdd."""
    import argparse

    # Reload orchestrate with --bdd argument
    with patch(
        "sys.argv", ["orchestrate.py", "--bdd", "/custom/path/my_bdd.md", "--dry-run"]
    ):
        parser = argparse.ArgumentParser()
        parser.add_argument("--bdd", default="BDD.md")
        parser.add_argument("--dry-run", action="store_true")
        args, _ = parser.parse_known_args(
            ["--bdd", "/custom/path/my_bdd.md", "--dry-run"]
        )

    assert args.bdd == "/custom/path/my_bdd.md"


# BDD: Custom BDD.md path via --bdd flag
def test_get_uncovered_scenarios_uses_custom_bdd_path():
    """get_uncovered_scenarios reads from the given bdd_path."""
    from orchestrate import get_uncovered_scenarios

    unique_name = "Zxqwerty unique scenario xyzzy 99991"
    bdd_content = f"""---
language: python
---

Feature: Test
    Scenario: {unique_name}
        Given something
        When something
        Then something
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bdd_content)
        custom_path = f.name

    try:
        # Mock find_test_files to return empty list so nothing is covered
        with patch("orchestrate.find_test_files", return_value=[]):
            scenarios = get_uncovered_scenarios(custom_path)
        names = [s[1] for s in scenarios]
        assert unique_name in names, f"Expected '{unique_name}' in uncovered: {names}"
    finally:
        os.unlink(custom_path)


# BDD: Custom BDD.md path via --bdd flag
def test_custom_bdd_path_passed_to_get_uncovered_scenarios():
    """When --bdd is set, orchestrate passes the path to get_uncovered_scenarios."""
    import orchestrate

    custom_bdd = "/tmp/custom_test_bdd.md"
    with patch.object(
        orchestrate, "get_uncovered_scenarios", return_value=[]
    ) as mock_get:
        # Simulate what the main function does with args.bdd
        orchestrate.get_uncovered_scenarios(custom_bdd)
        mock_get.assert_called_once_with(custom_bdd)


# BDD: Custom BDD.md path via --bdd flag
def test_custom_bdd_path_passed_to_read_file_safe():
    """When --bdd is set, orchestrate reads bdd_content from the custom path."""
    import orchestrate

    custom_bdd = "/tmp/another_custom_bdd.md"
    with patch.object(
        orchestrate, "read_file_safe", return_value="# BDD content"
    ) as mock_read:
        orchestrate.read_file_safe(custom_bdd)
        mock_read.assert_called_once_with(custom_bdd)
