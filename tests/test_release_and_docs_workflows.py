#!/usr/bin/env python3
"""Tests for release and docs workflow scenarios."""

import os

WORKFLOWS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".github", "workflows"
)


def _read(name):
    with open(os.path.join(WORKFLOWS_DIR, name)) as f:
        return f.read()


# BDD: Release workflow on version tag
def test_release_workflow_triggers_on_version_tag():
    content = _read("release.yml")
    assert "tags:" in content
    assert "v*" in content


# BDD: Release workflow on version tag
def test_release_workflow_creates_github_release():
    content = _read("release.yml")
    assert "action-gh-release" in content or "create-release" in content or "gh release" in content


# BDD: Release workflow on version tag
def test_release_workflow_generates_release_notes():
    content = _read("release.yml")
    assert "generate_release_notes" in content or "release_notes" in content or "auto" in content


# BDD: Release includes install.sh
def test_release_includes_install_sh_as_asset():
    content = _read("release.yml")
    assert "install.sh" in content


# BDD: Release includes install.sh
def test_release_workflow_has_write_permission():
    content = _read("release.yml")
    assert "write" in content


# BDD: Docs deployment to GitHub Pages
def test_docs_workflow_deploys_to_github_pages_environment():
    content = _read("docs.yml")
    assert "github-pages" in content


# BDD: Docs deployment to GitHub Pages
def test_docs_workflow_uses_deploy_pages_action():
    content = _read("docs.yml")
    assert "deploy-pages" in content


# BDD: Docs deployment to GitHub Pages
def test_docs_workflow_has_pages_write_permission():
    content = _read("docs.yml")
    assert "pages: write" in content
