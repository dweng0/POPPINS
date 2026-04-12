## 2026-04-12 10:58 — Skip frontmatter when parsing scenarios

Implemented the "Skip frontmatter when parsing scenarios" scenario by adding a test to `tests/test_check_bdd_coverage.py`. The test creates a BDD.md file with 10 lines of YAML frontmatter and verifies that only the actual Scenario entries are parsed, not the frontmatter content. The implementation in `check_bdd_coverage.py` already correctly handles frontmatter skipping by detecting the `---` delimiters and starting scenario parsing after the closing `---`, so the test passed immediately without requiring code changes.
