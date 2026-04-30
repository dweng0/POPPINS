import unittest
from unittest.mock import MagicMock

# Assuming agent and EventLogger are available in the test environment for mocking purposes
from scripts.agent import parse_cli_args
from src.event_logger import EventLogger


class TestEventLogging(unittest.TestCase):
    def setUp(self):
        # Mock file writer used by EventLogger during initialization/usage
        self.mock_file_writer = MagicMock()

    # BDD: Custom event log path via --event-log
    def test_custom_log_path_via_cli(self):
        # 1. Define mocked CLI arguments
        mock_args = ["agent.py", "--event-log=/custom/path/events.jsonl"]

        # 2. Parse the arguments (This is where the path should be extracted)
        parsed_config = parse_cli_args(mock_args)
        expected_path = "/custom/path/events.jsonl"
        self.assertEqual(
            parsed_config["event_log"],
            expected_path,
            "Should correctly extract custom event log path from CLI args.",
        )

        # 3. Initialize EventLogger using the parsed configuration and mock writer
        logger = EventLogger(log_path=expected_path, file_writer=self.mock_file_writer)

        # 4. Assert that the logger initialized correctly using the custom path
        self.assertEqual(
            logger._log_path,
            expected_path,
            "EventLogger should be initialized with the custom CLI path.",
        )
        # Optional: Ensure writer is set
        self.assertIs(logger.file_writer, self.mock_file_writer)
