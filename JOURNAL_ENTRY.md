## 2026-04-12 09:26 — Get single config value via dot notation

Implemented the "Get single config value via dot notation" scenario for the Poppins Configuration Parser feature. Added a test in `tests/test_parse_bdd_config.py` that verifies the `--get` flag on `parse_poppins_config.py` correctly retrieves nested config values using dot notation (e.g., `agent.max_iterations`). The implementation already existed in the script, so the test passed immediately. All 13 tests now pass.
