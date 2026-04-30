# BAADD — Behaviour and AI Driven Development
<div align="center">
<img src="cute_sheep.svg" width="180" alt="BAADD mascot"/>

*"BAADD"*

</div>

## BDD Drives everything
Build software with AI agents that read your BDD spec, write tests first, then code to pass them — all while journaling their progress. No config needed; just set your API key and let the agent evolve your project on schedule.

### Features
- **Evolve** - the agent finds uncovered scenarios, writes tests, implements code, and commits — all automatically. via a github action cron job.
- **Orchestrate** - for larger projects, spawn multiple agents in parallel, ordered by an AI orchestrator.
- **Interactive mode** - run evolution sessions interactively with Claude Code, guiding the agent

## Supported Models
- BAADD supports **any LLM provider with an API** — just set the corresponding environment variable. **Local or otherwise**
- BAADD **auto-detects your provider** from environment variables. Set one API key and run — no config needed.

#### Quickstart:
```` bash curl -fsSL https://raw.githubusercontent.com/dweng0/BAADD/main/install.sh | bash
````

| Provider | Environment Variable | Default Model | Notes |
|----------|---------------------|---------------|-------|
| **Anthropic** | `ANTHROPIC_API_KEY` | `claude-sonnet-4-5` | Highest priority; native tool use |
| **OpenAI** | `OPENAI_API_KEY` | `gpt-4o` | |
| **Groq** | `GROQ_API_KEY` | `llama-3.3-70b-versatile` | Fast inference |
| **Alibaba / Qwen** | `DASHSCOPE_API_KEY` | `qwen-max` | OpenAI-compatible endpoint |
| **Moonshot / Kimi** | `MOONSHOT_API_KEY` | `moonshot-v1-8k` | OpenAI-compatible endpoint |
| **Ollama** | `OLLAMA_HOST` | _(pass `--model`_) | Local models, no API key required |
| **Custom Provider** | `CUSTOM_API_KEY`, `CUSTOM_BASE_URL` | _(user-defined)_ | Custom integrations |

Provider priority (first key found wins): `ANTHROPIC_API_KEY` > `MOONSHOT_API_KEY` > `DASHSCOPE_API_KEY` > `OPENAI_API_KEY` > `GROQ_API_KEY` > `OLLAMA_HOST`

Override the model at any time with `--model <name>` or force a provider with `--provider <name>`.

---

## What is it?

BAADD is a **meta-framework / template** — not a library you install, but a pattern you adopt. You bring your spec; BAADD brings the agent, the loop, and the rules that keep it honest.

The three parts that make it work:

```mermaid
graph TD
    subgraph BAADD["BAADD — the meta-framework"]
        BDD["📄 BDD Spec Format\n(BDD.md + frontmatter)\nWhat to build"]
        LOOP["🔄 Evolve Loop\n(scripts/ + GitHub Actions)\nHow to build it"]
        CONTRACT["📜 Agent Behaviour Contract\n(IDENTITY.md)\nHow the agent must behave"]
    end

    BDD -->|"parsed by"| LOOP
    CONTRACT -->|"governs"| LOOP
    LOOP -->|"implements scenarios from"| BDD
    LOOP -->|"journals progress to"| BDD

    style BDD fill:#a855f7,color:#fff,stroke:none
    style LOOP fill:#3b82f6,color:#fff,stroke:none
    style CONTRACT fill:#6366f1,color:#fff,stroke:none
    style BAADD fill:#1e1e2e,color:#cdd6f4,stroke:#45475a
```

- **BDD Spec Format** — `BDD.md` with YAML frontmatter declaring language, build/test commands, and Gherkin scenarios. This is the only file you edit.
- **Evolve Loop** — the `scripts/` + GitHub Actions cron that drives the agent: find uncovered scenario → write test → write code → commit.
- **Agent Behaviour Contract** — `IDENTITY.md`, the agent's constitution. It defines what the agent is allowed to do, what it must never do, and how it measures progress.

> **You write the spec. The agent writes the code.**

### Using Claude Code?

Run `evolve` in your terminal and Claude Code will read the spec, pick the next uncovered scenario, write the test, implement it, and commit — then ask if you want to continue.

---

## How it works

```mermaid
flowchart TD
    A([📝 You write BDD.md]) --> B[GitHub Actions\ncron every 8h]
    B --> C{Uncovered or\nfailing scenarios?}
    C -- No --> D([✅ Nothing to do])
    C -- Yes --> E[Agent reads\nBDD.md]
    E --> F[Writes tests first]
    F --> G[Writes code to\nmake tests pass]
    G --> H{Tests pass and\ncoverage maintained?}
    H -- No --> G
    H -- Yes --> I[Agent commits]
    I --> J([📓 Journals session])
    I --> A

    style A fill:#a855f7,color:#fff,stroke:none
    style D fill:#22c55e,color:#fff,stroke:none
    style I fill:#3b82f6,color:#fff,stroke:none
    style J fill:#6366f1,color:#fff,stroke:none
```

