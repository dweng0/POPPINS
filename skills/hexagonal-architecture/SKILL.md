---
name: hexagonal-architecture
description: Design and implement features using Ports and Adapters (Hexagonal Architecture)
tools: [write_file, edit_file, read_file]
---

# Hexagonal Architecture (Ports and Adapters)

Every feature you implement must be structured so the domain logic is isolated from infrastructure. Use three layers:

## The Three Layers

### Port (the interface)
- A Python `Protocol` or `ABC` living in `src/ports/<name>.py`
- Contains only abstract method signatures — no logic, no imports of external libs
- The domain calls this; it never knows what's on the other side

```python
# src/ports/file_reader.py
from typing import Protocol

class FileReader(Protocol):
    def read(self, path: str) -> str: ...
```

### Adapter (the concrete implementation)
- Lives in `src/adapters/<technology>/<name>.py`
- Implements exactly one port for one specific technology (filesystem, subprocess, HTTP, etc.)
- Imports whatever library it needs (`os`, `subprocess`, `requests`, etc.)
- **Never imported by domain or application logic** — wired up at the entry point only

```python
# src/adapters/filesystem/os_file_reader.py
class OsFileReader:
    def read(self, path: str) -> str:
        with open(path) as f:
            return f.read()
```

### Domain / Application logic
- Lives in `src/` or `scripts/` as appropriate
- Imports only ports, never adapters or external libraries directly
- All external dependencies arrive as injected port parameters with sensible defaults

```python
# src/scenario_loader.py
from src.ports.file_reader import FileReader
from src.adapters.filesystem.os_file_reader import OsFileReader

def load_scenario(path: str, reader: FileReader = OsFileReader()) -> str:
    return reader.read(path)
```

## How to Apply This

1. **Identify the boundary**: what does this feature need from the outside world? (files, processes, network, clock, randomness)
2. **Name the port**: one verb-noun Protocol per distinct capability (`FileReader`, `CommandRunner`, `IssueTracker`)
3. **Write the adapter**: the smallest class that satisfies the port using the real technology
4. **Write the domain function**: receives the port as a parameter; inject the real adapter as the default
5. **Test with a fake**: in tests, pass a simple lambda or stub instead of the real adapter — no mocking frameworks needed

## When NOT to add a port

If the unit is pure data transformation with no I/O (parsing, formatting, calculating), skip the port layer entirely — it would be over-engineering. Note this explicitly in PLAN.md.

## File Layout

```
src/
  ports/
    file_reader.py       # Protocol: read(path) -> str
    command_runner.py    # Protocol: run(cmd) -> (stdout, returncode)
  adapters/
    filesystem/
      os_file_reader.py  # OsFileReader implements FileReader
    subprocess/
      shell_runner.py    # ShellRunner implements CommandRunner
```

## Tests Use Injection

```python
def test_load_scenario_reads_correct_path():
    # BDD: Load scenario from file
    captured = {}
    def fake_reader(path):
        captured["path"] = path
        return "Scenario: test"

    result = load_scenario("BDD.md", reader=fake_reader)
    assert captured["path"] == "BDD.md"
    assert "Scenario: test" in result
```

No `unittest.mock`, no patching — just pass a function or object that satisfies the Protocol.
