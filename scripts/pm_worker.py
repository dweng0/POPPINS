#!/usr/bin/env python3
"""
PM Worker — runs the PM → SE → Tester → PM pipeline for one scenario.

Each scenario gets its own worktree. Inside the worktree three sequential
agent.py calls handle design, implementation, and QA, coordinated through
files written in the worktree:

  PLAN.md        — PM's design doc (units, interfaces, DI boundaries, test strategy)
  QA_REPORT.md   — Tester's findings (marker present?, test results, coverage check)
  RETRY_NOTES.md — PM's targeted fix instructions for the SE (retries only)

Only the PM commits. The SE and Tester write files only.

Stdout conventions:
  [<scenario>] <phase> banner lines use ===
  [<scenario>] INFO lines use plain text
  [<scenario>] WARN / ERROR are prefixed
  Each agent's own output is prefixed with [<scenario> <ROLE>]
"""

import json
import os
import re
import sys
import subprocess
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parse_poppins_config import get_config as _get_poppins_config

# Per-phase agent timeouts (seconds).  PM-plan and SE need more time than Tester/Accept.
TIMEOUT_PM_PLAN   = 720
TIMEOUT_SE        = 900
TIMEOUT_TESTER    = 480
TIMEOUT_PM_ACCEPT = 360

MAX_RETRIES = 3

