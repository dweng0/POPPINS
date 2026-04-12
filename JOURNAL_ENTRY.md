## 2026-04-12 09:21 — Apply defaults when poppins.yml missing

Implemented the scenario "Apply defaults when poppins.yml missing" by adding a test to `tests/test_parse_bdd_config.py`. The test verifies that when no `poppins.yml` file exists, the `get_config()` function returns the built-in defaults with `max_iterations=75` and `session_timeout=3600`. The implementation already existed in `scripts/parse_poppins_config.py`, so the test validated the existing behavior. All 11 tests pass and the build is successful.
