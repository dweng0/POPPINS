# BDD: Provider priority order
def test_detects_anthropic_when_keys_are_set():
    from src.provider_detector import detect_provider
    from typing import Optional

    class StubConfigReader:
        """Stub implementation of EnvironmentConfigReader for testing."""

        def get_key(self, key: str) -> Optional[str]:
            if key == "ANTHROPIC_API_KEY":
                return "mock_anthropic_key"
            elif key == "OPENAI_API_KEY":
                return "mock_openai_key"
            return None

    stub_reader = StubConfigReader()
    result = detect_provider(config_reader=stub_reader)
    assert result == "anthropic"
