---
title: How It Works
description: A deep dive into the poppins architecture and data flow.
---

## System overview

```mermaid
graph TB
    subgraph User["User Layer"]
        BDD["BDD.md\n(Your spec)"]
        Issues["GitHub Issues"]
    end

    subgraph Framework["poppins Framework"]
        Identity["IDENTITY.md\n(Agent rules)"]
        Evolve["evolve.sh\n(Orchestrator)"]
        Agent["agent.py\n(AI runner)"]
        Coverage["check_bdd_coverage.py"]
        Parser["parse_bdd_config.py"]
        Setup["setup_env.sh"]
    end

    subgraph AI["AI Providers"]
        Anthropic["Anthropic"]
        OpenAI["OpenAI"]
        Groq["Groq"]
        Others["Moonshot / Qwen / Ollama"]
    end

    subgraph Output["Output"]
        Code["Source Code + Tests"]
        Journal["JOURNAL.md"]
        Status["BDD_STATUS.md"]
        Learnings["LEARNINGS.md"]
    end

    BDD --> Parser
    Parser --> Evolve
    Identity --> Agent
    Evolve --> Setup
    Evolve --> Coverage
    Evolve --> Agent
    Issues --> Evolve
    Agent --> Anthropic
    Agent --> OpenAI
    Agent --> Groq
    Agent --> Others
    Agent --> Code
    Agent --> Journal
    Agent --> Status
    Agent --> Learnings

    style BDD fill:#a855f7,color:#fff,stroke:none
    style Identity fill:#6366f1,color:#fff,stroke:none
    style Evolve fill:#3b82f6,color:#fff,stroke:none
    style Agent fill:#3b82f6,color:#fff,stroke:none
    style Code fill:#22c55e,color:#fff,stroke:none
```

## Data flow during a session

```mermaid
sequenceDiagram
    participant GH as GitHub Actions
    participant Evolve as evolve.sh
    participant Parser as parse_bdd_config.py
    participant Setup as setup_env.sh
    participant Cov as check_bdd_coverage.py
    participant Agent as agent.py
    participant AI as AI Provider

    GH->>Evolve: Trigger (cron/manual)
    Evolve->>Parser: Parse BDD.md frontmatter
    Parser-->>Evolve: language, build_cmd, test_cmd...
    Evolve->>Setup: Install toolchain
    Evolve->>Evolve: Verify build + tests
    Evolve->>Cov: Check scenario coverage
    Cov-->>Evolve: Coverage report
    Evolve->>Evolve: Fetch GitHub issues
    Evolve->>Agent: Prompt with context
    Agent->>AI: Messages + tool calls
    AI-->>Agent: Responses
    Agent->>Agent: Execute tools (bash, read, write, edit)
    Agent-->>Evolve: Session complete
    Evolve->>Evolve: Verify build + tests (post)
    Evolve->>Evolve: Ensure journal written
    Evolve->>GH: git push
```

## Provider detection

The agent auto-detects which AI provider to use based on environment variables:

```mermaid
flowchart TD
    Start([Start]) --> A{ANTHROPIC_API_KEY?}
    A -- Yes --> Anthropic[Use Anthropic\nclaude-haiku-4-5]
    A -- No --> B{MOONSHOT_API_KEY?}
    B -- Yes --> Moonshot[Use Moonshot\nkimi-latest]
    B -- No --> C{DASHSCOPE_API_KEY?}
    C -- Yes --> Dashscope[Use Alibaba\nqwen-max]
    C -- No --> D{OPENAI_API_KEY?}
    D -- Yes --> OpenAI[Use OpenAI\ngpt-4o]
    D -- No --> E{GROQ_API_KEY?}
    E -- Yes --> Groq[Use Groq\nllama-3.3-70b]
    E -- No --> F{OLLAMA_HOST?}
    F -- Yes --> Ollama[Use Ollama\nlocal model]
    F -- No --> Error([No provider found])

    style Anthropic fill:#a855f7,color:#fff,stroke:none
    style Error fill:#ef4444,color:#fff,stroke:none
```

Anthropic uses its native API with tool use. All other providers use the OpenAI-compatible chat completions API.

## Tool system

The agent has 6 tools available:

| Tool | Description |
|------|-------------|
| `bash` | Run any shell command |
| `read_file` | Read file contents |
| `write_file` | Create or overwrite a file |
| `edit_file` | Replace a string in a file |
| `list_files` | List files recursively |
| `search_files` | Search for patterns across files |

The agent loop runs up to **75 iterations**. At iteration 70, a wrap-up reminder is injected to ensure the session ends cleanly with a journal entry.

## Safety guarantees

```mermaid
flowchart TD
    A[Agent makes changes] --> B{Build passes?}
    B -- Yes --> C{Tests pass?}
    C -- Yes --> D[Commit]
    B -- No --> E[Fix attempt 1]
    C -- No --> E
    E --> F{Fixed?}
    F -- Yes --> D
    F -- No --> G[Fix attempt 2]
    G --> H{Fixed?}
    H -- Yes --> D
    H -- No --> I[Fix attempt 3]
    I --> J{Fixed?}
    J -- Yes --> D
    J -- No --> K[Revert ALL session changes]

    D --> L[Push]
    K --> L

    style D fill:#22c55e,color:#fff,stroke:none
    style K fill:#ef4444,color:#fff,stroke:none
    style L fill:#3b82f6,color:#fff,stroke:none
```

- The agent **never pushes broken code** — post-session verification catches failures
- After 3 failed fix attempts, the **entire session is reverted**
- The agent **never modifies** `IDENTITY.md`, `evolve.sh`, or `.github/workflows/`
- The agent **never builds features** not described in `BDD.md`
