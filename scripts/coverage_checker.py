import re

def normalize_string(s: str) -> str:
    """Converts a string to lowercase and removes non-alphanumeric characters for heuristic matching."""
    return re.sub(r'[^a-z0-9]', '', s.lower())

def detect_heuristic_match(test_function_name: str, scenario_name: str) -> bool:
    """Compares a test function name against a BDD scenario name using heuristic substring matching."""
    normalized_func = normalize_string(test_function_name)
    normalized_scenario = normalize_string(scenario_name)

    # Heuristic check: Does the normalized scenario string appear as a substring in the normalized function name?
    return normalized_scenario in normalized_func