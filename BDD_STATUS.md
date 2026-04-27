# BDD Status

Checked 333 scenario(s) across 24 test file(s).


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

- [ ] UNCOVERED: Format issue as markdown
- [ ] UNCOVERED: Truncate long issue body
- [ ] UNCOVERED: Sort issues by reaction count
- [x] Mark user content with boundaries
- [ ] UNCOVERED: Warn about untrusted content

## Feature: Bootstrap Script

- [ ] UNCOVERED: Scaffold TypeScript React project
- [ ] UNCOVERED: Scaffold Python project
- [ ] UNCOVERED: Scaffold Rust project
- [ ] UNCOVERED: Create CI workflow for TypeScript
- [ ] UNCOVERED: Create CI workflow for Python
- [ ] UNCOVERED: Verify build passes before marking initialized
- [ ] UNCOVERED: Create Day 0 journal entry
- [ ] UNCOVERED: Write fallback journal if agent skips
- [ ] UNCOVERED: Seed journal index on bootstrap

## Feature: Evolution Script

- [x] Load BDD config before session
- [ ] UNCOVERED: Check starting build state
- [ ] UNCOVERED: Continue with failing tests
- [ ] UNCOVERED: Exit if build broken at start
- [ ] UNCOVERED: Fetch trusted GitHub issues
- [ ] UNCOVERED: Generate issues file for agent
- [ ] UNCOVERED: Pre-compute coverage before session
- [ ] UNCOVERED: Detect test-only anti-pattern
- [ ] UNCOVERED: Retry fix on build failure
- [ ] UNCOVERED: Revert session on persistent failure
- [ ] UNCOVERED: Write journal if agent skipped
- [ ] UNCOVERED: Write fallback journal if agent still skips
- [ ] UNCOVERED: Update journal index after session
- [ ] UNCOVERED: Comment and close implemented issues
- [ ] UNCOVERED: Push changes after session
- [ ] UNCOVERED: Track session start SHA for rollback
- [x] Exclude management files from worktree commits
- [ ] UNCOVERED: Branch naming convention with timestamp
- [ ] UNCOVERED: Calculate has_work flag
- [ ] UNCOVERED: Guard warning for minimal work with uncovered scenarios
- [ ] UNCOVERED: Handle push failure gracefully
- [ ] UNCOVERED: Handle missing git remote

## Feature: Scenario Locking for Parallel Execution

- [x] Generate scenario slug from name
- [x] Slug truncates to 60 characters
- [x] Check for existing lock file
- [ ] UNCOVERED: Detect stale lock from dead PID
- [x] Write lock file with session metadata
- [ ] UNCOVERED: Release lock on completion
- [ ] UNCOVERED: Clean up lock on early exit

## Feature: Git Worktree Isolation

- [ ] UNCOVERED: Create worktree for scenario
- [ ] UNCOVERED: Copy runtime files to worktree
- [ ] UNCOVERED: Merge successful worktree to main
- [ ] UNCOVERED: Auto-resolve management file conflicts
- [ ] UNCOVERED: Fold JOURNAL_ENTRY.md into JOURNAL.md
- [ ] UNCOVERED: Clean up worktree after merge
- [ ] UNCOVERED: Remove worktree on failure

## Feature: Parallel Agent Orchestration

