## 2026-04-12 10:15 — Set OLLAMA_HOST from poppins.yml base_url

Implemented the scenario "Set OLLAMA_HOST from poppins.yml base_url" which verifies that when poppins.yml has `provider: ollama` and `base_url: http://localhost:11434/v1`, the OLLAMA_HOST environment variable is correctly set to `http://localhost:11434` (stripping the /v1 suffix).

The implementation already existed in `scripts/agent.py` in the `_apply_poppins_provider_config()` function, which uses `base_url.rstrip("/").removesuffix("/v1")` to strip the suffix. I added a test to `tests/test_agent_provider.py` with the BDD marker comment to link it to the scenario. Also fixed a merge conflict in `tests/test_agent.py` that was blocking test execution.
