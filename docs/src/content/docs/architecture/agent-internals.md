---
title: Agent Internals
description: How agent.py works — the multi-provider AI agent runner.
---

`scripts/agent.py` is the brain of poppins. It reads a prompt from stdin, runs an agent loop with tool use, and prints structured output.

## Architecture

```mermaid
graph TD
    subgraph agent.py
        Detect["detect_provider()"]
        Loop["Agent Loop\n(up to 75 iterations)"]
        Tools["run_tool()"]
        Print["print_tool_call()"]
    end

    stdin["Prompt\n(from evolve.sh)"] --> Detect
    Detect --> Loop
    Loop -->|"tool_use response"| Tools
    Tools -->|"result"| Loop
    Loop -->|"text response"| Print
    Loop -->|"end_turn / stop"| Done([Done])

    style Loop fill:#3b82f6,color:#fff,stroke:none
    style Done fill:#22c55e,color:#fff,stroke:none
```

## Two code paths

The agent supports two different API formats:

### Anthropic (native)
Uses the `anthropic` Python SDK directly with Anthropic's tool use format:

```mermaid
sequenceDiagram
    participant Agent as agent.py
    participant API as Anthropic API

    Agent->>API: messages.create(tools=TOOLS)
    API-->>Agent: content: [text, tool_use]
    Agent->>Agent: Execute tool
    Agent->>API: tool_result
    API-->>Agent: content: [text]
    Note over Agent: stop_reason == "end_turn" → done
```

### OpenAI-compatible (all others)
Uses the `openai` Python SDK. Works with OpenAI, Groq, Moonshot, Alibaba, and Ollama:

```mermaid
sequenceDiagram
    participant Agent as agent.py
    participant API as OpenAI-compatible API

    Agent->>API: chat.completions.create(tools=TOOLS_OPENAI)
    API-->>Agent: message.tool_calls
    Agent->>Agent: Execute tool
    Agent->>API: role: "tool", content: result
    API-->>Agent: message.content
    Note over Agent: finish_reason == "stop" → done
```

## Iteration limits

| Threshold | What happens |
|-----------|-------------|
| 70 | Wrap-up reminder injected — stop starting new work |
| 75 | Hard stop — agent loop exits |

The wrap-up message tells the agent to finish current work, update coverage, write a journal entry, and commit.

## Tool output limits

All tool outputs are truncated to **12,000 characters** to stay within context limits. File reads and bash output are capped at this limit.

## CI-aware logging

When running in GitHub Actions (`CI=true`), the agent uses collapsible log groups:

```
::group::Agent [3/75]: Implementing the add task scenario...
  $ npm test
  ✓ 3 tests passed
::endgroup::
```

This keeps CI logs readable even for long sessions.

## Skills system

The agent can load skills from a `skills/` directory. Each skill is a `SKILL.md` file that gets appended to the system prompt. This lets you extend the agent's behaviour without modifying `agent.py`.