- [ ] UNCOVERED: Find uncovered scenarios for orchestration
- [ ] UNCOVERED: AI-powered scenario ordering
- [ ] UNCOVERED: Fallback to BDD.md order on AI failure
- [ ] UNCOVERED: Select top N scenarios for parallel run
- [ ] UNCOVERED: Create worktrees for parallel scenarios
- [ ] UNCOVERED: Run agents in parallel with ThreadPoolExecutor
- [ ] UNCOVERED: Stream agent output with scenario prefix
- [ ] UNCOVERED: Merge results in planned order
- [ ] UNCOVERED: Track total agent time across workers
- [ ] UNCOVERED: Deferred scenarios message
- [x] Read max_rounds from poppins.yml
- [ ] UNCOVERED: Run orchestrator N rounds sequentially
- [ ] UNCOVERED: Override max rounds via CLI
- [ ] UNCOVERED: Write orchestrator event log
- [ ] UNCOVERED: Write orchestrator journal entry
- [ ] UNCOVERED: Override max parallel agents via CLI
- [ ] UNCOVERED: Dry run mode shows plan without execution
- [ ] UNCOVERED: Custom BDD.md path via --bdd flag
- [ ] UNCOVERED: Override orchestrator planning model
- [ ] UNCOVERED: Force orchestrator provider via CLI
- [ ] UNCOVERED: Worker result structure
- [ ] UNCOVERED: Status indicators for worker output
- [ ] UNCOVERED: Worker with no commits shows fail status
- [ ] UNCOVERED: Worker with failing tests shows warning

## Feature: Setup Environment Script

- [ ] UNCOVERED: Setup Rust toolchain
- [ ] UNCOVERED: Setup Node dependencies
- [ ] UNCOVERED: Setup Python dependencies
- [ ] UNCOVERED: Setup Go dependencies
- [ ] UNCOVERED: Always install agent dependencies
- [ ] UNCOVERED: Skip unknown language gracefully

## Feature: Add BDD Markers Utility

- [ ] UNCOVERED: Detect comment prefix by file extension
- [ ] UNCOVERED: Detect JavaScript comment prefix
- [x] Find test line matching scenario
- [ ] UNCOVERED: Insert marker above test function
- [ ] UNCOVERED: Skip if marker already exists
- [ ] UNCOVERED: Dry run mode shows planned changes
- [ ] UNCOVERED: Apply mode modifies files

## Feature: Dotenv Loading

- [x] Load .env file into environment
- [x] Handle quoted values in .env
- [x] Skip comment lines in .env
- [x] Environment variables override .env

## Feature: CI/CD Integration

- [ ] UNCOVERED: GitHub Actions workflow triggers on schedule
- [ ] UNCOVERED: Manual workflow dispatch
- [ ] UNCOVERED: Bootstrap detection in workflow
- [ ] UNCOVERED: Workflow timeout limit
- [ ] UNCOVERED: Retry after first attempt failure
- [ ] UNCOVERED: Retry after second attempt failure
- [ ] UNCOVERED: Configure git bot identity
- [ ] UNCOVERED: GitHub Actions log grouping
- [ ] UNCOVERED: Detect CI environment
- [ ] UNCOVERED: Release workflow on version tag
- [ ] UNCOVERED: Release includes install.sh
- [ ] UNCOVERED: Docs workflow triggers on docs path change
- [ ] UNCOVERED: Docs deployment to GitHub Pages

## Feature: Install Script

- [ ] UNCOVERED: Init new baadd project
- [ ] UNCOVERED: Update existing baadd project
- [ ] UNCOVERED: Auto-detect update mode
- [ ] UNCOVERED: Pin to specific version
- [ ] UNCOVERED: Fetch latest version from GitHub API
- [ ] UNCOVERED: Skip no-clobber files on update
- [ ] UNCOVERED: Archive journals before update
- [ ] UNCOVERED: Create BDD.md from template
- [ ] UNCOVERED: Init git repo if missing
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
- [ ] UNCOVERED: Never delete tests

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
- [ ] UNCOVERED: Issue response file format parsing

## Feature: Dashboard — scripts/dashboard.py (Python, Rich TUI)

- [ ] UNCOVERED: Dashboard file exists at scripts/dashboard.py
- [x] Rich is the only third-party import in dashboard.py
- [ ] UNCOVERED: Running "python3 scripts/dashboard.py" opens the Rich TUI immediately
- [ ] UNCOVERED: The dashboard is only for scripts/orchestrate.py — not evolve.sh or agent.py
- [x] dashboard.py defines a main() function called from __main__
- [ ] UNCOVERED: Live refresh loop uses rich.live.Live with refresh_per_second
- [ ] UNCOVERED: Each agent is rendered as a rich.panel.Panel
- [ ] UNCOVERED: Overall renderable is a rich.console.Group of Panels stacked vertically

