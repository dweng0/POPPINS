#!/usr/bin/env python3
"""Tests for agent provider detection"""

import os
import subprocess
import sys
import tempfile


# BDD: Detect custom provider from base URL
def test_detect_custom_provider_from_base_url():
    """Test that detect_provider() returns 'custom' when CUSTOM_BASE_URL is set."""
    # Create a small test script that imports and calls detect_provider
    test_script = """
import os
import sys
sys.path.insert(0, 'scripts')
# Clear any existing provider-related env vars to isolate the test
for key in ['ANTHROPIC_API_KEY', 'MOONSHOT_API_KEY', 'DASHSCOPE_API_KEY', 
            'OPENAI_API_KEY', 'GROQ_API_KEY', 'CUSTOM_API_KEY', 'OLLAMA_HOST']:
    if key in os.environ:
        del os.environ[key]

from agent import detect_provider
result = detect_provider()
print(result)
"""
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_script)
        script_path = f.name
    
    try:
        # Run the script with CUSTOM_BASE_URL set
        env = os.environ.copy()
        env["CUSTOM_BASE_URL"] = "https://custom.api.example.com/v1"
        # Clear other provider keys to ensure clean test
        for key in ['ANTHROPIC_API_KEY', 'MOONSHOT_API_KEY', 'DASHSCOPE_API_KEY', 
                    'OPENAI_API_KEY', 'GROQ_API_KEY', 'CUSTOM_API_KEY', 'OLLAMA_HOST']:
            env.pop(key, None)
        
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            env=env,
        )
        
        # Should return "custom"
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert result.stdout.strip() == "custom", f"Expected 'custom', got '{result.stdout.strip()}'"
    finally:
        os.unlink(script_path)
