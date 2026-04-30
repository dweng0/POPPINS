#!/usr/bin/env python3
"""
Orchestrator — coordinates parallel agent workers for BAADD evolution.

Finds all uncovered scenarios in BDD.md order, spawns up to max_parallel_agents
workers (each in its own git worktree), then merges results sequentially with
post-merge verification.

Usage:
    ANTHROPIC_API_KEY=sk-... python3 scripts/orchestrate.py
    python3 scripts/orchestrate.py --max-agents 2 --dry-run
"""

import os
import sys
import json
import subprocess
import tempfile
import argparse
import time
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from glob import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_poppins_config import get_config
from check_bdd_coverage import parse_scenarios, find_test_files, check_coverage
from pm_worker import run_pm_pipeline



def run_integration_tests(scenario_results, main_dir):
    """Run integration tests after merging."""
    print("    [INTEGRATION TEST] Running post-merge tests...", flush=True)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(scenario_results, f)
        results_file = f.name
    
    try:
        stdout, stderr, rc = run_cmd(
            f"python3 scripts/integration_test_agent.py --main-dir . --results-file {results_file} --max-fix-attempts 1",
            cwd=main_dir,
            timeout=120,
        )
        
        # Parse the output for pass/fail
        if "[OK]" in stdout or rc == 0:
            print(f"    [INTEGRATION TEST] PASSED", flush=True)
            return True, stdout
        else:
            print(f"    [INTEGRATION TEST] FAILED: {stderr or stdout}", flush=True)
            return False, stderr or stdout
    finally:
        if os.path.exists(results_file):
            os.unlink(results_file)


# Phase detection — log filename prefix → display label (in pipeline order)
_PHASE_PREFIXES = [
    ("pm_plan",    "PM-PLAN"),
    ("se",         "SE"),
    ("tester",     "TESTER"),
    ("pm_accept",  "ACCEPT"),
]


def _read_wt_phase_state(wt_path):
    """Return (active_label, current_iter, max_iter, done_labels) for one worktree.

    Uses file mtime to pick the most recently written log per phase so retries
    always reflect the live attempt rather than a stale peak from a prior attempt.
    """
    by_phase = {}  # prefix -> (mtime, peak_iter, max_iter, completed)
    for log_path in glob(os.path.join(wt_path, "agent_events_*.jsonl")):
        name = os.path.basename(log_path)
        phase_key = None
        for prefix, _label in _PHASE_PREFIXES:
            if name.startswith(f"agent_events_{prefix}_"):
                phase_key = prefix
                break
        if phase_key is None:
            continue
        mtime = os.path.getmtime(log_path)
        existing = by_phase.get(phase_key)
        if existing and existing[0] >= mtime:
            continue
        peak, mx, done = 0, 75, False
        try:
            with open(log_path) as f:
                for raw in f:
                    try:
                        rec = json.loads(raw)
                        ev = rec.get("event")
                        if ev == "iteration_start":
                            peak = max(peak, rec.get("iteration", 0))
                            mx = rec.get("max_iterations", mx)
                        elif ev == "session_end":
                            done = True
                    except (json.JSONDecodeError, KeyError):
                        pass
        except OSError:
            pass
        by_phase[phase_key] = (mtime, peak, mx, done)

    done_labels, active_label, current_iter, max_iter = [], None, 0, 75
    for prefix, label in _PHASE_PREFIXES:
        if prefix not in by_phase:
            continue
        _mtime, peak, mx, completed = by_phase[prefix]
        if completed:
            done_labels.append(label)
        elif active_label is None:
            active_label, current_iter, max_iter = label, peak, mx

    return active_label, current_iter, max_iter, done_labels


