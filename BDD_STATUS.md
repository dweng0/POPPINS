# BDD Status

Checked 432 scenario(s) across 63 test file(s).


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
- [x] Update existing baadd project
- [x] Auto-detect update mode
- [x] Pin to specific version
- [x] Fetch latest version from GitHub API
- [x] Skip no-clobber files on update
- [x] Archive journals before update
- [x] Create BDD.md from template
- [x] Init git repo if missing
- [x] Create locks directory
- [x] Read manifest file list
- [x] Stamp version in manifest
- [x] Already on target version skips update
- [x] Set executable permissions on scripts
- [x] Download file creates parent directories

## Feature: Identity and Safety Rules

- [x] Never modify IDENTITY.md
- [x] Never modify scripts/evolve.sh
- [x] Never modify .github/workflows/
- [x] Only build features from BDD.md
- [x] Never delete tests

## Feature: Error Recovery

- [x] API error causes retry exit
- [x] Post-merge verification catches breakage
- [x] Timeout kills long session
- [x] Handle missing gh CLI gracefully
- [x] Worktree creation failure
- [x] Handle test file that cannot be read
- [x] Tool output formatting with iteration tag
- [x] Tool icons for different tool types
- [x] Detect Moonshot provider
- [x] Detect Dashscope provider
- [x] Moonshot default model
- [x] Dashscope default model
- [x] Groq default model
- [x] Ollama default model
- [x] Custom provider requires api_key string placeholder
- [x] Ollama provider uses "ollama" as api_key
- [x] Mode flag affects wrap-up message content
- [x] Bootstrap mode agent prompt
- [x] Handle scenario with special characters in name
- [x] Handle concurrent scenario locks
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
- [x] Merge agent inserts markers above test functions
- [x] Merge agent handles duplicate markers
- [x] Merge agent writes resolved file to staging
- [x] Merge agent logs resolution decisions

## Feature: Integration Test Agent

- [x] Integration test agent runs full test suite
- [x] Integration test agent reports pass
- [x] Integration test agent reports fail
- [x] Integration test agent attempts fix on failure
- [x] Integration test agent re-runs tests after fix
- [x] Integration test agent fails session on persistent failure
- [x] Integration test agent writes test result log

## Feature: Worktree Session Lifecycle

- [ ] UNCOVERED: evolve.sh appends session_start to sessions.jsonl when worktree is created
- [ ] UNCOVERED: evolve.sh appends session_end to sessions.jsonl on normal completion
- [ ] UNCOVERED: evolve.sh appends session_end to sessions.jsonl on failure or early exit
- [ ] UNCOVERED: orchestrate.py appends session_start per worker worktree it spawns
- [ ] UNCOVERED: orchestrate.py appends session_end for each worker when it finishes
- [x] sessions.jsonl is created if it does not exist
- [ ] UNCOVERED: sessions.jsonl append is atomic enough to avoid corruption under parallel writes
- [ ] UNCOVERED: read_sessions(sessions_path) returns list of dicts parsed from sessions.jsonl
- [ ] UNCOVERED: read_sessions returns empty list when sessions.jsonl does not exist
- [ ] UNCOVERED: read_sessions skips malformed JSON lines without crashing
- [ ] UNCOVERED: active_wt_paths(sessions_path) returns only wt_paths with session_start and no session_end
- [ ] UNCOVERED: active_wt_paths excludes sessions older than SESSION_TIMEOUT seconds
- [ ] UNCOVERED: active_wt_paths handles duplicate session_start lines for the same wt_path

## Feature: Dashboard Worktree Staleness Filtering

