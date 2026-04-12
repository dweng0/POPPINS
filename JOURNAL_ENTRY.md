## 2026-04-12 10:03 — Add test coverage for custom provider detection

Implemented the "Detect custom provider from base URL" scenario by adding a test in `tests/test_agent_provider.py`. The test uses a subprocess approach to isolate environment variables and verify that `detect_provider()` returns "custom" when `CUSTOM_BASE_URL` is set. The implementation already existed in `scripts/agent.py`, so this session added the missing test coverage. All 17 tests now pass.
