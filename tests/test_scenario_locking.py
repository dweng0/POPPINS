#!/usr/bin/env python3
"""Tests for scenario locking functionality."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from scenario_locking import scenario_to_slug


# BDD: Generate scenario slug from name
def test_generate_scenario_slug_from_name():
    """Test that scenario names are converted to slugs correctly."""
    # Basic case from BDD spec
    assert scenario_to_slug("Login with valid credentials") == "login-with-valid-credentials"
    
    # Additional edge cases for robustness
    assert scenario_to_slug("Simple") == "simple"
    assert scenario_to_slug("Multiple   spaces") == "multiple-spaces"
    assert scenario_to_slug("Special@#$characters") == "special-characters"
    assert scenario_to_slug("Mixed123Numbers") == "mixed123numbers"
    assert scenario_to_slug("UPPERCASE") == "uppercase"
    assert scenario_to_slug("with-dashes") == "with-dashes"
    assert scenario_to_slug("with_underscores") == "with-underscores"


# BDD: Slug truncates to 60 characters
def test_slug_truncates_to_60_characters():
    """Test that scenario_to_slug truncates slugs to 60 characters."""
    # Very long scenario name should be truncated
    long_name = "A" * 100
    slug = scenario_to_slug(long_name)
    assert len(slug) <= 60
    assert slug == "a" * 60
    
    # Scenario name at exactly 60 chars should not be truncated
    exact_name = "A" * 60
    slug = scenario_to_slug(exact_name)
    assert len(slug) == 60
    
    # Scenario name at 61 chars should be truncated to 60
    over_name = "A" * 61
    slug = scenario_to_slug(over_name)
    assert len(slug) == 60
