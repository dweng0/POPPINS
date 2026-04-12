## 2026-04-12 09:32 — Handle empty BDD.md with no scenarios

Covered the scenario "Handle empty BDD.md with no scenarios" by writing a test in `tests/test_check_bdd_coverage.py`. The test creates a temporary BDD.md file with YAML frontmatter but no Feature or Scenario sections, runs `check_bdd_coverage.py` on it, and verifies it outputs "No scenarios found in BDD.md" and exits with code 0. The implementation already existed in the main script, so the test passed immediately. All 15 tests pass and the build succeeds.
