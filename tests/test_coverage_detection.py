from scripts.coverage_checker import is_partial_word_match


# BDD: Detect coverage via partial name matching
def test_partial_name_matching_success():
    # Assuming inputs that should pass the check based on implementation.
    test_name = "user_authentication_flow"
    scenario_description = "Tests user authentication and login process"
    assert is_partial_word_match(test_name, scenario_description) == True