- [ ] UNCOVERED: discover_worktrees runs git worktree prune before listing
- [ ] UNCOVERED: discover_worktrees excludes worktrees absent from sessions.jsonl active set
- [ ] UNCOVERED: discover_worktrees includes worktrees present in both git list and active set
- [ ] UNCOVERED: discover_worktrees falls back to git list only when sessions.jsonl is absent
- [ ] UNCOVERED: discover_worktrees excludes worktrees whose /tmp directory no longer exists on disk
- [ ] UNCOVERED: discover_worktrees treats stale sessions (no session_end, age > SESSION_TIMEOUT) as inactive
- [ ] UNCOVERED: discover_worktrees returns empty list when git worktree prune itself raises OSError
- [ ] UNCOVERED: discover_worktrees returns consistent results under concurrent calls
- [ ] UNCOVERED: discover_worktrees excludes worktrees with session_end written within the last 2 seconds
- [ ] UNCOVERED: git worktree prune is skipped when main_dir is not a git repository

## Feature: Dashboard BTOP-Style Responsive Layout

- [ ] UNCOVERED: build_layout() returns a rich.layout.Layout with header, body, log, statusbar sections
- [ ] UNCOVERED: agent grid uses 1 column when terminal width is less than 160
- [ ] UNCOVERED: agent grid uses 2 columns when terminal width is 160 to 239
- [ ] UNCOVERED: agent grid uses 3 columns when terminal width is 240 or more
- [ ] UNCOVERED: build_renderable updates Layout sections instead of returning a Group
- [ ] UNCOVERED: Layout degrades to single-column Group when rich.layout.Layout raises NotImplementedError
- [ ] UNCOVERED: Column count recalculates on every poll when terminal is resized
- [x] Empty agent list renders body section as a centered "waiting for agents" Panel
- [x] Single agent fills full width regardless of column threshold

## Feature: Dashboard Token Sparklines

- [ ] UNCOVERED: AgentState has a token_history field that is a deque with maxlen=60
- [ ] UNCOVERED: read_wt_state populates token_history from api_response events
- [ ] UNCOVERED: render_sparkline maps values to 8 block characters by percentile bucket
- [ ] UNCOVERED: render_sparkline returns a string of exactly `width` characters
- [ ] UNCOVERED: render_sparkline right-aligns when history has fewer points than width
- [ ] UNCOVERED: render_sparkline returns all "▁" when all values are equal (flat line)
- [ ] UNCOVERED: render_sparkline returns width spaces when history is empty
- [ ] UNCOVERED: render_sparkline truncates to rightmost `width` points when history is longer than width
- [ ] UNCOVERED: build_agent_panel includes the sparkline string inside the panel body
- [ ] UNCOVERED: sparkline line in agent panel is labelled "tok/iter" to explain the graph
- [ ] UNCOVERED: render_sparkline handles a single-element history without IndexError

## Feature: Dashboard Gradient Progress Bars

- [ ] UNCOVERED: render_gradient_bar returns green-marked filled chars at 0 percent used
- [ ] UNCOVERED: render_gradient_bar returns green markup at 30 percent used
- [ ] UNCOVERED: render_gradient_bar switches to yellow markup at 50 percent used
- [ ] UNCOVERED: render_gradient_bar switches to red markup at 75 percent used
- [ ] UNCOVERED: render_gradient_bar switches to bold red markup at 90 percent used
- [ ] UNCOVERED: render_gradient_bar returns fully filled bold-red bar at 100 percent
- [ ] UNCOVERED: render_gradient_bar result is exactly width visible characters when markup is stripped
- [ ] UNCOVERED: render_gradient_bar does not raise ZeroDivisionError when max_val is 0
- [ ] UNCOVERED: render_gradient_bar clamps filled chars to width when current exceeds max_val
- [ ] UNCOVERED: build_agent_panel uses render_gradient_bar instead of plain render_progress_bar

## Feature: Dashboard Status Bar

