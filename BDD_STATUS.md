# BDD Status

Checked 217 scenario(s) across 2 test file(s).


## Feature: BDD Specification Parser

- [x] Parse YAML frontmatter from BDD.md
- [x] Handle missing frontmatter gracefully
- [x] Parse frontmatter with quoted values
- [x] Extract all scenarios from BDD.md
- [ ] UNCOVERED: Parse scenario outline syntax
- [ ] UNCOVERED: Skip frontmatter when parsing scenarios

## Feature: Test Coverage Detection

- [ ] UNCOVERED: Find test files in project
- [ ] UNCOVERED: Exclude non-source directories from test search
- [ ] UNCOVERED: Detect coverage via BDD marker comment
- [ ] UNCOVERED: Detect coverage via marker with different comment style
- [ ] UNCOVERED: Detect coverage via heuristic name matching
- [ ] UNCOVERED: Detect coverage via partial name matching
- [ ] UNCOVERED: Report uncovered scenarios
- [ ] UNCOVERED: Exit with error code when scenarios uncovered
- [ ] UNCOVERED: Exit with success when all scenarios covered
- [ ] UNCOVERED: Handle empty BDD.md with no scenarios
- [ ] UNCOVERED: Handle BDD.md with only frontmatter

## Feature: Multi-Provider AI Agent

- [ ] UNCOVERED: Detect Anthropic provider from API key
- [ ] UNCOVERED: Detect OpenAI provider from API key
- [ ] UNCOVERED: Detect Groq provider from API key
- [ ] UNCOVERED: Detect Ollama provider from localhost probe
- [ ] UNCOVERED: Detect custom provider from base URL
- [ ] UNCOVERED: Provider priority order
- [ ] UNCOVERED: Use provider default model
- [ ] UNCOVERED: Override model via MODEL environment variable
- [ ] UNCOVERED: Load provider config from poppins.yml
- [ ] UNCOVERED: Environment variables override poppins.yml config
- [ ] UNCOVERED: Set OLLAMA_HOST from poppins.yml base_url
- [ ] UNCOVERED: No provider detected error message
- [ ] UNCOVERED: CUSTOM_MODEL required for custom provider without --model
- [ ] UNCOVERED: Unknown provider error
- [ ] UNCOVERED: Override provider via --provider flag
- [ ] UNCOVERED: Missing anthropic package error
- [ ] UNCOVERED: Missing openai package error
- [ ] UNCOVERED: Empty stdin prompt error
- [ ] UNCOVERED: Load skills from SKILL.md files
- [ ] UNCOVERED: Skills appended to system prompt
- [ ] UNCOVERED: Skip skills loading if directory missing
- [ ] UNCOVERED: Custom event log path via --event-log

## Feature: Agent Tool Execution

- [ ] UNCOVERED: Run bash command and capture output
- [ ] UNCOVERED: Run bash command with stderr
- [ ] UNCOVERED: Bash command timeout after 300 seconds
- [ ] UNCOVERED: Read file that exists
- [ ] UNCOVERED: Read file that does not exist
- [ ] UNCOVERED: Truncate long file output
- [ ] UNCOVERED: Write file creates parent directories
- [ ] UNCOVERED: Edit file replaces exact string
- [ ] UNCOVERED: Edit file fails when string not found
- [ ] UNCOVERED: Edit file replaces only first occurrence
- [ ] UNCOVERED: List files excludes git and node_modules
- [ ] UNCOVERED: Search files finds pattern
- [ ] UNCOVERED: Search files handles no matches

## Feature: Agent Loop and Iteration Management

- [ ] UNCOVERED: Agent stops at max iterations
- [ ] UNCOVERED: Wrap-up reminder injected at threshold
- [ ] UNCOVERED: Wrap-up reminder content for evolve mode
- [ ] UNCOVERED: Wrap-up reminder content for bootstrap mode
- [ ] UNCOVERED: Session ends on end_turn stop reason

## Feature: Context Window Management

- [ ] UNCOVERED: Estimate tokens from text
- [ ] UNCOVERED: Trim context when exceeding limit
- [ ] UNCOVERED: Preserve recent messages during trim
- [ ] UNCOVERED: Trim only tool result content

## Feature: Event Logging

- [ ] UNCOVERED: Log session start with provider and model
- [ ] UNCOVERED: Log tool call with input preview
- [ ] UNCOVERED: Log tool result with duration
- [ ] UNCOVERED: Log token usage per API response
- [ ] UNCOVERED: Log session end with reason

## Feature: Poppins Configuration Parser

- [ ] UNCOVERED: Parse poppins.yml with agent section
- [ ] UNCOVERED: Apply defaults when poppins.yml missing
- [ ] UNCOVERED: Deep merge file config with defaults
- [ ] UNCOVERED: Get single config value via dot notation
- [ ] UNCOVERED: Search parent directories for poppins.yml

## Feature: GitHub Issue Trust Verification

- [ ] UNCOVERED: Trust repo owner's issues directly
- [ ] UNCOVERED: Trust community issue with agent-approved label from owner
- [ ] UNCOVERED: Reject community issue with agent-approved from non-owner
- [ ] UNCOVERED: Verify label applier via GitHub events API

## Feature: Issue Formatting for Agent

- [ ] UNCOVERED: Format issue as markdown
- [ ] UNCOVERED: Truncate long issue body
- [ ] UNCOVERED: Sort issues by reaction count
- [ ] UNCOVERED: Mark user content with boundaries
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

- [ ] UNCOVERED: Load BDD config before session
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
- [ ] UNCOVERED: Exclude management files from worktree commits
- [ ] UNCOVERED: Branch naming convention with timestamp
- [ ] UNCOVERED: Calculate has_work flag
- [ ] UNCOVERED: Guard warning for minimal work with uncovered scenarios
- [ ] UNCOVERED: Handle push failure gracefully
- [ ] UNCOVERED: Handle missing git remote

