# BDD Status

Checked 347 scenario(s) across 57 test file(s).


## Feature: BDD Specification Parser

- [x] Parse YAML frontmatter from BDD.md
- [x] Handle missing frontmatter gracefully
- [x] Parse frontmatter with quoted values
- [x] Extract all scenarios from BDD.md
- [x] Parse scenario outline syntax
- [x] Skip frontmatter when parsing scenarios

## Feature: Test Coverage Detection

- [x] Find test files in project
- [x] Exclude non-source directories from test search
- [x] Detect coverage via BDD marker comment
- [x] Detect coverage via marker with different comment style
- [x] Detect coverage via heuristic name matching
- [x] Detect coverage via partial name matching
- [x] Report uncovered scenarios
- [x] Exit with error code when scenarios uncovered
- [x] Exit with success when all scenarios covered
- [x] Handle empty BDD.md with no scenarios
- [x] Handle BDD.md with only frontmatter

## Feature: Multi-Provider AI Agent

- [x] Detect Anthropic provider from API key
- [x] Detect OpenAI provider from API key
- [x] Detect Groq provider from API key
- [x] Detect Ollama provider from localhost probe
- [x] Detect custom provider from base URL
- [x] Provider priority order
- [x] Use provider default model
- [x] Override model via MODEL environment variable
- [x] Load provider config from poppins.yml
- [x] Environment variables override poppins.yml config
- [x] Set OLLAMA_HOST from poppins.yml base_url
- [x] No provider detected error message
- [x] CUSTOM_MODEL required for custom provider without --model
- [x] Unknown provider error
- [x] Override provider via --provider flag
- [x] Missing anthropic package error
- [x] Missing openai package error
- [x] Empty stdin prompt error
- [x] Load skills from SKILL.md files
- [x] Skills appended to system prompt
- [x] Skip skills loading if directory missing
- [x] Custom event log path via --event-log

## Feature: Agent Tool Execution

- [x] Run bash command and capture output
- [x] Run bash command with stderr
- [x] Bash command timeout after 300 seconds
- [x] Read file that exists
- [x] Read file that does not exist
- [x] Truncate long file output
- [x] Write file creates parent directories
- [x] Edit file replaces exact string
- [x] Edit file fails when string not found
- [x] Edit file replaces only first occurrence
- [x] List files excludes git and node_modules
- [x] Search files finds pattern
- [x] Search files handles no matches

## Feature: Agent Loop and Iteration Management

- [x] Agent stops at max iterations
- [x] Wrap-up reminder injected at threshold
- [x] Wrap-up reminder content for evolve mode
- [x] Wrap-up reminder content for bootstrap mode
- [x] Session ends on end_turn stop reason

## Feature: Context Window Management

- [x] Estimate tokens from text
- [x] Trim context when exceeding limit
- [x] Preserve recent messages during trim
- [x] Trim only tool result content

## Feature: Event Logging

- [x] Log session start with provider and model
- [x] Log tool call with input preview
- [x] Log tool result with duration
- [x] Log token usage per API response
- [x] Log session end with reason

## Feature: Poppins Configuration Parser

- [x] Parse poppins.yml with agent section
- [x] Apply defaults when poppins.yml missing
- [x] Deep merge file config with defaults
- [x] Default max_rounds is 1
- [x] Get single config value via dot notation
- [x] Search parent directories for poppins.yml

## Feature: GitHub Issue Trust Verification

- [x] Trust repo owner's issues directly
- [x] Trust community issue with agent-approved label from owner
- [x] Reject community issue with agent-approved from non-owner
- [x] Verify label applier via GitHub events API

## Feature: Issue Formatting for Agent

- [x] Format issue as markdown
- [x] Truncate long issue body
- [x] Sort issues by reaction count
- [x] Mark user content with boundaries
- [x] Warn about untrusted content

## Feature: Bootstrap Script

- [x] Scaffold TypeScript React project
- [x] Scaffold Python project
- [x] Scaffold Rust project
- [x] Create CI workflow for TypeScript
- [x] Create CI workflow for Python
- [x] Verify build passes before marking initialized
- [x] Create Day 0 journal entry
- [x] Write fallback journal if agent skips
- [x] Seed journal index on bootstrap

## Feature: Evolution Script

