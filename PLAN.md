## 0. Commands

build_cmd: python3 -m py_compile scripts/*.py && echo "Build OK"
test_cmd: python3 -m pytest tests/ -v --tb=short 2>/dev/null || python3 tests/run_tests.py
lint_cmd: python3 -m ruff check scripts/ tests/ --fix || echo "lint skipped"
coverage_check: python3 scripts/check_bdd_coverage.py BDD.md

## 1. Units

Unit: list_files(path: str, excluded_dirs: set[str]) -> list[str]
File: tools/file_system.py (or similar)
Description: Recursively traverses a directory and returns a flat list of all file paths.
Dependency injection point: A filesystem interface object that handles directory iteration and path resolution, allowing for mocking the underlying OS operations.

Unit: _is_excluded(path: str, excluded_dirs: set[str]) -> bool
File: tools/file_system.py (or similar)
Description: Checks if a given file or directory path matches any of the predefined exclusion patterns.
Dependency injection point: Takes the list/set of excluded directories as a parameter.

## 2. Test strategy

Test file path: tests/test_tool_execution.py
Exact test function name: test_list_files_excludes_git_and_node_modules
BDD marker: # BDD: List files excludes git and node_modules
What the test injects: A mocked filesystem implementation that simulates a directory structure containing both target files and excluded directories (.git, node_modules).
What it asserts: The returned list of files does not contain any paths starting with .git/ or node_modules/

## 3. Acceptance criteria

  - [ ] BDD marker present on line immediately above test function, exact match
  - [ ] Test fails before implementation (red)
  - [ ] Test passes after implementation (green)
  - [ ] Full test suite still passes
  - [ ] `python3 scripts/check_bdd_coverage.py BDD.md` shows [x] for this scenario

## 4. Out of scope

Handling symbolic links or file permissions are out of scope, as the current requirement focuses solely on directory exclusion logic.

## 5. Files to delete (optional)
