#!/usr/bin/env python3
"""Tests for dotenv loading functionality"""

import os
import sys
import tempfile

sys.path.insert(0, "scripts")
from agent import load_dotenv


# BDD: Skip comment lines in .env
def test_skip_comment_lines_in_env():
    """Test that load_dotenv() skips comment lines starting with #."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = os.path.join(tmpdir, ".env")
        
        # Create .env file with comment and key-value
        with open(env_path, "w") as f:
            f.write("# This is a comment\n")
            f.write("KEY=value\n")
            f.write("# Another comment\n")
            f.write("ANOTHER_KEY=another_value\n")
        
        # Save original environment
        original_env = os.environ.get("KEY"), os.environ.get("ANOTHER_KEY")
        
        try:
            # Remove keys from environment if they exist
            os.environ.pop("KEY", None)
            os.environ.pop("ANOTHER_KEY", None)
            
            # Load the .env file
            load_dotenv(env_path)
            
            # Verify KEY is set
            assert os.environ.get("KEY") == "value", f"Expected KEY=value, got KEY={os.environ.get('KEY')}"
            
            # Verify ANOTHER_KEY is set
            assert os.environ.get("ANOTHER_KEY") == "another_value", f"Expected ANOTHER_KEY=another_value, got ANOTHER_KEY={os.environ.get('ANOTHER_KEY')}"
            
            # Verify comment lines were not parsed as keys
            assert "This" not in os.environ, "Comment line should not be parsed as env var"
            assert "Another" not in os.environ, "Comment line should not be parsed as env var"
        finally:
            # Restore original environment
            if original_env[0] is not None:
                os.environ["KEY"] = original_env[0]
            else:
                os.environ.pop("KEY", None)
            if original_env[1] is not None:
                os.environ["ANOTHER_KEY"] = original_env[1]
            else:
                os.environ.pop("ANOTHER_KEY", None)
