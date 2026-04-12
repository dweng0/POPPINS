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


# BDD: Set OLLAMA_HOST from poppins.yml base_url
def test_set_ollama_host_from_poppins_yml_base_url():
    """Test that OLLAMA_HOST is set from poppins.yml base_url (strips /v1 suffix)."""
    # Get absolute path to scripts directory
    scripts_dir = os.path.abspath("scripts")
    
    # Create a small test script that imports agent and checks OLLAMA_HOST
    test_script = f"""
import os
import sys
sys.path.insert(0, '{scripts_dir}')

# Clear any existing provider-related env vars to isolate the test
for key in ['ANTHROPIC_API_KEY', 'MOONSHOT_API_KEY', 'DASHSCOPE_API_KEY', 
            'OPENAI_API_KEY', 'GROQ_API_KEY', 'CUSTOM_API_KEY', 'CUSTOM_BASE_URL', 'OLLAMA_HOST']:
    if key in os.environ:
        del os.environ[key]

# Read OLLAMA_HOST after agent module loads (which applies poppins config)
from agent import detect_provider
ollama_host = os.environ.get("OLLAMA_HOST", "")
print(f"OLLAMA_HOST:{{ollama_host}}")
"""
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_script)
        script_path = f.name
    
    try:
        # Create a temporary poppins.yml with ollama provider and base_url
        with tempfile.TemporaryDirectory() as tmpdir:
            poppins_path = os.path.join(tmpdir, "poppins.yml")
            with open(poppins_path, "w") as pf:
                pf.write("""agent:
  provider: ollama
  base_url: http://localhost:11434/v1
""")
            
            # Run the script in the temp directory so it finds poppins.yml
            env = os.environ.copy()
            env["PWD"] = tmpdir
            # Clear other provider keys to ensure clean test
            for key in ['ANTHROPIC_API_KEY', 'MOONSHOT_API_KEY', 'DASHSCOPE_API_KEY', 
                        'OPENAI_API_KEY', 'GROQ_API_KEY', 'CUSTOM_API_KEY', 'CUSTOM_BASE_URL', 'OLLAMA_HOST']:
                env.pop(key, None)
            
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                env=env,
                cwd=tmpdir,
            )
            
            # Should set OLLAMA_HOST to base_url without /v1 suffix
            assert result.returncode == 0, f"Script failed: {result.stderr}"
            output = result.stdout.strip()
            assert "OLLAMA_HOST:http://localhost:11434" in output, f"Expected 'OLLAMA_HOST:http://localhost:11434', got '{output}'"
    finally:
        os.unlink(script_path)


# BDD: Detect Dashscope provider
def test_detect_dashscope_provider():
    """Test that detect_provider() returns 'dashscope' when DASHSCOPE_API_KEY is set."""
    # Create a small test script that imports and calls detect_provider
    test_script = """
import os
import sys
sys.path.insert(0, 'scripts')
# Clear higher-priority provider env vars to isolate the test
# (do NOT clear DASHSCOPE_API_KEY - that's what we're testing)
for key in ['ANTHROPIC_API_KEY', 'MOONSHOT_API_KEY', 
            'OPENAI_API_KEY', 'GROQ_API_KEY', 'CUSTOM_API_KEY', 'CUSTOM_BASE_URL', 'OLLAMA_HOST']:
    if key in os.environ:
        del os.environ[key]

from agent import detect_provider, PROVIDER_CONFIGS
result = detect_provider()
config = PROVIDER_CONFIGS.get(result, {})
base_url = config.get('base_url', '')
print(f"provider:{result}")
print(f"base_url:{base_url}")
"""
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_script)
        script_path = f.name
    
    try:
        # Run the script with DASHSCOPE_API_KEY set
        env = os.environ.copy()
        env["DASHSCOPE_API_KEY"] = "sk-dashscope-test-key"
        # Clear other provider keys to ensure clean test (no higher-priority keys)
        for key in ['ANTHROPIC_API_KEY', 'MOONSHOT_API_KEY', 
                    'OPENAI_API_KEY', 'GROQ_API_KEY', 'CUSTOM_API_KEY', 'CUSTOM_BASE_URL', 'OLLAMA_HOST']:
            env.pop(key, None)
        
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            env=env,
        )
        
        # Should return "dashscope" with correct base_url
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        output = result.stdout.strip()
        assert "provider:dashscope" in output, f"Expected 'provider:dashscope', got '{output}'"
        assert "base_url:https://dashscope-intl.aliyuncs.com/compatible-mode/v1" in output, f"Expected correct base_url, got '{output}'"
    finally:
        os.unlink(script_path)
