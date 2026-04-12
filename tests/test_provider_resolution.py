import pytest
from unittest.mock import patch, MagicMock

# Assume src modules are available for import in tests
from src.providers import config_resolver

# Mock the global constant needed by the units we will implement
MOCKED_CONFIGS = {
    'valid_provider': {'key': 'secret'}, 
}

def test_unknown_provider_error_exit():
    # BDD: Unknown provider error
    with patch('src.providers.config_resolver.PROVIDER_CONFIGS', MOCKED_CONFIGS) as mock_configs:
        # We expect check_and_validate_provider to raise an exception or exit code 1
        with pytest.raises(ValueError, match='Unknown provider'):
            config_resolver.check_and_validate_provider('invalid_provider', mock_configs)