## Feature: Dashboard Worktree Discovery

- [ ] UNCOVERED: discover_worktrees returns baadd worktree paths from git worktree list output
- [ ] UNCOVERED: discover_worktrees excludes the main worktree
- [ ] UNCOVERED: discover_worktrees returns empty list when no baadd worktrees exist
- [ ] UNCOVERED: discover_worktrees returns empty list when git command fails
- [ ] UNCOVERED: slug_to_name converts hyphenated path slug to display name
- [ ] UNCOVERED: slug_to_name handles path with no trailing digits
- [ ] UNCOVERED: resolve_display_name prefers explicit wt_map entry over slug
- [ ] UNCOVERED: resolve_display_name falls back to slug_to_name when path not in wt_map

## Feature: JSONL Event Log Reading

- [ ] UNCOVERED: read_wt_state reads current_iter as the highest iteration value seen in iteration_start events
- [ ] UNCOVERED: read_wt_state reads max_iter from the max_iterations field of iteration_start events
- [ ] UNCOVERED: read_wt_state sets active_phase to the label of the most recent phase lacking session_end
- [ ] UNCOVERED: read_wt_state adds a phase label to done_phases when its log contains session_end
- [ ] UNCOVERED: read_wt_state returns done_phases in fixed pipeline order PM-PLAN SE TESTER ACCEPT
- [ ] UNCOVERED: read_wt_state reads tokens as the highest cumulative_output_tokens seen in api_response events
- [ ] UNCOVERED: read_wt_state reads start_ts as a float epoch from the ts field of the session_start event
- [ ] UNCOVERED: read_wt_state collects the 3 most recent tool_call events from the active phase log as last_tools
- [ ] UNCOVERED: read_wt_state skips malformed JSON lines and continues reading
- [ ] UNCOVERED: read_wt_state returns zeroed AgentState when no JSONL files exist in worktree
- [ ] UNCOVERED: read_wt_state picks the JSONL file with the highest mtime when multiple files share the same phase prefix
- [ ] UNCOVERED: read_wt_state handles OSError when opening a JSONL file
- [ ] UNCOVERED: read_wt_state sets start_ts to current time when no session_start event exists

## Feature: AgentState Dataclass

- [x] AgentState is a dataclass with the required fields
- [x] AgentState.elapsed_s property returns seconds since start_ts
- [ ] UNCOVERED: AgentState.is_stale property returns True when newest JSONL mtime is over 120 seconds old
- [ ] UNCOVERED: AgentState.is_stale returns False when any JSONL file was modified within 120 seconds
- [ ] UNCOVERED: AgentState.is_stale returns False when worktree has no JSONL files yet
- [ ] UNCOVERED: AgentState.is_done returns True only when all four phase labels are in done_phases
- [ ] UNCOVERED: AgentState.is_done returns False when fewer than four phases are done

## Feature: Tool Call Formatting

- [ ] UNCOVERED: format_tool_call formats read_file as "r: <path>"
- [ ] UNCOVERED: format_tool_call formats write_file as "w: <path>"
- [ ] UNCOVERED: format_tool_call formats bash as "$ <command>" truncated to 60 chars
- [ ] UNCOVERED: format_tool_call formats run_command identically to bash
- [ ] UNCOVERED: format_tool_call formats edit_file as "e: <path>"
- [ ] UNCOVERED: format_tool_call uses generic "tool: value" format for unknown tools
- [ ] UNCOVERED: format_tool_call returns "r: ?" when path key is missing from input_dict for read_file
- [ ] UNCOVERED: format_tool_call handles None input_dict without raising

## Feature: Log Line Filtering

