#!/usr/bin/env python3
"""Tests for scripts/run_agent.sh harness selection."""

import os
import stat
import subprocess
import tempfile

SCRIPT = os.path.abspath("scripts/run_agent.sh")


def _stub(tmpdir, name):
    """Create an executable stub that records its argv and stdin."""
    path = os.path.join(tmpdir, name)
    with open(path, "w") as f:
        f.write(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            "print(json.dumps({'argv': sys.argv[1:], 'stdin': sys.stdin.read()}))\n"
        )
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    return path


def _clean_env(**extra):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("POPPINS_", "AGENT_HARNESS", "HERMES_", "CUSTOM_", "MODEL"))}
    env.update(extra)
    return env


def _run(env, stdin="", cwd=None):
    return subprocess.run(["bash", SCRIPT], input=stdin, capture_output=True,
                          text=True, env=env, cwd=cwd)


# BDD: Native harness is used by default
def test_native_harness_is_used_by_default():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "scripts"))
        with open(os.path.join(tmp, "scripts", "agent.py"), "w") as f:
            f.write("import sys, json\nprint(json.dumps({'native': True, 'stdin': sys.stdin.read()}))\n")
        r = _run(_clean_env(), stdin="hello", cwd=tmp)
        assert r.returncode == 0, r.stderr
        assert '"native": true' in r.stdout
        assert '"stdin": "hello"' in r.stdout


# BDD: Hermes harness passes the prompt as a one-shot query
def test_hermes_harness_passes_prompt_as_one_shot_query():
    import json
    with tempfile.TemporaryDirectory() as tmp:
        hermes = _stub(tmp, "hermes")
        env = _clean_env(AGENT_HARNESS="hermes", HERMES_CMD=hermes,
                         MODEL="gemma-4-26b-a4b-it",
                         HERMES_PROVIDER="lan-lmstudio")
        r = _run(env, stdin="do the thing")
        assert r.returncode == 0, r.stderr
        argv = json.loads(r.stdout)["argv"]
        assert argv[:5] == ["chat", "-q", "do the thing", "--oneshot", "-Q"]
        assert argv[argv.index("--max-turns") + 1] == "75"
        assert argv[argv.index("--model") + 1] == "gemma-4-26b-a4b-it"
        assert argv[argv.index("--provider") + 1] == "lan-lmstudio"


# BDD: Hermes harness uses poppins.yml max_iterations as max turns
def test_hermes_harness_uses_max_iterations_as_max_turns():
    import json
    with tempfile.TemporaryDirectory() as tmp:
        hermes = _stub(tmp, "hermes")
        env = _clean_env(AGENT_HARNESS="hermes", HERMES_CMD=hermes,
                         POPPINS_AGENT_MAX_ITERATIONS="40")
        r = _run(env, stdin="x")
        argv = json.loads(r.stdout)["argv"]
        assert argv[argv.index("--max-turns") + 1] == "40"


# BDD: Hermes harness reports an error when hermes is not installed
def test_hermes_harness_errors_when_hermes_missing():
    env = _clean_env(AGENT_HARNESS="hermes", HERMES_CMD="definitely-not-hermes-xyz")
    r = _run(env, stdin="x")
    assert r.returncode != 0
    assert '"type":"error"' in r.stdout


# BDD: Unknown harness reports an error
def test_unknown_harness_reports_error():
    r = _run(_clean_env(AGENT_HARNESS="bogus"), stdin="x")
    assert r.returncode != 0
    assert '"type":"error"' in r.stdout
    assert "bogus" in r.stdout


# BDD: evolve.sh runs every agent session through run_agent.sh
def test_evolve_runs_sessions_through_run_agent():
    with open("scripts/evolve.sh") as f:
        src = f.read()
    assert "python3 scripts/agent.py" not in src
    assert src.count("bash scripts/run_agent.sh") >= 3


# BDD: Orchestrated workers use the configured harness
def test_pm_worker_uses_run_agent_for_hermes(monkeypatch, tmp_path):
    import sys
    sys.path.insert(0, "scripts")
    import pm_worker

    captured = {}

    class FakeProc:
        stdout = iter(["ok\n"])
        returncode = 0

        def wait(self, timeout=None):
            return 0

    def fake_popen(cmd, **kwargs):
        captured["cmd"] = cmd
        return FakeProc()

    monkeypatch.setenv("AGENT_HARNESS", "hermes")
    monkeypatch.setattr(pm_worker.subprocess, "Popen", fake_popen)
    pm_worker.run_agent("prompt", str(tmp_path), "/main", None, "gemma", "SE", 60, "[x]")
    assert "scripts/run_agent.sh" in captured["cmd"]
    assert "scripts/agent.py" not in captured["cmd"]
    assert 'MODEL="gemma"' in captured["cmd"]
