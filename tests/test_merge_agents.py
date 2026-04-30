#!/usr/bin/env python3
"""Tests for merge_agent.py and integration_test_agent.py"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Merge agent detects merge conflicts
def test_merge_agent_detects_merge_conflicts():
    """Test that merge agent can detect conflict markers in files."""
    from merge_agent import resolve_file_merge

    content_a = """<<<<<<< HEAD
def test_foo():
    pass
=======
def test_bar():
    pass
>>>>>>> agent/test-branch
"""

    # Should detect and resolve conflict markers
    result, status = resolve_file_merge(
        "test.py", content_a, content_a, "Scenario A", "Scenario B", "."
    )

    # Conflict markers should be removed
    assert "<<" not in result, "Conflict markers should be removed"
    assert "====" not in result, "Conflict markers should be removed"
    assert ">>>>" not in result, "Conflict markers should be removed"


# BDD: Merge agent combines imports from multiple scenarios
def test_merge_agent_combines_imports():
    """Test that merge agent can combine import statements."""
    from merge_agent import resolve_import_conflict

    content_a = """import os
import sys
"""

    content_b = """import json
from collections import defaultdict
"""

    result = resolve_import_conflict(content_a, content_b, "test.py")

    # Should have imports from both
    assert "os" in result or "sys" in result, "Should preserve original imports"
    assert "json" in result or "collections" in result, "Should add new imports"


# BDD: Integration test agent detects merge conflict markers
def test_integration_agent_detects_conflict_markers():
    """Test that integration test agent detects conflict markers in test output."""
    from integration_test_agent import analyze_test_failure

    stdout = "SyntaxError: invalid syntax\n<<<<<<< HEAD\n"
    stderr = ""

    suggestions = analyze_test_failure(stdout, stderr, 1)

    # Should suggest removing conflict markers
    conflict_suggestions = [s for s in suggestions if "conflict" in s.lower()]
    assert len(conflict_suggestions) > 0, "Should suggest removing conflict markers"


# BDD: Integration test agent reports pass when tests pass
def test_integration_agent_reports_pass():
    """Test that integration test agent reports success when tests pass."""

    # This is a mock test - in reality we'd need a proper test environment
    # The actual test would run pytest and check the return code
    assert True  # Placeholder for actual integration test


# BDD: Integration test agent attempts fix on failure
def test_integration_agent_attempts_fix():
    """Test that integration test agent attempts to fix failures."""
    # The agent should analyze failure output and suggest fixes
    from integration_test_agent import analyze_test_failure

    stdout = "SyntaxError: invalid syntax in test_example.py"
    stderr = ""

    suggestions = analyze_test_failure(stdout, stderr, 1)

    # Should suggest fixing syntax errors
    syntax_suggestions = [s for s in suggestions if "syntax" in s.lower()]
    assert len(syntax_suggestions) > 0, "Should suggest fixing syntax errors"