- [ ] UNCOVERED: is_log_noise returns True for TPS monitor lines matching "tok | X TPS |"
- [ ] UNCOVERED: is_log_noise returns True for bracketed per-agent output lines
- [ ] UNCOVERED: is_log_noise returns False for round banner lines starting with "==="
- [ ] UNCOVERED: is_log_noise returns False for MERGED result lines
- [ ] UNCOVERED: is_log_noise returns False for THROWN AWAY result lines
- [ ] UNCOVERED: is_log_noise returns False for Pre-flight status lines
- [ ] UNCOVERED: is_log_noise returns False for scenario-to-worktree mapping lines containing " → /tmp"
- [ ] UNCOVERED: is_log_noise returns False for empty lines
- [ ] UNCOVERED: parse_wt_mapping_line extracts scenario name and worktree path
- [ ] UNCOVERED: parse_wt_mapping_line returns None for lines without " → /tmp"
- [ ] UNCOVERED: parse_wt_mapping_line returns None for empty string
- [ ] UNCOVERED: log buffer is a deque(maxlen=10) that automatically discards oldest entries

## Feature: Dashboard Rendering Functions

- [ ] UNCOVERED: format_phase_line returns correct string for two done phases and one active phase
- [ ] UNCOVERED: format_phase_line returns all checkmarks when all four phases are done
- [ ] UNCOVERED: format_phase_line returns four dashes when nothing has started
- [ ] UNCOVERED: format_phase_line shows active phase with iteration count
- [ ] UNCOVERED: render_progress_bar returns a string of bar_width unicode chars using "█" and "░"
- [ ] UNCOVERED: render_progress_bar fills correct proportion at 50 percent
- [ ] UNCOVERED: render_progress_bar returns fully filled bar at 100 percent
- [ ] UNCOVERED: render_progress_bar clamps fill at 100 percent when current_iter exceeds max_iter
- [ ] UNCOVERED: render_progress_bar handles max_iter=0 without division-by-zero
- [ ] UNCOVERED: format_metrics_line returns formatted tokens and TPS string
- [ ] UNCOVERED: format_metrics_line returns dash when tokens is zero
- [ ] UNCOVERED: format_metrics_line computes TPS as tokens divided by elapsed_s
- [ ] UNCOVERED: format_metrics_line does not divide by zero when elapsed_s is 0
- [ ] UNCOVERED: format_elapsed returns seconds string for durations under 60 seconds
- [ ] UNCOVERED: format_elapsed returns minutes and zero-padded seconds for durations over 60 seconds
- [ ] UNCOVERED: format_elapsed returns "0s" for zero elapsed time
- [ ] UNCOVERED: build_agent_panel returns a rich.panel.Panel whose title is the scenario name
- [ ] UNCOVERED: build_agent_panel appends "(stale)" to panel title when state.is_stale is True
- [ ] UNCOVERED: build_agent_panel does not include "(stale)" when state.is_stale is False
- [ ] UNCOVERED: format_header returns a string containing agent count and session elapsed time
- [ ] UNCOVERED: format_header returns "waiting for agents" string when states list is empty
- [ ] UNCOVERED: format_log_strip returns a string containing all lines from the log buffer
- [ ] UNCOVERED: format_log_strip returns a placeholder string when log buffer is empty
- [ ] UNCOVERED: build_renderable returns a rich.console.Group containing all agent panels plus header and log panels
- [ ] UNCOVERED: build_renderable returns a Group with only header and log panels when states is empty

## Feature: Wrapper Mode

- [ ] UNCOVERED: wrapper mode constructs the subprocess command as ["python3", "scripts/orchestrate.py"] plus forwarded args
- [ ] UNCOVERED: wrapper mode passes all unrecognised args through to orchestrate.py unchanged
- [ ] UNCOVERED: stdout reader thread calls is_log_noise on each line and only appends non-noise lines to log_buffer
- [ ] UNCOVERED: stdout reader thread calls parse_wt_mapping_line and populates wt_map for matching lines
- [ ] UNCOVERED: wrapper main loop calls sys.exit with orchestrate.py returncode when subprocess exits with 0
- [ ] UNCOVERED: wrapper main loop calls sys.exit with orchestrate.py returncode when subprocess exits with 1
- [ ] UNCOVERED: wrapper renders "waiting for agents" header when no worktrees exist yet
- [ ] UNCOVERED: wrapper adds a new agent panel when a worktree appears between polls
- [ ] UNCOVERED: wrapper mode raises RuntimeError and prints clear message when scripts/orchestrate.py does not exist

