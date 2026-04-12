#!/usr/bin/env python3
"""Tests for orchestrate.py - orchestrator for parallel agent workers"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from orchestrate import scenario_to_slug


# BDD: Slug truncates to 60 characters
def test_slug_truncates_to_60_characters():
    """Test that scenario_to_slug() truncates long names to max 60 characters."""
    # Create a scenario name that is very long (100+ chars)
    long_name = "This is a very long scenario name that exceeds sixty characters and should be truncated properly"
    
    slug = scenario_to_slug(long_name)
    
    # The slug should be at most 60 characters
    assert len(slug) <= 60, f"Slug length {len(slug)} exceeds 60 characters: {slug}"
    
    # The slug should still be a valid slug (lowercase, hyphens only for separators)
    assert slug == slug.lower(), "Slug should be lowercase"
    assert all(c.isalnum() or c == '-' for c in slug), "Slug should only contain alphanumeric and hyphens"
