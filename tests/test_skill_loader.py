import os
import sys
import tempfile
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


# BDD: Skills appended to system prompt
def test_skills_appended_to_system_prompt():
    sys.path.insert(0, os.path.abspath("scripts"))
    import importlib
    agent = importlib.import_module("agent")

    with tempfile.TemporaryDirectory() as tmpdir:
        skill_path = os.path.join(tmpdir, "SKILL.md")
        with open(skill_path, "w") as f:
            f.write("MY_SKILL_CONTENT")

        skills_text = agent.load_skills(tmpdir)
        assert skills_text == "MY_SKILL_CONTENT"

        tdd_rules = "CRITICAL RULE — TDD cycle"
        system_prompt = tdd_rules
        if skills_text:
            system_prompt += "\n\n" + skills_text

        assert "MY_SKILL_CONTENT" in system_prompt
        tdd_pos = system_prompt.index(tdd_rules)
        skill_pos = system_prompt.index("MY_SKILL_CONTENT")
        assert skill_pos > tdd_pos, "skills_text must appear after TDD rules"


# BDD: Skip skills loading if directory missing
def test_skip_skills_loading_if_directory_missing():
    sys.path.insert(0, os.path.abspath("scripts"))
    import importlib
    agent = importlib.import_module("agent")

    result = agent.load_skills("./nonexistent_skills_dir_xyz")
    assert result == "", f"Expected empty string, got: {repr(result)}"
