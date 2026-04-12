import sys
from typing import List, Dict

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
