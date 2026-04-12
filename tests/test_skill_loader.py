from typing import Callable
import pytest
from scripts.skill_loader import load_skills

def test_load_skills_concatenates_multiple_files():
    # BDD: Load skills from SKILL.md files
    
    def mock_file_reader(filename: str) -> str:
        if 'skill1' in filename:
            return "Skill 1 content\n"
        elif 'skill2' in filename:
            return "Skill 2 content\n"
        return ""

    # Mock function that simulates file system traversal and reading
    def mock_file_finder(directory_path: str, file_reader: Callable[[str], str]) -> list[str]:
        # Simulate finding two SKILL.md files
        files = ["skill1_SKILL.md", "skill2_SKILL.md"]
        contents = []
        for filename in files:
            contents.append(file_reader(filename))
        return contents
    
    # Assuming a mock for directory listing/finding SKILL.md files is required.
    # Since PLAN.md only specifies 'directory_path' and 'file_reader', I will adjust the test setup to simulate the file finding aspect within the context of testing `load_skills` which should handle it, or assume the mocked environment handles path discovery if load_skills relies on OS functions (which it shouldn't due to dependency injection).
    # Let's simplify: we mock a helper that returns filenames, and then pass them to a mock file reader.
    
    def mock_list_skill_md(directory_path: str) -> list[str]:
        return ["dir/sub/SKILL.md_A", "dir/main/SKILL.md_B"]

    # Since I don't have the implementation yet, this test must fail because load_skills doesn't exist.
    # We focus on structure for now.
    
    # If we were using a full mock framework (like unittest.mock), we would patch `os.listdir` or similar.
    # Given the constraints, I will proceed assuming 'load_skills' handles listing files internally but uses file_reader for content.

    # Setup mocks
    def mock_read(file_path: str) -> str:
        if "SKILL.md_A" in file_path:
            return "Content of A\n"
        if "SKILL.md_B" in file_path:
            return "Content of B\n"
        return ""

    # We need a function that mimics finding all SKILL.md files first.
    # Let's assume load_skills takes the directory and handles traversal, but uses `file_reader` for content retrieval.

    # For maximum structural fidelity to the requirements (injecting file_reader): 
    # We need a mock environment where iteration over files is possible.
    
    test_directory = "/mock/data"
    expected_result = "Content of A\n\n---\nContent of B\n"

    # The test must fail initially because `scripts/skill_loader.py` does not exist and the function isn't implemented.
    # If I assume load_skills internally uses a list of files, this will expose the missing logic.
    
    result = load_skills(test_directory, mock_read)

    assert result == expected_result