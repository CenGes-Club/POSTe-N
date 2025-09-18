import os
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from logs import rename_log_file, DATA_LOG_PATH, EVENT_LOG_PATH


class TestRenameLogFile(unittest.TestCase):

    @patch("os.rename")
    def test_rename_log_file(self, mock_rename):
        # Fixed datetime for reproducibility
        now = datetime(2025, 1, 2, 10, 0, 0)
        previous_day = (now - timedelta(days=1)).strftime("%m-%d-%y")

        # Run the function
        rename_log_file(now)

        # Expected new file names
        expected_data_dst = DATA_LOG_PATH[:-4] + "_" + previous_day + DATA_LOG_PATH[-4:]
        expected_event_dst = EVENT_LOG_PATH[:-4] + "_" + previous_day + EVENT_LOG_PATH[-4:]

        # Check calls to os.rename
        mock_rename.assert_any_call(DATA_LOG_PATH, expected_data_dst)
        mock_rename.assert_any_call(EVENT_LOG_PATH, expected_event_dst)
        self.assertEqual(mock_rename.call_count, 2)


if __name__ == "__main__":
    unittest.main()
