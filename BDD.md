---
language: python
framework: none
build_cmd: python3 -m py_compile scripts/*.py && echo "Build OK"
test_cmd: python3 -m pytest tests/ -q --tb=short --no-header 2>/dev/null || python3 tests/run_tests.py
lint_cmd: python3 -m ruff check scripts/ tests/ --fix || echo "lint skipped"
fmt_cmd: python3 -m ruff format scripts/ tests/ || echo "format skipped"
birth_date: 2026-03-05
---

You must only write code and tests that meet the features and scenarios of this behaviour driven development document.

System: BAADD (Behaviour and AI Driven Development) — a framework where an AI agent builds and maintains a project driven entirely by BDD specifications. The agent reads BDD.md, implements uncovered scenarios one by one, and maintains 100% test coverage.

    Feature: BDD Specification Parser
        As a framework developer
        I want to parse BDD.md frontmatter and scenarios
        So that the agent knows what to build and how

        Scenario: Parse YAML frontmatter from BDD.md
            Given a BDD.md file with YAML frontmatter containing language, framework, build_cmd, test_cmd
            When parse_bdd_config.py is run on the file
            Then it outputs shell variables LANGUAGE, FRAMEWORK, BUILD_CMD, TEST_CMD with correct values

        Scenario: Handle missing frontmatter gracefully
            Given a BDD.md file without YAML frontmatter
            When parse_bdd_config.py is run on the file
            Then it outputs default values for all configuration keys

        Scenario: Parse frontmatter with quoted values
            Given a BDD.md file with frontmatter containing quoted strings like build_cmd: "npm run build"
            When parse_bdd_config.py is run
            Then the shell variable BUILD_CMD contains the unquoted value "npm run build"

        Scenario: Extract all scenarios from BDD.md
            Given a BDD.md file with multiple Features and Scenarios
            When check_bdd_coverage.py parses the file
            Then it returns all scenario names in order of appearance

        Scenario: Parse scenario outline syntax
            Given a BDD.md file containing "Scenario Outline: Login with <role>"
            When check_bdd_coverage.py parses the file
            Then it treats "Scenario Outline" the same as "Scenario" and extracts the name

        Scenario: Skip frontmatter when parsing scenarios
            Given a BDD.md file with 10 lines of YAML frontmatter
            When check_bdd_coverage.py parses scenarios
            Then it does not include frontmatter lines as scenarios

    Feature: Test Coverage Detection
        As a framework developer
        I want to detect which BDD scenarios have test coverage
        So that the agent knows what to implement next

        Scenario: Find test files in project
            Given a project with test files in tests/, src/, and nested directories
            When find_test_files() is called
            Then it returns all test files matching patterns like *test*.py, test_*.py, *_test.py

        Scenario: Exclude non-source directories from test search
            Given a project with test files in .git, node_modules, target, __pycache__
            When find_test_files() is called
            Then it excludes files in those directories from the result

        Scenario: Detect coverage via BDD marker comment
            Given a test file containing "# BDD: Login with valid credentials" above a test function
            When check_coverage() checks for "Login with valid credentials"
            Then it returns True (covered)

        Scenario: Detect coverage via marker with different comment style
            Given a JavaScript test file containing "// BDD: Submit form successfully" above a test
            When check_coverage() checks for "Submit form successfully"
            Then it returns True (covered)

        Scenario: Detect coverage via heuristic name matching
            Given a test file with function "test_login_with_valid_credentials"
            When check_coverage() checks for scenario "Login with valid credentials"
            Then it returns True via heuristic substring matching

        Scenario: Detect coverage via partial name matching
            Given a test named "test_leave_comment_name_missing"
            When check_coverage() checks for "Leave a comment with name field not filled in"
            Then it returns True via partial word matching

        Scenario: Report uncovered scenarios
            Given BDD.md with 5 scenarios and only 2 having test coverage
            When check_bdd_coverage.py runs
            Then it outputs 3 scenarios marked as UNCOVERED with [ ] checkbox

        Scenario: Exit with error code when scenarios uncovered
            Given BDD.md with scenarios lacking test coverage
            When check_bdd_coverage.py completes
            Then it exits with code 1

        Scenario: Exit with success when all scenarios covered
            Given BDD.md with all scenarios having test coverage
            When check_bdd_coverage.py completes
            Then it exits with code 0

        Scenario: Handle empty BDD.md with no scenarios
            Given BDD.md with frontmatter but no Feature or Scenario sections
            When check_bdd_coverage.py parses the file
            Then it outputs "No scenarios found in BDD.md" and exits with code 0

        Scenario: Handle BDD.md with only frontmatter
            Given BDD.md containing only YAML frontmatter enclosed in ---
            When check_bdd_coverage.py parses scenarios
            Then it finds zero scenarios and outputs "No scenarios found"

    Feature: Multi-Provider AI Agent
        As a framework developer
        I want the agent to support multiple LLM providers
        So that users can choose their preferred AI backend

        Scenario: Detect Anthropic provider from API key
            Given ANTHROPIC_API_KEY environment variable is set
            When detect_provider() is called
            Then it returns "anthropic"

        Scenario: Detect OpenAI provider from API key
            Given OPENAI_API_KEY is set and no ANTHROPIC_API_KEY
            When detect_provider() is called
            Then it returns "openai"

        Scenario: Detect Groq provider from API key
            Given GROQ_API_KEY is set and no higher-priority keys
            When detect_provider() is called
            Then it returns "groq"

        Scenario: Detect Ollama provider from localhost probe
            Given Ollama running on localhost:11434 and no API keys set
            When detect_provider() is called
            Then it returns "ollama"

        Scenario: Detect custom provider from base URL
            Given CUSTOM_BASE_URL set to a custom endpoint
            When detect_provider() is called
            Then it returns "custom"

        Scenario: Provider priority order
            Given ANTHROPIC_API_KEY and OPENAI_API_KEY both set
            When detect_provider() is called
            Then it returns "anthropic" (highest priority)

        Scenario: Use provider default model
            Given Anthropic provider detected with no MODEL override
            When agent.py resolves the model
            Then it uses default model "claude-haiku-4-5-20251001"

        Scenario: Override model via MODEL environment variable
            Given MODEL=gpt-4 environment variable
            When agent.py runs
            Then it uses gpt-4 regardless of provider defaults

        Scenario: Load provider config from poppins.yml
            Given poppins.yml with provider: "openai" and base_url: "https://custom.api/v1"
            When agent.py starts
            Then it applies those settings as environment defaults

        Scenario: Environment variables override poppins.yml config
            Given poppins.yml with provider: "openai" and ANTHROPIC_API_KEY environment variable
            When agent.py detects provider
            Then it uses "anthropic" from environment (env takes priority)

        Scenario: Set OLLAMA_HOST from poppins.yml base_url
            Given poppins.yml with provider: "ollama" and base_url: "http://localhost:11434/v1"
            When agent.py applies poppins provider config
            Then OLLAMA_HOST is set to "http://localhost:11434" (strips /v1 suffix)

        Scenario: No provider detected error message
            Given no API keys set, no CUSTOM_BASE_URL, and Ollama not running
            When agent.py tries to detect provider
            Then it prints error listing all supported provider env vars and exits with code 1

        Scenario: CUSTOM_MODEL required for custom provider without --model
            Given CUSTOM_BASE_URL set, CUSTOM_API_KEY set, provider=custom, but no CUSTOM_MODEL
            When agent.py tries to resolve model without --model flag
            Then it prints "ERROR: CUSTOM_MODEL not set" and exits with code 1

        Scenario: Unknown provider error
            Given --provider=invalid_provider flag passed
            When agent.py checks provider against PROVIDER_CONFIGS
            Then it prints "ERROR: Unknown provider" and exits with code 1

        Scenario: Override provider via --provider flag
            Given ANTHROPIC_API_KEY set and --provider=openai flag
            When agent.py resolves provider
            Then it uses "openai" from CLI flag (flag takes priority over env)

        Scenario: Missing anthropic package error
            Given anthropic provider detected and anthropic package not installed
            When agent.py tries to import anthropic
            Then it prints "ERROR: anthropic package not installed" and exits with code 1

        Scenario: Missing openai package error
            Given openai provider detected and openai package not installed
            When agent.py tries to import openai for OpenAI-compatible client
            Then it prints "ERROR: openai package not installed" and exits with code 1

        Scenario: Empty stdin prompt error
            Given agent.py started with empty stdin
            When agent.py reads prompt
            Then it prints "ERROR: no prompt provided on stdin" and exits with code 1

        Scenario: Load skills from SKILL.md files
            Given skills/ directory containing multiple SKILL.md files
            When load_skills() reads the directory
            Then it returns concatenated content separated by "---" markers

        Scenario: Skills appended to system prompt
            Given skills_text loaded from skills directory
            When system_prompt is constructed
            Then skills_text is appended after the TDD rules

        Scenario: Skip skills loading if directory missing
            Given --skills=./nonexistent passed
            When load_skills() runs
            Then it returns empty string (no skills loaded)

        Scenario: Custom event log path via --event-log
            Given --event-log=/custom/path/events.jsonl flag
            When agent.py starts
            Then EventLogger writes to /custom/path/events.jsonl instead of default

    Feature: Agent Tool Execution
        As an AI agent
        I want to execute tools to read files, run commands, and write code
        So that I can implement BDD scenarios

        Scenario: Run bash command and capture output
            Given run_tool("bash", {"command": "echo hello"})
            When the tool executes
            Then it returns "hello\n" as output

        Scenario: Run bash command with stderr
            Given run_tool("bash", {"command": "ls /nonexistent"})
            When the tool executes
            Then it includes stderr in the output

        Scenario: Bash command timeout after 300 seconds
            Given a bash command that runs longer than 300 seconds
            When the tool executes
            Then it returns "ERROR: command timed out after 300s"

        Scenario: Read file that exists
            Given run_tool("read_file", {"path": "/tmp/test.txt"}) with file containing "content"
            When the tool executes
            Then it returns the file contents

        Scenario: Read file that does not exist
            Given run_tool("read_file", {"path": "/nonexistent/file.txt"})
            When the tool executes
            Then it returns "ERROR: file not found: /nonexistent/file.txt"

        Scenario: Truncate long file output
            Given a file with 20,000 characters
            When read_file tool reads it with TOOL_OUTPUT_LIMIT=12000
            Then it truncates at 12000 chars and appends "[... truncated]" message

        Scenario: Write file creates parent directories
            Given run_tool("write_file", {"path": "/tmp/newdir/file.txt", "content": "text"})
            When the tool executes
            Then it creates /tmp/newdir/ if needed and writes the file

        Scenario: Edit file replaces exact string
            Given a file containing "old text here"
            When edit_file tool replaces "old text" with "new text"
            Then the file contains "new text here"

        Scenario: Edit file fails when string not found
            Given a file containing "some content"
            When edit_file tool tries to replace "missing string"
            Then it returns "ERROR: string not found"

        Scenario: Edit file replaces only first occurrence
            Given a file containing "foo foo foo"
            When edit_file tool replaces "foo" with "bar" with replaceAll=false
            Then the file contains "bar foo foo"

        Scenario: List files excludes git and node_modules
            Given list_files tool run on a project with .git and node_modules
            When the tool executes
            Then it excludes .git/* and node_modules/* from results

        Scenario: Search files finds pattern
            Given search_files tool searching for "def authenticate"
            When the tool executes
            Then it returns file paths and matching lines

        Scenario: Search files handles no matches
            Given search_files tool searching for "nonexistent_pattern_xyz"
            When the tool executes
            Then it returns "No files found containing: nonexistent_pattern_xyz"

    Feature: Agent Loop and Iteration Management
        As a framework developer
        I want the agent loop to have iteration limits
        So that sessions don't run indefinitely

        Scenario: Agent stops at max iterations
            Given MAX_ITERATIONS=75 and agent reaches iteration 75
            When the loop completes
            Then it prints "[BAADD agent: hit iteration limit (75)]"

        Scenario: Wrap-up reminder injected at threshold
            Given WRAP_UP_AT=70 and iteration reaches 70
            When the agent continues
            Then a wrap-up reminder message is injected into messages

        Scenario: Wrap-up reminder content for evolve mode
            Given wrap_up_at threshold reached in evolve mode
            When wrap-up message is generated
            Then it instructs agent to update BDD_STATUS.md, write journal, and commit

        Scenario: Wrap-up reminder content for bootstrap mode
            Given wrap_up_at threshold reached in bootstrap mode
            When wrap-up message is generated
            Then it instructs agent to create .baadd_initialized and Day 0 journal

        Scenario: Session ends on end_turn stop reason
            Given Anthropic API returns stop_reason="end_turn"
            When the agent loop processes the response
            Then it exits the loop and prints "[BAADD agent done — N iterations]"

    Feature: Context Window Management
        As a framework developer
        I want to trim old tool results when context exceeds limit
        So that the agent doesn't hit context window limits

        Scenario: Estimate tokens from text
            Given text with 4000 characters
            When estimate_tokens() calculates
            Then it returns approximately 1000 tokens (4 chars per token)

        Scenario: Trim context when exceeding limit
            Given messages with estimated 150,000 tokens and CONTEXT_WINDOW_LIMIT=100,000
            When trim_context() is called
            Then it truncates old tool result content to 200 chars with summary

        Scenario: Preserve recent messages during trim
            Given messages array with 50 entries
            When trim_context() trims to fit limit
            Then the last 12 messages (6 exchanges) remain untouched

        Scenario: Trim only tool result content
            Given messages with text blocks and tool_result blocks
            When trim_context() operates
            Then it only truncates tool_result content, not user/assistant text

    Feature: Event Logging
        As a framework developer
        I want structured event logs for observability
        So that I can analyze agent sessions

        Scenario: Log session start with provider and model
            Given agent session starting with provider=anthropic model=claude-haiku
            When EventLogger.session_start() is called
            Then it writes JSON with event="session_start", provider, model to agent_events.jsonl

        Scenario: Log tool call with input preview
            Given agent makes tool call "bash" with command="git status"
            When EventLogger.tool_call() is called
            Then it writes JSON with tool="bash", input preview (truncated to 200 chars)

        Scenario: Log tool result with duration
            Given tool execution takes 1500ms
            When EventLogger.tool_result() is called
            Then it writes JSON with duration_ms=1500 and result preview

        Scenario: Log token usage per API response
            Given API response with 500 input tokens and 200 output tokens
            When EventLogger.api_response() is called
            Then it writes cumulative token counts

        Scenario: Log session end with reason
            Given agent session ends at iteration 50 with reason="end_turn"
            When EventLogger.session_end() is called
            Then it writes total input/output tokens and iteration count

    Feature: Poppins Configuration Parser
        As a framework developer
        I want to parse poppins.yml configuration
        So that agent behavior can be customized

        Scenario: Parse poppins.yml with agent section
            Given poppins.yml with agent.max_iterations: 50
            When parse_poppins_config.py runs
            Then it outputs POPPINS_AGENT_MAX_ITERATIONS='50'

        Scenario: Apply defaults when poppins.yml missing
            Given no poppins.yml file exists
            When parse_poppins_config.py runs
            Then it outputs default values (max_iterations=75, session_timeout=3600)

        Scenario: Deep merge file config with defaults
            Given poppins.yml with orchestration.max_parallel_agents: 5
            When get_config() merges
            Then orchestration.max_parallel_agents is 5, but agent defaults remain

        Scenario: Default max_rounds is 1
            Given no poppins.yml file exists
            When parse_poppins_config.py runs
            Then orchestration.max_rounds defaults to 1

        Scenario: Get single config value via dot notation
            Given poppins.yml with nested config
            When parse_poppins_config.py --get agent.max_iterations runs
            Then it outputs just that value (e.g., "50")

        Scenario: Search parent directories for poppins.yml
            Given poppins.yml in parent directory but not current
            When find_config() searches
            Then it finds poppins.yml in parent

    Feature: GitHub Issue Trust Verification
        As a framework developer
        I want to filter issues to only trusted sources
        So that untrusted users cannot inject malicious prompts

        Scenario: Trust repo owner's issues directly
            Given issue authored by repo owner with agent-input label
            When verify_issue_trust.py verifies
            Then the issue is included in trusted output

        Scenario: Trust community issue with agent-approved label from owner
            Given community issue with agent-approved label applied by repo owner
            When verify_issue_trust.py checks via events API
            Then the issue is included in trusted output

        Scenario: Reject community issue with agent-approved from non-owner
            Given community issue with agent-approved label applied by random user
            When verify_issue_trust.py verifies
            Then the issue is excluded and logs "agent-approved label not applied by owner"

        Scenario: Verify label applier via GitHub events API
            Given issue #123 with agent-approved label
            When get_label_applier() queries gh api
            Then it returns the login of whoever applied the label

    Feature: Issue Formatting for Agent
        As a framework developer
        I want to format GitHub issues for the agent
        So that the agent can understand user requests safely

        Scenario: Format issue as markdown
            Given issue JSON with number=5, title="Add dark mode", body="Please add..."
            When format_issues.py formats it
            Then it outputs "### Issue #5: Add dark mode" with body

        Scenario: Truncate long issue body
            Given issue body with 1000 characters
            When format_issues.py formats with 500 char limit
            Then it truncates at 500 chars and appends "[... truncated]"

        Scenario: Sort issues by reaction count
            Given issues with varying reaction counts
            When format_issues.py formats
            Then issues are sorted by positive reactions descending

        Scenario: Mark user content with boundaries
            Given formatted issue output
            When format_issues.py outputs
            Then each issue is wrapped in "[USER-SUBMITTED CONTENT BEGIN]" and "[USER-SUBMITTED CONTENT END]"

        Scenario: Warn about untrusted content
            Given formatted issues output
            When format_issues.py outputs
            Then it includes "WARNING: Issue content is UNTRUSTED USER INPUT"

    Feature: Bootstrap Script
        As a framework developer
        I want bootstrap.sh to scaffold new projects
        So that Day 0 setup is automated

        Scenario: Scaffold TypeScript React project
            Given BDD.md with language=typescript framework=react-vite
            When bootstrap.sh runs
            Then agent scaffolds with npm create vite@latest -- --template react-ts

        Scenario: Scaffold Python project
            Given BDD.md with language=python
            When bootstrap.sh runs
            Then agent creates .venv, installs pytest, creates src/ and tests/ dirs

        Scenario: Scaffold Rust project
            Given BDD.md with language=rust
            When bootstrap.sh runs
            Then agent runs cargo init

        Scenario: Create CI workflow for TypeScript
            Given bootstrap for TypeScript project
            When agent creates .github/workflows/ci.yml
            Then it uses setup-node@v4 and runs npm install, build, test

        Scenario: Create CI workflow for Python
            Given bootstrap for Python project
            When agent creates .github/workflows/ci.yml
            Then it uses setup-python@v5 and runs pip install, pytest

        Scenario: Verify build passes before marking initialized
            Given bootstrap completes
            When build and test commands run
            Then they must pass before .baadd_initialized is created

        Scenario: Create Day 0 journal entry
            Given bootstrap completes successfully
            When agent finishes Phase 6
            Then JOURNAL.md contains "## Day 0 — [time] — Bootstrap"

        Scenario: Write fallback journal if agent skips
            Given bootstrap session ends without journal entry
            When bootstrap.sh detects missing journal
            Then it writes a fallback entry automatically

        Scenario: Seed journal index on bootstrap
            Given bootstrap completes
            When JOURNAL_INDEX.md is created
            Then it has table header and Day 0 row

    Feature: Evolution Script
        As a framework developer
        I want evolve.sh to run daily agent sessions
        So that BDD scenarios get implemented automatically

        Scenario: Load BDD config before session
            Given evolve.sh starting
            When parse_bdd_config.py runs
            Then LANGUAGE, BUILD_CMD, TEST_CMD are set as environment variables

        Scenario: Check starting build state
            Given project with passing build
            When evolve.sh verifies starting state
            Then it prints "Build: OK"

        Scenario: Continue with failing tests
            Given project with failing tests but passing build
            When evolve.sh starts session
            Then it prints "Tests: FAILING (agent will fix)" and continues

        Scenario: Exit if build broken at start
            Given project with broken build
            When evolve.sh verifies starting state
            Then it exits immediately without running agent

        Scenario: Fetch trusted GitHub issues
            Given gh CLI available and repo owner set
            When evolve.sh fetches issues
            Then it queries agent-input (owner) and agent-approved labels

        Scenario: Generate issues file for agent
            Given issues found from GitHub
            When evolve.sh creates ISSUES_TODAY.md
            Then agent can read it during session

        Scenario: Pre-compute coverage before session
            Given BDD.md with 10 scenarios, 7 covered
            When evolve.sh runs coverage check
            Then it captures uncovered scenario names for agent targeting

        Scenario: Detect test-only anti-pattern
            Given agent wrote test files but no implementation, tests failing
            When evolve.sh checks new files
            Then it detects the pattern and prompts agent to implement

        Scenario: Retry fix on build failure
            Given agent commits break the build
            When post-session verification fails
            Then evolve.sh runs up to 3 fix attempts

        Scenario: Revert session on persistent failure
            Given build fails after 3 fix attempts
            When evolve.sh cannot recover
            Then it reverts to session start SHA

        Scenario: Write journal if agent skipped
            Given agent session ends without journal entry
            When evolve.sh detects missing journal
            Then it prompts agent to write one

        Scenario: Write fallback journal if agent still skips
            Given agent fails to write journal after prompt
            When evolve.sh generates fallback
            Then JOURNAL.md gets an auto-generated entry

        Scenario: Update journal index after session
            Given session completes with coverage 5/10
            When evolve.sh updates JOURNAL_INDEX.md
            Then new row has date, time, coverage, and commit summary

        Scenario: Comment and close implemented issues
            Given ISSUE_RESPONSE.md with issue_number=5 status=fixed
            When evolve.sh processes responses
            Then it comments on GitHub issue and closes it

        Scenario: Push changes after session
            Given session completes successfully
            When final verification passes
            Then evolve.sh pushes to remote

        Scenario: Track session start SHA for rollback
            Given evolve.sh starting session
            When SESSION_START_SHA is captured via git rev-parse HEAD
            Then it is used for revert on failure and commit counting

        Scenario: Exclude management files from worktree commits
            Given agent in worktree commits code and tests
            When git add excludes certain files with ':!' pattern
            Then BDD_STATUS.md, JOURNAL.md, JOURNAL_INDEX.md are not committed

        Scenario: Branch naming convention with timestamp
            Given agent claims scenario "Login with valid credentials"
            When worktree branch is created
            Then branch name is "agent/login-with-valid-credentials-YYYYMMDD-HHMMSS"

        Scenario: Calculate has_work flag
            Given coverage 5/10 and 2 open issues
            When evolve.sh calculates has_work
            Then has_work="yes" because covered < total OR issues > 0

        Scenario: Guard warning for minimal work with uncovered scenarios
            Given agent made 2 commits and 5 scenarios remain uncovered
            When evolve.sh checks commits vs coverage
            Then it prints warning about agent possibly skipping implementation

        Scenario: Handle push failure gracefully
            Given git push fails due to auth or network
            When evolve.sh tries to push
            Then it prints "Push failed (check remote/auth)" but session still completes

        Scenario: Handle missing git remote
            Given git repo with no remote origin configured
            When evolve.sh tries to get REPO
            Then it falls back to "unknown/repo"

    Feature: Scenario Locking for Parallel Execution
        As a framework developer
        I want scenario locks to prevent race conditions
        So that multiple agents can run concurrently

        Scenario: Generate scenario slug from name
            Given scenario "Login with valid credentials"
            When scenario_to_slug() processes it
            Then it returns "login-with-valid-credentials" (lowercase, alphanumeric only)

        Scenario: Slug truncates to 60 characters
            Given scenario with very long name (100 chars)
            When scenario_to_slug() processes
            Then slug is max 60 chars

        Scenario: Check for existing lock file
            Given locks/login-with-valid-credentials.lock exists
            When agent tries to claim that scenario
            Then it skips to next uncovered scenario

        Scenario: Detect stale lock from dead PID
            Given lock file with PID=12345 and PID 12345 is dead
            When agent checks lock age
            Then it removes stale lock and claims scenario

        Scenario: Write lock file with session metadata
            Given agent claims scenario
            When lock is written
            Then it contains PID, HOST, DATE, TIME, SCENARIO, BRANCH

        Scenario: Release lock on completion
            Given agent completes scenario implementation
            When session ends
            Then locks/<slug>.lock is deleted

        Scenario: Clean up lock on early exit
            Given agent crashes or exits early
            When trap cleanup_worktree fires
            Then lock file is removed

    Feature: Git Worktree Isolation
        As a framework developer
        I want each agent to work in isolated git worktrees
        So that parallel agents don't conflict

        Scenario: Create worktree for scenario
            Given agent needs to implement scenario
            When evolve.sh creates worktree
            Then git worktree add creates isolated directory with new branch

        Scenario: Copy runtime files to worktree
            Given ISSUES_TODAY.md in main directory
            When worktree is created
            Then ISSUES_TODAY.md is copied to worktree

        Scenario: Merge successful worktree to main
            Given worktree branch with passing tests
            When merge happens
            Then git merge --no-ff integrates changes

        Scenario: Auto-resolve management file conflicts
            Given merge conflict in BDD_STATUS.md or JOURNAL_INDEX.md
            When evolve.sh resolves
            Then it prefers main's version (--ours)

        Scenario: Fold JOURNAL_ENTRY.md into JOURNAL.md
            Given JOURNAL_ENTRY.md in worktree after merge
            When evolve.sh processes
            Then entry is prepended to JOURNAL.md and file removed

        Scenario: Clean up worktree after merge
            Given merge completes
            When cleanup happens
            Then worktree removed, branch deleted, lock released

        Scenario: Remove worktree on failure
            Given agent fails to implement scenario
            When cleanup_worktree trap fires
            Then worktree is force-removed

    Feature: Parallel Agent Orchestration
        As a framework developer
        I want to run multiple agents concurrently
        So that multiple scenarios can be implemented in one session

        Scenario: Find uncovered scenarios for orchestration
            Given BDD.md with 8 uncovered scenarios
            When orchestrate.py starts
            Then it lists all 8 for planning

        Scenario: Select top N scenarios for parallel run
            Given 10 uncovered scenarios and max_parallel_agents=3
            When orchestrate.py selects scenarios
            Then only top 3 are attempted this session

        Scenario: Create worktrees for parallel scenarios
            Given 3 selected scenarios
            When orchestrate.py creates worktrees
            Then 3 isolated worktrees exist with unique branches

        Scenario: Run agents in parallel with ThreadPoolExecutor
            Given 3 scenarios ready
            When orchestrate.py spawns workers
            Then up to max_parallel_agents run concurrently

        Scenario: Stream agent output with scenario prefix
            Given parallel agent running
            When output is printed
            Then each line is prefixed with [scenario_name]

        Scenario: Merge results in planned order
            Given 3 agents complete with varying success
            When orchestrate.py merges
            Then merges happen in the planned order (not completion order)

        Scenario: Track total agent time across workers
            Given 3 agents running for 120s, 90s, 150s
            When session completes
            Then total_time reported as 360s

        Scenario: Deferred scenarios message
            Given 10 scenarios with max_agents=3
            When orchestration completes
            Then it prints remaining 7 scenarios for next run

        Scenario: Read max_rounds from poppins.yml
            Given poppins.yml with orchestration.max_rounds: 3
            When orchestrate.py resolves configuration
            Then it runs 3 sequential rounds

        Scenario: Run orchestrator N rounds sequentially
            Given max_rounds=3 and max_parallel_agents=2 with 9 uncovered scenarios
            When orchestrate.py executes
            Then it runs 3 rounds: round 1 picks top 2, round 2 picks next 2 from remaining, round 3 picks next 2

        Scenario: Override max rounds via CLI
            Given --max-rounds=4 flag passed to orchestrate.py
            When orchestrate.py resolves max_rounds
            Then it runs 4 rounds instead of poppins.yml config

        Scenario: Write orchestrator event log
            Given orchestration session completes
            When orchestrator_events.jsonl is written
            Then it contains results for each scenario (merged, commits, tests_pass)

        Scenario: Write orchestrator journal entry
            Given 2 scenarios merged, 1 failed
            When JOURNAL.md is updated
            Then it lists merged and failed scenarios

        Scenario: Override max parallel agents via CLI
            Given --max-agents=5 flag passed
            When orchestrate.py resolves max_agents
            Then it uses 5 instead of poppins.yml config

        Scenario: Dry run mode shows plan without execution
            Given --dry-run flag passed to orchestrate.py
            When orchestration planning completes
            Then it prints "[dry-run] Would spawn agents" and exits without running

        Scenario: Custom BDD.md path via --bdd flag
            Given --bdd=/path/to/custom_bdd.md flag
            When orchestrate.py reads scenarios
            Then it parses from /path/to/custom_bdd.md

        Scenario: Worker result structure
            Given worker completes scenario implementation
            When result dict is returned
            Then it contains scenario, branch, wt_path, commits, tests_pass, elapsed_s, rc, stdout

        Scenario: Status indicators for worker output
            Given worker with 3 commits and tests passing
            When result is printed
            Then status is "[OK]" with green indication

        Scenario: Worker with no commits shows fail status
            Given worker ran but made no commits
            When result is printed
            Then status is "[FAIL: no commits]"

        Scenario: Worker with failing tests shows warning
            Given worker made commits but tests fail
            When result is printed
            Then status is "[WARN: tests failing]"

    Feature: Setup Environment Script
        As a framework developer
        I want setup_env.sh to install toolchains
        So that projects have required dependencies

        Scenario: Setup Rust toolchain
            Given LANGUAGE=rust and cargo not installed
            When setup_env.sh runs
            Then it installs Rust via rustup

        Scenario: Setup Node dependencies
            Given LANGUAGE=node and package.json exists
            When setup_env.sh runs
            Then it runs npm install

        Scenario: Setup Python dependencies
            Given LANGUAGE=python and requirements.txt exists
            When setup_env.sh runs
            Then it runs pip install -r requirements.txt

        Scenario: Setup Go dependencies
            Given LANGUAGE=go and go.mod exists
            When setup_env.sh runs
            Then it runs go mod download

        Scenario: Always install agent dependencies
            Given any LANGUAGE
            When setup_env.sh runs
            Then it ensures anthropic and openai packages are installed

        Scenario: Skip unknown language gracefully
            Given LANGUAGE=unknownlang
            When setup_env.sh runs
            Then it prints warning and skips toolchain setup

    Feature: Add BDD Markers Utility
        As a framework developer
        I want to add BDD marker comments to existing tests
        So that coverage detection works reliably

        Scenario: Detect comment prefix by file extension
            Given file.py extension
            When detect_comment_prefix() runs
            Then it returns "#"

        Scenario: Detect JavaScript comment prefix
            Given file.test.js extension
            When detect_comment_prefix() runs
            Then it returns "//"

        Scenario: Find test line matching scenario
            Given test file with "def test_login_with_valid_credentials"
            When find_test_line() searches for "Login with valid credentials"
            Then it returns the line index

        Scenario: Insert marker above test function
            Given test at line 10, no existing marker
            When add_marker_to_file() inserts
            Then "# BDD: <scenario>" appears at line 10, test moved to line 11

        Scenario: Skip if marker already exists
            Given test already has "# BDD: Login with valid credentials" above it
            When add_marker_to_file() checks
            Then it returns None (no modification)

        Scenario: Dry run mode shows planned changes
            Given add_bdd_markers.py without --apply flag
            When it runs
            Then it prints "[would add]" but does not modify files

        Scenario: Apply mode modifies files
            Given add_bdd_markers.py --apply
            When it runs
            Then it writes modified files with new markers

    Feature: Dotenv Loading
        As a framework developer
        I want to load .env files
        So that API keys can be configured without environment variables

        Scenario: Load .env file into environment
            Given .env file with ANTHROPIC_API_KEY=sk-abc
            When load_dotenv() runs
            Then os.environ["ANTHROPIC_API_KEY"] = "sk-abc"

        Scenario: Handle quoted values in .env
            Given .env with KEY="value with spaces"
            When load_dotenv() parses
            Then the quotes are stripped

        Scenario: Skip comment lines in .env
            Given .env with "# comment" and "KEY=value"
            When load_dotenv() loads
            Then only KEY is set, comment ignored

        Scenario: Environment variables override .env
            Given ANTHROPIC_API_KEY in both .env and environment
            When load_dotenv() runs
            Then environment value takes priority (not overwritten)

    Feature: CI/CD Integration
        As a framework developer
        I want CI workflows for automation
        So that evolution runs automatically on schedule

        Scenario: GitHub Actions workflow triggers on schedule
            Given .github/workflows/evolve.yml
            When cron schedule triggers ('0 */8 * * *')
            Then workflow runs evolve.sh every 8 hours

        Scenario: Manual workflow dispatch
            Given GitHub Actions UI
            When user clicks "Run workflow" button
            Then evolution runs immediately on demand

        Scenario: Bootstrap detection in workflow
            Given workflow running and .baadd_initialized file missing
            When workflow checks for bootstrap marker
            Then it runs bootstrap.sh instead of evolve.sh

        Scenario: Workflow timeout limit
            Given GitHub Actions workflow running
            When session exceeds 150 minutes
            Then GitHub Actions terminates the job

        Scenario: Retry after first attempt failure
            Given first evolution attempt fails
            When workflow detects failure outcome
            Then it waits 15 minutes and retries

        Scenario: Retry after second attempt failure
            Given second evolution attempt also fails
            When workflow detects both attempts failed
            Then it waits 45 minutes and retries third time

        Scenario: Configure git bot identity
            Given workflow starting
            When git config is set
            Then user.name is "baadd-agent[bot]" and email is bot address

        Scenario: GitHub Actions log grouping
            Given agent running in CI environment
            When tool output exceeds 5 lines
            Then it uses ::group:: and ::endgroup:: for collapsible sections

        Scenario: Detect CI environment
            Given CI=true or GITHUB_ACTIONS=true environment
            When IN_CI is set
            Then agent uses CI-optimized output format

        Scenario: Release workflow on version tag
            Given git tag v1.0.0 pushed
            When release.yml workflow triggers
            Then it creates GitHub Release with auto-generated notes

        Scenario: Release includes install.sh
            Given release workflow running
            When release is created
            Then install.sh is attached as release asset

        Scenario: Docs workflow triggers on docs path change
            Given push to main branch with changes in docs/
            When docs.yml workflow evaluates paths filter
            Then workflow triggers to rebuild and deploy docs

        Scenario: Docs deployment to GitHub Pages
            Given docs build completes successfully
            When deploy-pages action runs
            Then docs are deployed to github-pages environment

    Feature: Install Script
        As a framework developer
        I want install.sh to init and update baadd projects
        So that users can quickly start using the framework

        Scenario: Init new baadd project
            Given empty directory
            When install.sh runs without arguments
            Then it downloads framework files and creates .baadd manifest

        Scenario: Update existing baadd project
            Given existing .baadd manifest file
            When install.sh runs with --update flag
            Then it downloads latest framework files without overwriting user files

        Scenario: Auto-detect update mode
            Given .baadd manifest exists in current directory
            When install.sh runs without flags
            Then it automatically switches to update mode

        Scenario: Pin to specific version
            Given --version=v1.2.3 flag
            When install.sh runs
            Then it downloads files from that specific version tag

        Scenario: Fetch latest version from GitHub API
            Given no --version flag
            When install.sh resolves version
            Then it queries GitHub releases/latest API and uses tag_name

        Scenario: Skip no-clobber files on update
            Given existing BDD.md, BDD_STATUS.md, poppins.yml files
            When install.sh updates framework
            Then those files are skipped (not overwritten)

        Scenario: Archive journals before update
            Given existing JOURNAL.md and JOURNAL_INDEX.md
            When install.sh updates to new version
            Then they are archived as JOURNAL_archive_<old_version>.md

        Scenario: Create BDD.md from template
            Given init mode and no existing BDD.md
            When install.sh completes
            Then BDD.md is created from BDD.example.md template

        Scenario: Init git repo if missing
            Given init mode and no .git directory
            When install.sh runs
            Then git init is executed

        Scenario: Create locks directory
            Given install.sh running in any mode
            When directory setup happens
            Then locks/ directory is created with .gitkeep

        Scenario: Read manifest file list
            Given .baadd manifest with files array
            When read_manifest_files() parses
            Then it returns list of files to download

        Scenario: Stamp version in manifest
            Given .baadd manifest
            When stamp_version() updates it
            Then version field is set to current version string

        Scenario: Already on target version skips update
            Given .baadd with version=v1.2.3 and --version=v1.2.3
            When install.sh checks current version
            Then it prints "Already on baadd v1.2.3" and exits

        Scenario: Set executable permissions on scripts
            Given framework scripts downloaded
            When install.sh completes
            Then scripts/*.sh and scripts/*.py have chmod +x

        Scenario: Download file creates parent directories
            Given file path scripts/newdir/tool.py
            When download() fetches file
            Then scripts/newdir/ is created if needed

    Feature: Identity and Safety Rules
        As the AI agent
        I want clear rules about what I can and cannot modify
        So that I don't break the framework

        Scenario: Never modify IDENTITY.md
            Given IDENTITY.md exists
            When agent considers modifying it
            Then it must refuse (safety rule)

        Scenario: Never modify scripts/evolve.sh
            Given evolve.sh exists
            When agent considers modifying it
            Then it must refuse (safety rule)

        Scenario: Never modify .github/workflows/
            Given workflow files exist
            When agent considers modifying them
            Then it must refuse (safety rule)

        Scenario: Only build features from BDD.md
            Given a feature request not in BDD.md
            When agent receives request
            Then it adds scenario to BDD.md first, then implements next session

        Scenario: Never delete tests
            Given existing test file
            When agent considers deleting it
            Then it must refuse (tests protect from regression)

    Feature: Error Recovery
        As a framework developer
        I want graceful error handling
        So that failures don't corrupt the repository

        Scenario: API error causes retry exit
            Given agent_events.jsonl contains "type":"error"
            When evolve.sh checks log
            Then it exits for retry (no commit)

        Scenario: Post-merge verification catches breakage
            Given merge completes but main's tests fail
            When post-merge verification runs
            Then it reverts to session start SHA

        Scenario: Timeout kills long session
            Given session exceeds TIMEOUT seconds
            When timeout command fires
            Then agent process is terminated

        Scenario: Handle missing gh CLI gracefully
            Given gh command not available
            When evolve.sh tries to fetch issues
            Then it prints "gh CLI not available" and creates empty ISSUES_TODAY.md

        Scenario: Worktree creation failure
            Given git worktree add fails due to branch conflict
            When evolve.sh tries to create worktree
            Then it skips that scenario and tries next one

        Scenario: Handle test file that cannot be read
            Given test file with permission denied or encoding error
            When check_bdd_coverage.py tries to read content
            Then it skips that file and continues checking others

        Scenario: Tool output formatting with iteration tag
            Given agent at iteration 25 of 75 making tool call
            When print_tool_call() formats output
            Then it shows "[25/75]" prefix with tool icon

        Scenario: Tool icons for different tool types
            Given tool call for bash, read_file, write_file, edit_file, search_files
            When print_tool_call() formats each
            Then bash shows "$", read shows "<-", write shows "->", edit shows "~~", search shows "??"

        Scenario: Detect Moonshot provider
            Given MOONSHOT_API_KEY set and no ANTHROPIC_API_KEY
            When detect_provider() is called
            Then it returns "moonshot" with base_url "https://api.moonshot.cn/v1"

        Scenario: Detect Dashscope provider
            Given DASHSCOPE_API_KEY set and no higher-priority keys
            When detect_provider() is called
            Then it returns "dashscope" with base_url "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

        Scenario: Moonshot default model
            Given Moonshot provider detected
            When agent.py resolves model
            Then it uses default model "kimi-latest"

        Scenario: Dashscope default model
            Given Dashscope provider detected
            When agent.py resolves model
            Then it uses default model "qwen-max"

        Scenario: Groq default model
            Given Groq provider detected
            When agent.py resolves model
            Then it uses default model "llama-3.3-70b-versatile"

        Scenario: Ollama default model
            Given Ollama provider detected
            When agent.py resolves model
            Then it uses default model "llama3.2"

        Scenario: Custom provider requires api_key string placeholder
            Given custom provider with no CUSTOM_API_KEY
            When OpenAI client is constructed
            Then it uses "custom" as placeholder api_key string (client requires non-empty)

        Scenario: Ollama provider uses "ollama" as api_key
            Given Ollama provider detected
            When OpenAI client is constructed
            Then api_key is set to "ollama" string (Ollama doesn't require auth)

        Scenario: Mode flag affects wrap-up message content
            Given agent started with --mode=bootstrap
            When wrap_up_at threshold is reached
            Then wrap-up message mentions creating .baadd_initialized and Day 0 journal

        Scenario: Bootstrap mode agent prompt
            Given --mode=bootstrap flag passed to agent.py
            When agent session starts
            Then system prompt emphasizes scaffolding not implementing scenarios

        Scenario: Handle scenario with special characters in name
            Given scenario "Login with email (user@example.com)"
            When scenario_to_slug() processes
            Then special chars replaced with hyphens: "login-with-email-user-example-com"

        Scenario: Handle concurrent scenario locks
            Given 3 agents running concurrently with different scenarios
            When each writes lock file
            Then each has unique slug, unique lock file, unique branch

        Scenario: Issue response file format parsing
            Given ISSUE_RESPONSE.md with multiple issue blocks
            When evolve.sh parses for gh issue comment
            Then it extracts issue_number, status, comment for each block

    Feature: Dashboard — scripts/dashboard.py (Python, Rich TUI)
        As a developer running orchestrate.py
        I want a live terminal dashboard in scripts/dashboard.py written in Python using the Rich library
        So that I can monitor all agents in real time without reading interleaved log output

        The dashboard is implemented in scripts/dashboard.py using ONLY the rich library
        (pip install rich). It uses rich.live.Live as the outer refresh loop,
        rich.panel.Panel for each agent box, rich.console.Console for output,
        rich.text.Text for styled strings, and rich.console.Group to stack panels vertically.
        Progress bars are built manually as unicode strings using "█" (filled) and "░" (empty)
        characters — NOT rich.progress.Progress (which is for foreground tasks, not inline display).
        No other TUI library (textual, curses, urwid, blessed) is used.

        Scenario: Dashboard file exists at scripts/dashboard.py
            Given the dashboard feature is implemented
            When "python3 scripts/dashboard.py --help" is run
            Then it exits without error and prints usage including "--watch" and "--refresh"

        Scenario: Rich is the only third-party import in dashboard.py
            Given scripts/dashboard.py source is read
            When all import statements are inspected
            Then the only third-party package imported is "rich" — no textual, urwid, curses, blessed

        Scenario: Running "python3 scripts/dashboard.py" opens the Rich TUI immediately
            Given scripts/dashboard.py is executed without --watch
            When the process starts
            Then a rich.live.Live display opens in the terminal immediately (before orchestrate.py produces any output)
            And it begins polling for worktrees and rendering panels every 2 seconds

        Scenario: The dashboard is only for scripts/orchestrate.py — not evolve.sh or agent.py
            Given scripts/dashboard.py is read
            When the subprocess command is inspected
            Then it only ever spawns ["python3", "scripts/orchestrate.py", ...] — never evolve.sh, agent.py, or any other script

        Scenario: dashboard.py defines a main() function called from __main__
            Given scripts/dashboard.py is read
            When the bottom of the file is checked
            Then it contains: if __name__ == "__main__": main()

        Scenario: Live refresh loop uses rich.live.Live with refresh_per_second
            Given scripts/dashboard.py is read
            When the Live usage is inspected
            Then it instantiates rich.live.Live(renderable, console=Console(), refresh_per_second=0.5)
            And calls live.update(build_renderable()) inside the polling loop

        Scenario: Each agent is rendered as a rich.panel.Panel
            Given build_agent_panel(state) is called with a valid AgentState
            When the return value is inspected
            Then it is an instance of rich.panel.Panel
            And the panel title is the scenario_name string

        Scenario: Overall renderable is a rich.console.Group of Panels stacked vertically
            Given build_renderable(states, log_buffer, session_elapsed) is called with 2 AgentState objects
            When the return value is inspected
            Then it is a rich.console.Group containing one Panel per agent plus a header Panel and a log Panel

    Feature: Dashboard Worktree Discovery
        As a developer watching orchestrate.py run
        I want the dashboard to discover active agent worktrees automatically
        So that it can display one panel per running agent

        discover_worktrees(main_dir) runs: subprocess.run(["git", "worktree", "list", "--porcelain"], ...)
        and returns a list of absolute paths that start with "/tmp/baadd-wt-".

        Scenario: discover_worktrees returns baadd worktree paths from git worktree list output
            Given git worktree list --porcelain output includes a "worktree /tmp/baadd-wt-my-scenario-1234" line
            When discover_worktrees("/home/user/project") is called
            Then it returns ["/tmp/baadd-wt-my-scenario-1234"]

        Scenario: discover_worktrees excludes the main worktree
            Given git worktree list output includes "worktree /home/user/project" (the main dir) and "worktree /tmp/baadd-wt-foo-99"
            When discover_worktrees("/home/user/project") is called
            Then it returns ["/tmp/baadd-wt-foo-99"] only — the main dir path is excluded

        Scenario: discover_worktrees returns empty list when no baadd worktrees exist
            Given git worktree list output contains only the main worktree line
            When discover_worktrees() is called
            Then it returns []

        Scenario: discover_worktrees returns empty list when git command fails
            Given subprocess.run raises an OSError or returns non-zero exit code
            When discover_worktrees() is called
            Then it returns [] without raising an exception

        Scenario: slug_to_name converts hyphenated path slug to display name
            Given wt_path is "/tmp/baadd-wt-enable-verbose-mode-5678"
            When slug_to_name(wt_path) is called
            Then it strips the "/tmp/baadd-wt-" prefix, strips the trailing "-<digits>" pid suffix
            And replaces remaining hyphens with spaces, returning "enable verbose mode"

        Scenario: slug_to_name handles path with no trailing digits
            Given wt_path is "/tmp/baadd-wt-my-feature"
            When slug_to_name(wt_path) is called
            Then it returns "my feature" without error

        Scenario: resolve_display_name prefers explicit wt_map entry over slug
            Given wt_map = {"/tmp/baadd-wt-foo-1": "Foo Bar Baz"}
            When resolve_display_name("/tmp/baadd-wt-foo-1", wt_map) is called
            Then it returns "Foo Bar Baz" — not the slug-derived fallback

        Scenario: resolve_display_name falls back to slug_to_name when path not in wt_map
            Given wt_map = {} (empty)
            When resolve_display_name("/tmp/baadd-wt-my-scenario-42", wt_map) is called
            Then it returns "my scenario" (slug fallback)

    Feature: JSONL Event Log Reading
        As a developer watching orchestrate.py run
        I want the dashboard to parse agent_events_*.jsonl files in each worktree
        So that it shows accurate phase, iteration, tokens, and recent tool calls

        read_wt_state(wt_path) globs for all agent_events_*.jsonl files in wt_path.
        It identifies phase from the filename prefix using this mapping:
          "pm_plan" → "PM-PLAN", "se" → "SE", "tester" → "TESTER", "pm_accept" → "ACCEPT"
        For each phase it picks the file with the highest mtime (to handle retries like se_1_, se_2_).
        It then reads every line as JSON, collecting: iteration_start, session_end, api_response, tool_call events.
        Returns an AgentState dataclass.

        Scenario: read_wt_state reads current_iter as the highest iteration value seen in iteration_start events
            Given a JSONL file containing iteration_start events with iteration values 1, 5, 12
            When read_wt_state(wt_path) is called
            Then the returned AgentState has current_iter == 12

        Scenario: read_wt_state reads max_iter from the max_iterations field of iteration_start events
            Given a JSONL file with an iteration_start event containing max_iterations=125
            When read_wt_state(wt_path) is called
            Then the returned AgentState has max_iter == 125

        Scenario: read_wt_state sets active_phase to the label of the most recent phase lacking session_end
            Given agent_events_pm_plan_*.jsonl has a session_end event
            And agent_events_se_*.jsonl has an iteration_start but no session_end
            When read_wt_state(wt_path) is called
            Then state.active_phase == "SE"

        Scenario: read_wt_state adds a phase label to done_phases when its log contains session_end
            Given agent_events_pm_plan_*.jsonl contains {"event": "session_end", ...}
            When read_wt_state(wt_path) is called
            Then "PM-PLAN" is in state.done_phases

        Scenario: read_wt_state returns done_phases in fixed pipeline order PM-PLAN SE TESTER ACCEPT
            Given both pm_plan and se logs have session_end (se log is newer)
            When read_wt_state(wt_path) is called
            Then state.done_phases == ["PM-PLAN", "SE"] — pm_plan appears first regardless of mtime

        Scenario: read_wt_state reads tokens as the highest cumulative_output_tokens seen in api_response events
            Given an api_response event with cumulative_output_tokens=4500
            When read_wt_state(wt_path) is called
            Then state.tokens == 4500

        Scenario: read_wt_state reads start_ts as a float epoch from the ts field of the session_start event
            Given a session_start event with ts="2026-04-26T10:00:00+00:00"
            When read_wt_state(wt_path) is called
            Then state.start_ts is a float approximately equal to datetime.fromisoformat("2026-04-26T10:00:00+00:00").timestamp()

        Scenario: read_wt_state collects the 3 most recent tool_call events from the active phase log as last_tools
            Given the active phase JSONL file contains 5 tool_call events in order A B C D E
            When read_wt_state(wt_path) is called
            Then state.last_tools == [format_tool_call(C), format_tool_call(D), format_tool_call(E)]

        Scenario: read_wt_state skips malformed JSON lines and continues reading
            Given a JSONL file where line 3 is "not valid json" and lines 1,2,4 are valid events
            When read_wt_state(wt_path) is called
            Then it does not raise an exception and processes lines 1, 2, and 4 correctly

        Scenario: read_wt_state returns zeroed AgentState when no JSONL files exist in worktree
            Given a worktree directory containing no agent_events_*.jsonl files
            When read_wt_state(wt_path) is called
            Then state.active_phase is None, state.done_phases == [], state.current_iter == 0, state.tokens == 0

        Scenario: read_wt_state picks the JSONL file with the highest mtime when multiple files share the same phase prefix
            Given agent_events_se_1_foo.jsonl (mtime=T) and agent_events_se_2_foo.jsonl (mtime=T+60)
            When read_wt_state(wt_path) selects which se log to use
            Then it reads agent_events_se_2_foo.jsonl (the most recently modified)

        Scenario: read_wt_state handles OSError when opening a JSONL file
            Given one of the agent_events_*.jsonl files raises OSError when opened
            When read_wt_state(wt_path) is called
            Then it skips that file and still processes the remaining files without raising

        Scenario: read_wt_state sets start_ts to current time when no session_start event exists
            Given a JSONL file with iteration_start events but no session_start event
            When read_wt_state(wt_path) is called
            Then state.start_ts is approximately time.time() (defaults to now)

    Feature: AgentState Dataclass
        As a developer building the dashboard
        I want a clean Python dataclass to hold per-agent state
        So that rendering functions are pure and easy to test

        AgentState is a dataclass defined in scripts/dashboard.py with these fields:
          wt_path: str
          scenario_name: str
          active_phase: Optional[str]  # "PM-PLAN", "SE", "TESTER", "ACCEPT", or None
          done_phases: List[str]
          current_iter: int
          max_iter: int
          tokens: int
          last_tools: List[str]  # up to 3 formatted tool call strings
          start_ts: float  # epoch timestamp, defaults to time.time()

        Scenario: AgentState is a dataclass with the required fields
            Given scripts/dashboard.py is read
            When the AgentState class definition is inspected
            Then it is decorated with @dataclass and has fields: wt_path, scenario_name, active_phase, done_phases, current_iter, max_iter, tokens, last_tools, start_ts

        Scenario: AgentState.elapsed_s property returns seconds since start_ts
            Given an AgentState with start_ts = time.time() - 60
            When state.elapsed_s is accessed
            Then it returns a float between 59 and 61

        Scenario: AgentState.is_stale property returns True when newest JSONL mtime is over 120 seconds old
            Given all agent_events_*.jsonl files in wt_path have mtime older than 120 seconds ago
            When state.is_stale is accessed (it re-stats the files each call)
            Then it returns True

        Scenario: AgentState.is_stale returns False when any JSONL file was modified within 120 seconds
            Given at least one agent_events_*.jsonl file has mtime within the last 30 seconds
            When state.is_stale is accessed
            Then it returns False

        Scenario: AgentState.is_stale returns False when worktree has no JSONL files yet
            Given wt_path directory exists but contains no agent_events_*.jsonl files
            When state.is_stale is accessed
            Then it returns False (not stale — just not started yet)

        Scenario: AgentState.is_done returns True only when all four phase labels are in done_phases
            Given state.done_phases == ["PM-PLAN", "SE", "TESTER", "ACCEPT"]
            When state.is_done is accessed
            Then it returns True

        Scenario: AgentState.is_done returns False when fewer than four phases are done
            Given state.done_phases == ["PM-PLAN", "SE"]
            When state.is_done is accessed
            Then it returns False

    Feature: Tool Call Formatting
        As a developer building the dashboard
        I want format_tool_call(tool, input_dict) to produce concise one-line action strings
        So that the agent "thought process" is readable at a glance in the panel

        format_tool_call(tool: str, input_dict: dict) -> str
        Maps known tool names to short prefixes and extracts the most relevant input field.
        The function lives in scripts/dashboard.py.

        Scenario: format_tool_call formats read_file as "r: <path>"
            Given tool="read_file" and input_dict={"path": "src/main.rs"}
            When format_tool_call("read_file", {"path": "src/main.rs"}) is called
            Then it returns "r: src/main.rs"

        Scenario: format_tool_call formats write_file as "w: <path>"
            Given tool="write_file" and input_dict={"path": "tests/test_foo.py", "content": "..."}
            When format_tool_call("write_file", {"path": "tests/test_foo.py", "content": "..."}) is called
            Then it returns "w: tests/test_foo.py" (content field ignored)

        Scenario: format_tool_call formats bash as "$ <command>" truncated to 60 chars
            Given tool="bash" and input_dict={"command": "cargo test --all -- --nocapture --test-threads=1 2>&1 | head"}
            When format_tool_call("bash", input_dict) is called
            Then the returned string starts with "$ " and the command portion is at most 60 characters

        Scenario: format_tool_call formats run_command identically to bash
            Given tool="run_command" and input_dict={"command": "pytest tests/ -v"}
            When format_tool_call("run_command", {"command": "pytest tests/ -v"}) is called
            Then it returns "$ pytest tests/ -v"

        Scenario: format_tool_call formats edit_file as "e: <path>"
            Given tool="edit_file" and input_dict={"path": "src/lib.rs", "old_string": "x", "new_string": "y"}
            When format_tool_call("edit_file", {"path": "src/lib.rs", "old_string": "x", "new_string": "y"}) is called
            Then it returns "e: src/lib.rs"

        Scenario: format_tool_call uses generic "tool: value" format for unknown tools
            Given tool="search_files" and input_dict={"pattern": "def authenticate"}
            When format_tool_call("search_files", {"pattern": "def authenticate"}) is called
            Then it returns "search_files: def authenticate"

        Scenario: format_tool_call returns "r: ?" when path key is missing from input_dict for read_file
            Given tool="read_file" and input_dict={} (empty dict)
            When format_tool_call("read_file", {}) is called
            Then it returns "r: ?" without raising a KeyError

        Scenario: format_tool_call handles None input_dict without raising
            Given tool="bash" and input_dict=None
            When format_tool_call("bash", None) is called
            Then it returns "$ ?" without raising an exception

    Feature: Log Line Filtering
        As a developer building the dashboard
        I want is_log_noise(line: str) -> bool to classify each stdout line from orchestrate.py
        So that the log strip panel shows only useful orchestrator-level output

        is_log_noise(line) returns True for lines that should be suppressed (per-agent noise).
        It returns False for lines that should be kept in the log buffer.
        parse_wt_mapping_line(line) -> Optional[Tuple[str, str]] parses the
        "  <scenario_name> → <wt_path>" lines that orchestrate.py prints when creating worktrees.
        Both functions live in scripts/dashboard.py.

        Scenario: is_log_noise returns True for TPS monitor lines matching "tok | X TPS |"
            Given line = "  [My Scenario PM-PLAN] 1234 tok | 45.1 TPS | 30s"
            When is_log_noise(line) is called
            Then it returns True

        Scenario: is_log_noise returns True for bracketed per-agent output lines
            Given line = "  [My Scenario SE] Writing implementation..."
            When is_log_noise(line) is called
            Then it returns True (matches pattern r"^\s+\[.+?\] " with non-TPS content)

        Scenario: is_log_noise returns False for round banner lines starting with "==="
            Given line = "=== Round 2/3 — 2 scenario(s) ==="
            When is_log_noise(line) is called
            Then it returns False

        Scenario: is_log_noise returns False for MERGED result lines
            Given line = "    → MERGED"
            When is_log_noise(line) is called
            Then it returns False

        Scenario: is_log_noise returns False for THROWN AWAY result lines
            Given line = "    → THROWN AWAY (no commits — agent made no progress)"
            When is_log_noise(line) is called
            Then it returns False

        Scenario: is_log_noise returns False for Pre-flight status lines
            Given line = "  Pre-flight: OK"
            When is_log_noise(line) is called
            Then it returns False

        Scenario: is_log_noise returns False for scenario-to-worktree mapping lines containing " → /tmp"
            Given line = "  My Scenario → /tmp/baadd-wt-my-scenario-1234"
            When is_log_noise(line) is called
            Then it returns False

        Scenario: is_log_noise returns False for empty lines
            Given line = ""
            When is_log_noise(line) is called
            Then it returns False

        Scenario: parse_wt_mapping_line extracts scenario name and worktree path
            Given line = "  Enable verbose mode → /tmp/baadd-wt-enable-verbose-mode-5678"
            When parse_wt_mapping_line(line) is called
            Then it returns the tuple ("Enable verbose mode", "/tmp/baadd-wt-enable-verbose-mode-5678")

        Scenario: parse_wt_mapping_line returns None for lines without " → /tmp"
            Given line = "  Pre-flight: OK"
            When parse_wt_mapping_line(line) is called
            Then it returns None

        Scenario: parse_wt_mapping_line returns None for empty string
            Given line = ""
            When parse_wt_mapping_line("") is called
            Then it returns None

        Scenario: log buffer is a deque(maxlen=10) that automatically discards oldest entries
            Given 15 non-noise lines have been appended to a deque(maxlen=10)
            When the deque is read
            Then it contains exactly 10 entries — the 10 most recent kept lines

    Feature: Dashboard Rendering Functions
        As a developer building the dashboard
        I want pure functions that build Rich renderables from AgentState data
        So that rendering is testable without a real terminal

        All rendering functions live in scripts/dashboard.py.
        They return plain strings or rich.text.Text / rich.panel.Panel objects.
        Tests call the functions and assert on the returned string content.

        Scenario: format_phase_line returns correct string for two done phases and one active phase
            Given done_phases=["PM-PLAN", "SE"], active_phase="TESTER", current_iter=31, max_iter=125
            When format_phase_line(done_phases, active_phase, current_iter, max_iter) is called
            Then the returned string contains "PM-PLAN✓", "SE✓", "TESTER", "31/125", and "─" for ACCEPT

        Scenario: format_phase_line returns all checkmarks when all four phases are done
            Given done_phases=["PM-PLAN", "SE", "TESTER", "ACCEPT"], active_phase=None
            When format_phase_line(done_phases, None, 0, 125) is called
            Then the returned string contains "PM-PLAN✓", "SE✓", "TESTER✓", "ACCEPT✓"

        Scenario: format_phase_line returns four dashes when nothing has started
            Given done_phases=[], active_phase=None
            When format_phase_line([], None, 0, 125) is called
            Then the returned string contains four "─" characters (one per phase)

        Scenario: format_phase_line shows active phase with iteration count
            Given done_phases=[], active_phase="PM-PLAN", current_iter=5, max_iter=125
            When format_phase_line([], "PM-PLAN", 5, 125) is called
            Then the returned string contains "PM-PLAN" and "5/125" and three "─" for the remaining phases

        Scenario: render_progress_bar returns a string of bar_width unicode chars using "█" and "░"
            Given current_iter=0, max_iter=125, bar_width=20
            When render_progress_bar(0, 125, 20) is called
            Then it returns "░░░░░░░░░░░░░░░░░░░░" (20 empty chars)

        Scenario: render_progress_bar fills correct proportion at 50 percent
            Given current_iter=62, max_iter=125 (approximately 49.6% ≈ 9 filled out of 20), bar_width=20
            When render_progress_bar(62, 125, 20) is called
            Then the returned string is exactly 20 chars and starts with "█████████░" (9 filled)

        Scenario: render_progress_bar returns fully filled bar at 100 percent
            Given current_iter=125, max_iter=125, bar_width=20
            When render_progress_bar(125, 125, 20) is called
            Then it returns "████████████████████" (20 filled chars)

        Scenario: render_progress_bar clamps fill at 100 percent when current_iter exceeds max_iter
            Given current_iter=200, max_iter=125, bar_width=20
            When render_progress_bar(200, 125, 20) is called
            Then it returns "████████████████████" (20 filled chars, no overflow or exception)

        Scenario: render_progress_bar handles max_iter=0 without division-by-zero
            Given current_iter=0, max_iter=0, bar_width=20
            When render_progress_bar(0, 0, 20) is called
            Then it returns "░░░░░░░░░░░░░░░░░░░░" without raising ZeroDivisionError

        Scenario: format_metrics_line returns formatted tokens and TPS string
            Given tokens=8321, tps=38.4
            When format_metrics_line(8321, 38.4) is called
            Then it returns "8,321 tok  38.4 TPS"

        Scenario: format_metrics_line returns dash when tokens is zero
            Given tokens=0, tps=0.0
            When format_metrics_line(0, 0.0) is called
            Then it returns "─" — not "0 tok  0.0 TPS"

        Scenario: format_metrics_line computes TPS as tokens divided by elapsed_s
            Given tokens=3600, elapsed_s=60
            When format_metrics_line(3600, elapsed_s=60) is called
            Then tps in the output is 60.0

        Scenario: format_metrics_line does not divide by zero when elapsed_s is 0
            Given tokens=100, elapsed_s=0
            When format_metrics_line(100, elapsed_s=0) is called
            Then it returns a string without raising ZeroDivisionError (tps shown as 0.0 or "─")

        Scenario: format_elapsed returns seconds string for durations under 60 seconds
            Given elapsed_s=45
            When format_elapsed(45) is called
            Then it returns "45s"

        Scenario: format_elapsed returns minutes and zero-padded seconds for durations over 60 seconds
            Given elapsed_s=185
            When format_elapsed(185) is called
            Then it returns "3m05s"

        Scenario: format_elapsed returns "0s" for zero elapsed time
            Given elapsed_s=0
            When format_elapsed(0) is called
            Then it returns "0s"

        Scenario: build_agent_panel returns a rich.panel.Panel whose title is the scenario name
            Given a valid AgentState with scenario_name="My Scenario"
            When build_agent_panel(state) is called
            Then isinstance(result, rich.panel.Panel) is True
            And the panel's title contains "My Scenario"

        Scenario: build_agent_panel appends "(stale)" to panel title when state.is_stale is True
            Given a valid AgentState where is_stale returns True
            When build_agent_panel(state) is called
            Then the panel's title contains "(stale)"

        Scenario: build_agent_panel does not include "(stale)" when state.is_stale is False
            Given a valid AgentState where is_stale returns False
            When build_agent_panel(state) is called
            Then the panel's title does not contain "(stale)"

        Scenario: format_header returns a string containing agent count and session elapsed time
            Given 3 AgentState objects and session_start_ts = time.time() - 95
            When format_header(states, session_start_ts) is called
            Then the returned string contains "3 agents" and "1m35s"

        Scenario: format_header returns "waiting for agents" string when states list is empty
            Given states=[]
            When format_header([], session_start_ts) is called
            Then the returned string contains "waiting for agents"

        Scenario: format_log_strip returns a string containing all lines from the log buffer
            Given log_buffer = deque(["Pre-flight: OK", "→ MERGED", "Round 2/3 complete"])
            When format_log_strip(log_buffer) is called
            Then "Pre-flight: OK" and "→ MERGED" and "Round 2/3 complete" all appear in the returned string

        Scenario: format_log_strip returns a placeholder string when log buffer is empty
            Given log_buffer = deque([])
            When format_log_strip(log_buffer) is called
            Then it returns a non-empty string such as "(waiting for orchestrator output...)"

        Scenario: build_renderable returns a rich.console.Group containing all agent panels plus header and log panels
            Given 2 AgentState objects and a non-empty log_buffer
            When build_renderable(states, log_buffer, session_start_ts) is called
            Then isinstance(result, rich.console.Group) is True
            And len(result.renderables) == 4 (header panel + 2 agent panels + log panel)

        Scenario: build_renderable returns a Group with only header and log panels when states is empty
            Given states=[] and empty log_buffer
            When build_renderable([], log_buffer, session_start_ts) is called
            Then isinstance(result, rich.console.Group) is True
            And len(result.renderables) == 2 (header panel + log panel)

    Feature: Wrapper Mode
        As a developer who wants to replace running orchestrate.py directly
        I want "python3 scripts/dashboard.py [args]" to launch orchestrate.py as a subprocess
        So that I see the TUI instead of raw interleaved output

        In wrapper mode (no --watch flag), dashboard.py runs:
          subprocess.Popen(["python3", "scripts/orchestrate.py"] + pass_through_args,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        A daemon threading.Thread reads proc.stdout line by line, calls is_log_noise() on each line,
        appends non-noise lines to a deque(maxlen=10), and calls parse_wt_mapping_line() to build wt_map.
        The main thread runs a rich.live.Live loop polling at poll_interval seconds.
        When proc.poll() is not None the loop exits and sys.exit(proc.returncode) is called.

        Scenario: wrapper mode constructs the subprocess command as ["python3", "scripts/orchestrate.py"] plus forwarded args
            Given parse_args() returns Namespace(watch=False, refresh=2, pass_args=["--max-agents", "3"])
            When build_subprocess_cmd(pass_args=["--max-agents", "3"]) is called
            Then it returns ["python3", "scripts/orchestrate.py", "--max-agents", "3"]

        Scenario: wrapper mode passes all unrecognised args through to orchestrate.py unchanged
            Given dashboard.py is invoked with "python3 scripts/dashboard.py --max-agents 2 --max-rounds 3"
            When the subprocess is constructed
            Then orchestrate.py receives the argv ["--max-agents", "2", "--max-rounds", "3"]

        Scenario: stdout reader thread calls is_log_noise on each line and only appends non-noise lines to log_buffer
            Given a mock proc.stdout that yields ["  [Foo SE] detail", "→ MERGED", ""]
            When the stdout reader thread processes those lines
            Then log_buffer contains ["→ MERGED"] only — the bracketed agent line is filtered out

        Scenario: stdout reader thread calls parse_wt_mapping_line and populates wt_map for matching lines
            Given proc.stdout yields "  My Scenario → /tmp/baadd-wt-my-scenario-1"
            When the stdout reader processes that line
            Then wt_map == {"/tmp/baadd-wt-my-scenario-1": "My Scenario"}

        Scenario: wrapper main loop calls sys.exit with orchestrate.py returncode when subprocess exits with 0
            Given the subprocess exits with returncode 0
            When the main loop detects proc.poll() is not None
            Then sys.exit(0) is called

        Scenario: wrapper main loop calls sys.exit with orchestrate.py returncode when subprocess exits with 1
            Given the subprocess exits with returncode 1
            When the main loop detects proc.poll() is not None
            Then sys.exit(1) is called

        Scenario: wrapper renders "waiting for agents" header when no worktrees exist yet
            Given wt_map is empty and discover_worktrees returns []
            When build_renderable([], log_buffer, session_start_ts) is rendered
            Then the header panel contains "waiting for agents"

        Scenario: wrapper adds a new agent panel when a worktree appears between polls
            Given the first poll finds 1 worktree and the second poll finds 2 worktrees
            When build_renderable is called on the second poll
            Then it returns a Group containing 2 agent panels

        Scenario: wrapper mode raises RuntimeError and prints clear message when scripts/orchestrate.py does not exist
            Given "scripts/orchestrate.py" does not exist at the expected path
            When the subprocess Popen call raises FileNotFoundError
            Then dashboard.py prints "ERROR: scripts/orchestrate.py not found" and exits with code 1

    Feature: Watcher Mode
        As a developer who wants to monitor an already-running orchestration
        I want "python3 scripts/dashboard.py --watch" to attach to existing worktrees
        So that I can observe without launching a new orchestration

        In watcher mode the subprocess is never started.
        discover_worktrees() is called on every poll to find /tmp/baadd-wt-* paths.
        The loop exits when discover_worktrees() has returned [] on two consecutive polls
        (to avoid exiting prematurely if worktrees are being created).
        After the Live context exits, it prints "All agents done." to stdout.

        Scenario: --watch flag causes no subprocess to be started
            Given dashboard.py is invoked with --watch
            When run_watcher_mode() executes
            Then subprocess.Popen is never called

        Scenario: watcher mode calls discover_worktrees on every poll iteration
            Given two polls occur with discover_worktrees returning ["/tmp/baadd-wt-foo-1"]
            When run_watcher_mode() polls twice
            Then discover_worktrees() has been called at least twice

        Scenario: watcher exits after two consecutive empty polls from discover_worktrees
            Given discover_worktrees returns [] on poll N and [] on poll N+1
            When run_watcher_mode() processes poll N+1
            Then the Live loop exits cleanly

        Scenario: watcher does not exit after a single empty poll
            Given discover_worktrees returns [] on poll N but ["/tmp/baadd-wt-foo"] on poll N-1
            When run_watcher_mode() processes poll N
            Then the loop continues (single empty result is not enough to exit)

        Scenario: watcher prints "All agents done." to stdout after the Live context closes
            Given all worktrees are cleaned up and watcher exits
            When run_watcher_mode() returns
            Then the console has printed "All agents done."

        Scenario: watcher resolves scenario names from slug_to_name when no wt_map is available
            Given discover_worktrees returns ["/tmp/baadd-wt-my-feature-42"] and wt_map is empty
            When build_renderable is called
            Then the agent panel title contains "my feature"

    Feature: Dashboard CLI Arguments
        As a developer using the dashboard
        I want a clear argparse CLI in dashboard.py
        So that both wrapper and watcher modes are easy to invoke and configure

        parse_args() uses argparse.ArgumentParser with parse_known_args() so that unrecognised flags
        are collected in a remainder list and forwarded to orchestrate.py in wrapper mode.
        It returns a Namespace with: watch (bool), refresh (int), and pass_args (list of str).

        Scenario: parse_args returns watch=False and mode is wrapper when --watch is absent
            Given sys.argv = ["dashboard.py"]
            When parse_args() is called
            Then result.watch is False

        Scenario: parse_args returns watch=True when --watch flag is present
            Given sys.argv = ["dashboard.py", "--watch"]
            When parse_args() is called
            Then result.watch is True

        Scenario: parse_args collects unrecognised flags into pass_args for forwarding
            Given sys.argv = ["dashboard.py", "--max-agents", "2", "--max-rounds", "3"]
            When parse_args() is called
            Then result.pass_args == ["--max-agents", "2", "--max-rounds", "3"]

        Scenario: parse_args --refresh sets poll interval
            Given sys.argv = ["dashboard.py", "--refresh", "5"]
            When parse_args() is called
            Then result.refresh == 5

        Scenario: parse_args default refresh interval is 2 seconds
            Given sys.argv = ["dashboard.py"]
            When parse_args() is called
            Then result.refresh == 2

        Scenario: --watch and --refresh can be combined with pass_args
            Given sys.argv = ["dashboard.py", "--watch", "--refresh", "3", "--max-agents", "2"]
            When parse_args() is called
            Then result.watch is True, result.refresh == 3, result.pass_args == ["--max-agents", "2"]

    Feature: Dashboard Error Handling and Edge Cases
        As a developer using the dashboard
        I want robust error handling throughout scripts/dashboard.py
        So that the TUI never crashes or hangs due to environment issues

        Scenario: Missing rich package causes immediate error with install instruction
            Given "import rich" raises ImportError
            When scripts/dashboard.py is executed
            Then it prints "ERROR: rich not installed. Run: pip install rich" to stderr and exits with code 1

        Scenario: KeyboardInterrupt during Live loop exits cleanly without traceback
            Given the Live loop is running and the user presses Ctrl-C
            When KeyboardInterrupt is raised inside the with Live(...) block
            Then the exception is caught, the Live display is closed, and the process exits with code 0 — no traceback printed

        Scenario: SIGTERM during wrapper mode terminates the subprocess before exiting
            Given dashboard.py is in wrapper mode and receives SIGTERM
            When the signal handler fires
            Then proc.terminate() is called on the orchestrate.py subprocess before the process exits

        Scenario: Worktree directory disappears between polls without crashing
            Given a worktree path was valid on the previous poll but has been deleted (rm -rf)
            When read_wt_state(vanished_wt_path) is called on the next poll
            Then it returns a zeroed AgentState without raising FileNotFoundError

        Scenario: glob finds no JSONL files in a worktree that exists but has not started yet
            Given glob("agent_events_*.jsonl") returns [] for wt_path
            When read_wt_state(wt_path) is called
            Then state.active_phase is None and state.current_iter == 0 — no exception

        Scenario: TPS calculation guards against division by zero when elapsed_s is 0
            Given state.tokens=500 and state.elapsed_s returns 0.0
            When format_metrics_line is called with those values
            Then it does not raise ZeroDivisionError and returns a valid string

        Scenario: Very long scenario name is truncated in panel title to prevent wrapping
            Given state.scenario_name is a 120-character string
            When build_agent_panel(state) is called
            Then the panel title uses at most 60 characters of the scenario name (truncated with "…")

        Scenario: render_progress_bar always returns a string of exactly bar_width characters
            Given bar_width=20 and various current_iter and max_iter values
            When render_progress_bar(current_iter, max_iter, bar_width) is called for each
            Then len(result) == 20 in every case

        Scenario: Dashboard handles zero-width terminal gracefully
            Given Console().width returns a very small number (less than 40)
            When build_renderable is called
            Then it does not raise an exception — panels render with minimum content

        Scenario: stdout reader thread sets a threading.Event when subprocess stdout is exhausted
            Given the subprocess closes its stdout pipe (process ended)
            When the stdout reader thread finishes reading
            Then it sets a done_event so the main loop can detect process exit without polling returncode in a tight loop

    Feature: Merge Agent for Conflict Resolution
        As a framework developer
        I want a dedicated merge agent to handle scenario merges
        So that conflicts are resolved intelligently before post-merge tests

        Scenario: Merge agent detects merge conflicts
            Given 3 scenarios modified the same test file with different imports
            When merge agent attempts to merge
            Then it detects the conflict markers in the file

        Scenario: Merge agent combines imports from multiple scenarios
            Given scenario A adds "from mod import foo" and scenario B adds "from mod import bar"
            When merge agent processes both
            Then merged file contains "from mod import foo, bar"

        Scenario: Merge agent preserves all test functions
            Given scenario A adds test_foo() and scenario B adds test_bar()
            When merge agent processes both
            Then merged file contains both test functions

        Scenario: Merge agent inserts markers above test functions
            Given test function at line 10 with no marker
            When merge agent processes scenario "Foo scenario"
            Then "# BDD: Foo scenario" is inserted at line 10

        Scenario: Merge agent handles duplicate markers
            Given test already has "# BDD: Foo scenario"
            When merge agent processes scenario "Foo scenario" again
            Then it skips adding the duplicate marker

        Scenario: Merge agent writes resolved file to staging
            Given conflict resolved in memory
            When merge agent commits
            Then resolved file is added to git index with conflict markers removed

        Scenario: Merge agent logs resolution decisions
            Given merge conflict detected
            When merge agent resolves
            Then it writes merge_resolution.jsonl with timestamp, file, action

    Feature: Integration Test Agent
        As a framework developer
        I want a dedicated agent to run post-merge integration tests
        So that failures are caught and fixed before final commit

        Scenario: Integration test agent runs full test suite
            Given merge agent has merged 3 scenarios
            When integration test agent runs
            Then it executes all test files in tests/

        Scenario: Integration test agent reports pass
            Given all tests pass after merge
            When integration test agent completes
            Then it prints "[OK] All tests passing" and exits with code 0

        Scenario: Integration test agent reports fail
            Given tests fail after merge (e.g., syntax error from conflict)
            When integration test agent completes
            Then it prints "[FAIL] X tests failed" and exits with code 1

        Scenario: Integration test agent attempts fix on failure
            Given tests fail after merge
            When integration test agent runs fix attempt
            Then it analyzes failure output and suggests fix

        Scenario: Integration test agent re-runs tests after fix
            Given integration test agent suggests fix
            When fix is applied and tests re-run
            Then it reports pass or fail

        Scenario: Integration test agent fails session on persistent failure
            Given tests fail after 1 fix attempt
            When integration test agent completes
            Then orchestration marks scenario as THROWN AWAY

        Scenario: Integration test agent writes test result log
            Given integration test completes
            When result is logged
            Then test_results.jsonl contains scenario, pass_count, fail_count, duration_ms

    Feature: Worktree Session Lifecycle
        As a developer running evolve.sh or orchestrate.py
        I want sessions to register start and end events in a central log
        So that the dashboard can distinguish live agents from orphaned or completed worktrees

        evolve.sh and orchestrate.py append JSON lines to sessions.jsonl in the main repo root.
        Each line is {"type": "session_start"|"session_end", "scenario": "...", "pid": 12345,
        "wt_path": "/tmp/baadd-wt-...", "ts": 1700000000.0}.
        The dashboard reads sessions.jsonl to determine which worktrees are truly active.
        A worktree is ACTIVE if it has a session_start with no matching session_end
        (matched by wt_path) AND the session_start is less than SESSION_TIMEOUT seconds old (default 3600).
        A worktree is STALE if session_start is present but no session_end AND age > SESSION_TIMEOUT.
        A worktree is DONE if session_end is present.

        Scenario: evolve.sh appends session_start to sessions.jsonl when worktree is created
            Given evolve.sh has locked a scenario and created /tmp/baadd-wt-my-scenario-1234
            When the worktree is ready and the agent session is about to start
            Then sessions.jsonl in the main repo root contains a line with type "session_start",
                 wt_path "/tmp/baadd-wt-my-scenario-1234", and a numeric "ts" timestamp

        Scenario: evolve.sh appends session_end to sessions.jsonl on normal completion
            Given an evolve.sh session completed successfully and merged back to main
            When the cleanup section of evolve.sh runs
            Then sessions.jsonl contains a "session_end" line with the same wt_path as the session_start

        Scenario: evolve.sh appends session_end to sessions.jsonl on failure or early exit
            Given evolve.sh exits early (build fail, test fail, lock race, or unhandled error)
            When the EXIT trap fires (cleanup_worktree)
            Then sessions.jsonl contains a "session_end" line for the wt_path even on non-zero exit

        Scenario: orchestrate.py appends session_start per worker worktree it spawns
            Given orchestrate.py spawns 3 parallel evolve.sh workers, each with its own wt_path
            When each worker worktree is created
            Then sessions.jsonl contains 3 separate session_start lines with distinct wt_paths

        Scenario: orchestrate.py appends session_end for each worker when it finishes
            Given orchestrate.py has spawned 3 workers and they all complete
            When the last worker exits
            Then sessions.jsonl contains 3 session_end lines matching the 3 wt_paths

        Scenario: sessions.jsonl is created if it does not exist
            Given sessions.jsonl does not exist in the repo root
            When evolve.sh or orchestrate.py appends the first session_start
            Then sessions.jsonl is created with that one line — no error raised

        Scenario: sessions.jsonl append is atomic enough to avoid corruption under parallel writes
            Given 4 evolve.sh processes run simultaneously and all write session_start at the same moment
            When sessions.jsonl is read after all writes complete
            Then it contains exactly 4 valid JSON lines — no truncated or merged lines
            (Use a file lock via flock or Python's fcntl before each append)

        Scenario: read_sessions(sessions_path) returns list of dicts parsed from sessions.jsonl
            Given sessions.jsonl contains 5 valid JSON lines and 1 blank line
            When read_sessions(sessions_path) is called
            Then it returns a list of 5 dicts — blank lines are skipped, no exception raised

        Scenario: read_sessions returns empty list when sessions.jsonl does not exist
            Given sessions.jsonl is absent
            When read_sessions(sessions_path) is called
            Then it returns [] without raising FileNotFoundError

        Scenario: read_sessions skips malformed JSON lines without crashing
            Given sessions.jsonl contains 3 valid lines and 1 line that is not valid JSON
            When read_sessions(sessions_path) is called
            Then it returns 3 dicts — the bad line is silently skipped

        Scenario: active_wt_paths(sessions_path) returns only wt_paths with session_start and no session_end
            Given sessions.jsonl has: start(A), start(B), end(B)
            When active_wt_paths(sessions_path) is called
            Then it returns {"/tmp/baadd-wt-A-..."} only — B is excluded because it has session_end

        Scenario: active_wt_paths excludes sessions older than SESSION_TIMEOUT seconds
            Given a session_start with no session_end was written 4000 seconds ago (default timeout 3600)
            When active_wt_paths(sessions_path) is called
            Then that wt_path is NOT returned — it is treated as stale/orphaned

        Scenario: active_wt_paths handles duplicate session_start lines for the same wt_path
            Given sessions.jsonl has two session_start lines for the same wt_path (crash + restart)
            When active_wt_paths is called
            Then wt_path appears at most once in the result — the latest session_start is used

    Feature: Dashboard Worktree Staleness Filtering
        As a developer using the dashboard
        I want the dashboard to show only genuinely active worktrees
        So that completed or orphaned agents do not clutter the display

        discover_worktrees(main_dir) is updated to:
        1. Run "git worktree prune" before "git worktree list" to remove stale git refs
           where the /tmp directory no longer exists.
        2. Cross-reference results with active_wt_paths(sessions_path) from sessions.jsonl.
        3. Return only worktrees that appear in BOTH git worktree list AND active_wt_paths.

        Scenario: discover_worktrees runs git worktree prune before listing
            Given some /tmp/baadd-wt-* directories were deleted without running git worktree remove
            When discover_worktrees(main_dir) is called
            Then it first runs ["git", "-C", main_dir, "worktree", "prune"] before listing
            And stale worktree refs are removed from .git/worktrees/ before the list is read

        Scenario: discover_worktrees excludes worktrees absent from sessions.jsonl active set
            Given git worktree list shows /tmp/baadd-wt-old-scenario-99
            And sessions.jsonl has session_end for that wt_path
            When discover_worktrees(main_dir) is called
            Then /tmp/baadd-wt-old-scenario-99 is NOT in the result

        Scenario: discover_worktrees includes worktrees present in both git list and active set
            Given git worktree list shows /tmp/baadd-wt-new-scenario-42
            And sessions.jsonl has session_start with no session_end for that wt_path
            When discover_worktrees(main_dir) is called
            Then /tmp/baadd-wt-new-scenario-42 IS in the result

        Scenario: discover_worktrees falls back to git list only when sessions.jsonl is absent
            Given sessions.jsonl does not exist (fresh install, pre-lifecycle-feature runs)
            When discover_worktrees(main_dir) is called
            Then it returns all /tmp/baadd-wt-* paths from git worktree list with no filtering
            And does not raise an exception

        Scenario: discover_worktrees excludes worktrees whose /tmp directory no longer exists on disk
            Given git worktree list still shows /tmp/baadd-wt-vanished-55 after prune fails to remove it
            When discover_worktrees(main_dir) is called
            Then it checks os.path.isdir(wt_path) and excludes paths where the directory is gone

        Scenario: discover_worktrees treats stale sessions (no session_end, age > SESSION_TIMEOUT) as inactive
            Given sessions.jsonl has session_start for /tmp/baadd-wt-hung-77 written 2 hours ago
            And no session_end for that wt_path
            And the /tmp/baadd-wt-hung-77 directory still exists
            When discover_worktrees(main_dir) is called
            Then /tmp/baadd-wt-hung-77 is NOT returned — it is considered orphaned

        Scenario: discover_worktrees returns empty list when git worktree prune itself raises OSError
            Given git is not installed or the subprocess call raises OSError during prune
            When discover_worktrees(main_dir) is called
            Then it returns [] without crashing — the prune failure is silently swallowed

        Scenario: discover_worktrees returns consistent results under concurrent calls
            Given two dashboard poll cycles call discover_worktrees simultaneously
            When both calls read sessions.jsonl at the same time (one is mid-write)
            Then each call returns a valid list — no exception from partial JSON read

        Scenario: discover_worktrees excludes worktrees with session_end written within the last 2 seconds
            Given session_end was written 1 second ago for /tmp/baadd-wt-just-done-88
            When discover_worktrees(main_dir) is called
            Then /tmp/baadd-wt-just-done-88 is NOT returned — session_end presence is sufficient to exclude

        Scenario: git worktree prune is skipped when main_dir is not a git repository
            Given main_dir is a path that is not inside a git repository
            When discover_worktrees(main_dir) is called
            Then it skips the prune step, returns [], and does not raise CalledProcessError

    Feature: Dashboard BTOP-Style Responsive Layout
        As a developer monitoring agents
        I want the dashboard to arrange panels in a multi-column grid that adapts to terminal width
        So that wide terminals show more agents at a glance like BTOP does

        The layout uses rich.layout.Layout for the outer frame:
          - "header" row: fixed height 3, spans full width
          - "body" row: flexible height, contains the agent grid
          - "log" row: fixed height 10
          - "statusbar" row: fixed height 1
        The agent grid inside "body" uses rich.columns.Columns with equal=True and expand=True.
        Column count: terminal_width >= 240 → 3 cols; >= 160 → 2 cols; < 160 → 1 col.
        The Layout object is passed directly to rich.live.Live instead of a Group.

        Scenario: build_layout() returns a rich.layout.Layout with header, body, log, statusbar sections
            Given build_layout() is called
            When the returned object is inspected
            Then it is an instance of rich.layout.Layout
            And it contains named sections: "header", "body", "log", "statusbar"

        Scenario: agent grid uses 1 column when terminal width is less than 160
            Given Console().width returns 120
            When build_agent_grid(states, terminal_width=120) is called
            Then it returns a rich.columns.Columns with 1 column worth of panels (one panel per row)

        Scenario: agent grid uses 2 columns when terminal width is 160 to 239
            Given Console().width returns 180
            When build_agent_grid(states, terminal_width=180) is called with 4 AgentState objects
            Then it returns a rich.columns.Columns with equal=True containing 4 panels arranged 2-per-row

        Scenario: agent grid uses 3 columns when terminal width is 240 or more
            Given Console().width returns 260
            When build_agent_grid(states, terminal_width=260) is called with 6 AgentState objects
            Then it returns a rich.columns.Columns with equal=True containing 6 panels arranged 3-per-row

        Scenario: build_renderable updates Layout sections instead of returning a Group
            Given build_renderable(states, log_buffer, session_start_ts, layout, terminal_width) is called
            When the layout sections are inspected after the call
            Then layout["header"].update(...) was called with a Panel
            And layout["body"].update(...) was called with the agent grid
            And layout["log"].update(...) was called with a Panel
            And layout["statusbar"].update(...) was called with a Text

        Scenario: Layout degrades to single-column Group when rich.layout.Layout raises NotImplementedError
            Given rich.layout.Layout instantiation raises NotImplementedError (older Rich version)
            When build_renderable is called
            Then it falls back to building a rich.console.Group as before — no crash

        Scenario: Column count recalculates on every poll when terminal is resized
            Given terminal width was 200 (2 cols) on poll N
            And terminal width changes to 120 (1 col) on poll N+1
            When build_renderable is called on poll N+1
            Then the agent grid switches to 1 column — no restart required

        Scenario: Empty agent list renders body section as a centered "waiting for agents" Panel
            Given states = []
            When build_agent_grid([], terminal_width=180) is called
            Then it returns a Panel containing "waiting for agents" text — not an empty Columns

        Scenario: Single agent fills full width regardless of column threshold
            Given states has exactly 1 AgentState and terminal_width=260
            When build_agent_grid(states, terminal_width=260) is called
            Then the single panel expands to full width — not a narrow 1/3 column

    Feature: Dashboard Token Sparklines
        As a developer monitoring agent progress
        I want a sparkline graph of token usage per iteration inside each agent panel
        So that I can see acceleration or stalling at a glance like BTOP's graphs

        Sparklines use the 8-level block characters: ▁▂▃▄▅▆▇█
        AgentState gains a token_history field: collections.deque(maxlen=60) of int (tokens per iteration).
        read_wt_state populates token_history from api_response events (output_tokens per iteration).
        render_sparkline(history, width) returns a plain string of exactly `width` block characters.
        The mapping: value maps to one of 8 chars based on its position in [min(history), max(history)].
        When history has fewer points than width, the sparkline is right-aligned (left-padded with spaces).

        Scenario: AgentState has a token_history field that is a deque with maxlen=60
            Given a freshly constructed AgentState
            When token_history is inspected
            Then it is a collections.deque with maxlen=60 and initial length 0

        Scenario: read_wt_state populates token_history from api_response events
            Given a JSONL file with api_response events having output_tokens 100, 200, 150
            When read_wt_state(wt_path) is called
            Then state.token_history == deque([100, 200, 150])

        Scenario: render_sparkline maps values to 8 block characters by percentile bucket
            Given history = deque([0, 10, 20, 30, 40, 50, 60, 70])
            When render_sparkline(history, width=8) is called
            Then it returns "▁▂▃▄▅▆▇█" — each value maps to the corresponding level

        Scenario: render_sparkline returns a string of exactly `width` characters
            Given history = deque([50, 100, 75]) and width = 20
            When render_sparkline(history, width=20) is called
            Then len(result) == 20 exactly

        Scenario: render_sparkline right-aligns when history has fewer points than width
            Given history = deque([80, 90]) and width = 10
            When render_sparkline(history, width=10) is called
            Then result starts with 8 spaces and ends with 2 block chars (e.g. "        ▆█")

        Scenario: render_sparkline returns all "▁" when all values are equal (flat line)
            Given history = deque([500, 500, 500, 500])
            When render_sparkline(history, width=4) is called
            Then result == "▁▁▁▁" — all values map to the lowest level when range is zero

        Scenario: render_sparkline returns width spaces when history is empty
            Given history = deque([]) and width = 10
            When render_sparkline(history, width=10) is called
            Then result == "          " (10 spaces) — no exception

        Scenario: render_sparkline truncates to rightmost `width` points when history is longer than width
            Given history = deque([1,2,3,4,5,6,7,8,9,10]) and width = 5
            When render_sparkline(history, width=5) is called
            Then it uses only the last 5 values [6,7,8,9,10] — oldest points are dropped

        Scenario: build_agent_panel includes the sparkline string inside the panel body
            Given state.token_history = deque([100, 200, 300]) and panel width is 40
            When build_agent_panel(state, panel_width=40) is called
            Then the panel body contains a line of block characters from render_sparkline

        Scenario: sparkline line in agent panel is labelled "tok/iter" to explain the graph
            Given a valid AgentState with non-empty token_history
            When build_agent_panel(state) is called
            Then the panel body contains "tok/iter" adjacent to or above the sparkline characters

        Scenario: render_sparkline handles a single-element history without IndexError
            Given history = deque([42]) and width = 5
            When render_sparkline(history, width=5) is called
            Then it returns "    ▁" (4 spaces + lowest block char) — no crash

    Feature: Dashboard Gradient Progress Bars
        As a developer monitoring agent iteration progress
        I want progress bars that change color from green to red as iterations are consumed
        So that I can spot agents approaching their limit at a glance like BTOP's CPU bars

        render_gradient_bar(current, max_val, width) returns a Rich markup string (not plain text).
        Color thresholds (by percentage of max_val used):
          0–49%  → [green]█[/green]  for filled chars
          50–74% → [yellow]█[/yellow]
          75–89% → [red]█[/red]
          90–100%→ [bold red]█[/bold red]
        Empty chars remain plain "░" (no color markup).
        The function returns a string suitable for use inside rich.text.Text.from_markup().

        Scenario: render_gradient_bar returns green-marked filled chars at 0 percent used
            Given current=0, max_val=100, width=10
            When render_gradient_bar(0, 100, 10) is called
            Then result == "░░░░░░░░░░" (all empty, no markup needed)

        Scenario: render_gradient_bar returns green markup at 30 percent used
            Given current=30, max_val=100, width=10
            When render_gradient_bar(30, 100, 10) is called
            Then the filled portion uses "[green]█[/green]" markup (3 filled green + 7 empty)

        Scenario: render_gradient_bar switches to yellow markup at 50 percent used
            Given current=50, max_val=100, width=10
            When render_gradient_bar(50, 100, 10) is called
            Then the filled portion uses "[yellow]█[/yellow]" markup (5 filled yellow + 5 empty)

        Scenario: render_gradient_bar switches to red markup at 75 percent used
            Given current=75, max_val=100, width=10
            When render_gradient_bar(75, 100, 10) is called
            Then the filled portion uses "[red]█[/red]" markup (7-8 filled red + 2-3 empty)

        Scenario: render_gradient_bar switches to bold red markup at 90 percent used
            Given current=90, max_val=100, width=10
            When render_gradient_bar(90, 100, 10) is called
            Then the filled portion uses "[bold red]█[/bold red]" markup (9 filled bold-red + 1 empty)

        Scenario: render_gradient_bar returns fully filled bold-red bar at 100 percent
            Given current=100, max_val=100, width=10
            When render_gradient_bar(100, 100, 10) is called
            Then result is 10 "[bold red]█[/bold red]" chars — no empty chars

        Scenario: render_gradient_bar result is exactly width visible characters when markup is stripped
            Given current=60, max_val=100, width=20
            When render_gradient_bar(60, 100, 20) is called
            Then rich.markup.strip_markup(result) has length 20 — markup tags do not count toward width

        Scenario: render_gradient_bar does not raise ZeroDivisionError when max_val is 0
            Given current=0, max_val=0, width=10
            When render_gradient_bar(0, 0, 10) is called
            Then it returns "░░░░░░░░░░" without raising ZeroDivisionError

        Scenario: render_gradient_bar clamps filled chars to width when current exceeds max_val
            Given current=150, max_val=100, width=10
            When render_gradient_bar(150, 100, 10) is called
            Then visible chars == 10 filled "[bold red]█[/bold red]" — no overflow or exception

        Scenario: build_agent_panel uses render_gradient_bar instead of plain render_progress_bar
            Given a valid AgentState with current_iter=80 and max_iter=100
            When build_agent_panel(state) is called
            Then the panel body contains "[red]" or "[bold red]" markup — confirming gradient bar is used

    Feature: Dashboard Status Bar
        As a developer monitoring agents
        I want a one-line status bar at the bottom of the dashboard
        So that key stats and keybindings are always visible like BTOP's footer

        build_status_bar(states, session_start_ts, terminal_width) returns a rich.text.Text object.
        Content (left-aligned, space-padded to terminal_width):
          "  q:quit  r:refresh  ↑↓:scroll log  │  agents: N  │  tok: X,XXX  │  up: Xm Xs  "
        Where N = len(states), X,XXX = sum of state.tokens for all states,
        and "up: Xm Xs" = formatted time since session_start_ts.
        The status bar background is styled with "reverse" (Rich's reverse-video style).

        Scenario: build_status_bar returns a rich.text.Text object
            Given any valid inputs
            When build_status_bar(states, session_start_ts, terminal_width=80) is called
            Then isinstance(result, rich.text.Text) is True

        Scenario: build_status_bar shows correct agent count
            Given 3 AgentState objects
            When build_status_bar(states, session_start_ts, terminal_width=120) is called
            Then the text contains "agents: 3"

        Scenario: build_status_bar shows summed token count across all agents
            Given states with token counts 1000, 2500, 750 (sum=4250)
            When build_status_bar(states, session_start_ts, terminal_width=120) is called
            Then the text contains "tok: 4,250"

        Scenario: build_status_bar shows session uptime in Xm Xs format
            Given session_start_ts = time.time() - 125 (2 minutes 5 seconds ago)
            When build_status_bar(states, session_start_ts, terminal_width=120) is called
            Then the text contains "up: 2m05s"

        Scenario: build_status_bar contains all four keybinding hints
            Given any valid inputs
            When build_status_bar(states, session_start_ts, terminal_width=120) is called
            Then the text contains "q:quit", "r:refresh", "↑↓:scroll log"

        Scenario: build_status_bar text is padded to exactly terminal_width characters
            Given terminal_width=100
            When build_status_bar([], session_start_ts, terminal_width=100) is called
            Then len(result.plain) == 100 (padded with spaces on the right)

        Scenario: build_status_bar uses reverse-video style for background
            Given any valid inputs
            When build_status_bar(states, session_start_ts, terminal_width=80) is called
            Then result._spans contain a style with "reverse" applied to the full text

        Scenario: build_status_bar shows "agents: 0" when states is empty
            Given states = []
            When build_status_bar([], session_start_ts, terminal_width=80) is called
            Then text contains "agents: 0" and "tok: 0"

        Scenario: build_status_bar does not raise when terminal_width is 0 or 1
            Given terminal_width=0 or terminal_width=1
            When build_status_bar([], session_start_ts, terminal_width) is called
            Then it returns a Text object without raising — content may be truncated

    Feature: Dashboard Keyboard Input
        As a developer using the dashboard
        I want to control the dashboard with keyboard shortcuts without freezing the display
        So that I can quit, force-refresh, or scroll without waiting for the next poll cycle

        Keyboard input is handled by a background daemon thread started in main().
        The thread uses sys.stdin, termios, and tty (all Python stdlib — not TUI libraries).
        It sets the terminal to raw mode (tty.setraw), reads one byte at a time, and puts
        keystrokes into a queue.Queue. The main Live loop drains the queue each cycle.
        On exit (KeyboardInterrupt or q), the thread restores the original terminal settings
        via termios.tcsetattr before the process terminates.

        Scenario: keyboard_input_thread is a daemon thread started in main()
            Given scripts/dashboard.py is read
            When the main() function body is inspected
            Then it starts a threading.Thread(target=keyboard_input_thread, daemon=True)
            before entering the rich.live.Live context

        Scenario: pressing q puts "q" into the key_queue
            Given keyboard_input_thread is running and the terminal is in raw mode
            When the user presses the "q" key (byte 0x71)
            Then "q" is placed into the shared queue.Queue

        Scenario: main loop reads q from key_queue and exits the Live loop
            Given key_queue.get_nowait() returns "q"
            When the main Live loop drains the queue
            Then it breaks out of the polling loop and exits cleanly (exit code 0)

        Scenario: pressing r puts "r" into the key_queue and triggers immediate refresh
            Given key_queue.get_nowait() returns "r"
            When the main Live loop drains the queue
            Then it calls live.update(build_renderable(...)) immediately without waiting for the next poll interval

        Scenario: pressing up-arrow puts "up" into the key_queue
            Given the terminal sends the ANSI escape sequence ESC [ A for up-arrow
            When keyboard_input_thread reads those 3 bytes
            Then it puts the string "up" into the key_queue as a single logical keystroke

        Scenario: pressing down-arrow puts "down" into the key_queue
            Given the terminal sends ESC [ B for down-arrow
            When keyboard_input_thread reads those 3 bytes
            Then it puts "down" into the key_queue

        Scenario: up-arrow increments log_scroll_offset by 1
            Given log_scroll_offset = 3 and key_queue yields "up"
            When the main loop drains the queue
            Then log_scroll_offset becomes 4

        Scenario: down-arrow decrements log_scroll_offset by 1 but not below 0
            Given log_scroll_offset = 1 and key_queue yields "down"
            When the main loop drains the queue
            Then log_scroll_offset becomes 0

        Scenario: down-arrow at offset 0 does not go negative
            Given log_scroll_offset = 0 and key_queue yields "down"
            When the main loop drains the queue
            Then log_scroll_offset remains 0 — no underflow

        Scenario: keyboard_input_thread restores terminal settings on exit
            Given keyboard_input_thread has set the terminal to raw mode
            When the thread exits (because main() sets a stop event)
            Then termios.tcsetattr is called with the original settings before the thread returns

        Scenario: keyboard_input_thread does not crash when stdin is not a tty (e.g. CI pipe)
            Given sys.stdin.fileno() raises io.UnsupportedOperation (stdin is a pipe)
            When keyboard_input_thread starts
            Then it exits silently without setting raw mode or raising — keyboard input is simply disabled

        Scenario: key_queue is bounded (maxsize=32) to prevent unbounded growth if keys are ignored
            Given scripts/dashboard.py is read
            When the key_queue instantiation is inspected
            Then queue.Queue(maxsize=32) is used — not an unbounded Queue()

        Scenario: multiple queued keystrokes are all drained in a single poll cycle
            Given key_queue contains ["up", "up", "r"] before the poll fires
            When the main loop drains the queue
            Then all three are processed — offset increases by 2 and a refresh is triggered

    Feature: Dashboard Log Panel Scrolling
        As a developer monitoring agents
        I want to scroll the log panel up to see older output without losing the live display
        So that I can review recent decisions without quitting like BTOP's process list

        The log panel shows the last LOG_HEIGHT lines of log_buffer by default (auto-scroll).
        LOG_HEIGHT defaults to 8. log_scroll_offset=0 means show the most recent lines.
        log_scroll_offset=N means show lines ending N lines before the most recent.
        Auto-scroll is suspended when log_scroll_offset > 0.
        Auto-scroll resumes when log_scroll_offset reaches 0 again.
        format_log_strip(log_buffer, height, scroll_offset) returns a string of exactly `height` lines.

        Scenario: format_log_strip with scroll_offset=0 returns the last `height` lines of log_buffer
            Given log_buffer has 20 lines numbered 1–20 and height=8, scroll_offset=0
            When format_log_strip(log_buffer, height=8, scroll_offset=0) is called
            Then the returned string contains lines 13–20 (the 8 most recent)

        Scenario: format_log_strip with scroll_offset=5 returns lines shifted 5 back from the end
            Given log_buffer has 20 lines numbered 1–20 and height=8, scroll_offset=5
            When format_log_strip(log_buffer, height=8, scroll_offset=5) is called
            Then the returned string contains lines 8–15 (shifted 5 earlier)

        Scenario: format_log_strip clamps scroll_offset so it never scrolls before the first line
            Given log_buffer has 10 lines and height=8, scroll_offset=100
            When format_log_strip(log_buffer, height=8, scroll_offset=100) is called
            Then the returned string contains lines 1–8 (clamped at buffer start) — no IndexError

        Scenario: format_log_strip pads with empty lines when log_buffer has fewer than height lines
            Given log_buffer has 3 lines and height=8, scroll_offset=0
            When format_log_strip(log_buffer, height=8, scroll_offset=0) is called
            Then the returned string contains 3 content lines and 5 empty lines — total height=8

        Scenario: log Panel title shows scroll position indicator when scroll_offset > 0
            Given log_scroll_offset = 4
            When the log Panel is built with that offset
            Then the panel title contains "↑4" or "↑ 4 more" — indicating lines above the current view

        Scenario: log Panel title shows "AUTO" or no indicator when scroll_offset is 0
            Given log_scroll_offset = 0
            When the log Panel is built
            Then the panel title does NOT contain "↑" — indicating auto-scroll mode is active

        Scenario: new log lines do not auto-scroll when scroll_offset > 0
            Given log_scroll_offset = 3 and a new line is appended to log_buffer
            When build_renderable is called on the next poll
            Then log_scroll_offset remains 3 — the view does not jump to the bottom

        Scenario: new log lines DO auto-scroll when scroll_offset is 0
            Given log_scroll_offset = 0 and a new line is appended to log_buffer
            When build_renderable is called on the next poll
            Then the log panel shows the newest line at the bottom — scroll_offset stays 0

        Scenario: scroll up beyond buffer start is clamped and does not raise IndexError
            Given log_buffer has 5 lines and log_scroll_offset = 4
            When the user presses up-arrow again (would make offset=5)
            Then log_scroll_offset is clamped to max(0, len(log_buffer) - LOG_HEIGHT)
            And format_log_strip does not raise IndexError

        Scenario: format_log_strip returns placeholder when log_buffer is empty regardless of scroll_offset
            Given log_buffer = deque([]) and scroll_offset = 0
            When format_log_strip(log_buffer, height=8, scroll_offset=0) is called
            Then it returns a non-empty placeholder string (e.g. "(waiting for orchestrator output...)")
    Feature: Pluggable Agent Harness
        As a developer running poppins against a local model
        I want to choose which agent harness runs each session
        So that I can use hermes-agent instead of the built-in agent loop

        Scenario: Native harness is used by default
            Given neither AGENT_HARNESS nor POPPINS_AGENT_HARNESS is set
            When scripts/run_agent.sh is run
            Then it runs scripts/agent.py with the same arguments and stdin

        Scenario: Hermes harness passes the prompt as a one-shot query
            Given AGENT_HARNESS is "hermes" and HERMES_CMD points to an installed hermes
            And MODEL is "gemma-4-26b-a4b-it" and HERMES_BASE_URL is "http://llm.local:1234/v1"
            When scripts/run_agent.sh is run with the prompt "do the thing" on stdin
            Then hermes is invoked with: chat -q "do the thing" --oneshot --max-turns 75 --model gemma-4-26b-a4b-it --base-url http://llm.local:1234/v1

        Scenario: Hermes harness uses poppins.yml max_iterations as max turns
            Given AGENT_HARNESS is "hermes" and POPPINS_AGENT_MAX_ITERATIONS is "40"
            When scripts/run_agent.sh is run
            Then hermes is invoked with --max-turns 40

        Scenario: Hermes harness reports an error when hermes is not installed
            Given AGENT_HARNESS is "hermes" and HERMES_CMD names a command that does not exist
            When scripts/run_agent.sh is run
            Then it prints a JSON line with "type":"error"
            And it exits non-zero

        Scenario: Unknown harness reports an error
            Given AGENT_HARNESS is "bogus"
            When scripts/run_agent.sh is run
            Then it prints a JSON line with "type":"error" naming "bogus"
            And it exits non-zero

        Scenario: evolve.sh runs every agent session through run_agent.sh
            Given scripts/evolve.sh
            Then it never invokes scripts/agent.py directly
            And every agent session goes through scripts/run_agent.sh

    Feature: Kotlin Test Discovery
        As a developer building a Kotlin project with poppins
        I want Kotlin tests to count toward BDD coverage
        So that Kotlin scenarios are marked covered

        Scenario: Kotlin test files are found
            Given files src/test/kotlin/RoomsTest.kt and src/main/kotlin/Rooms.kt
            When find_test_files is called
            Then src/test/kotlin/RoomsTest.kt is returned
            And src/main/kotlin/Rooms.kt is not returned

        Scenario: Kotlin files under build output are ignored
            Given a file build/generated/test/FooTest.kt
            When find_test_files is called
            Then it is not returned