1. You write `BDD.md` — features, scenarios, given/when/then
2. A GitHub Actions cron job fires every 8 hours
3. The AI agent reads `BDD.md`, finds uncovered or failing scenarios
4. It writes tests first, then writes code to make them pass
5. It commits only when tests pass and BDD coverage is maintained
6. It journals what it did and responds to GitHub issues

> **The agent never builds anything that isn't in BDD.md.**

---

## Setup

### 1. Scaffold a new project

```bash
mkdir my-project && cd my-project
curl -fsSL https://raw.githubusercontent.com/dweng0/BAADD/main/install.sh | bash
```

This downloads all framework files, creates a `BDD.md` template, and initialises a git repo. A `.BAADD` manifest is written to track the framework version — run the same command again at any time to update.

### 2. Configure BDD.md

Edit the frontmatter at the top of `BDD.md`:

```yaml
---
language: typescript        # rust | python | go | node | typescript | java
framework: react-vite       # or: none, express, django, etc. (informational)
build_cmd: npm run build
test_cmd: npm test
lint_cmd: npm run lint
fmt_cmd: npm run format
birth_date: 2026-01-01      # project start date (used for day counter)
---
```

Then write your features and scenarios below the frontmatter.

### 2b. Configure BAADD.yml (optional)

`BAADD.yml` controls how the agent runs — parallel workers, token limits, timeouts. The defaults work out of the box, but you can tune them:

```yaml
# BAADD.yml — HOW to build (BDD.md defines WHAT to build)
orchestration:
  max_parallel_agents: 3                    # workers per orchestrator run
  model_orchestrator: claude-haiku-4-5-20251001  # model for scenario ordering

agent:
  max_iterations: 75          # tool-call rounds per session
  wrap_up_at: 70              # when to inject wrap-up reminder
  max_tokens_per_response: 8192
  tool_output_limit: 12000    # max chars per tool result
  session_timeout: 3600       # seconds
  context_window_limit: 100000 # auto-trims older results past this
  default_model: claude-haiku-4-5-20251001
```

This file is not overwritten on framework updates.

### 3. Add your API key

In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|------|-------|
| `ANTHROPIC_API_KEY` | your `sk-ant-...` key |

### 4. Install agent dependencies (local runs only)

```bash
pip install anthropic
```

### 5. Run manually

```bash
ANTHROPIC_API_KEY=sk-... ./scripts/evolve.sh
```

### 6. Let it run on schedule

Push to GitHub. The workflow runs automatically every 8 hours via cron.

Trigger manually: **Actions tab → Evolution → Run workflow**.

---

## Commands reference

### Project initialization and updates

```bash
# Initialize BAADD in a new project
curl -fsSL https://raw.githubusercontent.com/dweng0/BAADD/main/install.sh | bash

# Update BAADD framework to latest version (preserves your journals)
./install.sh --update

# Pin to a specific BAADD version
./install.sh --version v1.2.0
```

### Evolution and development

```bash
# Run one evolution session manually (tests one scenario)
ANTHROPIC_API_KEY=sk-... ./scripts/evolve.sh

# Check BDD scenario coverage
python3 scripts/check_bdd_coverage.py BDD.md

# Run your project's build command (from BDD.md)
python3 -m py_compile pyken.py  # or whatever your build_cmd is

# Run your project's tests (from BDD.md)
.venv/bin/pytest tests/  # or whatever your test_cmd is
```

### Parallel evolution (orchestrator)

```bash
# Run the orchestrator — orders scenarios with AI, spawns parallel agents
ANTHROPIC_API_KEY=sk-... python3 scripts/orchestrate.py

# Preview the plan without executing
python3 scripts/orchestrate.py --dry-run

# Override max parallel agents
python3 scripts/orchestrate.py --max-agents 2
```

### Interactive evolution (Claude Code only)

```bash
# Run evolution sessions interactively with Claude Code
/evolve
```

### BDD coverage markers

```bash
# Dry run — see which tests would get markers
python3 scripts/add_bdd_markers.py BDD.md

# Apply markers to existing test files
python3 scripts/add_bdd_markers.py BDD.md --apply
```

Tests should include a BDD marker comment linking them to their scenario:

```python
# BDD: Successful login
def test_successful_login():
```

```typescript
// BDD: Successful login
test('successful login', () => {
```

The coverage checker uses these markers for exact matching, falling back to heuristic name matching for unmarked tests.

### Useful tools

```bash
# See what the agent will work on next
cat JOURNAL_INDEX.md

# Read full session logs
cat JOURNAL.md

# Check framework version
cat .BAADD | python3 -c "import sys,json; print(json.load(sys.stdin)['version'])"
```

---

## File reference

