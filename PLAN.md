# PLAN.md: Load skills from SKILL.md files

## 1. Units

*   **Name/Signature:** `load_skills(directory_path: str, file_reader: Callable[[str], str]) -> str`
    *   **File:** `scripts/skill_loader.py`
    *   **Description:** Reads all files matching 'SKILL.md' within the specified directory and concatenates their contents.
    *   **Dependency Injection Point:** `file_reader` (a function or mock object simulating filesystem read operations).

## 2. Test strategy

*   **Test file path:** `tests/test_skill_loader.py`
*   **Exact test function name:** `test_load_skills_concatenates_multiple_files`
*   **BDD marker:** `# BDD: Load skills from SKILL.md files`
*   **What the test injects:** A mock implementation of `file_reader` to simulate finding and reading two or more distinct SKILL.md files with known content.
*   **What it asserts:** The function returns a single string containing all mocked file contents, separated by the "---" marker.

## 3. Acceptance criteria

*   [ ] BDD marker present on line immediately above test function, exact match
*   [ ] Test fails before implementation (red)
*   [ ] Test passes after implementation (green)
*   [ ] Full test suite still passes
*   [ ] `python3 scripts/check_bdd_coverage.py BDD.md` shows [x] for this scenario

## 4. Out of scope

*   Detailed content validation or parsing of the skills within the SKILL.md files (only concatenation is required).
*   Robust error handling for cases where the input directory path does not exist.
*   Support for file types other than `SKILL.md`.
