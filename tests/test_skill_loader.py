import os
import tempfile
import pytest
from scripts.skill_loader import load_skills


# BDD: Load skills from SKILL.md files
def test_load_skills_concatenates_multiple_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create two subdirectories each with a SKILL.md
        dir_a = os.path.join(tmpdir, "feature_a")
        dir_b = os.path.join(tmpdir, "feature_b")
        os.makedirs(dir_a)
        os.makedirs(dir_b)

        with open(os.path.join(dir_a, "SKILL.md"), "w") as f:
            f.write("Content of A\n")
        with open(os.path.join(dir_b, "SKILL.md"), "w") as f:
            f.write("Content of B\n")

        result = load_skills(tmpdir, lambda path: open(path).read())

        # Both contents should appear, separated by \n---\n
        assert "Content of A\n" in result
        assert "Content of B\n" in result
        assert "\n---\n" in result
