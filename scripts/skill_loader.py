import os
from typing import Callable

def load_skills(directory_path: str, file_reader: Callable[[str], str]) -> str:
    """Reads all files matching 'SKILL.md' within the specified directory and concatenates their contents.

    Args:
        directory_path: The root path to search for SKILL.md files.
        file_reader: A callable function used to read the content of a file given its full path.

    Returns:
        A single string containing concatenated contents of all found SKILL.md files, separated by "---".
    """
    skill_files = []
    # Recursively find all 'SKILL.md' files starting from directory_path
    for root, _, filenames in os.walk(directory_path):
        if 'SKILL.md' in filenames:
            skill_files.append(os.path.join(root, 'SKILL.md'))

    contents = []
    # Use the injected file_reader to get content for each file found
    for file_path in skill_files:
        content = file_reader(file_path)
        contents.append(content)

    # Concatenate all contents with "---" separator
    return "\n---\n".join(contents)