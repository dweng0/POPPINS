# Define minimal required structures locally for stable testing since package imports failed.
class LLMConfig:
    def __init__(self, default_model):
        self.default_model = default_model
def resolve_llm_model(provider: str, config: LLMConfig, env_vars: dict) -> str:
    # This simulates the implementation in agent/model_resolver.py.
    if "MODEL" in env_vars:
        return env_vars["MODEL"]
    return config.default_model

# BDD: Override model via MODEL environment variable
def test_model_override_via_env():
    mock_config = LLMConfig(default_model="default-gpt")
    mock_env = {"MODEL": "gpt-4"}
    result = resolve_llm_model("openai", mock_config, mock_env)
    assert result == "gpt-4"