## Feature: Scenario Locking for Parallel Execution

- [ ] UNCOVERED: Generate scenario slug from name
- [ ] UNCOVERED: Slug truncates to 60 characters
- [ ] UNCOVERED: Check for existing lock file
- [ ] UNCOVERED: Detect stale lock from dead PID
- [ ] UNCOVERED: Write lock file with session metadata
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
- [ ] UNCOVERED: Find test line matching scenario
- [ ] UNCOVERED: Insert marker above test function
- [ ] UNCOVERED: Skip if marker already exists
- [ ] UNCOVERED: Dry run mode shows planned changes
- [ ] UNCOVERED: Apply mode modifies files

## Feature: Dotenv Loading

- [ ] UNCOVERED: Load .env file into environment
- [x] Handle quoted values in .env
- [ ] UNCOVERED: Skip comment lines in .env
- [ ] UNCOVERED: Environment variables override .env

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
- [ ] UNCOVERED: Handle test file that cannot be read
- [ ] UNCOVERED: Tool output formatting with iteration tag
- [ ] UNCOVERED: Tool icons for different tool types
- [ ] UNCOVERED: Detect Moonshot provider
- [ ] UNCOVERED: Detect Dashscope provider
- [ ] UNCOVERED: Moonshot default model
- [ ] UNCOVERED: Dashscope default model
- [ ] UNCOVERED: Groq default model
- [ ] UNCOVERED: Ollama default model
- [ ] UNCOVERED: Custom provider requires api_key string placeholder
- [ ] UNCOVERED: Ollama provider uses "ollama" as api_key
- [ ] UNCOVERED: Mode flag affects wrap-up message content
- [ ] UNCOVERED: Bootstrap mode agent prompt
- [ ] UNCOVERED: Handle scenario with special characters in name
- [ ] UNCOVERED: Handle concurrent scenario locks
- [ ] UNCOVERED: Issue response file format parsing

---
**6/217 scenarios covered.**

211 scenario(s) need tests:
- Parse scenario outline syntax
- Skip frontmatter when parsing scenarios
- Find test files in project
- Exclude non-source directories from test search
- Detect coverage via BDD marker comment
- Detect coverage via marker with different comment style
- Detect coverage via heuristic name matching
- Detect coverage via partial name matching
- Report uncovered scenarios
- Exit with error code when scenarios uncovered
- Exit with success when all scenarios covered
- Handle empty BDD.md with no scenarios
- Handle BDD.md with only frontmatter
- Detect Anthropic provider from API key
- Detect OpenAI provider from API key
- Detect Groq provider from API key
- Detect Ollama provider from localhost probe
- Detect custom provider from base URL
- Provider priority order
- Use provider default model
- Override model via MODEL environment variable
- Load provider config from poppins.yml
- Environment variables override poppins.yml config
- Set OLLAMA_HOST from poppins.yml base_url
- No provider detected error message
- CUSTOM_MODEL required for custom provider without --model
- Unknown provider error
- Override provider via --provider flag
- Missing anthropic package error
- Missing openai package error
- Empty stdin prompt error
- Load skills from SKILL.md files
- Skills appended to system prompt
- Skip skills loading if directory missing
- Custom event log path via --event-log
- Run bash command and capture output
- Run bash command with stderr
- Bash command timeout after 300 seconds
- Read file that exists
- Read file that does not exist
- Truncate long file output
- Write file creates parent directories
- Edit file replaces exact string
- Edit file fails when string not found
- Edit file replaces only first occurrence
- List files excludes git and node_modules
- Search files finds pattern
- Search files handles no matches
- Agent stops at max iterations
- Wrap-up reminder injected at threshold
- Wrap-up reminder content for evolve mode
- Wrap-up reminder content for bootstrap mode
- Session ends on end_turn stop reason
- Estimate tokens from text
- Trim context when exceeding limit
- Preserve recent messages during trim
- Trim only tool result content
- Log session start with provider and model
- Log tool call with input preview
- Log tool result with duration
- Log token usage per API response
- Log session end with reason
- Parse poppins.yml with agent section
- Apply defaults when poppins.yml missing
- Deep merge file config with defaults
- Get single config value via dot notation
- Search parent directories for poppins.yml
- Trust repo owner's issues directly
- Trust community issue with agent-approved label from owner
- Reject community issue with agent-approved from non-owner
- Verify label applier via GitHub events API
- Format issue as markdown
- Truncate long issue body
- Sort issues by reaction count
- Mark user content with boundaries
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
- Load BDD config before session
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
- Exclude management files from worktree commits
- Branch naming convention with timestamp
- Calculate has_work flag
- Guard warning for minimal work with uncovered scenarios
- Handle push failure gracefully
- Handle missing git remote
- Generate scenario slug from name
- Slug truncates to 60 characters
- Check for existing lock file
- Detect stale lock from dead PID
- Write lock file with session metadata
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
- Find test line matching scenario
- Insert marker above test function
- Skip if marker already exists
- Dry run mode shows planned changes
- Apply mode modifies files
- Load .env file into environment
- Skip comment lines in .env
- Environment variables override .env
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
- Handle test file that cannot be read
- Tool output formatting with iteration tag
- Tool icons for different tool types
- Detect Moonshot provider
- Detect Dashscope provider
- Moonshot default model
- Dashscope default model
- Groq default model
- Ollama default model
- Custom provider requires api_key string placeholder
- Ollama provider uses "ollama" as api_key
- Mode flag affects wrap-up message content
- Bootstrap mode agent prompt
- Handle scenario with special characters in name
- Handle concurrent scenario locks
- Issue response file format parsing
