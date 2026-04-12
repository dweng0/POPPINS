import pytest
from unittest.mock import Mock
from agents.providers.openai_client import try_initialize_openai # Assuming this path based on PLAN.md

def test_initialization_fails_when_package_is_missing():
    # BDD: Missing openai package error
    # Arrange
    mock_dependency_checker = Mock()
    mock_dependency_checker.side_effect = lambda pkg: pkg != 'openai'
    config = {}

    # Act
    success, message = try_initialize_openai(config, mock_dependency_checker)

    # Assert
    assert success is False
    assert "Missing required package: openai" in message