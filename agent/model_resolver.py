class LLMConfig: 
    def __init__(self, default_model: str): 
        self.default_model = default_model

def resolve_llm_model(provider: str, config: LLMConfig, env_vars: dict) -> str:
    """
    Determines the final model name based on environment variable overrides and configuration defaults.
    """
    # 1. Check for MODEL environment variable override
    if "MODEL" in env_vars:
        return env_vars["MODEL"]
    
    # 2. Fallback to configured default model
    return config.default_model