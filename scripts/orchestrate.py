#!/usr/bin/env python3
"""
Orchestrator — coordinates parallel agent workers for BAADD evolution.

Instead of each evolve.sh instance racing to claim a scenario, the orchestrator:
1. Reads BDD.md + BDD_STATUS.md to find all uncovered scenarios
2. Makes one AI call to produce a dependency-ordered execution plan
3. Spawns up to max_parallel_agents workers, each in its own worktree
4. Waits for workers, then merges results sequentially with verification

Usage:
    ANTHROPIC_API_KEY=sk-... python3 scripts/orchestrate.py

    # Or with explicit config overrides:
    python3 scripts/orchestrate.py --max-agents 2 --dry-run
"""

import os
import sys
import json
import subprocess
import argparse
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_poppins_config import get_config
from check_bdd_coverage import parse_scenarios, find_test_files, check_coverage


def load_dotenv(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_dotenv()


def run_cmd(cmd, cwd=None, timeout=30):
    """Run a shell command, return (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "timeout", 1


def scenario_to_slug(name):
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:60]


def get_uncovered_scenarios(bdd_path="BDD.md"):
    """Return list of (feature, scenario) tuples that lack test coverage."""
    scenarios = parse_scenarios(bdd_path)
    if not scenarios:
        return []

    test_files = find_test_files()
    test_contents = {}
    for path in test_files:
        try:
            with open(path) as f:
                test_contents[path] = f.read()
        except Exception:
            pass

    uncovered = []
    for feature, scenario in scenarios:
        if not check_coverage(scenario, test_files, test_contents):
            uncovered.append((feature, scenario))

    return uncovered


def read_file_safe(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def detect_provider():
    """Detect available LLM provider from environment, mirroring agent.py priority."""
    priority = [
        ("anthropic", "ANTHROPIC_API_KEY"),
        ("moonshot", "MOONSHOT_API_KEY"),
        ("dashscope", "DASHSCOPE_API_KEY"),
        ("openai", "OPENAI_API_KEY"),
        ("groq", "GROQ_API_KEY"),
        ("custom", "CUSTOM_API_KEY"),
    ]
    for name, env_var in priority:
        if os.environ.get(env_var):
            return name
    if os.environ.get("CUSTOM_BASE_URL"):
        return "custom"
    if os.environ.get("OLLAMA_HOST"):
        return "ollama"
    try:
        import urllib.request

        urllib.request.urlopen("http://localhost:11434", timeout=1)
        return "ollama"
    except Exception:
        pass
    return None


def resolve_model_and_client(provider, model_override=None):
    """Return (model_name, callable) where callable(prompt) -> response text.
    Supports all providers agent.py supports."""
    defaults = {
        "anthropic": "claude-haiku-4-5-20251001",
        "moonshot": "kimi-latest",
        "dashscope": "qwen-max",
        "openai": "gpt-4o",
        "groq": "llama-3.3-70b-versatile",
        "ollama": "llama3.2",
        "custom": os.environ.get("CUSTOM_MODEL", ""),
    }
    base_urls = {
        "moonshot": "https://api.moonshot.cn/v1",
        "dashscope": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "groq": "https://api.groq.com/openai/v1",
    }
    api_key_envs = {
        "anthropic": "ANTHROPIC_API_KEY",
        "moonshot": "MOONSHOT_API_KEY",
        "dashscope": "DASHSCOPE_API_KEY",
        "openai": "OPENAI_API_KEY",
        "groq": "GROQ_API_KEY",
        "custom": "CUSTOM_API_KEY",
    }

    model = model_override or os.environ.get("MODEL") or defaults.get(provider, "")

    if provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")

        def call(prompt):
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()

        return model, call

    # All other providers via OpenAI-compatible client
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai package not installed: pip install openai")

    api_key = os.environ.get(api_key_envs.get(provider, ""), "")
    base_url = base_urls.get(provider)

    if provider == "ollama":
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        base_url = host.rstrip("/") + "/v1"
        api_key = "ollama"
        model = (
            model_override
            or os.environ.get("MODEL")
            or os.environ.get("CUSTOM_MODEL", "llama3.2")
        )
    elif provider == "custom":
        base_url = os.environ.get("CUSTOM_BASE_URL")
        model = (
            model_override
            or os.environ.get("MODEL")
            or os.environ.get("CUSTOM_MODEL", "")
        )
        if not api_key:
            api_key = "custom"

    client_kwargs = {"api_key": api_key or "none"}
    if base_url:
        client_kwargs["base_url"] = base_url
    oai_client = OpenAI(**client_kwargs)

    def call(prompt):
        response = oai_client.chat.completions.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    return model, call


def plan_scenario_order(uncovered, bdd_content, provider, model_override=None):
    """Use a single AI call to order scenarios by dependency and priority.

    Returns a list of scenario names in recommended implementation order.
    Falls back to BDD.md order if the AI call fails or no provider is available.
    """
    scenario_names = [s for _, s in uncovered]

    if len(scenario_names) <= 1:
        return scenario_names

    if not provider:
        print("  No LLM provider available — using BDD.md order", flush=True)
        return scenario_names

    prompt = f"""You are analyzing a BDD specification to determine the best implementation order for uncovered scenarios.

Here is the full BDD spec:

<bdd>
{bdd_content[:8000]}
</bdd>

The following scenarios are UNCOVERED (no tests yet):
{json.dumps(scenario_names, indent=2)}

Analyze these scenarios and return them in optimal implementation order. Consider:
1. Dependencies — if scenario B requires functionality from scenario A, A goes first
2. Foundational work — scaffolding/setup scenarios before feature scenarios
3. Complexity — simpler scenarios first to build a working base
4. Feature grouping — scenarios in the same feature that share setup are cheaper to implement together

Return ONLY a JSON array of scenario names in the order they should be implemented.
No explanation, no markdown, just the JSON array. Example:
["Login with valid credentials", "View user dashboard", "Logout"]"""

    try:
        model, call = resolve_model_and_client(provider, model_override)
        print(f"  Planning with {provider} / {model}", flush=True)
        text = call(prompt)
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            ordered = json.loads(match.group())
            if set(ordered) == set(scenario_names):
                return ordered
            # AI returned a subset — append anything missing
            missing = [s for s in scenario_names if s not in ordered]
            return ordered + missing
    except Exception as e:
        print(f"  AI ordering failed ({e}), using BDD.md order", flush=True)

    return scenario_names


def create_worktree(scenario_slug, main_dir):
    """Create a git worktree for a scenario. Returns (worktree_path, branch_name)."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    branch = f"agent/{scenario_slug}-{timestamp}"
    wt_path = f"/tmp/baadd-wt-{scenario_slug}-{os.getpid()}"

    stdout, stderr, rc = run_cmd(
        f'git worktree add "{wt_path}" -b "{branch}"',
        cwd=main_dir,
        timeout=30,
    )
    if rc != 0:
        return None, None

    return wt_path, branch


def remove_worktree(wt_path, branch, main_dir):
    """Clean up a worktree and its branch."""
    if wt_path and os.path.isdir(wt_path):
        run_cmd(f'git worktree remove --force "{wt_path}"', cwd=main_dir, timeout=15)
    if branch:
        run_cmd(f'git branch -D "{branch}"', cwd=main_dir, timeout=10)


def run_worker(scenario_name, wt_path, branch, main_dir, config):
    """Run a single agent worker for one scenario. Returns a result dict."""
    agent_config = config.get("agent", {})
    model = os.environ.get(
        "MODEL", agent_config.get("default_model", "claude-haiku-4-5-20251001")
    )
    provider = agent_config.get("provider")
    timeout = agent_config.get("session_timeout", 3600)

    # Read BDD.md config for build/test commands
    stdout, _, _ = run_cmd("python3 scripts/parse_bdd_config.py BDD.md", cwd=main_dir)

    date = time.strftime("%Y-%m-%d")
    session_time = time.strftime("%H:%M")

    # Build a focused prompt for this single scenario
    prompt = f"""Today is {date} {session_time}.
You are working in a git worktree on branch: {branch}

Read these files first, in this order:
1. IDENTITY.md — your rules and purpose
2. BDD.md — the spec (this is the ONLY thing you build)
3. BDD_STATUS.md — which scenarios are currently covered

=== YOUR TARGET SCENARIO ===

You must implement exactly this one scenario this session:

  {scenario_name}

Do not pick a different scenario. Implement this scenario.

=== PHASE 1: Read BDD.md (MANDATORY) ===

BDD.md is your spec. Read it before doing anything else.

=== PHASE 2: Implement ===

The correct TDD cycle — ALL steps must complete before any commit:
  1. Write the test (name it after the scenario). Include a BDD marker comment
     on the line above the test: "# BDD: {scenario_name}" (Python) or
     "// BDD: {scenario_name}" (JS/TS/Go/Rust/Java). This marker is how
     the coverage checker links tests to scenarios.
  2. Run it — confirm it FAILS (do NOT commit yet)
  3. Write the implementation code that makes it pass
  4. Run build and tests — confirm ALL tests PASS
  5. Only now commit:
       git add -A -- ':!BDD_STATUS.md' ':!JOURNAL.md' ':!JOURNAL_INDEX.md'
       git commit -m "{date} {session_time}: implement {scenario_name}"

If checks fail after your implementation:
  - Read the error carefully
  - Fix it and re-run — up to 3 attempts
  - If still failing after 3 attempts: git checkout -- . (revert)

=== PHASE 3: Verify ===

Run: python3 scripts/check_bdd_coverage.py BDD.md
Confirm "{scenario_name}" is now marked [x]. Do not commit BDD_STATUS.md.

=== PHASE 4: Journal ===

Write a journal entry to JOURNAL_ENTRY.md (NOT JOURNAL.md):
## {date} {session_time} — [title]
[2-4 sentences: which scenario you covered, what approach you took]

Then: git add JOURNAL_ENTRY.md && git commit -m "{date} {session_time}: journal entry"

Now begin. Read IDENTITY.md first, then BDD.md.
"""

    # Write prompt to temp file
    prompt_file = (
        f"/tmp/baadd-prompt-{scenario_to_slug(scenario_name)}-{os.getpid()}.txt"
    )
    with open(prompt_file, "w") as f:
        f.write(prompt)

    # Copy runtime files to worktree
    for runtime_file in ["ISSUES_TODAY.md"]:
        src = os.path.join(main_dir, runtime_file)
        if os.path.exists(src):
            run_cmd(f'cp "{src}" "{wt_path}/"')

    # Run the agent - stream output in real-time
    event_log = os.path.join(wt_path, "agent_events.jsonl")
    provider_flag = f'--provider "{provider}" ' if provider else ""
    agent_cmd = (
        f'cd "{wt_path}" && '
        f'timeout {timeout} python3 "{main_dir}/scripts/agent.py" '
        f'{provider_flag}--model "{model}" --event-log "{event_log}" '
        f'< "{prompt_file}" 2>&1'
    )

    start_time = time.time()
    stdout_lines = []

    # Stream output in real-time with prefix
    prefix = f"[{scenario_name[:40]}]"
    try:
        proc = subprocess.Popen(
            agent_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=wt_path,
        )
        for line in proc.stdout:
            line = line.rstrip()
            stdout_lines.append(line)
            # Print in real-time with scenario prefix
            print(f"  {prefix} {line}", flush=True)
        proc.wait(timeout=timeout + 60)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout_lines.append("TIMEOUT")
        rc = 1
    elapsed = time.time() - start_time

    stdout = "\n".join(stdout_lines)

    # Clean up prompt
    try:
        os.unlink(prompt_file)
    except OSError:
        pass

    # Check if the agent made any commits
    commits_out, _, _ = run_cmd(
        f'git log --oneline HEAD.."{branch}" 2>/dev/null | wc -l',
        cwd=main_dir,
        timeout=10,
    )
    commit_count = int(commits_out.strip()) if commits_out.strip().isdigit() else 0

    # Check if tests pass in the worktree
    _, _, test_rc = run_cmd(
        'eval "$(python3 scripts/parse_bdd_config.py BDD.md)" && eval "$TEST_CMD"',
        cwd=wt_path,
        timeout=120,
    )

    return {
        "scenario": scenario_name,
        "branch": branch,
        "wt_path": wt_path,
        "commits": commit_count,
        "tests_pass": test_rc == 0,
        "elapsed_s": round(elapsed),
        "rc": rc,
        "stdout": stdout[:2000] if stdout else "",
    }


def merge_worker_result(result, main_dir):
    """Merge a successful worker's branch back to main. Returns True on success."""
    branch = result["branch"]
    scenario = result["scenario"]
    date = time.strftime("%Y-%m-%d")
    session_time = time.strftime("%H:%M")

    if result["commits"] == 0:
        print("    → THROWN AWAY (no commits — agent made no progress)", flush=True)
        return False

    if not result["tests_pass"]:
        print("    Tests failing in worktree — merging anyway", flush=True)

    # Merge
    merge_msg = f"{date} {session_time}: merge scenario '{scenario}'"
    stdout, stderr, rc = run_cmd(
        f'git merge --no-ff "{branch}" -m "{merge_msg}"',
        cwd=main_dir,
        timeout=30,
    )

    if rc != 0:
        # Try auto-resolve: prefer ours for management files
        run_cmd(
            "git checkout --ours BDD_STATUS.md JOURNAL_INDEX.md 2>/dev/null; git add -A",
            cwd=main_dir,
        )
        stdout, stderr, rc = run_cmd(
            f"git commit -m \"{date} {session_time}: merge '{scenario}' (auto-resolved)\"",
            cwd=main_dir,
            timeout=15,
        )
        if rc != 0:
            print(
                "    → THROWN AWAY (merge conflict could not be resolved)", flush=True
            )
            run_cmd("git merge --abort", cwd=main_dir)
            return False

    # Post-merge verification
    stdout_bdd, _, _ = run_cmd(
        "python3 scripts/parse_bdd_config.py BDD.md", cwd=main_dir
    )
    _, _, build_rc = run_cmd(
        'eval "$(python3 scripts/parse_bdd_config.py BDD.md)" && eval "$BUILD_CMD"',
        cwd=main_dir,
        timeout=120,
    )
    _, _, test_rc = run_cmd(
        'eval "$(python3 scripts/parse_bdd_config.py BDD.md)" && eval "$TEST_CMD"',
        cwd=main_dir,
        timeout=120,
    )

    if build_rc != 0 or test_rc != 0:
        print(
            "    Post-merge verification FAILED — keeping merge (investigate manually)",
            flush=True,
        )

    # Fold JOURNAL_ENTRY.md into JOURNAL.md if present
    journal_entry = os.path.join(main_dir, "JOURNAL_ENTRY.md")
    journal_md = os.path.join(main_dir, "JOURNAL.md")
    if os.path.exists(journal_entry):
        entry_content = read_file_safe(journal_entry)
        if entry_content.strip():
            journal_content = read_file_safe(journal_md)
            if journal_content:
                lines = journal_content.splitlines(True)
                new_content = (
                    lines[0] + "\n" + entry_content + "\n" + "".join(lines[1:])
                )
            else:
                new_content = "# Journal\n\n" + entry_content
            with open(journal_md, "w") as f:
                f.write(new_content)
        run_cmd(
            "git rm -f JOURNAL_ENTRY.md 2>/dev/null; rm -f JOURNAL_ENTRY.md",
            cwd=main_dir,
        )

    verdict = (
        "MERGED (tests failed — investigate)"
        if (not result["tests_pass"] or build_rc != 0 or test_rc != 0)
        else "MERGED"
    )
    print(f"    → {verdict}", flush=True)
    return True


def main():
    parser = argparse.ArgumentParser(description="BAADD Orchestrator")
    parser.add_argument(
        "--max-agents",
        type=int,
        default=None,
        help="Override max parallel agents from poppins.yml",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show the plan but don't execute"
    )
    parser.add_argument("--bdd", default="BDD.md", help="Path to BDD.md")
    parser.add_argument(
        "--model",
        default=None,
        help="Override model for the orchestrator planning call",
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="Force provider: anthropic|openai|groq|ollama|moonshot|dashscope|custom",
    )
    args = parser.parse_args()

    config = get_config()
    orch_config = config.get("orchestration", {})
    agent_config = config.get("agent", {})
    max_agents = args.max_agents or orch_config.get("max_parallel_agents", 3)

    # Apply poppins.yml config as env var defaults (env vars take priority)
    # This lets users configure their LLM once in poppins.yml
    for section, prefix_map in [
        (orch_config, [("base_url", "CUSTOM_BASE_URL"), ("api_key", None)]),
        (agent_config, [("base_url", "CUSTOM_BASE_URL"), ("api_key", None)]),
    ]:
        base_url = section.get("base_url")
        api_key = section.get("api_key")
        if base_url and not os.environ.get("CUSTOM_BASE_URL"):
            os.environ["CUSTOM_BASE_URL"] = base_url
        if api_key:
            # Set the appropriate key env var based on provider
            cfg_provider = section.get("provider", "")
            key_env = {
                "anthropic": "ANTHROPIC_API_KEY",
                "openai": "OPENAI_API_KEY",
                "groq": "GROQ_API_KEY",
                "moonshot": "MOONSHOT_API_KEY",
                "dashscope": "DASHSCOPE_API_KEY",
                "custom": "CUSTOM_API_KEY",
            }.get(cfg_provider, "CUSTOM_API_KEY")
            if not os.environ.get(key_env):
                os.environ[key_env] = api_key

    # Set OLLAMA_HOST from base_url if provider is ollama
    for section in [orch_config, agent_config]:
        if section.get("provider") == "ollama":
            base_url = section.get("base_url")
            if base_url and not os.environ.get("OLLAMA_HOST"):
                # Strip /v1 suffix if present — OLLAMA_HOST is the root
                os.environ["OLLAMA_HOST"] = base_url.rstrip("/").removesuffix("/v1")

    # Provider: CLI flag > poppins.yml > env var detection
    provider = args.provider or orch_config.get("provider") or detect_provider()
    # Model: CLI flag > poppins.yml orchestrator model > provider default
    model_orch_override = args.model or orch_config.get("model_orchestrator") or None

    main_dir = os.getcwd()
    date = time.strftime("%Y-%m-%d")
    session_time = time.strftime("%H:%M")
    session_start_sha, _, _ = run_cmd("git rev-parse HEAD", cwd=main_dir)

    print(f"=== BAADD Orchestrator ({date} {session_time}) ===", flush=True)
    print(f"  Max parallel agents: {max_agents}", flush=True)
    print(
        f"  Provider:            {provider or 'none (will use BDD.md order)'}",
        flush=True,
    )
    print(
        f"  Orchestrator model:  {model_orch_override or 'provider default'}",
        flush=True,
    )
    print("", flush=True)

    # Step 1: Find uncovered scenarios
    uncovered = get_uncovered_scenarios(args.bdd)
    if not uncovered:
        print("All scenarios covered. Nothing to do.", flush=True)
        return

    print(f"  Uncovered scenarios: {len(uncovered)}", flush=True)
    for feature, scenario in uncovered:
        print(f"    - [{feature}] {scenario}", flush=True)
    print("", flush=True)

    # Step 2: AI-powered ordering
    print("  Ordering scenarios...", flush=True)
    bdd_content = read_file_safe(args.bdd)
    ordered_names = plan_scenario_order(
        uncovered, bdd_content, provider, model_orch_override
    )
    print("  Execution order:", flush=True)
    for i, name in enumerate(ordered_names, 1):
        print(f"    {i}. {name}", flush=True)
    print("", flush=True)

    if args.dry_run:
        print("  [dry-run] Would spawn agents for the above scenarios.", flush=True)
        return

    # Step 3: Select only the top N scenarios to run this session
    selected_names = ordered_names[:max_agents]
    if len(ordered_names) > max_agents:
        print(
            f"  Selecting top {max_agents} scenario(s) to run this session "
            f"({len(ordered_names) - max_agents} deferred to next run):",
            flush=True,
        )
        for i, name in enumerate(selected_names, 1):
            print(f"    {i}. {name}", flush=True)
        print("", flush=True)

    # Step 4: Create worktrees for selected scenarios only
    print(
        f"\n  Creating worktrees for {len(selected_names)} scenario(s)...", flush=True
    )
    workers = {}
    for scenario_name in selected_names:
        slug = scenario_to_slug(scenario_name)
        wt_path, branch = create_worktree(slug, main_dir)
        if not wt_path:
            print(
                f"  [WARN] Failed to create worktree for: {scenario_name}", flush=True
            )
            continue
        workers[scenario_name] = (wt_path, branch)
        print(f"  {scenario_name[:50]} → {wt_path}", flush=True)

    if not workers:
        print("  No worktrees created. Exiting.", flush=True)
        return

    # Step 4: Run all agents in parallel (ThreadPoolExecutor handles concurrency limit)
    print(
        f"\n  Running {len(workers)} agents (max {max_agents} concurrent)...",
        flush=True,
    )
    results = []

    with ThreadPoolExecutor(max_workers=max_agents) as executor:
        futures = {}
        for scenario_name, (wt_path, branch) in workers.items():
            future = executor.submit(
                run_worker,
                scenario_name,
                wt_path,
                branch,
                main_dir,
                config,
            )
            futures[future] = scenario_name

        # Collect results as they complete (merge happens later in order)
        for future in as_completed(futures):
            scenario_name = futures[future]
            try:
                result = future.result()
                results.append(result)
                commits = result["commits"]
                tests_pass = result["tests_pass"]
                if commits == 0:
                    status_str = "[FAIL: no commits]"
                elif not tests_pass:
                    status_str = "[WARN: tests failing]"
                else:
                    status_str = "[OK]"
                print(
                    f"  {status_str} {scenario_name} — {commits} commit(s), {result['elapsed_s']}s",
                    flush=True,
                )
            except Exception as e:
                print(f"  [ERROR] {scenario_name}: {e}", flush=True)
                results.append(
                    {
                        "scenario": scenario_name,
                        "branch": workers[scenario_name][1],
                        "wt_path": workers[scenario_name][0],
                        "commits": 0,
                        "tests_pass": False,
                        "elapsed_s": 0,
                        "rc": 1,
                        "stdout": str(e),
                    }
                )

    # Step 5: Merge all results in the planned order (sequential, but doesn't block spawning)
    print(f"\n  Merging {len(results)} results in order...", flush=True)
    for result in sorted(results, key=lambda r: selected_names.index(r["scenario"])):
        scenario = result["scenario"]
        commits = result["commits"]
        tests = "tests pass" if result["tests_pass"] else "tests failing"
        print(f"  [{scenario[:50]}] — {commits} commit(s), {tests}", flush=True)
        merged = merge_worker_result(result, main_dir)
        result["merged"] = merged

    # Clean up worktrees
    print(f"\n  Cleaning up {len(workers)} worktrees...", flush=True)
    for scenario_name, (wt_path, branch) in workers.items():
        remove_worktree(wt_path, branch, main_dir)

    # Step 5: Final wrap-up
    print("  Updating coverage...", flush=True)
    run_cmd(
        "python3 scripts/check_bdd_coverage.py BDD.md > BDD_STATUS.md", cwd=main_dir
    )
    run_cmd(
        'git add -A && git diff --cached --quiet || git commit -m "'
        + f'{date} {session_time}: orchestrator wrap-up"',
        cwd=main_dir,
    )

    # Summary
    merged_count = sum(1 for r in results if r.get("merged"))
    failed_count = sum(1 for r in results if not r.get("merged"))
    total_time = sum(r.get("elapsed_s", 0) for r in results)

    deferred = ordered_names[max_agents:]

    print("\n=== Orchestrator complete ===", flush=True)
    print(f"  Scenarios attempted: {len(results)}", flush=True)
    print(f"  Merged:             {merged_count}", flush=True)
    print(f"  Thrown away:        {failed_count}", flush=True)
    print(f"  Total agent time:   {total_time}s", flush=True)
    print("", flush=True)
    col = 42
    print(f"  {'Scenario':<{col}} {'Commits':>7}  {'Tests':>6}  Outcome", flush=True)
    print(f"  {'-' * col}  {'-' * 7}  {'-' * 6}  {'-' * 30}", flush=True)
    for r in sorted(results, key=lambda r: selected_names.index(r["scenario"])):
        commits = r["commits"]
        tests = "pass" if r["tests_pass"] else ("—" if commits == 0 else "FAIL")
        if r.get("merged"):
            outcome = (
                "MERGED" if r["tests_pass"] else "MERGED (tests failed — investigate)"
            )
        elif commits == 0:
            outcome = "THROWN AWAY (no commits)"
        else:
            outcome = "THROWN AWAY (merge failed)"
        print(
            f"  {r['scenario'][:col]:<{col}}  {commits:>7}  {tests:>6}  {outcome}",
            flush=True,
        )
    print("=============================", flush=True)

    if deferred:
        print(
            f"\n  {len(deferred)} scenario(s) remaining — run again to continue:",
            flush=True,
        )
        for i, name in enumerate(deferred, 1):
            print(f"    {i}. {name}", flush=True)
        print(
            f"\n  python3 scripts/orchestrate.py --max-agents {max_agents}", flush=True
        )

    # Write orchestrator event log
    event_log_path = os.path.join(main_dir, "orchestrator_events.jsonl")
    with open(event_log_path, "a") as f:
        f.write(
            json.dumps(
                {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "event": "orchestration_complete",
                    "scenarios_attempted": len(results),
                    "merged": merged_count,
                    "failed": failed_count,
                    "total_agent_time_s": total_time,
                    "results": [
                        {
                            "scenario": r["scenario"],
                            "commits": r["commits"],
                            "tests_pass": r["tests_pass"],
                            "merged": r.get("merged", False),
                            "elapsed_s": r["elapsed_s"],
                        }
                        for r in results
                    ],
                }
            )
            + "\n"
        )

    # Write orchestrator journal entry
    merged_names = [r["scenario"] for r in results if r.get("merged")]
    failed_names = [r["scenario"] for r in results if not r.get("merged")]
    coverage_out, _, _ = run_cmd(
        "python3 scripts/check_bdd_coverage.py BDD.md", cwd=main_dir
    )
    covered_count = len([l for l in coverage_out.splitlines() if "[x]" in l])
    total_count = len([l for l in coverage_out.splitlines() if "- [" in l])

    journal_md = os.path.join(main_dir, "JOURNAL.md")
    journal_content = read_file_safe(journal_md)
    orchestrator_entry = f"\n## {date} {session_time} — Orchestrator session\n\n"
    orchestrator_entry += (
        f"Ran {len(results)} agents in parallel (max {max_agents} concurrent). "
    )
    orchestrator_entry += f"Total agent time: {total_time}s.\n\n"
    if merged_names:
        orchestrator_entry += (
            f"**Merged ({merged_count}):** {', '.join(merged_names[:5])}"
        )
        if len(merged_names) > 5:
            orchestrator_entry += f", and {len(merged_names) - 5} more"
        orchestrator_entry += "\n"
    if failed_names:
        orchestrator_entry += (
            f"**Failed ({failed_count}):** {', '.join(failed_names[:5])}"
        )
        if len(failed_names) > 5:
            orchestrator_entry += f", and {len(failed_names) - 5} more"
        orchestrator_entry += "\n"
    orchestrator_entry += f"\nCoverage: {covered_count}/{total_count} scenarios.\n"

    if journal_content:
        lines = journal_content.splitlines(True)
        new_journal = lines[0] + "\n" + orchestrator_entry + "".join(lines[1:])
    else:
        new_journal = "# Journal\n\n" + orchestrator_entry
    with open(journal_md, "w") as f:
        f.write(new_journal)
    run_cmd(
        f"git add JOURNAL.md && git commit -m '{date} {session_time}: orchestrator journal'",
        cwd=main_dir,
    )

    # Update JOURNAL_INDEX.md
    journal_index = os.path.join(main_dir, "JOURNAL_INDEX.md")
    index_content = read_file_safe(journal_index)
    session_summary = f"orchestrator: {merged_count} merged, {failed_count} failed"
    if not index_content:
        index_content = "# Journal Index\n\n| Date | Time | Coverage | Summary |\n|------|------|----------|--------|\n"
    index_lines = index_content.splitlines()
    if "| Date |" not in index_content:
        index_lines = [
            "# Journal Index",
            "",
            "| Date | Time | Coverage | Summary |",
            "|------|------|----------|--------|",
        ]
    new_row = f"| {date} | {session_time} | {covered_count}/{total_count} | {session_summary} |\n"
    index_content = "\n".join(index_lines) + "\n" + new_row
    with open(journal_index, "w") as f:
        f.write(index_content)
    run_cmd(
        f"git add JOURNAL_INDEX.md && git commit -m '{date} {session_time}: update journal index'",
        cwd=main_dir,
    )


if __name__ == "__main__":
    main()