- [ ] UNCOVERED: build_status_bar returns a rich.text.Text object
- [ ] UNCOVERED: build_status_bar shows correct agent count
- [ ] UNCOVERED: build_status_bar shows summed token count across all agents
- [ ] UNCOVERED: build_status_bar shows session uptime in Xm Xs format
- [ ] UNCOVERED: build_status_bar contains all four keybinding hints
- [ ] UNCOVERED: build_status_bar text is padded to exactly terminal_width characters
- [ ] UNCOVERED: build_status_bar uses reverse-video style for background
- [ ] UNCOVERED: build_status_bar shows "agents: 0" when states is empty
- [ ] UNCOVERED: build_status_bar does not raise when terminal_width is 0 or 1

## Feature: Dashboard Keyboard Input

- [ ] UNCOVERED: keyboard_input_thread is a daemon thread started in main()
- [ ] UNCOVERED: pressing q puts "q" into the key_queue
- [x] main loop reads q from key_queue and exits the Live loop
- [ ] UNCOVERED: pressing r puts "r" into the key_queue and triggers immediate refresh
- [ ] UNCOVERED: pressing up-arrow puts "up" into the key_queue
- [ ] UNCOVERED: pressing down-arrow puts "down" into the key_queue
- [ ] UNCOVERED: up-arrow increments log_scroll_offset by 1
- [ ] UNCOVERED: down-arrow decrements log_scroll_offset by 1 but not below 0
- [ ] UNCOVERED: down-arrow at offset 0 does not go negative
- [ ] UNCOVERED: keyboard_input_thread restores terminal settings on exit
- [ ] UNCOVERED: keyboard_input_thread does not crash when stdin is not a tty (e.g. CI pipe)
- [ ] UNCOVERED: key_queue is bounded (maxsize=32) to prevent unbounded growth if keys are ignored
- [ ] UNCOVERED: multiple queued keystrokes are all drained in a single poll cycle

## Feature: Dashboard Log Panel Scrolling

- [ ] UNCOVERED: format_log_strip with scroll_offset=0 returns the last `height` lines of log_buffer
- [ ] UNCOVERED: format_log_strip with scroll_offset=5 returns lines shifted 5 back from the end
- [ ] UNCOVERED: format_log_strip clamps scroll_offset so it never scrolls before the first line
- [ ] UNCOVERED: format_log_strip pads with empty lines when log_buffer has fewer than height lines
- [ ] UNCOVERED: log Panel title shows scroll position indicator when scroll_offset > 0
- [x] log Panel title shows "AUTO" or no indicator when scroll_offset is 0
- [ ] UNCOVERED: new log lines do not auto-scroll when scroll_offset > 0
- [ ] UNCOVERED: new log lines DO auto-scroll when scroll_offset is 0
- [ ] UNCOVERED: scroll up beyond buffer start is clamped and does not raise IndexError
- [ ] UNCOVERED: format_log_strip returns placeholder when log_buffer is empty regardless of scroll_offset

---
**352/432 scenarios covered.**