def _progress_bar(wt_paths, _max_iter_unused, _num_agents_unused, stop_event, interval=8):
    """Background thread: per-worktree phase + iteration bar on the terminal.

    Each worktree shows:  PM-PLAN✓ SE✓ [TESTER ████░░░░░░░░░░░░░░░░░░░░ 8/75]
    """
    if not sys.stdout.isatty():
        return
    bar_width = 20
    last_len = 0
    while not stop_event.wait(timeout=interval):
        parts = []
        for wt_path in wt_paths:
            active, curr, mx, done = _read_wt_phase_state(wt_path)
            done_str = " ".join(f"{l}✓" for l in done)
            if active:
                pct = curr / mx if mx > 0 else 0.0
                filled = int(bar_width * pct)
                bar = "█" * filled + "░" * (bar_width - filled)
                seg = f"[{active} {bar} {curr}/{mx}]"
                parts.append(f"{done_str} {seg}".strip())
            elif done_str:
                parts.append(done_str)
        if parts:
            line = "  " + "   ".join(parts)
            print(f"\r{' ' * last_len}\r{line}", end="", flush=True)
            last_len = len(line)
    if last_len:
        print(f"\r{' ' * last_len}\r", end="", flush=True)


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


def run_cmd(cmd, cwd=None, timeout=30, capture=True):
    """Run a shell command, return (stdout, stderr, returncode).

    capture=True  — buffer output, return it (default)
    capture=False — discard output (DEVNULL), return empty strings
    capture=None  — inherit parent stdio (output visible in terminal, no buffering)
    """
    if capture is None:
        proc = subprocess.Popen(cmd, shell=True, cwd=cwd)
    else:
        stdout_sink = subprocess.PIPE if capture else subprocess.DEVNULL
        stderr_sink = subprocess.PIPE if capture else subprocess.DEVNULL
        proc = subprocess.Popen(
            cmd, shell=True, stdout=stdout_sink, stderr=stderr_sink, text=True, cwd=cwd
        )
    try:
        out, err = proc.communicate(timeout=timeout)
        if capture:
            return out.strip(), err.strip(), proc.returncode
        return "", "", proc.returncode
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()  # drain pipes so no zombie
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



def select_scenarios(ordered_names, max_agents):
    """Return (selected, remaining) where selected is the top max_agents scenarios."""
    return ordered_names[:max_agents], ordered_names[max_agents:]


def format_worker_output(result):
    """Format worker result with scenario prefix on each line."""
    scenario_name = result.get("scenario", "unknown")
    stdout = result.get("stdout", "")
    commits = result.get("commits", 0)
    tests_pass = result.get("tests_pass", False)
    elapsed_s = result.get("elapsed_s", 0)
    rc = result.get("rc", 0)

    lines = [f"[{scenario_name}] {line}" for line in stdout.split("\n") if line.strip()]
    if commits == 0:
        status = "FAIL: no commits"
    elif not tests_pass:
        status = "WARN: tests failing"
    else:
        status = "OK"
    lines.append(f"[{scenario_name}] {status} — {commits} commit(s), {elapsed_s:.1f}s, exit={rc}")
    return "\n".join(lines)


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




