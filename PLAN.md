<<<<<<< HEAD
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
=======
# Design Plan: Custom event log path via --event-log

## 1. Units

*   **Name:** `parse_cli_args(args)`
    **File:** `scripts/agent.py`
    **Description:** Parses command line arguments, extracting configuration values like `--event-log`.
    **Dependency Injection Point:** Takes an iterable of CLI arguments (`sys.argv`) as a parameter to allow testing without actual system interaction.
*   **Name:** `EventLogger.__init__(self, log_path, file_writer)`
    **File:** `src/event_logger.py`
    **Description:** Initializes the event logging mechanism using a specified file path and a dependency-injected writer object.
    **Dependency Injection Point:** Takes `log_path` (str) and `file_writer` (Callable[[], str] or similar abstract interface for filesystem operations/buffering) as parameters to decouple logging from IO implementation.
*   **Name:** `get_default_log_path()`
    **File:** `src/config.py`
    **Description:** Returns the hardcoded, system default path if no custom path is provided.
    **Dependency Injection Point:** This unit does not require injection as it represents an inherent configuration value; however, for maximum testability, its return logic could accept a mock config source if defaults change dynamically.

## 2. Test strategy

*   **Test file path:** `tests/test_event_logging.py`
*   **Exact test function name:** `test_custom_log_path_via_cli`
*   **BDD marker:** # BDD: Custom event log path via --event-log
*   **What the test injects:** A mock `file_writer` object (simulating filesystem write operations) and a mocked CLI argument list containing `--event-log=/custom/path/events.jsonl`. This isolates the `EventLogger` initialization logic from actual IO.
*   **What it asserts:** It asserts that when `agent.py` is run with the flag, the `EventLogger` instance is created using `/custom/path/events.jsonl` as its path parameter, and subsequent log calls use this provided path through the mocked writer.
>>>>>>> agent/custom-event-log-path-via-event-log-20260412-150305

## 3. Acceptance criteria

*   [ ] BDD marker present on line immediately above test function, exact match
*   [ ] Test fails before implementation (red)
*   [ ] Test passes after implementation (green)
*   [ ] Full test suite still passes
*   [ ] `python3 scripts/check_bdd_coverage.py BDD.md` shows [x] for this scenario

## 4. Out of scope

<<<<<<< HEAD
*   Detailed content validation or parsing of the skills within the SKILL.md files (only concatenation is required).
*   Robust error handling for cases where the input directory path does not exist.
*   Support for file types other than `SKILL.md`.
=======
*   **Actual log writing logic:** We are only testing the path configuration and initialization, not the actual serialization or disk write operation (which is handled by mocking `file_writer`). This prevents unnecessary IO overhead during unit tests.
*   **Error handling for invalid paths:** Handling cases where `/custom/path/events.jsonl` does not exist or is inaccessible is out of scope for this initial scenario; basic path parsing and injection are the focus.
>>>>>>> agent/custom-event-log-path-via-event-log-20260412-150305
