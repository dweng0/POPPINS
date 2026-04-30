#!/usr/bin/env python3
"""Tests for orchestrate.py - orchestrator for parallel agent workers"""

import sys
import os
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from orchestrate import (
    scenario_to_slug,
    get_uncovered_scenarios,
    select_scenarios,
    create_worktree,
)


# BDD: Slug truncates to 60 characters
def test_slug_truncates_to_60_characters():
    """Test that scenario_to_slug() truncates long names to max 60 characters."""
    long_name = "This is a very long scenario name that exceeds sixty characters and should be truncated properly"

    slug = scenario_to_slug(long_name)

    assert len(slug) <= 60, f"Slug length {len(slug)} exceeds 60 characters: {slug}"
    assert slug == slug.lower(), "Slug should be lowercase"
    assert all(c.isalnum() or c == "-" for c in slug), (
        "Slug should only contain alphanumeric and hyphens"
    )


# BDD: Find uncovered scenarios for orchestration
def test_find_uncovered_scenarios_for_orchestration():
    """get_uncovered_scenarios returns all scenarios lacking test coverage."""
    bdd_content = """---
language: python
build_cmd: echo ok
test_cmd: echo ok
---

Feature: Test Feature
    Scenario: Alpha scenario one
        Given something
        Then something

    Scenario: Beta scenario two
        Given another thing
        Then another thing

    Scenario: Gamma scenario three
        Given third thing
        Then third thing

    Scenario: Delta scenario four
        Given fourth
        Then fourth

    Scenario: Epsilon scenario five
        Given fifth
        Then fifth

    Scenario: Zeta scenario six
        Given sixth
        Then sixth

    Scenario: Eta scenario seven
        Given seventh
        Then seventh

    Scenario: Theta scenario eight
        Given eighth
        Then eighth
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bdd_content)
        bdd_path = f.name

    try:
        with patch("orchestrate.find_test_files", return_value=[]):
            result = get_uncovered_scenarios(bdd_path)
    finally:
        os.unlink(bdd_path)

    assert len(result) == 8, (
        f"Expected 8 uncovered scenarios, got {len(result)}: {result}"
    )
    scenario_names = [s for _, s in result]
    assert "Alpha scenario one" in scenario_names
    assert "Theta scenario eight" in scenario_names


# BDD: Select top N scenarios for parallel run
def test_select_top_n_scenarios_for_parallel_run():
    """select_scenarios(ordered_names, max_agents) returns only top N scenarios."""
    ordered = [f"Scenario {i}" for i in range(1, 11)]  # 10 scenarios

    selected, remaining = select_scenarios(ordered, max_agents=3)

    assert len(selected) == 3, f"Expected 3 selected, got {len(selected)}"
    assert selected == ["Scenario 1", "Scenario 2", "Scenario 3"]
    assert len(remaining) == 7
    assert remaining == [f"Scenario {i}" for i in range(4, 11)]


# BDD: Run agents in parallel with ThreadPoolExecutor
def test_run_agents_in_parallel_with_threadpoool_executor():
    """orchestrate.py uses ThreadPoolExecutor to spawn multiple agent workers concurrently."""
    import os

    scripts_dir = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    )
    orchestrate_path = scripts_dir + "/orchestrate.py"

    with open(orchestrate_path) as f:
        source = f.read()

    assert "ThreadPoolExecutor" in source, (
        "orchestrate.py should use ThreadPoolExecutor for parallel execution"
    )


# BDD: Create worktrees for parallel scenarios
def test_create_worktrees_for_parallel_scenarios():
    """create_worktree creates isolated worktrees with unique branches for 3 scenarios."""
    orig = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            os.chdir(tmpdir)
            os.system("git init > /dev/null 2>&1")
            os.system("git config user.email 'test@example.com'")
            os.system("git config user.name 'Test User'")
            os.system(
                "touch README.md && git add README.md && git commit -m 'init' > /dev/null 2>&1"
            )

            main_dir = tmpdir
            scenarios = ["Scenario 1", "Scenario 2", "Scenario 3"]

            worktrees = []
            for scenario in scenarios:
                slug = scenario_to_slug(scenario)
                wt_path, branch = create_worktree(slug, main_dir)
                worktrees.append((wt_path, branch, scenario))

            assert len(worktrees) == 3, f"Expected 3 worktrees, got {len(worktrees)}"

            for wt_path, branch, scenario in worktrees:
                assert wt_path is not None, (
                    f"Worktree path should not be None for {scenario}"
                )
                assert branch is not None, f"Branch should not be None for {scenario}"
                assert os.path.isdir(wt_path), (
                    f"Worktree directory should exist: {wt_path}"
                )
                assert branch.startswith("agent/"), (
                    f"Branch should start with 'agent/': {branch}"
                )
                assert scenario_to_slug(scenario) in branch, (
                    f"Branch should contain scenario slug: {branch}"
                )

            branches = [branch for _, branch, _ in worktrees]
            assert len(set(branches)) == 3, "All branches should be unique"

            wt_paths = [wt_path for wt_path, _, _ in worktrees]
            assert len(set(wt_paths)) == 3, "All worktree paths should be unique"
        finally:
            os.chdir(orig)