## Feature: Watcher Mode

- [ ] UNCOVERED: --watch flag causes no subprocess to be started
- [ ] UNCOVERED: watcher mode calls discover_worktrees on every poll iteration
- [ ] UNCOVERED: watcher exits after two consecutive empty polls from discover_worktrees
- [ ] UNCOVERED: watcher does not exit after a single empty poll
- [ ] UNCOVERED: watcher prints "All agents done." to stdout after the Live context closes
- [ ] UNCOVERED: watcher resolves scenario names from slug_to_name when no wt_map is available

## Feature: Dashboard CLI Arguments

- [x] parse_args returns watch=False and mode is wrapper when --watch is absent
- [x] parse_args returns watch=True when --watch flag is present
- [x] parse_args collects unrecognised flags into pass_args for forwarding
- [x] parse_args --refresh sets poll interval
- [x] parse_args default refresh interval is 2 seconds
- [x] --watch and --refresh can be combined with pass_args

## Feature: Dashboard Error Handling and Edge Cases

- [ ] UNCOVERED: Missing rich package causes immediate error with install instruction
- [ ] UNCOVERED: KeyboardInterrupt during Live loop exits cleanly without traceback
- [ ] UNCOVERED: SIGTERM during wrapper mode terminates the subprocess before exiting
- [ ] UNCOVERED: Worktree directory disappears between polls without crashing
- [ ] UNCOVERED: glob finds no JSONL files in a worktree that exists but has not started yet
- [ ] UNCOVERED: TPS calculation guards against division by zero when elapsed_s is 0
- [x] Very long scenario name is truncated in panel title to prevent wrapping
- [ ] UNCOVERED: render_progress_bar always returns a string of exactly bar_width characters
- [ ] UNCOVERED: Dashboard handles zero-width terminal gracefully
- [ ] UNCOVERED: stdout reader thread sets a threading.Event when subprocess stdout is exhausted

---
**105/333 scenarios covered.**

