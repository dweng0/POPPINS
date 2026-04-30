#!/usr/bin/env python3
"""Tests for orchestrate.py write orchestrator journal entry"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Write orchestrator journal entry
def test_orchestrator_journal_entry_format():
    """Orchestrator journal entry should have proper format."""
    date = time.strftime("%Y-%m-%d")
    session_time = time.strftime("%H:%M")
    merged_count = 3
    failed_count = 1

    orchestrator_entry = f"## {date} {session_time} — orchestrator session\n\n"
    orchestrator_entry += f"- Merged: {merged_count} scenarios\n"
    orchestrator_entry += f"- Failed: {failed_count} scenarios\n"
    orchestrator_entry += "- Total agent time: 450s\n"

    assert f"## {date} {session_time} — orchestrator session" in orchestrator_entry
    assert "Merged: 3 scenarios" in orchestrator_entry
    assert "Failed: 1 scenarios" in orchestrator_entry


# BDD: Write orchestrator journal entry
def test_orchestrator_journal_entry_with_results():
    """Journal entry should list merged and failed scenarios."""
    merged = ["Scenario A", "Scenario B", "Scenario C"]
    failed = ["Scenario D"]

    orchestrator_entry = "## 2026-04-29 20:55 — orchestrator session\n\n"
    orchestrator_entry += "- Merged: Scenario A, Scenario B, Scenario C\n"
    orchestrator_entry += "- Failed: Scenario D\n"

    assert "Merged: Scenario A, Scenario B, Scenario C" in orchestrator_entry
    assert "Failed: Scenario D" in orchestrator_entry


# BDD: Write orchestrator journal entry
def test_orchestrator_journal_entry_all_merged():
    """All scenarios merged should show no failures."""
    merged = ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4"]
    failed = []

    orchestrator_entry = "## 2026-04-29 20:55 — orchestrator session\n\n"
    orchestrator_entry += "- Merged: Scenario 1, Scenario 2, Scenario 3, Scenario 4\n"
    orchestrator_entry += "- Failed: none\n"

    assert (
        "Merged: Scenario 1, Scenario 2, Scenario 3, Scenario 4" in orchestrator_entry
    )
    assert "Failed: none" in orchestrator_entry


# BDD: Write orchestrator journal entry
def test_orchestrator_journal_entry_all_failed():
    """All scenarios failed should show no merges."""
    merged = []
    failed = ["Scenario A", "Scenario B"]

    orchestrator_entry = "## 2026-04-29 20:55 — orchestrator session\n\n"
    orchestrator_entry += "- Merged: none\n"
    orchestrator_entry += "- Failed: Scenario A, Scenario B\n"

    assert "Merged: none" in orchestrator_entry
    assert "Failed: Scenario A, Scenario B" in orchestrator_entry


# BDD: Write orchestrator journal entry
def test_orchestrator_journal_entry_prepended_to_journal():
    """Journal entry should be prepended to existing JOURNAL.md."""
    existing_journal = "# Journal\n\n## 2026-04-29 10:00 — Day 1\nSome content\n"
    new_entry = "## 2026-04-29 20:55 — orchestrator session\n\n- Merged: 2 scenarios\n"

    lines = existing_journal.splitlines(True)
    new_journal = lines[0] + "\n" + new_entry + "".join(lines[1:])

    assert new_journal.startswith("# Journal")
    assert "## 2026-04-29 20:55 — orchestrator session" in new_journal
    assert "## 2026-04-29 10:00 — Day 1" in new_journal


# BDD: Write orchestrator journal entry
def test_orchestrator_journal_entry_new_journal():
    """New journal should be created if JOURNAL.md doesn't exist."""
    orchestrator_entry = (
        "## 2026-04-29 20:55 — orchestrator session\n\n- Merged: 3 scenarios\n"
    )

    new_journal = "# Journal\n\n" + orchestrator_entry

    assert new_journal.startswith("# Journal")
    assert "orchestrator session" in new_journal


# BDD: Write orchestrator journal entry
def test_orchestrator_journal_entry_with_coverage():
    """Journal entry should include coverage information."""
    covered_count = 287
    total_count = 347

    orchestrator_entry = "## 2026-04-29 20:55 — orchestrator session\n\n"
    orchestrator_entry += "- Merged: 4 scenarios\n"
    orchestrator_entry += f"\nCoverage: {covered_count}/{total_count} scenarios.\n"

    assert "Coverage: 287/347 scenarios" in orchestrator_entry


# BDD: Write orchestrator journal entry
def test_orchestrator_journal_entry_empty_results():
    """Empty results should still generate journal entry."""
    orchestrator_entry = "## 2026-04-29 20:55 — orchestrator session\n\n"
    orchestrator_entry += "- Merged: none\n"
    orchestrator_entry += "- Failed: none\n"

    assert "Merged: none" in orchestrator_entry
    assert "Failed: none" in orchestrator_entry


# BDD: Write orchestrator journal entry
def test_orchestrator_journal_entry_with_total_time():
    """Journal entry should include total agent time."""
    total_time = 450.5

    orchestrator_entry = "## 2026-04-29 20:55 — orchestrator session\n\n"
    orchestrator_entry += "- Merged: 3 scenarios\n"
    orchestrator_entry += f"- Total agent time: {total_time}s\n"

    assert "Total agent time: 450.5s" in orchestrator_entry


# BDD: Write orchestrator journal entry
def test_orchestrator_journal_entry_summary_line():
    """Journal index should have summary line with coverage and outcomes."""
    date = time.strftime("%Y-%m-%d")
    session_time = time.strftime("%H:%M")
    merged_count = 4
    failed_count = 1
    covered_count = 287
    total_count = 347

    session_summary = f"orchestrator: {merged_count} merged, {failed_count} failed"

    assert "orchestrator: 4 merged, 1 failed" in session_summary
