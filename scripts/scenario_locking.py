#!/usr/bin/env python3
"""Scenario locking utilities for parallel agent execution."""

import re


def scenario_to_slug(scenario_name: str) -> str:
    """Convert a scenario name to a URL-safe slug.
    
    Args:
        scenario_name: The scenario name (e.g., "Login with valid credentials")
    
    Returns:
        A lowercase slug with alphanumeric characters and hyphens only
        (e.g., "login-with-valid-credentials")
    """
    # Convert to lowercase
    slug = scenario_name.lower()
    
    # Replace any non-alphanumeric character (except hyphens) with a hyphen
    slug = re.sub(r'[^a-z0-9-]', '-', slug)
    
    # Replace multiple consecutive hyphens with a single hyphen
    slug = re.sub(r'-+', '-', slug)
    
    # Strip leading and trailing hyphens
    slug = slug.strip('-')
    
    return slug
