import pytest
from unittest.mock import MagicMock, patch

# Assuming tools are imported from a module named 'tools'
from tools.file_system import list_files


@pytest.fixture
def mock_filesystem():
    """Mocks the filesystem behavior for testing file listing."""
    mock = MagicMock()
    # Define a structure that includes files and excluded folders
    structure = [
        "src/file1.py",
        "docs/guide.md",
        ".git/hooks/pre-commit",
        "node_modules/some_package/index.js",
        "app/main.py",
    ]

    # Mock the directory traversal (which list_files will rely on)
    mock.traverse.return_value = structure

    # We mock the specific dependency injection point, assuming it is an interface
    with patch("tools.file_system.FilesystemInterface", return_value=mock) as MockFS:
        yield MockFS()


# BDD: List files excludes git and node_modules
def test_list_files_excludes_git_and_node_modules(mock_filesystem):
    """Tests that list_files correctly skips .git and node_modules directories."""
    excluded = {".git", "node_modules"}

    # Call the function under test, injecting our mock filesystem
    result = list_files(path="./", excluded_dirs=excluded, fs=mock_filesystem)

    expected_files = ["src/file1.py", "docs/guide.md", "app/main.py"]

    # Assert the result contains only non-excluded files
    assert sorted(result) == sorted(expected_files)
