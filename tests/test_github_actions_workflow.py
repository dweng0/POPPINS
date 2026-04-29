#!/usr/bin/env python3
"""Tests for GitHub Actions workflow triggers on schedule"""

import sys
import os
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


# BDD: GitHub Actions workflow triggers on schedule
def test_evolve_workflow_exists():
    """.github/workflows/evolve.yml should exist."""
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    
    if os.path.exists(workflows_dir):
        evolve_yml = os.path.join(workflows_dir, "evolve.yml")
        assert os.path.exists(evolve_yml), f"evolve.yml should exist in {workflows_dir}"


# BDD: GitHub Actions workflow triggers on schedule
def test_evolve_workflow_cron_schedule():
    """evolve.yml should have cron schedule trigger."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    evolve_yml = os.path.join(workflows_dir, "evolve.yml")
    
    with open(evolve_yml) as f:
        content = f.read()
    
    assert "schedule:" in content
    assert "cron:" in content


# BDD: GitHub Actions workflow triggers on schedule
def test_evolve_workflow_runs_evolve_sh():
    """evolve.yml should run evolve.sh."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    evolve_yml = os.path.join(workflows_dir, "evolve.yml")
    
    with open(evolve_yml) as f:
        content = f.read()
    
    assert "evolve.sh" in content


# BDD: GitHub Actions workflow triggers on schedule
def test_evolve_workflow_8_hour_interval():
    """evolve.yml should run every 8 hours."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    evolve_yml = os.path.join(workflows_dir, "evolve.yml")
    
    with open(evolve_yml) as f:
        content = f.read()
    
    assert "'0 */8 * * *'" in content or "*/8" in content


# BDD: GitHub Actions workflow triggers on schedule
def test_evolve_workflow_manual_dispatch():
    """evolve.yml should have manual workflow dispatch option."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    evolve_yml = os.path.join(workflows_dir, "evolve.yml")
    
    with open(evolve_yml) as f:
        content = f.read()
    
    assert "workflow_dispatch:" in content


# BDD: GitHub Actions workflow triggers on schedule
def test_docs_workflow_exists():
    """.github/workflows/docs.yml should exist."""
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    
    if os.path.exists(workflows_dir):
        docs_yml = os.path.join(workflows_dir, "docs.yml")
        assert os.path.exists(docs_yml), f"docs.yml should exist in {workflows_dir}"


# BDD: GitHub Actions workflow triggers on schedule
def test_release_workflow_exists():
    """.github/workflows/release.yml should exist."""
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    
    if os.path.exists(workflows_dir):
        release_yml = os.path.join(workflows_dir, "release.yml")
        assert os.path.exists(release_yml), f"release.yml should exist in {workflows_dir}"


# BDD: GitHub Actions workflow triggers on schedule
def test_workflow_timeout_limit():
    """Workflows should have timeout limit."""
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    
    if os.path.exists(workflows_dir):
        for yml_file in glob.glob(os.path.join(workflows_dir, "*.yml")):
            with open(yml_file) as f:
                content = f.read()
            
            if "timeout" in content.lower() or "minutes" in content.lower():
                assert True
                return
        
        assert False, "No timeout found in any workflow"


# BDD: GitHub Actions workflow triggers on schedule
def test_workflow_uses_gh_cli():
    """Workflows should use github-actions/checkout."""
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    
    if os.path.exists(workflows_dir):
        for yml_file in glob.glob(os.path.join(workflows_dir, "*.yml")):
            with open(yml_file) as f:
                content = f.read()
            
            if "checkout" in content.lower():
                assert True
                return
        
        assert False, "No checkout found in any workflow"


# BDD: GitHub Actions workflow triggers on schedule
def test_workflow_uses_setup_python():
    """Workflows should use setup-python for Python."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    
    if os.path.exists(workflows_dir):
        for yml_file in glob.glob(os.path.join(workflows_dir, "*.yml")):
            with open(yml_file) as f:
                content = f.read()
            
            if "setup-python" in content.lower():
                assert True
                return
        
        assert False, "No setup-python found in any workflow"


# BDD: GitHub Actions workflow triggers on schedule
def test_workflow_uses_setup_node():
    """Workflows should use setup-node for JS projects."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    
    if os.path.exists(workflows_dir):
        for yml_file in glob.glob(os.path.join(workflows_dir, "*.yml")):
            with open(yml_file) as f:
                content = f.read()
            
            if "setup-node" in content.lower():
                assert True
                return
        
        assert False, "No setup-node found in any workflow"


# BDD: GitHub Actions workflow triggers on schedule
def test_workflow_uses_setup_rust():
    """Workflows should use actions-rs/toolchain for Rust."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    
    if os.path.exists(workflows_dir):
        for yml_file in glob.glob(os.path.join(workflows_dir, "*.yml")):
            with open(yml_file) as f:
                content = f.read()
            
            if "rust" in content.lower() and ("toolchain" in content.lower() or "rustup" in content.lower()):
                assert True
                return
        
        assert False, "No Rust toolchain setup found in any workflow"


# BDD: GitHub Actions workflow triggers on schedule
def test_workflow_uses_setup_go():
    """Workflows should use actions/setup-go for Go."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    
    if os.path.exists(workflows_dir):
        for yml_file in glob.glob(os.path.join(workflows_dir, "*.yml")):
            with open(yml_file) as f:
                content = f.read()
            
            if "go" in content.lower() and "setup-go" in content.lower():
                assert True
                return
        
        assert False, "No setup-go found in any workflow"


# BDD: GitHub Actions workflow triggers on schedule
def test_workflow_retry_on_failure():
    """Workflows should have retry on failure."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    
    if os.path.exists(workflows_dir):
        for yml_file in glob.glob(os.path.join(workflows_dir, "*.yml")):
            with open(yml_file) as f:
                content = f.read()
            
            if "retry" in content.lower() or "max-attempts" in content.lower():
                assert True
                return
        
        assert False, "No retry config found in any workflow"


# BDD: GitHub Actions workflow triggers on schedule
def test_evolve_workflow_env_vars():
    """evolve.yml should set required env vars."""
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    workflows_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows")
    evolve_yml = os.path.join(workflows_dir, "evolve.yml")
    
    with open(evolve_yml) as f:
        content = f.read()
    
    assert "ANTHROPIC_API_KEY" in content or "api_key" in content.lower()