# Existing files the SE must never modify. Loaded from poppins.yml
# agent.protected_paths; falls back to built-in defaults.
_poppins_cfg = _get_poppins_config()
PROTECTED_PATHS = _poppins_cfg.get("agent", {}).get("protected_paths") or [
    "scripts/",
    ".github/",
    "IDENTITY.md",
    "BDD.md",
    "conftest.py",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_se_protected_files(wt_path):
    """Return list of protected files the SE modified. Empty = clean."""
    diff_out, _, _ = run_cmd(
        "git diff --name-only HEAD 2>/dev/null", cwd=wt_path, timeout=10
    )
    modified = [f.strip() for f in diff_out.splitlines() if f.strip()]
    violations = []
    for path in modified:
        for protected in PROTECTED_PATHS:
            if path == protected or path.startswith(protected):
                violations.append(path)
                break
    return violations


def run_cmd(cmd, cwd=None, timeout=30):
    """Run a shell command. Returns (stdout, stderr, returncode)."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=timeout,
    )
    return result.stdout, result.stderr, result.returncode


def _read_event_log_tokens(event_log_path):
    """Return cumulative_output_tokens from the latest api_response event, or 0."""
    total = 0
    try:
        with open(event_log_path) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec.get("event") == "api_response":
                        total = rec.get("cumulative_output_tokens", total) or total
                except (json.JSONDecodeError, KeyError):
                    pass
    except OSError:
        pass
    return total


def _tps_monitor(event_log_path, stream_prefix, t0, stop_event,
                 interval=5, min_tokens=10):
    """Background thread: print periodic TPS status lines while an agent runs."""
    while not stop_event.wait(timeout=interval):
        elapsed = time.time() - t0
        tokens = _read_event_log_tokens(event_log_path)
        if tokens >= min_tokens and elapsed > 0:
            tps = tokens / elapsed
            print(
                f"  [{stream_prefix}] {tokens} tok | {tps:.1f} TPS | {round(elapsed)}s",
                flush=True,
            )


def run_agent(prompt, wt_path, main_dir, provider, model,
              log_suffix, phase_timeout, stream_prefix):
    """
    Write prompt to a temp file, run agent.py, buffer output.
    Prints periodic TPS status lines while running; dumps full output when done.
    Returns (stdout_str, returncode, elapsed_seconds).
    """
    slug = re.sub(r"[^a-z0-9]", "_", log_suffix.lower())[:40]
    prompt_file = f"/tmp/baadd-pm-{slug}-{os.getpid()}.txt"
    with open(prompt_file, "w") as f:
        f.write(prompt)

    event_log = os.path.join(wt_path, f"agent_events_{slug}.jsonl")
    provider_flag = f'--provider "{provider}" ' if provider else ""
    skills_dir = os.path.join(main_dir, "skills")
    skills_flag = f'--skills "{skills_dir}" ' if os.path.isdir(skills_dir) else ""
    cmd = (
        f'cd "{wt_path}" && '
        f'timeout {phase_timeout} python3 "{main_dir}/scripts/agent.py" '
        f'{provider_flag}{skills_flag}--model "{model}" --event-log "{event_log}" '
        f'< "{prompt_file}" 2>&1'
    )

    stdout_lines = []
    t0 = time.time()
    stop_event = threading.Event()
    monitor = threading.Thread(
        target=_tps_monitor,
        args=(event_log, stream_prefix, t0, stop_event),
        daemon=True,
    )
    monitor.start()

    try:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=wt_path,
        )
        for line in proc.stdout:
            stdout_lines.append(line.rstrip())
        proc.wait(timeout=phase_timeout + 30)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout_lines.append("TIMEOUT")
        rc = 1
    finally:
        stop_event.set()
        monitor.join(timeout=2)

    elapsed = round(time.time() - t0)

    # Print final TPS line, then dump full buffered output
    tokens = _read_event_log_tokens(event_log)
    tps_str = f" | {tokens / elapsed:.1f} TPS" if elapsed > 0 and tokens >= 10 else ""
    print(
        f"  [{stream_prefix}] done — {tokens} tok{tps_str} | {elapsed}s",
        flush=True,
    )
    for line in stdout_lines:
        print(f"  [{stream_prefix}] {line}", flush=True)

    try:
        os.unlink(prompt_file)
    except OSError:
        pass

    return "\n".join(stdout_lines), rc, elapsed


def read_file(path):
    """Read a file, return empty string if missing."""
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return ""


def tail_file(path, label, n=8):
    """Return a printable summary of the last n non-empty lines of a file."""
    content = read_file(path)
    if not content.strip():
        return f"  ({label} is empty or missing)"
    lines = [l for l in content.splitlines() if l.strip()][-n:]
    return "\n".join(f"    {l}" for l in lines)


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

PM_PLAN_PROMPT = """\
Today is {date} {time}.
You are a senior software architect and project manager working in a git worktree.
Branch: {branch}

Your ONLY job this session is to produce PLAN.md — a design document for one BDD scenario.
You do NOT write any source or test code. You do NOT run tests. You do NOT commit anything.

=== YOUR SCENARIO ===

{scenario_text}

=== YOUR TASK ===

Read BDD.md to understand the full system context, then use the write_file tool
to create PLAN.md in the current directory. Writing PLAN.md is the ONLY output
you produce — do not describe the plan in text, do not use any other tool.

PLAN.md must contain these six sections (in order):

## 0. Commands

Read BDD.md frontmatter (the YAML block at the top) and copy the exact shell
commands the SE and Tester must use. This section is mandatory — it prevents
every downstream agent from having to re-derive these themselves.

  build_cmd: <exact value from BDD.md frontmatter>
  test_cmd:  <exact value from BDD.md frontmatter>
  lint_cmd:  <exact value from BDD.md frontmatter, or "none" if absent>
  coverage_check: python3 scripts/check_bdd_coverage.py BDD.md

The SE and Tester will copy these commands verbatim. Do not paraphrase.

## 1. Units

Design using Hexagonal Architecture (Ports and Adapters). Classify every unit as
one of three roles — this determines where it lives and what it may import:

  PORT — an abstract interface (Python Protocol or ABC) that the domain calls.
    - Lives in src/ports/<name>.py
    - Contains only abstract method signatures, no logic
    - Example: a FileReader Protocol with a `read(path) -> str` method

  ADAPTER — a concrete class that implements a port for one specific technology.
    - Lives in src/adapters/<technology>/<name>.py
    - Imports the port it implements plus whatever library it needs (os, subprocess, etc.)
    - Never imported by domain or application code — wired up at the entry point only

  DOMAIN/APPLICATION — pure logic; the heart of the feature.
    - Lives in src/ or scripts/ as appropriate
    - Imports only ports, never adapters or external libraries directly
    - All external dependencies arrive via injected port parameters

For each unit list:
  - Role (PORT / ADAPTER / DOMAIN)
  - Name and exact signature (the SE will copy this verbatim — be precise)
  - File it lives in
  - One-sentence description
  - Dependency injection point: any external dependency (filesystem, subprocess,
    clock, network, random) MUST be a port parameter with a sensible default
    adapter, not a raw library call. This is mandatory — it is what makes the
    unit testable in isolation.

If the scenario is simple enough that a port/adapter split would be over-engineering
(e.g. a pure data-transformation function with no I/O), note this explicitly and
omit the port layer — but justify the decision.

## 2. Test strategy

  - Test file path (existing tests/test_*.py file or a new one)
  - Exact test function name (snake_case)
  - BDD marker (exact string — this line goes IMMEDIATELY above the def):
        # BDD: {scenario_name}
  - What the test injects (which DI parameters it uses to isolate the unit)
  - What it asserts

## 3. Acceptance criteria

  - [ ] BDD marker present on line immediately above test function, exact match
  - [ ] Test fails before implementation (red)
  - [ ] Test passes after implementation (green)
  - [ ] Full test suite still passes
  - [ ] `python3 scripts/check_bdd_coverage.py BDD.md` shows [x] for this scenario

## 4. Out of scope

List anything you decided NOT to build and why (prevents SE scope creep).

## 5. Files to delete (optional)

If and ONLY if this scenario explicitly requires removing an existing file, list
each file path here, one per line, with a one-sentence justification. Leave this
section empty (or omit the list) if no deletions are needed. The merge guard reads
this section — any file the SE deletes that is NOT listed here will cause the work
to be thrown away.

Example (only include if deletions are actually needed):
  - scripts/old_helper.py — superseded by the new unified loader in this scenario

Use write_file to write PLAN.md now. That is your only action after reading BDD.md.
Do not write any source code, test code, or other files. Do not commit.
"""

SE_IMPLEMENT_PROMPT = """\
Today is {date} {time}.
You are a software engineer working in a git worktree.
Branch: {branch}

Your ONLY job is to implement the design in PLAN.md exactly as written.
Read PLAN.md now before doing anything else.

{retry_section}
=== CONSTRAINTS (absolute — no exceptions) ===

- Do NOT run any git command (no git add, git commit, git checkout, git status)
- Do NOT modify BDD.md, PLAN.md, IDENTITY.md, QA_REPORT.md, RETRY_NOTES.md
- Do NOT modify ANY existing file in scripts/ — those are shared infrastructure.
  If PLAN.md says to add a function to an existing script, use edit_file to ADD
  the function only; never rewrite the whole file.
- Do NOT use sed, awk, or shell redirection to modify files — use edit_file only
- Do NOT deviate from the design in PLAN.md — implement exactly what it specifies
- If something in PLAN.md looks wrong, implement it as written anyway; the PM
  will update the plan if it needs changing

=== YOUR TASK ===

Follow this sequence exactly:

1. Read PLAN.md
2. Write the test first
   - Use the exact test file path, function name, and BDD marker from PLAN.md
   - The BDD marker line must be IMMEDIATELY above the def line — no blank line between:
       # BDD: {scenario_name}
       def test_...(...)
3. Verify the marker:
       grep -n "BDD: {scenario_name}" <test_file>
   If grep returns nothing — the marker is missing or wrong. Fix it before continuing.
4. Run the test — confirm it FAILS (expected at this point)
5. Implement all units from PLAN.md with the exact names and signatures specified
6. Run the full test suite using the exact test_cmd from PLAN.md § 0 (Commands).
   If anything fails — syntax errors, import errors, broken assertions — fix it and
   re-run. Repeat until the full suite passes or you have tried 3 times.
   The Tester will independently re-run the same suite; hand off clean work.
7. Stop. Do not commit. Do not write journal. The PM will review and commit.
"""

TESTER_PROMPT = """\
Today is {date} {time}.
You are a QA engineer working in a git worktree.
Branch: {branch}

Your job is to verify the SE's implementation against PLAN.md and write QA_REPORT.md.
You are READ-ONLY on all source and test files — do not modify them.

IMPORTANT: You MUST use write_file to create QA_REPORT.md. Do not just output the
report as text — the pipeline cannot read your stdout. Writing QA_REPORT.md is
mandatory; it is the only file you may write.

If any check FAILS, you must ALSO write FAIL_STACK_TRACE.md containing the full
raw output (stdout + stderr) from the failing command — no truncation. The SE
needs the complete stack trace to diagnose the problem.

{retry_context}

=== YOUR TASK ===

1. Read PLAN.md
2. Read the test file and implementation files it names
3. Run each check below
4. If any check fails, write FAIL_STACK_TRACE.md with the full raw output
5. Write QA_REPORT.md using the exact format below

=== CHECKS ===

A. Marker check
   grep -n "BDD: {scenario_name}" <test_file from PLAN.md>
   PASS if the marker is present on the line IMMEDIATELY above the test function def.
   FAIL if absent, wrong string, or not directly above the def.

B. Regression test run (full suite)
   Use the exact test_cmd from PLAN.md § 0 (Commands). Run every test in the
   project — not just the scenario under review — to confirm no regressions.
   Capture the complete stdout + stderr.
   PASS if exit code is 0. FAIL otherwise.
   On FAIL: write the full captured output to FAIL_STACK_TRACE.md (every line,
   including collection errors, tracebacks, and the final summary).

C. Coverage check
   python3 scripts/check_bdd_coverage.py BDD.md 2>&1 | grep "{scenario_name}"
   PASS if the line shows [x].
   FAIL if it shows UNCOVERED or is absent.

D. Design compliance
   For each unit in PLAN.md: confirm it exists with the correct name and signature.
   Confirm dependency injection points are parameters (not hardcoded).

=== QA_REPORT.md FORMAT (use exactly this) ===

# QA Report: {scenario_name}

## A. Marker check
Status: PASS / FAIL
Detail: <paste the grep output, or "not found">

## B. Test run
Status: PASS / FAIL
Exit code: <n>
Detail: <one-line summary — e.g. "all passed" or "5 failed, 2 errors — see FAIL_STACK_TRACE.md">

## C. Coverage check
Status: PASS / FAIL
Detail: <the coverage checker line for this scenario>

## D. Design compliance
Status: PASS / FAIL
Detail: <deviations from PLAN.md, or "all units present as specified">

## Overall
PASS — all checks passed
FAIL — <comma-separated list of failed checks, e.g. "A, C">
"""

PM_ACCEPT_PROMPT = """\
Today is {date} {time}.
You are the project manager. You wrote the design (PLAN.md) and now must decide
whether the SE's implementation meets the standard.

Branch: {branch}

=== YOUR TASK ===

1. Read PLAN.md
2. Read QA_REPORT.md
3. Make a decision and act on it (see below)

=== ACCEPT CRITERIA ===

ACCEPT when ALL of these hold:
  - Check A (marker) is PASS
  - Check B (test run) is PASS — all tests must pass; failing tests are a hard blocker
  - Check C (coverage) is PASS
  - Check D (design compliance) is PASS

REJECT if ANY of A, B, C, or D is FAIL.

=== IF YOU ACCEPT ===

Commit the implementation (exclude management files):
  git add -A -- ':!BDD_STATUS.md' ':!JOURNAL.md' ':!JOURNAL_INDEX.md' \\
                ':!PLAN.md' ':!QA_REPORT.md' ':!RETRY_NOTES.md'
  git commit -m "{date} {time}: implement {scenario_name}"

Write JOURNAL_ENTRY.md:
  ## {date} {time} — {scenario_name}
  [2-4 sentences: what the PM designed, what the SE built, what the tester confirmed]

Commit the journal:
  git add JOURNAL_ENTRY.md
  git commit -m "{date} {time}: journal entry"

Output this exact line last:
  PM_DECISION: ACCEPT

=== IF YOU REJECT ===

1. Read FAIL_STACK_TRACE.md if it exists — this contains the full test output and
   stack traces from the Tester's run. Use it to give the SE precise guidance.

2. Write RETRY_NOTES.md. Be surgical — quote the exact wrong string and exact
   correct string for every issue. Never write vague guidance like "fix the marker".
   Show the SE precisely what to change.
   For each failure that has a stack trace, end the note with:
     "Full stack trace: see FAIL_STACK_TRACE.md"

Output this exact line last:
  PM_DECISION: REJECT
"""


# ---------------------------------------------------------------------------
# Scenario text extraction
# ---------------------------------------------------------------------------

def extract_scenario_block(bdd_content, scenario_name):
    """
    Extract the scenario block from BDD.md content for the named scenario.
    Returns the Scenario line + its Given/When/Then/And/But lines.
    Falls back to a bare Scenario: line if not found (logs a warning).
    """
    lines = bdd_content.splitlines()
    in_scenario = False
    block = []
    scenario_lower = scenario_name.lower().strip()

    for line in lines:
        stripped = line.strip()
        if not in_scenario:
            m = re.match(r"Scenario(?:\s+Outline)?:\s*(.+)", stripped, re.IGNORECASE)
            if m and m.group(1).strip().lower() == scenario_lower:
                in_scenario = True
                block.append(line)
        else:
            # Stop at next Scenario/Feature boundary
            if stripped and re.match(r"(Scenario|Feature)[\s:]", stripped, re.IGNORECASE):
                break
            block.append(line)

    if block:
        return "\n".join(block).strip()

    # Fallback — warn so it's visible in logs
    print(
        f"  [pm_worker] WARN: could not find scenario block for '{scenario_name}' "
        f"in BDD.md — using bare scenario name",
        flush=True,
    )
    return f"Scenario: {scenario_name}"


# ---------------------------------------------------------------------------
# Programmatic QA report fallback
# ---------------------------------------------------------------------------

def generate_qa_report(scenario_name, wt_path):
    """
    Run the mechanical checks (A, B, C) directly and write QA_REPORT.md.
    Called when the Tester agent fails to produce the file itself.
    Check D (design compliance) is left as UNKNOWN — only the agent can read code.
    Returns the report content as a string.
    """
    lines = [f"# QA Report: {scenario_name}", "", "*(Generated programmatically — Tester agent did not write this file)*", ""]

    # A: Marker check
    marker_out, _, marker_rc = run_cmd(
        f'grep -rn "BDD: {scenario_name}" tests/ scripts/ src/ 2>/dev/null || true',
        cwd=wt_path, timeout=10,
    )
    marker_lines = [l for l in marker_out.splitlines() if l.strip()]
    # Must be immediately above a def line — check the line after each match
    marker_above_def = False
    if marker_lines:
        for hit in marker_lines:
            # hit format: "path:lineno:content"
            parts = hit.split(":", 2)
            if len(parts) >= 2:
                try:
                    filepath, lineno = parts[0], int(parts[1])
                    file_lines = read_file(os.path.join(wt_path, filepath)).splitlines()
                    # line numbers are 1-based; check the next line
                    if lineno < len(file_lines) and file_lines[lineno].strip().startswith("def "):
                        marker_above_def = True
                        break
                except (ValueError, IndexError):
                    pass
    a_status = "PASS" if marker_above_def else ("FOUND_BUT_MISPLACED" if marker_lines else "FAIL")
    lines += [
        "## A. Marker check",
        f"Status: {a_status}",
        f"Detail: {marker_lines[0] if marker_lines else 'not found'}",
        "",
    ]

    # B: Test run
    test_out, test_err, test_rc = run_cmd(
        "python3 -m pytest tests/ --tb=short -q 2>&1 || true",
        cwd=wt_path, timeout=120,
    )
    b_status = "PASS" if test_rc == 0 else "FAIL"
    # Grab the summary line (last non-empty line)
    test_summary = next((l for l in reversed(test_out.splitlines()) if l.strip()), "no output")
    lines += [
        "## B. Test run",
        f"Status: {b_status}",
        f"Exit code: {test_rc}",
        f"Detail: {test_summary}",
        "",
    ]

    # C: Coverage check
    cov_out, _, cov_rc = run_cmd(
        f'python3 scripts/check_bdd_coverage.py BDD.md 2>&1 | grep "{scenario_name}" || echo "scenario not found in output"',
        cwd=wt_path, timeout=30,
    )
    cov_line = cov_out.strip().splitlines()[0] if cov_out.strip() else "no output"
    c_status = "PASS" if "[x]" in cov_line else "FAIL"
    lines += [
        "## C. Coverage check",
        f"Status: {c_status}",
        f"Detail: {cov_line}",
        "",
    ]

    # D: Design compliance — cannot check programmatically
    lines += [
        "## D. Design compliance",
        "Status: UNKNOWN",
        "Detail: not checked (Tester agent did not run)",
        "",
    ]

    # Overall
    failed = [s for s in [a_status, b_status, c_status] if s != "PASS"]
    overall = "PASS — all checked items passed" if not failed else f"FAIL — {', '.join(['A' if a_status != 'PASS' else '', 'B' if b_status != 'PASS' else '', 'C' if c_status != 'PASS' else ''])}"
    lines += ["## Overall", overall.strip(", ")]

    content = "\n".join(lines)
    with open(os.path.join(wt_path, "QA_REPORT.md"), "w") as f:
        f.write(content)
    return content


# ---------------------------------------------------------------------------
# Stdout extraction fallback
# ---------------------------------------------------------------------------

def _extract_markdown_from_stdout(stdout):
    """
    If the PM agent printed the plan as text instead of writing the file,
    extract everything from the first markdown heading onward.
    Returns the extracted string, or empty string if nothing useful found.
    """
    lines = stdout.splitlines()
    start = None
    for i, line in enumerate(lines):
        # Look for the first top-level or second-level markdown heading
        if re.match(r"^#{1,2}\s+", line):
            start = i
            break
    if start is None:
        return ""
    return "\n".join(lines[start:]).strip()


# ---------------------------------------------------------------------------
# Failed pipeline tracker
# ---------------------------------------------------------------------------

def _record_failed_pipeline(scenario_name, wt_path, main_dir, log):
    """Append an entry to FAILED_PIPELINES.md in the main repo directory."""
    retry_path = os.path.join(wt_path, "RETRY_NOTES.md")
    retry_notes = read_file(retry_path).strip()
    if not retry_notes:
        retry_notes = "_No RETRY_NOTES.md found — PM did not record a reason._"

    date = time.strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n## {date} — {scenario_name}\n\n"
        f"{retry_notes}\n"
    )

    failed_path = os.path.join(main_dir, "FAILED_PIPELINES.md")
    if not os.path.exists(failed_path):
        header = "# Failed Pipelines\n\nScenarios that exhausted all retries without being accepted.\n"
        with open(failed_path, "w") as f:
            f.write(header)

    with open(failed_path, "a") as f:
        f.write(entry)

    log(f"Recorded failure in FAILED_PIPELINES.md")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pm_pipeline(scenario_name, scenario_text, wt_path, branch, main_dir, config):
    """
    Run the PM → SE → Tester → PM pipeline for one scenario.
    Returns a result dict with the same shape expected by orchestrate.py.
    """
    agent_config = config.get("agent", {})
    model = os.environ.get(
        "MODEL", agent_config.get("default_model", "claude-haiku-4-5-20251001")
    )
    provider = agent_config.get("provider")

    date = time.strftime("%Y-%m-%d")
    session_time = time.strftime("%H:%M")
    prefix = scenario_name[:35]
    start_time = time.time()
    all_stdout = []

    def log(msg):
        print(f"  [{prefix}] {msg}", flush=True)

    def elapsed():
        return f"{round(time.time() - start_time)}s"

    # -----------------------------------------------------------------------
    # Pipeline header
    # -----------------------------------------------------------------------
    log(f"{'='*60}")
    log(f"PIPELINE START")
    log(f"  scenario : {scenario_name}")
    log(f"  branch   : {branch}")
    log(f"  worktree : {wt_path}")
    log(f"  model    : {model}  provider: {provider or 'auto'}")
    log(f"  max retries: {MAX_RETRIES}")
    log(f"{'='*60}")

    # -----------------------------------------------------------------------
    # Phase 1: PM designs
    # -----------------------------------------------------------------------
    log(f"--- PHASE 1: PM PLAN ---")
    log(f"Scenario text injected ({len(scenario_text)} chars)")

    plan_prompt = PM_PLAN_PROMPT.format(
        date=date,
        time=session_time,
        branch=branch,
        scenario_name=scenario_name,
        scenario_text=scenario_text,
    )
    stdout, rc, phase_elapsed = run_agent(
        plan_prompt, wt_path, main_dir, provider, model,
        f"pm-plan-{scenario_name[:20]}", TIMEOUT_PM_PLAN,
        f"{prefix} PM-PLAN",
    )
    all_stdout.append(stdout)
    log(f"PM-PLAN done  rc={rc}  {phase_elapsed}s")

    plan_path = os.path.join(wt_path, "PLAN.md")
    if not os.path.exists(plan_path):
        # Fallback: the agent may have printed the plan to stdout instead of
        # using the write tool.  Extract everything after the first "# " heading.
        log("WARN: PM did not write PLAN.md — attempting stdout extraction")
        plan_content = _extract_markdown_from_stdout(stdout)
        if plan_content:
            with open(plan_path, "w") as f:
                f.write(plan_content)
            log(f"Extracted PLAN.md from stdout ({len(plan_content)} bytes)")
        else:
            log("ERROR: could not extract plan from stdout — aborting pipeline")
            return _result(scenario_name, branch, wt_path, 0, False, False,
                           start_time, 1, "\n".join(all_stdout))

    plan_size = os.path.getsize(plan_path)
    log(f"PLAN.md written ({plan_size} bytes)")
    log("PLAN.md tail:")
    print(tail_file(plan_path, "PLAN.md"), flush=True)

    # -----------------------------------------------------------------------
    # Phases 2-4: SE → Tester → PM accept loop
    # -----------------------------------------------------------------------
    accepted = False

    for attempt in range(1, MAX_RETRIES + 1):
        log(f"--- PHASE 2: SE IMPLEMENT  attempt {attempt}/{MAX_RETRIES} ---")

        # Build retry context if this is not the first attempt
        retry_section = ""
        retry_path = os.path.join(wt_path, "RETRY_NOTES.md")
        if attempt > 1 and os.path.exists(retry_path):
            stack_trace_path = os.path.join(wt_path, "FAIL_STACK_TRACE.md")
            stack_hint = (
                "\nThe full stack trace from the failing test run is in "
                "FAIL_STACK_TRACE.md — read it before making any changes.\n"
                if os.path.exists(stack_trace_path) else ""
            )
            retry_section = (
                "=== RETRY NOTES FROM PM ===\n\n"
                + read_file(retry_path)
                + stack_hint
                + "\n\nAddress every point above. Nothing else.\n"
            )
            log(f"RETRY_NOTES.md injected into SE prompt ({os.path.getsize(retry_path)} bytes):")
            print(tail_file(retry_path, "RETRY_NOTES.md"), flush=True)
            if os.path.exists(stack_trace_path):
                log(f"FAIL_STACK_TRACE.md present ({os.path.getsize(stack_trace_path)} bytes) — SE will be directed to read it")

        se_prompt = SE_IMPLEMENT_PROMPT.format(
            date=date,
            time=session_time,
            branch=branch,
            scenario_name=scenario_name,
            retry_section=retry_section,
        )
        stdout, rc, phase_elapsed = run_agent(
            se_prompt, wt_path, main_dir, provider, model,
            f"se-{attempt}-{scenario_name[:15]}", TIMEOUT_SE,
            f"{prefix} SE",
        )
        all_stdout.append(stdout)
        log(f"SE done  rc={rc}  {phase_elapsed}s  total={elapsed()}")

        # Hard guard: reject immediately if SE touched protected files
        violations = check_se_protected_files(wt_path)
        if violations:
            log(f"HARD REJECT: SE modified protected file(s): {violations}")
            log(f"Resetting and writing RETRY_NOTES before next attempt")
            run_cmd("git checkout -- . 2>&1", cwd=wt_path)
            retry_notes = (
                "# Retry Notes\n\n"
                "The SE modified files that are strictly off-limits:\n\n"
                + "".join(f"- `{v}`\n" for v in violations)
                + "\nDo NOT touch any file under `scripts/`, `.github/`, "
                "`IDENTITY.md`, `BDD.md`, or `conftest.py`.\n"
                "These are shared infrastructure — they must never be rewritten.\n"
                "Only create or edit files under `src/`, `tests/`, or `tools/`.\n"
            )
            with open(os.path.join(wt_path, "RETRY_NOTES.md"), "w") as f:
                f.write(retry_notes)
            continue

        # Quick marker pre-check so we can warn early without waiting for tester
        marker_out, _, _ = run_cmd(
            f'grep -rn "BDD: {scenario_name}" tests/ scripts/ src/ 2>/dev/null || true',
            cwd=wt_path, timeout=10,
        )
        if marker_out.strip():
            log(f"Marker pre-check: FOUND — {marker_out.strip().splitlines()[0]}")
        else:
            log(f"Marker pre-check: WARN — marker not found yet (tester will confirm)")

        log(f"--- PHASE 3: TESTER QA  attempt {attempt}/{MAX_RETRIES} ---")
        retry_context = ""
        if attempt > 1 and os.path.exists(retry_path):
            retry_context = (
                "=== PREVIOUS PM REJECTION NOTES ===\n\n"
                + read_file(retry_path)
                + "\n\nPay particular attention to the issues the PM flagged above "
                "when running your checks.\n"
            )
        tester_prompt = TESTER_PROMPT.format(
            date=date,
            time=session_time,
            branch=branch,
            scenario_name=scenario_name,
            retry_context=retry_context,
        )
        stdout, rc, phase_elapsed = run_agent(
            tester_prompt, wt_path, main_dir, provider, model,
            f"tester-{attempt}-{scenario_name[:12]}", TIMEOUT_TESTER,
            f"{prefix} TESTER",
        )
        all_stdout.append(stdout)
        log(f"Tester done  rc={rc}  {phase_elapsed}s  total={elapsed()}")

        qa_path = os.path.join(wt_path, "QA_REPORT.md")
        qa_content = read_file(qa_path).strip()
        if not qa_content:
            # Try stdout extraction first (agent may have printed instead of written)
            log("WARN: Tester did not write QA_REPORT.md — attempting stdout extraction")
            qa_extracted = _extract_markdown_from_stdout(stdout)
            if qa_extracted:
                with open(qa_path, "w") as f:
                    f.write(qa_extracted)
                qa_content = qa_extracted
                log(f"Extracted QA_REPORT.md from stdout ({len(qa_content)} bytes)")
            else:
                # Programmatic fallback: run the mechanical checks ourselves
                log("Stdout extraction failed — running checks programmatically")
                qa_content = generate_qa_report(scenario_name, wt_path)
                log(f"Generated QA_REPORT.md programmatically ({len(qa_content)} bytes)")
        else:
            log(f"QA_REPORT.md written ({os.path.getsize(qa_path)} bytes)")

        # Echo the Overall verdict line
        for line in qa_content.splitlines():
            stripped = line.strip()
            if stripped.startswith("PASS") or stripped.startswith("FAIL"):
                log(f"QA overall → {stripped}")
                break

        log(f"--- PHASE 4: PM ACCEPT  attempt {attempt}/{MAX_RETRIES} ---")
        accept_prompt = PM_ACCEPT_PROMPT.format(
            date=date,
            time=session_time,
            branch=branch,
            scenario_name=scenario_name,
        )
        stdout, rc, phase_elapsed = run_agent(
            accept_prompt, wt_path, main_dir, provider, model,
            f"pm-accept-{attempt}-{scenario_name[:10]}", TIMEOUT_PM_ACCEPT,
            f"{prefix} PM-ACCEPT",
        )
        all_stdout.append(stdout)
        log(f"PM-ACCEPT done  rc={rc}  {phase_elapsed}s  total={elapsed()}")

        # Detect PM decision from agent output
        decision = "UNKNOWN"
        for line in stdout.splitlines():
            if "PM_DECISION: ACCEPT" in line:
                decision = "ACCEPT"
                break
            if "PM_DECISION: REJECT" in line:
                decision = "REJECT"
                break

        log(f"PM decision: {decision}")

        if decision == "REJECT":
            retry_path = os.path.join(wt_path, "RETRY_NOTES.md")
            if os.path.exists(retry_path):
                log(f"RETRY_NOTES.md ({os.path.getsize(retry_path)} bytes):")
                print(tail_file(retry_path, "RETRY_NOTES.md", n=12), flush=True)
            else:
                log("WARN: PM rejected but did not write RETRY_NOTES.md")

        if decision == "ACCEPT":
            accepted = True
            break

        if attempt < MAX_RETRIES:
            log(f"Rejected — resetting SE work for retry {attempt + 1}")
            # Reset SE's file changes; preserve PLAN.md, QA_REPORT.md, RETRY_NOTES.md
            # (those are untracked so git clean handles them; git checkout resets tracked)
            reset_out, reset_err, reset_rc = run_cmd(
                "git checkout -- . 2>&1; "
                "git clean -fd -e PLAN.md -e QA_REPORT.md -e RETRY_NOTES.md -e FAIL_STACK_TRACE.md 2>&1",
                cwd=wt_path,
            )
            if reset_out.strip():
                log(f"git reset output: {reset_out.strip()[:200]}")
            if reset_rc != 0:
                log(f"WARN: git reset returned rc={reset_rc}")
        else:
            log(f"All {MAX_RETRIES} attempts exhausted — no commit")
            _record_failed_pipeline(scenario_name, wt_path, main_dir, log)

    # -----------------------------------------------------------------------
    # Final checks
    # -----------------------------------------------------------------------
    commits_out, _, _ = run_cmd(
        f'git log --oneline HEAD.."{branch}" 2>/dev/null | wc -l',
        cwd=main_dir, timeout=10,
    )
    commit_count = int(commits_out.strip()) if commits_out.strip().isdigit() else 0

    _, _, test_rc = run_cmd(
        'eval "$(python3 scripts/parse_bdd_config.py BDD.md)" && eval "$TEST_CMD"',
        cwd=wt_path, timeout=120,
    )
    tests_pass = test_rc == 0

    marker_grep, _, _ = run_cmd(
        f'grep -rn "BDD: {scenario_name}" tests/ scripts/ src/ 2>/dev/null || true',
        cwd=wt_path, timeout=10,
    )
    has_marker = bool(marker_grep.strip())

    # -----------------------------------------------------------------------
    # Pipeline summary
    # -----------------------------------------------------------------------
    log(f"{'='*60}")
    log(f"PIPELINE COMPLETE")
    log(f"  accepted   : {accepted}")
    log(f"  commits    : {commit_count}")
    log(f"  tests pass : {tests_pass} (rc={test_rc})")
    log(f"  has marker : {has_marker}")
    if marker_grep.strip():
        log(f"  marker at  : {marker_grep.strip().splitlines()[0]}")
    log(f"  total time : {elapsed()}")
    log(f"{'='*60}")

    return _result(
        scenario_name, branch, wt_path,
        commit_count, tests_pass, has_marker,
        start_time, 0 if accepted else 1,
        "\n".join(all_stdout),
    )


def _result(scenario, branch, wt_path, commits, tests_pass, has_marker,
            start_time, rc, stdout):
    return {
        "scenario": scenario,
        "branch": branch,
        "wt_path": wt_path,
        "commits": commits,
        "tests_pass": tests_pass,
        "has_marker": has_marker,
        "elapsed_s": round(time.time() - start_time),
        "rc": rc,
        "stdout": stdout[:2000],
    }