- [x] Load BDD config before session
- [x] Check starting build state
- [x] Continue with failing tests
- [x] Exit if build broken at start
- [x] Fetch trusted GitHub issues
- [x] Generate issues file for agent
- [x] Pre-compute coverage before session
- [x] Detect test-only anti-pattern
- [x] Retry fix on build failure
- [x] Revert session on persistent failure
- [x] Write journal if agent skipped
- [x] Write fallback journal if agent still skips
- [x] Update journal index after session
- [x] Comment and close implemented issues
- [x] Push changes after session
- [x] Track session start SHA for rollback
- [x] Exclude management files from worktree commits
- [x] Branch naming convention with timestamp
- [x] Calculate has_work flag
- [x] Guard warning for minimal work with uncovered scenarios
- [x] Handle push failure gracefully
- [x] Handle missing git remote

## Feature: Scenario Locking for Parallel Execution

- [x] Generate scenario slug from name
- [x] Slug truncates to 60 characters
- [x] Check for existing lock file
- [x] Detect stale lock from dead PID
- [x] Write lock file with session metadata
- [x] Release lock on completion
- [x] Clean up lock on early exit

## Feature: Git Worktree Isolation

- [x] Create worktree for scenario
- [x] Copy runtime files to worktree
- [x] Merge successful worktree to main
- [x] Auto-resolve management file conflicts
- [x] Fold JOURNAL_ENTRY.md into JOURNAL.md
- [x] Clean up worktree after merge
- [x] Remove worktree on failure

## Feature: Parallel Agent Orchestration

- [x] Find uncovered scenarios for orchestration
- [x] AI-powered scenario ordering
- [x] Fallback to BDD.md order on AI failure
- [x] Select top N scenarios for parallel run
- [x] Create worktrees for parallel scenarios
- [x] Run agents in parallel with ThreadPoolExecutor
- [x] Stream agent output with scenario prefix
- [x] Merge results in planned order
- [x] Track total agent time across workers
- [x] Deferred scenarios message
- [x] Read max_rounds from poppins.yml
- [x] Run orchestrator N rounds sequentially
- [x] Override max rounds via CLI
- [x] Write orchestrator event log
- [x] Write orchestrator journal entry
- [x] Override max parallel agents via CLI
- [x] Dry run mode shows plan without execution
- [x] Custom BDD.md path via --bdd flag
- [x] Override orchestrator planning model
- [x] Force orchestrator provider via CLI
- [x] Worker result structure
- [x] Status indicators for worker output
- [x] Worker with no commits shows fail status
- [x] Worker with failing tests shows warning

## Feature: Setup Environment Script

- [x] Setup Rust toolchain
- [x] Setup Node dependencies
- [x] Setup Python dependencies
- [x] Setup Go dependencies
- [x] Always install agent dependencies
- [x] Skip unknown language gracefully

## Feature: Add BDD Markers Utility

- [x] Detect comment prefix by file extension
- [x] Detect JavaScript comment prefix
- [x] Find test line matching scenario
- [x] Insert marker above test function
- [x] Skip if marker already exists
- [x] Dry run mode shows planned changes
- [x] Apply mode modifies files

## Feature: Dotenv Loading

- [x] Load .env file into environment
- [x] Handle quoted values in .env
- [x] Skip comment lines in .env
- [x] Environment variables override .env

## Feature: CI/CD Integration

- [x] GitHub Actions workflow triggers on schedule
- [x] Manual workflow dispatch
- [x] Bootstrap detection in workflow
- [x] Workflow timeout limit
- [x] Retry after first attempt failure
- [x] Retry after second attempt failure
- [x] Configure git bot identity
- [x] GitHub Actions log grouping
- [x] Detect CI environment
- [x] Release workflow on version tag
- [x] Release includes install.sh
- [x] Docs workflow triggers on docs path change
- [x] Docs deployment to GitHub Pages

## Feature: Install Script