| File | Purpose |
|------|---------|
| `BDD.md` | The spec — edit this to drive development |
| `BAADD.yml` | Agent/orchestrator config — edit to tune behaviour |
| `IDENTITY.md` | Agent constitution — do not modify |
| `JOURNAL.md` | Agent's full session logs — auto-written |
| `JOURNAL_INDEX.md` | One-line-per-session summary index — auto-generated |
| `LEARNINGS.md` | Agent's cached research — auto-written |
| `BDD_STATUS.md` | Scenario coverage status — auto-generated |
| `scripts/evolve.sh` | Main evolution loop — do not modify |
| `scripts/orchestrate.py` | Parallel orchestrator — AI-ordered, multi-agent |
| `scripts/agent.py` | The AI agent runner |
| `scripts/check_bdd_coverage.py` | Scenario coverage checker (supports BDD markers) |
| `scripts/add_bdd_markers.py` | Upgrade tool — adds BDD markers to existing tests |
| `scripts/parse_bdd_config.py` | BDD.md frontmatter parser |
| `scripts/parse_BAADD_config.py` | BAADD.yml config parser |
| `scripts/setup_env.sh` | Language-aware toolchain installer |

---

## Writing good BDD scenarios

```gherkin
Feature: User authentication
    As a user
    I want to log in with my email and password
    So that I can access my account

    Scenario: Successful login
        Given I am on the login page
        When I enter valid email and password
        Then I am redirected to my dashboard

    Scenario: Wrong password
        Given I am on the login page
        When I enter a valid email but wrong password
        Then I see "Invalid email or password"
```

Keep scenarios:

- **Specific** — one behaviour per scenario
- **Observable** — the `Then` clause must be testable
- **Independent** — each scenario stands alone

---

## Using Claude Code interactively

If you have [Claude Code](https://claude.ai/code) installed, you can run evolution sessions interactively instead of waiting for the cron:

```
> evolve
```

Claude Code will read the spec, pick the next uncovered scenario, write the test, implement it, and commit — then ask if you want to continue. This uses the same workflow as the GitHub cron but lets you guide the session in real time.

---

## Skills

The `skills/` directory contains optional guidance documents that are appended to the agent's system prompt in every pipeline (`evolve.sh`, `orchestrate.py`, and Claude Code interactive). Each skill is a `SKILL.md` file describing a specific discipline. You can add, remove, or edit skills without touching any script.

### Built-in skills

| Skill | When the agent uses it |
|-------|----------------------|
| `skills/evolve/` | Core TDD/BDD cycle — the prime directive for every implementation session |
| `skills/self-assess/` | Coverage gap analysis — finding uncovered scenarios and misfiled tests |
| `skills/hexagonal-architecture/` | Ports and adapters design when adding new I/O boundaries |
| `skills/communicate/` | Writing journal entries and GitHub issue responses |
| `skills/research/` | Web search when implementing something unfamiliar |
| `skills/diagnose/` | Structured debug loop for hard bugs — build a feedback loop, hypothesise, instrument, fix |
| `skills/zoom-out/` | Map unfamiliar modules before navigating them |

### Pipeline fit

| Pipeline | How skills load | Key skills |
|----------|----------------|-----------|
| `scripts/evolve.sh` | `agent.py --skills ./skills` — all skills in system prompt | `evolve`, `diagnose` (fix loop), `zoom-out` (navigate code) |
| `scripts/orchestrate.py` | Same `agent.py` call per sub-agent (PM-PLAN, SE, TESTER, ACCEPT) | SE uses `evolve` + `diagnose`; PM-PLAN uses `zoom-out` |
| Claude Code interactive | Skills loaded via Claude Code's skill system | All skills available on demand |

### Adding a skill

1. Create `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`) and markdown body.
2. The agent picks it up automatically — no script changes needed.

To disable a skill without deleting it, move it out of `skills/` (e.g., to `skills/_disabled/`).

---

## Guardrails

The orchestrator applies deterministic checks before merging any worktree branch to prevent the SE agent from causing unintended damage.

### File deletion guard

Before merging, the orchestrator diffs the worktree branch against the merge base and rejects any branch that deletes an existing file unless the PM explicitly approved the deletion in `PLAN.md`.

The PM declares approved deletions in section 5 of `PLAN.md`:

```markdown
## 5. Files to delete (optional)

- scripts/old_helper.py — superseded by the new unified loader in this scenario
```

Any file deleted by the SE that is not listed here causes the work to be thrown away. The PM is instructed to populate this section only when the scenario genuinely requires removing a file.

### Considerations for improvement

- **Truncation detection** — the current guard catches `git rm`-style deletions but not files that are overwritten with empty or near-empty content. A secondary check using `git diff --numstat` to flag files where all lines were removed and nothing was added would cover this case. The threshold for "suspiciously large removal" is context-dependent, which is why this has not been added yet.

---

## GitHub issues

Label issues with `agent-input` to have the agent pick them up.

If an issue proposes a new feature, the agent will add it to `BDD.md` as a Scenario before implementing it.

---

## Links

- **BAADD Framework**: https://github.com/dweng0/BAADD
- **Documentation**: See the `CLAUDE.md` file in your project for detailed guidance
- **GitHub Issues**: Use `agent-input` label to task the AI agent
