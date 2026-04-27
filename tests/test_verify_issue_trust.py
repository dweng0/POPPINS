#!/usr/bin/env python3
"""Tests for verify_issue_trust.py"""

import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Trust repo owner's issues directly
def test_trust_repo_owner_issue_directly():
    """Test that issues authored by repo owner are trusted directly."""
    from verify_issue_trust import verify_issues
    
    issues = [
        {
            "number": 1,
            "title": "Test issue",
            "author": {"login": "repo_owner"},
            "labels": [{"name": "agent-input"}],
        }
    ]
    repo = "owner/repo"
    owner = "repo_owner"
    
    trusted = verify_issues(issues, repo, owner)
    
    assert len(trusted) == 1
    assert trusted[0]["number"] == 1


# BDD: Trust community issue with agent-approved label from owner
def test_trust_community_issue_with_agent_approved_from_owner():
    """Test that community issues with agent-approved label from owner are trusted."""
    from verify_issue_trust import verify_issues
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = MagicMock()
        mock_run.return_value.stdout.strip.return_value = "repo_owner"
        mock_run.return_value.returncode = 0
        
        issues = [
            {
                "number": 3,
                "title": "Approved community issue",
                "author": {"login": "random_user"},
                "labels": [{"name": "agent-approved"}],
            }
        ]
        repo = "owner/repo"
        owner = "repo_owner"
        
        trusted = verify_issues(issues, repo, owner)
        
        assert len(trusted) == 1
        assert trusted[0]["number"] == 3


# BDD: Reject community issue with agent-approved from non-owner
def test_reject_community_issue_with_agent_approved_from_non_owner():
    """Test that community issues with agent-approved label from non-owner are rejected."""
    from verify_issue_trust import verify_issues
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = MagicMock()
        mock_run.return_value.stdout.strip.return_value = "random_user"
        mock_run.return_value.returncode = 0
        
        issues = [
            {
                "number": 4,
                "title": "Improperly approved issue",
                "author": {"login": "random_user"},
                "labels": [{"name": "agent-approved"}],
            }
        ]
        repo = "owner/repo"
        owner = "repo_owner"
        
        trusted = verify_issues(issues, repo, owner)
        
        assert len(trusted) == 0


# BDD: Verify label applier via GitHub events API
def test_get_label_applier_success():
    """Test that get_label_applier queries GitHub events API correctly."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = MagicMock()
        mock_run.return_value.stdout.strip.return_value = "repo_owner"
        mock_run.return_value.returncode = 0
        
        from verify_issue_trust import get_label_applier
        
        applier = get_label_applier("owner/repo", 123, "agent-approved")
        
        assert applier == "repo_owner"
        mock_run.assert_called_once()


# BDD: Verify label applier via GitHub events API
def test_get_label_applier_no_label_applied():
    """Test that get_label_applier returns None when no label was applied."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = MagicMock()
        mock_run.return_value.stdout.strip.return_value = "null"
        mock_run.return_value.returncode = 0
        
        from verify_issue_trust import get_label_applier
        
        applier = get_label_applier("owner/repo", 123, "agent-approved")
        
        assert applier is None


# BDD: Verify label applier via GitHub events API
def test_get_label_applier_exception_returns_none():
    """Test that get_label_applier returns None on exception."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("Network error")
        
        from verify_issue_trust import get_label_applier
        
        applier = get_label_applier("owner/repo", 123, "agent-approved")
        
        assert applier is None
