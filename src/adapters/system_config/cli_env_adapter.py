import argparse
import os
from typing import Optional

# Assuming src/ports is accessible
from src.ports.config_reader import ConfigReader

class SystemConfigAdapter(ConfigReader):
    """
    Reads actual provider and API key settings from sys.argv (CLI) 
    and os.environ, implementing the ConfigReader Port.
    """
    def __init__(self, args=None):
        # Initialize argparse to handle CLI arguments if provided
        if args:
            self._parser = argparse.ArgumentParser()
            self._parser.add_argument('--provider', type=str, help='The provider to use')
            parsed_args, _ = self._parser.parse_known_args(args)
            self._cli_provider = parsed_args.provider
        else:
            self._cli_provider = None

    def get_cli_provider(self) -> Optional[str]:
        return self._cli_provider

    def is_api_key_set(self, provider: str) -> bool:
        """Checks environment variable presence for API keys."""
        env_var_name = f"{provider.upper()}_API_KEY"
        return os.environ.get(env_var_name) is not None