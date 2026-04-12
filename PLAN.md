## 1. Units

**Unit: resolve_llm_model(provider: str, config: LLMConfig, env_vars: dict) -> str**
*   File: `agent/model_resolver.py`
*   Description: Determines the final model name to be used by the agent based on provider defaults and explicit environment variable overrides.
*   Dependency injection point: `config: LLMConfig` (to provide configured defaults), `env_vars: dict` (to inject current environment variables).

## 2. Test strategy

*   Test file path: `tests/test_llm_resolution.py`
*   Exact test function name: `test_model_override_via_env`
*   BDD marker: `# BDD: Override model via MODEL environment variable`
*   What the test injects: Mocked environment variables dictionary where `MODEL='gpt-4'`, along with a mock LLM configuration.
*   What it asserts: The function returns `'gpt-4'` as the resolved model name.

## 3. Acceptance criteria

*   [ ] BDD marker present on line immediately above test function, exact match
*   [ ] Test fails before implementation (red)
*   [ ] Test passes after implementation (green)
*   [ ] Full test suite still passes
*   [ ] `python3 scripts/check_bdd_coverage.py BDD.md` shows [x] for this scenario

## 4. Out of scope

*   Implementing the actual API call logic using the resolved model (this is a subsequent feature).
*   Handling overrides via command-line flags, as this scenario strictly targets environment variables.
