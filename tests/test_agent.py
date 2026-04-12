#!/usr/bin/env python3
"""Tests for agent.py provider detection"""

import os
import sys

sys.path.insert(0, "scripts")
from agent import detect_provider


# BDD: Detect Anthropic provider from API key
def test_detect_anthropic_provider_from_api_key():
    """Test that detect_provider() returns 'anthropic' when ANTHROPIC_API_KEY is set."""
    # Save original environment
    original_anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    original_poppins_cfg_provider = None
    
    try:
        # Remove any existing ANTHROPIC_API_KEY
        os.environ.pop("ANTHROPIC_API_KEY", None)
        
        # Set ANTHROPIC_API_KEY
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key"
        
        # Need to reimport to pick up the new environment variable
        # Since detect_provider uses module-level _POPPINS_CFG, we need to test differently
        # The function checks PROVIDER_PRIORITY which includes ANTHROPIC_API_KEY
        result = detect_provider()
        
        # Verify it returns 'anthropic'
        assert result == "anthropic", f"Expected 'anthropic', got '{result}'"
        
    finally:
        # Restore original environment
        if original_anthropic_key is not None:
            os.environ["ANTHROPIC_API_KEY"] = original_anthropic_key
        else:
            os.environ.pop("ANTHROPIC_API_KEY", None)
