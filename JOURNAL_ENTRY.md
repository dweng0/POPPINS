## 2026-04-12 10:03 — Detect Anthropic provider from API key

Implemented the "Detect Anthropic provider from API key" scenario from the Multi-Provider AI Agent feature. Created `tests/test_agent.py` with a test that verifies `detect_provider()` returns "anthropic" when `ANTHROPIC_API_KEY` is set.

The implementation required modifying `detect_provider()` in `scripts/agent.py` to check environment variables before falling back to poppins.yml config. This change aligns with the BDD scenario "Environment variables override poppins.yml config" which specifies that env vars should take priority. All 17 tests pass after this change.
