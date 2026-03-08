import hashlib
import json
import sys
import unittest
from unittest.mock import MagicMock

# Ensure clean mocks
if "dailyform.toodledo" in sys.modules:
    del sys.modules["dailyform.toodledo"]

# Mock requests before import
mock_requests = MagicMock()
# Mock response for module-level calls
mock_response = MagicMock()
mock_response.text = json.dumps({"userid": "12345", "token": "mock_token"})
mock_requests.get.return_value = mock_response
sys.modules["requests"] = mock_requests

mock_config = MagicMock()
mock_config.get.return_value = "mock_value"
sys.modules["configparser"] = MagicMock()
sys.modules["configparser"].ConfigParser.return_value = mock_config

from dailyform import toodledo  # noqa: E402


class TestToodledo(unittest.TestCase):
    def setUp(self):
        # We don't need to reload because we set up mocks correctly before import
        # Reset session values if needed
        toodledo.session = {"appid": "test_appid"}
        toodledo.apptoken = "test_token"
        toodledo.userpw = "test_pw"
        toodledo.email = "test@example.com"

    def tearDown(self):
        import os
        if os.path.exists("session.pkl"):
            try:
                os.remove("session.pkl")
            except OSError:
                pass

    def test_make_sig(self):
        # Test make_sig
        # toodledo.apptoken is reset in setUp to "test_token"
        # "test" + "test_token" = "testtest_token"
        sig = toodledo.make_sig("test")

        expected_sig = hashlib.md5("testtest_token".encode("utf-8")).hexdigest()
        self.assertEqual(sig, expected_sig)

    def test_get_todos(self):
        # Setup specific mock for get_todos call
        mock_todos_response = MagicMock()
        mock_todos_response.text = json.dumps([{"title": "Task 1"}, {"title": "Task 2"}])

        # We need to update the mock on the imported module
        toodledo.requests.get.return_value = mock_todos_response

        toodledo.session["key"] = "test_key"

        todos = toodledo.get_todos()
        self.assertEqual(todos, [{"title": "Task 1"}, {"title": "Task 2"}])


if __name__ == "__main__":
    unittest.main()
