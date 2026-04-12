## 2026-04-12 09:26 — Skip comment lines in .env

Implemented the "Skip comment lines in .env" scenario by adding a test file `tests/test_dotenv.py` with the BDD marker comment. The test verifies that `load_dotenv()` correctly skips lines starting with `#` while parsing KEY=value pairs. The implementation already existed in `scripts/agent.py` with the `line.startswith("#")` check, so no code changes were needed — only the test to provide coverage. All 13 tests pass and the BDD coverage checker now marks this scenario as covered [x].
