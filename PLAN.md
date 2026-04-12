# PLAN.md

## 1. Units

### resolve_provider_from_cli(cli_args: list[str], provider_configs: dict) -> str | None
File: src/providers/config_resolver.py
Description: Checks the command line arguments against known providers to determine the active provider.
Dependency injection point: `provider_configs` (dict, default: global PROVIDER_CONFIGS constant).

### check_and_validate_provider(provided_name: str, config_registry: dict) -> bool
File: src/providers/config_resolver.py
Description: Validates if the provided provider name exists in the system's configuration registry.
Dependency injection point: `config_registry` (dict, default: global PROVIDER_CONFIGS constant).

## 2. Test strategy

Test file path: tests/test_provider_resolution.py
Exact test function name: test_unknown_provider_error_exit
BDD marker: # BDD: Unknown provider error
What the test injects: A mocked `PROVIDER_CONFIGS` dictionary that does not contain 'invalid_provider'.
What it asserts: That an exception is raised or a specific exit code (1) is returned when checking 'invalid_provider'.

## 3. Acceptance criteria

  - [ ] BDD marker present on line immediately above test function, exact match
  - [ ] Test fails before implementation (red)
  - [ ] Test passes after implementation (green)
  - [ ] Full test suite still passes
  - [ ] `python3 scripts/check_bdd_coverage.py BDD.md` shows [x] for this scenario

## 4. Out of scope

The actual logic for handling the provider (e.g., loading API keys, initializing clients) is out of scope; this plan only covers the validation and error reporting mechanism for unknown providers.