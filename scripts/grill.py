#!/usr/bin/env python3
"""
grill.py — Interactive idea grilling session with optional docs integration.

Grills the user with questions about their idea one at a time,
recommends answers, then drafts a BDD Scenario.

With CONTEXT.md present: challenges terms against domain glossary,
updates CONTEXT.md inline, offers ADRs for hard decisions.

Usage:
    python3 scripts/grill.py "I want to add user authentication"
    python3 scripts/grill.py  # prompts for idea interactively
"""

import json
import os
import re
import sys
from pathlib import Path


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

BASE_SYSTEM_PROMPT = """You are grilling the user about their idea for a software feature.
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

DOCS_ADDON = """

## Domain awareness

{context_block}

Additional rules:
- If the user uses a term that conflicts with or is absent from the glossary above, call it out immediately.
- Propose precise canonical terms when vague language emerges.
- Stress-test domain relationships with concrete edge-case scenarios.
- If a stated assumption contradicts how the codebase works, surface it."""

INTRO = """Grill session started. Answer questions or press Enter to accept recommendation.
Type 'q' to quit without saving.
─────────────────────────────────────────────────────────────────\n"""


# ── docs helpers ──────────────────────────────────────────────────────────────


def find_context_file(root: Path) -> Path | None:
    """Return CONTEXT.md path if it exists (single-context repos only)."""
    candidate = root / "CONTEXT.md"
    return candidate if candidate.exists() else None


def find_adr_dir(root: Path) -> Path:
    """Return docs/adr/ dir (create if absent)."""
    d = root / "docs" / "adr"
    d.mkdir(parents=True, exist_ok=True)
    return d


def next_adr_number(adr_dir: Path) -> int:
    existing = sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md"))
    if not existing:
        return 1
    last = existing[-1].name[:4]
    return int(last) + 1


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s]+", "-", text)


def read_context(path: Path) -> str:
    return path.read_text().strip()


def build_system_prompt(context_text: str | None) -> str:
    if not context_text:
        return BASE_SYSTEM_PROMPT
    block = f"Existing domain glossary (CONTEXT.md):\n\n{context_text}"
    return BASE_SYSTEM_PROMPT + DOCS_ADDON.format(context_block=block)


# ── AI helpers ────────────────────────────────────────────────────────────────


def stream_response(client, system: str, messages: list) -> str:
    full = []
    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=system,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full.append(text)
    print()
    return "".join(full)


def call_once(client, prompt: str) -> str:
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def extract_scenario(text: str) -> str:
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


# ── post-session docs update ──────────────────────────────────────────────────


def extract_doc_updates(client, conversation: list, existing_context: str) -> dict:
    """Ask Claude to pull new terms and ADR candidates from the conversation."""
    conv_text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in conversation)
    existing_block = (
        f"Existing CONTEXT.md:\n{existing_context}\n\n" if existing_context else ""
    )
    prompt = f"""{existing_block}Grill session transcript:
{conv_text}

Analyse the transcript and respond with valid JSON only — no prose, no markdown fences:
{{
  "new_terms": [
    {{"term": "...", "definition": "one sentence"}},
    ...
  ],
  "new_relationships": [
    "X contains many Y (1..*)",
    ...
  ],
  "adr_candidates": [
    {{
      "title": "short title",
      "context": "one sentence",
      "decision": "one sentence",
      "why": "one sentence"
    }},
    ...
  ]
}}

