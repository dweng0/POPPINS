#!/usr/bin/env python3
"""
grill.py — Interactive idea grilling session.

Grills the user with questions about their idea one at a time,
recommends answers, then drafts a BDD Scenario.

Usage:
    python3 scripts/grill.py "I want to add user authentication"
    python3 scripts/grill.py  # prompts for idea interactively
"""

import os
import sys
import textwrap


def load_dotenv(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]
            if key and key not in os.environ:
                os.environ[key] = value


load_dotenv()

try:
    import anthropic
except ImportError:
    print("Error: pip install anthropic", file=sys.stderr)
    sys.exit(1)

SYSTEM_PROMPT = """You are grilling the user about their idea for a software feature.
Your goal: extract enough detail to write a precise BDD Scenario.

Rules:
- Ask ONE question at a time. Never bundle multiple questions.
- After each question, provide YOUR recommended answer in brackets: [Recommended: ...]
- Ask about: who uses it, what triggers it, what the system does, what the outcome is, edge cases.
- When you have enough info (typically 6-10 questions), output EXACTLY this marker on its own line:
  GRILL_COMPLETE
  Then immediately write a BDD Scenario block in this format:

  Scenario: <name>
      Given <precondition>
      When <action>
      Then <outcome>

  Add And/But lines as needed. Be specific, not vague.
- Never ask more than 10 questions. Force output after 10.
- Keep questions short and direct. No filler."""

INTRO = """Grill session started. Answer questions or press Enter to accept recommendation.
Type 'q' to quit without saving.
─────────────────────────────────────────────────────────────────\n"""


def stream_response(client, messages):
    """Stream a response, return full text."""
    full = []
    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full.append(text)
    print()
    return "".join(full)


def extract_scenario(text):
    """Pull Scenario block from response text."""
    lines = text.split("\n")
    scenario_lines = []
    in_scenario = False
    for line in lines:
        if line.strip().startswith("Scenario:"):
            in_scenario = True
        if in_scenario:
            if line.strip() == "GRILL_COMPLETE":
                continue
            scenario_lines.append(line)
    return "\n".join(scenario_lines).strip()


def run():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    if len(sys.argv) > 1:
        idea = " ".join(sys.argv[1:])
    else:
        print("What's your idea? ", end="", flush=True)
        idea = input().strip()
        if not idea:
            print("No idea provided. Exiting.")
            sys.exit(0)

    print(INTRO)

    messages = [
        {"role": "user", "content": f"My idea: {idea}"},
    ]

    scenario_text = None

    while True:
        response = stream_response(client, messages)
        messages.append({"role": "assistant", "content": response})

        if "GRILL_COMPLETE" in response:
            scenario_text = extract_scenario(response)
            break

        # get user input
        print("\nYour answer (Enter = accept recommendation, q = quit): ", end="", flush=True)
        try:
            user_input = input().strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            sys.exit(0)

        if user_input.lower() in ("q", "quit", "exit"):
            print("Session ended. No scenario saved.")
            sys.exit(0)

        if not user_input:
            # extract recommendation from response
            rec = ""
            for line in response.split("\n"):
                if "[Recommended:" in line:
                    start = line.index("[Recommended:") + len("[Recommended:")
                    end = line.rindex("]") if "]" in line[start:] else len(line)
                    rec = line[start:end].strip()
                    break
            if rec:
                print(f"(Accepted: {rec})")
                user_input = rec
            else:
                print("(No recommendation found — please type your answer)")
                print("Your answer: ", end="", flush=True)
                try:
                    user_input = input().strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nAborted.")
                    sys.exit(0)

        messages.append({"role": "user", "content": user_input})
        print()

    if not scenario_text:
        print("No scenario generated.")
        sys.exit(1)

    print("\n─────────────────────────────────────────────────────────────────")
    print("GENERATED SCENARIO:\n")
    print(scenario_text)
    print("─────────────────────────────────────────────────────────────────")

    # write to temp file for the shell script to pick up
    out_path = "/tmp/baadd_grill_scenario.md"
    with open(out_path, "w") as f:
        f.write(scenario_text + "\n")

    print(f"\nScenario written to {out_path}")
    sys.exit(0)


if __name__ == "__main__":
    run()
