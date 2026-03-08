import json
import sys
import unittest
from unittest.mock import MagicMock, patch
import importlib

# Clean up any mocks left over from other tests
if "dailyform.toodledo" in sys.modules:
    del sys.modules["dailyform.toodledo"]

# Mock requests
sys.modules["requests"] = MagicMock()

# Mock configparser to return a mock value for access_token
mock_config = MagicMock()
mock_config.get.side_effect = lambda section, key: "mock_token" if key == "access_token" else MagicMock()
sys.modules["configparser"] = MagicMock()
sys.modules["configparser"].ConfigParser.return_value = mock_config

from dailyform import toodledo  # noqa: E402


class TestToodledo(unittest.TestCase):
    def setUp(self):
        # We need to reload toodledo to make sure it doesn't use the mock from test_dailyform.py
        importlib.reload(toodledo)
        toodledo.access_token = "mock_token"

    def test_get_todos_success(self):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"num": 2, "total": 2},
            {"id": 1234, "title": "Task 1"},
            {"id": 5678, "title": "Task 2"},
        ]
        toodledo.requests.get.return_value = mock_response

        todos = toodledo.get_todos()
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0]["title"], "Task 1")
        self.assertEqual(todos[1]["title"], "Task 2")

    def test_get_todos_empty(self):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"num": 0, "total": 0}]
        toodledo.requests.get.return_value = mock_response

        todos = toodledo.get_todos()
        self.assertEqual(todos, [])

    def test_get_todos_no_token(self):
        toodledo.access_token = None
        todos = toodledo.get_todos()
        self.assertEqual(todos, [])


if __name__ == "__main__":
    unittest.main()
