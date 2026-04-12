## 2026-04-12 08:51 — Find test files in project

Implemented the "Find test files in project" scenario under Test Coverage Detection feature. Added a test `test_find_test_files_in_project()` in `tests/test_check_bdd_coverage.py` that verifies the `find_test_files()` function correctly identifies test files matching patterns like `*test*.py`, `test_*.py`, and `*_test.py` across nested directories while excluding non-test files. The implementation already existed in `scripts/check_bdd_coverage.py` and the test passes, confirming the function works as specified.
