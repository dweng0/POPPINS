---
title: Installation
description: How to install poppins in a new or existing project.
---

## Scaffold a new project

```bash
mkdir my-project && cd my-project
curl -fsSL https://raw.githubusercontent.com/dweng0/POPPINS/main/install.sh | bash
```

This downloads all framework files, creates a `BDD.md` template, and initialises a git repo. A `.poppins` manifest tracks the framework version — run the same command again to update.

## Update an existing project

```bash
# Update to latest
./install.sh --update

# Pin to a specific version
./install.sh --version v1.2.0
```

When updating, poppins automatically archives your journal files before overwriting framework files. Your `BDD.md` is never overwritten.

## What gets installed

After running the installer, your project will contain:

```
my-project/
├── .github/workflows/
│   └── evolve.yml          # Cron job (every 8h)
├── scripts/
│   ├── evolve.sh            # Main evolution loop
│   ├── agent.py             # AI agent runner
│   ├── check_bdd_coverage.py
│   ├── parse_bdd_config.py
│   └── setup_env.sh
├── BDD.md                   # Your spec (edit this!)
├── BDD.example.md           # Example spec for reference
├── IDENTITY.md              # Agent constitution
├── JOURNAL.md               # Agent session logs
├── JOURNAL_INDEX.md         # One-line-per-session index
├── LEARNINGS.md             # Agent's research cache
├── BDD_STATUS.md            # Coverage status
└── .poppins                 # Framework manifest
```

## Prerequisites

- **Python 3.8+** — for the agent runner
- **Git** — for version control
- **An AI provider API key** — see [Quick Start](/POPPINS/getting-started/quick-start/) for options
- **Language toolchain** — whatever your project needs (Node, Rust, Go, etc.)

## Install agent dependencies

```bash
pip install anthropic openai
```

Only one package is needed depending on your provider — `anthropic` for Anthropic, `openai` for all others (OpenAI, Groq, Moonshot, Alibaba, Ollama all use the OpenAI-compatible client).
