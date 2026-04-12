import os
import sys
from typing import List, Dict


def load_dotenv(path: str = ".env") -> None:
    """Load .env file into environment. Existing env vars take priority."""
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                if key and key not in os.environ:
                    os.environ[key] = value
    except FileNotFoundError:
        pass

def parse_cli_args(args: List[str]) -> Dict[str, str]:
    """
    Parses command line arguments.
    Specifically extracts the --event-log path if present.
    """
    config = {}
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--event-log":
            if i + 1 < len(args): # Ensure there is a value following the flag
                config['event_log'] = args[i+1]
                i += 1 # Skip the next argument (the path)
            else:
                raise ValueError("Missing value for --event-log")
        # Add logic for other potential arguments here in future iterations
        i += 1
    return config
