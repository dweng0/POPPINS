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
