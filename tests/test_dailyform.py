import os
import sys
import unittest
from unittest.mock import MagicMock

# Mock modules before importing dailyform
sys.modules["dailyform.secrets"] = MagicMock()
sys.modules["dailyform.secrets"].WU_API_KEY = "TEST_API_KEY"

# Mock urllib.request
mock_urllib = MagicMock()
mock_urllib_request = MagicMock()
mock_urllib.request = mock_urllib_request
sys.modules["urllib"] = mock_urllib
sys.modules["urllib.request"] = mock_urllib_request

# Mock toodledo to avoid import errors
mock_toodledo = MagicMock()
mock_toodledo.get_todos.return_value = [{"title": "Mock Todo"}]
sys.modules["dailyform.toodledo"] = mock_toodledo

from dailyform.form import DailyForm  # noqa: E402


class TestDailyForm(unittest.TestCase):
    def setUp(self):
        if os.path.exists("oldfacts.db"):
            os.remove("oldfacts.db")

    def tearDown(self):
        if os.path.exists("oldfacts.db"):
            try:
                os.remove("oldfacts.db")
            except OSError:
                pass

    def test_daily_form_output(self):
        # Configure mock weather response
        mock_response = MagicMock()
        mock_response.read.return_value = b"""
        {
            "forecast": {
                "simpleforecast": {
                    "forecastday": [
                        {
                            "date": {"day": 1, "month": 1, "year": 2023},
                            "low": {"fahrenheit": 32},
                            "conditions": "Cloudy"
                        }
                    ]
                }
            }
        }
        """

        # We need to set the return value on the imported module's urllib.request.urlopen
        # Since we mocked sys.modules['urllib.request'], dailyform.form.urllib.request refers to that mock
        mock_urllib_request.urlopen.return_value = mock_response

        # Test case 1: Forced weather failure
        dt = DailyForm("Andy")
        dt.fail_weather = True
        dt.prepare()
        dt.prepare()  # Second prepare calls analyze/format implicitly or explicitly
        output = dt.render_text()
        self.assertIn("DailyForm for Andy", output)
        del dt

        # Test case 2: Valid zip code
        dt = DailyForm("Andy")
        dt.facts["zip_code"] = "10001"
        dt.prepare()
        dt.prepare()
        output = dt.render_text()
        self.assertIn("DailyForm for Andy", output)
        del dt

        # Test case 3: Default behavior
        dt = DailyForm("Andy")
        dt.prepare()
        dt.prepare()
        output = dt.render_text()
        self.assertIn("DailyForm for Andy", output)
        del dt

        # Test case 4: Forced weather failure again
        dt = DailyForm("Andy")
        dt.fail_weather = True
        dt.prepare()
        dt.prepare()
        output = dt.render_text()
        self.assertIn("DailyForm for Andy", output)
        del dt


if __name__ == "__main__":
    unittest.main()
