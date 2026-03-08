"""Tests for the toodledo module."""

import unittest
from unittest.mock import MagicMock, patch

from dailyform import toodledo


class TestToodledo(unittest.TestCase):
    """Test suite for the toodledo module."""

    @patch("dailyform.toodledo.config")
    @patch("dailyform.toodledo.requests.get")
    def test_get_todos_success(self, mock_get, mock_config):
        """Test successfully fetching todos."""
        mock_config.toodledo_access_token = "mock_token"
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"num": 2, "total": 2},
            {"id": 1234, "title": "Task 1"},
            {"id": 5678, "title": "Task 2"},
        ]
        mock_get.return_value = mock_response

        todos = toodledo.get_todos()
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0]["title"], "Task 1")
        self.assertEqual(todos[1]["title"], "Task 2")

    @patch("dailyform.toodledo.config")
    @patch("dailyform.toodledo.requests.get")
    def test_get_todos_empty(self, mock_get, mock_config):
        """Test fetching todos when the list is empty."""
        mock_config.toodledo_access_token = "mock_token"
        mock_response = MagicMock()
        mock_response.json.return_value = [{"num": 0, "total": 0}]
        mock_get.return_value = mock_response

        todos = toodledo.get_todos()
        self.assertEqual(todos, [])

    @patch("dailyform.toodledo.config")
    def test_get_todos_no_token(self, mock_config):
        """Test fetching todos without an access token."""
        mock_config.toodledo_access_token = None
        todos = toodledo.get_todos()
        self.assertEqual(todos, [])

if __name__ == "__main__":
    unittest.main()
