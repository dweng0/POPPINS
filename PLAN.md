## 1. Units

*   **Name:** `detect_heuristic_match(test_function_name: str, scenario_name: str) -> bool`
    *   **File:** `scripts/coverage_checker.py`
    *   **Description:** Compares a test function name against a BDD scenario name using heuristic substring matching after normalizing both strings.
    *   **Dependency injection point:** None (operates on string inputs).

## 2. Test strategy

*   **Test file path:** `tests/test_coverage_heuristics.py` (new test file)
*   **Exact test function name:** `test_detect_heuristic_match_success`
*   **BDD marker:** `# BDD: Detect coverage via heuristic name matching`
*   **What the test injects:** Direct calls to the `detect_heuristic_match` unit with predefined strings.
*   **What it asserts:** That calling `detect_heuristic_match("test_login_with_valid_credentials", "Login with valid credentials")` returns `True`.

## 3. Acceptance criteria

*   [ ] BDD marker present on line immediately above test function, exact match
*   [ ] Test fails before implementation (red)
*   [ ] Test passes after implementation (green)
*   [ ] Full test suite still passes
*   [ ] `python3 scripts/check_bdd_coverage.py BDD.md` shows [x] for this scenario

## 4. Out of scope

*   Implementing the full parsing logic for extracting function names from source files; this unit assumes the test function name string is already provided.
*   Supporting partial word matching or complex regular expression comparisons (these are covered by separate BDD scenarios).
