---
title: Introduction
description: What poppins is and why it exists.
---

poppins (**B**ehaviour and **A**I **D**riven **D**evelopment) is a meta-framework where an AI agent builds and maintains a project driven entirely by BDD specifications.

## The idea

You describe **what** you want built using [Gherkin](https://cucumber.io/docs/gherkin/) scenarios. An AI agent figures out **how** to build it — writing tests first, then writing the minimum code to make them pass.

```mermaid
graph LR
    You["You write BDD.md"] --> Agent["AI agent reads spec"]
    Agent --> Tests["Writes tests first"]
    Tests --> Code["Writes code"]
    Code --> Commit["Commits when green"]
    Commit --> You
```

## Three pillars

poppins has three parts that work together:

```mermaid
graph TD
    subgraph poppins["poppins — the meta-framework"]
        BDD["BDD Spec Format\n(BDD.md + frontmatter)\nWhat to build"]
        LOOP["Evolve Loop\n(scripts/ + GitHub Actions)\nHow to build it"]
        CONTRACT["Agent Behaviour Contract\n(IDENTITY.md)\nHow the agent must behave"]
    end

    BDD -->|"parsed by"| LOOP
    CONTRACT -->|"governs"| LOOP
    LOOP -->|"implements scenarios from"| BDD
    LOOP -->|"journals progress to"| BDD

    style BDD fill:#a855f7,color:#fff,stroke:none
    style LOOP fill:#3b82f6,color:#fff,stroke:none
    style CONTRACT fill:#6366f1,color:#fff,stroke:none
    style poppins fill:#1e1e2e,color:#cdd6f4,stroke:#45475a
```

1. **BDD Spec Format** — `BDD.md` with YAML frontmatter declaring language, build/test commands, and Gherkin scenarios. This is the only file you edit.
2. **Evolve Loop** — the `scripts/` + GitHub Actions cron that drives the agent: find uncovered scenario → write test → write code → commit.
3. **Agent Behaviour Contract** — `IDENTITY.md`, the agent's constitution. It defines what the agent can do, what it must never do, and how it measures progress.

## What makes it different

- **Spec-driven** — the agent never builds anything that isn't in `BDD.md`
- **Test-first** — every scenario gets a test before any implementation code
- **Self-healing** — if the build breaks, the agent reverts and journals the failure
- **Multi-provider** — works with Anthropic, OpenAI, Groq, Alibaba, Moonshot, or local Ollama
- **Language-agnostic** — TypeScript, Python, Rust, Go, Java — just set the frontmatter
