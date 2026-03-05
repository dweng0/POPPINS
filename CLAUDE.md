# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## What This Is

BAADD (Behaviour and AI Driven Development) — a framework where an AI agent builds and maintains a project driven entirely by BDD specifications in `BDD.md`.

## Key Files

- `BDD.md` — the spec (frontmatter configures language/build/test commands)
- `IDENTITY.md` — agent constitution (do not modify)
- `scripts/evolve.sh` — main evolution loop
- `scripts/agent.py` — AI agent runner (requires `pip install anthropic`)
- `scripts/check_bdd_coverage.py` — verifies all scenarios have test coverage
- `scripts/parse_bdd_config.py` — reads BDD.md frontmatter as shell variables
- `scripts/setup_env.sh` — installs language-specific toolchain

## Running

```bash
# Install agent dependency
pip install anthropic

# Run one evolution session
ANTHROPIC_API_KEY=sk-... ./scripts/evolve.sh

# Check BDD coverage manually
python3 scripts/check_bdd_coverage.py BDD.md
```

## Safety Rules

- Never modify `IDENTITY.md`, `scripts/evolve.sh`, or `.github/workflows/`
- Every change must pass build and tests
- Only implement features described in `BDD.md`
- Write tests before writing implementation code
