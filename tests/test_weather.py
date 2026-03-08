import json
import sys
import unittest
from datetime import date
from unittest.mock import MagicMock, patch
import importlib

if "dailyform.weather" in sys.modules:
    del sys.modules["dailyform.weather"]

# Mock secrets
sys.modules["dailyform.secrets"] = MagicMock()
sys.modules["dailyform.secrets"].OWM_API_KEY = "TEST_API_KEY"

# Mock urllib and urllib.request
mock_urllib = MagicMock()
mock_urllib_request = MagicMock()
mock_urllib.request = mock_urllib_request
sys.modules["urllib"] = mock_urllib
sys.modules["urllib.request"] = mock_urllib_request

from dailyform import weather  # noqa: E402


class TestWeather(unittest.TestCase):
    def setUp(self):
        importlib.reload(weather)

    def test_get_weather_forecast(self):
        mock_response = MagicMock()
        mock_json = {
            "list": [
                {
                    "dt_txt": "2023-01-01 12:00:00",
                    "main": {"temp_min": 32.5},
                    "weather": [{"main": "Clouds"}],
                },
                {
                    "dt_txt": "2023-01-01 15:00:00",
                    "main": {"temp_min": 28.0},  # Lower temp on same day
                    "weather": [{"main": "Snow"}],
                },
                {
                    "dt_txt": "2023-01-02 12:00:00",
                    "main": {"temp_min": 45.0},
                    "weather": [{"main": "Clear"}],
                },
            ]
        }
        mock_response.read.return_value = json.dumps(mock_json).encode("utf-8")

        # Make the context manager work (with ...)
        mock_response.__enter__.return_value = mock_response
        weather.urllib.request.urlopen.return_value = mock_response

        forecasts = weather.get_weather_forecast("10001")

        self.assertEqual(len(forecasts), 2)

        day1 = date(2023, 1, 1)
        day2 = date(2023, 1, 2)

        self.assertIn(day1, forecasts)
        self.assertIn(day2, forecasts)

        # It should record the lowest temp (28.0) but might keep the first condition encountered (Clouds)
        self.assertEqual(forecasts[day1]["low"]["fahrenheit"], 28.0)
        self.assertEqual(forecasts[day1]["conditions"], "Clouds")

        self.assertEqual(forecasts[day2]["low"]["fahrenheit"], 45.0)
        self.assertEqual(forecasts[day2]["conditions"], "Clear")


if __name__ == "__main__":
    unittest.main()
