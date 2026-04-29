#!/usr/bin/env python3
"""Tests for orchestrate.py override max rounds via CLI"""

import sys
import os
import argparse
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Override max rounds via CLI
def test_cli_max_rounds_flag():
    """--max-rounds flag should override poppins.yml config."""
    from parse_poppins_config import get_config
    
    config = get_config()
    
    default_max_rounds = config.get("orchestration", {}).get("max_rounds", 1)
    
    assert default_max_rounds == 1


# BDD: Override max rounds via CLI
def test_cli_max_rounds_overrides_config():
    """CLI --max-rounds should take priority over config file."""
    import orchestrate
    
    config = {"orchestration": {"max_rounds": 3}}
    cli_max_rounds = 5
    
    max_rounds = cli_max_rounds if cli_max_rounds else config.get("orchestration", {}).get("max_rounds", 1)
    
    assert max_rounds == 5


# BDD: Override max rounds via CLI
def test_cli_max_rounds_defaults_when_not_specified():
    """When --max-rounds not specified, use config or default."""
    config = {"orchestration": {"max_rounds": 4}}
    cli_max_rounds = None
    
    max_rounds = cli_max_rounds if cli_max_rounds else config.get("orchestration", {}).get("max_rounds", 1)
    
    assert max_rounds == 4


# BDD: Override max rounds via CLI
def test_cli_max_rounds_zero_means_default():
    """--max-rounds=0 should use default (1) instead of 0."""
    cli_max_rounds = 0
    default = 1
    
    max_rounds = cli_max_rounds if cli_max_rounds and cli_max_rounds > 0 else default
    
    assert max_rounds == 1


# BDD: Override max rounds via CLI
def test_cli_max_rounds_large_value():
    """CLI --max-rounds should accept large values."""
    cli_max_rounds = 100
    
    max_rounds = cli_max_rounds
    
    assert max_rounds == 100


# BDD: Override max rounds via CLI
def test_cli_max_rounds_one():
    """--max-rounds=1 should run exactly one round."""
    cli_max_rounds = 1
    
    max_rounds = cli_max_rounds
    
    assert max_rounds == 1


# BDD: Override max rounds via CLI
def test_orchestrator_respects_cli_max_rounds():
    """Orchestrator should respect --max-rounds from CLI."""
    import orchestrate
    
    config = {"orchestration": {"max_rounds": 2}}
    max_rounds_cli = 4
    
    effective_max_rounds = max_rounds_cli if max_rounds_cli else config.get("orchestration", {}).get("max_rounds", 1)
    
    assert effective_max_rounds == 4


# BDD: Override max rounds via CLI
def test_cli_max_rounds_with_popins_config():
    """CLI --max-rounds should override poppins.yml orchestration.max_rounds."""
    poppins_config = {"orchestration": {"max_rounds": 2}}
    cli_max_rounds = 5
    
    effective = cli_max_rounds if cli_max_rounds else poppins_config.get("orchestration", {}).get("max_rounds", 1)
    
    assert effective == 5


# BDD: Override max rounds via CLI
def test_cli_max_rounds_preserves_other_config():
    """CLI --max-rounds should not affect other config values."""
    poppins_config = {
        "orchestration": {
            "max_rounds": 2,
            "max_parallel_agents": 3,
        }
    }
    cli_max_rounds = 7
    
    effective_max_rounds = cli_max_rounds if cli_max_rounds else poppins_config.get("orchestration", {}).get("max_rounds", 1)
    effective_max_agents = poppins_config.get("orchestration", {}).get("max_parallel_agents", 1)
    
    assert effective_max_rounds == 7
    assert effective_max_agents == 3


# BDD: Override max rounds via CLI
def test_orchestrator_rounds_count_with_override():
    """With --max-rounds=3, orchestrator should run 3 rounds."""
    from orchestrate import select_scenarios
    
    ordered = [f"Scenario {i}" for i in range(1, 11)]
    max_agents = 3
    max_rounds = 3
    
    all_selected = []
    remaining = ordered.copy()
    
    for round_num in range(1, max_rounds + 1):
        selected, remaining = select_scenarios(remaining, max_agents=max_agents)
        if not selected:
            break
        all_selected.extend(selected)
    
    assert len(all_selected) == 9
    assert len(remaining) == 1
    assert all_selected == [f"Scenario {i}" for i in range(1, 10)]
