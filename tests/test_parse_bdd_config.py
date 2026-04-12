#!/usr/bin/env python3
"""Tests for parse_bdd_config.py"""

import os
import subprocess
import tempfile


# BDD: Parse YAML frontmatter from BDD.md
def test_parse_yaml_frontmatter_from_bdd_md():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("---\n")
        f.write("language: python\n")
        f.write("framework: pytest\n")
        f.write("build_cmd: python3 -m py_compile src/*.py\n")
        f.write("test_cmd: python3 -m pytest tests/\n")
        f.write("---\n")
        f.write("\n")
        f.write("Some content\n")
        f.flush()

        result = subprocess.run(
            ["python3", "scripts/parse_bdd_config.py", f.name],
            capture_output=True,
            text=True,
        )

        output = result.stdout
        assert "LANGUAGE='python'" in output
        assert "FRAMEWORK='pytest'" in output
        assert "BUILD_CMD='python3 -m py_compile src/*.py'" in output
        assert "TEST_CMD='python3 -m pytest tests/'" in output

        os.unlink(f.name)


# BDD: Handle missing frontmatter gracefully
def test_handle_missing_frontmatter_gracefully():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("No frontmatter here\n")
        f.write("Just regular content\n")
        f.flush()

        result = subprocess.run(
            ["python3", "scripts/parse_bdd_config.py", f.name],
            capture_output=True,
            text=True,
        )

        output = result.stdout
        assert "LANGUAGE='unknown'" in output
        assert "FRAMEWORK='none'" in output

        os.unlink(f.name)


# BDD: Parse frontmatter with quoted values
def test_parse_frontmatter_with_quoted_values():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("---\n")
        f.write("language: typescript\n")
        f.write('build_cmd: "npm run build"\n')
        f.write("test_cmd: 'npm test'\n")
        f.write("---\n")
        f.flush()

        result = subprocess.run(
            ["python3", "scripts/parse_bdd_config.py", f.name],
            capture_output=True,
            text=True,
        )

        output = result.stdout
        assert "LANGUAGE='typescript'" in output
        assert "BUILD_CMD='npm run build'" in output
        assert "TEST_CMD='npm test'" in output

        os.unlink(f.name)
