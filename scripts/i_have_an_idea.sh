#!/bin/bash
# scripts/i_have_an_idea.sh — Grill yourself on an idea, then optionally append to BDD.md.
#
# Usage:
#   ./scripts/i_have_an_idea.sh "I want to add user authentication"
#   ./scripts/i_have_an_idea.sh   # prompts interactively

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GRILL_PY="$SCRIPT_DIR/grill.py"
BDD_MD="$REPO_ROOT/BDD.md"
SCENARIO_TMP="/tmp/baadd_grill_scenario.md"

# ── Prereqs ──
if ! python3 -c "import anthropic" 2>/dev/null; then
    echo "Error: run 'pip install anthropic' first"
    exit 1
fi

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    if [ -f "$REPO_ROOT/.env" ]; then
        # shellcheck disable=SC1090
        set -a && source "$REPO_ROOT/.env" && set +a
    fi
fi

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "Error: ANTHROPIC_API_KEY not set"
    exit 1
fi

# ── Run grill session ──
rm -f "$SCENARIO_TMP"

if [ $# -gt 0 ]; then
    python3 "$GRILL_PY" "$@"
else
    python3 "$GRILL_PY"
fi

# ── Check output ──
if [ ! -f "$SCENARIO_TMP" ]; then
    echo "No scenario produced. Exiting."
    exit 0
fi

echo ""
read -r -p "Append this scenario to BDD.md? [y/N] " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Not appended. Scenario saved at $SCENARIO_TMP"
    exit 0
fi

# ── Append to BDD.md ──
# Find the last Feature block and append after it, or just append at end
echo "" >> "$BDD_MD"
cat "$SCENARIO_TMP" >> "$BDD_MD"

echo ""
echo "Appended to BDD.md."
echo "Review with: tail -20 BDD.md"
echo "Then run: ./scripts/evolve.sh"
