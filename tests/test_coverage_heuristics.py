from scripts.coverage_checker import detect_heuristic_match

# BDD: Handle BDD.md with only frontmatter
def test_detect_heuristic_match_success():
    assert detect_heuristic_match("test_login_with_valid_credentials", "Login with valid credentials") is True