- [x] Init new baadd project
- [ ] UNCOVERED: Update existing baadd project
- [ ] UNCOVERED: Auto-detect update mode
- [ ] UNCOVERED: Pin to specific version
- [ ] UNCOVERED: Fetch latest version from GitHub API
- [ ] UNCOVERED: Skip no-clobber files on update
- [ ] UNCOVERED: Archive journals before update
- [ ] UNCOVERED: Create BDD.md from template
- [x] Init git repo if missing
- [ ] UNCOVERED: Create locks directory
- [ ] UNCOVERED: Read manifest file list
- [ ] UNCOVERED: Stamp version in manifest
- [ ] UNCOVERED: Already on target version skips update
- [ ] UNCOVERED: Set executable permissions on scripts
- [ ] UNCOVERED: Download file creates parent directories

## Feature: Identity and Safety Rules

- [ ] UNCOVERED: Never modify IDENTITY.md
- [ ] UNCOVERED: Never modify scripts/evolve.sh
- [ ] UNCOVERED: Never modify .github/workflows/
- [ ] UNCOVERED: Only build features from BDD.md
- [x] Never delete tests

## Feature: Error Recovery

- [ ] UNCOVERED: API error causes retry exit
- [ ] UNCOVERED: Post-merge verification catches breakage
- [ ] UNCOVERED: Timeout kills long session
- [x] Handle missing gh CLI gracefully
- [ ] UNCOVERED: Worktree creation failure
- [x] Handle test file that cannot be read
- [ ] UNCOVERED: Tool output formatting with iteration tag
- [ ] UNCOVERED: Tool icons for different tool types
- [x] Detect Moonshot provider
- [x] Detect Dashscope provider
- [ ] UNCOVERED: Moonshot default model
- [ ] UNCOVERED: Dashscope default model
- [ ] UNCOVERED: Groq default model
- [ ] UNCOVERED: Ollama default model
- [ ] UNCOVERED: Custom provider requires api_key string placeholder
- [ ] UNCOVERED: Ollama provider uses "ollama" as api_key
- [ ] UNCOVERED: Mode flag affects wrap-up message content
- [x] Bootstrap mode agent prompt
- [ ] UNCOVERED: Handle scenario with special characters in name
- [ ] UNCOVERED: Handle concurrent scenario locks
- [x] Issue response file format parsing

## Feature: Dashboard — scripts/dashboard.py (Python, Rich TUI)

- [x] Dashboard file exists at scripts/dashboard.py
- [x] Rich is the only third-party import in dashboard.py
- [x] Running "python3 scripts/dashboard.py" opens the Rich TUI immediately
- [x] The dashboard is only for scripts/orchestrate.py — not evolve.sh or agent.py
- [x] dashboard.py defines a main() function called from __main__
- [x] Live refresh loop uses rich.live.Live with refresh_per_second
- [x] Each agent is rendered as a rich.panel.Panel
- [x] Overall renderable is a rich.console.Group of Panels stacked vertically

## Feature: Dashboard Worktree Discovery

- [x] discover_worktrees returns baadd worktree paths from git worktree list output
- [x] discover_worktrees excludes the main worktree
- [x] discover_worktrees returns empty list when no baadd worktrees exist
- [x] discover_worktrees returns empty list when git command fails
- [x] slug_to_name converts hyphenated path slug to display name
- [x] slug_to_name handles path with no trailing digits
- [x] resolve_display_name prefers explicit wt_map entry over slug
- [x] resolve_display_name falls back to slug_to_name when path not in wt_map

## Feature: JSONL Event Log Reading

- [x] read_wt_state reads current_iter as the highest iteration value seen in iteration_start events
- [x] read_wt_state reads max_iter from the max_iterations field of iteration_start events
- [x] read_wt_state sets active_phase to the label of the most recent phase lacking session_end
- [x] read_wt_state adds a phase label to done_phases when its log contains session_end
- [x] read_wt_state returns done_phases in fixed pipeline order PM-PLAN SE TESTER ACCEPT
- [x] read_wt_state reads tokens as the highest cumulative_output_tokens seen in api_response events
- [x] read_wt_state reads start_ts as a float epoch from the ts field of the session_start event
- [x] read_wt_state collects the 3 most recent tool_call events from the active phase log as last_tools
- [x] read_wt_state skips malformed JSON lines and continues reading
- [x] read_wt_state returns zeroed AgentState when no JSONL files exist in worktree
- [x] read_wt_state picks the JSONL file with the highest mtime when multiple files share the same phase prefix
- [x] read_wt_state handles OSError when opening a JSONL file
- [x] read_wt_state sets start_ts to current time when no session_start event exists