def merge_worker_result(result, main_dir):
    """Merge a successful worker's branch back to main. Returns True on success."""
    branch = result["branch"]
    scenario = result["scenario"]
    date = time.strftime("%Y-%m-%d")
    session_time = time.strftime("%H:%M")

    if result["commits"] == 0:
        print("    → THROWN AWAY (no commits — agent made no progress)", flush=True)
        return False

    if not result.get("has_marker", True):
        print(
            f"    → THROWN AWAY (BDD marker '# BDD: {scenario}' not found in test files)",
            flush=True,
        )
        return False

    if not result["tests_pass"]:
        print(
            "    → THROWN AWAY (tests failing in worktree — PM rejected)", flush=True
        )
        return False

    # Guard: reject if SE deleted existing files that the PM didn't explicitly
    # approve in PLAN.md section 5.
    merge_base_out, _, mb_rc = run_cmd(
        f'git merge-base HEAD "{branch}"', cwd=main_dir
    )
    if mb_rc == 0:
        merge_base = merge_base_out.strip()
        deleted_out, _, _ = run_cmd(
            f'git diff --name-only --diff-filter=D "{merge_base}"..."{branch}"',
            cwd=main_dir,
        )
        deleted_files = [f for f in deleted_out.splitlines() if f.strip()]
        if deleted_files:
            # Parse PM-approved deletions from PLAN.md "## 5. Files to delete" section
            approved_deletions = set()
            plan_path = os.path.join(result["wt_path"], "PLAN.md")
            if os.path.exists(plan_path):
                with open(plan_path) as f:
                    plan_text = f.read()
                in_section = False
                for line in plan_text.splitlines():
                    if re.match(r"^##\s+5\.", line):
                        in_section = True
                        continue
                    if in_section:
                        if re.match(r"^##\s+", line):
                            break
                        # Bullet lines: "  - path/to/file — justification"
                        m = re.match(r"^\s*[-*]\s+(\S+)", line)
                        if m:
                            approved_deletions.add(m.group(1))

            unapproved = [f for f in deleted_files if f not in approved_deletions]
            if unapproved:
                print(
                    f"    → THROWN AWAY (SE deleted files not approved in PLAN.md §5: {unapproved})",
                    flush=True,
                )
                return False
            if approved_deletions:
                print(
                    f"    Approved deletions (listed in PLAN.md §5): {sorted(approved_deletions & set(deleted_files))}",
                    flush=True,
                )

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

    # Post-merge verification with integration test agent
    # First, run integration tests to catch any issues
    integration_success, integration_output = run_integration_tests([result], main_dir)
    
    if not integration_success:
        print(
            "    Post-merge verification FAILED — reverting merge (PM rejected)",
            flush=True,
        )
        run_cmd("git revert --no-edit HEAD", cwd=main_dir, timeout=30)
        print("    → THROWN AWAY (post-merge tests failed — reverted)", flush=True)
        return False

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

    print("    → MERGED", flush=True)
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
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=None,
        help="Override number of sequential rounds from poppins.yml",
    )
    args = parser.parse_args()

    config = get_config()
    orch_config = config.get("orchestration", {})
    agent_config = config.get("agent", {})
    max_agents = args.max_agents or orch_config.get("max_parallel_agents", 3)
    max_rounds = args.max_rounds if args.max_rounds is not None else orch_config.get("max_rounds", 1)

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
    print(f"  Max rounds: {max_rounds}", flush=True)
    print(
        f"  Provider:            {provider or 'none (will use BDD.md order)'}",
        flush=True,
    )
    print(
        f"  Orchestrator model:  {model_orch_override or 'provider default'}",
        flush=True,
    )
    print("", flush=True)

    # Pre-flight: verify existing tests pass before starting (skip in dry-run)
    if not args.dry_run:
        # Parse config once — used for both the test run and the error hint
        bdd_cfg_out, _, _ = run_cmd("python3 scripts/parse_bdd_config.py BDD.md", cwd=main_dir)
        test_cmd_hint = "pytest"
        for _line in bdd_cfg_out.splitlines():
            if _line.startswith("export TEST_CMD="):
                test_cmd_hint = _line.split("=", 1)[1].strip().strip("'")
                break

        print("  Pre-flight: running test suite...", flush=True)
        _, _, preflight_rc = run_cmd(
            f'eval "$(python3 scripts/parse_bdd_config.py BDD.md)" && eval "$TEST_CMD"',
            cwd=main_dir,
            timeout=600,
            capture=None,  # stream to terminal — no Python buffering
        )
        if preflight_rc != 0:
            print("", flush=True)
            print("ERROR: existing tests are failing — pipeline cannot run.", flush=True)
            print("Fix the failing tests on main before starting a cycle.", flush=True)
            print("", flush=True)
            print(f"  Run:  {test_cmd_hint}", flush=True)
            sys.exit(1)
        print("  Pre-flight: OK", flush=True)
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

    # Step 2: Use BDD.md natural order (top-to-bottom = intentional priority order)
    ordered_names = [s for _, s in uncovered]

    print("  Execution order (BDD.md order):", flush=True)
    for i, name in enumerate(ordered_names, 1):
        print(f"    {i}. {name}", flush=True)
    print("", flush=True)

    if args.dry_run:
        total_slots = max_rounds * max_agents
        for round_num in range(1, max_rounds + 1):
            start = (round_num - 1) * max_agents
            round_scenarios = ordered_names[start : start + max_agents]
            if not round_scenarios:
                break
            print(f"  Round {round_num}/{max_rounds}: {len(round_scenarios)} scenario(s)", flush=True)
            for name in round_scenarios:
                print(f"    - {name}", flush=True)
        truly_deferred = ordered_names[total_slots:]
        if truly_deferred:
            print(f"\n  {len(truly_deferred)} scenario(s) deferred beyond {max_rounds} round(s).", flush=True)
        print(f"  [dry-run] Would spawn agents across {max_rounds} round(s).", flush=True)
        return

    # Rounds loop: each round picks the next max_agents scenarios from the ordered list
    all_results = []
    all_selected_names = []
    remaining_names = list(ordered_names)

    for round_num in range(1, max_rounds + 1):
        if not remaining_names:
            print(f"\n  All scenarios exhausted before round {round_num}. Stopping.", flush=True)
            break

        selected_names = remaining_names[:max_agents]
        remaining_names = remaining_names[max_agents:]
        all_selected_names.extend(selected_names)

        if max_rounds > 1:
            print(f"\n=== Round {round_num}/{max_rounds} — {len(selected_names)} scenario(s) ===", flush=True)

        # Create worktrees for this round's scenarios
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
            # Extract scoped spec into worktree — avoids loading full BDD.md per agent
            scenario_md = os.path.join(wt_path, "BDD_SCENARIO.md")
            _, _, extract_rc = run_cmd(
                f'bash "{main_dir}/scripts/extract_scenario.sh" '
                f'"{scenario_name}" "{main_dir}/BDD.md" "{scenario_md}"'
            )
            if extract_rc != 0 or not os.path.exists(scenario_md):
                print(
                    f"  [ERROR] extract_scenario.sh failed for '{scenario_name}' — skipping "
                    f"(do not fall back to full BDD.md; fix extract_scenario.sh)",
                    flush=True,
                )
                remove_worktree(wt_path, branch, main_dir)
                continue
            workers[scenario_name] = (wt_path, branch)
            lines = len(open(scenario_md).readlines())
            print(f"  {scenario_name[:50]} → {wt_path} ({lines} lines spec)", flush=True)

        if not workers:
            print("  No worktrees created for this round. Skipping.", flush=True)
            continue

        # Run agents in parallel
        print(
            f"\n  Running {len(workers)} agents (max {max_agents} concurrent)...",
            flush=True,
        )
        results = []
        completed_this_session = 0
        progress_lock = threading.Lock()

        # Combined iteration progress bar across all worktrees
        max_iter_cfg = agent_config.get("max_iterations", 75)
        wt_paths = [wt for wt, _branch in workers.values()]
        pb_stop = threading.Event()
        pb_thread = threading.Thread(
            target=_progress_bar,
            args=(wt_paths, max_iter_cfg, len(workers), pb_stop),
            daemon=True,
        )
        pb_thread.start()

        with ThreadPoolExecutor(max_workers=max_agents) as executor:
            futures = {}
            for scenario_name, (wt_path, branch) in workers.items():
                future = executor.submit(
                    run_pm_pipeline,
                    scenario_name,
                    wt_path,
                    branch,
                    main_dir,
                    config,
                )
                futures[future] = scenario_name

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
                    with progress_lock:
                        completed_this_session += 1
                        done_total = len(all_results) + completed_this_session
                        remaining = len(ordered_names) - done_total
                        print(
                            f"  {status_str} {scenario_name} — {commits} commit(s), {result['elapsed_s']}s"
                            f"  [{done_total}/{len(ordered_names)} done, {remaining} remaining]",
                            flush=True,
                        )
                except Exception as e:
                    print(f"  [ERROR] {scenario_name}: {e}", flush=True)
                    wt_path, branch, _ = workers[scenario_name]
                    results.append(
                        {
                            "scenario": scenario_name,
                            "branch": branch,
                            "wt_path": wt_path,
                            "commits": 0,
                            "tests_pass": False,
                            "has_marker": False,
                            "elapsed_s": 0,
                            "rc": 1,
                            "stdout": str(e),
                        }
                    )

        pb_stop.set()
        pb_thread.join(timeout=2)

        # Merge results in planned order
        print(f"\n  Merging {len(results)} results in order...", flush=True)
        for result in sorted(results, key=lambda r: selected_names.index(r["scenario"])):
            scenario = result["scenario"]
            commits = result["commits"]
            tests = "tests pass" if result["tests_pass"] else "tests failing"
            print(f"  [{scenario[:50]}] — {commits} commit(s), {tests}", flush=True)
            merged = merge_worker_result(result, main_dir)
            result["merged"] = merged

        # Round progress summary
        round_merged = sum(1 for r in results if r.get("merged"))
        round_failed = len(results) - round_merged
        done_so_far = len(all_results) + len(results)
        remaining_after = len(ordered_names) - done_so_far
        print(
            f"\n  Round {round_num}/{max_rounds} complete — "
            f"{round_merged} merged, {round_failed} thrown away. "
            f"Progress: {done_so_far}/{len(ordered_names)} attempted, {remaining_after} remaining.",
            flush=True,
        )

        # Clean up worktrees for this round
        print(f"\n  Cleaning up {len(workers)} worktrees...", flush=True)
        for scenario_name, (wt_path, branch) in workers.items():
            remove_worktree(wt_path, branch, main_dir)

        # Put thrown-away scenarios back so they appear in the remaining list
        # and can be retried in a future session.
        thrown_away = [r["scenario"] for r in results if not r.get("merged")]
        remaining_names = thrown_away + remaining_names

        all_results.extend(results)

    results = all_results
    deferred = remaining_names

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

    print("\n=== Orchestrator complete ===", flush=True)
    print(f"  Scenarios attempted: {len(results)}", flush=True)
    print(f"  Merged:             {merged_count}", flush=True)
    print(f"  Thrown away:        {failed_count}", flush=True)
    print(f"  Total agent time:   {total_time}s", flush=True)
    print("", flush=True)
    col = 42
    print(f"  {'Scenario':<{col}} {'Commits':>7}  {'Tests':>6}  Outcome", flush=True)
    print(f"  {'-' * col}  {'-' * 7}  {'-' * 6}  {'-' * 30}", flush=True)
    for r in sorted(results, key=lambda r: all_selected_names.index(r["scenario"])):
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
            f"\n  python3 scripts/orchestrate.py --max-agents {max_agents} --max-rounds {max_rounds}",
            flush=True,
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
    # BDD_STATUS.md was just written above — parse it instead of re-running the script
    bdd_status = read_file_safe(os.path.join(main_dir, "BDD_STATUS.md"))
    covered_count = len([l for l in bdd_status.splitlines() if "[x]" in l])
    total_count = len([l for l in bdd_status.splitlines() if "- [" in l])

    journal_md = os.path.join(main_dir, "JOURNAL.md")
    journal_content = read_file_safe(journal_md)
    orchestrator_entry = f"\n## {date} {session_time} — Orchestrator session\n\n"
    orchestrator_entry += (
        f"Ran {len(results)} agents across {max_rounds} round(s) (max {max_agents} concurrent per round). "
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
