## 2026-04-12 09:21 — Search parent directories for poppins.yml

Implemented the "Search parent directories for poppins.yml" scenario by writing a test that verifies `find_config()` can locate poppins.yml when it exists in a parent directory but not in the current working directory. The implementation already existed in `scripts/parse_poppins_config.py` with a proper parent directory traversal algorithm, so the test passed immediately. Added the test with the required BDD marker comment to `tests/test_parse_bdd_config.py`.
