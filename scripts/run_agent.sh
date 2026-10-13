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
#   hermes_cmd       command to invoke                  [HERMES_CMD]       default: hermes
#   hermes_provider  provider name from ~/.hermes/config.yaml `providers:`
#                    (e.g. a local LM Studio entry)    [HERMES_PROVIDER]  default: hermes config
#   hermes_reasoning reasoning effort, e.g. none       [HERMES_REASONING] default: hermes config
#   hermes_toolsets  comma-separated toolsets          [HERMES_TOOLSETS]  default: hermes config
#                    (small local models do best with reasoning none and file,terminal,todo)
#   max_iterations   passed as --max-turns
#   MODEL            model name (already resolved by evolve.sh)
#
# hermes chat has no --base-url flag: endpoints and keys live in hermes' own config.
set -uo pipefail

HARNESS="${AGENT_HARNESS:-${POPPINS_AGENT_HARNESS:-native}}"

case "$HARNESS" in
    native)
        exec python3 scripts/agent.py "$@"
        ;;
    hermes)
        HERMES_CMD="${HERMES_CMD:-${POPPINS_AGENT_HERMES_CMD:-hermes}}"
        PROVIDER="${HERMES_PROVIDER:-${POPPINS_AGENT_HERMES_PROVIDER:-}}"
        MAX_TURNS="${POPPINS_AGENT_MAX_ITERATIONS:-75}"

        if ! command -v "${HERMES_CMD%% *}" >/dev/null 2>&1; then
            echo '{"type":"error","message":"hermes harness selected but hermes is not installed"}'
            exit 1
        fi

        PROMPT="$(cat)"
        ARGS=(chat -q "$PROMPT" --oneshot -Q --max-turns "$MAX_TURNS")
        [ -n "${MODEL:-}" ] && ARGS+=(--model "$MODEL")
        [ -n "$PROVIDER" ] && ARGS+=(--provider "$PROVIDER")
        REASONING="${HERMES_REASONING:-${POPPINS_AGENT_HERMES_REASONING:-}}"
        TOOLSETS="${HERMES_TOOLSETS:-${POPPINS_AGENT_HERMES_TOOLSETS:-}}"
        [ -n "$REASONING" ] && ARGS+=(--reasoning "$REASONING")
        [ -n "$TOOLSETS" ] && ARGS+=(-t "$TOOLSETS")

        # shellcheck disable=SC2086
        exec $HERMES_CMD "${ARGS[@]}"
        ;;
    *)
        echo "{\"type\":\"error\",\"message\":\"unknown agent harness: $HARNESS\"}"
        exit 1
        ;;
esac
