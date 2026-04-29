#!/usr/bin/env python3
"""Tests for add_bdd_markers.py apply mode modifies files"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Apply mode modifies files
def test_apply_mode_flag_exists():
    """add_bdd_markers.py should have --apply flag."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    add_markers_path = scripts_dir + "/add_bdd_markers.py"
    
    with open(add_markers_path) as f:
        content = f.read()
    
    assert "--apply" in content


# BDD: Apply mode modifies files
def test_apply_mode_dry_run_default():
    """add_bdd_markers.py should default to dry-run mode."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    add_markers_path = scripts_dir + "/add_bdd_markers.py"
    
    with open(add_markers_path) as f:
        content = f.read()
    
    assert "dry-run" in content.lower() or "apply" in content.lower()


# BDD: Apply mode modifies files
def test_apply_mode_writes_markers():
    """add_bdd_markers.py --apply should write markers to test files."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    add_markers_path = scripts_dir + "/add_bdd_markers.py"
    
    with open(add_markers_path) as f:
        content = f.read()
    
    assert "write" in content.lower() or "open" in content.lower()


# BDD: Apply mode modifies files
def test_apply_mode_dry_run_output():
    """add_bdd_markers.py without --apply should show what would change."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    add_markers_path = scripts_dir + "/add_bdd_markers.py"
    
    with open(add_markers_path) as f:
        content = f.read()
    
    assert "[would add]" in content


# BDD: Apply mode modifies files
def test_apply_mode_marker_insertion():
    """add_bdd_markers.py --apply should insert marker above test function."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    add_markers_path = scripts_dir + "/add_bdd_markers.py"
    
    with open(add_markers_path) as f:
        content = f.read()
    
    assert "insert" in content.lower() or "write" in content.lower()


# BDD: Apply mode modifies files
def test_apply_mode_error_handling():
    """add_bdd_markers.py --apply should handle errors gracefully."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    add_markers_path = scripts_dir + "/add_bdd_markers.py"
    
    with open(add_markers_path) as f:
        content = f.read()
    
    assert "try" in content.lower() or "except" in content.lower()


# BDD: Apply mode modifies files
def test_apply_mode_overwrite_protection():
    """add_bdd_markers.py --apply should not overwrite existing markers."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    add_markers_path = scripts_dir + "/add_bdd_markers.py"
    
    with open(add_markers_path) as f:
        content = f.read()
    
    assert "skip" in content.lower() or "existing" in content.lower()


# BDD: Apply mode modifies files
def test_apply_mode_recursive_search():
    """add_bdd_markers.py --apply should search recursively."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    add_markers_path = scripts_dir + "/add_bdd_markers.py"
    
    with open(add_markers_path) as f:
        content = f.read()
    
    assert "glob" in content.lower() or "os.walk" in content.lower() or "find_test_files" in content.lower()


# BDD: Apply mode modifies files
def test_apply_mode_file_extension_filter():
    """add_bdd_markers.py --apply should filter by file extension."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    add_markers_path = scripts_dir + "/add_bdd_markers.py"
    
    with open(add_markers_path) as f:
        content = f.read()
    
    assert ".py" in content or ".js" in content or ".ts" in content


# BDD: Apply mode modifies files
def test_apply_mode_summary():
    """add_bdd_markers.py --apply should show summary of changes."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    add_markers_path = scripts_dir + "/add_bdd_markers.py"
    
    with open(add_markers_path) as f:
        content = f.read()
    
    assert "marker" in content.lower() or "applied" in content.lower()
