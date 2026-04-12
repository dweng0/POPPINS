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

## 3. Acceptance criteria

*   [ ] BDD marker present on line immediately above test function, exact match
*   [ ] Test fails before implementation (red)
*   [ ] Test passes after implementation (green)
*   [ ] Full test suite still passes
*   [ ] `python3 scripts/check_bdd_coverage.py BDD.md` shows [x] for this scenario

## 4. Out of scope

*   **Actual log writing logic:** We are only testing the path configuration and initialization, not the actual serialization or disk write operation (which is handled by mocking `file_writer`). This prevents unnecessary IO overhead during unit tests.
*   **Error handling for invalid paths:** Handling cases where `/custom/path/events.jsonl` does not exist or is inaccessible is out of scope for this initial scenario; basic path parsing and injection are the focus.