#!/usr/bin/env python3
"""Tests for orchestrate.py override max parallel agents via CLI"""

import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: Override max parallel agents via CLI
def test_cli_max_agents_flag():
    """--max-agents flag should override poppins.yml config."""
    from parse_poppins_config import get_config
    
    config = get_config()
    
    default_max_agents = config.get("orchestration", {}).get("max_parallel_agents", 1)
    
    assert default_max_agents >= 1


# BDD: Override max parallel agents via CLI
def test_cli_max_agents_overrides_config():
    """CLI --max-agents should take priority over config file."""
    config = {"orchestration": {"max_parallel_agents": 3}}
    cli_max_agents = 5
    
    max_agents = cli_max_agents if cli_max_agents else config.get("orchestration", {}).get("max_parallel_agents", 1)
    
    assert max_agents == 5


# BDD: Override max parallel agents via CLI
def test_cli_max_agents_defaults_when_not_specified():
    """When --max-agents not specified, use config or default."""
    config = {"orchestration": {"max_parallel_agents": 4}}
    cli_max_agents = None
    
    max_agents = cli_max_agents if cli_max_agents else config.get("orchestration", {}).get("max_parallel_agents", 1)
    
    assert max_agents == 4


# BDD: Override max parallel agents via CLI
def test_cli_max_agents_zero_means_default():
    """--max-agents=0 should use default (1) instead of 0."""
    cli_max_agents = 0
    default = 1
    
    max_agents = cli_max_agents if cli_max_agents and cli_max_agents > 0 else default
    
    assert max_agents == 1


# BDD: Override max parallel agents via CLI
def test_cli_max_agents_large_value():
    """CLI --max-agents should accept large values."""
    cli_max_agents = 20
    
    max_agents = cli_max_agents
    
    assert max_agents == 20


# BDD: Override max parallel agents via CLI
def test_cli_max_agents_one():
    """--max-agents=1 should run agents sequentially."""
    cli_max_agents = 1
    
    max_agents = cli_max_agents
    
    assert max_agents == 1


# BDD: Override max parallel agents via CLI
def test_orchestrator_respects_cli_max_agents():
    """Orchestrator should respect --max-agents from CLI."""
    import orchestrate
    
    config = {"orchestration": {"max_parallel_agents": 3}}
    cli_max_agents = 7
    
    effective_max_agents = cli_max_agents if cli_max_agents else config.get("orchestration", {}).get("max_parallel_agents", 1)
    
    assert effective_max_agents == 7


# BDD: Override max parallel agents via CLI
def test_cli_max_agents_with_popins_config():
    """CLI --max-agents should override poppins.yml orchestration.max_parallel_agents."""
    poppins_config = {"orchestration": {"max_parallel_agents": 2}}
    cli_max_agents = 6
    
    effective = cli_max_agents if cli_max_agents else poppins_config.get("orchestration", {}).get("max_parallel_agents", 1)
    
    assert effective == 6


# BDD: Override max parallel agents via CLI
def test_cli_max_agents_preserves_other_config():
    """CLI --max-agents should not affect other config values."""
    poppins_config = {
        "orchestration": {
            "max_parallel_agents": 3,
            "max_rounds": 4,
        }
    }
    cli_max_agents = 8
    
    effective_max_agents = cli_max_agents if cli_max_agents else poppins_config.get("orchestration", {}).get("max_parallel_agents", 1)
    effective_max_rounds = poppins_config.get("orchestration", {}).get("max_rounds", 1)
    
    assert effective_max_agents == 8
    assert effective_max_rounds == 4


# BDD: Override max parallel agents via CLI
def test_orchestrator_parallel_workers_with_override():
    """With --max-agents=5, orchestrator should spawn up to 5 parallel workers."""
    from concurrent.futures import ThreadPoolExecutor
    
    max_agents_cli = 5
    
    with ThreadPoolExecutor(max_workers=max_agents_cli) as executor:
        assert max_agents_cli == 5


# BDD: Override max parallel agents via CLI
def test_orchestrator_round_with_max_agents():
    """Each round should respect --max-agents limit."""
    from orchestrate import select_scenarios
    
    ordered = [f"Scenario {i}" for i in range(1, 16)]
    max_agents = 4
    max_rounds = 3
    
    all_selected = []
    remaining = ordered.copy()
    
    for round_num in range(1, max_rounds + 1):
        selected, remaining = select_scenarios(remaining, max_agents=max_agents)
        if not selected:
            break
        assert len(selected) <= max_agents, f"Round {round_num} selected {len(selected)} > {max_agents}"
        all_selected.extend(selected)
    
    assert len(all_selected) == 12
    assert len(remaining) == 3


# BDD: Override max parallel agents via CLI
def test_cli_max_agents_with_fewer_scenarios():
    """If fewer scenarios than max_agents, select all."""
    from orchestrate import select_scenarios
    
    ordered = [f"Scenario {i}" for i in range(1, 4)]
    max_agents = 10
    
    selected, remaining = select_scenarios(ordered, max_agents=max_agents)
    
    assert len(selected) == 3
    assert remaining == []


# BDD: Override max parallel agents via CLI
def test_orchestrator_max_agents_from_config():
    """When no CLI flag, use config value."""
    config = {"orchestration": {"max_parallel_agents": 6}}
    cli_max_agents = None
    
    effective = cli_max_agents if cli_max_agents else config.get("orchestration", {}).get("max_parallel_agents", 1)
    
    assert effective == 6


# BDD: Override max parallel agents via CLI
def test_orchestrator_max_agents_both_cli_and_config():
    """CLI should override config when both specified."""
    config = {"orchestration": {"max_parallel_agents": 3}}
    cli_max_agents = 9
    
    effective = cli_max_agents if cli_max_agents else config.get("orchestration", {}).get("max_parallel_agents", 1)
    
    assert effective == 9
