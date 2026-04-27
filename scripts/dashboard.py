#!/usr/bin/env python3
"""
BAADD Dashboard — live Rich TUI for scripts/orchestrate.py.

Wrapper mode (default):
    python3 scripts/dashboard.py [orchestrate args...]
    Launches orchestrate.py as a subprocess and shows a live Rich TUI.

Watcher mode:
    python3 scripts/dashboard.py --watch
    Attaches to an already-running orchestration by discovering worktrees.
"""

import argparse
import collections
import dataclasses
import datetime
import glob
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from typing import Dict, Optional

try:
    from rich.console import Console, Group
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    print("ERROR: rich not installed. Run: pip install rich", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PHASE_PREFIXES = [
    ("pm_plan",    "PM-PLAN"),
    ("se",         "SE"),
    ("tester",     "TESTER"),
    ("pm_accept",  "ACCEPT"),
]
_ALL_PHASE_LABELS = [label for _, label in _PHASE_PREFIXES]
_BAR_WIDTH = 20
_STALE_AFTER_S = 120
_MAX_LOG_LINES = 10
_MAX_SCENARIO_NAME = 60

# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    """Parse known args; return (Namespace, pass_through_list).

    Known flags: --watch, --refresh N
    Everything else is collected in the remainder list for forwarding to orchestrate.py.
    """
    parser = argparse.ArgumentParser(
        prog="dashboard.py",
        description="Rich TUI dashboard for scripts/orchestrate.py",
        add_help=True,
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        default=False,
        help="Watcher mode: attach to an already-running orchestration",
    )
    parser.add_argument(
        "--refresh",
        type=int,
        default=2,
        metavar="SECONDS",
        help="Polling interval in seconds (default: 2)",
    )
    namespace, remainder = parser.parse_known_args(argv)
    return namespace, remainder

# ---------------------------------------------------------------------------
# Worktree discovery
# ---------------------------------------------------------------------------

def discover_worktrees(main_dir=None):
    """Return list of /tmp/baadd-wt-* paths from git worktree list."""
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=main_dir or os.getcwd(),
            timeout=10,
        )
        if result.returncode != 0:
            return []
        paths = []
        for line in result.stdout.splitlines():
            if line.startswith("worktree "):
                path = line[len("worktree "):]
                if "/tmp/baadd-wt-" in path:
                    paths.append(path)
        return paths
    except Exception:
        return []


def slug_to_name(wt_path):
    """Convert /tmp/baadd-wt-my-scenario-99999 → 'my scenario'."""
    basename = os.path.basename(wt_path)
    # Strip leading "baadd-wt-"
    if basename.startswith("baadd-wt-"):
        basename = basename[len("baadd-wt-"):]
    # Strip trailing -<digits> pid suffix
    basename = re.sub(r"-\d+$", "", basename)
    return basename.replace("-", " ")


def resolve_display_name(wt_path, wt_map):
    """Return explicit name from wt_map, or fall back to slug_to_name."""
    return wt_map.get(wt_path) or slug_to_name(wt_path)

# ---------------------------------------------------------------------------
# Log line filtering
# ---------------------------------------------------------------------------

def is_log_noise(line):
    """Return True for per-agent lines that should be suppressed from the log strip."""
    # TPS monitor: "  [prefix] 1234 tok | 45.1 TPS | 30s"
    if re.search(r"\d+\s+tok\s+\|\s+[\d.]+\s+TPS", line):
        return True
    # Per-agent bracketed output: "  [Scenario Name PHASE] some text"
    # but NOT mapping lines like "  Scenario → /tmp/..."
    if re.match(r"^\s+\[.+?\] ", line) and "→ /tmp" not in line:
        return True
    return False


def parse_wt_mapping_line(line):
    """Parse '  Scenario name → /tmp/baadd-wt-...' lines.

    Returns (scenario_name, wt_path) or None.
    """
    m = re.match(r"^\s+(.+?)\s+→\s+(/tmp/baadd-wt-\S+)", line)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return None

# ---------------------------------------------------------------------------
# JSONL reading
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class AgentState:
    wt_path: str
    scenario_name: str
    active_phase: Optional[str] = None
    done_phases: dataclasses.field(default_factory=list) = dataclasses.field(default_factory=list)
    current_iter: int = 0
    max_iter: int = 125
    tokens: int = 0
    last_tools: dataclasses.field(default_factory=list) = dataclasses.field(default_factory=list)
    start_ts: float = dataclasses.field(default_factory=time.time)

    @property
    def elapsed_s(self):
        return time.time() - self.start_ts

    @property
    def is_stale(self):
        files = glob.glob(os.path.join(self.wt_path, "agent_events_*.jsonl"))
        if not files:
            return False
        try:
            newest = max(os.path.getmtime(f) for f in files)
            return (time.time() - newest) > _STALE_AFTER_S
        except OSError:
            return False

    @property
    def is_done(self):
        return set(_ALL_PHASE_LABELS).issubset(set(self.done_phases))


def format_tool_call(tool, input_dict):
    """Format a tool_call event into a short action string."""
    if input_dict is None:
        input_dict = {}
    if tool in ("read_file", "read"):
        return f"r: {input_dict.get('path', '?')}"
    if tool in ("write_file", "write"):
        return f"w: {input_dict.get('path', '?')}"
    if tool in ("edit_file", "edit"):
        return f"e: {input_dict.get('path', '?')}"
    if tool in ("bash", "run_command", "execute", "shell"):
        cmd = input_dict.get("command", input_dict.get("cmd", "?"))
        return f"$ {str(cmd)[:60]}"
    # generic fallback
    first_val = next(iter(input_dict.values()), "?") if input_dict else "?"
    return f"{tool}: {str(first_val)[:50]}"


def read_wt_state(wt_path, scenario_name=None):
    """Read all agent_events_*.jsonl files in wt_path and return an AgentState."""
    state = AgentState(
        wt_path=wt_path,
        scenario_name=scenario_name or slug_to_name(wt_path),
    )
    # Group log files by phase, pick highest mtime per phase
    by_phase: Dict[str, tuple] = {}
    for log_path in glob.glob(os.path.join(wt_path, "agent_events_*.jsonl")):
        name = os.path.basename(log_path)
        phase_key = None
        for prefix, _label in _PHASE_PREFIXES:
            if name.startswith(f"agent_events_{prefix}_") or name == f"agent_events_{prefix}.jsonl":
                phase_key = prefix
                break
        if phase_key is None:
            continue
        try:
            mtime = os.path.getmtime(log_path)
        except OSError:
            continue
        existing = by_phase.get(phase_key)
        if existing is None or existing[0] < mtime:
            by_phase[phase_key] = (mtime, log_path)

    # Parse each phase log
    phase_data: Dict[str, dict] = {}
    for phase_key, (mtime, log_path) in by_phase.items():
        peak_iter, max_iter, done = 0, 125, False
        tokens = 0
        start_ts = None
        tools = []
        try:
            with open(log_path) as f:
                for raw in f:
                    try:
                        rec = json.loads(raw)
                    except (json.JSONDecodeError, ValueError):
                        continue
                    ev = rec.get("event")
                    if ev == "session_start":
                        ts_str = rec.get("ts")
                        if ts_str:
                            try:
                                start_ts = datetime.datetime.fromisoformat(ts_str).timestamp()
                            except Exception:
                                pass
                    elif ev == "iteration_start":
                        peak_iter = max(peak_iter, rec.get("iteration", 0))
                        max_iter = rec.get("max_iterations", max_iter)
                    elif ev == "api_response":
                        t = rec.get("cumulative_output_tokens") or 0
                        tokens = max(tokens, t)
                    elif ev == "tool_call":
                        desc = format_tool_call(rec.get("tool", "?"), rec.get("input") or {})
                        tools.append(desc)
                    elif ev == "session_end":
                        done = True
        except OSError:
            continue
        phase_data[phase_key] = {
            "peak_iter": peak_iter,
            "max_iter": max_iter,
            "done": done,
            "tokens": tokens,
            "start_ts": start_ts,
            "tools": tools,
        }

    # Build state from phase data in pipeline order
    done_phases = []
    active_phase = None
    for prefix, label in _PHASE_PREFIXES:
        if prefix not in phase_data:
            continue
        d = phase_data[prefix]
        if d["done"]:
            done_phases.append(label)
        elif active_phase is None:
            active_phase = label
            state.current_iter = d["peak_iter"]
            state.max_iter = d["max_iter"]
            state.last_tools = d["tools"][-3:]
            state.tokens = d["tokens"]
            if d["start_ts"]:
                state.start_ts = d["start_ts"]

    state.done_phases = done_phases
    state.active_phase = active_phase

    # If no active phase, use the last done phase for token/tool info
    if active_phase is None and done_phases:
        last_prefix = None
        for prefix, label in reversed(_PHASE_PREFIXES):
            if label in done_phases:
                last_prefix = prefix
                break
        if last_prefix and last_prefix in phase_data:
            d = phase_data[last_prefix]
            state.tokens = d["tokens"]
            state.last_tools = d["tools"][-3:]
            if d["start_ts"]:
                state.start_ts = d["start_ts"]

    return state

# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def render_progress_bar(current_iter, max_iter, bar_width=_BAR_WIDTH):
    """Return a unicode progress bar string of exactly bar_width chars."""
    if max_iter <= 0:
        return "░" * bar_width
    ratio = min(1.0, current_iter / max_iter)
    filled = int(bar_width * ratio)
    return "█" * filled + "░" * (bar_width - filled)


def format_phase_line(done_phases, active_phase, current_iter, max_iter):
    """Return a compact phase status string."""
    parts = []
    for label in _ALL_PHASE_LABELS:
        if label in done_phases:
            parts.append(f"{label}✓")
        elif label == active_phase:
            parts.append(f"[{label} {current_iter}/{max_iter}]")
        else:
            parts.append("─")
    return "  ".join(parts)


def format_elapsed(elapsed_s):
    """Format elapsed seconds as '45s' or '3m05s'."""
    s = int(elapsed_s)
    if s < 60:
        return f"{s}s"
    return f"{s // 60}m{s % 60:02d}s"


def format_metrics_line(tokens, elapsed_s=None, tps=None):
    """Return a metrics string or '─' when no tokens yet."""
    if tokens == 0:
        return "─"
    if tps is None:
        if elapsed_s and elapsed_s > 0:
            tps = tokens / elapsed_s
        else:
            tps = 0.0
    return f"{tokens:,} tok  {tps:.1f} TPS"


def build_agent_panel(state):
    """Build a rich.panel.Panel for one agent."""
    name = state.scenario_name
    if len(name) > _MAX_SCENARIO_NAME:
        name = name[:_MAX_SCENARIO_NAME - 1] + "…"
    title = name
    if state.is_stale:
        title = f"{name} (stale)"

    bar = render_progress_bar(state.current_iter, state.max_iter)
    phase_line = format_phase_line(
        state.done_phases, state.active_phase, state.current_iter, state.max_iter
    )
    elapsed = format_elapsed(state.elapsed_s)
    metrics = format_metrics_line(state.tokens, state.elapsed_s)

    lines = [
        f"{phase_line}   {elapsed}",
        f"[{bar}]",
        metrics,
    ]
    for tool in state.last_tools:
        lines.append(f"  {tool}")

    content = Text("\n".join(lines))
    return Panel(content, title=title, title_align="left")


def format_header(states, session_start_ts):
    """Return a header string."""
    elapsed = format_elapsed(time.time() - session_start_ts)
    if not states:
        return f"BAADD Dashboard  │  waiting for agents  │  {elapsed}"
    count = len(states)
    label = "agent" if count == 1 else "agents"
    return f"BAADD Dashboard  │  {count} {label} running  │  {elapsed}"


def format_log_strip(log_buffer):
    """Return a string of recent orchestrator log lines."""
    if not log_buffer:
        return "(waiting for orchestrator output...)"
    return "\n".join(log_buffer)


def build_renderable(states, log_buffer, session_start_ts):
    """Build the full Rich renderable (Group of Panels)."""
    header_text = format_header(states, session_start_ts)
    header_panel = Panel(Text(header_text), style="bold")
    log_panel = Panel(Text(format_log_strip(log_buffer)), title="log", title_align="left")
    agent_panels = [build_agent_panel(s) for s in states]
    return Group(header_panel, *agent_panels, log_panel)

# ---------------------------------------------------------------------------
# Subprocess command builder
# ---------------------------------------------------------------------------

def build_subprocess_cmd(pass_args):
    """Return the command list to launch orchestrate.py."""
    return [sys.executable, "scripts/orchestrate.py"] + list(pass_args)

# ---------------------------------------------------------------------------
# Wrapper mode
# ---------------------------------------------------------------------------

def run_wrapper_mode(pass_args, poll_interval, console):
    cmd = build_subprocess_cmd(pass_args)
    if not os.path.exists("scripts/orchestrate.py"):
        print("ERROR: scripts/orchestrate.py not found", file=sys.stderr)
        sys.exit(1)

    wt_map: Dict[str, str] = {}
    log_buffer = collections.deque(maxlen=_MAX_LOG_LINES)
    done_event = threading.Event()

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except FileNotFoundError:
        print("ERROR: scripts/orchestrate.py not found", file=sys.stderr)
        sys.exit(1)

    def _sigterm(signum, frame):
        proc.terminate()
        sys.exit(1)

    signal.signal(signal.SIGTERM, _sigterm)

    def _read_stdout():
        for line in proc.stdout:
            line = line.rstrip()
            mapping = parse_wt_mapping_line(line)
            if mapping:
                wt_map[mapping[1]] = mapping[0]
            if not is_log_noise(line):
                log_buffer.append(line)
        done_event.set()

    reader = threading.Thread(target=_read_stdout, daemon=True)
    reader.start()

    session_start = time.time()
    try:
        with Live(console=console, refresh_per_second=0.5, screen=False) as live:
            while True:
                wt_paths = discover_worktrees()
                states = [
                    read_wt_state(p, resolve_display_name(p, wt_map))
                    for p in wt_paths
                ]
                live.update(build_renderable(states, log_buffer, session_start))
                if done_event.wait(timeout=poll_interval):
                    # Final render
                    wt_paths = discover_worktrees()
                    states = [
                        read_wt_state(p, resolve_display_name(p, wt_map))
                        for p in wt_paths
                    ]
                    live.update(build_renderable(states, log_buffer, session_start))
                    break
    except KeyboardInterrupt:
        proc.terminate()
        sys.exit(0)

    proc.wait()
    sys.exit(proc.returncode)

# ---------------------------------------------------------------------------
# Watcher mode
# ---------------------------------------------------------------------------

def run_watcher_mode(poll_interval, console):
    wt_map: Dict[str, str] = {}
    log_buffer = collections.deque(maxlen=_MAX_LOG_LINES)
    session_start = time.time()
    consecutive_empty = 0

    try:
        with Live(console=console, refresh_per_second=0.5, screen=False) as live:
            while True:
                wt_paths = discover_worktrees()
                if not wt_paths:
                    consecutive_empty += 1
                    if consecutive_empty >= 2:
                        live.update(build_renderable([], log_buffer, session_start))
                        break
                else:
                    consecutive_empty = 0

                states = [
                    read_wt_state(p, resolve_display_name(p, wt_map))
                    for p in wt_paths
                ]
                live.update(build_renderable(states, log_buffer, session_start))
                time.sleep(poll_interval)
    except KeyboardInterrupt:
        pass

    console.print("All agents done.")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args, pass_args = parse_args()
    console = Console()
    if args.watch:
        run_watcher_mode(args.refresh, console)
    else:
        run_wrapper_mode(pass_args, args.refresh, console)


if __name__ == "__main__":
    main()