## Feature: AgentState Dataclass

- [x] AgentState is a dataclass with the required fields
- [x] AgentState.elapsed_s property returns seconds since start_ts
- [x] AgentState.is_stale property returns True when newest JSONL mtime is over 120 seconds old
- [x] AgentState.is_stale returns False when any JSONL file was modified within 120 seconds
- [x] AgentState.is_stale returns False when worktree has no JSONL files yet
- [x] AgentState.is_done returns True only when all four phase labels are in done_phases
- [x] AgentState.is_done returns False when fewer than four phases are done

## Feature: Tool Call Formatting

- [x] format_tool_call formats read_file as "r: <path>"
- [x] format_tool_call formats write_file as "w: <path>"
- [x] format_tool_call formats bash as "$ <command>" truncated to 60 chars
- [x] format_tool_call formats run_command identically to bash
- [x] format_tool_call formats edit_file as "e: <path>"
- [x] format_tool_call uses generic "tool: value" format for unknown tools
- [x] format_tool_call returns "r: ?" when path key is missing from input_dict for read_file
- [x] format_tool_call handles None input_dict without raising

## Feature: Log Line Filtering

- [x] is_log_noise returns True for TPS monitor lines matching "tok | X TPS |"
- [x] is_log_noise returns True for bracketed per-agent output lines
- [x] is_log_noise returns False for round banner lines starting with "==="
- [x] is_log_noise returns False for MERGED result lines
- [x] is_log_noise returns False for THROWN AWAY result lines
- [x] is_log_noise returns False for Pre-flight status lines
- [x] is_log_noise returns False for scenario-to-worktree mapping lines containing " → /tmp"
- [x] is_log_noise returns False for empty lines
- [x] parse_wt_mapping_line extracts scenario name and worktree path
- [x] parse_wt_mapping_line returns None for lines without " → /tmp"
- [x] parse_wt_mapping_line returns None for empty string
- [x] log buffer is a deque(maxlen=10) that automatically discards oldest entries

## Feature: Dashboard Rendering Functions

- [x] format_phase_line returns correct string for two done phases and one active phase
- [x] format_phase_line returns all checkmarks when all four phases are done
- [x] format_phase_line returns four dashes when nothing has started
- [x] format_phase_line shows active phase with iteration count
- [x] render_progress_bar returns a string of bar_width unicode chars using "█" and "░"
- [x] render_progress_bar fills correct proportion at 50 percent
- [x] render_progress_bar returns fully filled bar at 100 percent
- [x] render_progress_bar clamps fill at 100 percent when current_iter exceeds max_iter
- [x] render_progress_bar handles max_iter=0 without division-by-zero
- [x] format_metrics_line returns formatted tokens and TPS string
- [x] format_metrics_line returns dash when tokens is zero
- [x] format_metrics_line computes TPS as tokens divided by elapsed_s
- [x] format_metrics_line does not divide by zero when elapsed_s is 0
- [x] format_elapsed returns seconds string for durations under 60 seconds
- [x] format_elapsed returns minutes and zero-padded seconds for durations over 60 seconds
- [x] format_elapsed returns "0s" for zero elapsed time
- [x] build_agent_panel returns a rich.panel.Panel whose title is the scenario name
- [x] build_agent_panel appends "(stale)" to panel title when state.is_stale is True
- [x] build_agent_panel does not include "(stale)" when state.is_stale is False
- [x] format_header returns a string containing agent count and session elapsed time
- [x] format_header returns "waiting for agents" string when states list is empty
- [x] format_log_strip returns a string containing all lines from the log buffer
- [x] format_log_strip returns a placeholder string when log buffer is empty
- [x] build_renderable returns a rich.console.Group containing all agent panels plus header and log panels
- [x] build_renderable returns a Group with only header and log panels when states is empty

## Feature: Wrapper Mode

