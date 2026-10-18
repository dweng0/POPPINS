#!/usr/bin/env python3
"""Accepted-but-uncommitted agent work is committed before merge."""

import os
import subprocess
import sys

sys.path.insert(0, "scripts")


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def _repo(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README").write_text("x\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


# BDD: Accepted work left uncommitted is committed before merge
def test_leftover_work_is_committed(tmp_path):
    import pm_worker

    repo = _repo(tmp_path)
    os.makedirs(repo / "src/test")
    (repo / "src/test/FooTest.kt").write_text("// BDD: Foo\n")
    (repo / "PLAN.md").write_text("plan\n")
    (repo / "BDD_SCENARIO.md").write_text("spec\n")

    assert pm_worker._commit_leftover_work("Foo", str(repo), lambda *_: None)

    committed = _git(repo, "show", "--name-only", "--format=", "HEAD").split()
    assert committed == ["src/test/FooTest.kt"]
    assert "PLAN.md" in _git(repo, "status", "--porcelain")


# BDD: Clean accepted worktree gets no extra commit
def test_clean_worktree_no_commit(tmp_path):
    import pm_worker

    repo = _repo(tmp_path)
    before = _git(repo, "rev-parse", "HEAD")
    assert not pm_worker._commit_leftover_work("Foo", str(repo), lambda *_: None)
    assert _git(repo, "rev-parse", "HEAD") == before
