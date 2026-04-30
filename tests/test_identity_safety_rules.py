#!/usr/bin/env python3
"""Tests for Identity and Safety Rules — verifies IDENTITY.md declares the rules."""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _identity():
    with open(os.path.join(ROOT, "IDENTITY.md")) as f:
        return f.read()


# BDD: Never modify IDENTITY.md
def test_identity_md_exists():
    assert os.path.exists(os.path.join(ROOT, "IDENTITY.md"))


# BDD: Never modify IDENTITY.md
def test_identity_md_declares_no_modify_self():
    content = _identity()
    assert "IDENTITY.md" in content
    assert "never" in content.lower() or "Never" in content


# BDD: Never modify scripts/evolve.sh
def test_evolve_sh_exists():
    assert os.path.exists(os.path.join(ROOT, "scripts", "evolve.sh"))


# BDD: Never modify scripts/evolve.sh
def test_identity_md_declares_no_modify_evolve_sh():
    content = _identity()
    assert "evolve.sh" in content


# BDD: Never modify .github/workflows/
def test_workflows_dir_exists():
    assert os.path.isdir(os.path.join(ROOT, ".github", "workflows"))


# BDD: Never modify .github/workflows/
def test_identity_md_declares_no_modify_workflows():
    content = _identity()
    assert ".github/workflows" in content or "workflows" in content


# BDD: Only build features from BDD.md
def test_identity_md_declares_bdd_as_source_of_truth():
    content = _identity()
    assert "BDD.md" in content
    assert "source of truth" in content.lower() or "spec" in content.lower()


# BDD: Only build features from BDD.md
def test_identity_md_no_features_outside_bdd():
    content = _identity()
    # Rule 1 explicitly says not to build things not in BDD.md
    assert (
        "not in BDD.md" in content
        or "outside BDD" in content
        or "do not build" in content.lower()
    )
