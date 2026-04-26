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


# BDD: CUSTOM_MODEL required for custom provider without --model
def test_custom_model_required_for_custom_provider_without_model():
    """Test that agent.py requires CUSTOM_MODEL when provider is custom and no --model flag."""
    scripts_dir = os.path.abspath("scripts")
    agent_path = os.path.abspath("scripts/agent.py")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Run the script with custom provider but no CUSTOM_MODEL
        env = os.environ.copy()
        env['CUSTOM_BASE_URL'] = 'https://custom.api.example.com/v1'
        env['CUSTOM_API_KEY'] = 'sk-test-key'
        env['CUSTOM_MODEL'] = ''  # Clear CUSTOM_MODEL to trigger the error
        for key in ['ANTHROPIC_API_KEY', 'MOONSHOT_API_KEY', 'DASHSCOPE_API_KEY', 
                    'OPENAI_API_KEY', 'GROQ_API_KEY', 'OLLAMA_HOST']:
            env.pop(key, None)
        
        # Test detect_provider
        test_script = """
import os
import sys
sys.path.insert(0, 'SCRIPTS_DIR')
os.environ['CUSTOM_BASE_URL'] = 'https://custom.api.example.com/v1'
from agent import detect_provider
print("provider:" + str(detect_provider()))
""".replace('SCRIPTS_DIR', scripts_dir)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            script_path = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                env=env,
                cwd=tmpdir,
            )
            
            # detect_provider should return "custom"
            assert result.returncode == 0, f"Script failed: {result.stderr}"
            assert result.stdout.strip() == "provider:custom", f"Expected 'provider:custom', got '{result.stdout.strip()}'"
        finally:
            os.unlink(script_path)
        
        # Now test the full agent.py script with no --model and no CUSTOM_MODEL
        # Provide empty stdin to trigger CUSTOM_MODEL error before stdin error
        result = subprocess.run(
            [sys.executable, agent_path, "--provider", "custom"],
            capture_output=True,
            text=True,
            env=env,
            cwd=tmpdir,
            input="",
        )
        
        # Should exit with code 1 and print CUSTOM_MODEL error (checked before stdin)
        assert result.returncode == 1, f"Expected exit code 1, got {result.returncode}"
        assert "ERROR: CUSTOM_MODEL not set" in result.stderr, f"Expected CUSTOM_MODEL error, got: {result.stderr}"


# BDD: No provider detected error message
def test_no_provider_detected_error_message():
    """Test that agent.py prints error listing all supported provider env vars when no provider detected."""
    scripts_dir = os.path.abspath("scripts")
    agent_path = os.path.abspath("scripts/agent.py")
    
    test_script = """
import os
import sys
sys.path.insert(0, 'SCRIPTS_DIR')

# Clear all provider-related env vars
for key in ['ANTHROPIC_API_KEY', 'MOONSHOT_API_KEY', 'DASHSCOPE_API_KEY', 
            'OPENAI_API_KEY', 'GROQ_API_KEY', 'CUSTOM_API_KEY', 'CUSTOM_BASE_URL', 'OLLAMA_HOST']:
    if key in os.environ:
        del os.environ[key]

from agent import detect_provider
result = detect_provider()
print("provider:" + str(result))
""".replace('SCRIPTS_DIR', scripts_dir)
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_script)
        script_path = f.name
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Run the script with no provider env vars set and no poppins.yml
            env = os.environ.copy()
            for key in ['ANTHROPIC_API_KEY', 'MOONSHOT_API_KEY', 'DASHSCOPE_API_KEY', 
                        'OPENAI_API_KEY', 'GROQ_API_KEY', 'CUSTOM_API_KEY', 'CUSTOM_BASE_URL', 'OLLAMA_HOST']:
                env.pop(key, None)
            env['PWD'] = tmpdir
            
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                env=env,
                cwd=tmpdir,
            )
            
            # detect_provider should return None
            assert result.returncode == 0, f"Script failed: {result.stderr}"
            assert result.stdout.strip() == "provider:None", f"Expected 'provider:None', got '{result.stdout.strip()}'"
            
            # Now test the full agent.py script with no stdin (should fail)
            # Use absolute path for agent.py
            result = subprocess.run(
                [sys.executable, agent_path],
                capture_output=True,
                text=True,
                env=env,
                cwd=tmpdir,
            )
            
            # Should exit with code 1 and print error message
            assert result.returncode == 1, f"Expected exit code 1, got {result.returncode}"
            assert "ERROR: No API key found" in result.stderr, f"Expected error message, got: {result.stderr}"
            assert "ANTHROPIC_API_KEY" in result.stderr, "Error should list ANTHROPIC_API_KEY"
            assert "MOONSHOT_API_KEY" in result.stderr, "Error should list MOONSHOT_API_KEY"
            assert "DASHSCOPE_API_KEY" in result.stderr, "Error should list DASHSCOPE_API_KEY"
            assert "OPENAI_API_KEY" in result.stderr, "Error should list OPENAI_API_KEY"
            assert "GROQ_API_KEY" in result.stderr, "Error should list GROQ_API_KEY"
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


# BDD: Missing anthropic package error
def test_missing_anthropic_package_error():
    """Test that agent.py has error handling for missing anthropic package."""
    # Verify the error handling code exists in agent.py
    with open("scripts/agent.py") as f:
        content = f.read()
    
    assert "anthropic package not installed" in content, \
        "Error message for missing anthropic package should exist"
    assert "pip install anthropic" in content, \
        "Installation instruction should exist"
    
    # Verify the try/except block exists
    assert "try:" in content, "Try block should exist"
    assert "import anthropic" in content, "Import anthropic should exist"
    assert "except ImportError:" in content, "ImportError handler should exist"
    
    # If anthropic is installed, verify it works
    import importlib.util
    anthropic_found = importlib.util.find_spec("anthropic") is not None
    
    if anthropic_found:
        scripts_dir = os.path.abspath("scripts")
        agent_path = os.path.abspath("scripts/agent.py")
        
        test_script = """
import os
import sys
sys.path.insert(0, 'SCRIPTS_DIR')
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-test-key'
from agent import detect_provider
print("provider:" + str(detect_provider()))
""".replace('SCRIPTS_DIR', scripts_dir)
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_script)
            script_path = f.name
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Copy agent.py to tmpdir
                import shutil
                shutil.copy(agent_path, os.path.join(tmpdir, 'agent.py'))
                shutil.copy(os.path.join(scripts_dir, 'parse_poppins_config.py'), 
                           os.path.join(tmpdir, 'parse_poppins_config.py'))
                
                env = os.environ.copy()
                env['ANTHROPIC_API_KEY'] = 'sk-ant-test-key'
                for key in ['MOONSHOT_API_KEY', 'DASHSCOPE_API_KEY', 
                            'OPENAI_API_KEY', 'GROQ_API_KEY', 'CUSTOM_API_KEY', 'CUSTOM_BASE_URL', 'OLLAMA_HOST']:
                    env.pop(key, None)
                
                result = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=tmpdir,
                )
                
                assert result.returncode == 0, f"Script failed: {result.stderr}"
                assert result.stdout.strip() == "provider:anthropic", \
                    f"Expected 'provider:anthropic', got '{result.stdout.strip()}'"
        finally:
            os.unlink(script_path)

