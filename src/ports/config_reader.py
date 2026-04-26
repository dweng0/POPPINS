from typing import Optional, Protocol

<<<<<<< HEAD
class EnvironmentConfigReader(Protocol):
    """Abstracts the source of configuration secrets."""
    def get_key(self, key_name: str) -> Optional[str]:
        ...
=======
class ConfigReader(Protocol):
    """
    Defines the abstract interface for accessing CLI arguments and environment variables.
    """
    def get_cli_provider(self) -> Optional[str]: 
        ...

    def is_api_key_set(self, provider: str) -> bool: ...
>>>>>>> agent/override-provider-via-provider-flag-20260426-203821
