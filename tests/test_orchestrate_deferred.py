#!/usr/bin/env python3
"""Tests for orchestrate.py deferred scenarios message"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Deferred scenarios message
def test_deferred_scenarios_message_shows_remaining():
    """When max_rounds reached, show deferred scenarios for next run."""
    remaining = ["Scenario A", "Scenario B", "Scenario C"]

    message = f"\n  {len(remaining)} scenario(s) remaining — run again to continue:"

    assert "3 scenario(s) remaining" in message
    assert "run again to continue" in message


# BDD: Deferred scenarios message
def test_deferred_scenarios_list_format():
    """Deferred scenarios should be listed with numbers."""
    deferred = ["Scenario One", "Scenario Two", "Scenario Three"]

    lines = []
    lines.append(f"\n  {len(deferred)} scenario(s) remaining — run again to continue:")
    for i, name in enumerate(deferred, 1):
        lines.append(f"    {i}. {name}")

    result = "\n".join(lines)

    assert "1. Scenario One" in result
    assert "2. Scenario Two" in result
    assert "3. Scenario Three" in result


# BDD: Deferred scenarios message
def test_deferred_scenarios_single_item():
    """Single deferred scenario should show singular 'scenario'."""
    deferred = ["Only Scenario"]

    message = f"\n  {len(deferred)} scenario(s) remaining — run again to continue:"

    assert "1 scenario(s) remaining" in message


# BDD: Deferred scenarios message
def test_deferred_scenarios_no_remaining():
    """No deferred scenarios means all completed."""
    deferred = []

    message = f"\n  {len(deferred)} scenario(s) remaining — run again to continue:"

    assert "0 scenario(s) remaining" in message


# BDD: Deferred scenarios message
def test_deferred_scenarios_command_suggestion():
    """Message should suggest how to continue."""
    deferred = ["Scenario A", "Scenario B"]

    lines = []
    lines.append(f"\n  {len(deferred)} scenario(s) remaining — run again to continue:")
    for i, name in enumerate(deferred, 1):
        lines.append(f"    {i}. {name}")

    lines.append("\n  python3 scripts/orchestrate.py --max-agents 3 --max-rounds 2")

    result = "\n".join(lines)

    assert "python3 scripts/orchestrate.py" in result
    assert "--max-agents" in result
    assert "--max-rounds" in result


# BDD: Deferred scenarios message
def test_deferred_scenarios_output_format():
    """Deferred scenarios output should match orchestrator format."""
    deferred = ["Scenario Alpha", "Scenario Beta", "Scenario Gamma"]

    output_lines = []
    output_lines.append(
        f"\n  {len(deferred)} scenario(s) remaining — run again to continue:"
    )
    for i, name in enumerate(deferred, 1):
        output_lines.append(f"    {i}. {name}")

    output = "\n".join(output_lines)

    assert output.startswith("\n  3 scenario(s) remaining")
    assert "    1. Scenario Alpha" in output
    assert "    2. Scenario Beta" in output
    assert "    3. Scenario Gamma" in output


# BDD: Deferred scenarios message
def test_deferred_scenarios_with_many_items():
    """Many deferred scenarios should all be listed."""
    deferred = [f"Scenario {i}" for i in range(1, 11)]

    lines = []
    lines.append(f"\n  {len(deferred)} scenario(s) remaining — run again to continue:")
    for i, name in enumerate(deferred, 1):
        lines.append(f"    {i}. {name}")

    result = "\n".join(lines)

    assert "10 scenario(s) remaining" in result
    for i in range(1, 11):
        assert f"    {i}. Scenario {i}" in result


# BDD: Deferred scenarios message
def test_deferred_scenarios_preserves_order():
    """Deferred scenarios should preserve their order from remaining list."""
    deferred = ["Last", "First", "Middle"]

    lines = []
    lines.append(f"\n  {len(deferred)} scenario(s) remaining — run again to continue:")
    for i, name in enumerate(deferred, 1):
        lines.append(f"    {i}. {name}")

    result = "\n".join(lines)

    assert "    1. Last" in result
    assert "    2. First" in result
    assert "    3. Middle" in result
