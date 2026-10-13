#!/usr/bin/env bash
# run_agent.sh — run one agent session with the configured harness.
#
# Reads the session prompt from stdin. Extra arguments are passed to the
# native agent (scripts/agent.py) unchanged.
#
# Harness is chosen by poppins.yml `agent.harness` (POPPINS_AGENT_HARNESS)
# or the AGENT_HARNESS environment variable:
#   native  — scripts/agent.py (default)
#   hermes  — NousResearch hermes-agent in one-shot mode
#
# Hermes settings (poppins.yml `agent.*`, env overrides in brackets):
#   hermes_cmd   command to invoke             [HERMES_CMD]       default: hermes
#   base_url     OpenAI-compatible endpoint    [HERMES_BASE_URL]  falls back to agent.base_url
#   max_iterations  passed as --max-turns
#   MODEL        model name (already resolved by evolve.sh)
set -uo pipefail

HARNESS="${AGENT_HARNESS:-${POPPINS_AGENT_HARNESS:-native}}"

case "$HARNESS" in
    native)
        exec python3 scripts/agent.py "$@"
        ;;
    hermes)
        HERMES_CMD="${HERMES_CMD:-${POPPINS_AGENT_HERMES_CMD:-hermes}}"
        BASE_URL="${HERMES_BASE_URL:-${POPPINS_AGENT_BASE_URL:-${CUSTOM_BASE_URL:-}}}"
        API_KEY="${CUSTOM_API_KEY:-${POPPINS_AGENT_API_KEY:-local}}"
        MAX_TURNS="${POPPINS_AGENT_MAX_ITERATIONS:-75}"

        if ! command -v "${HERMES_CMD%% *}" >/dev/null 2>&1; then
            echo '{"type":"error","message":"hermes harness selected but hermes is not installed"}'
            exit 1
        fi

        PROMPT="$(cat)"
        ARGS=(chat -q "$PROMPT" --oneshot --max-turns "$MAX_TURNS" --api-key "$API_KEY")
        [ -n "${MODEL:-}" ] && ARGS+=(--model "$MODEL")
        [ -n "$BASE_URL" ] && ARGS+=(--base-url "$BASE_URL")

        # shellcheck disable=SC2086
        exec $HERMES_CMD "${ARGS[@]}"
        ;;
    *)
        echo "{\"type\":\"error\",\"message\":\"unknown agent harness: $HARNESS\"}"
        exit 1
        ;;
esac
