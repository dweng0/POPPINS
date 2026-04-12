PROVIDER_CONFIGS = {}

def resolve_provider_from_cli(cli_args: list[str], provider_configs: dict) -> str | None:
    """Checks the command line arguments against known providers to determine the active provider.
    Dependency injection point: `provider_configs` (dict, default: global PROVIDER_CONFIGS constant).
    """
    # Simple implementation assuming --provider flag
    for i, arg in enumerate(cli_args):
        if arg == '--provider' and i + 1 < len(cli_args):
            provider_name = cli_args[i+1]
            if provider_name in provider_configs:
                return provider_name
    return None

def check_and_validate_provider(provided_name: str, config_registry: dict) -> bool:
    """Validates if the provided provider name exists in the system's configuration registry.
    Dependency injection point: `config_registry` (dict, default: global PROVIDER_CONFIGS constant).
    """
    if provided_name not in config_registry:
        raise ValueError(f"Unknown provider: {provided_name}")
    return True