Rules:
- new_terms: only project-specific terms not already in CONTEXT.md, not generic programming terms.
- new_relationships: only if a cardinality or ownership relationship was established.
- adr_candidates: only decisions that are (1) hard to reverse, (2) surprising without context, AND (3) result of genuine trade-offs. Empty list if none.
- If nothing new, return empty lists."""
    raw = call_once(client, prompt)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # try to extract JSON from response
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
    return {"new_terms": [], "new_relationships": [], "adr_candidates": []}


def append_to_context(path: Path, updates: dict) -> bool:
    """Append new terms/relationships to CONTEXT.md. Returns True if changed."""
    new_terms = updates.get("new_terms", [])
    new_rels = updates.get("new_relationships", [])
    if not new_terms and not new_rels:
        return False

    text = path.read_text() if path.exists() else ""

    if new_terms:
        if "# Language" not in text:
            text += "\n\n# Language\n"
        for t in new_terms:
            entry = f"- **{t['term']}**: {t['definition']}"
            if entry not in text:
                text = text.rstrip() + f"\n{entry}"

    if new_rels:
        if "# Relationships" not in text:
            text += "\n\n# Relationships\n"
        for r in new_rels:
            entry = f"- {r}"
            if entry not in text:
                text = text.rstrip() + f"\n{entry}"

    path.write_text(text.strip() + "\n")
    return True


def write_adr(adr_dir: Path, num: int, candidate: dict) -> Path:
    slug = slugify(candidate["title"])
    filename = f"{num:04d}-{slug}.md"
    path = adr_dir / filename
    content = f"""# ADR-{num:04d}: {candidate["title"]}

Context: {candidate["context"]}

Decision: {candidate["decision"]}

Why: {candidate["why"]}
"""
    path.write_text(content)
    return path


def prompt_yn(question: str) -> bool:
    print(f"{question} [y/N] ", end="", flush=True)
    try:
        return input().strip().lower() == "y"
    except (EOFError, KeyboardInterrupt):
        return False


# ── main ──────────────────────────────────────────────────────────────────────


def run():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    root = Path.cwd()
    context_path = find_context_file(root)
    context_text = read_context(context_path) if context_path else None
    system_prompt = build_system_prompt(context_text)

    if context_path:
        print(f"[docs] Loaded {context_path.relative_to(root)}")

    if len(sys.argv) > 1:
        idea = " ".join(sys.argv[1:])
    else:
        print("What's your idea? ", end="", flush=True)
        idea = input().strip()
        if not idea:
            print("No idea provided. Exiting.")
            sys.exit(0)

    print(INTRO)

    messages = [{"role": "user", "content": f"My idea: {idea}"}]
    scenario_text = None

    while True:
        response = stream_response(client, system_prompt, messages)
        messages.append({"role": "assistant", "content": response})

        if "GRILL_COMPLETE" in response:
            scenario_text = extract_scenario(response)
            break

        print(
            "\nYour answer (Enter = accept recommendation, q = quit): ",
            end="",
            flush=True,
        )
        try:
            user_input = input().strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            sys.exit(0)

        if user_input.lower() in ("q", "quit", "exit"):
            print("Session ended. No scenario saved.")
            sys.exit(0)

        if not user_input:
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

    out_path = "/tmp/baadd_grill_scenario.md"
    with open(out_path, "w") as f:
        f.write(scenario_text + "\n")
    print(f"\nScenario written to {out_path}")

    # ── docs post-processing ──────────────────────────────────────────────────
    print("\n[docs] Analysing session for domain updates…")
    updates = extract_doc_updates(client, messages, context_text or "")

    new_terms = updates.get("new_terms", [])
    new_rels = updates.get("new_relationships", [])
    adr_candidates = updates.get("adr_candidates", [])

    if new_terms or new_rels:
        target = context_path or (root / "CONTEXT.md")
        rel = target.relative_to(root)
        print("\nNew domain terms/relationships found:")
        for t in new_terms:
            print(f"  + {t['term']}: {t['definition']}")
        for r in new_rels:
            print(f"  + {r}")
        if prompt_yn(f"Append to {rel}?"):
            changed = append_to_context(target, updates)
            if changed:
                print(f"[docs] Updated {rel}")
    else:
        print("[docs] No new domain terms found.")

    if adr_candidates:
        adr_dir = find_adr_dir(root)
        num = next_adr_number(adr_dir)
        for candidate in adr_candidates:
            print(f"\nADR candidate: {candidate['title']}")
            print(f"  Context:  {candidate['context']}")
            print(f"  Decision: {candidate['decision']}")
            print(f"  Why:      {candidate['why']}")
            if prompt_yn("Write ADR?"):
                path = write_adr(adr_dir, num, candidate)
                print(f"[docs] Written {path.relative_to(root)}")
                num += 1

    sys.exit(0)


if __name__ == "__main__":
    run()
