import os
import sys
import tempfile
import subprocess
from unittest.mock import patch

sys.path.insert(0, os.path.abspath("scripts"))
from agent import run_tool


# BDD: Run bash command and capture output
def test_run_bash_command_and_capture_output():
    result = run_tool("bash", {"command": "echo hello"})
    assert "hello" in result


# BDD: Run bash command with stderr
def test_run_bash_command_with_stderr():
    result = run_tool("bash", {"command": "ls /nonexistent_path_xyz 2>&1 || ls /nonexistent_path_xyz"})
    assert result  # some output returned


# BDD: Bash command timeout after 300 seconds
def test_bash_command_timeout():
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("sleep", 300)):
        result = run_tool("bash", {"command": "sleep 400"})
    assert "ERROR: command timed out after 300s" in result


# BDD: Read file that does not exist
def test_read_file_that_does_not_exist():
    result = run_tool("read_file", {"path": "/nonexistent/file.txt"})
    assert result == "ERROR: file not found: /nonexistent/file.txt"


# BDD: Truncate long file output
def test_truncate_long_file_output():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("x" * 20000)
        path = f.name
    try:
        result = run_tool("read_file", {"path": path})
        assert "[... truncated" in result
        assert len(result) < 20000
    finally:
        os.unlink(path)


# BDD: Write file creates parent directories
def test_write_file_creates_parent_directories():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "newdir", "subdir", "file.txt")
        result = run_tool("write_file", {"path": path, "content": "hello"})
        assert os.path.exists(path)
        with open(path) as f:
            assert f.read() == "hello"


# BDD: Edit file replaces exact string
def test_edit_file_replaces_exact_string():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("old text here")
        path = f.name
    try:
        result = run_tool("edit_file", {"path": path, "old_str": "old text", "new_str": "new text"})
        with open(path) as f:
            assert f.read() == "new text here"
    finally:
        os.unlink(path)


# BDD: Edit file fails when string not found
def test_edit_file_fails_when_string_not_found():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("some content")
        path = f.name
    try:
        result = run_tool("edit_file", {"path": path, "old_str": "missing string", "new_str": "x"})
        assert "ERROR: string not found" in result
    finally:
        os.unlink(path)


# BDD: Edit file replaces only first occurrence
def test_edit_file_replaces_only_first_occurrence():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("foo foo foo")
        path = f.name
    try:
        run_tool("edit_file", {"path": path, "old_str": "foo", "new_str": "bar"})
        with open(path) as f:
            assert f.read() == "bar foo foo"
    finally:
        os.unlink(path)
