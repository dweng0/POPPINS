import os
import re
from typing import Callable, Optional


def _parse_pipelines(content: str) -> Optional[list]:
    """Return list of pipelines from YAML frontmatter, or None if field absent."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    fm = match.group(1)
    line = re.search(r"^pipelines:\s*\[([^\]]*)\]", fm, re.MULTILINE)
    if not line:
        return None
    return [p.strip() for p in line.group(1).split(",") if p.strip()]


def load_skills(
    directory_path: str,
    file_reader: Callable[[str], str],
    pipeline: Optional[str] = None,
) -> str:
    """Read all SKILL.md files under directory_path and concatenate their contents.

    If pipeline is given, skills with a `pipelines:` frontmatter field are only
    included when pipeline appears in that list. Skills with no `pipelines:` field
    are always included.
    """
    skill_files = []
    for root, _, filenames in os.walk(directory_path):
        if "SKILL.md" in filenames:
            skill_files.append(os.path.join(root, "SKILL.md"))

    contents = []
    for file_path in sorted(skill_files):
        content = file_reader(file_path)
        if pipeline is not None:
            allowed = _parse_pipelines(content)
            if allowed is not None and pipeline not in allowed:
                continue
        contents.append(content)

    return "\n---\n".join(contents)
