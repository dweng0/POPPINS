#!/usr/bin/env python3
"""Tests for scripts/add_bdd_markers.py"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
<<<<<<< HEAD
from add_bdd_markers import detect_comment_prefix


# BDD: Detect comment prefix by file extension
def test_detect_comment_prefix_by_file_extension():
    """Detect comment prefix by file extension."""
    assert detect_comment_prefix("file.py") == "#"
=======

from add_bdd_markers import detect_comment_prefix

# BDD: Detect JavaScript comment prefix
def test_detect_javascript_comment_prefix():
    assert detect_comment_prefix("file.test.js") == "//"
>>>>>>> agent/detect-javascript-comment-prefix-20260427-210602