228 scenario(s) need tests:
- Format issue as markdown
- Truncate long issue body
- Sort issues by reaction count
- Warn about untrusted content
- Scaffold TypeScript React project
- Scaffold Python project
- Scaffold Rust project
- Create CI workflow for TypeScript
- Create CI workflow for Python
- Verify build passes before marking initialized
- Create Day 0 journal entry
- Write fallback journal if agent skips
- Seed journal index on bootstrap
- Check starting build state
- Continue with failing tests
- Exit if build broken at start
- Fetch trusted GitHub issues
- Generate issues file for agent
- Pre-compute coverage before session
- Detect test-only anti-pattern
- Retry fix on build failure
- Revert session on persistent failure
- Write journal if agent skipped
- Write fallback journal if agent still skips
- Update journal index after session
- Comment and close implemented issues
- Push changes after session
- Track session start SHA for rollback
- Branch naming convention with timestamp
- Calculate has_work flag
- Guard warning for minimal work with uncovered scenarios
- Handle push failure gracefully
- Handle missing git remote
- Detect stale lock from dead PID
- Release lock on completion
- Clean up lock on early exit
- Create worktree for scenario
- Copy runtime files to worktree
- Merge successful worktree to main
- Auto-resolve management file conflicts
- Fold JOURNAL_ENTRY.md into JOURNAL.md
- Clean up worktree after merge
- Remove worktree on failure
- Find uncovered scenarios for orchestration
- AI-powered scenario ordering
- Fallback to BDD.md order on AI failure
- Select top N scenarios for parallel run
- Create worktrees for parallel scenarios
- Run agents in parallel with ThreadPoolExecutor
- Stream agent output with scenario prefix
- Merge results in planned order
- Track total agent time across workers
- Deferred scenarios message
- Run orchestrator N rounds sequentially
- Override max rounds via CLI
- Write orchestrator event log
- Write orchestrator journal entry
- Override max parallel agents via CLI
- Dry run mode shows plan without execution
- Custom BDD.md path via --bdd flag
- Override orchestrator planning model
- Force orchestrator provider via CLI
- Worker result structure
- Status indicators for worker output
- Worker with no commits shows fail status
- Worker with failing tests shows warning
- Setup Rust toolchain
- Setup Node dependencies
- Setup Python dependencies
- Setup Go dependencies
- Always install agent dependencies
- Skip unknown language gracefully
- Detect comment prefix by file extension
- Detect JavaScript comment prefix
- Insert marker above test function
- Skip if marker already exists
- Dry run mode shows planned changes
- Apply mode modifies files
- GitHub Actions workflow triggers on schedule
- Manual workflow dispatch
- Bootstrap detection in workflow
- Workflow timeout limit
- Retry after first attempt failure
- Retry after second attempt failure
- Configure git bot identity
- GitHub Actions log grouping
- Detect CI environment
- Release workflow on version tag
- Release includes install.sh
- Docs workflow triggers on docs path change
- Docs deployment to GitHub Pages
- Init new baadd project
- Update existing baadd project
- Auto-detect update mode
- Pin to specific version
- Fetch latest version from GitHub API
- Skip no-clobber files on update
- Archive journals before update
- Create BDD.md from template
- Init git repo if missing
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
- Never delete tests
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
- Issue response file format parsing
- Dashboard file exists at scripts/dashboard.py
- Running "python3 scripts/dashboard.py" opens the Rich TUI immediately
- The dashboard is only for scripts/orchestrate.py — not evolve.sh or agent.py
- Live refresh loop uses rich.live.Live with refresh_per_second
- Each agent is rendered as a rich.panel.Panel
- Overall renderable is a rich.console.Group of Panels stacked vertically
- discover_worktrees returns baadd worktree paths from git worktree list output
- discover_worktrees excludes the main worktree
- discover_worktrees returns empty list when no baadd worktrees exist
- discover_worktrees returns empty list when git command fails
- slug_to_name converts hyphenated path slug to display name
- slug_to_name handles path with no trailing digits
- resolve_display_name prefers explicit wt_map entry over slug
- resolve_display_name falls back to slug_to_name when path not in wt_map
- read_wt_state reads current_iter as the highest iteration value seen in iteration_start events
- read_wt_state reads max_iter from the max_iterations field of iteration_start events
- read_wt_state sets active_phase to the label of the most recent phase lacking session_end
- read_wt_state adds a phase label to done_phases when its log contains session_end
- read_wt_state returns done_phases in fixed pipeline order PM-PLAN SE TESTER ACCEPT
- read_wt_state reads tokens as the highest cumulative_output_tokens seen in api_response events
- read_wt_state reads start_ts as a float epoch from the ts field of the session_start event
- read_wt_state collects the 3 most recent tool_call events from the active phase log as last_tools
- read_wt_state skips malformed JSON lines and continues reading
- read_wt_state returns zeroed AgentState when no JSONL files exist in worktree
- read_wt_state picks the JSONL file with the highest mtime when multiple files share the same phase prefix
- read_wt_state handles OSError when opening a JSONL file
- read_wt_state sets start_ts to current time when no session_start event exists
- AgentState.is_stale property returns True when newest JSONL mtime is over 120 seconds old
- AgentState.is_stale returns False when any JSONL file was modified within 120 seconds
- AgentState.is_stale returns False when worktree has no JSONL files yet
- AgentState.is_done returns True only when all four phase labels are in done_phases
- AgentState.is_done returns False when fewer than four phases are done
- format_tool_call formats read_file as "r: <path>"
- format_tool_call formats write_file as "w: <path>"
- format_tool_call formats bash as "$ <command>" truncated to 60 chars
- format_tool_call formats run_command identically to bash
- format_tool_call formats edit_file as "e: <path>"
- format_tool_call uses generic "tool: value" format for unknown tools
- format_tool_call returns "r: ?" when path key is missing from input_dict for read_file
- format_tool_call handles None input_dict without raising
- is_log_noise returns True for TPS monitor lines matching "tok | X TPS |"
- is_log_noise returns True for bracketed per-agent output lines
- is_log_noise returns False for round banner lines starting with "==="
- is_log_noise returns False for MERGED result lines
- is_log_noise returns False for THROWN AWAY result lines
- is_log_noise returns False for Pre-flight status lines
- is_log_noise returns False for scenario-to-worktree mapping lines containing " → /tmp"
- is_log_noise returns False for empty lines
- parse_wt_mapping_line extracts scenario name and worktree path
- parse_wt_mapping_line returns None for lines without " → /tmp"
- parse_wt_mapping_line returns None for empty string
- log buffer is a deque(maxlen=10) that automatically discards oldest entries
- format_phase_line returns correct string for two done phases and one active phase
- format_phase_line returns all checkmarks when all four phases are done
- format_phase_line returns four dashes when nothing has started
- format_phase_line shows active phase with iteration count
- render_progress_bar returns a string of bar_width unicode chars using "█" and "░"
- render_progress_bar fills correct proportion at 50 percent
- render_progress_bar returns fully filled bar at 100 percent
- render_progress_bar clamps fill at 100 percent when current_iter exceeds max_iter
- render_progress_bar handles max_iter=0 without division-by-zero
- format_metrics_line returns formatted tokens and TPS string
- format_metrics_line returns dash when tokens is zero
- format_metrics_line computes TPS as tokens divided by elapsed_s
- format_metrics_line does not divide by zero when elapsed_s is 0
- format_elapsed returns seconds string for durations under 60 seconds
- format_elapsed returns minutes and zero-padded seconds for durations over 60 seconds
- format_elapsed returns "0s" for zero elapsed time
- build_agent_panel returns a rich.panel.Panel whose title is the scenario name
- build_agent_panel appends "(stale)" to panel title when state.is_stale is True
- build_agent_panel does not include "(stale)" when state.is_stale is False
- format_header returns a string containing agent count and session elapsed time
- format_header returns "waiting for agents" string when states list is empty
- format_log_strip returns a string containing all lines from the log buffer
- format_log_strip returns a placeholder string when log buffer is empty
- build_renderable returns a rich.console.Group containing all agent panels plus header and log panels
- build_renderable returns a Group with only header and log panels when states is empty
- wrapper mode constructs the subprocess command as ["python3", "scripts/orchestrate.py"] plus forwarded args
- wrapper mode passes all unrecognised args through to orchestrate.py unchanged
- stdout reader thread calls is_log_noise on each line and only appends non-noise lines to log_buffer
- stdout reader thread calls parse_wt_mapping_line and populates wt_map for matching lines
- wrapper main loop calls sys.exit with orchestrate.py returncode when subprocess exits with 0
- wrapper main loop calls sys.exit with orchestrate.py returncode when subprocess exits with 1
- wrapper renders "waiting for agents" header when no worktrees exist yet
- wrapper adds a new agent panel when a worktree appears between polls
- wrapper mode raises RuntimeError and prints clear message when scripts/orchestrate.py does not exist
- --watch flag causes no subprocess to be started
- watcher mode calls discover_worktrees on every poll iteration
- watcher exits after two consecutive empty polls from discover_worktrees
- watcher does not exit after a single empty poll
- watcher prints "All agents done." to stdout after the Live context closes
- watcher resolves scenario names from slug_to_name when no wt_map is available
- Missing rich package causes immediate error with install instruction
- KeyboardInterrupt during Live loop exits cleanly without traceback
- SIGTERM during wrapper mode terminates the subprocess before exiting
- Worktree directory disappears between polls without crashing
- glob finds no JSONL files in a worktree that exists but has not started yet
- TPS calculation guards against division by zero when elapsed_s is 0
- render_progress_bar always returns a string of exactly bar_width characters
- Dashboard handles zero-width terminal gracefully
- stdout reader thread sets a threading.Event when subprocess stdout is exhausted
