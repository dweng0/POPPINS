import re


def normalize_string(s: str) -> str:
    """Converts a string to lowercase and removes non-alphanumeric characters for heuristic matching."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def get_words(text: str) -> list[str]:
    """Tokenizes text into lowercase alphanumeric words."""
    return [word for word in re.split(r"\W+", text.lower()) if word]


def is_partial_word_match(test_name: str, scenario_description: str) -> bool:
    """Checks if the test name partially matches any word in the scenario description by performing tokenized substring comparisons."""
    test_words = get_words(test_name)
    scenario_words = get_words(scenario_description)

    for t_word in test_words:
        for s_word in scenario_words:
            # Check if one word is a substring of the other (partial match at token level)
            if t_word in s_word or s_word in t_word:
                return True

    return False


def detect_heuristic_match(test_function_name: str, scenario_name: str) -> bool:
    """Compares a test function name against a BDD scenario name using heuristic substring matching."""
    normalized_func = normalize_string(test_function_name)
    normalized_scenario = normalize_string(scenario_name)

    # Heuristic check: Does the normalized scenario string appear as a substring in the normalized function name?
    return normalized_scenario in normalized_func