80 scenario(s) need tests:
- evolve.sh appends session_start to sessions.jsonl when worktree is created
- evolve.sh appends session_end to sessions.jsonl on normal completion
- evolve.sh appends session_end to sessions.jsonl on failure or early exit
- orchestrate.py appends session_start per worker worktree it spawns
- orchestrate.py appends session_end for each worker when it finishes
- sessions.jsonl append is atomic enough to avoid corruption under parallel writes
- read_sessions(sessions_path) returns list of dicts parsed from sessions.jsonl
- read_sessions returns empty list when sessions.jsonl does not exist
- read_sessions skips malformed JSON lines without crashing
- active_wt_paths(sessions_path) returns only wt_paths with session_start and no session_end
- active_wt_paths excludes sessions older than SESSION_TIMEOUT seconds
- active_wt_paths handles duplicate session_start lines for the same wt_path
- discover_worktrees runs git worktree prune before listing
- discover_worktrees excludes worktrees absent from sessions.jsonl active set
- discover_worktrees includes worktrees present in both git list and active set
- discover_worktrees falls back to git list only when sessions.jsonl is absent
- discover_worktrees excludes worktrees whose /tmp directory no longer exists on disk
- discover_worktrees treats stale sessions (no session_end, age > SESSION_TIMEOUT) as inactive
- discover_worktrees returns empty list when git worktree prune itself raises OSError
- discover_worktrees returns consistent results under concurrent calls
- discover_worktrees excludes worktrees with session_end written within the last 2 seconds
- git worktree prune is skipped when main_dir is not a git repository
- build_layout() returns a rich.layout.Layout with header, body, log, statusbar sections
- agent grid uses 1 column when terminal width is less than 160
- agent grid uses 2 columns when terminal width is 160 to 239
- agent grid uses 3 columns when terminal width is 240 or more
- build_renderable updates Layout sections instead of returning a Group
- Layout degrades to single-column Group when rich.layout.Layout raises NotImplementedError
- Column count recalculates on every poll when terminal is resized
- AgentState has a token_history field that is a deque with maxlen=60
- read_wt_state populates token_history from api_response events
- render_sparkline maps values to 8 block characters by percentile bucket
- render_sparkline returns a string of exactly `width` characters
- render_sparkline right-aligns when history has fewer points than width
- render_sparkline returns all "▁" when all values are equal (flat line)
- render_sparkline returns width spaces when history is empty
- render_sparkline truncates to rightmost `width` points when history is longer than width
- build_agent_panel includes the sparkline string inside the panel body
- sparkline line in agent panel is labelled "tok/iter" to explain the graph
- render_sparkline handles a single-element history without IndexError
- render_gradient_bar returns green-marked filled chars at 0 percent used
- render_gradient_bar returns green markup at 30 percent used
- render_gradient_bar switches to yellow markup at 50 percent used
- render_gradient_bar switches to red markup at 75 percent used
- render_gradient_bar switches to bold red markup at 90 percent used
- render_gradient_bar returns fully filled bold-red bar at 100 percent
- render_gradient_bar result is exactly width visible characters when markup is stripped
- render_gradient_bar does not raise ZeroDivisionError when max_val is 0
- render_gradient_bar clamps filled chars to width when current exceeds max_val
- build_agent_panel uses render_gradient_bar instead of plain render_progress_bar
- build_status_bar returns a rich.text.Text object
- build_status_bar shows correct agent count
- build_status_bar shows summed token count across all agents
- build_status_bar shows session uptime in Xm Xs format
- build_status_bar contains all four keybinding hints
- build_status_bar text is padded to exactly terminal_width characters
- build_status_bar uses reverse-video style for background
- build_status_bar shows "agents: 0" when states is empty
- build_status_bar does not raise when terminal_width is 0 or 1
- keyboard_input_thread is a daemon thread started in main()
- pressing q puts "q" into the key_queue
- pressing r puts "r" into the key_queue and triggers immediate refresh
- pressing up-arrow puts "up" into the key_queue
- pressing down-arrow puts "down" into the key_queue
- up-arrow increments log_scroll_offset by 1
- down-arrow decrements log_scroll_offset by 1 but not below 0
- down-arrow at offset 0 does not go negative
- keyboard_input_thread restores terminal settings on exit
- keyboard_input_thread does not crash when stdin is not a tty (e.g. CI pipe)
- key_queue is bounded (maxsize=32) to prevent unbounded growth if keys are ignored
- multiple queued keystrokes are all drained in a single poll cycle
- format_log_strip with scroll_offset=0 returns the last `height` lines of log_buffer
- format_log_strip with scroll_offset=5 returns lines shifted 5 back from the end
- format_log_strip clamps scroll_offset so it never scrolls before the first line
- format_log_strip pads with empty lines when log_buffer has fewer than height lines
- log Panel title shows scroll position indicator when scroll_offset > 0
- new log lines do not auto-scroll when scroll_offset > 0
- new log lines DO auto-scroll when scroll_offset is 0
- scroll up beyond buffer start is clamped and does not raise IndexError
- format_log_strip returns placeholder when log_buffer is empty regardless of scroll_offset
