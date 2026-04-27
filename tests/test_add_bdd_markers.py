#!/usr/bin/env python3
"""Tests for scripts/add_bdd_markers.py"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
<<<<<<< HEAD
from add_bdd_markers import detect_comment_prefix, has_existing_marker, add_marker_to_file
=======
from add_bdd_markers import detect_comment_prefix, compute_planned_changes, format_output
>>>>>>> agent/dry-run-mode-shows-planned-changes-20260427-212352


# BDD: Detect comment prefix by file extension
def test_detect_comment_prefix_by_file_extension():
    """Detect comment prefix by file extension."""
    assert detect_comment_prefix("file.py") == "#"


# BDD: Detect JavaScript comment prefix
def test_detect_javascript_comment_prefix():
    assert detect_comment_prefix("file.test.js") == "//"


<<<<<<< HEAD
# BDD: Skip if marker already exists
def test_skip_if_marker_already_exists():
    """If a BDD marker already exists above the target line, add_marker_to_file returns None."""
    content = "# BDD: Login with valid credentials\ndef test_login_with_valid_credentials():\n    pass\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(content)
        f.flush()
        tmp_path = f.name

    try:
        # Line index 1 is the "def test_login..." line; line index 0 has the marker
        result = add_marker_to_file(tmp_path, line_index=1, scenario_name="Login with valid credentials", prefix="#")
        assert result is None, f"Expected None (marker already exists), got: {result!r}"

        # Verify file was not modified
        with open(tmp_path) as f:
            assert f.read() == content, "File content should be unchanged"
    finally:
        os.unlink(tmp_path)
=======
# BDD: Dry run mode shows planned changes
def test_dry_run_mode_shows_planned_changes():
    """Dry run mode shows planned changes without modifying files."""
    test_contents = {
        "tests/test_example.py": "def test_detect_coverage_via_bdd_marker_comment():\n    pass\n"
    }
    scenarios = [("Test Coverage Detection", "Detect coverage via BDD marker comment")]

    planned = compute_planned_changes(scenarios, test_contents)

    # Assert exactly one planned change
    assert len(planned) == 1
    assert planned[0]["scenario_name"] == "Detect coverage via BDD marker comment"
    assert planned[0]["filepath"] == "tests/test_example.py"
    assert planned[0]["line_index"] == 0
    assert planned[0]["prefix"] == "#"
    assert planned[0]["match_type"] in ("full", "partial", "words")

    # Assert dry-run output formatting
    output = format_output(planned, applied_count=1, skipped_has_marker=0, skipped_no_match=0, apply_mode=False)
    assert "[would add]" in output
    assert "[add]" not in output.replace("[would add]", "")
>>>>>>> agent/dry-run-mode-shows-planned-changes-20260427-212352