- [x] wrapper mode constructs the subprocess command as ["python3", "scripts/orchestrate.py"] plus forwarded args
- [x] wrapper mode passes all unrecognised args through to orchestrate.py unchanged
- [x] stdout reader thread calls is_log_noise on each line and only appends non-noise lines to log_buffer
- [x] stdout reader thread calls parse_wt_mapping_line and populates wt_map for matching lines
- [x] wrapper main loop calls sys.exit with orchestrate.py returncode when subprocess exits with 0
- [x] wrapper main loop calls sys.exit with orchestrate.py returncode when subprocess exits with 1
- [x] wrapper renders "waiting for agents" header when no worktrees exist yet
- [x] wrapper adds a new agent panel when a worktree appears between polls
- [x] wrapper mode raises RuntimeError and prints clear message when scripts/orchestrate.py does not exist

## Feature: Watcher Mode

- [x] --watch flag causes no subprocess to be started
- [x] watcher mode calls discover_worktrees on every poll iteration
- [x] watcher exits after two consecutive empty polls from discover_worktrees
- [x] watcher does not exit after a single empty poll
- [x] watcher prints "All agents done." to stdout after the Live context closes
- [x] watcher resolves scenario names from slug_to_name when no wt_map is available

## Feature: Dashboard CLI Arguments

- [x] parse_args returns watch=False and mode is wrapper when --watch is absent
- [x] parse_args returns watch=True when --watch flag is present
- [x] parse_args collects unrecognised flags into pass_args for forwarding
- [x] parse_args --refresh sets poll interval
- [x] parse_args default refresh interval is 2 seconds
- [x] --watch and --refresh can be combined with pass_args

## Feature: Dashboard Error Handling and Edge Cases

- [x] Missing rich package causes immediate error with install instruction
- [x] KeyboardInterrupt during Live loop exits cleanly without traceback
- [x] SIGTERM during wrapper mode terminates the subprocess before exiting
- [x] Worktree directory disappears between polls without crashing
- [x] glob finds no JSONL files in a worktree that exists but has not started yet
- [x] TPS calculation guards against division by zero when elapsed_s is 0
- [x] Very long scenario name is truncated in panel title to prevent wrapping
- [x] render_progress_bar always returns a string of exactly bar_width characters
- [x] Dashboard handles zero-width terminal gracefully
- [x] stdout reader thread sets a threading.Event when subprocess stdout is exhausted

## Feature: Merge Agent for Conflict Resolution

- [x] Merge agent detects merge conflicts
- [x] Merge agent combines imports from multiple scenarios
- [x] Merge agent preserves all test functions
- [ ] UNCOVERED: Merge agent inserts markers above test functions
- [ ] UNCOVERED: Merge agent handles duplicate markers
- [ ] UNCOVERED: Merge agent writes resolved file to staging
- [ ] UNCOVERED: Merge agent logs resolution decisions

## Feature: Integration Test Agent

- [x] Integration test agent runs full test suite
- [x] Integration test agent reports pass
- [x] Integration test agent reports fail
- [x] Integration test agent attempts fix on failure
- [ ] UNCOVERED: Integration test agent re-runs tests after fix
- [ ] UNCOVERED: Integration test agent fails session on persistent failure
- [ ] UNCOVERED: Integration test agent writes test result log

---
**308/347 scenarios covered.**

39 scenario(s) need tests:
- Update existing baadd project
- Auto-detect update mode
- Pin to specific version
- Fetch latest version from GitHub API
- Skip no-clobber files on update
- Archive journals before update
- Create BDD.md from template
- Create locks directory
- Read manifest file list
- Stamp version in manifest
- Already on target version skips update
- Set executable permissions on scripts
- Download file creates parent directories
- Never modify IDENTITY.md
- Never modify scripts/evolve.sh
- Never modify .github/workflows/
- Only build features from BDD.md
- API error causes retry exit
- Post-merge verification catches breakage
- Timeout kills long session
- Worktree creation failure
- Tool output formatting with iteration tag
- Tool icons for different tool types
- Moonshot default model
- Dashscope default model
- Groq default model
- Ollama default model
- Custom provider requires api_key string placeholder
- Ollama provider uses "ollama" as api_key
- Mode flag affects wrap-up message content
- Handle scenario with special characters in name
- Handle concurrent scenario locks
- Merge agent inserts markers above test functions
- Merge agent handles duplicate markers
- Merge agent writes resolved file to staging
- Merge agent logs resolution decisions
- Integration test agent re-runs tests after fix
- Integration test agent fails session on persistent failure
- Integration test agent writes test result log
